"""CRUD operations for database models."""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AuditLog,
    AuditResult,
    Client,
    Contract,
    Invoice,
)

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    """Base CRUD class."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def create(self, db: AsyncSession, obj_in: dict[str, Any]) -> ModelType:
        """Create object."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: UUID) -> ModelType | None:
        """Get object by id."""
        return await db.get(self.model, id)

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all objects."""
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: dict[str, Any],
    ) -> ModelType:
        """Update object."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: UUID) -> None:
        """Delete object."""
        db_obj = await db.get(self.model, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()


class CRUDClient(CRUDBase[Client]):
    """CRUD for Client."""

    async def get_by_email(self, db: AsyncSession, email: str) -> Client | None:
        """Get client by email."""
        query = select(Client).where(Client.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()


class CRUDInvoice(CRUDBase[Invoice]):
    """CRUD for Invoice."""

    async def get_by_invoice_number(self, db: AsyncSession, invoice_number: str) -> Invoice | None:
        """Get invoice by invoice number."""
        query = select(Invoice).where(Invoice.invoice_number == invoice_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_client_id(
        self,
        db: AsyncSession,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Invoice]:
        """Get invoices by client id."""
        query = select(Invoice).where(Invoice.client_id == client_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_status(
        self,
        db: AsyncSession,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Invoice]:
        """Get invoices by status."""
        query = select(Invoice).where(Invoice.status == status).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


class CRUDContract(CRUDBase[Contract]):
    """CRUD for Contract."""

    async def get_by_contract_number(
        self, db: AsyncSession, contract_number: str
    ) -> Contract | None:
        """Get contract by contract number."""
        query = select(Contract).where(Contract.contract_number == contract_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_client_id(
        self,
        db: AsyncSession,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Contract]:
        """Get contracts by client id."""
        query = select(Contract).where(Contract.client_id == client_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


class CRUDAuditResult(CRUDBase[AuditResult]):
    """CRUD for AuditResult."""

    async def get_by_invoice_id(
        self,
        db: AsyncSession,
        invoice_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditResult]:
        """Get audit results by invoice id."""
        query = (
            select(AuditResult)
            .where(AuditResult.invoice_id == invoice_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_contract_id(
        self,
        db: AsyncSession,
        contract_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditResult]:
        """Get audit results by contract id."""
        query = (
            select(AuditResult)
            .where(AuditResult.contract_id == contract_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


class CRUDAuditLog(CRUDBase[AuditLog]):
    """CRUD for AuditLog."""

    async def get_by_client_id(
        self,
        db: AsyncSession,
        client_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get audit logs by client id."""
        query = select(AuditLog).where(AuditLog.client_id == client_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_entity_id(
        self,
        db: AsyncSession,
        entity_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get audit logs by entity id."""
        query = select(AuditLog).where(AuditLog.entity_id == entity_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()


# Create instances
client_crud = CRUDClient(Client)
invoice_crud = CRUDInvoice(Invoice)
contract_crud = CRUDContract(Contract)
audit_result_crud = CRUDAuditResult(AuditResult)
audit_log_crud = CRUDAuditLog(AuditLog)
