# CRUD API Endpoints

This document describes all the CRUD endpoints that have been implemented for the Tesseract SaaS MVP backend.

## Base URL

All endpoints are relative to the API base URL:
- Local development: `http://localhost:8000`
- Docker: `http://backend:8000`

## Clients API

### List all clients
- **Method**: GET
- **Path**: `/clients`
- **Query Parameters**:
  - `skip` (int, default: 0) - Number of items to skip
  - `limit` (int, default: 100) - Maximum number of items to return
- **Response**: Array of ClientResponse objects

```bash
curl http://localhost:8000/clients?skip=0&limit=10
```

### Create a new client
- **Method**: POST
- **Path**: `/clients`
- **Request Body**:
  ```json
  {
    "name": "Acme Corp",
    "email": "contact@acme.com",
    "phone": "+1-555-0100",
    "address": "123 Business St",
    "data": {}
  }
  ```
- **Response**: ClientResponse object

### Get client by ID
- **Method**: GET
- **Path**: `/clients/{client_id}`
- **Response**: ClientResponse object

### Update a client
- **Method**: PUT
- **Path**: `/clients/{client_id}`
- **Request Body**: Partial ClientUpdate object (all fields optional)
- **Response**: ClientResponse object

### Delete a client
- **Method**: DELETE
- **Path**: `/clients/{client_id}`
- **Response**: 204 No Content

---

## Invoices API

### List all invoices
- **Method**: GET
- **Path**: `/invoices`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of InvoiceResponse objects

### Create a new invoice
- **Method**: POST
- **Path**: `/invoices`
- **Request Body**:
  ```json
  {
    "client_id": "uuid",
    "invoice_number": "INV-001",
    "amount": 10000,
    "currency": "USD",
    "status": "draft",
    "issue_date": "2024-01-01T00:00:00Z",
    "due_date": "2024-02-01T00:00:00Z",
    "extracted_entities": {},
    "data": {}
  }
  ```
- **Response**: InvoiceResponse object

### Get invoice by ID
- **Method**: GET
- **Path**: `/invoices/{invoice_id}`
- **Response**: InvoiceResponse object

### Update an invoice
- **Method**: PUT
- **Path**: `/invoices/{invoice_id}`
- **Request Body**: Partial InvoiceUpdate object
- **Response**: InvoiceResponse object

### Delete an invoice
- **Method**: DELETE
- **Path**: `/invoices/{invoice_id}`
- **Response**: 204 No Content

### Get invoices by client
- **Method**: GET
- **Path**: `/invoices/search/client/{client_id}`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of InvoiceResponse objects

### Get invoices by status
- **Method**: GET
- **Path**: `/invoices/search/status/{status}`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of InvoiceResponse objects

---

## Contracts API

### List all contracts
- **Method**: GET
- **Path**: `/contracts`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of ContractResponse objects

### Create a new contract
- **Method**: POST
- **Path**: `/contracts`
- **Request Body**:
  ```json
  {
    "client_id": "uuid",
    "contract_number": "CNT-001",
    "title": "Service Agreement",
    "status": "draft",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2025-01-01T00:00:00Z",
    "extracted_entities": {},
    "rule_references": {},
    "data": {}
  }
  ```
- **Response**: ContractResponse object

### Get contract by ID
- **Method**: GET
- **Path**: `/contracts/{contract_id}`
- **Response**: ContractResponse object

### Update a contract
- **Method**: PUT
- **Path**: `/contracts/{contract_id}`
- **Request Body**: Partial ContractUpdate object
- **Response**: ContractResponse object

### Delete a contract
- **Method**: DELETE
- **Path**: `/contracts/{contract_id}`
- **Response**: 204 No Content

### Get contracts by client
- **Method**: GET
- **Path**: `/contracts/search/client/{client_id}`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of ContractResponse objects

---

## Audit Results API

### List all audit results
- **Method**: GET
- **Path**: `/audit-results`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of AuditResultResponse objects

### Create a new audit result
- **Method**: POST
- **Path**: `/audit-results`
- **Request Body**:
  ```json
  {
    "invoice_id": "uuid",
    "contract_id": "uuid",
    "rule_id": "rule-001",
    "status": "pending",
    "extracted_entities": {},
    "variance_metrics": {},
    "rule_references": {},
    "findings": {}
  }
  ```
- **Response**: AuditResultResponse object

### Get audit result by ID
- **Method**: GET
- **Path**: `/audit-results/{audit_result_id}`
- **Response**: AuditResultResponse object

### Update an audit result
- **Method**: PUT
- **Path**: `/audit-results/{audit_result_id}`
- **Request Body**: Partial AuditResultUpdate object
- **Response**: AuditResultResponse object

### Delete an audit result
- **Method**: DELETE
- **Path**: `/audit-results/{audit_result_id}`
- **Response**: 204 No Content

### Get audit results by invoice
- **Method**: GET
- **Path**: `/audit-results/search/invoice/{invoice_id}`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of AuditResultResponse objects

### Get audit results by contract
- **Method**: GET
- **Path**: `/audit-results/search/contract/{contract_id}`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of AuditResultResponse objects

---

## Audit Logs API

### List all audit logs
- **Method**: GET
- **Path**: `/audit-logs`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of AuditLogResponse objects

### Create a new audit log
- **Method**: POST
- **Path**: `/audit-logs`
- **Request Body**:
  ```json
  {
    "client_id": "uuid",
    "entity_type": "invoice",
    "entity_id": "uuid",
    "action": "created",
    "status": "success",
    "changes": {},
    "error_message": null,
    "data": {}
  }
  ```
- **Response**: AuditLogResponse object

### Get audit log by ID
- **Method**: GET
- **Path**: `/audit-logs/{audit_log_id}`
- **Response**: AuditLogResponse object

### Get audit logs by client
- **Method**: GET
- **Path**: `/audit-logs/search/client/{client_id}`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of AuditLogResponse objects

### Get audit logs by entity
- **Method**: GET
- **Path**: `/audit-logs/search/entity/{entity_id}`
- **Query Parameters**: `skip`, `limit`
- **Response**: Array of AuditLogResponse objects

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message here"
}
```

Common HTTP Status Codes:
- `200 OK` - Successful GET request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Frontend Integration

The frontend includes TypeScript hooks for consuming these APIs:

### useClients
```typescript
import { useClients } from "@/lib/hooks";

function MyComponent() {
  const { clients, loading, error } = useClients({ skip: 0, limit: 10 });
  // ...
}
```

### useInvoices
```typescript
import { useInvoices } from "@/lib/hooks";

function MyComponent() {
  const { invoices, loading, error } = useInvoices({ clientId: "uuid" });
  // ...
}
```

### useContracts
```typescript
import { useContracts } from "@/lib/hooks";

function MyComponent() {
  const { contracts, loading, error } = useContracts({ clientId: "uuid" });
  // ...
}
```

### useAuditResults
```typescript
import { useAuditResults } from "@/lib/hooks";

function MyComponent() {
  const { auditResults, loading, error } = useAuditResults({ invoiceId: "uuid" });
  // ...
}
```

### useAuditLogs
```typescript
import { useAuditLogs } from "@/lib/hooks";

function MyComponent() {
  const { auditLogs, loading, error } = useAuditLogs({ clientId: "uuid" });
  // ...
}
```

---

## Testing with Swagger UI

You can test all these endpoints interactively using Swagger UI:

1. Start the backend: `make up`
2. Open http://localhost:8000/docs in your browser
3. Click on any endpoint to expand it
4. Click "Try it out"
5. Enter parameters and request body
6. Click "Execute"

---

## Pagination

All list endpoints support pagination with `skip` and `limit` query parameters:

```
GET /clients?skip=0&limit=10
```

This will return 10 clients, skipping the first 0 (starting from the beginning).

---

## Status Codes

### Invoice Status Values
- `draft` - Invoice not yet sent
- `pending` - Invoice sent, awaiting payment
- `paid` - Invoice has been paid
- `overdue` - Payment is past due
- `cancelled` - Invoice was cancelled

### Contract Status Values
- `draft` - Contract in draft form
- `pending` - Contract awaiting signature
- `active` - Contract is currently active
- `completed` - Contract has completed
- `terminated` - Contract was terminated

### Audit Result Status Values
- `pending` - Audit result awaiting review
- `completed` - Audit has been completed
- `failed` - Audit failed with issues
- `approved` - Audit result approved

---

## API Documentation

For complete interactive API documentation with request/response examples, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
