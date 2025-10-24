"""
Email Generator Module.
Creates HTML emails from templates and client data.
"""

import os
from pathlib import Path
from typing import Dict
from jinja2 import Environment, FileSystemLoader, Template
from premailer import transform
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

        # Load Jinja2 template
        template_dir = self.template_path.parent
        template_file = self.template_path.name

        env = Environment(loader=FileSystemLoader(str(template_dir)))
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
            client_data: Client information from database
            extracted_data: Extracted data from PDF (business name, KPIs, etc.)

        Returns:
            Dictionary with 'subject', 'html_body', 'text_body' keys
        """
        try:
            # Determine service type and standard paragraph
            service_type = client_data['ServiceType'].upper()
            if service_type == 'SEO':
                standard_paragraph = self.config.get(
                    'STANDARD_SEO_PARAGRAPH',
                    'Your keyword rankings continue to improve.'
                )
                report_type = 'SEO Report'
            else:  # SEM
                standard_paragraph = self.config.get(
                    'STANDARD_SEM_PARAGRAPH',
                    'Your Google Ads campaigns continue to drive quality traffic.'
                )
                report_type = 'Google Ads Report'

            # Generate subject line
            month_year = extracted_data.get('report_month', 'Monthly')
            subject = f"Your {month_year} {report_type}"

            # Prepare template context
            context = {
                'subject_line': subject,
                'first_name': client_data['FirstName'],
                'business_name': client_data['BusinessName'],
                'personalized_text': client_data.get('PersonalizedText', ''),
                'standard_paragraph': standard_paragraph,
                'kpis': extracted_data.get('kpis', {}),
                'closing_paragraph': self.config.get(
                    'STANDARD_CLOSING_PARAGRAPH',
                    'Please review the attached PDF for your complete monthly report.'
                ),
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
            text_body = self._generate_text_body(context)

            self.logger.info(
                f"Generated email for {client_data['BusinessName']} - "
                f"Subject: {subject}"
            )

            return {
                'subject': subject,
                'html_body': html_body,
                'text_body': text_body,
                'recipient_email': client_data['Email'],
                'recipient_name': client_data['FirstName']
            }

        except Exception as e:
            self.logger.error(
                f"Failed to generate email for {client_data.get('BusinessName', 'Unknown')}: "
                f"{str(e)}"
            )
            raise

    def _generate_text_body(self, context: Dict) -> str:
        """
        Generate plain text version of email.

        Args:
            context: Template context

        Returns:
            Plain text email body
        """
        text = f"Hi {context['first_name']},\n\n"
        text += f"Please see the data below for {context['business_name']}.\n\n"

        if context.get('personalized_text'):
            text += f"{context['personalized_text']}\n\n"

        text += f"{context['standard_paragraph']}\n\n"

        text += "KEY METRICS:\n"
        text += "-" * 40 + "\n"
        for kpi_name, kpi_value in context['kpis'].items():
            text += f"{kpi_name}: {kpi_value}\n"
        text += "-" * 40 + "\n\n"

        text += f"{context['closing_paragraph']}\n\n"

        text += "Best regards,\n"
        text += f"{context['agency_name']}\n"
        text += f"{context['agency_email']} | {context['agency_phone']}\n"
        if context.get('agency_website'):
            text += f"{context['agency_website']}\n"

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
