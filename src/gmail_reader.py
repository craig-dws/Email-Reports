"""
Gmail Reader Module.
Extracts emails and PDF attachments from Gmail using Gmail API.

This module handles:
- Gmail API authentication with automatic token refresh
- Searching for emails from Looker Studio senders
- Downloading PDF attachments
- Marking emails as processed (read or labeled)
- Proper error handling for API rate limits and network errors
- Support for batch arrival of PDFs
"""

import os
import base64
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from .logger import get_logger

logger = get_logger('GmailReader')


class GmailReader:
    """Reads emails and extracts PDFs from Gmail."""

    # Gmail API scopes - readonly for extraction, modify for marking as read
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    # Label name for marking processed emails
    PROCESSED_LABEL_NAME = 'EmailReports/Processed'

    # Rate limiting settings
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1  # seconds

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
        self.processed_label_id = None

        self._authenticate()
        self._ensure_processed_label()

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

    def _ensure_processed_label(self):
        """
        Ensure the 'Processed' label exists in Gmail, create if it doesn't.
        Sets self.processed_label_id for use in marking emails as processed.
        """
        try:
            # Get all labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])

            # Look for existing processed label
            for label in labels:
                if label['name'] == self.PROCESSED_LABEL_NAME:
                    self.processed_label_id = label['id']
                    self.logger.info(f"Found existing label: {self.PROCESSED_LABEL_NAME}")
                    return

            # Create the label if it doesn't exist
            label_object = {
                'name': self.PROCESSED_LABEL_NAME,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()

            self.processed_label_id = created_label['id']
            self.logger.info(f"Created new label: {self.PROCESSED_LABEL_NAME}")

        except HttpError as e:
            self.logger.warning(f"Failed to create/find processed label: {e}")
            # Not critical - we can still mark as read
        except Exception as e:
            self.logger.warning(f"Unexpected error managing labels: {e}")

    def _execute_with_retry(self, request, operation_name: str):
        """
        Execute a Gmail API request with exponential backoff retry logic.

        Args:
            request: Gmail API request object
            operation_name: Name of operation for logging

        Returns:
            API response

        Raises:
            Exception: If all retries are exhausted
        """
        backoff = self.INITIAL_BACKOFF

        for attempt in range(self.MAX_RETRIES):
            try:
                return request.execute()

            except HttpError as e:
                # Check if it's a rate limit error (429) or server error (5xx)
                if e.resp.status in [429, 500, 503]:
                    if attempt < self.MAX_RETRIES - 1:
                        self.logger.warning(
                            f"{operation_name} failed (attempt {attempt + 1}/{self.MAX_RETRIES}): "
                            f"HTTP {e.resp.status}. Retrying in {backoff}s..."
                        )
                        time.sleep(backoff)
                        backoff *= 2  # Exponential backoff
                    else:
                        self.logger.error(
                            f"{operation_name} failed after {self.MAX_RETRIES} attempts"
                        )
                        raise
                else:
                    # Non-retryable error
                    self.logger.error(f"{operation_name} failed: HTTP {e.resp.status}")
                    raise

            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    self.logger.warning(
                        f"{operation_name} failed (attempt {attempt + 1}/{self.MAX_RETRIES}): "
                        f"{str(e)}. Retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    self.logger.error(
                        f"{operation_name} failed after {self.MAX_RETRIES} attempts: {str(e)}"
                    )
                    raise

        # Should not reach here, but just in case
        raise Exception(f"{operation_name} failed after all retries")

    def search_emails(
        self,
        sender_emails: List[str],
        unread_only: bool = True,
        has_attachment: bool = True,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Search for emails matching criteria.

        Args:
            sender_emails: List of sender email addresses to filter by
            unread_only: Only return unread emails
            has_attachment: Only return emails with attachments
            max_results: Maximum number of emails to retrieve

        Returns:
            List of email metadata dictionaries with 'id' and 'threadId'
        """
        # Build query
        query_parts = []

        # Add sender filter (OR condition for multiple senders)
        if sender_emails:
            if len(sender_emails) == 1:
                query_parts.append(f'from:{sender_emails[0]}')
            else:
                sender_query = ' OR '.join([f'from:{email}' for email in sender_emails])
                query_parts.append(f'({sender_query})')

        if unread_only:
            query_parts.append('is:unread')

        if has_attachment:
            query_parts.append('has:attachment')

        query = ' '.join(query_parts)
        self.logger.info(f"Searching emails with query: {query}")

        try:
            request = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            )
            results = self._execute_with_retry(request, "Search emails")

            messages = results.get('messages', [])
            self.logger.info(f"Found {len(messages)} matching emails")

            return messages

        except Exception as e:
            self.logger.error(f"Failed to search emails: {str(e)}")
            raise

    def get_emails_from_sender(self, sender_email: str, max_results: int = 50) -> List[Dict]:
        """
        Get emails from a specific sender.

        Args:
            sender_email: Email address to filter by
            max_results: Maximum number of emails to retrieve

        Returns:
            List of email metadata dictionaries
        """
        return self.search_emails(
            sender_emails=[sender_email],
            unread_only=False,
            has_attachment=False,
            max_results=max_results
        )

    def get_unread_emails_from_sender(self, sender_email: str, max_results: int = 50) -> List[Dict]:
        """
        Get unread emails from a specific sender.

        Args:
            sender_email: Email address to filter by
            max_results: Maximum number of emails to retrieve

        Returns:
            List of email metadata dictionaries
        """
        return self.search_emails(
            sender_emails=[sender_email],
            unread_only=True,
            has_attachment=False,
            max_results=max_results
        )

    def get_email_details(self, message_id: str) -> Dict:
        """
        Get detailed information about an email.

        Args:
            message_id: Gmail message ID

        Returns:
            Dict with email details including subject, from, date, and parts
        """
        try:
            request = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            )
            message = self._execute_with_retry(request, f"Get email details {message_id}")

            # Extract headers
            headers = message.get('payload', {}).get('headers', [])
            email_info = {
                'id': message_id,
                'subject': '',
                'from': '',
                'date': '',
                'payload': message.get('payload', {})
            }

            for header in headers:
                name = header['name'].lower()
                if name == 'subject':
                    email_info['subject'] = header['value']
                elif name == 'from':
                    email_info['from'] = header['value']
                elif name == 'date':
                    email_info['date'] = header['value']

            return email_info

        except Exception as e:
            self.logger.error(f"Failed to get email details for {message_id}: {str(e)}")
            raise

    def extract_pdfs_from_email(
        self,
        message_id: str,
        output_dir: str,
        sanitize_filename: bool = True
    ) -> Tuple[List[str], List[str]]:
        """
        Extract PDF attachments from an email.

        Args:
            message_id: Gmail message ID
            output_dir: Directory to save PDFs
            sanitize_filename: Whether to sanitize filenames for Windows compatibility

        Returns:
            Tuple of (list of successfully extracted PDF paths, list of errors)
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        pdf_files = []
        errors = []

        try:
            # Get message details
            email_info = self.get_email_details(message_id)
            payload = email_info['payload']

            # Check for attachments in parts
            parts = payload.get('parts', [])
            if not parts:
                # Try checking if the whole payload is an attachment
                if payload.get('filename', '').lower().endswith('.pdf'):
                    parts = [payload]

            if not parts:
                self.logger.debug(f"No attachments in message {message_id}")
                return pdf_files, errors

            for part in parts:
                filename = part.get('filename', '')
                if not filename or not filename.lower().endswith('.pdf'):
                    continue

                try:
                    # Get attachment ID
                    attachment_id = part.get('body', {}).get('attachmentId')

                    if not attachment_id:
                        error_msg = f"No attachment ID for {filename} in message {message_id}"
                        self.logger.warning(error_msg)
                        errors.append(error_msg)
                        continue

                    # Download attachment with retry logic
                    request = self.service.users().messages().attachments().get(
                        userId='me',
                        messageId=message_id,
                        id=attachment_id
                    )
                    attachment = self._execute_with_retry(
                        request,
                        f"Download attachment {filename}"
                    )

                    # Decode attachment data
                    try:
                        file_data = base64.urlsafe_b64decode(attachment['data'])
                    except Exception as e:
                        error_msg = f"Failed to decode {filename}: {str(e)}"
                        self.logger.error(error_msg)
                        errors.append(error_msg)
                        continue

                    # Sanitize filename if requested
                    if sanitize_filename:
                        filename = self._sanitize_filename(filename)

                    # Save file
                    pdf_path = output_path / filename

                    # Handle duplicate filenames
                    if pdf_path.exists():
                        base = pdf_path.stem
                        ext = pdf_path.suffix
                        counter = 1
                        while pdf_path.exists():
                            pdf_path = output_path / f"{base}_{counter}{ext}"
                            counter += 1
                        self.logger.info(f"Renamed duplicate file to: {pdf_path.name}")

                    with open(pdf_path, 'wb') as f:
                        f.write(file_data)

                    pdf_files.append(str(pdf_path))
                    self.logger.info(f"Extracted PDF: {pdf_path.name} ({len(file_data)} bytes)")

                except Exception as e:
                    error_msg = f"Failed to extract {filename} from message {message_id}: {str(e)}"
                    self.logger.error(error_msg)
                    errors.append(error_msg)
                    continue

        except Exception as e:
            error_msg = f"Failed to process message {message_id}: {str(e)}"
            self.logger.error(error_msg)
            errors.append(error_msg)

        return pdf_files, errors

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for Windows compatibility.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove invalid Windows filename characters
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')

        # Limit length (Windows has 260 char path limit)
        if len(filename) > 200:
            name_part = filename[:-4]  # Remove .pdf
            filename = name_part[:196] + '.pdf'

        return filename

    def extract_all_pdfs(
        self,
        sender_emails: List[str],
        output_dir: str,
        mark_as_processed: bool = True,
        unread_only: bool = True
    ) -> Dict:
        """
        Extract all PDF attachments from emails from specified senders.

        Args:
            sender_emails: List of email addresses to filter by
            output_dir: Directory to save PDFs
            mark_as_processed: Whether to mark emails as processed after extraction
            unread_only: Only process unread emails

        Returns:
            Dictionary with extraction results:
            {
                'pdfs': [list of PDF paths],
                'processed_count': int,
                'error_count': int,
                'errors': [list of error messages]
            }
        """
        result = {
            'pdfs': [],
            'processed_count': 0,
            'error_count': 0,
            'errors': []
        }

        # Search for emails with PDF attachments
        messages = self.search_emails(
            sender_emails=sender_emails,
            unread_only=unread_only,
            has_attachment=True,
            max_results=50
        )

        self.logger.info(f"Processing {len(messages)} emails for PDF extraction")

        for message in messages:
            message_id = message['id']

            try:
                # Extract PDFs from this email
                pdfs, errors = self.extract_pdfs_from_email(message_id, output_dir)

                if pdfs:
                    result['pdfs'].extend(pdfs)
                    result['processed_count'] += 1

                    # Mark as processed if requested
                    if mark_as_processed:
                        self.mark_as_processed(message_id)

                if errors:
                    result['errors'].extend(errors)
                    result['error_count'] += len(errors)

            except Exception as e:
                error_msg = f"Error processing message {message_id}: {str(e)}"
                self.logger.error(error_msg)
                result['errors'].append(error_msg)
                result['error_count'] += 1
                continue

        self.logger.info(
            f"Extraction complete: {len(result['pdfs'])} PDFs from "
            f"{result['processed_count']} emails, {result['error_count']} errors"
        )
        return result

    def mark_as_processed(self, message_id: str):
        """
        Mark an email as processed (read + custom label).

        Args:
            message_id: Gmail message ID
        """
        try:
            modify_body = {'removeLabelIds': ['UNREAD']}

            # Add processed label if available
            if self.processed_label_id:
                modify_body['addLabelIds'] = [self.processed_label_id]

            request = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=modify_body
            )
            self._execute_with_retry(request, f"Mark as processed {message_id}")

            self.logger.debug(f"Marked message {message_id} as processed")

        except Exception as e:
            self.logger.error(f"Failed to mark message as processed: {str(e)}")

    def mark_as_read(self, message_id: str):
        """
        Mark an email as read (without custom label).

        Args:
            message_id: Gmail message ID
        """
        try:
            request = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            )
            self._execute_with_retry(request, f"Mark as read {message_id}")

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
            request = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['Subject']
            )
            message = self._execute_with_retry(request, f"Get subject {message_id}")

            headers = message.get('payload', {}).get('headers', [])
            for header in headers:
                if header['name'].lower() == 'subject':
                    return header['value']

            return "(No Subject)"

        except Exception as e:
            self.logger.error(f"Failed to get message subject: {str(e)}")
            return "(Error retrieving subject)"


# Convenience function for easy import
def extract_looker_studio_pdfs(
    sender_emails: List[str],
    output_dir: str,
    credentials_path: str = 'credentials.json',
    token_path: str = 'token.json'
) -> Dict:
    """
    Convenience function to extract PDFs from Looker Studio emails.

    Args:
        sender_emails: List of Looker Studio sender email addresses
        output_dir: Directory to save PDFs
        credentials_path: Path to OAuth credentials
        token_path: Path to OAuth token

    Returns:
        Dictionary with extraction results
    """
    reader = GmailReader(credentials_path, token_path)
    return reader.extract_all_pdfs(
        sender_emails=sender_emails,
        output_dir=output_dir,
        mark_as_processed=True,
        unread_only=True
    )
