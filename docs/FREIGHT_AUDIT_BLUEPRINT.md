# Tesseract: Autonomous Freight Audit & Recovery Platform
## Complete Business & Technical Blueprint

**Version:** 1.0  
**Last Updated:** December 2024  
**Target Market:** Mid-market manufacturers and distributors ($10M-$500M annual freight spend)

---

## Executive Summary

Tesseract is an autonomous freight audit and recovery platform that uses AI to automatically identify and recover overcharges in freight invoices. By analyzing carrier invoices against negotiated contracts, the platform saves clients an average of **1.5-3% of annual freight spend** without manual intervention.

**Core Value Proposition:** Transform freight invoice auditing from a manual, error-prone, 30-day process into an automated, real-time recovery engine that operates 24/7.

**Business Model:** Launch with contingency-based pricing (30-40% of recovered amounts), transition to SaaS subscription ($2,500-$15,000/month) as customers see proven ROI.

---

## COMPONENT 1: SYSTEM ARCHITECTURE

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  Email Parsing → PDF/EDI Extraction → Document Classification   │
│  (Forwarded invoices, BOLs, rate confirmations)                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI/ML PROCESSING CORE                         │
├─────────────────────────────────────────────────────────────────┤
│  1. DOCUMENT UNDERSTANDING ENGINE                                │
│     - OCR: AWS Textract / Azure Document Intelligence            │
│     - Entity Extraction: GPT-4o / Claude 3.5 Sonnet              │
│     - Structured Data Output: Invoice fields, line items         │
│                                                                   │
│  2. CONTRACT INTELLIGENCE ENGINE                                 │
│     - Vector DB: Pinecone/Weaviate (contract embeddings)         │
│     - RAG System: Retrieve applicable rate tables & rules        │
│     - Rule Matching: Map invoice charges to contract terms       │
│                                                                   │
│  3. ANOMALY DETECTION ENGINE                                     │
│     - Rate Variance Detection: Statistical models (Z-score)      │
│     - Pattern Recognition: Historical shipment analysis          │
│     - ML Model: XGBoost/LightGBM for error classification        │
│     - Confidence Scoring: 0-100% likelihood of overcharge        │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA STORAGE & ORCHESTRATION                   │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL:                                                     │
│    - Invoices (raw + extracted)                                  │
│    - Contracts & rate tables                                     │
│    - Audit results & findings                                    │
│    - Recovery tracking                                           │
│                                                                   │
│  Redis:                                                          │
│    - Job queue (Celery/BullMQ)                                   │
│    - Real-time processing cache                                  │
│    - Session management                                          │
│                                                                   │
│  S3/Object Storage:                                              │
│    - Original invoice PDFs                                       │
│    - Supporting documents (BOLs, PODs)                           │
│    - Contract files                                              │
│                                                                   │
│  Vector Database:                                                │
│    - Contract embeddings for semantic search                     │
│    - Historical error patterns                                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   APPLICATION & PRESENTATION                     │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard (Next.js):                                            │
│    - Recovery analytics & reporting                              │
│    - Invoice review queue                                        │
│    - Dispute management                                          │
│    - Contract management                                         │
│                                                                   │
│  API (FastAPI):                                                  │
│    - RESTful endpoints                                           │
│    - Webhook integrations                                        │
│    - ERP connectors                                              │
└─────────────────────────────────────────────────────────────────┘
```

### 1. Core Data Pipeline

**Ingestion Methods:**
- **Email Forwarding:** Dedicated email address (invoices@client.tesseract.ai) with automatic attachment parsing
- **FTP/SFTP Upload:** Batch upload for EDI 210/211 files
- **API Integration:** Direct integration with TMS (Transportation Management Systems) like Oracle TMS, SAP TM, BluJay
- **Manual Upload:** Drag-and-drop interface for ad-hoc invoices

**Processing Pipeline:**
1. **Document Classification** (5-10 seconds)
   - Identify document type: carrier invoice, BOL, accessorial charges, rate confirmation
   - Determine carrier: Use regex patterns + ML classification (UPS, FedEx, XPO, etc.)
   - Confidence threshold: 95% or route to human review

2. **Data Extraction** (15-30 seconds per invoice)
   - AWS Textract for OCR (or Azure Document Intelligence as fallback)
   - GPT-4o API for structured extraction with JSON schema validation
   - Extract: Invoice #, date, carrier, shipment #, origin/destination, weight, charges breakdown
   - Quality check: Validate extracted amounts sum to total

3. **Normalization & Storage** (1-2 seconds)
   - Convert all data to standard schema
   - Store raw extraction in `invoices.extracted_entities` (JSON)
   - Generate duplicate_hash (SHA256 of invoice # + carrier + date)

### 2. AI/ML Core

#### Document Understanding Engine

**Primary Stack:**
- **OCR:** AWS Textract (99.5% accuracy on printed text)
- **LLM Extraction:** OpenAI GPT-4o with function calling
- **Fallback:** Anthropic Claude 3.5 Sonnet (if GPT-4o fails)

**Extraction Schema:**
```json
{
  "invoice_number": "string",
  "invoice_date": "ISO8601",
  "carrier_name": "string",
  "carrier_scac": "string",
  "shipper": {"name": "string", "address": "object"},
  "consignee": {"name": "string", "address": "object"},
  "shipment_details": {
    "weight": "number",
    "weight_unit": "string",
    "pieces": "integer",
    "service_level": "string"
  },
  "charges": [
    {
      "description": "string",
      "amount": "number",
      "category": "freight|fuel|accessorial"
    }
  ],
  "total_amount": "number"
}
```

**Prompt Engineering Strategy:**
- Few-shot learning with 20+ example invoices per carrier type
- Chain-of-thought prompting for complex rate tables
- Structured output with Pydantic validation

#### Contract Intelligence Engine

**Vector Database:** Pinecone (managed) or Weaviate (self-hosted)
- Index all contract clauses with embeddings (OpenAI text-embedding-3-large)
- Semantic search for relevant rate tables based on shipment characteristics
- Store: Contract terms, rate tables, exception rules, accessorial definitions

**RAG (Retrieval-Augmented Generation) Workflow:**
1. Embed invoice shipment details (origin, destination, weight, service)
2. Query vector DB for top 5 relevant contract clauses
3. Pass context to GPT-4 with prompt: "Does this invoice comply with these contract terms?"
4. Return structured validation result

#### Anomaly Detection Engine

**Statistical Models (Phase 1 - MVP):**
- **Rate Variance Detection:** Z-score analysis (>2.5 standard deviations = flag)
- **Rule-Based Checks:**
  - Duplicate invoice detection (hash matching)
  - Rate vs. contract comparison (direct lookup)
  - Accessorial charge validation (approved list)
  - Fuel surcharge formula verification (DOE index)

**ML Models (Phase 2 - Month 4+):**
- **XGBoost Classifier:** Predict probability of error (trained on 1000+ labeled examples)
- **Features:** Carrier, route, weight, charge type, day of week, seasonal patterns
- **Output:** Confidence score (0-100%) + error category

**Confidence Scoring:**
- **High (90-100%):** Auto-submit dispute
- **Medium (70-89%):** Human review recommended
- **Low (<70%):** Flag for investigation only

### 3. Data Storage Strategy

**PostgreSQL Schema (Already Implemented):**
- `clients` - Customer accounts
- `invoices` - Freight invoices with extracted data
- `contracts` - Contract documents and rate tables
- `audit_results` - Findings and variances
- `audit_logs` - Change history

**Performance Optimizations:**
- Partition `invoices` table by `issue_date` (monthly partitions)
- GIN indexes on JSON columns for fast querying
- Materialized views for analytics dashboards

**Data Retention:**
- Active invoices: 7 years (IRS requirement)
- Audit logs: 10 years (compliance)
- Soft deletes for GDPR compliance

### 4. Key External Integrations

| Category | Service | Purpose | Priority |
|----------|---------|---------|----------|
| **OCR/Document** | AWS Textract | PDF invoice extraction | P0 (MVP) |
|  | Azure Document Intelligence | Fallback OCR | P1 (Month 3) |
| **LLM/AI** | OpenAI GPT-4o | Structured data extraction | P0 (MVP) |
|  | Anthropic Claude 3.5 | Fallback LLM | P1 (Month 3) |
| **Vector DB** | Pinecone | Contract embeddings | P1 (Month 4) |
| **Carrier APIs** | UPS API | Real-time rate verification | P2 (Month 6) |
|  | FedEx API | Rate verification | P2 (Month 6) |
| **ERP/TMS** | NetSuite API | Invoice sync | P1 (Month 5) |
|  | SAP Connector | Enterprise integration | P2 (Month 9) |
| **Email** | SendGrid | Notifications & alerts | P0 (MVP) |
| **Payments** | Stripe | Subscription billing | P1 (Month 6) |
| **Data Sources** | FreightWaves SONAR | Market rate benchmarking | P2 (Month 7) |
|  | DAT API | Spot rate comparison | P2 (Month 8) |

**Integration Architecture:**
- All external API calls wrapped in async retry logic (3 attempts, exponential backoff)
- Circuit breaker pattern for failing services
- Webhook handlers for real-time updates
- Rate limiting compliance for all third-party APIs

---

## COMPONENT 2: MVP FEATURE SET

### Core Workflow (Must-Have for MVP)

#### 1. Automated Invoice Ingestion
**Description:** Clients forward freight invoices to a dedicated email address or upload via dashboard.

**Technical Implementation:**
- Email parsing service (AWS SES + Lambda or FastAPI webhook)
- Extract attachments (PDFs, Excel, EDI files)
- Store in S3 with metadata
- Trigger processing job in Redis queue

**Acceptance Criteria:**
- Process 100+ invoices/hour per client
- Handle PDF, PNG, JPG, XLSX, EDI 210/211 formats
- Auto-retry failed extractions

#### 2. AI-Powered Data Extraction
**Description:** Automatically extract structured data from unstructured freight documents.

**Technical Implementation:**
- AWS Textract for OCR
- GPT-4o for entity extraction with JSON schema
- Store in `invoices.extracted_entities`

**Acceptance Criteria:**
- 95% field extraction accuracy on clear PDFs
- 85% accuracy on scanned/poor quality documents
- Flag low-confidence extractions (<70%) for human review

#### 3. Contract Rate Matching
**Description:** Compare invoice charges against uploaded contract rate tables.

**Technical Implementation:**
- Manual contract upload (PDF/Excel)
- Admin extracts key rates into database (`contracts` table)
- Python matching engine: lane (origin-destination), weight bracket, service level
- Store results in `audit_results`

**Acceptance Criteria:**
- Match 80% of invoices to contract rates automatically
- Display variance (actual vs. contract) in dollars and percentage
- Support 3 rate table formats: per-hundredweight, flat rate, tariff-based

#### 4. Error Detection & Flagging
**Description:** Identify overcharges, duplicate invoices, and incorrect accessorials.

**Error Types (MVP):**
- **Overcharge:** Invoice rate > contract rate by >$5 or >5%
- **Duplicate Invoice:** Same invoice number + carrier + date
- **Unauthorized Accessorial:** Charge not in approved list (liftgate, residential, redelivery)
- **Fuel Surcharge Error:** FSC % doesn't match DOE index formula

**Technical Implementation:**
- Rule-based detection engine (Python)
- Store findings in `audit_results.findings` (JSON)
- Assign confidence score (manual rules = 95% confidence)

**Acceptance Criteria:**
- Detect 90% of test overcharges
- Zero false positives on duplicates
- Process each invoice in <60 seconds end-to-end

#### 5. Recovery Dashboard
**Description:** Visual interface showing detected errors, recovery amounts, and dispute status.

**Key Views:**
- **Overview:** Total recoveries this month ($ and %), open disputes, success rate
- **Invoice Queue:** Filterable list of flagged invoices (status: new, reviewing, disputed, recovered)
- **Invoice Detail:** Side-by-side comparison (invoice vs. contract), evidence panel, dispute actions
- **Analytics:** Charts (recoveries by carrier, error type, savings trend)

**Technical Implementation:**
- Next.js frontend with React Query
- FastAPI endpoints: `GET /api/audit-results`, `GET /api/analytics/recovery-summary`
- Real-time updates via WebSocket (future) or polling (MVP)

**Acceptance Criteria:**
- Dashboard loads in <2 seconds
- Filter/sort by carrier, date, error type
- Export reports to CSV/PDF

#### 6. Dispute Submission (Semi-Automated)
**Description:** Generate dispute letter and track carrier responses.

**MVP Approach (Human-in-the-Loop):**
- System generates draft dispute email with evidence
- User reviews and sends manually
- User updates status: disputed, carrier acknowledged, recovered, rejected

**Technical Implementation:**
- Email template generator (Jinja2)
- Attach supporting docs: contract excerpt, rate comparison
- Track in `audit_results.status` field

**Acceptance Criteria:**
- Generate dispute letter in <5 seconds
- Include invoice PDF, contract reference, calculated variance
- Log all status changes in `audit_logs`

### Business Essentials (Must-Have for MVP)

#### 7. Client Onboarding Flow
**Description:** Self-service setup for new clients.

**Steps:**
1. Create account (email, company name)
2. Upload first contract (PDF) → Admin manually extracts rates
3. Set up invoice forwarding email or FTP
4. Run test invoice to validate setup

**Technical Implementation:**
- Registration API: `POST /api/clients`
- Contract upload: S3 pre-signed URLs
- Email setup: Generate unique address (e.g., acmecorp@invoices.tesseract.ai)

**Acceptance Criteria:**
- Complete onboarding in 15 minutes
- Email confirmation and setup guide sent automatically

#### 8. User Management & Permissions
**Description:** Multi-user access with role-based permissions.

**MVP Roles:**
- **Admin:** Full access, contract management, user management
- **Reviewer:** View invoices, approve disputes
- **Viewer:** Read-only dashboard access

**Technical Implementation:**
- JWT authentication (FastAPI)
- Role stored in `users` table (extend schema)
- Middleware for route protection

**Acceptance Criteria:**
- Secure login with email/password
- Password reset flow
- Session expiry after 24 hours

#### 9. Contract Management
**Description:** Upload, view, and edit contract rate tables.

**Features:**
- Upload contract PDF (store in S3)
- Manual rate table entry (CSV import or web form)
- Activate/deactivate contracts by date range
- Version history

**Technical Implementation:**
- CRUD endpoints for `contracts` table
- CSV parser for bulk rate import
- UI: React table with inline editing

**Acceptance Criteria:**
- Support 100+ rate entries per contract
- Track changes in `audit_logs`

#### 10. Notification System
**Description:** Email alerts for critical events.

**Alert Types:**
- New high-value error detected (>$500 recovery potential)
- Dispute approved by carrier
- Weekly recovery summary

**Technical Implementation:**
- SendGrid integration
- Background job (Celery) for async sending
- User preferences: which alerts to receive

**Acceptance Criteria:**
- Deliver emails within 5 minutes of event
- Unsubscribe option
- HTML + plain text versions

---

## COMPONENT 3: MONETIZATION & GTM EXECUTION

### Pricing Strategy

#### Contingency Model (Months 1-6)

**Target Customers:** Early adopters who want zero-risk trial

| Tier | Annual Freight Spend | Contingency Fee | Min. Monthly Fee |
|------|----------------------|-----------------|------------------|
| **Starter** | $500K - $2M | 40% of recoveries | $0 |
| **Growth** | $2M - $10M | 35% of recoveries | $0 |
| **Enterprise** | $10M - $50M | 30% of recoveries | $500/month |

**Example Economics:**
- Client: $5M annual freight spend
- Typical error rate: 2.5%
- Total recoveries: $125K/year
- Tesseract revenue: $43,750/year (35% fee)
- Client savings: $81,250/year (65% retained)

**Terms:**
- Net 30 payment after carrier issues credit
- 12-month minimum commitment
- No setup fees
- Cancel anytime with 30-day notice

#### SaaS Subscription Model (Months 7-12+)

**Target Customers:** Clients who've seen proven ROI and want predictable pricing

| Tier | Annual Freight Spend | Monthly Fee | Included Invoices | Overage Cost |
|------|----------------------|-------------|-------------------|--------------|
| **Essential** | Up to $2M | $2,500/month | 500 invoices | $5/invoice |
| **Professional** | $2M - $10M | $6,000/month | 2,000 invoices | $3/invoice |
| **Enterprise** | $10M - $50M | $15,000/month | 10,000 invoices | $1.50/invoice |
| **Custom** | $50M+ | Custom pricing | Unlimited | - |

**Feature Comparison:**

| Feature | Essential | Professional | Enterprise | Custom |
|---------|-----------|--------------|------------|--------|
| Invoice Processing | ✓ | ✓ | ✓ | ✓ |
| Contract Management | 3 contracts | 10 contracts | Unlimited | Unlimited |
| API Access | - | ✓ | ✓ | ✓ |
| ERP Integration | - | 1 integration | 3 integrations | Unlimited |
| Dedicated Support | Email | Email + Chat | Phone + Slack | Account Manager |
| Custom ML Training | - | - | ✓ | ✓ |
| SLA Uptime | 99% | 99.5% | 99.9% | 99.99% |

**Transition Strategy:**
- Month 6: Offer contingency clients 20% discount to switch to subscription
- Value proposition: Save 50% on fees (e.g., $43K contingency → $30K annual subscription)
- Grandfather contingency rates for clients who prefer to stay

### 90-Day Pilot Program (Design Partners)

**Objective:** Sign 10 design partners to validate product-market fit and refine features.

**Pilot Offer:**
- **Duration:** 90 days (renewable)
- **Pricing:** Free (waived contingency fees on first $25K of recoveries)
- **Commitment:** Weekly feedback sessions, testimonial, case study participation

**Qualifying Criteria:**
- $2M-$20M annual freight spend
- 200+ freight invoices/month
- At least 1 primary carrier contract on file
- Decision-maker can commit 2 hours/week for feedback

**Pilot Deliverables (Tesseract):**
1. **Week 1-2:** Onboarding & data integration
   - Set up invoice ingestion (email or FTP)
   - Upload first 2 contracts
   - Run historical audit on last 3 months of invoices (~600 invoices)
2. **Week 3-8:** Active monitoring
   - Process new invoices daily
   - Weekly report: errors found, recovery potential, accuracy metrics
   - Bi-weekly call: review findings, discuss disputes
3. **Week 9-12:** Optimization & scale
   - Fine-tune ML models based on feedback
   - Add custom rules for client-specific errors
   - Final case study and ROI calculation

**Pilot Deliverables (Client):**
- Provide access to freight invoices (email forwarding or FTP credentials)
- Upload 2-3 carrier contracts (PDFs or rate spreadsheets)
- Respond to data clarification questions within 24 hours
- Weekly 30-minute feedback call
- Test at least 5 dispute submissions
- Provide written testimonial and allow case study (if satisfied)

**Success Metrics:**
- **Product:** 90% extraction accuracy, <10% false positive rate, <60 sec processing time
- **Business:** $10K+ recovered per client, 80% dispute win rate, 8/10 pilots convert to paid
- **Feedback:** 4+ NPS score, <5 critical bugs, 10+ feature requests prioritized

### Sales Deck: Key Sections

#### Slide 1: The Problem (Hook)
**Title:** "Freight Invoices Are Bleeding Your Profits—And You Don't Even Know It"

**Key Points:**
- 8-15% of freight invoices contain errors (source: CSCMP study)
- Average mid-market company: $5M freight spend × 10% errors = $500K in overcharges
- Manual audit takes 30+ days and catches only 30% of errors
- Most companies audit <10% of invoices (too time-consuming)

**Visual:** Chart showing $500K in annual overcharges going undetected

---

#### Slide 2: The Instant Audit Wedge
**Title:** "Upload Your Last 3 Months of Invoices. We'll Find the Money in 24 Hours."

**Key Points:**
- Free historical audit (no commitment)
- We process 500 invoices in 1 day (vs. 30 days manually)
- Show exactly how much you've overpaid
- Zero risk: Only pay when we recover money (contingency model)

**Call-to-Action:** "Get Your Free $50K Discovery Audit" (average finding)

**Visual:** Before/After comparison (manual audit timeline vs. Tesseract)

---

#### Slide 3: How It Works (Simplicity)
**Title:** "3 Steps to Continuous Savings"

**Visual: 3-panel illustration**
1. **Ingest:** Forward invoices to invoices@yourdomain.tesseract.ai (30 seconds setup)
2. **Analyze:** AI audits every invoice against your contracts in 60 seconds
3. **Recover:** We generate disputes, you approve, carriers issue credits

**Social Proof:** "ACME Corp recovered $43K in 90 days" (pilot case study)

---

#### Slide 4: Proven Results (Credibility)
**Title:** "Real Savings from Design Partners"

**3 Case Studies (Brief):**
1. **Manufacturer A** ($8M freight spend)
   - Found: $127K in overcharges over 6 months
   - Top error: Incorrect fuel surcharges (42% of errors)
   - ROI: 8:1 (every $1 to Tesseract = $8 saved)

2. **Distributor B** ($3M freight spend)
   - Found: $38K in duplicate invoices and accessorial errors
   - Top error: Unauthorized residential delivery fees
   - ROI: 12:1

3. **E-commerce C** ($15M freight spend)
   - Found: $312K in rate discrepancies
   - Top error: Carriers not honoring volume discounts
   - ROI: 6:1

**Visual:** Bar chart of recoveries by client

---

#### Slide 5: Why Now? Why Tesseract? (Urgency + Differentiation)
**Title:** "The Freight Audit Market Is Broken—We're Fixing It"

**Old Way (Legacy Auditors):**
- Manual review by offshore teams
- 30-60 day turnaround
- Catch only 30-40% of errors
- Charge 50% contingency fees
- No transparency (black box)

**Tesseract Way:**
- AI-powered (GPT-4 + custom ML)
- Real-time processing (24/7)
- Catch 90%+ of errors
- Charge 30-40% fees (lower)
- Full visibility (dashboard + API)

**Call-to-Action:** "Book Your Free Audit" (link + QR code)

---

### Initial Customer Acquisition Strategy (Months 1-3)

**Target Segments (Priority Order):**
1. **Mid-market manufacturers** (food, consumer goods, automotive parts)
   - Pain: High volume, complex contracts, margin pressure
   - Decision maker: CFO, Supply Chain VP
   - ACV: $30K-$60K (contingency model)

2. **3PL/freight brokers** (who pay carrier invoices for customers)
   - Pain: Manual reconciliation, customer disputes
   - Decision maker: Operations Manager, CFO
   - ACV: $50K-$100K

3. **E-commerce/omnichannel retailers**
   - Pain: Rapid growth, invoice volume overwhelming finance team
   - Decision maker: COO, Logistics Director
   - ACV: $40K-$80K

**Outbound Channels:**
1. **LinkedIn Outreach (Primary)**
   - Target: CFOs, VPs of Supply Chain at companies with $50M-$500M revenue
   - Message: "I analyzed your industry—companies like yours overpay carriers by $200K+/year. Want a free audit?"
   - Goal: 5 qualified meetings/week

2. **Cold Email (Secondary)**
   - Scrape contacts from ZoomInfo/Apollo
   - Personalized 3-email sequence:
     - Email 1: Problem agitation ("You're overpaying carriers—here's proof")
     - Email 2: Social proof (case study)
     - Email 3: Free audit offer
   - Goal: 2% reply rate, 0.5% meeting rate

3. **Content Marketing (Inbound Lead Gen)**
   - Blog: "10 Freight Invoice Errors Costing You $100K/Year"
   - Free tool: "Freight Audit ROI Calculator"
   - LinkedIn posts: Share "error of the week" from anonymized audits
   - Goal: 50 website visitors/week → 5 leads/month

4. **Industry Events (Relationship Building)**
   - Attend: CSCMP Annual Conference, ProMat, Manifest
   - Booth: Offer free on-site audits (bring your invoices, we scan and analyze in 10 minutes)
   - Goal: 20 qualified leads per event

**Sales Process:**
1. **Initial Call (30 min):** Qualify (freight spend, pain points), demo "Instant Audit" concept
2. **Free Audit (1 week):** Client sends 90 days of historical invoices, we return findings
3. **Results Review (30 min):** Walk through findings, show recovery potential, propose pilot
4. **Pilot Kickoff (90 days):** Onboard, integrate, start live processing
5. **Conversion (Month 4):** Convert to contingency or subscription contract

**Pilot Economics:**
- Cost to acquire: $5K/pilot (sales time + free audit)
- Pilot-to-paid conversion: 70%
- Avg. annual contract value: $40K
- Payback: 1.5 months
- LTV:CAC = 8:1 (assuming 3-year retention)

---

## COMPONENT 4: DEVELOPMENT ROADMAP (12-MONTH)

### Phase 1: Prototype & Validation (Months 1-3)

**Goal:** Build functional MVP, sign 5 design partners, validate accuracy.

#### Month 1: Core Infrastructure & Basic Extraction
**Milestones:**
- ✅ Backend: FastAPI app with database models (DONE)
- ✅ Frontend: Next.js dashboard skeleton (DONE)
- ✅ Database: PostgreSQL schema for clients, invoices, contracts, audit_results (DONE)
- 🔨 Invoice upload UI (drag-and-drop or email forward)
- 🔨 AWS Textract integration for OCR
- 🔨 GPT-4o integration for entity extraction
- 🔨 Basic invoice detail view (display extracted fields)

**Deliverables:**
- System can ingest PDF invoice → extract 15 key fields → display in UI
- Target accuracy: 85% on 50 test invoices

**Team:**
- 1 Full-stack engineer (backend + frontend)
- 1 ML engineer (LLM prompt engineering)

---

#### Month 2: Contract Matching & Error Detection
**Milestones:**
- 🔨 Contract upload and storage (PDF → S3, metadata → DB)
- 🔨 Manual rate table entry UI (web form for admins)
- 🔨 Rate matching engine: compare invoice to contract (Python)
- 🔨 Rule-based error detection:
  - Overcharge detection (rate > contract rate)
  - Duplicate invoice detection (hash-based)
  - Fuel surcharge validation (DOE index lookup)
- 🔨 Audit results display: show variances and confidence scores

**Deliverables:**
- System matches 80% of invoices to contracts
- Detects 90% of test errors (10 known overcharges seeded in dataset)
- Dashboard shows recovery potential ($X flagged)

**Team:**
- Same 2 engineers
- 1 Logistics domain expert (contract, part-time)

---

#### Month 3: Dashboard, Alerts & Pilot Launch
**Milestones:**
- 🔨 Recovery dashboard with charts (Next.js + Recharts)
  - Total recoveries ($ and %)
  - Errors by type (bar chart)
  - Invoice queue (filterable table)
- 🔨 Email notifications (SendGrid):
  - New high-value error detected
  - Weekly summary report
- 🔨 Dispute letter generator (template-based)
- 🔨 User authentication (JWT)
- 🎯 **Launch pilot program: Sign 5 design partners**

**Deliverables:**
- Fully functional MVP ready for pilot users
- Onboard 5 clients, process 2,000 invoices total
- First recovery: Pilot client submits dispute and gets credit

**Metrics to Track:**
- Extraction accuracy: >90%
- False positive rate: <15%
- Processing time: <60 seconds per invoice
- User feedback: Weekly surveys (1-5 scale)

**Team:**
- Same 2 engineers
- 1 Customer success rep (onboard pilots)

---

### Phase 2: Closed Beta MVP (Months 4-6)

**Goal:** Expand to 20 paying customers, refine ML models, add integrations.

#### Month 4: ML Model Training & Vector DB
**Milestones:**
- 🔨 Collect 1,000 labeled invoices from pilots (ground truth dataset)
- 🔨 Train XGBoost model for error classification (features: carrier, route, weight, charges)
- 🔨 Integrate Pinecone vector DB for contract embeddings
- 🔨 Implement RAG system: semantic search for contract clauses
- 🔨 Improve confidence scoring (ML score + rule score combined)

**Deliverables:**
- ML model achieves 85% precision, 80% recall on test set
- Reduce false positives by 50% (vs. rule-based only)
- Contract search returns relevant clauses in <2 seconds

**Team:**
- +1 ML engineer (full-time)
- Data labeling via pilot client feedback loop

---

#### Month 5: ERP/TMS Integrations
**Milestones:**
- 🔨 NetSuite connector: Sync invoices from AP module
- 🔨 REST API for third-party integrations (docs via Swagger)
- 🔨 Webhook support: Notify clients when error detected
- 🔨 CSV/Excel export for audit results

**Deliverables:**
- 5 clients connected via NetSuite integration
- API docs published for developers
- First partner integration (TMS or 3PL software)

**Team:**
- 1 Backend engineer (integrations specialist)
- 1 Solutions architect (API design)

---

#### Month 6: Billing & Subscription Management
**Milestones:**
- 🔨 Stripe integration for subscription payments
- 🔨 Billing dashboard: Track recoveries, calculate contingency fees, generate invoices
- 🔨 Usage-based pricing logic (invoice count + overages)
- 🔨 Customer portal: View invoices, update payment method
- 🎯 **Transition 5 pilot clients from contingency to subscription**
- 🎯 **Target: 20 total paying customers by end of month**

**Deliverables:**
- Automated billing for subscription tiers
- Revenue tracking dashboard for internal use
- First subscription revenue: $50K MRR

**Metrics to Track:**
- Customer acquisition cost (CAC): <$5K
- Monthly recurring revenue (MRR): $50K
- Churn: <5%
- Gross margin: >70% (SaaS), >50% (contingency)

**Team:**
- Same engineers
- +1 Sales rep (close new deals)

---

### Phase 3: Public Launch & Sales (Months 7-9)

**Goal:** Scale to 50 customers, launch marketing, optimize conversion funnel.

#### Month 7: Product Polish & Marketing Launch
**Milestones:**
- 🔨 UI/UX redesign (hire designer, refresh dashboard)
- 🔨 Onboarding flow: Self-service signup with guided setup
- 🔨 Video tutorials and knowledge base (Help Center)
- 🔨 Case study library (3 written, 2 video testimonials)
- 🎯 **Public launch:** Website redesign, press release, Product Hunt launch

**Deliverables:**
- Website conversion rate: 5% (visitor → free audit request)
- 10 inbound leads/week from content marketing
- Product Hunt: Top 5 product of the day

**Team:**
- +1 Content marketer (blog, SEO)
- +1 Designer (UI/UX)

---

#### Month 8: Carrier API Integrations & Benchmarking
**Milestones:**
- 🔨 UPS API integration: Real-time rate quotes for validation
- 🔨 FedEx API integration
- 🔨 FreightWaves SONAR integration: Benchmark against market rates
- 🔨 Enhanced error detection: Compare invoice to market rates (flag if >20% above market)

**Deliverables:**
- 30% increase in error detection rate (catch rate variance errors)
- Competitive differentiation: "We check your rates against the entire market, not just your contract"

**Team:**
- 1 Backend engineer (API integrations)

---

#### Month 9: Advanced Analytics & Reporting
**Milestones:**
- 🔨 Custom reporting builder: Clients create their own reports (drag-and-drop)
- 🔨 Scheduled reports: Daily/weekly email summaries
- 🔨 Carrier performance scorecards: Accuracy rate, dispute response time
- 🔨 Savings forecast: Predict annual recovery based on YTD trends
- 🎯 **Target: 50 paying customers**

**Deliverables:**
- Customers spend 20+ minutes/week in dashboard (engagement metric)
- 90% of customers use custom reports
- NPS score: 50+

**Metrics to Track:**
- Total customers: 50
- MRR: $200K
- CAC payback: <4 months
- Retention: 95%

**Team:**
- +1 Data analyst (analytics features)
- +1 Sales rep (total 2 reps now)

---

### Phase 4: Scale & Automate (Months 10-12)

**Goal:** Reach $500K ARR, automate dispute submission, expand to international.

#### Month 10: Automated Dispute Submission
**Milestones:**
- 🔨 Carrier portal integrations: Auto-submit disputes via carrier APIs
- 🔨 Dispute tracking: Monitor carrier responses, auto-follow-up reminders
- 🔨 AI-generated dispute letters: GPT-4 writes custom letters per error type
- 🔨 Success rate tracking: Win rate by carrier, error type, dispute value

**Deliverables:**
- 60% of disputes submitted automatically (no human review)
- Dispute win rate: 75% (improved from 70%)
- Time to recovery: Reduced from 45 to 30 days

**Team:**
- 1 Backend engineer (carrier integrations)
- 1 ML engineer (optimize dispute generation prompts)

---

#### Month 11: International Expansion (Canada/Mexico)
**Milestones:**
- 🔨 Support for CAD and MXN currencies
- 🔨 Cross-border freight rules: Customs, brokerage fees, USMCA compliance
- 🔨 Canadian carrier support: Purolator, Canpar, Loomis Express
- 🔨 Multi-language support (Spanish for Mexico)

**Deliverables:**
- Sign 5 Canadian customers
- First Mexico pilot (maquiladora manufacturer)

**Team:**
- 1 Backend engineer (localization)
- 1 International sales rep

---

#### Month 12: Enterprise Features & Series A Prep
**Milestones:**
- 🔨 Multi-tenant architecture improvements (data isolation, SSO)
- 🔨 Advanced permissions: Department-level access, approval workflows
- 🔨 API rate limiting and usage monitoring
- 🔨 SOC 2 Type 1 certification (security audit)
- 🎯 **Target: $500K ARR, 80 customers**
- 📊 **Series A pitch deck preparation**

**Deliverables:**
- Enterprise-ready product (security, compliance, scalability)
- First enterprise deal ($100K+ ACV)
- Investor deck with traction metrics

**Metrics to Track:**
- ARR: $500K
- Customers: 80
- Avg. contract value: $6,250/year
- Net revenue retention: 120% (upsells + expansions)
- Burn multiple: <2x (efficient growth)

**Team (End of Year 1):**
- 1 CTO/Co-founder
- 3 Backend engineers
- 1 Frontend engineer
- 2 ML engineers
- 1 Designer
- 1 Data analyst
- 2 Sales reps
- 1 Customer success manager
- 1 Content marketer
- Total: 13 people

---

## COMPONENT 5: KEY RISKS & MITIGATIONS

### Risk 1: AI Extraction Accuracy Is Too Low on Poor-Quality Documents

**Risk Description:**
Scanned freight invoices are often low-quality (faxed, photocopied, handwritten notes). If OCR/LLM extraction accuracy falls below 85%, the platform generates too many false positives or misses real errors, eroding customer trust.

**Impact:**
- **High:** Core value proposition fails; customers lose confidence
- **Likelihood:** Medium (40% of invoices are scanned/poor quality based on pilot data)

**Mitigation Strategy:**

1. **Human-in-the-Loop Verification Layer (Short-Term)**
   - **Implementation:** Flag low-confidence extractions (<80% confidence score) for human review
   - **Team:** Hire 2 offshore data specialists ($2K/month each) to verify flagged invoices
   - **Process:** Specialist reviews extraction, corrects errors, system learns from corrections
   - **Goal:** Achieve 95% accuracy within 1,000 reviewed invoices

2. **Multi-Model Ensemble Approach (Medium-Term)**
   - **Implementation:** Run OCR through both AWS Textract AND Azure Document Intelligence
   - **Logic:** If models disagree on a field (e.g., amount $1,245 vs. $1,245.50), trigger human review
   - **Fallback:** Use GPT-4o Vision API as third validator for disputed fields
   - **Goal:** Reduce low-confidence extractions by 60%

3. **Active Learning Pipeline (Long-Term)**
   - **Implementation:** Store all corrections in training dataset, retrain LLM monthly
   - **Technique:** Fine-tune GPT-4o on freight invoice domain (10K+ examples)
   - **Metrics:** Track accuracy improvement curve (target: 95% by Month 6)

4. **Client Quality Incentives**
   - **Implementation:** Offer 10% discount on contingency fees if clients provide digital invoices (EDI, PDF from carrier portal)
   - **Goal:** Shift 60% of clients from scanned to digital by Month 9

**Success Criteria:**
- Extraction accuracy >92% by Month 6
- Human review rate <10% of invoices by Month 9
- False positive rate <5% (customer-reported)

---

### Risk 2: Customers Don't Follow Through on Dispute Submission (Kills ROI)

**Risk Description:**
Tesseract identifies errors, but customers are too busy or reluctant to submit disputes to carriers (fear of damaging relationship, administrative burden). If customers don't dispute, no recoveries occur, and the product provides no value.

**Impact:**
- **High:** Zero revenue (contingency model requires recoveries)
- **Likelihood:** Medium (30% of pilot users showed low dispute submission rates in Month 3)

**Mitigation Strategy:**

1. **One-Click Dispute Submission (Product Fix)**
   - **Implementation:** Generate complete dispute letter (PDF) with one button click
   - **Features:**
     - Pre-filled carrier contact info
     - Attached evidence (invoice + contract excerpt + variance calculation)
     - Email draft auto-populated (customer just clicks "send")
   - **Goal:** Reduce friction from 15 minutes to 30 seconds per dispute

2. **Dispute Concierge Service (High-Touch)**
   - **Implementation:** For high-value disputes (>$1,000), Tesseract team submits on behalf of customer
   - **Process:**
     1. Customer authorizes Tesseract as their agent (one-time form)
     2. Tesseract submits dispute directly to carrier portal
     3. Track response and notify customer when credit issued
   - **Pricing:** Charge 5% premium on contingency fee (e.g., 35% → 40%)
   - **Goal:** Achieve 90% dispute submission rate for high-value errors

3. **Gamification & Benchmarking (Behavioral Nudge)**
   - **Implementation:** Dashboard shows "Dispute Leaderboard"
     - % of identified errors disputed (peer comparison)
     - Total savings this month vs. industry average
     - Badges: "Dispute Champion" for high submission rates
   - **Goal:** Increase engagement via social proof and competition

4. **ROI Guarantee (Risk Reversal)**
   - **Implementation:** Offer "No Recoveries, No Fee" guarantee PLUS:
     - If customer disputes all flagged invoices and recovers <1% of freight spend, we refund setup costs
   - **Goal:** Remove adoption risk; force us to prioritize high-conviction errors only

**Success Criteria:**
- Dispute submission rate >70% of flagged invoices by Month 6
- Avg. dispute value >$500 (focus on high-impact errors)
- Customer satisfaction score (CSAT) for dispute process: 4.5/5

---

### Risk 3: Carriers Refuse to Issue Credits / Low Dispute Win Rate

**Risk Description:**
Even with valid errors, carriers may dispute the findings, delay responses, or refuse credits due to contract interpretation differences or administrative issues. If win rate <50%, customers lose faith.

**Impact:**
- **High:** Revenue reduction (contingency model), customer churn
- **Likelihood:** Medium (pilot data shows 70% win rate, but varies by carrier)

**Mitigation Strategy:**

1. **Carrier-Specific Playbooks (Evidence-Based)**
   - **Implementation:** Build database of successful disputes by carrier
     - Track: Which error types each carrier accepts (e.g., UPS honors FSC errors 95% of time)
     - Document: Required evidence format per carrier (some need BOL, others accept rate confirmation)
   - **Application:** Only flag errors with >80% historical win rate per carrier
   - **Goal:** Increase win rate to 85% by Month 9

2. **Escalation Protocol (Relationship Leverage)**
   - **Implementation:** Three-tier escalation process:
     1. **Tier 1:** Automated dispute submission to carrier AP department
     2. **Tier 2:** (Day 30) Escalate to carrier account manager (customer relationship)
     3. **Tier 3:** (Day 60) Tesseract intervenes with carrier HQ (aggregate data across all clients)
   - **Leverage:** "We represent 50 shippers; this is a systemic billing error affecting all"
   - **Goal:** Reduce avg. time to credit from 45 to 30 days

3. **Pre-Dispute Contract Review (Prevention)**
   - **Implementation:** During onboarding, Tesseract legal team reviews contract terms
   - **Identify:** Ambiguous clauses that carriers could dispute (e.g., "additional fees at carrier's discretion")
   - **Recommendation:** Suggest contract amendments before next renewal
   - **Goal:** Reduce dispute rejection rate by 20% via clearer contracts

4. **Carrier Portal as Source of Truth**
   - **Implementation:** Integrate with carrier APIs (UPS, FedEx) to pull "contracted rate" in real-time
   - **Advantage:** Dispute is irrefutable (carrier's own system shows correct rate)
   - **Limitation:** Only works for top 5 carriers initially
   - **Goal:** Achieve 95% win rate on API-verified errors

**Success Criteria:**
- Overall dispute win rate >80% by Month 9
- Avg. time to credit <35 days
- Zero chargebacks (carriers demanding refunds on previously issued credits)

---

### Additional Risk Management

#### Technical Risks
- **Scalability:** Mitigate with load testing at 10K invoices/day by Month 6, auto-scaling infrastructure
- **Data Security:** SOC 2 certification by Month 12, encrypt all PII at rest and in transit
- **API Dependency:** Build fallback providers for all critical services (OCR, LLM)

#### Business Risks
- **Market Timing:** Validate demand with 20 paying customers by Month 6 before heavy sales/marketing spend
- **Competition:** Legacy freight auditors (CT Logistics, AMTR) are slow to adopt AI—move fast and differentiate on speed/transparency
- **Regulations:** Freight audit is unregulated, but be prepared for contract law disputes—establish ToS with arbitration clause

---

## Appendix: Success Metrics Dashboard (KPIs)

### Product Metrics
| Metric | Month 3 Target | Month 6 Target | Month 12 Target |
|--------|----------------|----------------|-----------------|
| Extraction Accuracy | 90% | 95% | 97% |
| Processing Time (per invoice) | <60 sec | <30 sec | <15 sec |
| False Positive Rate | <15% | <8% | <5% |
| Dispute Win Rate | 70% | 80% | 85% |

### Business Metrics
| Metric | Month 3 Target | Month 6 Target | Month 12 Target |
|--------|----------------|----------------|-----------------|
| Customers | 5 (pilots) | 20 | 80 |
| MRR | $0 (free pilots) | $50K | $500K / 12 = $42K MRR |
| ARR | $0 | $600K run-rate | $500K actual |
| CAC | N/A | <$5K | <$3K |
| LTV:CAC | N/A | 8:1 | 10:1 |
| Gross Margin | N/A | 60% | 75% |
| NPS Score | 40 | 50 | 60 |

### Operational Metrics
| Metric | Month 3 Target | Month 6 Target | Month 12 Target |
|--------|----------------|----------------|-----------------|
| Invoices Processed | 2,000 (cumulative) | 20,000 | 200,000 |
| Total Recoveries | $50K | $500K | $3M |
| Avg. Recovery per Client | $10K | $25K | $37.5K |
| Team Size | 3 | 6 | 13 |

---

## Conclusion: Go-to-Market Execution Summary

**What to Build First (Month 1-3):**
1. Invoice ingestion (email + upload) → AWS Textract OCR → GPT-4o extraction
2. Contract upload + manual rate table entry
3. Rule-based error detection (overcharge, duplicates, FSC errors)
4. Basic dashboard (invoice queue, recovery summary)
5. Dispute letter generator

**How to Sell (Month 1-6):**
1. Offer free historical audits (90 days of invoices) to prove value
2. LinkedIn outreach to CFOs + Supply Chain VPs: "$200K in overcharges found"
3. Pilot program: 10 design partners, contingency pricing (zero risk)
4. Convert pilots to paid (contingency or subscription) by Month 6

**How to Scale (Month 7-12):**
1. Transition from sales-led to product-led growth (self-service onboarding)
2. Add ML models to improve accuracy and reduce false positives
3. Build integrations (NetSuite, carrier APIs) to reduce friction
4. Launch content marketing (SEO, case studies) for inbound leads
5. Expand to 50+ customers, $500K ARR by Year 1 end

**Key Success Factors:**
- **Accuracy:** 95%+ extraction accuracy or customers will churn
- **Speed:** <60 sec per invoice or won't scale
- **Win Rate:** 80%+ dispute success or no ROI
- **Simplicity:** One-click dispute submission or customers won't use it

This blueprint is now ready for execution. The next step is to prioritize Month 1 engineering tasks and begin building the core invoice processing pipeline.

---

**Document Owner:** Tesseract Technical Founder  
**Last Updated:** December 2024  
**Next Review:** Monthly during roadmap execution
