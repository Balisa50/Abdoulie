"""Seed script for sample data."""

import asyncio
import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import AuditLog, AuditResult, Client, Contract, Invoice
from app.settings import settings


async def create_tables():
    """Create all tables."""
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


async def seed_data():
    """Seed sample data."""
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create sample clients
        client1 = Client(
            id=uuid4(),
            name="Acme Corporation",
            email="contact@acme.com",
            phone="+1-555-0101",
            address="123 Business Ave, Commerce City, CO 80022",
            data={
                "industry": "Manufacturing",
                "employees": 500,
                "founded": 1995,
            },
        )

        client2 = Client(
            id=uuid4(),
            name="TechStart Inc",
            email="hello@techstart.io",
            phone="+1-555-0102",
            address="456 Innovation Blvd, San Francisco, CA 94105",
            data={
                "industry": "Technology",
                "employees": 150,
                "founded": 2018,
            },
        )

        session.add(client1)
        session.add(client2)
        await session.flush()

        # Create sample invoices
        invoice1 = Invoice(
            id=uuid4(),
            client_id=client1.id,
            invoice_number="INV-2024-001",
            amount=150000,  # $1500.00
            currency="USD",
            status="paid",
            issue_date=datetime.now(UTC) - timedelta(days=30),
            due_date=datetime.now(UTC) - timedelta(days=5),
            duplicate_hash=hashlib.sha256(b"INV-2024-001-acme").hexdigest(),
            extracted_entities={
                "vendor": "Acme Corporation",
                "line_items": [
                    {"description": "Service A", "quantity": 10, "unit_price": 1000},
                    {"description": "Service B", "quantity": 5, "unit_price": 2000},
                ],
            },
            metadata={
                "payment_method": "wire_transfer",
                "po_number": "PO-2024-001",
            },
        )

        invoice2 = Invoice(
            id=uuid4(),
            client_id=client1.id,
            invoice_number="INV-2024-002",
            amount=75000,  # $750.00
            currency="USD",
            status="pending",
            issue_date=datetime.now(UTC),
            due_date=datetime.now(UTC) + timedelta(days=30),
            duplicate_hash=hashlib.sha256(b"INV-2024-002-acme").hexdigest(),
            extracted_entities={
                "vendor": "Acme Corporation",
                "line_items": [{"description": "Service C", "quantity": 5, "unit_price": 1500}],
            },
            data={
                "payment_method": "check",
            },
        )

        invoice3 = Invoice(
            id=uuid4(),
            client_id=client2.id,
            invoice_number="INV-2024-003",
            amount=50000,  # $500.00
            currency="USD",
            status="draft",
            issue_date=datetime.now(UTC),
            due_date=datetime.now(UTC) + timedelta(days=45),
            extracted_entities={
                "vendor": "TechStart Inc",
                "line_items": [
                    {"description": "Cloud Services", "quantity": 1, "unit_price": 50000}
                ],
            },
            data={"project_code": "PROJ-2024-001"},
        )

        session.add(invoice1)
        session.add(invoice2)
        session.add(invoice3)
        await session.flush()

        # Create sample contracts
        contract1 = Contract(
            id=uuid4(),
            client_id=client1.id,
            contract_number="CTR-2024-001",
            title="Service Agreement - 2024",
            status="active",
            start_date=datetime.now(UTC) - timedelta(days=90),
            end_date=datetime.now(UTC) + timedelta(days=270),
            extracted_entities={
                "parties": ["Acme Corporation", "Service Provider"],
                "payment_terms": "Net 30",
            },
            rule_references={
                "rules": ["PAYMENT_TERMS", "SERVICE_LEVEL", "TERMINATION"],
            },
            data={
                "contract_type": "service_agreement",
                "jurisdiction": "Colorado",
            },
        )

        contract2 = Contract(
            id=uuid4(),
            client_id=client2.id,
            contract_number="CTR-2024-002",
            title="Consulting Services - Q1 2024",
            status="draft",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC) + timedelta(days=90),
            extracted_entities={
                "parties": ["TechStart Inc", "Consulting Firm"],
                "scope": "Technical Advisory",
            },
            rule_references={
                "rules": ["NDA", "IP_OWNERSHIP", "CONFIDENTIALITY"],
            },
            data={
                "contract_type": "consulting",
                "jurisdiction": "California",
            },
        )

        session.add(contract1)
        session.add(contract2)
        await session.flush()

        # Create sample audit results
        audit_result1 = AuditResult(
            id=uuid4(),
            invoice_id=invoice1.id,
            contract_id=None,
            rule_id="PAYMENT_TERMS",
            status="passed",
            extracted_entities={"terms": "Net 30", "currency": "USD"},
            variance_metrics={
                "amount_variance_percent": 0.0,
                "date_variance_days": 0,
            },
            rule_references={
                "rule_name": "Payment Terms Validation",
                "version": "1.0",
            },
            findings={
                "validation_passed": True,
                "message": "Invoice payment terms match contract",
            },
        )

        audit_result2 = AuditResult(
            id=uuid4(),
            invoice_id=invoice2.id,
            contract_id=None,
            rule_id="AMOUNT_VALIDATION",
            status="failed",
            extracted_entities={"expected_amount": 75000, "actual_amount": 75000},
            variance_metrics={
                "amount_variance_percent": 0.0,
                "date_variance_days": 0,
            },
            rule_references={
                "rule_name": "Amount Validation",
                "version": "1.0",
            },
            findings={
                "validation_passed": False,
                "message": "Amount exceeds expected range",
                "exceeded_by": 0,
            },
        )

        audit_result3 = AuditResult(
            id=uuid4(),
            invoice_id=None,
            contract_id=contract1.id,
            rule_id="SERVICE_LEVEL",
            status="pending",
            extracted_entities={"sla_response_time": "24 hours"},
            variance_metrics={},
            rule_references={
                "rule_name": "Service Level Agreement",
                "version": "1.0",
            },
            findings={
                "validation_pending": True,
                "message": "Awaiting service level metrics",
            },
        )

        session.add(audit_result1)
        session.add(audit_result2)
        session.add(audit_result3)
        await session.flush()

        # Create sample audit logs
        audit_log1 = AuditLog(
            id=uuid4(),
            client_id=client1.id,
            entity_type="invoice",
            entity_id=invoice1.id,
            action="created",
            status="success",
            changes={
                "invoice_number": "INV-2024-001",
                "amount": 150000,
            },
            data={"user_id": "user-001", "ip_address": "192.168.1.1"},
        )

        audit_log2 = AuditLog(
            id=uuid4(),
            client_id=client1.id,
            entity_type="invoice",
            entity_id=invoice1.id,
            action="updated",
            status="success",
            changes={
                "status": ["draft", "paid"],
            },
            data={"user_id": "user-002", "ip_address": "192.168.1.2"},
        )

        audit_log3 = AuditLog(
            id=uuid4(),
            client_id=client2.id,
            entity_type="contract",
            entity_id=contract2.id,
            action="created",
            status="success",
            changes={
                "contract_number": "CTR-2024-002",
                "status": "draft",
            },
            data={"user_id": "user-001", "ip_address": "192.168.1.3"},
        )

        session.add(audit_log1)
        session.add(audit_log2)
        session.add(audit_log3)

        await session.commit()
        print("✓ Sample data seeded successfully")


async def main():
    """Main function."""
    print("Creating tables...")
    await create_tables()
    print("✓ Tables created")

    print("Seeding sample data...")
    await seed_data()


if __name__ == "__main__":
    asyncio.run(main())
