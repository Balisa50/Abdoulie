"""Audit results router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import audit_result_crud
from app.database import get_db
from app.schemas import AuditResultCreate, AuditResultResponse, AuditResultUpdate

router = APIRouter(prefix="/audit-results", tags=["audit-results"])


@router.get("", response_model=list[AuditResultResponse])
async def list_audit_results(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all audit results."""
    return await audit_result_crud.get_all(db, skip=skip, limit=limit)


@router.post("", response_model=AuditResultResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_result(
    audit_result: AuditResultCreate, db: AsyncSession = Depends(get_db)
):
    """Create a new audit result."""
    return await audit_result_crud.create(db, audit_result.model_dump())


@router.get("/{audit_result_id}", response_model=AuditResultResponse)
async def get_audit_result(audit_result_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get audit result by ID."""
    db_audit_result = await audit_result_crud.get(db, audit_result_id)
    if not db_audit_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audit result not found"
        )
    return db_audit_result


@router.put("/{audit_result_id}", response_model=AuditResultResponse)
async def update_audit_result(
    audit_result_id: UUID,
    audit_result: AuditResultUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an audit result."""
    db_audit_result = await audit_result_crud.get(db, audit_result_id)
    if not db_audit_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audit result not found"
        )
    return await audit_result_crud.update(
        db, db_audit_result, audit_result.model_dump(exclude_unset=True)
    )


@router.delete("/{audit_result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_result(audit_result_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete an audit result."""
    db_audit_result = await audit_result_crud.get(db, audit_result_id)
    if not db_audit_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Audit result not found"
        )
    await audit_result_crud.delete(db, audit_result_id)


@router.get("/search/invoice/{invoice_id}", response_model=list[AuditResultResponse])
async def list_invoice_audit_results(
    invoice_id: UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all audit results for a specific invoice."""
    return await audit_result_crud.get_by_invoice_id(db, invoice_id, skip=skip, limit=limit)


@router.get("/search/contract/{contract_id}", response_model=list[AuditResultResponse])
async def list_contract_audit_results(
    contract_id: UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all audit results for a specific contract."""
    return await audit_result_crud.get_by_contract_id(db, contract_id, skip=skip, limit=limit)
