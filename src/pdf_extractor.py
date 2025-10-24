"""
PDF Extraction Module for Looker Studio Reports.
Extracts business name, date, and KPI metrics from PDF reports.
"""

import pdfplumber
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
from .logger import get_logger

logger = get_logger('PDFExtractor')


class PDFExtractor:
    """Extracts data from Looker Studio PDF reports."""

    # KPI field names to extract
    KPI_FIELDS = [
        'Sessions',
        'Conversions',
        'Active Users',
        'Engagement Rate',
        'Bounce Rate',
        'Average Session Duration'
    ]

    def __init__(self):
        """Initialize PDF extractor."""
        self.logger = logger

    def extract_report_data(self, pdf_path: str) -> Dict:
        """
        Extract all data from a PDF report.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing extracted data:
            {
                'business_name': str,
                'report_date': str,
                'report_month': str,
                'kpis': dict,
                'extraction_errors': list,
                'pdf_filename': str
            }
        """
        pdf_path = Path(pdf_path)
        self.logger.info(f"Extracting data from: {pdf_path.name}")

        result = {
            'business_name': None,
            'report_date': None,
            'report_month': None,
            'kpis': {},
            'extraction_errors': [],
            'pdf_filename': pdf_path.name
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract text from first page (usually contains header and KPIs)
                first_page = pdf.pages[0]
                text = first_page.extract_text()

                # Extract business name (typically in header)
                result['business_name'] = self._extract_business_name(text)

                # Extract date/month
                result['report_date'], result['report_month'] = self._extract_date(text)

                # Extract KPI table
                tables = first_page.extract_tables()
                result['kpis'] = self._extract_kpis(text, tables)

                # Check for missing data
                if not result['business_name']:
                    result['extraction_errors'].append("Could not extract business name")

                if not result['report_month']:
                    result['extraction_errors'].append("Could not extract report date/month")

                missing_kpis = [k for k in self.KPI_FIELDS if k not in result['kpis']]
                if missing_kpis:
                    result['extraction_errors'].append(
                        f"Missing KPIs: {', '.join(missing_kpis)}"
                    )

                if result['extraction_errors']:
                    self.logger.warning(
                        f"Extraction warnings for {pdf_path.name}: "
                        f"{'; '.join(result['extraction_errors'])}"
                    )
                else:
                    self.logger.info(f"Successfully extracted all data from {pdf_path.name}")

        except Exception as e:
            error_msg = f"Failed to extract data from {pdf_path.name}: {str(e)}"
            self.logger.error(error_msg)
            result['extraction_errors'].append(error_msg)

        return result

    def _extract_business_name(self, text: str) -> Optional[str]:
        """
        Extract business name from PDF text.
        Looks for company name patterns in the header.

        Args:
            text: PDF text content

        Returns:
            Business name or None
        """
        # Try multiple patterns for business name extraction
        patterns = [
            r'(?:Report for|Client:|Business:)\s*([A-Z][A-Za-z0-9\s&,.\'-]+?)(?:\n|$)',
            r'^([A-Z][A-Za-z0-9\s&,.\'-]{3,}?)(?:\s*-\s*(?:SEO|SEM|Google Ads)|\n)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                business_name = match.group(1).strip()
                # Clean up common artifacts
                business_name = re.sub(r'\s+', ' ', business_name)
                if len(business_name) > 3:  # Ensure it's not too short
                    return business_name

        # Fallback: Look at first non-empty line
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            first_line = lines[0]
            # Check if it looks like a business name (not a date or number)
            if not re.match(r'^\d|^Page\s+\d|^Report|^Date:', first_line):
                return first_line[:100]  # Limit length

        return None

    def _extract_date(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract report date and format month for subject line.

        Args:
            text: PDF text content

        Returns:
            Tuple of (full_date, month_year) e.g., ("2025-01-15", "January 2025")
        """
        # Date patterns
        patterns = [
            r'(?:Date|Period|Month):\s*(\w+\s+\d{4})',  # "January 2025"
            r'(\w+\s+\d{1,2},?\s+\d{4})',  # "January 15, 2025"
            r'(\d{1,2}/\d{1,2}/\d{4})',    # "01/15/2025"
            r'(\d{4}-\d{2}-\d{2})',        # "2025-01-15"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()

                # Try to parse and format
                try:
                    # Try different date formats
                    for fmt in ['%B %Y', '%B %d, %Y', '%m/%d/%Y', '%Y-%m-%d']:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            full_date = dt.strftime('%Y-%m-%d')
                            month_year = dt.strftime('%B %Y')
                            return full_date, month_year
                        except ValueError:
                            continue
                except Exception:
                    pass

        return None, None

    def _extract_kpis(self, text: str, tables: list) -> Dict[str, str]:
        """
        Extract KPI metrics from tables or text.

        Args:
            text: PDF text content
            tables: Extracted tables from pdfplumber

        Returns:
            Dictionary of KPI name -> value
        """
        kpis = {}

        # Try table extraction first (more reliable)
        if tables:
            kpis = self._extract_kpis_from_tables(tables)

        # If table extraction didn't get all KPIs, try text parsing
        if len(kpis) < len(self.KPI_FIELDS):
            text_kpis = self._extract_kpis_from_text(text)
            # Merge, preferring table data
            for key, value in text_kpis.items():
                if key not in kpis:
                    kpis[key] = value

        return kpis

    def _extract_kpis_from_tables(self, tables: list) -> Dict[str, str]:
        """Extract KPIs from table structures."""
        kpis = {}

        for table in tables:
            if not table:
                continue

            # Look for KPI names in first column, values in second
            for row in table:
                if not row or len(row) < 2:
                    continue

                metric_name = str(row[0]).strip() if row[0] else ""
                metric_value = str(row[1]).strip() if row[1] else ""

                # Check if this row contains a KPI we're looking for
                for kpi_field in self.KPI_FIELDS:
                    if kpi_field.lower() in metric_name.lower():
                        if metric_value and metric_value != 'None':
                            kpis[kpi_field] = metric_value
                        break

        return kpis

    def _extract_kpis_from_text(self, text: str) -> Dict[str, str]:
        """Extract KPIs using text pattern matching (fallback method)."""
        kpis = {}

        for kpi_field in self.KPI_FIELDS:
            # Create pattern for this KPI
            pattern = rf'{re.escape(kpi_field)}\s*:?\s*([0-9,]+\.?[0-9]*%?|[0-9]+m?\s*[0-9]+s?)'

            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                kpis[kpi_field] = match.group(1).strip()

        return kpis

    def validate_extraction(self, extracted_data: Dict) -> bool:
        """
        Validate that extraction was successful.

        Args:
            extracted_data: Extracted data dictionary

        Returns:
            True if extraction is valid, False otherwise
        """
        if not extracted_data['business_name']:
            return False

        if not extracted_data['report_month']:
            return False

        # Check that we have at least 4 out of 6 KPIs (some flexibility)
        if len(extracted_data['kpis']) < 4:
            return False

        return True
