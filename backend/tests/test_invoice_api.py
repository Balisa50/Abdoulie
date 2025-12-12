import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestInvoiceAPI:
    """Test suite for invoice API endpoints."""

    def test_extract_endpoint_success(self) -> None:
        """
        Test that the /invoice/extract endpoint successfully processes a PDF.
        """
        # Arrange: Create a simple PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf_path = tmp_file.name

        try:
            # Create PDF with sample invoice content
            doc = fitz.open()
            page = doc.new_page(width=612, height=792)

            text_content = """
            FREIGHT INVOICE
            Carrier: ROADWAY EXPRESS
            Invoice: INV-2024-001
            Date: 01/15/2024
            PRO: PRO-12345
            Total: $1,575.00
            """

            page.insert_text((50, 100), text_content)
            doc.save(pdf_path)
            doc.close()

            # Act: Upload the PDF
            with open(pdf_path, "rb") as f:
                response = client.post(
                    "/invoice/extract", files={"file": ("test_invoice.pdf", f, "application/pdf")}
                )

            # Assert
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert isinstance(data["data"], dict)

        finally:
            Path(pdf_path).unlink(missing_ok=True)

    def test_extract_endpoint_rejects_non_pdf(self) -> None:
        """
        Test that the endpoint rejects non-PDF files.
        """
        # Arrange: Create a text file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(b"This is not a PDF")
            txt_path = tmp_file.name

        try:
            # Act
            with open(txt_path, "rb") as f:
                response = client.post(
                    "/invoice/extract", files={"file": ("test.txt", f, "text/plain")}
                )

            # Assert
            assert response.status_code == 400
            assert "PDF" in response.json()["detail"]

        finally:
            Path(txt_path).unlink(missing_ok=True)

    def test_audit_endpoint_success(self) -> None:
        """
        Test that the /invoice/audit endpoint correctly audits an invoice.
        """
        # Arrange
        request_data = {
            "invoice_data": {
                "carrier_name": "ROADWAY EXPRESS",
                "invoice_number": "INV-2024-001",
                "total_charge": 1575.00,
            },
            "shipment_data": {"mileage": 450},
            "contract_rules": {
                "carrier_name": "ROADWAY EXPRESS",
                "max_rate_per_mile": 3.50,
            },
        }

        # Act
        response = client.post("/invoice/audit", json=request_data)

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "anomalies" in data
        assert "anomaly_count" in data
        assert isinstance(data["anomalies"], list)
        assert data["anomaly_count"] == len(data["anomalies"])

    def test_audit_endpoint_detects_rate_overage(self) -> None:
        """
        Test that the audit endpoint correctly detects rate overage.
        """
        # Arrange: Invoice with $4.12/mile rate (over $3.50 limit)
        request_data = {
            "invoice_data": {
                "carrier_name": "ROADWAY EXPRESS",
                "total_charge": 1857.50,  # $4.12/mile
            },
            "shipment_data": {"mileage": 450},
            "contract_rules": {
                "carrier_name": "ROADWAY EXPRESS",
                "max_rate_per_mile": 3.50,
            },
        }

        # Act
        response = client.post("/invoice/audit", json=request_data)

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["anomaly_count"] > 0

        # Verify rate overage anomaly is present
        anomalies = data["anomalies"]
        rate_anomalies = [a for a in anomalies if a["type"] == "RATE_OVERAGE"]
        assert len(rate_anomalies) > 0, "Should detect rate overage"

    def test_audit_endpoint_detects_carrier_mismatch(self) -> None:
        """
        Test that the audit endpoint correctly detects carrier mismatch.
        """
        # Arrange
        request_data = {
            "invoice_data": {
                "carrier_name": "FEDEX FREIGHT",  # Wrong carrier
                "total_charge": 1500.00,
            },
            "shipment_data": {"mileage": 450},
            "contract_rules": {
                "carrier_name": "ROADWAY EXPRESS",
                "max_rate_per_mile": 3.50,
            },
        }

        # Act
        response = client.post("/invoice/audit", json=request_data)

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["anomaly_count"] > 0

        # Verify carrier mismatch anomaly is present
        anomalies = data["anomalies"]
        carrier_anomalies = [a for a in anomalies if a["type"] == "CARRIER_MISMATCH"]
        assert len(carrier_anomalies) > 0, "Should detect carrier mismatch"

    def test_audit_endpoint_uses_default_contract_rules(self) -> None:
        """
        Test that the audit endpoint uses default contract rules when not provided.
        """
        # Arrange: Request without contract_rules
        request_data = {
            "invoice_data": {
                "carrier_name": "ROADWAY EXPRESS",
                "total_charge": 1500.00,
            },
            "shipment_data": {"mileage": 450},
        }

        # Act
        response = client.post("/invoice/audit", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_audit_endpoint_handles_missing_fields(self) -> None:
        """
        Test that the audit endpoint handles missing required fields.
        """
        # Arrange: Missing critical fields
        request_data = {
            "invoice_data": {"invoice_number": "INV-001"},  # Missing carrier and charge
            "shipment_data": {},  # Missing mileage
        }

        # Act
        response = client.post("/invoice/audit", json=request_data)

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["anomaly_count"] > 0

        # Should detect missing fields
        anomalies = data["anomalies"]
        missing_anomalies = [a for a in anomalies if a["type"] == "MISSING_FIELD"]
        assert len(missing_anomalies) > 0, "Should detect missing fields"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
