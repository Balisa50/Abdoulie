"""Audit logs router."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import audit_log_crud
from app.database import get_db
from app.schemas import AuditLogCreate, AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogResponse])
async def list_audit_logs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all audit logs."""
    return await audit_log_crud.get_all(db, skip=skip, limit=limit)


@router.post("", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_log(audit_log: AuditLogCreate, db: AsyncSession = Depends(get_db)):
    """Create a new audit log."""
    return await audit_log_crud.create(db, audit_log.model_dump())


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
async def get_audit_log(audit_log_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get audit log by ID."""
    db_audit_log = await audit_log_crud.get(db, audit_log_id)
    if not db_audit_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    return db_audit_log


@router.get("/search/client/{client_id}", response_model=list[AuditLogResponse])
async def list_client_audit_logs(
    client_id: UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all audit logs for a specific client."""
    return await audit_log_crud.get_by_client_id(db, client_id, skip=skip, limit=limit)


@router.get("/search/entity/{entity_id}", response_model=list[AuditLogResponse])
async def list_entity_audit_logs(
    entity_id: UUID, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """Get all audit logs for a specific entity."""
    return await audit_log_crud.get_by_entity_id(db, entity_id, skip=skip, limit=limit)
