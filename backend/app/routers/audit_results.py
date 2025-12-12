import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit_engine import AuditEngine
from app.crud import audit_result_crud, contract_crud, invoice_crud
from app.database import get_db
from app.schemas import AuditResultCreate, AuditResultResponse, AuditResultUpdate
from app.security import verify_api_key
from app.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/audit-results",
    tags=["audit-results"],
    dependencies=[Depends(verify_api_key)] if settings.require_api_key else [],
)


class AuditRequest(BaseModel):
    """Request model for running an audit."""

    invoice_id: UUID
    contract_id: UUID | None = None
    shipment_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Shipment data for audit validation",
    )


@router.post("", response_model=AuditResultResponse)
async def create_audit_result(
    audit_result_in: AuditResultCreate,
    db: AsyncSession = Depends(get_db),
) -> AuditResultResponse:
    """Create a new audit result."""
    logger.info(f"Creating audit result for rule: {audit_result_in.rule_id}")

    if audit_result_in.invoice_id:
        invoice = await invoice_crud.get(db, audit_result_in.invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

    if audit_result_in.contract_id:
        contract = await contract_crud.get(db, audit_result_in.contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

    audit_result = await audit_result_crud.create(db, audit_result_in.model_dump())
    return AuditResultResponse.model_validate(audit_result)


@router.post("/run-audit", response_model=AuditResultResponse)
async def run_audit(
    request: AuditRequest,
    db: AsyncSession = Depends(get_db),
) -> AuditResultResponse:
    """Run an audit on an invoice."""
    logger.info(f"Running audit on invoice: {request.invoice_id}")

    invoice = await invoice_crud.get(db, request.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if not invoice.extracted_entities:
        raise HTTPException(
            status_code=400,
            detail="Invoice has no extracted data. Please extract invoice data first.",
        )

    contract_rules = {}
    if request.contract_id:
        contract = await contract_crud.get(db, request.contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        contract_rules = contract.data or contract_rules

    if not contract_rules:
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
            "allowed_accessorials": ["FUEL SURCHARGE"],
            "min_string_similarity": 0.8,
        }

    try:
        engine = AuditEngine(contract_rules)
        anomalies = engine.audit(invoice.extracted_entities, request.shipment_data)

        audit_result_data = {
            "invoice_id": request.invoice_id,
            "contract_id": request.contract_id,
            "rule_id": "GENERAL_AUDIT",
            "status": "passed" if not anomalies else "failed",
            "findings": {
                "anomalies": anomalies,
                "anomaly_count": len(anomalies),
                "invoice_data": invoice.extracted_entities,
                "contract_rules": contract_rules,
            },
        }

        audit_result = await audit_result_crud.create(db, audit_result_data)
        return AuditResultResponse.model_validate(audit_result)

    except Exception as e:
        logger.error(f"Error running audit: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error running audit")


@router.get("", response_model=list[AuditResultResponse])
async def list_audit_results(
    invoice_id: UUID | None = Query(None),
    contract_id: UUID | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
) -> list[AuditResultResponse]:
    """List audit results, optionally filtered."""
    logger.info(
        f"Listing audit results: invoice_id={invoice_id}, contract_id={contract_id}, status={status}"
    )

    if invoice_id:
        invoice = await invoice_crud.get(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        audit_results = await audit_result_crud.get_by_invoice_id(
            db, invoice_id, skip=skip, limit=limit
        )
    elif contract_id:
        contract = await contract_crud.get(db, contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        audit_results = await audit_result_crud.get_by_contract_id(
            db, contract_id, skip=skip, limit=limit
        )
    else:
        audit_results = await audit_result_crud.get_all(db, skip=skip, limit=limit)

    if status:
        audit_results = [ar for ar in audit_results if ar.status == status]

    return [AuditResultResponse.model_validate(ar) for ar in audit_results]


@router.get("/{audit_result_id}", response_model=AuditResultResponse)
async def get_audit_result(
    audit_result_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> AuditResultResponse:
    """Get an audit result by ID."""
    logger.info(f"Getting audit result: {audit_result_id}")
    audit_result = await audit_result_crud.get(db, audit_result_id)
    if not audit_result:
        raise HTTPException(status_code=404, detail="Audit result not found")
    return AuditResultResponse.model_validate(audit_result)


@router.put("/{audit_result_id}", response_model=AuditResultResponse)
async def update_audit_result(
    audit_result_id: UUID,
    audit_result_in: AuditResultUpdate,
    db: AsyncSession = Depends(get_db),
) -> AuditResultResponse:
    """Update an audit result."""
    logger.info(f"Updating audit result: {audit_result_id}")
    audit_result = await audit_result_crud.get(db, audit_result_id)
    if not audit_result:
        raise HTTPException(status_code=404, detail="Audit result not found")

    update_data = audit_result_in.model_dump(exclude_unset=True)
    updated_audit_result = await audit_result_crud.update(db, audit_result, update_data)
    return AuditResultResponse.model_validate(updated_audit_result)


@router.delete("/{audit_result_id}")
async def delete_audit_result(
    audit_result_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Delete an audit result."""
    logger.info(f"Deleting audit result: {audit_result_id}")
    audit_result = await audit_result_crud.get(db, audit_result_id)
    if not audit_result:
        raise HTTPException(status_code=404, detail="Audit result not found")

    await audit_result_crud.delete(db, audit_result_id)
    return {"status": "success", "message": "Audit result deleted"}
