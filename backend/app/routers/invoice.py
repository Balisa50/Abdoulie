import logging
import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.audit_engine import AuditEngine
from app.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/invoice", tags=["invoice"])


class ExtractResponse(BaseModel):
    """Response model for invoice extraction endpoint."""

    success: bool
    data: dict[str, Any]
    message: str | None = None


class AuditRequest(BaseModel):
    """Request model for invoice audit endpoint."""

    invoice_data: dict[str, Any] = Field(
        ...,
        description="Extracted invoice data",
        examples=[
            {
                "carrier_name": "ROADWAY EXPRESS",
                "invoice_number": "INV-2024-001",
                "invoice_date": "2024-01-15",
                "total_charge": 1857.50,
                "shipment_reference": "PRO-12345",
            }
        ],
    )
    shipment_data: dict[str, Any] = Field(
        ...,
        description="Reference shipment data",
        examples=[{"mileage": 450, "origin": "Chicago, IL", "destination": "Denver, CO"}],
    )
    contract_rules: dict[str, Any] | None = Field(
        None,
        description="Contract rules to validate against (optional, uses defaults if not provided)",
        examples=[
            {
                "carrier_name": "ROADWAY EXPRESS",
                "max_rate_per_mile": 3.50,
                "allowed_accessorials": ["FUEL SURCHARGE"],
            }
        ],
    )


class AuditResponse(BaseModel):
    """Response model for invoice audit endpoint."""

    success: bool
    anomalies: list[dict[str, Any]]
    anomaly_count: int
    message: str | None = None


@router.post("/extract", response_model=ExtractResponse)
async def extract_invoice(file: UploadFile = File(...)) -> ExtractResponse:
    """
    Extract structured data from a freight invoice PDF.

    Accepts a PDF file upload and returns extracted fields including:
    - carrier_name
    - invoice_number
    - invoice_date
    - total_charge
    - shipment_reference

    Uses hybrid extraction: direct text extraction with OCR fallback.
    """
    logger.info(f"Received file upload: {file.filename}")

    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        logger.info(f"Saved temporary file: {tmp_path}")

        # Process the invoice
        processor = DocumentProcessor()
        extracted_data = processor.process_invoice(tmp_path)

        # Clean up temporary file
        Path(tmp_path).unlink(missing_ok=True)

        # Check if extraction was successful
        if not any(extracted_data.values()):
            return ExtractResponse(
                success=False,
                data=extracted_data,
                message="No data could be extracted from the PDF. The document may be empty or unreadable.",
            )

        return ExtractResponse(
            success=True, data=extracted_data, message="Invoice data extracted successfully"
        )

    except Exception as e:
        logger.error(f"Error processing invoice: {e}", exc_info=True)
        # Clean up temporary file on error
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass

        raise HTTPException(status_code=500, detail=f"Error processing invoice: {str(e)}")


@router.post("/audit", response_model=AuditResponse)
async def audit_invoice(request: AuditRequest) -> AuditResponse:
    """
    Audit an invoice against contract rules and detect anomalies.

    Performs automated checks including:
    - Rate per mile validation (overage detection)
    - Carrier name matching
    - Charge validation
    - Additional business rule checks

    Returns a list of detected anomalies with severity levels.
    """
    logger.info("Starting invoice audit")

    # Use default contract rules if not provided
    contract_rules = request.contract_rules or {
        "carrier_name": "ROADWAY EXPRESS",
        "max_rate_per_mile": 3.50,
        "allowed_accessorials": ["FUEL SURCHARGE"],
        "min_string_similarity": 0.8,
    }

    try:
        # Initialize audit engine
        engine = AuditEngine(contract_rules)

        # Perform audit
        anomalies = engine.audit(request.invoice_data, request.shipment_data)

        return AuditResponse(
            success=True,
            anomalies=anomalies,
            anomaly_count=len(anomalies),
            message=f"Audit complete: {len(anomalies)} anomalies detected"
            if anomalies
            else "Audit complete: no anomalies detected",
        )

    except Exception as e:
        logger.error(f"Error during audit: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during audit: {str(e)}")
