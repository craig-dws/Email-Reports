"""Test script to extract data from sample PDF reports."""

import pdfplumber
from pathlib import Path

def extract_pdf_sample(pdf_path, report_type):
    """Extract and display text from PDF."""
    output = []
    output.append(f"\n{'='*80}")
    output.append(f"{report_type} REPORT: {Path(pdf_path).name}")
    output.append('='*80)

    with pdfplumber.open(pdf_path) as pdf:
        # Get first page
        first_page = pdf.pages[0]

        # Extract text
        text = first_page.extract_text()
        output.append("\n--- FULL TEXT (first 3000 chars) ---")
        output.append(text[:3000] if text else "No text found")

        # Extract tables
        tables = first_page.extract_tables()
        output.append(f"\n--- TABLES FOUND: {len(tables)} ---")

        for i, table in enumerate(tables):
            output.append(f"\n--- TABLE {i+1} ---")
            if table:
                for row in table[:15]:  # First 15 rows
                    output.append(str(row))

    return '\n'.join(output)

# Test both PDFs and save to file
with open('pdf_extraction_results.txt', 'w', encoding='utf-8') as f:
    f.write(extract_pdf_sample('tgc_seo.pdf', 'SEO'))
    f.write('\n\n')
    f.write(extract_pdf_sample('tgc_google_ads.pdf', 'GOOGLE ADS'))

print("Extraction complete! Results saved to pdf_extraction_results.txt")
