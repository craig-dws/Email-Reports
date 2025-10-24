"""
Gmail Sender Module.
Creates Gmail drafts with HTML content and PDF attachments.
"""

import os
import base64
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from .logger import get_logger

logger = get_logger('GmailSender')


class GmailSender:
    """Creates Gmail drafts with attachments."""

    # Gmail API scopes (requires compose permission)
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Initialize Gmail sender.

        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to store/load token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.logger = logger

        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth 2.0."""
        creds = None

        # Check if token exists
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
                self.logger.info("Loaded existing Gmail credentials")
            except Exception as e:
                self.logger.warning(f"Failed to load existing credentials: {e}")

        # If credentials are invalid or don't exist, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("Refreshed Gmail credentials")
                except Exception as e:
                    self.logger.error(f"Failed to refresh credentials: {e}")
                    creds = None

            if not creds:
                if not os.path.exists(self.credentials_path):
                    self.logger.error(f"Credentials file not found: {self.credentials_path}")
                    raise FileNotFoundError(
                        f"Gmail credentials not found. Please place credentials.json in the project directory."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                self.logger.info("Completed OAuth authentication")

            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            self.logger.info(f"Saved credentials to {self.token_path}")

        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail API service initialized")

    def create_draft(
        self,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str = "",
        attachment_path: Optional[str] = None
    ) -> Dict:
        """
        Create a Gmail draft with optional attachment.

        Args:
            recipient: Recipient email address
            subject: Email subject line
            html_body: HTML email body
            text_body: Plain text email body (fallback)
            attachment_path: Path to PDF attachment (optional)

        Returns:
            Draft creation response dictionary
        """
        try:
            # Create MIME message
            message = self._create_mime_message(
                recipient,
                subject,
                html_body,
                text_body,
                attachment_path
            )

            # Encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Create draft
            draft_body = {
                'message': {
                    'raw': encoded_message
                }
            }

            draft = self.service.users().drafts().create(
                userId='me',
                body=draft_body
            ).execute()

            self.logger.info(
                f"Created draft for {recipient} - Subject: {subject} - Draft ID: {draft['id']}"
            )

            return draft

        except Exception as e:
            self.logger.error(f"Failed to create draft for {recipient}: {str(e)}")
            raise

    def _create_mime_message(
        self,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str = "",
        attachment_path: Optional[str] = None
    ) -> MIMEMultipart:
        """
        Create MIME multipart message.

        Args:
            recipient: Recipient email address
            subject: Email subject line
            html_body: HTML email body
            text_body: Plain text email body
            attachment_path: Path to PDF attachment

        Returns:
            MIMEMultipart message
        """
        # Create multipart message
        message = MIMEMultipart('mixed')
        message['To'] = recipient
        message['Subject'] = subject

        # Create multipart alternative for HTML and text
        msg_alternative = MIMEMultipart('alternative')
        message.attach(msg_alternative)

        # Add text version
        if text_body:
            part_text = MIMEText(text_body, 'plain', 'utf-8')
            msg_alternative.attach(part_text)

        # Add HTML version
        part_html = MIMEText(html_body, 'html', 'utf-8')
        msg_alternative.attach(part_html)

        # Add PDF attachment if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                pdf_data = f.read()

            part_pdf = MIMEApplication(pdf_data, _subtype='pdf')
            filename = Path(attachment_path).name
            part_pdf.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(part_pdf)

            self.logger.debug(f"Attached PDF: {filename}")

        return message

    def create_drafts_batch(self, draft_data_list: list) -> Dict[str, any]:
        """
        Create multiple drafts in batch.

        Args:
            draft_data_list: List of dictionaries containing draft data
                Each dict should have: recipient, subject, html_body, text_body, attachment_path

        Returns:
            Dictionary with success/failure statistics and details
        """
        results = {
            'total': len(draft_data_list),
            'successful': 0,
            'failed': 0,
            'draft_ids': [],
            'errors': []
        }

        for idx, draft_data in enumerate(draft_data_list, 1):
            try:
                self.logger.info(f"Creating draft {idx}/{len(draft_data_list)}")

                draft = self.create_draft(
                    recipient=draft_data['recipient'],
                    subject=draft_data['subject'],
                    html_body=draft_data['html_body'],
                    text_body=draft_data.get('text_body', ''),
                    attachment_path=draft_data.get('attachment_path')
                )

                results['successful'] += 1
                results['draft_ids'].append(draft['id'])

            except Exception as e:
                results['failed'] += 1
                error_info = {
                    'recipient': draft_data.get('recipient', 'Unknown'),
                    'subject': draft_data.get('subject', 'Unknown'),
                    'error': str(e)
                }
                results['errors'].append(error_info)
                self.logger.error(f"Failed to create draft {idx}: {str(e)}")

        self.logger.info(
            f"Batch draft creation complete: "
            f"{results['successful']}/{results['total']} successful, "
            f"{results['failed']} failed"
        )

        return results

    def send_draft(self, draft_id: str) -> Dict:
        """
        Send a draft email.

        Args:
            draft_id: Gmail draft ID

        Returns:
            Send response dictionary
        """
        try:
            sent_message = self.service.users().drafts().send(
                userId='me',
                body={'id': draft_id}
            ).execute()

            self.logger.info(f"Sent draft {draft_id}")
            return sent_message

        except Exception as e:
            self.logger.error(f"Failed to send draft {draft_id}: {str(e)}")
            raise

    def delete_draft(self, draft_id: str):
        """
        Delete a draft.

        Args:
            draft_id: Gmail draft ID
        """
        try:
            self.service.users().drafts().delete(
                userId='me',
                id=draft_id
            ).execute()

            self.logger.info(f"Deleted draft {draft_id}")

        except Exception as e:
            self.logger.error(f"Failed to delete draft {draft_id}: {str(e)}")
            raise

    def list_drafts(self, max_results: int = 50) -> list:
        """
        List existing drafts.

        Args:
            max_results: Maximum number of drafts to retrieve

        Returns:
            List of draft metadata
        """
        try:
            results = self.service.users().drafts().list(
                userId='me',
                maxResults=max_results
            ).execute()

            drafts = results.get('drafts', [])
            self.logger.info(f"Found {len(drafts)} existing drafts")

            return drafts

        except Exception as e:
            self.logger.error(f"Failed to list drafts: {str(e)}")
            raise
