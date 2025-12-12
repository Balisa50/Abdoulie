import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Client(Base):
    """Client entity."""

    __tablename__ = "clients"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)  # JSONB equivalent for custom attributes
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    invoices = relationship("Invoice", back_populates="client", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="client", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="client", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_clients_email", "email"),)  # type: ignore


class Invoice(Base):
    """Invoice entity."""

    __tablename__ = "invoices"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    client_id = Column(Uuid, ForeignKey("clients.id"), nullable=False)
    invoice_number = Column(String(100), nullable=False, unique=True)
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(String(50), nullable=False, default="draft")
    issue_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    duplicate_hash = Column(String(64), nullable=True)  # SHA256 hash for duplicate detection
    extracted_entities = Column(JSON, nullable=True)  # JSONB for extracted data
    data = Column(JSON, nullable=True)  # JSONB for flexible invoice data
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    client = relationship("Client", back_populates="invoices")
    audit_results = relationship(
        "AuditResult", back_populates="invoice", cascade="all, delete-orphan"
    )

    __table_args__ = (  # type: ignore
        Index("ix_invoices_client_id", "client_id"),
        Index("ix_invoices_status", "status"),
        Index("ix_invoices_issue_date", "issue_date"),
        Index("ix_invoices_duplicate_hash", "duplicate_hash"),
    )


class Contract(Base):
    """Contract entity."""

    __tablename__ = "contracts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    client_id = Column(Uuid, ForeignKey("clients.id"), nullable=False)
    contract_number = Column(String(100), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    extracted_entities = Column(JSON, nullable=True)  # JSONB for extracted entities
    rule_references = Column(JSON, nullable=True)  # JSONB for rule references
    data = Column(JSON, nullable=True)  # JSONB for flexible contract data
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    client = relationship("Client", back_populates="contracts")
    audit_results = relationship(
        "AuditResult", back_populates="contract", cascade="all, delete-orphan"
    )

    __table_args__ = (  # type: ignore
        Index("ix_contracts_client_id", "client_id"),
        Index("ix_contracts_status", "status"),
    )


class AuditResult(Base):
    """Audit result entity."""

    __tablename__ = "audit_results"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    invoice_id = Column(Uuid, ForeignKey("invoices.id"), nullable=True)
    contract_id = Column(Uuid, ForeignKey("contracts.id"), nullable=True)
    rule_id = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending, passed, failed
    extracted_entities = Column(JSON, nullable=True)  # JSONB for extracted entities
    variance_metrics = Column(JSON, nullable=True)  # JSONB for variance data
    rule_references = Column(JSON, nullable=True)  # JSONB for rule references
    findings = Column(JSON, nullable=True)  # JSONB for detailed findings
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    invoice = relationship("Invoice", back_populates="audit_results")
    contract = relationship("Contract", back_populates="audit_results")

    __table_args__ = (  # type: ignore
        Index("ix_audit_results_invoice_id", "invoice_id"),
        Index("ix_audit_results_contract_id", "contract_id"),
        Index("ix_audit_results_rule_id", "rule_id"),
        Index("ix_audit_results_status", "status"),
    )


class AuditLog(Base):
    """Audit log entity for tracking changes."""

    __tablename__ = "audit_logs"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    client_id = Column(Uuid, ForeignKey("clients.id"), nullable=True)
    entity_type = Column(String(100), nullable=False)  # invoice, contract, audit_result
    entity_id = Column(Uuid, nullable=False)
    action = Column(String(50), nullable=False)  # created, updated, deleted
    status = Column(String(50), nullable=False, default="success")  # success, error
    changes = Column(JSON, nullable=True)  # JSONB for detailed changes
    error_message = Column(Text, nullable=True)
    data = Column(JSON, nullable=True)  # JSONB for additional context
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    # Relationships
    client = relationship("Client", back_populates="audit_logs")

    __table_args__ = (  # type: ignore
        Index("ix_audit_logs_client_id", "client_id"),
        Index("ix_audit_logs_entity_type", "entity_type"),
        Index("ix_audit_logs_entity_id", "entity_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_status", "status"),
        Index("ix_audit_logs_created_at", "created_at"),
    )
