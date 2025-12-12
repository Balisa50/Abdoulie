#!/usr/bin/env python3
"""
Tesseract Core Engine - Demo Workflow Script

This script demonstrates the complete invoice extraction and audit workflow.
It can run standalone (without the API) to show the core engine functionality.

Usage:
    python demo_workflow.py
"""

import sys
from pathlib import Path

# Add app to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.audit_engine import AuditEngine
from app.create_sample_invoice import (
    create_carrier_mismatch_invoice,
    create_overage_invoice,
    create_sample_invoice,
)
from app.document_processor import DocumentProcessor


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_extraction_results(data: dict) -> None:
    """Print extraction results in a formatted way."""
    print("\nExtracted Data:")
    for key, value in data.items():
        if value is not None:
            print(f"  ✓ {key:20s}: {value}")
        else:
            print(f"  ✗ {key:20s}: [NOT FOUND]")


def print_audit_results(anomalies: list) -> None:
    """Print audit results in a formatted way."""
    if not anomalies:
        print("\n✅ PASS - No anomalies detected. Invoice is compliant.")
        return

    print(f"\n❌ FAIL - {len(anomalies)} anomaly(ies) detected:\n")

    for i, anomaly in enumerate(anomalies, 1):
        severity_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        emoji = severity_emoji.get(anomaly["severity"], "⚪")

        print(f"{i}. {emoji} [{anomaly['severity']}] {anomaly['type']}")
        print(f"   Field: {anomaly['field']}")
        print(f"   Detail: {anomaly['detail']}")
        if anomaly.get("expected") is not None:
            print(f"   Expected: {anomaly['expected']}")
            print(f"   Actual: {anomaly['actual']}")
        print()


def demo_extraction_and_audit(
    pdf_path: str,
    scenario_name: str,
    shipment_data: dict,
    contract_rules: dict,
) -> None:
    """
    Demonstrate complete workflow: extraction + audit.
    """
    print_section(f"SCENARIO: {scenario_name}")

    # Step 1: Extract data from PDF
    print("\n[Step 1] Extracting data from PDF...")
    processor = DocumentProcessor()

    try:
        extracted_data = processor.process_invoice(pdf_path)
        print_extraction_results(extracted_data)
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return

    # Step 2: Audit the invoice
    print("\n[Step 2] Auditing invoice against contract rules...")
    print(f"\nContract Rules:")
    print(f"  Carrier: {contract_rules.get('carrier_name')}")
    print(f"  Max Rate: ${contract_rules.get('max_rate_per_mile')}/mile")
    print(f"\nShipment Data:")
    print(f"  Mileage: {shipment_data.get('mileage')} miles")

    engine = AuditEngine(contract_rules)

    try:
        anomalies = engine.audit(extracted_data, shipment_data)
        print_audit_results(anomalies)
    except Exception as e:
        print(f"❌ Audit failed: {e}")


def main() -> None:
    """
    Main demo workflow.
    """
    print("\n" + "=" * 70)
    print("  TESSERACT CORE ENGINE - INVOICE EXTRACTION & AUDIT DEMO")
    print("=" * 70)
    print("\nThis demo will:")
    print("  1. Generate sample invoice PDFs")
    print("  2. Extract structured data from each PDF")
    print("  3. Audit each invoice against contract rules")
    print("  4. Report any detected anomalies")

    # Generate sample invoices
    print_section("Generating Sample Invoice PDFs")

    try:
        create_sample_invoice()
        create_overage_invoice()
        create_carrier_mismatch_invoice()
        print("\n✓ Sample invoices created successfully")
    except Exception as e:
        print(f"\n❌ Failed to create sample invoices: {e}")
        return

    # Define contract rules
    contract_rules = {
        "carrier_name": "ROADWAY EXPRESS",
        "max_rate_per_mile": 3.50,
        "allowed_accessorials": ["FUEL SURCHARGE"],
        "min_string_similarity": 0.8,
    }

    # Define shipment reference data
    shipment_data = {"mileage": 450, "origin": "Chicago, IL", "destination": "Denver, CO"}

    # Scenario 1: Valid invoice
    demo_extraction_and_audit(
        pdf_path="sample_invoice.pdf",
        scenario_name="Valid Invoice (Within Contract Terms)",
        shipment_data=shipment_data,
        contract_rules=contract_rules,
    )

    # Scenario 2: Rate overage
    demo_extraction_and_audit(
        pdf_path="sample_invoice_overage.pdf",
        scenario_name="Rate Overage (Exceeds $3.50/mile limit)",
        shipment_data=shipment_data,
        contract_rules=contract_rules,
    )

    # Scenario 3: Carrier mismatch
    demo_extraction_and_audit(
        pdf_path="sample_invoice_wrong_carrier.pdf",
        scenario_name="Carrier Mismatch (Wrong carrier on invoice)",
        shipment_data=shipment_data,
        contract_rules=contract_rules,
    )

    # Summary
    print_section("DEMO COMPLETE")
    print("\nKey Capabilities Demonstrated:")
    print("  ✓ PDF text extraction with OCR fallback")
    print("  ✓ Structured field extraction (carrier, amount, date, etc.)")
    print("  ✓ Rate per mile calculation and validation")
    print("  ✓ Carrier name matching with fuzzy logic")
    print("  ✓ Anomaly detection with severity classification")
    print("  ✓ Detailed anomaly reporting")

    print("\n" + "=" * 70)
    print("  Next Steps:")
    print("=" * 70)
    print("\n1. Test with API endpoints:")
    print("   curl -X POST http://localhost:8000/invoice/extract \\")
    print('     -F "file=@sample_invoice.pdf"')
    print("\n2. View API documentation:")
    print("   http://localhost:8000/docs")
    print("\n3. Run comprehensive tests:")
    print("   pytest tests/ -v")
    print("\n4. Read technical documentation:")
    print("   cat backend/TESSERACT_CORE_ENGINE.md")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
