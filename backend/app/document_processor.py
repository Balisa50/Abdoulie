import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import fitz  # PyMuPDF
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processes freight invoice PDFs to extract structured data.
    Uses hybrid approach: direct text extraction with OCR fallback.
    """

    def __init__(self) -> None:
        self.field_patterns = {
            "carrier_name": [
                r"carrier[:\s]+([A-Z][A-Z\s&]+(?:EXPRESS|FREIGHT|LOGISTICS|LINES|INC|LLC)?)",
                r"from[:\s]+([A-Z][A-Z\s&]+(?:EXPRESS|FREIGHT|LOGISTICS|LINES|INC|LLC)?)",
                r"([A-Z][A-Z\s&]{10,}(?:EXPRESS|FREIGHT|LOGISTICS|LINES))",
            ],
            "invoice_number": [
                r"invoice\s*#?[:\s]*([A-Z0-9\-]+)",
                r"inv(?:oice)?\.?\s*#?[:\s]*([A-Z0-9\-]+)",
            ],
            "invoice_date": [
                r"invoice\s*date[:\s]+([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{2,4})",
                r"date[:\s]+([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{2,4})",
                r"([\d]{1,2}[\/\-][\d]{1,2}[\/\-][\d]{4})",
            ],
            "total_charge": [
                r"total[:\s]+\$?\s*([\d,]+\.?\d{0,2})",
                r"amount\s*due[:\s]+\$?\s*([\d,]+\.?\d{0,2})",
                r"balance[:\s]+\$?\s*([\d,]+\.?\d{0,2})",
            ],
            "shipment_reference": [
                r"pro\s*#?[:\s]*([A-Z0-9\-]+)",
                r"ref(?:erence)?[:\s]*([A-Z0-9\-]+)",
                r"shipment[:\s]*([A-Z0-9\-]+)",
            ],
        }

    def process_invoice(self, pdf_file_path: str) -> dict[str, Any]:
        """
        Main entry point for processing an invoice PDF.

        Args:
            pdf_file_path: Path to the PDF invoice file

        Returns:
            Dictionary containing extracted fields
        """
        logger.info(f"Processing invoice: {pdf_file_path}")

        # Step 1: Try direct text extraction
        text = self._extract_text_direct(pdf_file_path)

        # Step 2: Check text quality; use OCR if needed
        if self._is_text_quality_poor(text):
            logger.info("Poor text quality detected, falling back to OCR")
            text = self._extract_text_ocr(pdf_file_path)

        # Step 3: Extract structured fields
        extracted_data = self._extract_fields(text)

        logger.info(f"Extraction complete: {extracted_data}")
        return extracted_data

    def _extract_text_direct(self, pdf_path: str) -> str:
        """Extract text directly from PDF using PyMuPDF."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Direct text extraction failed: {e}")
            return ""

    def _is_text_quality_poor(self, text: str) -> bool:
        """
        Heuristic to determine if extracted text quality is poor.
        Checks for minimum length and alphanumeric content.
        """
        if len(text.strip()) < 50:
            return True

        alphanumeric_count = sum(c.isalnum() for c in text)
        if len(text) > 0 and (alphanumeric_count / len(text)) < 0.3:
            return True

        return False

    def _extract_text_ocr(self, pdf_path: str) -> str:
        """
        Extract text using OCR on PDF converted to images.
        Applies preprocessing for better OCR accuracy.
        """
        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path, dpi=300)

            text = ""
            for i, image in enumerate(images):
                logger.info(f"Processing page {i + 1} with OCR")

                # Preprocess image for better OCR
                processed_image = self._preprocess_image(image)

                # Perform OCR
                page_text = pytesseract.image_to_string(processed_image)
                text += page_text + "\n"

            return text
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy.
        Applies grayscale, thresholding, and noise reduction.
        """
        # Convert PIL Image to OpenCV format
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

        # Convert back to PIL Image
        return Image.fromarray(denoised)

    def _extract_fields(self, text: str) -> dict[str, Any]:
        """
        Extract structured fields from raw text using regex patterns.
        """
        extracted: dict[str, Any] = {}

        for field_name, patterns in self.field_patterns.items():
            value = None
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    break

            if field_name == "total_charge" and value:
                # Clean and convert to float
                value = value.replace(",", "")
                try:
                    value = float(value)
                except ValueError:
                    value = None

            elif field_name == "invoice_date" and value:
                # Normalize date format
                value = self._normalize_date(value)

            elif field_name == "carrier_name" and value:
                # Clean up carrier name
                value = " ".join(value.split()).upper()

            extracted[field_name] = value

        return extracted

    def _normalize_date(self, date_str: str) -> str | None:
        """
        Normalize date string to YYYY-MM-DD format.
        """
        date_formats = [
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%m/%d/%y",
            "%m-%d-%y",
            "%d/%m/%Y",
            "%d-%m-%Y",
        ]

        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return date_str
