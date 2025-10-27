"""
Unit tests for Email Generator module.
"""

import os
import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.email_generator import EmailGenerator


class TestEmailGenerator(unittest.TestCase):
    """Test cases for EmailGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.template_path = project_root / "templates" / "email_template.html"

        self.config = {
            'AGENCY_NAME': 'Test Agency',
            'AGENCY_EMAIL': 'test@testagency.com',
            'AGENCY_PHONE': '(555) 123-4567',
            'AGENCY_WEBSITE': 'www.testagency.com',
            'STANDARD_SEO_PARAGRAPH': 'Your keyword rankings continue to improve across target search terms.',
            'STANDARD_SEM_PARAGRAPH': 'Your Google Ads campaigns continue to drive quality traffic and conversions.',
            'STANDARD_CLOSING_PARAGRAPH': 'Please review the attached PDF for your complete monthly report.'
        }

        self.generator = EmailGenerator(
            template_path=str(self.template_path),
            config=self.config
        )

    def test_initialization(self):
        """Test EmailGenerator initialization."""
        self.assertIsNotNone(self.generator)
        self.assertIsNotNone(self.generator.template)
        self.assertEqual(self.generator.config, self.config)

    def test_extract_first_name_single(self):
        """Test extracting single first name."""
        result = self.generator._extract_first_name("John")
        self.assertEqual(result, "John")

    def test_extract_first_name_with_ampersand(self):
        """Test extracting first name with ampersand separator."""
        result = self.generator._extract_first_name("John & Mary")
        self.assertEqual(result, "John")

    def test_extract_first_name_with_comma(self):
        """Test extracting first name with comma separator."""
        result = self.generator._extract_first_name("John, Mary, Bob")
        self.assertEqual(result, "John")

    def test_extract_first_name_empty(self):
        """Test extracting first name from empty string."""
        result = self.generator._extract_first_name("")
        self.assertEqual(result, "")

    def test_extract_first_name_whitespace(self):
        """Test extracting first name with extra whitespace."""
        result = self.generator._extract_first_name("  John  &  Mary  ")
        self.assertEqual(result, "John")

    def test_format_kpi_value_plain_number(self):
        """Test formatting plain numeric KPI value."""
        result = self.generator._format_kpi_value("Sessions", "22837")
        self.assertEqual(result, "22,837")

    def test_format_kpi_value_already_formatted(self):
        """Test formatting already formatted value with comma."""
        result = self.generator._format_kpi_value("Sessions", "22,837")
        self.assertEqual(result, "22,837")

    def test_format_kpi_value_percentage(self):
        """Test formatting percentage value."""
        result = self.generator._format_kpi_value("Engagement rate", "45.2%")
        self.assertEqual(result, "45.2%")

    def test_format_kpi_value_decimal_rate(self):
        """Test formatting decimal rate (should add %)."""
        result = self.generator._format_kpi_value("Bounce rate", "38.7")
        self.assertEqual(result, "38.7%")

    def test_format_kpi_value_currency(self):
        """Test formatting currency value."""
        result = self.generator._format_kpi_value("Avg. CPC", "$2.96")
        self.assertEqual(result, "$2.96")

    def test_format_kpi_value_decimal_cost(self):
        """Test formatting decimal cost (should add $)."""
        result = self.generator._format_kpi_value("Cost", "156.78")
        self.assertEqual(result, "$156.78")

    def test_format_kpi_value_time_format(self):
        """Test formatting time duration."""
        result = self.generator._format_kpi_value("Average session duration", "00:03:29")
        self.assertEqual(result, "00:03:29")

    def test_format_kpi_value_none(self):
        """Test formatting None value."""
        result = self.generator._format_kpi_value("Sessions", "None")
        self.assertEqual(result, "N/A")

    def test_format_kpi_value_empty(self):
        """Test formatting empty value."""
        result = self.generator._format_kpi_value("Sessions", "")
        self.assertEqual(result, "N/A")

    def test_format_kpis_dict_values(self):
        """Test formatting KPIs with dict values (from PDF extractor)."""
        kpis = {
            'Sessions': {'value': '22837', 'change': '11.8%'},
            'Engagement rate': {'value': '45.2%', 'change': '5.3%'},
            'Bounce rate': {'value': '38.7%', 'change': '-3.2%'}
        }

        result = self.generator._format_kpis(kpis, 'SEO')

        self.assertEqual(result['Sessions'], '22,837')
        self.assertEqual(result['Engagement rate'], '45.2%')
        self.assertEqual(result['Bounce rate'], '38.7%')

    def test_format_kpis_string_values(self):
        """Test formatting KPIs with string values."""
        kpis = {
            'Sessions': '22837',
            'Engagement rate': '45.2%',
            'Bounce rate': '38.7'
        }

        result = self.generator._format_kpis(kpis, 'SEO')

        self.assertEqual(result['Sessions'], '22,837')
        self.assertEqual(result['Engagement rate'], '45.2%')
        self.assertEqual(result['Bounce rate'], '38.7%')

    def test_html_to_text_simple(self):
        """Test HTML to text conversion."""
        html = "<p>This is a test.</p>"
        result = self.generator._html_to_text(html)
        self.assertEqual(result, "This is a test.")

    def test_html_to_text_multiple_paragraphs(self):
        """Test HTML to text with multiple paragraphs."""
        html = "<p>Paragraph 1.</p>\n\n<p>Paragraph 2.</p>"
        result = self.generator._html_to_text(html)
        self.assertIn("Paragraph 1", result)
        self.assertIn("Paragraph 2", result)

    def test_html_to_text_entities(self):
        """Test HTML entity conversion."""
        html = "<p>Test &amp; example</p>"
        result = self.generator._html_to_text(html)
        self.assertEqual(result, "Test & example")

    def test_generate_email_seo(self):
        """Test generating SEO email."""
        client_data = {
            'Client-Name': 'The George Centre',
            'Contact-Name': 'Caroline',
            'Contact-Email': 'caroline@example.com',
            'SEO-Introduction': '<p>Throughout the month we have been focusing upon on-page and off-page SEO.</p>',
            'Google-Ads-Introduction': ''
        }

        extracted_data = {
            'business_name': 'The George Centre',
            'report_month': 'September 2024',
            'report_type': 'SEO',
            'kpis': {
                'Sessions': {'value': '22837', 'change': '11.8%'},
                'Active users': {'value': '14350', 'change': '14.8%'},
                'New users': {'value': '13703', 'change': '15.3%'},
                'Key events': {'value': '157', 'change': '-17.9%'},
                'Engagement rate': {'value': '62.85%', 'change': '3.8%'},
                'Bounce rate': {'value': '37.15%', 'change': '-4.4%'},
                'Average session duration': {'value': '00:03:29', 'change': '2.1%'}
            }
        }

        result = self.generator.generate_email(client_data, extracted_data)

        # Verify result structure
        self.assertIn('subject', result)
        self.assertIn('html_body', result)
        self.assertIn('text_body', result)
        self.assertIn('recipient_email', result)
        self.assertIn('recipient_name', result)

        # Verify subject line
        self.assertEqual(result['subject'], 'Your September 2024 SEO Report')

        # Verify recipient info
        self.assertEqual(result['recipient_email'], 'caroline@example.com')
        self.assertEqual(result['recipient_name'], 'Caroline')

        # Verify HTML body contains key elements
        self.assertIn('Caroline', result['html_body'])
        self.assertIn('The George Centre', result['html_body'])
        self.assertIn('22,837', result['html_body'])  # Formatted sessions
        self.assertIn('SEO', result['html_body'])

        # Verify text body contains key elements
        self.assertIn('Caroline', result['text_body'])
        self.assertIn('The George Centre', result['text_body'])
        self.assertIn('22,837', result['text_body'])

    def test_generate_email_google_ads(self):
        """Test generating Google Ads email."""
        client_data = {
            'Client-Name': 'The George Centre',
            'Contact-Name': 'Caroline',
            'Contact-Email': 'caroline@example.com',
            'SEO-Introduction': '',
            'Google-Ads-Introduction': '<p>The following table shows some key KPI data for Google Ads ONLY.</p>'
        }

        extracted_data = {
            'business_name': 'The George Centre',
            'report_month': 'September 2024',
            'report_type': 'Google Ads',
            'kpis': {
                'Clicks': {'value': '1234', 'change': '15.2%'},
                'Impressions': {'value': '45678', 'change': '8.3%'},
                'CTR': {'value': '2.70%', 'change': '5.1%'},
                'Conversions': {'value': '89', 'change': '12.4%'},
                'Conv. rate': {'value': '7.21%', 'change': '3.2%'},
                'Avg. CPC': {'value': '$2.96', 'change': '-2.5%'},
                'Cost': {'value': '$3,652.64', 'change': '11.8%'}
            }
        }

        result = self.generator.generate_email(client_data, extracted_data)

        # Verify subject line
        self.assertEqual(result['subject'], 'Your September 2024 Google Ads Report')

        # Verify HTML body contains Google Ads specific content
        self.assertIn('Google Ads', result['html_body'])
        self.assertIn('1,234', result['html_body'])  # Formatted clicks
        self.assertIn('$2.96', result['html_body'])  # CPC

    def test_generate_email_multiple_contacts(self):
        """Test generating email with multiple contact names."""
        client_data = {
            'Client-Name': 'Test Company',
            'Contact-Name': 'John & Mary',
            'Contact-Email': 'contact@test.com',
            'SEO-Introduction': '<p>Test intro</p>',
            'Google-Ads-Introduction': ''
        }

        extracted_data = {
            'business_name': 'Test Company',
            'report_month': 'September 2024',
            'report_type': 'SEO',
            'kpis': {'Sessions': '1000'}
        }

        result = self.generator.generate_email(client_data, extracted_data)

        # Should use first name only
        self.assertEqual(result['recipient_name'], 'John')
        self.assertIn('Hi John', result['html_body'])
        self.assertIn('Hi John', result['text_body'])

    def test_generate_email_missing_personalized_text(self):
        """Test generating email without personalized text."""
        client_data = {
            'Client-Name': 'Test Company',
            'Contact-Name': 'John',
            'Contact-Email': 'john@test.com',
            'SEO-Introduction': '',  # Empty
            'Google-Ads-Introduction': ''
        }

        extracted_data = {
            'business_name': 'Test Company',
            'report_month': 'September 2024',
            'report_type': 'SEO',
            'kpis': {'Sessions': '1000'}
        }

        result = self.generator.generate_email(client_data, extracted_data)

        # Should still generate email successfully
        self.assertIn('subject', result)
        self.assertIn('html_body', result)
        self.assertIn('Test Company', result['html_body'])

    def test_preview_email(self):
        """Test email preview generation."""
        email_data = {
            'subject': 'Test Subject',
            'recipient_email': 'test@example.com',
            'html_body': '<p>Test email body</p>'
        }

        preview = self.generator.preview_email(email_data)

        # Verify preview contains expected elements
        self.assertIn('Test Subject', preview)
        self.assertIn('test@example.com', preview)
        self.assertIn('Test email body', preview)
        self.assertIn('<html>', preview)


class TestEmailGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.template_path = project_root / "templates" / "email_template.html"

        self.config = {
            'AGENCY_NAME': 'Test Agency',
            'AGENCY_EMAIL': 'test@testagency.com',
            'AGENCY_PHONE': '(555) 123-4567',
            'STANDARD_SEO_PARAGRAPH': 'SEO paragraph',
            'STANDARD_SEM_PARAGRAPH': 'SEM paragraph',
            'STANDARD_CLOSING_PARAGRAPH': 'Closing paragraph'
        }

        self.generator = EmailGenerator(
            template_path=str(self.template_path),
            config=self.config
        )

    def test_missing_kpis(self):
        """Test handling of missing KPIs."""
        client_data = {
            'Client-Name': 'Test Company',
            'Contact-Name': 'John',
            'Contact-Email': 'john@test.com',
            'SEO-Introduction': '<p>Test</p>',
            'Google-Ads-Introduction': ''
        }

        extracted_data = {
            'business_name': 'Test Company',
            'report_month': 'September 2024',
            'report_type': 'SEO',
            'kpis': {}  # Empty KPIs
        }

        result = self.generator.generate_email(client_data, extracted_data)

        # Should still generate email with empty KPI table
        self.assertIn('subject', result)
        self.assertIn('html_body', result)

    def test_special_characters_in_business_name(self):
        """Test handling business names with special characters."""
        client_data = {
            'Client-Name': 'Test & Associates, LLC',
            'Contact-Name': 'John',
            'Contact-Email': 'john@test.com',
            'SEO-Introduction': '<p>Test</p>',
            'Google-Ads-Introduction': ''
        }

        extracted_data = {
            'business_name': 'Test & Associates, LLC',
            'report_month': 'September 2024',
            'report_type': 'SEO',
            'kpis': {'Sessions': '1000'}
        }

        result = self.generator.generate_email(client_data, extracted_data)

        # Special characters should be properly escaped in HTML
        self.assertIn('Test &amp; Associates', result['html_body'])
        # But normal in text
        self.assertIn('Test & Associates', result['text_body'])


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEmailGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailGeneratorEdgeCases))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
