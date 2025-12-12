"""Tests for database models and CRUD operations."""

import hashlib
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.crud import (
    audit_log_crud,
    audit_result_crud,
    client_crud,
    contract_crud,
    invoice_crud,
)
from app.database import Base
from app.models import AuditLog, AuditResult, Client, Contract, Invoice


@pytest.fixture
async def db_session():
    """Create async database session for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()


class TestClientCRUD:
    """Test Client CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_client(self, db_session: AsyncSession):
        """Test creating a client."""
        client_data = {
            "id": uuid4(),
            "name": "Test Client",
            "email": "test@example.com",
            "phone": "+1-555-0101",
            "address": "123 Main St",
            "metadata": {"key": "value"},
        }

        client = await client_crud.create(db_session, client_data)

        assert client.id == client_data["id"]
        assert client.name == "Test Client"
        assert client.email == "test@example.com"
        assert client.metadata == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_client(self, db_session: AsyncSession):
        """Test getting a client by id."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }

        await client_crud.create(db_session, client_data)
        retrieved_client = await client_crud.get(db_session, client_id)

        assert retrieved_client is not None
        assert retrieved_client.name == "Test Client"

    @pytest.mark.asyncio
    async def test_get_client_by_email(self, db_session: AsyncSession):
        """Test getting a client by email."""
        client_data = {
            "id": uuid4(),
            "name": "Test Client",
            "email": "unique@example.com",
        }

        await client_crud.create(db_session, client_data)
        retrieved_client = await client_crud.get_by_email(
            db_session, "unique@example.com"
        )

        assert retrieved_client is not None
        assert retrieved_client.email == "unique@example.com"

    @pytest.mark.asyncio
    async def test_get_all_clients(self, db_session: AsyncSession):
        """Test getting all clients."""
        for i in range(3):
            client_data = {
                "id": uuid4(),
                "name": f"Client {i}",
                "email": f"client{i}@example.com",
            }
            await client_crud.create(db_session, client_data)

        clients = await client_crud.get_all(db_session)

        assert len(clients) == 3

    @pytest.mark.asyncio
    async def test_update_client(self, db_session: AsyncSession):
        """Test updating a client."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Original Name",
            "email": "test@example.com",
        }

        client = await client_crud.create(db_session, client_data)

        update_data = {"name": "Updated Name", "phone": "+1-555-9999"}
        updated_client = await client_crud.update(db_session, client, update_data)

        assert updated_client.name == "Updated Name"
        assert updated_client.phone == "+1-555-9999"

    @pytest.mark.asyncio
    async def test_delete_client(self, db_session: AsyncSession):
        """Test deleting a client."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }

        await client_crud.create(db_session, client_data)
        await client_crud.delete(db_session, client_id)

        deleted_client = await client_crud.get(db_session, client_id)
        assert deleted_client is None


class TestInvoiceCRUD:
    """Test Invoice CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_invoice(self, db_session: AsyncSession):
        """Test creating an invoice."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }
        await client_crud.create(db_session, client_data)

        invoice_data = {
            "id": uuid4(),
            "client_id": client_id,
            "invoice_number": "INV-001",
            "amount": 10000,
            "currency": "USD",
            "status": "pending",
            "issue_date": datetime.now(UTC),
            "due_date": datetime.now(UTC) + timedelta(days=30),
            "duplicate_hash": hashlib.sha256(b"INV-001").hexdigest(),
            "extracted_entities": {"vendor": "Test"},
        }

        invoice = await invoice_crud.create(db_session, invoice_data)

        assert invoice.invoice_number == "INV-001"
        assert invoice.amount == 10000
        assert invoice.status == "pending"

    @pytest.mark.asyncio
    async def test_get_invoice_by_client_id(self, db_session: AsyncSession):
        """Test getting invoices by client id."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }
        await client_crud.create(db_session, client_data)

        for i in range(3):
            invoice_data = {
                "id": uuid4(),
                "client_id": client_id,
                "invoice_number": f"INV-{i:03d}",
                "amount": 10000 * (i + 1),
                "status": "pending",
                "issue_date": datetime.now(UTC),
            }
            await invoice_crud.create(db_session, invoice_data)

        invoices = await invoice_crud.get_by_client_id(db_session, client_id)

        assert len(invoices) == 3

    @pytest.mark.asyncio
    async def test_get_invoice_by_status(self, db_session: AsyncSession):
        """Test getting invoices by status."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }
        await client_crud.create(db_session, client_data)

        invoice_data1 = {
            "id": uuid4(),
            "client_id": client_id,
            "invoice_number": "INV-001",
            "amount": 10000,
            "status": "paid",
            "issue_date": datetime.now(UTC),
        }
        await invoice_crud.create(db_session, invoice_data1)

        invoice_data2 = {
            "id": uuid4(),
            "client_id": client_id,
            "invoice_number": "INV-002",
            "amount": 20000,
            "status": "pending",
            "issue_date": datetime.now(UTC),
        }
        await invoice_crud.create(db_session, invoice_data2)

        paid_invoices = await invoice_crud.get_by_status(db_session, "paid")
        assert len(paid_invoices) == 1
        assert paid_invoices[0].status == "paid"

    @pytest.mark.asyncio
    async def test_update_invoice(self, db_session: AsyncSession):
        """Test updating an invoice."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }
        await client_crud.create(db_session, client_data)

        invoice_data = {
            "id": uuid4(),
            "client_id": client_id,
            "invoice_number": "INV-001",
            "amount": 10000,
            "status": "pending",
            "issue_date": datetime.now(UTC),
        }
        invoice = await invoice_crud.create(db_session, invoice_data)

        update_data = {"status": "paid", "amount": 15000}
        updated_invoice = await invoice_crud.update(db_session, invoice, update_data)

        assert updated_invoice.status == "paid"
        assert updated_invoice.amount == 15000


class TestContractCRUD:
    """Test Contract CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_contract(self, db_session: AsyncSession):
        """Test creating a contract."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }
        await client_crud.create(db_session, client_data)

        contract_data = {
            "id": uuid4(),
            "client_id": client_id,
            "contract_number": "CTR-001",
            "title": "Test Contract",
            "status": "active",
            "start_date": datetime.now(UTC),
            "end_date": datetime.now(UTC) + timedelta(days=365),
            "extracted_entities": {"parties": ["Party A", "Party B"]},
            "rule_references": {"rules": ["RULE1", "RULE2"]},
        }

        contract = await contract_crud.create(db_session, contract_data)

        assert contract.contract_number == "CTR-001"
        assert contract.title == "Test Contract"
        assert contract.status == "active"

    @pytest.mark.asyncio
    async def test_get_contract_by_client_id(self, db_session: AsyncSession):
        """Test getting contracts by client id."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }
        await client_crud.create(db_session, client_data)

        for i in range(2):
            contract_data = {
                "id": uuid4(),
                "client_id": client_id,
                "contract_number": f"CTR-{i:03d}",
                "title": f"Contract {i}",
                "status": "active",
                "start_date": datetime.now(UTC),
            }
            await contract_crud.create(db_session, contract_data)

        contracts = await contract_crud.get_by_client_id(db_session, client_id)

        assert len(contracts) == 2


class TestAuditResultCRUD:
    """Test AuditResult CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_audit_result_for_invoice(self, db_session: AsyncSession):
        """Test creating an audit result for invoice."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }
        await client_crud.create(db_session, client_data)

        invoice_data = {
            "id": uuid4(),
            "client_id": client_id,
            "invoice_number": "INV-001",
            "amount": 10000,
            "status": "pending",
            "issue_date": datetime.now(UTC),
        }
        invoice = await invoice_crud.create(db_session, invoice_data)

        audit_data = {
            "id": uuid4(),
            "invoice_id": invoice.id,
            "contract_id": None,
            "rule_id": "RULE_001",
            "status": "passed",
            "extracted_entities": {"test": "data"},
            "variance_metrics": {"variance": 0.0},
        }

        audit_result = await audit_result_crud.create(db_session, audit_data)

        assert audit_result.invoice_id == invoice.id
        assert audit_result.rule_id == "RULE_001"
        assert audit_result.status == "passed"

    @pytest.mark.asyncio
    async def test_get_audit_results_by_invoice_id(self, db_session: AsyncSession):
        """Test getting audit results by invoice id."""
        client_id = uuid4()
        client_data = {
            "id": client_id,
            "name": "Test Client",
            "email": "test@example.com",
        }
        await client_crud.create(db_session, client_data)

        invoice_data = {
            "id": uuid4(),
            "client_id": client_id,
            "invoice_number": "INV-001",
            "amount": 10000,
            "status": "pending",
            "issue_date": datetime.now(UTC),
        }
        invoice = await invoice_crud.create(db_session, invoice_data)

        for i in range(2):
            audit_data = {
                "id": uuid4(),
                "invoice_id": invoice.id,
                "rule_id": f"RULE_{i:03d}",
                "status": "passed",
            }
            await audit_result_crud.create(db_session, audit_data)

        results = await audit_result_crud.get_by_invoice_id(db_session, invoice.id)

        assert len(results) == 2


class TestAuditLogCRUD:
    """Test AuditLog CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_audit_log(self, db_session: AsyncSession):
        """Test creating an audit log."""
        client_id = uuid4()
        entity_id = uuid4()

        audit_log_data = {
            "id": uuid4(),
            "client_id": client_id,
            "entity_type": "invoice",
            "entity_id": entity_id,
            "action": "created",
            "status": "success",
            "changes": {"field": "value"},
        }

        audit_log = await audit_log_crud.create(db_session, audit_log_data)

        assert audit_log.entity_type == "invoice"
        assert audit_log.action == "created"
        assert audit_log.status == "success"

    @pytest.mark.asyncio
    async def test_get_audit_logs_by_client_id(self, db_session: AsyncSession):
        """Test getting audit logs by client id."""
        client_id = uuid4()

        for i in range(3):
            audit_log_data = {
                "id": uuid4(),
                "client_id": client_id,
                "entity_type": "invoice",
                "entity_id": uuid4(),
                "action": "created",
                "status": "success",
            }
            await audit_log_crud.create(db_session, audit_log_data)

        logs = await audit_log_crud.get_by_client_id(db_session, client_id)

        assert len(logs) == 3

    @pytest.mark.asyncio
    async def test_get_audit_logs_by_entity_id(self, db_session: AsyncSession):
        """Test getting audit logs by entity id."""
        entity_id = uuid4()

        for i in range(2):
            audit_log_data = {
                "id": uuid4(),
                "client_id": uuid4(),
                "entity_type": "invoice",
                "entity_id": entity_id,
                "action": "created" if i == 0 else "updated",
                "status": "success",
            }
            await audit_log_crud.create(db_session, audit_log_data)

        logs = await audit_log_crud.get_by_entity_id(db_session, entity_id)

        assert len(logs) == 2
        assert logs[0].action == "created"
        assert logs[1].action == "updated"
