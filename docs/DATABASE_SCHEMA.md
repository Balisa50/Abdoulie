# Database Schema Documentation

This document describes the Tesseract SaaS MVP database schema, including all tables, columns, relationships, and indexes.

## Overview

The database is built on PostgreSQL with SQLAlchemy ORM and Alembic for migrations. All tables use UUIDs as primary keys and include timestamp tracking for audit purposes.

## Tables

### Clients

Stores core client/customer information.

**Table Name:** `clients`

**Columns:**
- `id` (UUID, PK) - Unique identifier
- `name` (VARCHAR 255, NOT NULL) - Client company name
- `email` (VARCHAR 255, NOT NULL, UNIQUE) - Contact email
- `phone` (VARCHAR 20) - Contact phone number
- `address` (TEXT) - Physical address
- `metadata` (JSON) - Flexible metadata storage
- `created_at` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Creation timestamp
- `updated_at` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Last update timestamp

**Indexes:**
- `ix_clients_email` - Email lookup

**Relationships:**
- One-to-Many: invoices
- One-to-Many: contracts
- One-to-Many: audit_logs

---

### Invoices

Stores invoice data with client associations and extracted entity information.

**Table Name:** `invoices`

**Columns:**
- `id` (UUID, PK) - Unique identifier
- `client_id` (UUID, FK) - Reference to client
- `invoice_number` (VARCHAR 100, NOT NULL, UNIQUE) - Invoice identifier
- `amount` (INTEGER, NOT NULL) - Amount in cents
- `currency` (VARCHAR 3, NOT NULL, DEFAULT 'USD') - Currency code
- `status` (VARCHAR 50, NOT NULL, DEFAULT 'draft') - Invoice status (draft, pending, paid, etc.)
- `issue_date` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Invoice issue date
- `due_date` (TIMESTAMP WITH TIMEZONE) - Payment due date
- `duplicate_hash` (VARCHAR 64) - SHA256 hash for duplicate detection
- `extracted_entities` (JSON) - Extracted entities (vendor, line items, etc.)
- `metadata` (JSON) - Additional flexible data
- `created_at` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Creation timestamp
- `updated_at` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Last update timestamp

**Indexes:**
- `ix_invoices_client_id` - Client lookup
- `ix_invoices_status` - Status filtering
- `ix_invoices_issue_date` - Date filtering
- `ix_invoices_duplicate_hash` - Duplicate detection

**Relationships:**
- Many-to-One: client
- One-to-Many: audit_results

---

### Contracts

Stores contract information with rule references and extracted entities.

**Table Name:** `contracts`

**Columns:**
- `id` (UUID, PK) - Unique identifier
- `client_id` (UUID, FK) - Reference to client
- `contract_number` (VARCHAR 100, NOT NULL, UNIQUE) - Contract identifier
- `title` (VARCHAR 255, NOT NULL) - Contract title
- `status` (VARCHAR 50, NOT NULL, DEFAULT 'draft') - Contract status (draft, active, expired, etc.)
- `start_date` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Contract start date
- `end_date` (TIMESTAMP WITH TIMEZONE) - Contract end date
- `extracted_entities` (JSON) - Extracted entities (parties, payment terms, etc.)
- `rule_references` (JSON) - References to applicable rules
- `metadata` (JSON) - Additional flexible data
- `created_at` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Creation timestamp
- `updated_at` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Last update timestamp

**Indexes:**
- `ix_contracts_client_id` - Client lookup
- `ix_contracts_status` - Status filtering

**Relationships:**
- Many-to-One: client
- One-to-Many: audit_results

---

### Audit Results

Stores audit/validation results for invoices and contracts.

**Table Name:** `audit_results`

**Columns:**
- `id` (UUID, PK) - Unique identifier
- `invoice_id` (UUID, FK, NULLABLE) - Reference to invoice (if applicable)
- `contract_id` (UUID, FK, NULLABLE) - Reference to contract (if applicable)
- `rule_id` (VARCHAR 100, NOT NULL) - Identifier of rule being audited
- `status` (VARCHAR 50, NOT NULL, DEFAULT 'pending') - Audit status (pending, passed, failed)
- `extracted_entities` (JSON) - Extracted entities from audit
- `variance_metrics` (JSON) - Variance/deviation metrics
- `rule_references` (JSON) - Details about the rule applied
- `findings` (JSON) - Detailed audit findings
- `created_at` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Creation timestamp
- `updated_at` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Last update timestamp

**Indexes:**
- `ix_audit_results_invoice_id` - Invoice lookup
- `ix_audit_results_contract_id` - Contract lookup
- `ix_audit_results_rule_id` - Rule lookup
- `ix_audit_results_status` - Status filtering

**Relationships:**
- Many-to-One: invoice (optional)
- Many-to-One: contract (optional)

---

### Audit Logs

Stores audit trail of all entity changes for compliance and debugging.

**Table Name:** `audit_logs`

**Columns:**
- `id` (UUID, PK) - Unique identifier
- `client_id` (UUID, FK, NULLABLE) - Reference to client (if applicable)
- `entity_type` (VARCHAR 100, NOT NULL) - Type of entity (invoice, contract, audit_result)
- `entity_id` (UUID, NOT NULL) - ID of the entity being logged
- `action` (VARCHAR 50, NOT NULL) - Action performed (created, updated, deleted)
- `status` (VARCHAR 50, NOT NULL, DEFAULT 'success') - Status of action (success, error)
- `changes` (JSON) - Details of changes made
- `error_message` (TEXT) - Error details if status is error
- `metadata` (JSON) - Additional context (user_id, ip_address, etc.)
- `created_at` (TIMESTAMP WITH TIMEZONE, NOT NULL) - Timestamp of action

**Indexes:**
- `ix_audit_logs_client_id` - Client lookup
- `ix_audit_logs_entity_type` - Entity type filtering
- `ix_audit_logs_entity_id` - Entity lookup
- `ix_audit_logs_action` - Action filtering
- `ix_audit_logs_status` - Status filtering
- `ix_audit_logs_created_at` - Time-based queries

**Relationships:**
- Many-to-One: client (optional)

---

## Data Types

### UUID
All primary keys and foreign keys use UUID (Universally Unique Identifier) to ensure globally unique identifiers across distributed systems.

### JSON (JSONB in PostgreSQL)
JSON columns provide flexible storage for semi-structured data:
- `extracted_entities` - Stores extracted data from OCR/parsing
- `metadata` - Custom fields and extended attributes
- `variance_metrics` - Numerical variance data
- `rule_references` - Rule definitions and configurations
- `changes` - Change history in audit logs
- `findings` - Audit findings and details

### Timestamps
All timestamp columns use `TIMESTAMP WITH TIMEZONE` to handle different timezones correctly and support global operations.

---

## Relationships and Constraints

### Foreign Key Constraints
- `invoices.client_id` → `clients.id` (CASCADE DELETE)
- `contracts.client_id` → `clients.id` (CASCADE DELETE)
- `audit_results.invoice_id` → `invoices.id` (CASCADE DELETE)
- `audit_results.contract_id` → `contracts.id` (CASCADE DELETE)
- `audit_logs.client_id` → `clients.id` (CASCADE DELETE)

### Unique Constraints
- `clients.email` - One email per client
- `invoices.invoice_number` - One invoice number globally
- `contracts.contract_number` - One contract number globally

---

## Indexing Strategy

The schema includes indexes on:

1. **Foreign Keys** - For efficient joins
   - `invoices.client_id`
   - `contracts.client_id`
   - `audit_results.invoice_id`
   - `audit_results.contract_id`
   - `audit_logs.client_id`

2. **Filtering Columns** - For WHERE clauses
   - `clients.email`
   - `invoices.status`
   - `contracts.status`
   - `audit_results.status`
   - `audit_logs.status`, `entity_type`, `action`

3. **Date Range Queries** - For time-based searches
   - `invoices.issue_date`
   - `audit_logs.created_at`

4. **Business Logic** - For duplicate detection
   - `invoices.duplicate_hash`

---

## Usage Examples

### Creating a Client with Invoices

```python
from app.crud import client_crud, invoice_crud
from app.schemas import ClientCreate, InvoiceCreate

# Create client
client_data = ClientCreate(
    name="ACME Corp",
    email="contact@acme.com",
    phone="+1-555-0101",
    metadata={"industry": "Manufacturing"}
)
client = await client_crud.create(db, client_data.model_dump())

# Create invoice for client
invoice_data = InvoiceCreate(
    client_id=client.id,
    invoice_number="INV-001",
    amount=50000,
    issue_date=datetime.now(UTC)
)
invoice = await invoice_crud.create(db, invoice_data.model_dump())
```

### Querying Invoices by Client

```python
invoices = await invoice_crud.get_by_client_id(db, client_id)
pending_invoices = await invoice_crud.get_by_status(db, "pending")
```

### Audit Trail

```python
from app.crud import audit_log_crud
from app.schemas import AuditLogCreate

# Log an action
log_data = AuditLogCreate(
    client_id=client.id,
    entity_type="invoice",
    entity_id=invoice.id,
    action="created",
    changes={"invoice_number": "INV-001"}
)
await audit_log_crud.create(db, log_data.model_dump())

# Query logs
logs = await audit_log_crud.get_by_entity_id(db, invoice.id)
```

---

## Migration Management

### Applying Migrations

```bash
cd backend
alembic upgrade head
```

### Creating New Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Viewing Migration History

```bash
cd backend
alembic history
```

---

## Performance Considerations

1. **JSON Indexing** - Use GIN indexes on JSON columns for frequently queried fields:
   ```sql
   CREATE INDEX idx_invoices_extracted_entities 
   ON invoices USING GIN (extracted_entities);
   ```

2. **Composite Indexes** - Consider adding composite indexes for common filter combinations:
   ```sql
   CREATE INDEX idx_invoices_client_status 
   ON invoices(client_id, status);
   ```

3. **Partitioning** - For large tables, consider partitioning by date:
   ```sql
   CREATE TABLE invoices_2024
   PARTITION OF invoices
   FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
   ```

---

## Security Considerations

1. **Sensitive Data** - Store sensitive information (API keys, passwords) in `.env`, not in database metadata
2. **Audit Logs** - Review `audit_logs` table regularly for suspicious activity
3. **Access Control** - Implement row-level security (RLS) in PostgreSQL for multi-tenant support
4. **Data Retention** - Implement archival/deletion policies for old audit logs

---

## Backup and Recovery

1. **Regular Backups** - Schedule daily backups
   ```bash
   pg_dump -U tesseract -h localhost tesseract > backup.sql
   ```

2. **Recovery**
   ```bash
   psql -U tesseract -h localhost tesseract < backup.sql
   ```

---

## Future Enhancements

1. **Soft Deletes** - Add `deleted_at` column for logical deletion
2. **Versioning** - Implement entity versioning for historical tracking
3. **Full-Text Search** - Add FTS indexes on text fields
4. **Webhooks** - Track webhook events in audit logs
5. **Notifications** - Add notification queue for audit events
