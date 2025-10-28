"""
Email Generator Module.
Creates HTML emails from templates and client data.
"""

import os
import re
from pathlib import Path
from typing import Dict
from jinja2 import Environment, FileSystemLoader, Template
from premailer import transform
from markupsafe import Markup
from .logger import get_logger

logger = get_logger('EmailGenerator')


class EmailGenerator:
    """Generates personalized HTML emails from templates."""

    def __init__(self, template_path: str, config: Dict):
        """
        Initialize email generator.

        Args:
            template_path: Path to email template HTML file
            config: Configuration dictionary with agency info and standard text
        """
        self.template_path = Path(template_path)
        self.config = config
        self.logger = logger

        # Load Jinja2 template with autoescape enabled
        template_dir = self.template_path.parent
        template_file = self.template_path.name

        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True  # Enable autoescaping for security
        )
        self.template = env.get_template(template_file)

        self.logger.info(f"Email template loaded from: {template_path}")

    def generate_email(
        self,
        client_data: Dict,
        extracted_data: Dict
    ) -> Dict[str, str]:
        """
        Generate personalized email for a client.

        Args:
            client_data: Client information from database (with CSV field names)
            extracted_data: Extracted data from PDF (business name, KPIs, etc.)

        Returns:
            Dictionary with 'subject', 'html_body', 'text_body' keys
        """
        try:
            # Get client info using CSV field names
            client_name = client_data.get('Client-Name', '').strip()
            contact_name = client_data.get('Contact-Name', '').strip()
            contact_email = client_data.get('Contact-Email', '').strip()

            # Extract first name from Contact-Name (may contain multiple names separated by &)
            first_name = self._extract_first_name(contact_name)

            # Determine report type from extracted data
            report_type = extracted_data.get('report_type', 'SEO')

            # Get appropriate personalized intro and standard paragraph
            if report_type == 'Google Ads':
                personalized_intro = client_data.get('Google-Ads-Introduction', '').strip()
                standard_paragraph = self.config.get(
                    'STANDARD_SEM_PARAGRAPH',
                    'Your Google Ads campaigns continue to drive quality traffic and conversions.'
                )
                service_label = 'Google Ads Report'
            else:  # SEO
                personalized_intro = client_data.get('SEO-Introduction', '').strip()
                standard_paragraph = self.config.get(
                    'STANDARD_SEO_PARAGRAPH',
                    'Your keyword rankings continue to improve across target search terms.'
                )
                service_label = 'SEO Report'

            # Generate subject line
            month_year = extracted_data.get('report_month', 'Monthly')
            subject = f"Your {month_year} {service_label}"

            # Format KPIs for display
            formatted_kpis = self._format_kpis(
                extracted_data.get('kpis', {}),
                report_type
            )

            # Prepare template context
            context = {
                'subject_line': subject,
                'first_name': first_name,
                'business_name': client_name,
                'report_type': report_type,  # 'SEO' or 'Google Ads'
                # Mark personalized_intro as safe HTML (it contains <p> tags from CSV)
                'personalized_text': Markup(personalized_intro) if personalized_intro else '',
                'kpis': formatted_kpis,
                'agency_name': self.config.get('AGENCY_NAME', ''),
                'agency_email': self.config.get('AGENCY_EMAIL', ''),
                'agency_phone': self.config.get('AGENCY_PHONE', ''),
                'agency_website': self.config.get('AGENCY_WEBSITE', ''),
            }

            # Render HTML
            html_body = self.template.render(context)

            # Inline CSS for email client compatibility
            html_body = transform(html_body)

            # Generate plain text version (simple fallback)
            text_body = self._generate_text_body(context, formatted_kpis)

            self.logger.info(
                f"Generated email for {client_name} - Subject: {subject}"
            )

            return {
                'subject': subject,
                'html_body': html_body,
                'text_body': text_body,
                'recipient_email': contact_email,
                'recipient_name': first_name,
                'business_name': client_name
            }

        except Exception as e:
            business_name = client_data.get('Client-Name', 'Unknown')
            self.logger.error(
                f"Failed to generate email for {business_name}: {str(e)}"
            )
            raise

    def _extract_first_name(self, contact_name: str) -> str:
        """
        Extract first name from contact name field.
        Handles cases like "John & Mary" or "John" or "John, Mary, Bob".

        Args:
            contact_name: Contact name string

        Returns:
            First name only
        """
        if not contact_name:
            return ""

        # Remove extra whitespace
        contact_name = contact_name.strip()

        # Split by & or comma
        names = re.split(r'[&,]', contact_name)

        if names:
            # Get first name and clean it
            first_name = names[0].strip()
            return first_name

        return contact_name

    def _format_kpis(self, kpis: Dict, report_type: str) -> list:
        """
        Format KPI values for display in email with color coding based on change.

        Args:
            kpis: Dictionary of KPI name -> data dict with 'value' and 'change' keys
            report_type: 'SEO' or 'Google Ads'

        Returns:
            List of dicts with 'name', 'value', 'color' keys
        """
        formatted = []

        for kpi_name, kpi_data in kpis.items():
            # Extract value and change
            if isinstance(kpi_data, dict):
                value = kpi_data.get('value', '')
                change = kpi_data.get('change', '')
            else:
                value = kpi_data
                change = ''

            # Format value
            formatted_value = self._format_kpi_value(kpi_name, value)

            # Format change (keep as-is, just ensure it has % sign)
            formatted_change = str(change) if change else 'N/A'
            if formatted_change != 'N/A' and '%' not in formatted_change:
                formatted_change = f"{formatted_change}%"

            # Determine color based on change percentage
            color = self._get_kpi_color(kpi_name, change)

            formatted.append({
                'name': kpi_name,
                'value': formatted_value,
                'change': formatted_change,
                'color': color
            })

        return formatted

    def _get_kpi_color(self, kpi_name: str, change: str) -> str:
        """
        Determine the color for a KPI value based on its change percentage.

        Args:
            kpi_name: Name of the KPI
            change: Change percentage (e.g., '11.8%', '-5.2%')

        Returns:
            Color code: '#27ae60' (green), '#e74c3c' (red), or '#333333' (black)
        """
        if not change or change == 'N/A':
            return '#333333'  # Black for no change data

        # Parse change percentage
        try:
            # Remove % sign and convert to float
            change_str = str(change).replace('%', '').strip()
            change_value = float(change_str)
        except (ValueError, AttributeError):
            return '#333333'  # Black if can't parse

        # For Bounce Rate, inverse the color logic (lower is better)
        if 'bounce' in kpi_name.lower():
            if change_value < 0:
                return '#27ae60'  # Green for decrease
            elif change_value > 0:
                return '#e74c3c'  # Red for increase
            else:
                return '#333333'  # Black for no change
        else:
            # For all other metrics, higher is better
            if change_value > 0:
                return '#27ae60'  # Green for increase
            elif change_value < 0:
                return '#e74c3c'  # Red for decrease
            else:
                return '#333333'  # Black for no change

    def _format_kpi_value(self, kpi_name: str, value: str) -> str:
        """
        Format a single KPI value based on its type.

        Args:
            kpi_name: Name of the KPI
            value: Raw value string

        Returns:
            Formatted value string
        """
        if not value or value == 'None':
            return 'N/A'

        value = str(value).strip()

        # Already formatted values (with currency, percentage, time format)
        if any(char in value for char in ['$', '%', ':']):
            return value

        # For numeric values, add thousands separators if not already present
        # Check if it's a plain number
        if re.match(r'^\d+$', value):
            try:
                num = int(value)
                return f"{num:,}"
            except ValueError:
                return value

        # Decimal numbers (without percentage)
        if re.match(r'^\d+\.\d+$', value):
            # Could be engagement rate, bounce rate (should be %)
            # Or could be cost (should be $)
            if 'rate' in kpi_name.lower():
                return f"{value}%"
            elif 'cpc' in kpi_name.lower() or 'cost' in kpi_name.lower():
                return f"${value}"
            else:
                return value

        return value

    def _generate_text_body(self, context: Dict, formatted_kpis: list) -> str:
        """
        Generate plain text version of email.

        Args:
            context: Template context
            formatted_kpis: List of formatted KPI dicts

        Returns:
            Plain text email body
        """
        text = f"Hi {context['first_name']},\n\n"

        # Opening line (different for SEO vs Google Ads)
        report_type = context.get('report_type', 'SEO')
        if report_type == 'Google Ads':
            text += f"Please see attached report for the {context['business_name']} Google Ads Campaign.\n\n"
        else:
            text += f"Please see the data below for {context['business_name']}.\n\n"

        # Convert HTML personalized text to plain text
        if context.get('personalized_text'):
            personalized_plain = self._html_to_text(str(context['personalized_text']))
            text += f"{personalized_plain}\n\n"

        # Traffic type description
        if report_type == 'SEO':
            text += "The following shows some key KPI data for Organic Search Traffic ONLY. These KPIs will help to track visitor traffic resulting from SEO activities.\n\n"
        else:
            text += "The following table shows some key KPI data for Google Ads ONLY. These KPIs will help to track visitor traffic resulting from Google Ads activities.\n\n"

        text += "KEY METRICS:\n"
        text += "-" * 60 + "\n"
        # Header row
        text += f"{'Metric':<30} {'Value':>12} {'Change':>12}\n"
        text += "-" * 60 + "\n"
        for kpi in formatted_kpis:
            text += f"{kpi['name']:<30} {kpi['value']:>12} {kpi['change']:>12}\n"
        text += "-" * 60 + "\n\n"

        text += "Either myself or Mitch would be happy to take you through the reports via Phone or Zoom session if you would like. Please let us know, and this can be arranged.\n\n"

        text += "Thanks,\n"

        return text

    def _html_to_text(self, html: str) -> str:
        """
        Convert HTML to plain text by removing tags.

        Args:
            html: HTML string

        Returns:
            Plain text string
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        return text

    def preview_email(self, email_data: Dict) -> str:
        """
        Generate a preview of the email for review.

        Args:
            email_data: Email data dictionary

        Returns:
            HTML preview string
        """
        preview = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .preview-header {{ background: #f4f4f4; padding: 15px; margin-bottom: 20px; }}
                .email-content {{ border: 2px solid #ddd; padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="preview-header">
                <h2>Email Preview</h2>
                <p><strong>To:</strong> {email_data['recipient_email']}</p>
                <p><strong>Subject:</strong> {email_data['subject']}</p>
            </div>
            <div class="email-content">
                {email_data['html_body']}
            </div>
        </body>
        </html>
        """
        return preview
