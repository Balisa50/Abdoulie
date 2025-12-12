import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit_engine import AuditEngine
from app.crud import client_crud, invoice_crud
from app.database import get_db
from app.document_processor import DocumentProcessor
from app.models import Invoice
from app.schemas import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from app.security import validate_file_upload, verify_api_key
from app.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/invoices",
    tags=["invoices"],
    dependencies=[Depends(verify_api_key)] if settings.require_api_key else [],
)


@router.post("", response_model=InvoiceResponse)
async def create_invoice(
    invoice_in: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    """Create a new invoice."""
    logger.info(f"Creating invoice: {invoice_in.invoice_number}")

    client = await client_crud.get(db, invoice_in.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    existing_invoice = await invoice_crud.get_by_invoice_number(db, invoice_in.invoice_number)
    if existing_invoice:
        raise HTTPException(status_code=400, detail="Invoice with this number already exists")

    invoice = await invoice_crud.create(db, invoice_in.model_dump())
    return InvoiceResponse.model_validate(invoice)


@router.post("/upload", response_model=InvoiceResponse)
async def upload_invoice(
    client_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    """Upload and process a PDF invoice."""
    logger.info(f"Uploading invoice for client: {client_id}")

    client = await client_crud.get(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    validate_file_upload(file.filename, file.content_type, settings.max_upload_size)

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    tmp_path = None
    try:
        content = await file.read(settings.max_upload_size + 1)
        if len(content) > settings.max_upload_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {settings.max_upload_size / (1024 * 1024):.1f}MB",
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name

        logger.info(f"Processing PDF: {tmp_path}")

        processor = DocumentProcessor()
        extracted_data = processor.process_invoice(tmp_path)

        Path(tmp_path).unlink(missing_ok=True)

        invoice_date = extracted_data.get("invoice_date")
        if isinstance(invoice_date, str):
            try:
                issue_date = datetime.fromisoformat(invoice_date)
            except (ValueError, TypeError):
                issue_date = datetime.now()
        else:
            issue_date = invoice_date or datetime.now()

        invoice_data = {
            "client_id": client_id,
            "invoice_number": extracted_data.get("invoice_number", file.filename),
            "amount": int(float(extracted_data.get("total_charge", 0)) * 100),
            "currency": "USD",
            "status": "draft",
            "issue_date": issue_date,
            "extracted_entities": extracted_data,
        }

        invoice = await invoice_crud.create(db, invoice_data)
        return InvoiceResponse.model_validate(invoice)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading invoice: {e}", exc_info=True)
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Error processing invoice")


@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(
    client_id: UUID | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> list[InvoiceResponse]:
    """List invoices, optionally filtered by client or status."""
    logger.info(f"Listing invoices: client_id={client_id}, status={status}, skip={skip}, limit={limit}")

    if client_id:
        client = await client_crud.get(db, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        if status:
            invoices = await invoice_crud.get_by_status(db, status, skip=skip, limit=limit)
            invoices = [inv for inv in invoices if inv.client_id == client_id]
        else:
            invoices = await invoice_crud.get_by_client_id(db, client_id, skip=skip, limit=limit)
    elif status:
        invoices = await invoice_crud.get_by_status(db, status, skip=skip, limit=limit)
    else:
        invoices = await invoice_crud.get_all(db, skip=skip, limit=limit)

    return [InvoiceResponse.model_validate(invoice) for invoice in invoices]


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    """Get an invoice by ID."""
    logger.info(f"Getting invoice: {invoice_id}")
    invoice = await invoice_crud.get(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceResponse.model_validate(invoice)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    invoice_in: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    """Update an invoice."""
    logger.info(f"Updating invoice: {invoice_id}")
    invoice = await invoice_crud.get(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    update_data = invoice_in.model_dump(exclude_unset=True)
    updated_invoice = await invoice_crud.update(db, invoice, update_data)
    return InvoiceResponse.model_validate(updated_invoice)


@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Delete an invoice."""
    logger.info(f"Deleting invoice: {invoice_id}")
    invoice = await invoice_crud.get(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    await invoice_crud.delete(db, invoice_id)
    return {"status": "success", "message": "Invoice deleted"}
