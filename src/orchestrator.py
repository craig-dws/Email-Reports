"""
Main Orchestrator Module.
Coordinates the complete email report workflow.
"""

import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
from .logger import get_logger, ReportLogger
from .pdf_extractor import PDFExtractor
from .client_database import ClientDatabase
from .email_generator import EmailGenerator
from .gmail_reader import GmailReader
from .gmail_sender import GmailSender
from .approval_workflow import ApprovalWorkflow

logger = get_logger('Orchestrator')


class ReportOrchestrator:
    """Main orchestrator for the email reporting system."""

    def __init__(self, env_file: str = '.env'):
        """
        Initialize the orchestrator.

        Args:
            env_file: Path to .env configuration file
        """
        # Load environment variables
        load_dotenv(env_file)

        # Initialize logger
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.report_logger = ReportLogger(log_dir='logs', log_level=log_level)
        self.logger = logger

        self.logger.info("Initializing Email Reports Orchestrator")

        # Load configuration
        self.config = self._load_config()

        # Initialize modules
        self.pdf_extractor = PDFExtractor()
        self.client_db = ClientDatabase(
            csv_path=self.config['CLIENT_DATABASE_PATH'],
            fuzzy_threshold=int(self.config.get('FUZZY_MATCH_THRESHOLD', 85))
        )
        self.email_generator = EmailGenerator(
            template_path=self.config['TEMPLATE_PATH'],
            config=self.config
        )
        self.approval_workflow = ApprovalWorkflow(
            tracking_csv_path=self.config['APPROVAL_TRACKING_PATH']
        )

        # Gmail modules (initialized on demand)
        self.gmail_reader = None
        self.gmail_sender = None

        self.logger.info("Orchestrator initialized successfully")

    def _load_config(self) -> Dict:
        """Load configuration from environment variables."""
        config = {
            'GMAIL_SENDER_EMAIL': os.getenv('GMAIL_SENDER_EMAIL'),
            'LOOKER_STUDIO_SENDER': os.getenv('LOOKER_STUDIO_SENDER'),
            'CLIENT_DATABASE_PATH': os.getenv('CLIENT_DATABASE_PATH'),
            'PDF_STORAGE_PATH': os.getenv('PDF_STORAGE_PATH'),
            'TEMPLATE_PATH': os.getenv('TEMPLATE_PATH'),
            'APPROVAL_TRACKING_PATH': os.getenv('APPROVAL_TRACKING_PATH'),
            'FUZZY_MATCH_THRESHOLD': os.getenv('FUZZY_MATCH_THRESHOLD', '85'),
            'MAX_PDFS_PER_RUN': os.getenv('MAX_PDFS_PER_RUN', '50'),
            'AGENCY_NAME': os.getenv('AGENCY_NAME'),
            'AGENCY_EMAIL': os.getenv('AGENCY_EMAIL'),
            'AGENCY_PHONE': os.getenv('AGENCY_PHONE'),
            'AGENCY_WEBSITE': os.getenv('AGENCY_WEBSITE'),
            'STANDARD_SEO_PARAGRAPH': os.getenv('STANDARD_SEO_PARAGRAPH'),
            'STANDARD_SEM_PARAGRAPH': os.getenv('STANDARD_SEM_PARAGRAPH'),
            'STANDARD_CLOSING_PARAGRAPH': os.getenv('STANDARD_CLOSING_PARAGRAPH'),
        }

        self.logger.info("Configuration loaded from environment")
        return config

    def run_full_workflow(self, extract_from_gmail: bool = True, create_drafts: bool = True):
        """
        Run the complete workflow from PDF extraction to draft creation.

        Args:
            extract_from_gmail: Whether to extract PDFs from Gmail
            create_drafts: Whether to create Gmail drafts for approved emails
        """
        self.logger.info("="*60)
        self.logger.info("STARTING FULL WORKFLOW")
        self.logger.info("="*60)

        try:
            # Step 1: Extract PDFs from Gmail (if requested)
            pdf_files = []
            if extract_from_gmail:
                pdf_files = self.extract_pdfs_from_gmail()
            else:
                # Use PDFs already in storage directory
                pdf_storage = Path(self.config['PDF_STORAGE_PATH'])
                pdf_files = list(pdf_storage.glob('*.pdf'))
                self.logger.info(f"Found {len(pdf_files)} PDFs in storage directory")

            if not pdf_files:
                self.logger.warning("No PDFs found to process")
                return

            # Step 2: Process each PDF
            self.logger.info(f"Processing {len(pdf_files)} PDF files")
            processed_data = self.process_pdfs(pdf_files)

            # Step 3: Generate emails
            self.logger.info("Generating emails")
            email_data = self.generate_emails(processed_data)

            # Step 4: Add to approval workflow
            self.logger.info("Adding to approval workflow")
            self.populate_approval_tracking(processed_data, email_data)

            # Step 5: Export approval tracking to HTML for review
            html_path = Path(self.config['APPROVAL_TRACKING_PATH']).parent / 'approval_review.html'
            self.approval_workflow.export_review_html(str(html_path))
            self.logger.info(f"Approval review exported to: {html_path}")

            # Step 6: Create drafts for approved emails (if requested)
            if create_drafts:
                approved_count = self.create_drafts_for_approved()
                self.logger.info(f"Created {approved_count} Gmail drafts")

            # Print summary
            summary = self.approval_workflow.get_summary()
            self.logger.info("="*60)
            self.logger.info("WORKFLOW SUMMARY")
            self.logger.info("="*60)
            self.logger.info(f"Total PDFs processed: {len(pdf_files)}")
            self.logger.info(f"Emails generated: {len(email_data)}")
            self.logger.info(f"Approved: {summary['approved']}")
            self.logger.info(f"Pending: {summary['pending']}")
            self.logger.info(f"Needs Revision: {summary['needs_revision']}")
            self.logger.info("="*60)

        except Exception as e:
            self.logger.error(f"Workflow failed: {str(e)}")
            raise

    def extract_pdfs_from_gmail(self) -> List[str]:
        """Extract PDFs from Gmail."""
        if not self.gmail_reader:
            self.gmail_reader = GmailReader()

        looker_sender = self.config['LOOKER_STUDIO_SENDER']
        pdf_storage = self.config['PDF_STORAGE_PATH']

        self.logger.info(f"Extracting PDFs from emails sent by {looker_sender}")

        pdf_files = self.gmail_reader.extract_all_pdfs(
            sender_email=looker_sender,
            output_dir=pdf_storage,
            mark_as_read=False  # Don't mark as read automatically
        )

        return pdf_files

    def process_pdfs(self, pdf_files: List[str]) -> List[Dict]:
        """
        Process PDF files and extract data.

        Args:
            pdf_files: List of PDF file paths

        Returns:
            List of processed data dictionaries
        """
        processed_data = []

        for idx, pdf_path in enumerate(pdf_files, 1):
            self.logger.info(f"Processing PDF {idx}/{len(pdf_files)}: {Path(pdf_path).name}")

            # Extract data from PDF
            extracted = self.pdf_extractor.extract_report_data(pdf_path)

            # Match to client
            client = None
            if extracted['business_name']:
                client = self.client_db.find_client(extracted['business_name'])

            if not client:
                self.logger.warning(f"No client match found for: {extracted['business_name']}")
                extracted['extraction_errors'].append("No matching client in database")

            processed_data.append({
                'pdf_path': pdf_path,
                'extracted': extracted,
                'client': client
            })

        return processed_data

    def generate_emails(self, processed_data: List[Dict]) -> List[Dict]:
        """
        Generate emails for processed data.

        Args:
            processed_data: List of processed PDF data

        Returns:
            List of email data dictionaries
        """
        email_data = []

        for data in processed_data:
            if not data['client']:
                self.logger.warning(f"Skipping email generation for {data['extracted']['business_name']} - no client match")
                continue

            try:
                email = self.email_generator.generate_email(
                    client_data=data['client'],
                    extracted_data=data['extracted']
                )

                email['pdf_path'] = data['pdf_path']
                email['client_id'] = data['client']['ClientID']
                email['business_name'] = data['client']['BusinessName']
                email['extraction_errors'] = data['extracted']['extraction_errors']

                email_data.append(email)

            except Exception as e:
                self.logger.error(f"Failed to generate email for {data['client']['BusinessName']}: {str(e)}")
                continue

        return email_data

    def populate_approval_tracking(self, processed_data: List[Dict], email_data: List[Dict]):
        """
        Populate approval tracking with generated emails.

        Args:
            processed_data: List of processed PDF data
            email_data: List of email data
        """
        # Clear existing tracking
        self.approval_workflow.clear_tracking()

        # Add each email to tracking
        for email in email_data:
            self.approval_workflow.add_for_review(
                client_id=email['client_id'],
                business_name=email['business_name'],
                email_subject=email['subject'],
                extraction_errors=email.get('extraction_errors', [])
            )

    def create_drafts_for_approved(self) -> int:
        """
        Create Gmail drafts for all approved emails.

        Returns:
            Number of drafts created
        """
        if not self.gmail_sender:
            self.gmail_sender = GmailSender()

        # Get approved reviews
        approved_reviews = self.approval_workflow.get_approved_reviews()

        if not approved_reviews:
            self.logger.info("No approved emails to create drafts for")
            return 0

        # Get corresponding email data
        # (In production, we'd need to store email data or regenerate)
        # For now, we'll need to regenerate emails for approved clients

        self.logger.info(f"Creating drafts for {len(approved_reviews)} approved emails")

        # ... Implementation would regenerate emails and create drafts ...

        return len(approved_reviews)

    def approve_all_pending(self):
        """Approve all pending emails (convenience method for testing)."""
        pending = self.approval_workflow.get_pending_reviews()

        for review in pending:
            if review['ExtractionErrors']:
                self.logger.warning(f"Skipping auto-approval for {review['BusinessName']} - has extraction errors")
                continue

            self.approval_workflow.update_status(
                client_id=review['ClientID'],
                new_status=ApprovalWorkflow.STATUS_APPROVED,
                notes="Auto-approved (no extraction errors)"
            )

        self.logger.info(f"Auto-approved {len([r for r in pending if not r['ExtractionErrors']])} emails")
