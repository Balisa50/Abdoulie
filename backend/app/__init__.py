"""Tesseract Backend Application"""

from app.crud import (
    audit_log_crud,
    audit_result_crud,
    client_crud,
    contract_crud,
    invoice_crud,
)
from app.database import AsyncSessionLocal, Base, engine, get_db
from app.models import AuditLog, AuditResult, Client, Contract, Invoice
from app.schemas import (
    AuditLogCreate,
    AuditLogResponse,
    AuditResultCreate,
    AuditResultResponse,
    AuditResultUpdate,
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    ContractCreate,
    ContractResponse,
    ContractUpdate,
    InvoiceCreate,
    InvoiceResponse,
    InvoiceUpdate,
)

__all__ = [
    # Models
    "Client",
    "Invoice",
    "Contract",
    "AuditResult",
    "AuditLog",
    # Schemas
    "ClientCreate",
    "ClientResponse",
    "ClientUpdate",
    "InvoiceCreate",
    "InvoiceResponse",
    "InvoiceUpdate",
    "ContractCreate",
    "ContractResponse",
    "ContractUpdate",
    "AuditResultCreate",
    "AuditResultResponse",
    "AuditResultUpdate",
    "AuditLogCreate",
    "AuditLogResponse",
    # CRUD
    "client_crud",
    "invoice_crud",
    "contract_crud",
    "audit_result_crud",
    "audit_log_crud",
    # Database
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db",
]
