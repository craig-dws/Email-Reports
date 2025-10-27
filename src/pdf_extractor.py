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

    # KPI field names to extract for SEO reports (in ORDER they appear in Looker Studio)
    # Note: "Conversions" in Looker Studio SEO reports is called "Key events"
    SEO_KPI_FIELDS = [
        'Sessions',
        'Active users',
        'New users',
        'Key events',
        'Engagement rate',
        'Bounce rate',
        'Average session duration'
    ]

    # KPI field names to extract for Google Ads reports (in ORDER they appear in Looker Studio)
    GOOGLE_ADS_KPI_FIELDS = [
        'Clicks',
        'Impressions',
        'CTR',
        'Conversions',
        'Conv. rate',  # Looker Studio abbreviates "Conversion rate" as "Conv. rate"
        'Avg. CPC',    # Looker Studio abbreviates "Average CPC" as "Avg. CPC"
        'Cost'
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
                'report_type': str,  # 'SEO' or 'Google Ads'
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
            'report_type': None,  # Will be detected: 'SEO' or 'Google Ads'
            'kpis': {},
            'extraction_errors': [],
            'pdf_filename': pdf_path.name
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract text from first page (usually contains header and KPIs)
                first_page = pdf.pages[0]
                text = first_page.extract_text()

                # Detect report type (SEO or Google Ads)
                result['report_type'] = self._detect_report_type(text)

                # Extract business name (typically in header)
                result['business_name'] = self._extract_business_name(text)

                # Extract date/month
                result['report_date'], result['report_month'] = self._extract_date(text)

                # Extract KPI table (based on report type)
                tables = first_page.extract_tables()
                result['kpis'] = self._extract_kpis(text, tables, result['report_type'])

                # Check for missing data
                if not result['business_name']:
                    result['extraction_errors'].append("Could not extract business name")

                if not result['report_month']:
                    result['extraction_errors'].append("Could not extract report date/month")

                if not result['report_type']:
                    result['extraction_errors'].append("Could not detect report type (SEO or Google Ads)")

                # Check for missing KPIs based on report type
                expected_kpis = (self.SEO_KPI_FIELDS if result['report_type'] == 'SEO'
                               else self.GOOGLE_ADS_KPI_FIELDS)
                missing_kpis = [k for k in expected_kpis if k not in result['kpis']]
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

    def _detect_report_type(self, text: str) -> Optional[str]:
        """
        Detect whether this is an SEO or Google Ads report.

        Args:
            text: PDF text content

        Returns:
            'SEO' or 'Google Ads' or None
        """
        text_lower = text.lower()

        # Google Ads indicators
        google_ads_keywords = ['google ads', 'cpc', 'clicks', 'impressions', 'ctr', 'cost per click']
        seo_keywords = ['organic search', 'bounce rate', 'engagement rate', 'active users', 'keyword rankings']

        google_ads_score = sum(1 for keyword in google_ads_keywords if keyword in text_lower)
        seo_score = sum(1 for keyword in seo_keywords if keyword in text_lower)

        # Determine type based on keyword scores
        if google_ads_score > seo_score:
            return 'Google Ads'
        elif seo_score > google_ads_score:
            return 'SEO'

        # Fallback: check filename if available
        # (this would need to be passed in, so for now just return SEO as default)
        return 'SEO'

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

    def _extract_kpis(self, text: str, tables: list, report_type: str) -> Dict[str, str]:
        """
        Extract KPI metrics from tables or text.

        Args:
            text: PDF text content
            tables: Extracted tables from pdfplumber
            report_type: 'SEO' or 'Google Ads'

        Returns:
            Dictionary of KPI name -> value
        """
        kpis = {}

        # Get expected KPI fields based on report type
        expected_fields = (self.SEO_KPI_FIELDS if report_type == 'SEO'
                         else self.GOOGLE_ADS_KPI_FIELDS)

        # Try table extraction first (more reliable)
        if tables:
            kpis = self._extract_kpis_from_tables(tables, expected_fields)

        # If table extraction didn't get all KPIs, try text parsing
        if len(kpis) < len(expected_fields):
            text_kpis = self._extract_kpis_from_text(text, expected_fields)
            # Merge, preferring table data
            for key, value in text_kpis.items():
                if key not in kpis:
                    kpis[key] = value

        return kpis

    def _extract_kpis_from_tables(self, tables: list, expected_fields: list) -> Dict[str, str]:
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
                for kpi_field in expected_fields:
                    if kpi_field.lower() in metric_name.lower():
                        if metric_value and metric_value != 'None':
                            kpis[kpi_field] = metric_value
                        break

        return kpis

    def _extract_kpis_from_text(self, text: str, expected_fields: list) -> Dict[str, str]:
        """
        Extract KPIs using text pattern matching for Looker Studio format.
        Looker Studio PDFs have a specific format:
        Line 1: Metric names (e.g., "Sessions Active users New users...")
        Line 2: Values (e.g., "22,837 14,350 13,703...")
        Line 3: Changes (e.g., "11.8% 14.8% 15.3%...")
        """
        kpis = {}
        lines = text.split('\n')

        best_match = None
        best_match_count = 0

        # Find the line with the MOST matching fields (not just >= 3)
        # This handles cases where multiple lines contain some fields
        for i, line in enumerate(lines):
            fields_found = [field for field in expected_fields if field.lower() in line.lower()]

            if len(fields_found) > best_match_count and i + 2 < len(lines):
                best_match = i
                best_match_count = len(fields_found)

        # Extract from the best match
        if best_match is not None and best_match_count >= 3:
            i = best_match
            header_line = lines[i]
            values_line = lines[i + 1].strip()
            changes_line = lines[i + 2].strip()
            kpis = self._parse_looker_studio_kpis(
                header_line, values_line, changes_line, expected_fields
            )

        return kpis

    def _parse_looker_studio_kpis(self, header_line: str, values_line: str,
                                   changes_line: str, expected_fields: list) -> Dict:
        """
        Parse Looker Studio's three-line KPI format.
        Returns dict with structure: {metric_name: {'value': '22,837', 'change': '11.8%'}}
        """
        kpis = {}

        # Extract values - handle time format (00:03:29), currency ($2.96), percentages (5.12%), and numbers (22,837)
        # Order matters: check time format first, then currency, then regular numbers/percentages
        values = re.findall(r'[0-9]{2}:[0-9]{2}:[0-9]{2}|[$][0-9,]+\.?[0-9]*|[0-9,]+\.?[0-9]*%?', values_line)

        # Extract changes - handle percentages and N/A
        changes = re.findall(r'-?[0-9]+\.?[0-9]*%|N/A', changes_line)

        # Map expected fields to their positions in the header
        header_lower = header_line.lower()
        field_positions = []

        for field in expected_fields:
            field_lower = field.lower()
            if field_lower in header_lower:
                # Find approximate position
                pos = header_lower.find(field_lower)
                field_positions.append((pos, field))

        # Sort by position (left to right in header)
        field_positions.sort()

        # Map values and changes to fields based on position
        for idx, (pos, field) in enumerate(field_positions):
            if idx < len(values):
                value = values[idx]
                change = changes[idx] if idx < len(changes) else None
                kpis[field] = {'value': value, 'change': change}

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
