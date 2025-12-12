"""
Utility script to create sample freight invoice PDFs for testing.
Run this script to generate test invoice PDFs.
"""

import fitz  # PyMuPDF
from pathlib import Path


def create_sample_invoice(output_path: str = "sample_invoice.pdf") -> None:
    """
    Create a sample freight invoice PDF for testing.
    """
    # Create a new PDF document
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)  # Letter size

    # Define invoice content
    content = [
        ("FREIGHT INVOICE", 50, 50, 18, "bold"),
        ("", 50, 80, 12, "normal"),
        ("ROADWAY EXPRESS INC", 50, 100, 14, "bold"),
        ("1234 Transport Way", 50, 120, 10, "normal"),
        ("Chicago, IL 60601", 50, 135, 10, "normal"),
        ("", 50, 160, 12, "normal"),
        ("Invoice Number: INV-2024-12345", 50, 180, 12, "normal"),
        ("Invoice Date: 03/15/2024", 50, 200, 12, "normal"),
        ("PRO Number: PRO-98765", 50, 220, 12, "normal"),
        ("", 50, 250, 12, "normal"),
        ("SHIPMENT DETAILS", 50, 270, 14, "bold"),
        ("", 50, 290, 12, "normal"),
        ("Origin: Chicago, IL", 50, 310, 10, "normal"),
        ("Destination: Denver, CO", 50, 330, 10, "normal"),
        ("Distance: 450 miles", 50, 350, 10, "normal"),
        ("", 50, 380, 12, "normal"),
        ("CHARGES", 50, 400, 14, "bold"),
        ("", 50, 420, 12, "normal"),
        ("Line Haul: $1,350.00", 50, 440, 10, "normal"),
        ("Fuel Surcharge: $225.00", 50, 460, 10, "normal"),
        ("", 50, 490, 12, "normal"),
        ("TOTAL AMOUNT DUE: $1,575.00", 50, 510, 14, "bold"),
        ("", 50, 540, 12, "normal"),
        ("Payment Terms: Net 30", 50, 560, 10, "normal"),
        ("", 50, 590, 12, "normal"),
        ("Thank you for your business!", 50, 620, 10, "italic"),
    ]

    # Add content to the page
    for text, x, y, size, style in content:
        if style == "bold":
            fontname = "helv-bold"
        elif style == "italic":
            fontname = "helv-oblique"
        else:
            fontname = "helv"

        page.insert_text((x, y), text, fontsize=size, fontname=fontname)

    # Save the document
    doc.save(output_path)
    doc.close()

    print(f"Sample invoice created: {output_path}")


def create_overage_invoice(output_path: str = "sample_invoice_overage.pdf") -> None:
    """
    Create a sample invoice with rate overage for testing anomaly detection.
    """
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)

    content = [
        ("FREIGHT INVOICE", 50, 50, 18, "bold"),
        ("", 50, 80, 12, "normal"),
        ("ROADWAY EXPRESS", 50, 100, 14, "bold"),
        ("", 50, 140, 12, "normal"),
        ("Invoice Number: INV-2024-99999", 50, 160, 12, "normal"),
        ("Invoice Date: 03/15/2024", 50, 180, 12, "normal"),
        ("PRO Number: PRO-OVERCHARGE", 50, 200, 12, "normal"),
        ("", 50, 230, 12, "normal"),
        ("Distance: 450 miles", 50, 250, 10, "normal"),
        ("", 50, 280, 12, "normal"),
        ("TOTAL AMOUNT DUE: $1,857.50", 50, 310, 14, "bold"),
        ("", 50, 350, 12, "normal"),
        ("(This invoice contains a rate overage)", 50, 380, 10, "italic"),
        ("Expected rate: $3.50/mile", 50, 400, 10, "italic"),
        ("Actual rate: $4.13/mile", 50, 420, 10, "italic"),
    ]

    for text, x, y, size, style in content:
        if style == "bold":
            fontname = "helv-bold"
        elif style == "italic":
            fontname = "helv-oblique"
        else:
            fontname = "helv"

        page.insert_text((x, y), text, fontsize=size, fontname=fontname)

    doc.save(output_path)
    doc.close()

    print(f"Sample overage invoice created: {output_path}")


def create_carrier_mismatch_invoice(
    output_path: str = "sample_invoice_wrong_carrier.pdf",
) -> None:
    """
    Create a sample invoice with wrong carrier for testing anomaly detection.
    """
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)

    content = [
        ("FREIGHT INVOICE", 50, 50, 18, "bold"),
        ("", 50, 80, 12, "normal"),
        ("FEDEX FREIGHT", 50, 100, 14, "bold"),
        ("", 50, 140, 12, "normal"),
        ("Invoice Number: INV-2024-88888", 50, 160, 12, "normal"),
        ("Invoice Date: 03/15/2024", 50, 180, 12, "normal"),
        ("PRO Number: PRO-WRONGCARRIER", 50, 200, 12, "normal"),
        ("", 50, 230, 12, "normal"),
        ("Distance: 450 miles", 50, 250, 10, "normal"),
        ("", 50, 280, 12, "normal"),
        ("TOTAL AMOUNT DUE: $1,500.00", 50, 310, 14, "bold"),
        ("", 50, 350, 12, "normal"),
        ("(This invoice has a carrier mismatch)", 50, 380, 10, "italic"),
        ("Expected: ROADWAY EXPRESS", 50, 400, 10, "italic"),
    ]

    for text, x, y, size, style in content:
        if style == "bold":
            fontname = "helv-bold"
        elif style == "italic":
            fontname = "helv-oblique"
        else:
            fontname = "helv"

        page.insert_text((x, y), text, fontsize=size, fontname=fontname)

    doc.save(output_path)
    doc.close()

    print(f"Sample carrier mismatch invoice created: {output_path}")


if __name__ == "__main__":
    # Create sample invoices
    create_sample_invoice()
    create_overage_invoice()
    create_carrier_mismatch_invoice()

    print("\nSample invoices created successfully!")
    print("\nYou can test them with:")
    print("  curl -X POST http://localhost:8000/invoice/extract \\")
    print('    -F "file=@sample_invoice.pdf"')
