from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


# Client Schemas
class ClientBase(BaseModel):
    """Base client schema."""

    name: str
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    data: dict[str, Any] | None = None


class ClientCreate(ClientBase):
    """Client creation schema."""

    pass


class ClientUpdate(BaseModel):
    """Client update schema."""

    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    data: dict[str, Any] | None = None


class ClientResponse(ClientBase):
    """Client response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


# Invoice Schemas
class InvoiceBase(BaseModel):
    """Base invoice schema."""

    invoice_number: str
    amount: int
    currency: str = "USD"
    status: str = "draft"
    issue_date: datetime
    due_date: datetime | None = None
    duplicate_hash: str | None = None
    extracted_entities: dict[str, Any] | None = None
    data: dict[str, Any] | None = None


class InvoiceCreate(InvoiceBase):
    """Invoice creation schema."""

    client_id: UUID


class InvoiceUpdate(BaseModel):
    """Invoice update schema."""

    invoice_number: str | None = None
    amount: int | None = None
    currency: str | None = None
    status: str | None = None
    issue_date: datetime | None = None
    due_date: datetime | None = None
    duplicate_hash: str | None = None
    extracted_entities: dict[str, Any] | None = None
    data: dict[str, Any] | None = None


class InvoiceResponse(InvoiceBase):
    """Invoice response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: datetime


# Contract Schemas
class ContractBase(BaseModel):
    """Base contract schema."""

    contract_number: str
    title: str
    status: str = "draft"
    start_date: datetime
    end_date: datetime | None = None
    extracted_entities: dict[str, Any] | None = None
    rule_references: dict[str, Any] | None = None
    data: dict[str, Any] | None = None


class ContractCreate(ContractBase):
    """Contract creation schema."""

    client_id: UUID


class ContractUpdate(BaseModel):
    """Contract update schema."""

    contract_number: str | None = None
    title: str | None = None
    status: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    extracted_entities: dict[str, Any] | None = None
    rule_references: dict[str, Any] | None = None
    data: dict[str, Any] | None = None


class ContractResponse(ContractBase):
    """Contract response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: datetime


# Audit Result Schemas
class AuditResultBase(BaseModel):
    """Base audit result schema."""

    rule_id: str
    status: str = "pending"
    extracted_entities: dict[str, Any] | None = None
    variance_metrics: dict[str, Any] | None = None
    rule_references: dict[str, Any] | None = None
    findings: dict[str, Any] | None = None


class AuditResultCreate(AuditResultBase):
    """Audit result creation schema."""

    invoice_id: UUID | None = None
    contract_id: UUID | None = None


class AuditResultUpdate(BaseModel):
    """Audit result update schema."""

    status: str | None = None
    extracted_entities: dict[str, Any] | None = None
    variance_metrics: dict[str, Any] | None = None
    rule_references: dict[str, Any] | None = None
    findings: dict[str, Any] | None = None


class AuditResultResponse(AuditResultBase):
    """Audit result response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    invoice_id: UUID | None
    contract_id: UUID | None
    created_at: datetime
    updated_at: datetime


# Audit Log Schemas
class AuditLogBase(BaseModel):
    """Base audit log schema."""

    entity_type: str
    entity_id: UUID
    action: str
    status: str = "success"
    changes: dict[str, Any] | None = None
    error_message: str | None = None
    data: dict[str, Any] | None = None


class AuditLogCreate(AuditLogBase):
    """Audit log creation schema."""

    client_id: UUID | None = None


class AuditLogResponse(AuditLogBase):
    """Audit log response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    client_id: UUID | None
    created_at: datetime
