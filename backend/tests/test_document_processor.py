import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest

from app.document_processor import DocumentProcessor


class TestDocumentProcessor:
    """Test suite for the DocumentProcessor."""

    def test_extract_fields_from_text(self) -> None:
        """
        Test that fields are correctly extracted from invoice text.
        """
        # Arrange
        processor = DocumentProcessor()

        sample_text = """
        FREIGHT INVOICE
        
        From: ROADWAY EXPRESS INC
        Invoice #: INV-2024-12345
        Date: 03/15/2024
        
        Shipment Reference: PRO-98765
        
        Total Amount Due: $1,857.50
        
        Thank you for your business.
        """

        # Act
        extracted = processor._extract_fields(sample_text)

        # Assert
        assert extracted["carrier_name"] is not None
        assert "ROADWAY EXPRESS" in extracted["carrier_name"]

        assert extracted["invoice_number"] is not None
        assert "INV-2024-12345" in extracted["invoice_number"]

        assert extracted["invoice_date"] is not None

        assert extracted["total_charge"] is not None
        assert extracted["total_charge"] == 1857.50

        assert extracted["shipment_reference"] is not None
        assert "PRO-98765" in extracted["shipment_reference"]

    def test_date_normalization(self) -> None:
        """
        Test that various date formats are normalized correctly.
        """
        # Arrange
        processor = DocumentProcessor()

        # Act & Assert
        assert processor._normalize_date("03/15/2024") == "2024-03-15"
        assert processor._normalize_date("03-15-2024") == "2024-03-15"
        assert processor._normalize_date("3/15/24") == "2024-03-15"

    def test_text_quality_assessment(self) -> None:
        """
        Test that poor text quality is correctly identified.
        """
        # Arrange
        processor = DocumentProcessor()

        good_text = "This is a properly formatted invoice with lots of readable text content."
        poor_text = "abc"
        garbled_text = "∂ƒ˙©˙∆˚¬∆˚¬∂∫˜˚∆√ç≈"

        # Act & Assert
        assert not processor._is_text_quality_poor(good_text), "Good text should pass"
        assert processor._is_text_quality_poor(poor_text), "Short text should fail"
        assert processor._is_text_quality_poor(garbled_text), "Garbled text should fail"

    def test_process_invoice_with_sample_pdf(self) -> None:
        """
        Test processing a simple PDF invoice (integration test).
        """
        # Arrange: Create a simple PDF with invoice data
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf_path = tmp_file.name

        try:
            # Create PDF with sample invoice content
            doc = fitz.open()
            page = doc.new_page(width=612, height=792)

            text_content = """
            FREIGHT INVOICE
            
            Carrier: ROADWAY EXPRESS
            Invoice Number: INV-2024-001
            Invoice Date: 01/15/2024
            
            PRO Number: PRO-12345
            
            Total Charge: $1,575.00
            """

            page.insert_text((50, 100), text_content)
            doc.save(pdf_path)
            doc.close()

            # Act
            processor = DocumentProcessor()
            result = processor.process_invoice(pdf_path)

            # Assert
            assert result is not None
            assert isinstance(result, dict)

            # Should extract at least some fields
            extracted_values = [v for v in result.values() if v is not None]
            assert len(extracted_values) > 0, "Should extract at least one field"

        finally:
            # Cleanup
            Path(pdf_path).unlink(missing_ok=True)

    def test_handles_missing_fields_gracefully(self) -> None:
        """
        Test that processor handles invoices with missing fields gracefully.
        """
        # Arrange
        processor = DocumentProcessor()

        incomplete_text = """
        Some random invoice text without proper structure.
        No clear fields present.
        """

        # Act
        extracted = processor._extract_fields(incomplete_text)

        # Assert
        assert isinstance(extracted, dict), "Should return a dict"
        assert len(extracted) > 0, "Should have field keys"

        # Fields may be None, but dict should be properly structured
        for field in ["carrier_name", "invoice_number", "total_charge"]:
            assert field in extracted, f"Field '{field}' should be present in result"

    def test_total_charge_parsing(self) -> None:
        """
        Test that various total charge formats are parsed correctly.
        """
        # Arrange
        processor = DocumentProcessor()

        test_cases = [
            ("Total: $1,234.56", 1234.56),
            ("Amount Due: 999.99", 999.99),
            ("Balance: $5,000.00", 5000.00),
            ("TOTAL $100", 100.0),
        ]

        # Act & Assert
        for text, expected_amount in test_cases:
            extracted = processor._extract_fields(text)
            assert (
                extracted["total_charge"] == expected_amount
            ), f"Failed to parse: {text} (expected {expected_amount}, got {extracted['total_charge']})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
