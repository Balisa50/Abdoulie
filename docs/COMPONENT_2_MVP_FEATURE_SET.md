# Tesseract MVP Feature Set: Core Workflow & Business Essentials

**Component 2: MVP Feature Definition**  
**Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Ready for Development  

---

## Executive Summary

The Tesseract MVP consists of **10 must-have features** divided into two categories:

- **Core Workflow (6 features):** The autonomous freight audit and recovery engine
- **Business Essentials (4 features):** Platform operations and customer management

This document defines each feature with specific, measurable acceptance criteria to guide development and QA.

---

## CORE WORKFLOW FEATURES (Months 1-3)

These features comprise the core value proposition: automatically detect and help recover overcharges in freight invoices.

### 1. Automated Carrier Invoice Ingestion

**Category:** Core Workflow | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 1-2 | **Owner:** Backend Engineer

#### What It Does

Clients submit freight invoices to Tesseract through multiple channels. The system receives, validates, and queues them for processing without manual intervention.

#### Business Value

- **Customer Experience:** Seamless invoice submission (no copying/pasting data)
- **Operational Scale:** Process 100+ invoices/hour per client
- **Time to Insight:** Errors detected within hours, not days

#### Technical Specification

**Input Methods:**
1. **Email Forwarding** (Primary)
   - Dedicated email address: `{client_id}@invoices.tesseract.ai`
   - Attachment extraction: PDFs, PNGs, JPGs, Excel files, EDI 210/211
   - Auto-reply with confirmation and processing status
   
2. **Web Dashboard Upload** (Secondary)
   - Drag-and-drop interface
   - Batch upload (up to 50 files at once)
   - Progress indicators with ETA

3. **API Integration** (Future - Month 4)
   - `POST /api/v1/invoices/upload` endpoint
   - Webhook for TMS integration

**Processing Pipeline:**
```
1. Receive invoice (email attachment or web upload)
2. Validate file format & size (<50 MB)
3. Store raw file in S3: s3://tesseract-uploads/{client_id}/{date}/{filename}
4. Generate metadata: file hash, upload timestamp, source
5. Queue processing job in Redis: tesseract:processing:{client_id}:{timestamp}
6. Send confirmation email with tracking link
7. Monitor job status (pending → processing → success/failed)
```

**Data Stored:**
- `invoices.raw_document_url` → S3 file path
- `invoices.upload_source` → "email" | "web" | "api"
- `invoices.upload_timestamp` → ISO8601 datetime
- `invoices.processing_status` → "pending" | "processing" | "success" | "failed"

#### Acceptance Criteria

- [ ] Process 100+ invoices/hour per concurrent client
- [ ] Handle PDF, PNG, JPG, XLSX, EDI 210/211 file formats
- [ ] Reject files >50 MB with user-friendly error message
- [ ] Auto-retry failed uploads with exponential backoff (3 attempts)
- [ ] Generate unique tracking URL for each invoice
- [ ] Send email confirmation within 30 seconds of upload
- [ ] Handle duplicate submissions (same file hash) without reprocessing
- [ ] Support parallel uploads for the same client
- [ ] Maintain upload audit trail for 7 years

#### Success Metrics

- 99.5% upload success rate
- <5 second average upload time
- <2% auto-retry rate (indicating robust first-time processing)

---

### 2. AI-Powered Data Extraction

**Category:** Core Workflow | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 2-3 | **Owner:** ML Engineer + Backend Engineer

#### What It Does

Automatically extract structured invoice data (invoice number, date, charges, shipper/consignee, etc.) from unstructured PDFs and scanned documents using OCR and LLM technology.

#### Business Value

- **Accuracy:** 95% extraction on clear documents, 85% on scanned
- **Speed:** 15-30 seconds per invoice (vs. 2-3 minutes manual)
- **Consistency:** 100% of invoices processed the same way

#### Technical Specification

**Technology Stack:**
- **OCR Engine:** AWS Textract (primary), Azure Document Intelligence (fallback)
- **Extraction Engine:** OpenAI GPT-4o with structured output schema
- **Fallback:** Anthropic Claude 3.5 Sonnet (if GPT-4o rate limited)

**Extraction Schema:**
```json
{
  "invoice_metadata": {
    "invoice_number": "string (required)",
    "invoice_date": "ISO8601 (required)",
    "invoice_amount_total": "decimal (required)",
    "currency": "USD | CAD"
  },
  "carrier_info": {
    "carrier_name": "string (required)",
    "carrier_scac": "string (LT, XPO, etc.)",
    "carrier_phone": "string"
  },
  "shipment_details": {
    "shipment_number": "string",
    "po_number": "string",
    "ship_date": "ISO8601",
    "delivery_date": "ISO8601",
    "weight": "decimal",
    "weight_unit": "LB | KG",
    "pieces": "integer",
    "service_level": "Ground | Express | Priority | LTL | Truckload",
    "pickup_location": {
      "address": "string",
      "city": "string",
      "state": "string",
      "zip": "string"
    },
    "delivery_location": {
      "address": "string",
      "city": "string",
      "state": "string",
      "zip": "string"
    }
  },
  "charges": [
    {
      "description": "string (e.g., 'Freight Base', 'Fuel Surcharge', 'Liftgate')",
      "amount": "decimal",
      "category": "freight | fuel | accessorial | tax",
      "line_item_number": "integer"
    }
  ],
  "extraction_confidence": {
    "overall_confidence": "0-100 (percent)",
    "field_confidence": {
      "invoice_number": "0-100",
      "invoice_date": "0-100",
      "invoice_amount_total": "0-100"
    },
    "low_confidence_fields": ["field_name", "..."]
  },
  "extraction_metadata": {
    "ocr_engine_used": "textract | azure",
    "llm_model": "gpt-4o",
    "processing_time_ms": "integer",
    "document_quality": "excellent | good | fair | poor"
  }
}
```

**Processing Workflow:**
```
1. Receive invoice document (from Ingestion step)
2. Call AWS Textract to extract raw text + layout
3. Assess document quality (scanned, printed, handwritten)
4. If document quality < 50%, flag for manual review
5. Prepare LLM prompt with OCR results + schema
6. Call GPT-4o with function calling for structured output
7. Validate extracted amounts sum to total (allow $0.01 rounding)
8. Validate required fields (invoice #, date, total, carrier)
9. Store extraction results in database
10. If confidence < 70%, flag for human review
11. If confidence >= 70%, proceed to Contract Matching
```

**LLM Prompt Template:**
```
You are an expert freight invoice processor. Extract the following structured data 
from this carrier invoice. Be precise with numbers and dates.

[OCR RESULTS]
{ocr_text}

[REFERENCE IMAGE REGIONS]
{ocr_bounding_boxes}

Return a JSON object with these fields:
{schema}

Rules:
- All currency amounts must be numeric
- Dates must be ISO8601 format
- Confidence scores should reflect uncertainty (0=guessing, 100=certain)
- If a field is not found, use null but note it in low_confidence_fields
- Sum of charges should equal invoice total (allow $0.01 rounding)
```

**Data Stored:**
- `invoices.extracted_entities` → Full JSON extraction result
- `invoices.extraction_confidence` → Overall confidence score (0-100)
- `invoices.extraction_status` → "success" | "partial" | "needs_review" | "failed"
- `invoices.low_confidence_fields` → Array of field names requiring review

#### Acceptance Criteria

- [ ] 95% field extraction accuracy on clear printed PDFs (validated on 100+ test invoices)
- [ ] 85% field extraction accuracy on scanned/low-quality documents
- [ ] Flag all extractions <70% confidence for human review queue
- [ ] Process each invoice in 15-30 seconds end-to-end
- [ ] Validate extracted amounts sum to invoice total (±$0.01)
- [ ] Return structured JSON matching schema (no missing required fields)
- [ ] Support 5 major carrier formats (UPS, FedEx, XPO, YRC, Old Dominion)
- [ ] Fallback to Claude if GPT-4o fails or rate limited
- [ ] Extract minimum 15 key fields per invoice (invoice #, date, total, carrier, origin, destination, weight, service level, plus charges)

#### Success Metrics

- 97%+ of invoices extracted with confidence ≥ 70%
- <5% manual review queue rate
- 99.5% successful extraction (no crashed jobs)
- Average extraction cost per invoice: <$0.10 (API calls)

#### Integration Points

- **Upstream:** Automated Carrier Invoice Ingestion (receives documents)
- **Downstream:** Contract Rate Matching (passes structured data)
- **External:** AWS Textract, OpenAI GPT-4o, Anthropic Claude

---

### 3. Contract Rate Matching

**Category:** Core Workflow | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 3-4 | **Owner:** Backend Engineer

#### What It Does

Compares each extracted invoice against the client's negotiated carrier contracts to identify rate variances and overcharges.

#### Business Value

- **Baseline Comparison:** Establish what the client should pay vs. what they actually paid
- **Negotiated Rate Visibility:** Prove contract terms are being honored
- **Foundation for Error Detection:** Enables automated error flagging in next step

#### Technical Specification

**Contract Data Structure:**
```
contracts table:
- contract_id (PK)
- client_id (FK)
- carrier_scac (e.g., "XPO", "FDX")
- carrier_name
- contract_name (e.g., "XPO National FY2024")
- rate_table_type: "per-100lb" | "flat_rate" | "tariff" | "zone"
- effective_date (start)
- expiration_date (end)
- upload_url (S3 path to contract PDF)
- created_by (user_id)
- created_at (timestamp)

rate_rules table:
- rule_id (PK)
- contract_id (FK)
- origin_zip_range_start
- origin_zip_range_end
- destination_zip_range_start
- destination_zip_range_end
- weight_min (lbs)
- weight_max (lbs)
- service_level (Ground, Express, etc.)
- rate_per_100lb | flat_rate (numeric)
- accessorial_rules (JSON)
- created_at (timestamp)
```

**Matching Algorithm:**

For each invoice charge, execute in order:
```
1. Parse extracted charges into line items
2. For each charge:
   a. Identify charge category: freight_base | fuel_surcharge | accessorial
   b. If FREIGHT_BASE charge:
      - Extract: origin zip, destination zip, weight, service level
      - Look up applicable rate_rules WHERE:
        * contract.effective_date <= invoice_date <= contract.expiration_date
        * rule.origin_zip BETWEEN rule.origin_zip_range
        * rule.destination_zip BETWEEN rule.destination_zip_range
        * rule.weight BETWEEN rule.weight_min AND rule.weight_max
        * rule.service_level = invoice.service_level
      - If FOUND: Calculate expected charge = weight / 100 * contract_rate
      - If NOT FOUND: Mark as "no_contract_rate_found"
      - Calculate variance = actual_charge - expected_charge
      - Store result in audit_results
   c. If FUEL_SURCHARGE:
      - Verify FSC % is within contract range (typically ±2%)
      - Validate against DOE index date
   d. If ACCESSORIAL:
      - Check if charge_description is in client's approved_accessories list
      - Verify amount matches contract accessorial_rules

3. Generate variance summary:
   - Total base rate variance
   - Fuel surcharge variance
   - Unauthorized accessorial charges
```

**Data Stored:**
- `audit_results.contract_matched` → bool
- `audit_results.matched_contract_id` → contract_id | null
- `audit_results.rate_comparison` → JSON with expected vs actual per charge
- `audit_results.variances` → Array of identified differences
- `audit_results.total_variance_amount` → decimal (sum of all variances)

#### Acceptance Criteria

- [ ] Match 80% of valid invoices to contract rates automatically
- [ ] Support 3 rate table formats: per-hundredweight, flat rate, zone-based, tariff
- [ ] Calculate variance in dollars and percentage for each charge
- [ ] Flag invoices with "no matching contract rate" for manual review
- [ ] Handle weight breaks (e.g., 0-499 lbs, 500-999 lbs, 1000+ lbs)
- [ ] Support origin/destination matching by ZIP code range or city
- [ ] Process each invoice comparison in <5 seconds
- [ ] Display rate comparison table (expected vs. actual) for user review
- [ ] Store audit trail of which rate rules were applied

#### Success Metrics

- 80% automatic rate matching success rate
- <2% false negatives (missed rate matches)
- <1 second average matching time per invoice
- 100% variance calculation accuracy (validated manually on 50 test cases)

#### Admin Features

- Contract upload and management UI
- CSV import for rate tables
- Rate rule activation/deactivation by date range
- Version history and change audit log

---

### 4. Error Detection & Flagging

**Category:** Core Workflow | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 4-5 | **Owner:** Backend Engineer + ML Engineer

#### What It Does

Automatically identifies overcharges, duplicate invoices, unauthorized charges, and other billing errors based on contract terms and historical patterns. Flags high-confidence errors for dispute submission.

#### Business Value

- **Error Discovery:** 90%+ recall on common error types
- **Confidence Scoring:** Distinguish high-confidence (auto-dispute) from medium/low (manual review)
- **Audit Trail:** Document exactly how each error was detected

#### Technical Specification

**Error Type Definitions & Detection Rules:**

**1. Overcharge on Freight Base Rate**
- **Trigger:** Matched contract rate exists AND actual charge > contract rate
- **Threshold:** >$5 absolute variance OR >5% percentage variance
- **Confidence:** 95% if clear contract match, 70% if partial
- **Example:** Contract: $2.50/100lb, Invoice: $2.75/100lb → Flag as 10% overcharge

**2. Duplicate Invoice**
- **Trigger:** Exact match on (invoice_number, carrier_scac, invoice_date) within same client
- **Secondary Check:** Shipment number + weight + charge amount match
- **Confidence:** 99% if within 24 hours, 95% if within 7 days
- **Action:** Auto-reject duplicate, link to original invoice
- **Example:** Same invoice #INV-12345 submitted twice in same week

**3. Unauthorized Accessorial Charge**
- **Trigger:** Charge category = "accessorial" AND description NOT in approved_accessories
- **Approved List:** Liftgate, Residential Delivery, Inside Pickup, Redelivery, Inside Delivery, Tailgate Required
- **Unapproved Examples:** "Fuel Surcharge Exception", "Holiday Delivery", "Special Handling"
- **Confidence:** 95% (rule-based)
- **Action:** Flag for review; if approved by user, add to client's accessorial_rules

**4. Fuel Surcharge Error**
- **Trigger:** Charge category = "fuel_surcharge"
- **Validation 1:** FSC % vs. DOE index
  - Fetch DOE index for invoice_date
  - Compare invoice FSC % to contract FSC formula
  - Flag if >2% deviation
- **Validation 2:** FSC formula compliance
  - Common formula: (Price - $2.45) / $2.45
  - Flag if formula not followed
- **Confidence:** 85% (requires fuel index reference)
- **Example:** Contract: "FSC = (Current WTI - $2.45) / $2.45", Actual FSC: 18%, but DOE index says should be 12%

**5. Rate-Per-Hundredweight Calculation Error**
- **Trigger:** Charge description contains "per 100 lb" or similar
- **Validation:** (weight_lbs / 100) * rate_per_100lb = charge_amount (±$0.10)
- **Confidence:** 95% (math-based)
- **Example:** Weight: 450 lbs, Rate: $2.50/100lb, Charge: $11.25 ✓ vs. $12.00 ✗

**6. Missing Negotiated Discount**
- **Trigger:** Contract includes volume or shipper discount, not applied to invoice
- **Validation:** Check if shipper/lane/service level qualifies for discount
- **Confidence:** 70% (business logic dependent)
- **Example:** Contract: "Volume Discount: 10% on 50+ shipments/month", Only 3 shipments → no discount expected

**7. Weight Discrepancy**
- **Trigger:** Billable weight on invoice > actual weight by >10%
- **Confidence:** 70% (requires dimensional data)
- **Example:** Actual weight: 100 lbs, Billed weight: 120 lbs (billable minimum)

**Detection Pipeline:**

```python
def detect_errors(invoice: Invoice, contract: Contract, client_prefs: ClientPreferences):
    errors = []
    confidence_scores = {}
    
    # Check 1: Overcharge Detection
    if contract.matched_rate and invoice.freight_charge > contract.expected_charge:
        variance_pct = (invoice.freight_charge - contract.expected_charge) / contract.expected_charge
        if variance_pct > 0.05 or (invoice.freight_charge - contract.expected_charge) > 5:
            errors.append({
                'type': 'OVERCHARGE',
                'description': f'Rate {variance_pct*100:.1f}% above contract',
                'variance_amount': invoice.freight_charge - contract.expected_charge,
                'confidence': 95
            })
    
    # Check 2: Duplicate Detection
    duplicate = db.query(Invoice).filter(
        Invoice.client_id == invoice.client_id,
        Invoice.invoice_number == invoice.invoice_number,
        Invoice.carrier_scac == invoice.carrier_scac,
        Invoice.invoice_date == invoice.invoice_date,
        Invoice.id != invoice.id
    ).first()
    if duplicate:
        errors.append({
            'type': 'DUPLICATE',
            'description': f'Duplicate of invoice {duplicate.id}',
            'variance_amount': invoice.total_amount,
            'confidence': 99 if (now() - duplicate.invoice_date).days < 1 else 95
        })
    
    # Check 3: Unauthorized Accessorial
    for charge in invoice.charges:
        if charge.category == 'accessorial':
            if charge.description not in client_prefs.approved_accessories:
                errors.append({
                    'type': 'UNAUTHORIZED_ACCESSORIAL',
                    'description': f'Unauthorized charge: {charge.description}',
                    'variance_amount': charge.amount,
                    'confidence': 95
                })
    
    # Check 4: Fuel Surcharge Validation
    fsc_charge = next((c for c in invoice.charges if c.category == 'fuel'), None)
    if fsc_charge and contract.fuel_formula:
        expected_fsc = calculate_fsc(contract.fuel_formula, invoice.invoice_date)
        actual_fsc = fsc_charge.amount / invoice.freight_charge
        if abs(expected_fsc - actual_fsc) > 0.02:
            errors.append({
                'type': 'FUEL_SURCHARGE_ERROR',
                'description': f'FSC {actual_fsc*100:.1f}% vs. expected {expected_fsc*100:.1f}%',
                'variance_amount': fsc_charge.amount - (invoice.freight_charge * expected_fsc),
                'confidence': 85
            })
    
    return errors
```

**Data Stored:**
- `audit_results.errors` → JSON array of detected errors
- `audit_results.error_type` → Enum of detected error types
- `audit_results.total_error_amount` → Sum of all error variances
- `audit_results.overall_confidence` → Weighted average of error confidences
- `audit_results.requires_manual_review` → bool (true if confidence <70%)

#### Acceptance Criteria

- [ ] Detect 90% of test overcharges (validated on 50+ manually-flagged test invoices)
- [ ] Zero false positives on duplicate detection (100% precision)
- [ ] Identify 95%+ of unauthorized accessories vs. approved list
- [ ] Validate fuel surcharge formulas with >85% accuracy
- [ ] Process error detection for each invoice in <5 seconds
- [ ] Assign confidence score (0-100%) to each error based on rule certainty
- [ ] Return structured error report with variance amounts in dollars
- [ ] Support client-specific error rules via admin UI
- [ ] Log all error detection logic for audit trail

#### Success Metrics

- 90% error recall rate
- <2% false positive rate (flagged non-errors)
- <1 second average detection time per invoice
- 95%+ confidence on high-value errors (>$100)

---

### 5. Recovery Dashboard

**Category:** Core Workflow | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 5-6 | **Owner:** Frontend Engineer

#### What It Does

Provides a centralized visual interface for users to view all invoices, flagged errors, recovery progress, and analytics. The dashboard is the primary interface for decision-making about disputes.

#### Business Value

- **Visibility:** Single pane of glass for all freight recovery activity
- **Prioritization:** Sort by recovery potential to focus on high-value disputes
- **Analytics:** Understand error patterns and savings by carrier/lane
- **Accountability:** Track dispute status from detection to recovery

#### Technical Specification

**Dashboard Views:**

**1. Overview Page** (Default Landing)
```
┌─────────────────────────────────────────────────────────┐
│  Tesseract Dashboard                          [Settings] │
├─────────────────────────────────────────────────────────┤
│  📊 This Month's Recovery                                │
│  ┌─────────────────────────────────────────────────────┐│
│  │  Total Errors Found:    $47,250                     ││
│  │  Disputes Submitted:    $35,800                     ││
│  │  Recoveries Received:   $28,640 (80% success rate) ││
│  │  Pending Disputes:      $11,550 (28 invoices)      ││
│  └─────────────────────────────────────────────────────┘│
│                                                          │
│  📈 Top 5 Carriers with Errors                          │
│  ┌────────────────┬──────────┬──────────────────┐       │
│  │ Carrier        │ Errors   │ Total $ Variance │       │
│  ├────────────────┼──────────┼──────────────────┤       │
│  │ XPO            │ 145      │ $18,500          │       │
│  │ FedEx          │  87      │ $12,300          │       │
│  │ UPS            │  42      │ $ 8,200          │       │
│  │ YRC            │  31      │ $ 4,800          │       │
│  │ Old Dominion   │  28      │ $ 3,450          │       │
│  └────────────────┴──────────┴──────────────────┘       │
│                                                          │
│  ⚠️ Errors Breakdown                                    │
│  [Overcharge: 215] [Dup: 8] [Accessorial: 42] [FSC: 15]│
└─────────────────────────────────────────────────────────┘
```

**Metrics Displayed:**
- Total recovery potential this month/quarter/year
- Success rate (disputes won / disputes submitted)
- Average recovery per invoice
- Error breakdown by type (pie chart)
- Top error sources by carrier (bar chart)
- Monthly trend (line chart showing cumulative recovery)

**2. Invoice Queue Page** (Filterable List)
```
Invoices (342 total) | [All] [New Errors] [Reviewing] [Disputed] [Recovered] [Rejected]

Filters: Carrier [▼] Date Range [▼] Min Error Amount [$]  [Search by Invoice#]

┌─────────┬──────────────┬──────────┬──────────┬──────────────┬─────────────┐
│ Invoice │ Carrier      │ Date     │ Invoice$ │ Error Amount │ Status      │
├─────────┼──────────────┼──────────┼──────────┼──────────────┼─────────────┤
│ INV-1245│ XPO Logistics│ Jan 15   │ $2,850   │ $285 (10%)   │ ⚠ Reviewing │
│ INV-1244│ FedEx Freight│ Jan 14   │ $1,250   │ $50 (4%)     │ ✓ Disputed  │
│ INV-1243│ UPS Freight  │ Jan 13   │ $890     │ $120 (13.5%) │ ✓ Recovered │
│ INV-1242│ YRC Worldwide│ Jan 12   │ $3,420   │ $515 (15%)   │ ✗ Rejected  │
│ INV-1241│ XPO Logistics│ Jan 11   │ $2,100   │ $0 (Match)   │ ○ No Error  │
└─────────┴──────────────┴──────────┴──────────┴──────────────┴─────────────┘
```

**Sort/Filter Options:**
- Status (New Errors, Reviewing, Disputed, Recovered, Rejected, No Error)
- Date range (This Month, Last 3 Months, Custom)
- Carrier (multi-select)
- Error type (Overcharge, Duplicate, Accessorial, Fuel, etc.)
- Minimum error amount ($0, $50, $100, $500, Custom)
- Sort by: Date, Error Amount, Carrier, Success Likelihood

**3. Invoice Detail Page** (Drill-Down)
```
┌──────────────────────────────────────────────────────────┐
│ < Back to Queue                          Invoice INV-1245 │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  INVOICE INFORMATION                  EXTRACTED DATA     │
│  ┌────────────────────────────┐   ┌──────────────────┐   │
│  │ Carrier: XPO Logistics     │   │ ✓ Invoice #      │   │
│  │ Date: Jan 15, 2024         │   │ ✓ Date           │   │
│  │ Shipment #: SHP-98765      │   │ ✓ Carrier        │   │
│  │ Origin: Los Angeles, CA    │   │ ⚠ Weight: Low    │   │
│  │ Dest: Chicago, IL          │   │ ✓ Charges        │   │
│  │ Weight: 850 lbs            │   └──────────────────┘   │
│  │ Service: Ground            │                          │
│  │ Total: $2,850              │   ERROR DETECTED         │
│  └────────────────────────────┘   ┌──────────────────┐   │
│                                    │ Overcharge       │   │
│  RATE COMPARISON                   │ Confidence: 95%  │   │
│  ┌────────────────────────────┐   │ Variance: $285   │   │
│  │ Contract Rate: $2.50/100lb │   └──────────────────┘   │
│  │ Expected Charge: $21.25    │                          │
│  │ Actual Charge: $25.00      │   CONTRACT REFERENCE    │
│  │ Variance: $3.75 (17.6%)    │   ┌──────────────────┐   │
│  └────────────────────────────┘   │ XPO National 2024│   │
│                                    │ Effective: 1/1-  │   │
│  CHARGE BREAKDOWN                  │ 12/31/2024       │   │
│  ┌──────────────┬────────────┐    │ Download PDF ↓   │   │
│  │ Freight Base │ $2,100     │    └──────────────────┘   │
│  │ Fuel Charge  │ $525       │                          │
│  │ Tax          │ $225       │    ACTIONS               │
│  │ TOTAL        │ $2,850     │    ┌──────────────────┐   │
│  └──────────────┴────────────┘    │ [Generate Dispute]   │
│                                    │ [More Info]          │
│                                    │ [Approve Error]      │
│                                    │ [Mark as OK]         │
│                                    │ [Flag for Review]    │
│                                    └──────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

**Technical Implementation:**
- **Frontend:** Next.js with React Query for data fetching and caching
- **Backend APIs:**
  - `GET /api/v1/dashboard/overview` → Summary metrics
  - `GET /api/v1/invoices?status=&carrier=&date_from=&date_to=&min_error=$` → Filtered invoice list
  - `GET /api/v1/invoices/{id}` → Full invoice detail with contract comparison
  - `GET /api/v1/analytics/recovery-summary?period=month` → Charts and analytics
  - `GET /api/v1/analytics/error-breakdown?period=month` → Error type distribution
- **Performance:**
  - Dashboard overview: <1 second load time (cached)
  - Invoice queue: <2 seconds with pagination (50 invoices/page)
  - Invoice detail: <1 second (pre-loaded data)
- **Export Capability:**
  - CSV export of invoice queue (all visible columns)
  - PDF export of individual invoice with supporting docs
  - Monthly summary report (PDF with charts)

#### Acceptance Criteria

- [ ] Dashboard loads in <2 seconds
- [ ] Invoice queue displays 50 invoices with sorting/filtering
- [ ] Invoice detail page shows extraction data, rate comparison, and error summary
- [ ] Filter/sort by carrier, date range, error type, minimum error amount
- [ ] Export invoice queue to CSV
- [ ] Export invoice detail + supporting docs to PDF
- [ ] Real-time status updates (no page refresh required)
- [ ] Mobile responsive (dashboard usable on tablet)
- [ ] All currency amounts properly formatted with $
- [ ] Show data quality indicators (extraction confidence, contract match status)

#### Success Metrics

- <1 second average page load (observed with 5000+ invoices in database)
- 99% uptime
- <50ms response time for all API endpoints (p95)

---

### 6. Dispute Submission (Semi-Automated)

**Category:** Core Workflow | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 6 | **Owner:** Backend Engineer + Frontend Engineer

#### What It Does

Generates professional dispute letters with supporting documentation and tracks carrier responses. MVP uses human-in-the-loop approach: system generates draft, user reviews and sends via email.

#### Business Value

- **Speed:** 90% reduction in time to submit dispute (5 min system-generated vs. 30 min manual)
- **Consistency:** Standardized dispute format for all carriers
- **Evidence:** Automatic attachment of invoice, contract excerpt, and variance calculation
- **Tracking:** Complete audit trail of dispute lifecycle

#### Technical Specification

**Dispute Letter Template** (Jinja2):

```jinja2
Dear {{ carrier_name }} Billing Department,

Re: Invoice Dispute - Invoice #{{ invoice.invoice_number }}
    Shipment: {{ invoice.shipment_number }}
    Invoice Date: {{ invoice.invoice_date }}
    Service Period: {{ invoice.service_date_from }} to {{ invoice.service_date_to }}

We are writing to dispute the above-referenced invoice due to billing errors 
identified during our freight audit. Our analysis indicates:

**ERROR DETAILS:**
{% for error in errors %}
- {{ error.error_type }}: {{ error.description }}
  Original Charge: ${{ error.original_amount }}
  Correct Charge: ${{ error.expected_amount }}
  Variance: ${{ error.variance_amount }}
{% endfor %}

**TOTAL VARIANCE: ${{ total_variance }}**

**CONTRACT REFERENCE:**
Contract Name: {{ contract.name }}
Effective Period: {{ contract.effective_date }} to {{ contract.expiration_date }}
Relevant Rate: {{ contract.applicable_rate }}

**SUPPORTING DOCUMENTATION:**
- Original Invoice (attached)
- Contract Rate Table Excerpt (attached)
- Rate Calculation Summary (attached)

We request a credit memo in the amount of ${{ total_variance }} to resolve this matter.

Please acknowledge receipt of this dispute within 5 business days and advise 
on your resolution timeline.

Thank you,
{{ user.full_name }}
{{ company.name }}
{{ contact.email }}
{{ contact.phone }}
```

**Dispute Workflow:**

1. **Generation Phase**
   - User clicks "Generate Dispute" on invoice detail page
   - System triggers `/api/v1/disputes/generate` endpoint
   - Backend generates dispute letter (Jinja2 template)
   - Collects supporting documents:
     * Original invoice PDF (from S3)
     * Contract excerpt (extract relevant rate table from contract)
     * Rate calculation sheet (generated CSV)
   - Returns draft to frontend for review
   - User can edit letter, change email recipient, or regenerate

2. **Submission Phase**
   - User reviews draft and clicks "Send Dispute"
   - System auto-populates email recipient (from extracted carrier contact info or user selection)
   - Optional: Attach additional documents user specifies
   - User clicks "Send"
   - Backend sends email via SendGrid
   - Records dispute submission in database:
     * `disputes.submitted_date` = now
     * `disputes.submitted_by` = current_user_id
     * `disputes.status` = "submitted"
     * `disputes.email_message_id` = SendGrid message ID (for tracking)

3. **Tracking Phase**
   - Dashboard shows dispute status (submitted, acknowledged, approved, rejected, in_negotiation)
   - User manually updates status when carrier responds (MVP)
   - Optional: User can add response notes/comments
   - System logs all status changes in `audit_logs`

**Data Stored:**
- `disputes` table:
  - dispute_id (PK)
  - audit_result_id (FK) → Links to original error
  - invoice_id (FK)
  - submitted_date
  - submitted_by (user_id)
  - status (submitted | acknowledged | in_negotiation | approved | rejected)
  - disputed_amount
  - resolved_amount (if approved)
  - response_date
  - notes (JSON for user comments)
  - email_message_id (SendGrid tracking)

**API Endpoints:**
- `POST /api/v1/disputes/generate` → Generate draft dispute letter
  - Input: `invoice_id`
  - Output: `{ letter_html, attachments: [pdf, csv, ...], recipient_email }`
  
- `POST /api/v1/disputes/send` → Send dispute via email
  - Input: `{ letter_content, attachments, recipient_email, invoice_id }`
  - Output: `{ dispute_id, status, submission_time, email_id }`
  
- `GET /api/v1/disputes/{id}` → Get dispute details
  
- `PATCH /api/v1/disputes/{id}/status` → Update dispute status
  - Input: `{ status, notes, resolved_amount }`

#### Acceptance Criteria

- [ ] Generate professional dispute letter in <5 seconds
- [ ] Attach original invoice PDF, contract excerpt, and calculation sheet
- [ ] Allow user to edit letter before sending
- [ ] Send dispute email via SendGrid with proper formatting
- [ ] Track dispute submission with unique ID and timestamp
- [ ] Support manual status updates (submitted → acknowledged → approved/rejected)
- [ ] Auto-suggest carrier billing email address from invoice extraction data
- [ ] Log all dispute-related actions for audit trail
- [ ] Display dispute submission success confirmation
- [ ] Support resubmission of dispute if carrier doesn't respond (≥10 days)

#### Success Metrics

- <5 second dispute generation time
- 99% successful email delivery
- <2 minute average user time to review and send dispute
- <1 minute average status update time

---

## BUSINESS ESSENTIALS FEATURES (Months 1-3)

These features enable customer success, security, and operational management.

### 7. Client Onboarding Flow

**Category:** Business Essentials | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 1-2 | **Owner:** Full Stack Engineer

#### What It Does

Self-service setup for new clients to create an account, configure invoice ingestion, and validate the system is working with test data.

#### Business Value

- **User Acquisition:** Enable customers to start without sales team help
- **Time to Value:** New clients see first audit results within 24 hours
- **Data Security:** Clients control their own contract and invoice data
- **Compliance:** Audit trail of who onboarded, when, and what permissions they granted

#### Technical Specification

**Onboarding Flow:**

```
Step 1: Sign Up (2 min)
  → Email
  → Password (min 12 chars, complexity requirements)
  → Company Name
  → Full Name
  → Phone Number
  → Agree to Terms & Privacy Policy
  
  → Send confirmation email with link
  → User clicks link, account activated

Step 2: Account Setup (3 min)
  → Create first "organization" / "workspace"
  → Organization Name (e.g., "Acme Corp Freight")
  → Billing Contact (pre-filled from signup)
  → Billing Email (for invoices/alerts)
  
  → Generate unique invoice ingestion email
  → Display: "acmecorp@invoices.tesseract.ai"
  → Copy to clipboard button

Step 3: Contract Upload (5 min)
  → Upload contract PDF (S3 pre-signed URL)
  → System scans for rate tables
  → Display: "Contract uploaded. Admin will review within 24 hours."
  → (For MVP, manual extraction by admin; note in UI)
  
Step 4: Verify Ingestion (3 min)
  → Send test invoice to acmecorp@invoices.tesseract.ai
  → Dashboard shows: "Test invoice received! Processing..."
  → After extraction: "Test invoice processed. View here [link]"
  
Step 5: Complete Setup (2 min)
  → Review dashboard walkthrough
  → Invite additional users (optional)
  → View getting-started guide (PDF)
  → Set up notifications preferences
  
→ Onboarding Complete
  → Send welcome email with quick-start guide
  → Schedule optional onboarding call (Calendly link)
```

**Data Created During Onboarding:**
- `clients` → New client record
- `users` → Admin user account
- `organizations` → Workspace/account
- `invoices.ingestion_email` → Unique email address
- `contracts` → First contract (pending admin extraction)
- `user_preferences` → Notification settings

**Technical Implementation:**
- **Frontend:** Next.js form with step-by-step wizard
- **Backend APIs:**
  - `POST /api/v1/auth/signup` → Create user account
  - `POST /api/v1/clients` → Create new client record
  - `POST /api/v1/organizations` → Create workspace
  - `POST /api/v1/contracts/upload` → Pre-signed S3 URL
  - `POST /api/v1/test-invoice/send` → Send test invoice
  - `GET /api/v1/onboarding/status` → Get current step
- **Email:**
  - Confirmation email (account activation)
  - Welcome email (after setup complete)
  - Onboarding guide (PDF attachment)

#### Acceptance Criteria

- [ ] Complete onboarding in 15 minutes or less
- [ ] Email confirmation required for account activation
- [ ] Generate unique ingestion email address for each client
- [ ] Allow contract PDF upload (up to 100 MB)
- [ ] Send test invoice and confirm processing
- [ ] Create user, client, and organization records in database
- [ ] Display progress indicator showing onboarding step
- [ ] Allow users to skip steps and return later
- [ ] Send welcome email with setup guide and next steps
- [ ] Secure password reset flow
- [ ] Optional: Schedule onboarding call with Calendly integration

#### Success Metrics

- <15 minute average onboarding time
- 80%+ completion rate (users who start reach step 5)
- <24 hour activation time (email confirmation to dashboard access)

---

### 8. User Management & Permissions

**Category:** Business Essentials | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 2-3 | **Owner:** Backend Engineer

#### What It Does

Enable multi-user access with role-based permissions. Control who can view invoices, approve disputes, manage contracts, and administer the account.

#### Business Value

- **Team Collaboration:** Multiple users (CFO, accounting, logistics) can work together
- **Security:** Role-based access prevents unauthorized changes
- **Compliance:** Audit trail of who made what changes
- **Operational Efficiency:** Delegate invoice review and approval tasks

#### Technical Specification

**User Roles:**

| Role | Invoice View | Dispute Submit | Contract Mgmt | User Mgmt | Dashboard |
|------|--------------|----------------|--------------|-----------|-----------|
| **Admin** | ✓ Edit | ✓ Send | ✓ Full Edit | ✓ Add/Remove | ✓ All |
| **Reviewer** | ✓ View Only | ✓ Send | ✗ View Only | ✗ | ✓ View Only |
| **Viewer** | ✓ View Only | ✗ | ✗ View Only | ✗ | ✓ View Only |

**Detailed Permissions:**

**Admin:**
- View/edit all invoices and audit results
- Generate and send disputes
- Upload and manage contracts
- Edit contract rate tables
- Add/remove/edit users
- View all analytics and reports
- Configure billing settings
- Export data

**Reviewer:**
- View all invoices and audit results (read-only)
- Generate and send disputes
- Add notes/comments to invoices
- Cannot modify contract data
- Cannot add/remove users
- View dashboard (read-only)

**Viewer:**
- View dashboard and invoices (read-only)
- Cannot take any actions (no dispute submission)
- Cannot access admin settings
- Useful for executive overview

**User Management Interface:**

```
Settings → Team & Access

[+ Add User]

Current Users:
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Name         │ Email        │ Role         │ Last Active  │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ John Smith   │ john@acme... │ Admin        │ 2 hrs ago    │
│ Jane Doe     │ jane@acme... │ Reviewer     │ 15 mins ago  │
│ Bob Johnson  │ bob@acme...  │ Viewer       │ 1 month ago  │
└──────────────┴──────────────┴──────────────┴──────────────┘

Actions: [Edit] [Disable] [Resend Invite] [Remove]
```

**Technical Implementation:**

- **Authentication:** JWT-based (no session state on server)
- **Token Structure:**
  ```json
  {
    "sub": "user_id",
    "email": "user@company.com",
    "role": "admin|reviewer|viewer",
    "org_id": "org_id",
    "exp": 1704067200,
    "iat": 1704067200
  }
  ```

- **Authorization Middleware:**
  ```python
  def require_role(*allowed_roles):
      async def role_checker(request: Request):
          token = request.headers.get("Authorization")
          user_role = decode_token(token).role
          if user_role not in allowed_roles:
              raise HTTPException(status_code=403, detail="Insufficient permissions")
      return role_checker
  ```

- **Database Schema:**
  ```
  users:
    - user_id (PK)
    - email (unique)
    - password_hash
    - full_name
    - phone
    - role (admin | reviewer | viewer)
    - organization_id (FK)
    - created_at
    - last_login
    - is_active (bool)
    - is_email_verified (bool)
  
  user_sessions:
    - session_id (PK)
    - user_id (FK)
    - token_hash
    - created_at
    - expires_at
    - ip_address
    - user_agent
  
  user_actions (audit log):
    - action_id (PK)
    - user_id (FK)
    - action (dispute_sent, contract_uploaded, user_added, etc.)
    - resource_id (invoice_id, contract_id, etc.)
    - timestamp
  ```

**API Endpoints:**
- `POST /api/v1/users` → Invite new user
- `GET /api/v1/users` → List all users
- `PATCH /api/v1/users/{id}` → Update user role/status
- `DELETE /api/v1/users/{id}` → Remove user
- `POST /api/v1/auth/login` → Login with email/password
- `POST /api/v1/auth/password-reset` → Password reset flow
- `POST /api/v1/auth/refresh-token` → Refresh JWT

#### Acceptance Criteria

- [ ] Implement 3 role types with defined permissions
- [ ] JWT-based authentication with 24-hour token expiry
- [ ] Email/password login with secure hashing (bcrypt)
- [ ] Password reset flow via email link
- [ ] Admin can invite users, change roles, disable accounts
- [ ] Session tracking (last login, IP address) for security
- [ ] Audit log of all user actions (who accessed what, when)
- [ ] Display role and last active date in user list
- [ ] Auto-logout after 24 hours of inactivity
- [ ] Rate limiting on login attempts (5 attempts/15 minutes)

#### Success Metrics

- 100% of API routes protected with role checks
- <50ms authentication overhead per request
- Zero unauthorized access incidents
- 99.9% uptime of auth system

---

### 9. Contract Management

**Category:** Business Essentials | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 3-4 | **Owner:** Backend Engineer + Frontend Engineer

#### What It Does

Allows admins to upload carrier contracts, extract/enter rate tables, activate/deactivate contracts, and maintain version history. This data feeds the Contract Rate Matching and Error Detection engines.

#### Business Value

- **Rate Accuracy:** All rate comparisons based on current, authorized contracts
- **Version Control:** Track contract changes over time
- **Flexibility:** Support multiple contract formats and rate structures
- **Efficiency:** Bulk import rates via CSV to save time on data entry

#### Technical Specification

**Contract Upload Interface:**

```
Settings → Contracts

[+ Add New Contract]

Active Contracts:
┌──────────────────┬────────────┬──────────────┬──────────────┐
│ Contract Name    │ Carrier    │ Effective    │ Expires      │
├──────────────────┼────────────┼──────────────┼──────────────┤
│ XPO National 2024│ XPO        │ Jan 1, 2024  │ Dec 31, 2024 │
│ FedEx Regional...|FedEx Freight│ Mar 1, 2024 │ Feb 28, 2025 │
│ UPS LTL Growth   │ UPS        │ Apr 15, 2024 │ Apr 14, 2025 │
└──────────────────┴────────────┴──────────────┴──────────────┘

Archive:
[Show archived contracts]
```

**Contract Upload Process:**

1. **File Upload** (Drag-and-drop or file picker)
   - Accept PDF, Excel (.xlsx), CSV
   - Max size: 100 MB
   - Store in S3: `s3://tesseract-contracts/{org_id}/{contract_id}/{filename}`

2. **Contract Details** (User enters metadata)
   - Contract Name (e.g., "XPO National LTL 2024")
   - Carrier Name (auto-suggest from uploaded file)
   - Carrier SCAC (e.g., "XPO") → used for matching to invoices
   - Effective Date (start)
   - Expiration Date (end)
   - Rate Table Format (dropdown: per-hundredweight, flat rate, zone-based, tariff)
   - Primary Contact (name, email, phone)
   - Notes (optional, e.g., "Volume discount applies after 100 shipments")

3. **Rate Table Entry** (3 options)

   **Option A: Manual CSV Import**
   ```csv
   origin_zip_start,origin_zip_end,destination_zip_start,destination_zip_end,weight_min,weight_max,service_level,rate_per_100lb
   90000,90999,10000,19999,0,100,Ground,2.50
   90000,90999,10000,19999,101,500,Ground,2.35
   90000,90999,10000,19999,501,9999,Ground,2.15
   ```

   **Option B: Web Form Entry** (for small contracts)
   ```
   [+ Add Rate Rule]
   Origin ZIP Range: [90000] - [90999]
   Destination ZIP: [10000] - [19999]
   Weight Range: [0] - [100] lbs
   Service Level: [Ground ▼]
   Rate: $[2.50] per 100 lbs
   [Save]
   ```

   **Option C: Admin Manual Extraction** (for complex/legacy contracts)
   - Admin extracts rates from PDF manually
   - Tesseract team offers white-glove extraction (future premium feature)

4. **Accessorial Rules Entry**
   ```
   Approved Accessories:
   ☑ Liftgate Pickup - $75
   ☑ Liftgate Delivery - $75
   ☑ Residential Delivery - $50
   ☑ Inside Pickup - $100
   ☑ Inside Delivery - $100
   ☑ Redelivery - $100
   ☑ Holiday Delivery - $200
   ☐ Special Handling (requires justification)
   
   Unapproved (auto-flag if found):
   - Fuel Surcharge Exception
   - Late Delivery Fee
   - Customer-Requested Deviation
   ```

5. **Fuel Surcharge Rule** (if applicable)
   ```
   Fuel Surcharge Formula:
   ☑ Use DOE Index
     Formula: (Current Price - Base) / Base
     Base Price: $2.45/gallon
   
   OR
   
   ☑ Fixed FSC Percentage:
     FSC %: [2.5]% (fixed)
   
   OR
   
   ☑ Custom Formula:
     [Text field for custom calculation]
   ```

6. **Review & Activate**
   - Display summary of loaded rates (count, date range coverage)
   - Show sample rates for major lanes
   - "Activate" button to make contract live
   - Archive old contract (if new version of same contract)

**Data Schema:**

```
contracts:
  - contract_id (PK)
  - organization_id (FK)
  - carrier_name
  - carrier_scac
  - contract_name
  - contract_document_url (S3 path)
  - rate_table_type (per-100lb | flat | zone | tariff)
  - effective_date
  expiration_date
  - created_by (user_id)
  - created_at
  - is_active (bool)
  - version_number
  - parent_contract_id (FK) → for version history

contract_rates:
  - rate_id (PK)
  - contract_id (FK)
  - origin_zip_start
  - origin_zip_end
  - destination_zip_start
  - destination_zip_end
  - weight_min_lbs
  - weight_max_lbs
  - service_level
  - rate_per_100lb (nullable)
  - flat_rate (nullable)
  - zone_rate (nullable)
  - effective_date
  - created_at

contract_accessorials:
  - accessorial_id (PK)
  - contract_id (FK)
  - accessorial_name (e.g., "Liftgate Delivery")
  - charge_amount
  - is_approved (bool)
  - created_at

contract_fuel_rules:
  - fuel_rule_id (PK)
  - contract_id (FK)
  - fuel_rule_type (doe_index | fixed | custom)
  - base_price (for DOE index)
  - fixed_percentage (for fixed FSC)
  - custom_formula (for custom)
  - created_at
```

**API Endpoints:**
- `POST /api/v1/contracts` → Create new contract (metadata only)
- `POST /api/v1/contracts/{id}/upload` → Upload contract PDF/Excel
- `POST /api/v1/contracts/{id}/rates/import` → Bulk import rates (CSV)
- `POST /api/v1/contracts/{id}/rates` → Add single rate rule
- `GET /api/v1/contracts` → List all contracts
- `GET /api/v1/contracts/{id}` → Get contract details with rates
- `PUT /api/v1/contracts/{id}` → Update contract metadata
- `PATCH /api/v1/contracts/{id}/status` → Activate/archive
- `GET /api/v1/contracts/{id}/history` → View version history
- `DELETE /api/v1/contracts/{id}/rates/{rate_id}` → Remove individual rate

#### Acceptance Criteria

- [ ] Upload contract files up to 100 MB (PDF, Excel, CSV)
- [ ] Support 3+ rate table formats (per-hundredweight, flat rate, zone-based)
- [ ] Import rates via CSV (bulk) and web form (individual)
- [ ] Display count of loaded rates and sample rates for verification
- [ ] Activate/deactivate contracts by date range
- [ ] Maintain version history (can restore old contract versions)
- [ ] Track who created/edited each contract (`created_by`, `updated_by`)
- [ ] Allow 100+ rate entries per contract
- [ ] Support accessorial rules (approved/unapproved charge types)
- [ ] Support fuel surcharge formulas (DOE index, fixed %, custom)
- [ ] Validate rate table coverage (warn if gaps in ZIP code ranges or weight brackets)

#### Success Metrics

- <5 minute setup time for new contract
- 99%+ accuracy of imported rates (manual spot-check validation)
- <10 second bulk rate import for 1000+ rows
- 100% data integrity (no rate import failures)

---

### 10. Notification System

**Category:** Business Essentials | **Priority:** P0 (MVP Launch)  
**Timeline:** Week 5-6 | **Owner:** Backend Engineer

#### What It Does

Automatically sends email alerts for important events (new high-value errors, disputes approved, weekly summaries). Users can customize which notifications they receive.

#### Business Value

- **Real-Time Visibility:** Users know immediately about high-value opportunities
- **Engagement:** Keep users engaged with product value
- **Compliance:** Audit trail of all notifications sent
- **Flexibility:** Users control notification preferences

#### Technical Specification

**Notification Types:**

**1. High-Value Error Alert** (Real-Time)
- **Trigger:** New audit result with error_amount > $500 AND confidence > 80%
- **Delay:** <5 minutes after error detected
- **Recipients:** Admin + users with "Reviewer" role
- **Frequency:** Each error sent separately (no batching)
- **Content:**
  ```
  Subject: Alert: $475 Freight Overcharge Detected - Invoice INV-1245 (XPO)
  
  Hi John,
  
  A high-value error has been detected on a freight invoice.
  
  Error Details:
  - Carrier: XPO Logistics
  - Invoice: INV-1245
  - Error Type: Freight Rate Overcharge
  - Amount: $475 (15.2% over contract)
  - Contract Rate: $2.50/100lb
  - Billed Rate: $2.88/100lb
  
  Action Required: Review the invoice and submit a dispute if accuracy confirmed.
  [View Invoice >]
  
  This invoice is ready for dispute submission.
  ```

**2. Dispute Approved Alert** (Event-Triggered)
- **Trigger:** Admin manually updates dispute status to "approved" OR carrier auto-responds with credit memo
- **Delay:** Immediate
- **Recipients:** User who submitted dispute + admins
- **Content:**
  ```
  Subject: Recovery Confirmed - Invoice INV-1245 ($475 Credited)
  
  Hi John,
  
  Great news! Your dispute has been approved by XPO Logistics.
  
  Recovery Details:
  - Invoice: INV-1245
  - Disputed Amount: $475
  - Recovered Amount: $475 (100%)
  - Credit Memo Expected: Within 10 business days
  
  [View Dispute Details >]
  ```

**3. Weekly Summary** (Scheduled)
- **Trigger:** Scheduled daily at 8 AM local time, send if errors > 0
- **Recipients:** Admin + users with "Reviewer" role
- **Content:**
  ```
  Subject: Weekly Freight Recovery Summary - Week of Jan 15
  
  Hi Team,
  
  Here's your freight audit summary for the week:
  
  📊 Summary
  - Invoices Processed: 342
  - Errors Detected: 47
  - Recovery Potential: $5,250
  - Disputes Submitted: 23
  - Recoveries Received: $8,900
  
  🏆 Top Carriers by Error
  1. XPO: 18 errors ($2,100)
  2. FedEx: 12 errors ($1,850)
  3. UPS: 10 errors ($950)
  4. YRC: 5 errors ($350)
  5. Other: 2 errors ($100)
  
  💰 Recovery Trend (Last 4 weeks)
  Week 1: $4,200
  Week 2: $3,850
  Week 3: $6,100
  Week 4: $8,900 ↑
  
  [View Full Dashboard >]
  
  Next Steps: Review this week's top 5 errors and submit disputes.
  ```

**4. Monthly Summary** (Scheduled)
- **Trigger:** 1st of each month at 9 AM, send if month > 0
- **Recipients:** All users
- **Content:** Similar to weekly but with month-over-month comparison and P&L impact

**5. Admin Alert: Contract Expiring Soon** (Event-Triggered)
- **Trigger:** 30 days before contract expiration
- **Recipients:** Admins only
- **Content:**
  ```
  Subject: Action Required: XPO Contract Expires in 30 Days
  
  Your XPO Logistics contract expires on January 15, 2024.
  
  Action: Upload new contract or extend existing contract to maintain continuous rate matching.
  
  [Manage Contracts >]
  ```

**Technical Implementation:**

- **Email Service:** SendGrid (primary), AWS SES (fallback)
- **Job Queue:** Celery + Redis (for async processing)
- **Scheduling:** Celery Beat for recurring tasks
- **Tracking:** Store email sends in database for audit trail

**Notification Preferences UI:**

```
Settings → Notifications

Email Alerts:
☑ High-Value Errors Detected (>$500)
☑ Dispute Approved by Carrier
☑ Weekly Summary Report
☑ Monthly Summary Report
☐ All Disputed Invoices (verbose)
☐ System Maintenance Alerts

Frequency:
[Send Immediately ▼]

Unsubscribe: [Manage Email Preferences]
```

**Database Schema:**

```
notification_preferences:
  - preference_id (PK)
  - user_id (FK)
  - notification_type (high_value_error | dispute_approved | weekly_summary | ...)
  - is_enabled (bool)
  - frequency (immediate | daily | weekly)
  - created_at

notification_sends (audit log):
  - send_id (PK)
  - user_id (FK)
  - notification_type
  - recipient_email
  - subject
  - sent_at
  - sendgrid_message_id
  - bounced (bool)
  - opened (bool)
  - clicked (bool)
  - opened_at (timestamp)
```

**API Endpoints:**
- `GET /api/v1/users/{id}/notifications/preferences` → Get user preferences
- `PATCH /api/v1/users/{id}/notifications/preferences` → Update preferences
- `GET /api/v1/notifications/history` → View sent notifications (audit log)
- `POST /api/v1/notifications/test` → Send test email

#### Acceptance Criteria

- [ ] Send high-value error alerts within 5 minutes of error detection
- [ ] Allow users to customize which notifications they receive
- [ ] Support immediate, daily, and weekly frequency options
- [ ] Send weekly summary every Monday morning at 8 AM
- [ ] Include relevant data (carrier, invoice number, amounts, error type)
- [ ] Use HTML + plain text email versions for accessibility
- [ ] Track email delivery, opens, and clicks via SendGrid webhooks
- [ ] Maintain notification history for 90 days (audit trail)
- [ ] Include one-click unsubscribe link in all emails
- [ ] Support email preference center (users can update preferences without auth)

#### Success Metrics

- 98%+ email delivery rate
- <5% bounce rate
- <2 minute alert delivery time
- 30%+ email open rate (industry benchmark: 20-25%)
- 80%+ user satisfaction with notification content

---

## Summary Table

| Feature | Category | P0/P1 | Months | MVP Scope | Notes |
|---------|----------|-------|--------|-----------|-------|
| **1. Automated Invoice Ingestion** | Core | P0 | 1-2 | Email, web upload, S3 storage | +API Month 4 |
| **2. AI Data Extraction** | Core | P0 | 2-3 | Textract + GPT-4o, 95% accuracy | +Azure fallback Month 3 |
| **3. Contract Rate Matching** | Core | P0 | 3-4 | Per-100lb, flat, zone rates | Manual contract upload |
| **4. Error Detection** | Core | P0 | 4-5 | Overcharge, duplicate, accessorial, FSC | +ML models Month 4 |
| **5. Recovery Dashboard** | Core | P0 | 5-6 | Overview, queue, detail, analytics views | WebSocket real-time Month 4 |
| **6. Dispute Submission** | Core | P0 | 6 | Semi-automated (human-in-loop) | Full automation Month 4 |
| **7. Client Onboarding** | Essentials | P0 | 1-2 | 6-step wizard, test invoice | White-glove service Month 6 |
| **8. User Management** | Essentials | P0 | 2-3 | 3 roles, JWT auth, session tracking | OAuth Month 6 |
| **9. Contract Management** | Essentials | P0 | 3-4 | Upload, CSV import, version history | Admin extraction service Month 6 |
| **10. Notification System** | Essentials | P0 | 5-6 | Email alerts, preferences, SendGrid | SMS alerts Month 6 |

---

## Success Criteria for MVP Completion

The MVP is complete when:

1. **Core Workflow (6/6 features)** are production-ready:
   - ✅ 100+ invoices/hour ingestion capacity
   - ✅ 95%+ extraction accuracy on clear documents
   - ✅ 80%+ contract rate matching
   - ✅ 90%+ error detection recall
   - ✅ <2 second dashboard load time
   - ✅ Semi-automated dispute submission working

2. **Business Essentials (4/4 features)** are production-ready:
   - ✅ <15 minute onboarding time
   - ✅ Multi-user access with role-based permissions
   - ✅ Contract upload and rate management
   - ✅ Email notifications working (98%+ delivery rate)

3. **Operational Metrics:**
   - ✅ 5 pilot customers signed up
   - ✅ 10,000+ invoices processed
   - ✅ $100,000+ recovery potential identified
   - ✅ 80%+ dispute success rate on sampled invoices
   - ✅ 99.5%+ platform uptime
   - ✅ <100ms average API response time

4. **Security & Compliance:**
   - ✅ All data encrypted (S3, database)
   - ✅ Password hashing (bcrypt)
   - ✅ JWT-based authentication
   - ✅ Role-based access control enforced
   - ✅ Audit logs for all sensitive actions
   - ✅ GDPR compliance (privacy policy, data deletion)

---

## Development Roadmap

### Month 1: Foundation (Weeks 1-4)
- Weeks 1-2: Invoice Ingestion + Client Onboarding
- Weeks 2-3: AI Data Extraction + User Management
- Weeks 3-4: Contract Rate Matching + Contract Management

### Month 2: Core Workflow (Weeks 5-8)
- Week 4-5: Error Detection & Flagging
- Week 5-6: Recovery Dashboard
- Week 6: Dispute Submission
- Week 7-8: Testing, bug fixes, performance optimization

### Month 3: Launch & Scale (Weeks 9-12)
- Week 9: Security audit, penetration testing
- Week 10-11: Pilot customer onboarding, user feedback
- Week 12: Bug fixes, final optimizations, official launch

---

## Key Metrics & Targets

**Extraction Accuracy:**
- Clear PDFs: 95%+ accuracy
- Scanned documents: 85%+ accuracy
- Overall: 90%+ of invoices flagged as high-confidence (≥70%)

**Processing Performance:**
- Invoice ingestion: <10 seconds
- Data extraction: 15-30 seconds
- Rate matching: <5 seconds
- Error detection: <5 seconds
- Total end-to-end: <60 seconds per invoice

**Recovery Success:**
- Dispute win rate: 80%+ (industry benchmark: 75-85%)
- Recovery potential: 1.5-3% of freight spend
- False positive rate: <2% (non-errors flagged as errors)
- Human review rate: <20% (invoices requiring manual review)

**Platform Performance:**
- Dashboard load time: <2 seconds
- API response time: <100ms (p95)
- Uptime: 99.5%+
- Email delivery: 98%+

---

## Next Steps for Implementation

1. **Review this document** with product and engineering teams
2. **Validate feature scope** with potential pilot customers
3. **Prioritize features** within 3-month timeline
4. **Assign feature owners** for each of the 10 features
5. **Break down features** into technical user stories
6. **Set up development environment** (already done ✅)
7. **Begin Month 1 development** with Ingestion + Onboarding
8. **Weekly status reviews** against acceptance criteria

---

**Document Status:** Ready for Development ✅  
**Last Review:** December 2024  
**Next Review:** End of Month 1 (Incorporation of team feedback)
