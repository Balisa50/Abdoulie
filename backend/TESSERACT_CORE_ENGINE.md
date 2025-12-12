# Tesseract Core Engine - Invoice Extraction & Audit

## Overview

The Tesseract Core Engine is a production-ready backend system that automates freight invoice auditing. It extracts data from PDF invoices and validates them against contract rules to detect billing anomalies.

## Core Components

### 1. Document Processor (`app/document_processor.py`)

**Purpose:** Extracts structured data from freight invoice PDFs.

**Key Features:**
- Hybrid extraction approach: direct text extraction with OCR fallback
- Intelligent text quality assessment
- Image preprocessing for better OCR accuracy
- Regex-based field extraction for common invoice formats
- Handles multiple date and currency formats

**Extracted Fields:**
- `carrier_name` - Freight carrier name
- `invoice_number` - Unique invoice identifier
- `invoice_date` - Invoice date (normalized to YYYY-MM-DD)
- `total_charge` - Total invoice amount (float)
- `shipment_reference` - PRO number or shipment tracking ID

**Technology Stack:**
- PyMuPDF (fitz) for direct PDF text extraction
- Tesseract OCR for scanned/image-based PDFs
- OpenCV for image preprocessing
- pdf2image for PDF-to-image conversion

### 2. Audit Engine (`app/audit_engine.py`)

**Purpose:** Validates invoices against contract rules and detects billing anomalies.

**Core Anomaly Checks:**

1. **Rate Overage Detection**
   - Calculates actual rate per mile
   - Compares against contracted maximum rate
   - Flags overcharges with severity levels

2. **Carrier Validation**
   - Verifies carrier name matches contract
   - Uses fuzzy string matching for minor variations
   - Configurable similarity threshold

3. **Data Validation**
   - Checks for missing required fields
   - Validates positive charges
   - Detects suspicious/unreasonable amounts

**Anomaly Structure:**
```json
{
  "type": "RATE_OVERAGE",
  "severity": "HIGH",
  "detail": "Calculated rate $4.12/mi exceeds contracted $3.50/mi by $282.50 (17.7% over)",
  "field": "total_charge",
  "expected": 1575.00,
  "actual": 1857.50
}
```

### 3. API Layer (`app/routers/invoice.py`)

**Endpoints:**

#### POST `/invoice/extract`
Upload a freight invoice PDF and extract structured data.

**Request:**
- Multipart form data with PDF file

**Response:**
```json
{
  "success": true,
  "data": {
    "carrier_name": "ROADWAY EXPRESS",
    "invoice_number": "INV-2024-12345",
    "invoice_date": "2024-03-15",
    "total_charge": 1575.00,
    "shipment_reference": "PRO-98765"
  },
  "message": "Invoice data extracted successfully"
}
```

#### POST `/invoice/audit`
Audit an invoice against contract rules.

**Request:**
```json
{
  "invoice_data": {
    "carrier_name": "ROADWAY EXPRESS",
    "total_charge": 1857.50
  },
  "shipment_data": {
    "mileage": 450
  },
  "contract_rules": {
    "carrier_name": "ROADWAY EXPRESS",
    "max_rate_per_mile": 3.50,
    "min_string_similarity": 0.8
  }
}
```

**Response:**
```json
{
  "success": true,
  "anomalies": [
    {
      "type": "RATE_OVERAGE",
      "severity": "HIGH",
      "detail": "Calculated rate $4.13/mi exceeds contracted $3.50/mi...",
      "field": "total_charge",
      "expected": 1575.00,
      "actual": 1857.50
    }
  ],
  "anomaly_count": 1,
  "message": "Audit complete: 1 anomalies detected"
}
```

## Installation & Setup

### Prerequisites
- Python 3.11+
- Tesseract OCR installed on system
- Poppler utils (for PDF processing)

### Install System Dependencies (Ubuntu/Debian)
```bash
apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0
```

### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Docker Setup (Recommended)
```bash
# Build and start services
docker-compose up --build

# Backend will be available at http://localhost:8000
```

## Usage Examples

### Generate Sample Invoices
```bash
cd backend
python app/create_sample_invoice.py
```

This creates three test PDFs:
- `sample_invoice.pdf` - Valid invoice
- `sample_invoice_overage.pdf` - Invoice with rate overage
- `sample_invoice_wrong_carrier.pdf` - Invoice with carrier mismatch

### Extract Invoice Data
```bash
curl -X POST http://localhost:8000/invoice/extract \
  -F "file=@sample_invoice.pdf"
```

### Audit an Invoice
```bash
curl -X POST http://localhost:8000/invoice/audit \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_data": {
      "carrier_name": "ROADWAY EXPRESS",
      "total_charge": 1857.50
    },
    "shipment_data": {
      "mileage": 450
    },
    "contract_rules": {
      "carrier_name": "ROADWAY EXPRESS",
      "max_rate_per_mile": 3.50
    }
  }'
```

### Complete Workflow Example
```python
import requests

# Step 1: Extract data from PDF
with open("sample_invoice.pdf", "rb") as f:
    extract_response = requests.post(
        "http://localhost:8000/invoice/extract",
        files={"file": f}
    )

invoice_data = extract_response.json()["data"]

# Step 2: Audit the invoice
audit_response = requests.post(
    "http://localhost:8000/invoice/audit",
    json={
        "invoice_data": invoice_data,
        "shipment_data": {"mileage": 450},
        "contract_rules": {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50
        }
    }
)

anomalies = audit_response.json()["anomalies"]
print(f"Found {len(anomalies)} anomalies")
```

## Testing

### Run All Tests
```bash
cd backend
pytest tests/ -v
```

### Run Specific Test Suites
```bash
# Test audit engine
pytest tests/test_audit_engine.py -v

# Test document processor
pytest tests/test_document_processor.py -v

# Test API endpoints
pytest tests/test_invoice_api.py -v
```

### Test Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

## Key Design Decisions

### 1. Hybrid PDF Processing
- **Why:** PDFs can contain embedded text OR scanned images
- **Solution:** Try direct extraction first, fall back to OCR if quality is poor
- **Benefit:** Handles both native and scanned invoices

### 2. Regex-Based Field Extraction
- **Why:** Invoice formats vary but follow common patterns
- **Solution:** Multiple regex patterns per field with priority ordering
- **Trade-off:** Works for semi-standard formats; may need ML for highly variable documents

### 3. String Similarity for Carrier Matching
- **Why:** Carrier names may have minor variations (e.g., "INC" vs "INCORPORATED")
- **Solution:** Use SequenceMatcher with configurable threshold (default 80%)
- **Benefit:** Reduces false positives from trivial differences

### 4. Severity-Based Anomaly Classification
- **Why:** Not all anomalies require immediate action
- **Solution:** HIGH/MEDIUM/LOW severity based on business impact
- **Benefit:** Enables prioritized review workflow

## Performance Characteristics

- **PDF Extraction:** ~1-3 seconds per page (direct text)
- **OCR Processing:** ~5-10 seconds per page (300 DPI)
- **Audit Logic:** <100ms per invoice
- **Memory Usage:** ~200-500MB per process

## Future Enhancements

### Short Term
- [ ] Add machine learning model for field extraction
- [ ] Support for multi-page invoices
- [ ] Batch processing capability
- [ ] Async processing with Celery

### Long Term
- [ ] Support for additional document formats (XML, EDI)
- [ ] Advanced anomaly detection (ML-based)
- [ ] Historical trend analysis
- [ ] Integration with ERP systems

## Production Considerations

### Scalability
- Use Celery for async processing of large batches
- Implement Redis-based rate limiting
- Consider horizontal scaling for API layer

### Monitoring
- Log all extractions and audits with timestamps
- Track extraction accuracy metrics
- Monitor anomaly detection rates
- Set up alerts for system errors

### Security
- Implement authentication/authorization for API endpoints
- Sanitize uploaded PDFs (virus scanning)
- Encrypt stored invoice data
- Audit logging for compliance

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Support & Contribution

For issues, questions, or contributions, please refer to the main project README.

## License

See LICENSE file in project root.
