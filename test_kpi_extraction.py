"""Test KPI extraction from sample PDFs."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import directly to avoid relative import issues
import pdfplumber
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

# Copy the PDFExtractor class here for testing
class PDFExtractorTest:
    """Test version of PDFExtractor."""

    # Fields in the exact ORDER they appear in Looker Studio SEO reports
    SEO_KPI_FIELDS = [
        'Sessions',
        'Active users',
        'New users',
        'Key events',
        'Engagement rate',
        'Bounce rate',
        'Average session duration'
    ]

    # Fields in the exact ORDER they appear in Looker Studio Google Ads reports
    GOOGLE_ADS_KPI_FIELDS = [
        'Clicks',
        'Impressions',
        'CTR',
        'Conversions',
        'Conv. rate',  # Looker Studio abbreviates this
        'Avg. CPC',
        'Cost'
    ]

    def extract_report_data(self, pdf_path: str) -> Dict:
        """Extract all data from a PDF report."""
        pdf_path = Path(pdf_path)
        print(f"Extracting data from: {pdf_path.name}")

        result = {
            'business_name': None,
            'report_date': None,
            'report_month': None,
            'report_type': None,
            'kpis': {},
            'extraction_errors': [],
            'pdf_filename': pdf_path.name
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text()

                # Detect report type
                result['report_type'] = self._detect_report_type(text)

                # Extract business name
                result['business_name'] = self._extract_business_name(text)

                # Extract date/month
                result['report_date'], result['report_month'] = self._extract_date(text)

                # Extract KPIs
                expected_fields = (self.SEO_KPI_FIELDS if result['report_type'] == 'SEO'
                                 else self.GOOGLE_ADS_KPI_FIELDS)
                tables = first_page.extract_tables()
                result['kpis'] = self._extract_kpis_from_text(text, expected_fields)

                # Check for missing data
                if not result['business_name']:
                    result['extraction_errors'].append("Could not extract business name")
                if not result['report_month']:
                    result['extraction_errors'].append("Could not extract report date/month")
                if not result['report_type']:
                    result['extraction_errors'].append("Could not detect report type")

                missing_kpis = [k for k in expected_fields if k not in result['kpis']]
                if missing_kpis:
                    result['extraction_errors'].append(f"Missing KPIs: {', '.join(missing_kpis)}")

        except Exception as e:
            error_msg = f"Failed to extract data: {str(e)}"
            result['extraction_errors'].append(error_msg)

        return result

    def _detect_report_type(self, text: str) -> Optional[str]:
        """Detect whether this is an SEO or Google Ads report."""
        text_lower = text.lower()
        google_ads_keywords = ['google ads', 'cpc', 'clicks', 'impressions', 'ctr', 'cost per click']
        seo_keywords = ['seo report', 'bounce rate', 'engagement rate', 'active users', 'key events']

        google_ads_score = sum(1 for keyword in google_ads_keywords if keyword in text_lower)
        seo_score = sum(1 for keyword in seo_keywords if keyword in text_lower)

        if google_ads_score > seo_score:
            return 'Google Ads'
        elif seo_score > google_ads_score:
            return 'SEO'
        return 'SEO'

    def _extract_business_name(self, text: str) -> Optional[str]:
        """Extract business name from PDF text."""
        patterns = [
            r'(?:SEO Report for|Report for|Google Ads for)\s+([A-Z][A-Za-z0-9\s&,.\'-]+?)(?:\s+[A-Z][a-z]{2}\s+\d|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                business_name = match.group(1).strip()
                business_name = re.sub(r'\s+', ' ', business_name)
                if len(business_name) > 3:
                    return business_name

        # Fallback
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            first_line = lines[0]
            if not re.match(r'^\d|^Page\s+\d|^Report|^Date:', first_line):
                return first_line[:100]

        return None

    def _extract_date(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract report date and format month for subject line."""
        patterns = [
            r'([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\s*-\s*[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})',  # "Jul 1, 2025 - Sep 30, 2025"
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                date_range = match.group(1).strip()
                # Extract end date (second date in range)
                end_date_match = re.search(r'-\s*([A-Z][a-z]{2})\s+\d{1,2},\s+(\d{4})', date_range)
                if end_date_match:
                    month_abbr = end_date_match.group(1)
                    year = end_date_match.group(2)
                    # Convert month abbreviation to full month name
                    month_map = {'Jan': 'January', 'Feb': 'February', 'Mar': 'March', 'Apr': 'April',
                                'May': 'May', 'Jun': 'June', 'Jul': 'July', 'Aug': 'August',
                                'Sep': 'September', 'Oct': 'October', 'Nov': 'November', 'Dec': 'December'}
                    month_name = month_map.get(month_abbr, month_abbr)
                    return date_range, f"{month_name} {year}"

        return None, None

    def _extract_kpis_from_text(self, text: str, expected_fields: list) -> Dict:
        """Extract KPIs using Looker Studio format."""
        kpis = {}
        lines = text.split('\n')

        best_match = None
        best_match_count = 0

        # Find the line with the MOST matching fields (not just >= 3)
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
        """Parse Looker Studio's three-line KPI format."""
        kpis = {}

        # Extract values - handle time format, percentages, currency, and regular numbers
        values = re.findall(r'[0-9]{2}:[0-9]{2}:[0-9]{2}|[$][0-9,]+\.?[0-9]*|[0-9,]+\.?[0-9]*%?', values_line)
        # Extract changes - handle percentages and N/A
        changes = re.findall(r'-?[0-9]+\.?[0-9]*%|N/A', changes_line)

        header_lower = header_line.lower()
        field_positions = []

        for field in expected_fields:
            field_lower = field.lower()
            if field_lower in header_lower:
                pos = header_lower.find(field_lower)
                field_positions.append((pos, field))

        field_positions.sort()

        for idx, (pos, field) in enumerate(field_positions):
            if idx < len(values):
                value = values[idx]
                change = changes[idx] if idx < len(changes) else None
                kpis[field] = {'value': value, 'change': change}

        return kpis


# Test extraction
extractor = PDFExtractorTest()

print("="*80)
print("TESTING SEO PDF EXTRACTION")
print("="*80)
seo_data = extractor.extract_report_data('tgc_seo.pdf')

print(f"\nBusiness Name: {seo_data['business_name']}")
print(f"Report Date: {seo_data['report_date']}")
print(f"Report Month: {seo_data['report_month']}")
print(f"Report Type: {seo_data['report_type']}")
print(f"\nExtraction Errors: {seo_data['extraction_errors']}")
print(f"\nKPIs Extracted:")
for kpi, data in seo_data['kpis'].items():
    if isinstance(data, dict):
        print(f"  {kpi}: {data.get('value', 'N/A')} (Change: {data.get('change', 'N/A')})")
    else:
        print(f"  {kpi}: {data}")

print("\n" + "="*80)
print("TESTING GOOGLE ADS PDF EXTRACTION")
print("="*80)
ads_data = extractor.extract_report_data('tgc_google_ads.pdf')

print(f"\nBusiness Name: {ads_data['business_name']}")
print(f"Report Date: {ads_data['report_date']}")
print(f"Report Month: {ads_data['report_month']}")
print(f"Report Type: {ads_data['report_type']}")
print(f"\nExtraction Errors: {ads_data['extraction_errors']}")
print(f"\nKPIs Extracted:")
for kpi, data in ads_data['kpis'].items():
    if isinstance(data, dict):
        print(f"  {kpi}: {data.get('value', 'N/A')} (Change: {data.get('change', 'N/A')})")
    else:
        print(f"  {kpi}: {data}")
