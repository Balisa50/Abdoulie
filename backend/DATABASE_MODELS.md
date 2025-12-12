# Database Models and Schema

This document describes the database layer implementation for the Tesseract SaaS MVP backend.

## Overview

The database layer consists of:
- **SQLAlchemy ORM Models** - Define entity structures and relationships
- **Alembic Migrations** - Version control for database schema
- **Pydantic Schemas** - Validation and serialization for API
- **CRUD Operations** - Simplified database interaction patterns
- **Sample Seed Data** - Pre-populated data for testing

## File Structure

```
backend/
├── app/
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── crud.py            # CRUD operation classes
│   ├── database.py        # Database engine and session management
│   └── seed.py            # Sample data seeding script
├── migrations/
│   ├── versions/
│   │   └── 001_create_initial_schema.py  # Initial migration
│   ├── env.py             # Alembic environment configuration
│   └── README             # Migration usage guide
└── tests/
    ├── test_models.py     # Model CRUD operation tests
    └── conftest.py        # Test fixtures
```

## Models

### Client

Represents a customer or organization.

```python
class Client(Base):
    id: UUID                    # Primary key
    name: str                   # Company name
    email: str                  # Contact email (unique)
    phone: str | None           # Contact phone
    address: str | None         # Physical address
    data: dict | None           # Custom JSON data
    created_at: datetime        # Creation timestamp
    updated_at: datetime        # Last update timestamp
```

**Relationships:**
- `invoices` (1:M) - Client's invoices
- `contracts` (1:M) - Client's contracts
- `audit_logs` (1:M) - Client's audit trail

**Indexes:**
- `email` - For unique lookups

---

### Invoice

Represents an invoice document.

```python
class Invoice(Base):
    id: UUID                        # Primary key
    client_id: UUID                 # Client reference
    invoice_number: str             # Unique invoice identifier
    amount: int                     # Amount in cents
    currency: str                   # ISO currency code (default: USD)
    status: str                     # draft, pending, paid, etc.
    issue_date: datetime            # Date invoice was issued
    due_date: datetime | None       # Payment due date
    duplicate_hash: str | None      # SHA256 for duplicate detection
    extracted_entities: dict | None # Extracted data from parsing
    data: dict | None               # Additional invoice data
    created_at: datetime            # Creation timestamp
    updated_at: datetime            # Last update timestamp
```

**Relationships:**
- `client` (M:1) - Parent client
- `audit_results` (1:M) - Audit results for this invoice

**Indexes:**
- `client_id` - Filter by client
- `status` - Filter by status
- `issue_date` - Filter by date
- `duplicate_hash` - Detect duplicates

---

### Contract

Represents a contract or agreement.

```python
class Contract(Base):
    id: UUID                        # Primary key
    client_id: UUID                 # Client reference
    contract_number: str            # Unique contract identifier
    title: str                      # Contract title
    status: str                     # draft, active, expired, etc.
    start_date: datetime            # Contract start date
    end_date: datetime | None       # Contract end date
    extracted_entities: dict | None # Extracted contract data
    rule_references: dict | None    # Referenced validation rules
    data: dict | None               # Additional contract data
    created_at: datetime            # Creation timestamp
    updated_at: datetime            # Last update timestamp
```

**Relationships:**
- `client` (M:1) - Parent client
- `audit_results` (1:M) - Audit results for this contract

**Indexes:**
- `client_id` - Filter by client
- `status` - Filter by status

---

### AuditResult

Represents the result of an audit/validation rule.

```python
class AuditResult(Base):
    id: UUID                        # Primary key
    invoice_id: UUID | None         # Related invoice (if applicable)
    contract_id: UUID | None        # Related contract (if applicable)
    rule_id: str                    # Rule identifier
    status: str                     # pending, passed, failed
    extracted_entities: dict | None # Data extracted during audit
    variance_metrics: dict | None   # Variance/deviation metrics
    rule_references: dict | None    # Rule definition details
    findings: dict | None           # Detailed findings from audit
    created_at: datetime            # Creation timestamp
    updated_at: datetime            # Last update timestamp
```

**Relationships:**
- `invoice` (M:1, optional) - Parent invoice
- `contract` (M:1, optional) - Parent contract

**Indexes:**
- `invoice_id` - Filter by invoice
- `contract_id` - Filter by contract
- `rule_id` - Filter by rule
- `status` - Filter by status

---

### AuditLog

Audit trail for tracking all entity changes.

```python
class AuditLog(Base):
    id: UUID                   # Primary key
    client_id: UUID | None     # Associated client (if applicable)
    entity_type: str           # Type: invoice, contract, audit_result
    entity_id: UUID            # Entity being logged
    action: str                # created, updated, deleted
    status: str                # success, error
    changes: dict | None       # Details of what changed
    error_message: str | None  # Error details if status is error
    data: dict | None          # Context: user_id, ip_address, etc.
    created_at: datetime       # Action timestamp
```

**Relationships:**
- `client` (M:1, optional) - Associated client

**Indexes:**
- `client_id` - Filter by client
- `entity_type` - Filter by entity type
- `entity_id` - Find all logs for an entity
- `action` - Filter by action type
- `status` - Filter by status
- `created_at` - Time-based queries

---

## Database Connection

### Configuration

Database connection is configured in `app/settings.py`:

```python
# Environment variable
DATABASE_URL = "postgresql+asyncpg://user:password@host:5432/dbname"

# Default development URL
DATABASE_URL = "postgresql+asyncpg://tesseract:tesseract@postgres:5432/tesseract"
```

### Engine Setup

`app/database.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## CRUD Operations

### Usage Pattern

```python
from app.crud import client_crud, invoice_crud
from app.database import AsyncSessionLocal

async with AsyncSessionLocal() as db:
    # Create
    client = await client_crud.create(db, {
        "name": "Acme Corp",
        "email": "contact@acme.com"
    })
    
    # Read
    client = await client_crud.get(db, client_id)
    
    # Update
    client = await client_crud.update(db, client, {
        "name": "Acme Corporation"
    })
    
    # Delete
    await client_crud.delete(db, client_id)
    
    # Query
    invoices = await invoice_crud.get_by_client_id(db, client_id)
    pending = await invoice_crud.get_by_status(db, "pending")
```

### Available CRUD Classes

- `client_crud` (CRUDClient)
  - `create()`, `get()`, `get_all()`, `update()`, `delete()`
  - `get_by_email()`

- `invoice_crud` (CRUDInvoice)
  - `create()`, `get()`, `get_all()`, `update()`, `delete()`
  - `get_by_invoice_number()`, `get_by_client_id()`, `get_by_status()`

- `contract_crud` (CRUDContract)
  - `create()`, `get()`, `get_all()`, `update()`, `delete()`
  - `get_by_contract_number()`, `get_by_client_id()`

- `audit_result_crud` (CRUDAuditResult)
  - `create()`, `get()`, `get_all()`, `update()`, `delete()`
  - `get_by_invoice_id()`, `get_by_contract_id()`

- `audit_log_crud` (CRUDAuditLog)
  - `create()`, `get()`, `get_all()`, `update()`, `delete()`
  - `get_by_client_id()`, `get_by_entity_id()`

---

## Pydantic Schemas

Each model has three schema classes:

### Pattern

```python
# Base schema - common fields
class EntityBase(BaseModel):
    field1: str
    field2: int | None = None

# Create schema - input for POST
class EntityCreate(EntityBase):
    pass

# Update schema - input for PATCH
class EntityUpdate(BaseModel):
    field1: str | None = None
    field2: int | None = None

# Response schema - output from API
class EntityResponse(EntityBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime
```

### Available Schemas

**Client:**
- `ClientCreate` / `ClientUpdate` / `ClientResponse`

**Invoice:**
- `InvoiceCreate` / `InvoiceUpdate` / `InvoiceResponse`

**Contract:**
- `ContractCreate` / `ContractUpdate` / `ContractResponse`

**AuditResult:**
- `AuditResultCreate` / `AuditResultUpdate` / `AuditResultResponse`

**AuditLog:**
- `AuditLogCreate` / `AuditLogResponse`

---

## Migrations

### Managing Migrations

Create a new migration after changing models:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply all migrations:

```bash
alembic upgrade head
```

Rollback one migration:

```bash
alembic downgrade -1
```

View migration history:

```bash
alembic history
```

### Current Migrations

- `001_create_initial_schema.py` - Creates all core tables

---

## Seeding Sample Data

### Generate Sample Data

```bash
cd backend
python -m app.seed
```

Creates:
- 2 clients with detailed metadata
- 3 invoices with extracted entities
- 2 contracts with rule references
- 3 audit results with different statuses
- 3 audit logs showing entity changes

### Seed Data Structure

The seed script populates realistic test data:

```python
# Sample client with metadata
Client(
    name="Acme Corporation",
    email="contact@acme.com",
    data={
        "industry": "Manufacturing",
        "employees": 500,
        "founded": 1995
    }
)

# Sample invoice with extracted data
Invoice(
    invoice_number="INV-2024-001",
    amount=150000,  # $1500.00
    extracted_entities={
        "vendor": "Acme Corporation",
        "line_items": [
            {"description": "Service A", "quantity": 10, "unit_price": 1000}
        ]
    }
)

# Sample contract with rules
Contract(
    contract_number="CTR-2024-001",
    rule_references={
        "rules": ["PAYMENT_TERMS", "SERVICE_LEVEL", "TERMINATION"]
    }
)
```

---

## Testing

### Run Tests

```bash
# All tests
pytest

# Specific test class
pytest tests/test_models.py::TestClientCRUD

# Specific test
pytest tests/test_models.py::TestClientCRUD::test_create_client -xvs

# With coverage
pytest --cov=app tests/
```

### Test Coverage

Current tests cover:

- **ClientCRUD** (6 tests)
  - Create, read, update, delete, list, get by email

- **InvoiceCRUD** (4 tests)
  - Create, read, update, list, get by client, get by status

- **ContractCRUD** (2 tests)
  - Create, read, list, get by client

- **AuditResultCRUD** (2 tests)
  - Create, read, list, get by invoice, get by contract

- **AuditLogCRUD** (3 tests)
  - Create, read, list, get by client, get by entity

**Total: 17 tests covering basic CRUD for all entities**

---

## Data Types and Conventions

### UUIDs

All primary and foreign keys use UUID (uuid4):

```python
id = Column(Uuid, primary_key=True, default=uuid.uuid4)
client_id = Column(Uuid, ForeignKey("clients.id"), nullable=False)
```

### Timestamps

All timestamps use timezone-aware UTC:

```python
from datetime import UTC, datetime

created_at = Column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda: datetime.now(UTC)
)
```

### JSON Columns

All JSON columns are nullable and store flexible data:

```python
data = Column(JSON, nullable=True)  # Stores dict[str, Any]
```

### Amounts

Invoice amounts are stored in cents (integers) to avoid float precision issues:

```python
amount = Column(Integer, nullable=False)  # Amount in cents
# Example: $15.00 is stored as 1500
```

### Status Fields

Status fields use VARCHAR(50) for flexibility:

```python
status = Column(String(50), nullable=False, default="draft")
# Possible values: draft, pending, paid, expired, active, completed, etc.
```

---

## Performance Optimization

### Indexes

All frequently queried columns are indexed:
- Foreign keys (client_id, invoice_id, contract_id)
- Status fields
- Date fields
- Unique identifiers

### Pagination

All list queries support offset/limit pagination:

```python
items = await crud.get_all(db, skip=0, limit=100)
items = await invoice_crud.get_by_client_id(db, client_id, skip=20, limit=50)
```

### Async/Await

All database operations are async for non-blocking I/O:

```python
async def get_invoices(db: AsyncSession, client_id: UUID):
    invoices = await invoice_crud.get_by_client_id(db, client_id)
    return invoices
```

---

## Common Patterns

### Create with Relationships

```python
# Create client
client = await client_crud.create(db, {
    "name": "Acme Corp",
    "email": "contact@acme.com"
})

# Create invoice for client
invoice = await invoice_crud.create(db, {
    "client_id": client.id,
    "invoice_number": "INV-001",
    "amount": 50000,
    "issue_date": datetime.now(UTC)
})

# Create audit result
result = await audit_result_crud.create(db, {
    "invoice_id": invoice.id,
    "rule_id": "PAYMENT_TERMS",
    "status": "passed"
})
```

### Audit Entity Changes

```python
# Log entity creation
await audit_log_crud.create(db, {
    "client_id": client.id,
    "entity_type": "invoice",
    "entity_id": invoice.id,
    "action": "created",
    "changes": {"invoice_number": "INV-001"}
})

# Log entity update
await audit_log_crud.create(db, {
    "entity_type": "invoice",
    "entity_id": invoice.id,
    "action": "updated",
    "changes": {"status": ["draft", "paid"]}
})
```

---

## Troubleshooting

### Connection Issues

```python
# Check database URL
from app.settings import settings
print(settings.database_url)

# Test connection
async with engine.connect() as conn:
    await conn.execute(text("SELECT 1"))
```

### Migration Issues

```bash
# View current revision
alembic current

# View all revisions
alembic history

# Downgrade to specific revision
alembic downgrade 001
```

### Type Hints

Enable strict type checking:

```bash
mypy app/ --strict
```

---

## Future Enhancements

- Soft deletes with `deleted_at` column
- Entity versioning and history tracking
- Full-text search indexes
- Partitioning for large tables
- Webhook/event audit logging
- Row-level security for multi-tenancy
