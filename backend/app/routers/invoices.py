"""Invoices router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import invoice_crud
from app.database import get_db
from app.schemas import InvoiceCreate, InvoiceResponse, InvoiceUpdate

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all invoices."""
    return await invoice_crud.get_all(db, skip=skip, limit=limit)


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    """Create a new invoice."""
    return await invoice_crud.create(db, invoice.model_dump())


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get invoice by ID."""
    db_invoice = await invoice_crud.get(db, invoice_id)
    if not db_invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return db_invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID, invoice: InvoiceUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an invoice."""
    db_invoice = await invoice_crud.get(db, invoice_id)
    if not db_invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return await invoice_crud.update(db, db_invoice, invoice.model_dump(exclude_unset=True))


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(invoice_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete an invoice."""
    db_invoice = await invoice_crud.get(db, invoice_id)
    if not db_invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    await invoice_crud.delete(db, invoice_id)


@router.get("/search/client/{client_id}", response_model=list[InvoiceResponse])
async def list_client_invoices(
    client_id: UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all invoices for a specific client."""
    return await invoice_crud.get_by_client_id(db, client_id, skip=skip, limit=limit)


@router.get("/search/status/{status}", response_model=list[InvoiceResponse])
async def list_invoices_by_status(
    status: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get invoices by status."""
    return await invoice_crud.get_by_status(db, status, skip=skip, limit=limit)
