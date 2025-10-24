"""
Gmail Reader Module.
Extracts emails and PDF attachments from Gmail using Gmail API.
"""

import os
import base64
from pathlib import Path
from typing import List, Dict
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from .logger import get_logger

logger = get_logger('GmailReader')


class GmailReader:
    """Reads emails and extracts PDFs from Gmail."""

    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Initialize Gmail reader.

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

    def get_emails_from_sender(self, sender_email: str, max_results: int = 50) -> List[Dict]:
        """
        Get emails from a specific sender.

        Args:
            sender_email: Email address to filter by
            max_results: Maximum number of emails to retrieve

        Returns:
            List of email metadata dictionaries
        """
        try:
            query = f'from:{sender_email}'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            self.logger.info(f"Found {len(messages)} emails from {sender_email}")

            return messages

        except Exception as e:
            self.logger.error(f"Failed to retrieve emails: {str(e)}")
            raise

    def get_unread_emails_from_sender(self, sender_email: str, max_results: int = 50) -> List[Dict]:
        """
        Get unread emails from a specific sender.

        Args:
            sender_email: Email address to filter by
            max_results: Maximum number of emails to retrieve

        Returns:
            List of email metadata dictionaries
        """
        try:
            query = f'from:{sender_email} is:unread'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            self.logger.info(f"Found {len(messages)} unread emails from {sender_email}")

            return messages

        except Exception as e:
            self.logger.error(f"Failed to retrieve unread emails: {str(e)}")
            raise

    def extract_pdfs_from_email(self, message_id: str, output_dir: str) -> List[str]:
        """
        Extract PDF attachments from an email.

        Args:
            message_id: Gmail message ID
            output_dir: Directory to save PDFs

        Returns:
            List of paths to extracted PDF files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        pdf_files = []

        try:
            # Get message details
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()

            # Check for attachments
            if 'parts' not in message['payload']:
                self.logger.debug(f"No attachments in message {message_id}")
                return pdf_files

            for part in message['payload']['parts']:
                if part.get('filename') and part['filename'].lower().endswith('.pdf'):
                    attachment_id = part['body'].get('attachmentId')

                    if attachment_id:
                        # Download attachment
                        attachment = self.service.users().messages().attachments().get(
                            userId='me',
                            messageId=message_id,
                            id=attachment_id
                        ).execute()

                        # Decode and save
                        file_data = base64.urlsafe_b64decode(attachment['data'])
                        pdf_path = output_path / part['filename']

                        with open(pdf_path, 'wb') as f:
                            f.write(file_data)

                        pdf_files.append(str(pdf_path))
                        self.logger.info(f"Extracted PDF: {part['filename']}")

        except Exception as e:
            self.logger.error(f"Failed to extract PDFs from message {message_id}: {str(e)}")
            raise

        return pdf_files

    def extract_all_pdfs(self, sender_email: str, output_dir: str, mark_as_read: bool = False) -> List[str]:
        """
        Extract all PDF attachments from emails from a specific sender.

        Args:
            sender_email: Email address to filter by
            output_dir: Directory to save PDFs
            mark_as_read: Whether to mark emails as read after extraction

        Returns:
            List of paths to all extracted PDF files
        """
        all_pdfs = []

        # Get unread emails from sender
        messages = self.get_unread_emails_from_sender(sender_email)

        self.logger.info(f"Processing {len(messages)} emails for PDF extraction")

        for message in messages:
            message_id = message['id']

            try:
                pdfs = self.extract_pdfs_from_email(message_id, output_dir)
                all_pdfs.extend(pdfs)

                # Mark as read if requested
                if mark_as_read and pdfs:
                    self.mark_as_read(message_id)

            except Exception as e:
                self.logger.error(f"Error processing message {message_id}: {str(e)}")
                continue

        self.logger.info(f"Extracted {len(all_pdfs)} PDF files total")
        return all_pdfs

    def mark_as_read(self, message_id: str):
        """
        Mark an email as read.

        Args:
            message_id: Gmail message ID
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            self.logger.debug(f"Marked message {message_id} as read")

        except Exception as e:
            self.logger.error(f"Failed to mark message as read: {str(e)}")

    def get_message_subject(self, message_id: str) -> str:
        """
        Get the subject line of an email.

        Args:
            message_id: Gmail message ID

        Returns:
            Subject line
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['Subject']
            ).execute()

            headers = message.get('payload', {}).get('headers', [])
            for header in headers:
                if header['name'].lower() == 'subject':
                    return header['value']

            return "(No Subject)"

        except Exception as e:
            self.logger.error(f"Failed to get message subject: {str(e)}")
            return "(Error retrieving subject)"
