"""
Gmail Sender Module.
Creates Gmail drafts with HTML content and PDF attachments.
Supports spaced-out sending with rate limiting and retry logic.
"""

import os
import base64
import time
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, Optional, List
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from .logger import get_logger

logger = get_logger('GmailSender')


class GmailSender:
    """Creates Gmail drafts with attachments and sends emails with rate limiting."""

    # Gmail API scopes (requires compose and send permissions)
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.send'
    ]

    # Rate limiting settings
    MAX_RETRIES = 3
    INITIAL_BACKOFF = 1  # seconds
    DEFAULT_SEND_DELAY = 300  # 5 minutes between sends (in seconds)

    def __init__(self,
                 credentials_path: str = 'credentials.json',
                 token_path: str = 'token.json',
                 send_delay: int = DEFAULT_SEND_DELAY):
        """
        Initialize Gmail sender.

        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to store/load token
            send_delay: Delay in seconds between sending emails (default: 300 = 5 minutes)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.send_delay = send_delay
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

    def _execute_with_retry(self, api_call, operation_name: str):
        """
        Execute Gmail API call with exponential backoff retry logic.

        Args:
            api_call: Callable that executes the API request
            operation_name: Description of the operation for logging

        Returns:
            API response

        Raises:
            Exception: If all retries are exhausted
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                return api_call()
            except HttpError as e:
                # Check if error is rate limit (429) or server error (5xx)
                if e.resp.status in [429, 500, 503]:
                    if attempt < self.MAX_RETRIES - 1:
                        # Calculate exponential backoff delay
                        delay = self.INITIAL_BACKOFF * (2 ** attempt)
                        self.logger.warning(
                            f"{operation_name} failed (attempt {attempt + 1}/{self.MAX_RETRIES}): "
                            f"{e.resp.status} - Retrying in {delay}s"
                        )
                        time.sleep(delay)
                        continue
                # Re-raise if not retryable or max retries reached
                raise
            except Exception as e:
                # For non-HTTP errors, retry with backoff
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.INITIAL_BACKOFF * (2 ** attempt)
                    self.logger.warning(
                        f"{operation_name} failed (attempt {attempt + 1}/{self.MAX_RETRIES}): "
                        f"{str(e)} - Retrying in {delay}s"
                    )
                    time.sleep(delay)
                    continue
                raise

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

            # Create draft with retry logic
            draft_body = {
                'message': {
                    'raw': encoded_message
                }
            }

            def _create():
                return self.service.users().drafts().create(
                    userId='me',
                    body=draft_body
                ).execute()

            draft = self._execute_with_retry(_create, f"Create draft for {recipient}")

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

    def send_email(
        self,
        recipient: str,
        subject: str,
        html_body: str,
        text_body: str = "",
        attachment_path: Optional[str] = None
    ) -> Dict:
        """
        Send an email directly without creating a draft first.

        Args:
            recipient: Recipient email address
            subject: Email subject line
            html_body: HTML email body
            text_body: Plain text email body (fallback)
            attachment_path: Path to PDF attachment (optional)

        Returns:
            Send response dictionary
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

            # Send email with retry logic
            send_body = {'raw': encoded_message}

            def _send():
                return self.service.users().messages().send(
                    userId='me',
                    body=send_body
                ).execute()

            sent_message = self._execute_with_retry(_send, f"Send email to {recipient}")

            self.logger.info(
                f"Sent email to {recipient} - Subject: {subject} - Message ID: {sent_message['id']}"
            )

            return sent_message

        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient}: {str(e)}")
            raise

    def send_preview_email(
        self,
        preview_recipient: str,
        original_recipient: str,
        subject: str,
        html_body: str,
        text_body: str = "",
        attachment_path: Optional[str] = None
    ) -> Dict:
        """
        Send a preview email to review address for approval.
        Adds [PREVIEW] tag to subject line to distinguish from actual emails.

        Args:
            preview_recipient: Email address to send preview to (e.g., owner@agency.com)
            original_recipient: Original intended recipient (shown in preview)
            subject: Email subject line
            html_body: HTML email body
            text_body: Plain text email body (fallback)
            attachment_path: Path to PDF attachment (optional)

        Returns:
            Send response dictionary
        """
        try:
            # Add preview header to HTML body
            preview_header = f"""
            <div style="background-color: #fff3cd; border: 2px solid #ffc107; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
                <h3 style="margin: 0 0 10px 0; color: #856404;">📧 EMAIL PREVIEW</h3>
                <p style="margin: 5px 0; color: #856404;"><strong>Original Recipient:</strong> {original_recipient}</p>
                <p style="margin: 5px 0; color: #856404;"><strong>Subject:</strong> {subject}</p>
                <p style="margin: 5px 0; color: #856404; font-size: 12px;"><em>This is a preview for approval. The actual email will be sent from Gmail drafts.</em></p>
            </div>
            """
            preview_html_body = preview_header + html_body

            # Add [PREVIEW] tag to subject
            preview_subject = f"[PREVIEW] {subject}"

            # Send preview email
            return self.send_email(
                recipient=preview_recipient,
                subject=preview_subject,
                html_body=preview_html_body,
                text_body=f"[PREVIEW for {original_recipient}]\n\n{text_body}",
                attachment_path=attachment_path
            )

        except Exception as e:
            self.logger.error(f"Failed to send preview email: {str(e)}")
            raise

    def send_draft(self, draft_id: str) -> Dict:
        """
        Send a draft email.

        Args:
            draft_id: Gmail draft ID

        Returns:
            Send response dictionary
        """
        try:
            def _send():
                return self.service.users().drafts().send(
                    userId='me',
                    body={'id': draft_id}
                ).execute()

            sent_message = self._execute_with_retry(_send, f"Send draft {draft_id}")

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

    def send_drafts_with_delay(
        self,
        draft_ids: List[str],
        delay_seconds: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Send multiple drafts with spacing between sends to avoid spam flags.

        Args:
            draft_ids: List of Gmail draft IDs to send
            delay_seconds: Delay in seconds between sends (uses self.send_delay if None)

        Returns:
            Dictionary with success/failure statistics and details
        """
        if delay_seconds is None:
            delay_seconds = self.send_delay

        results = {
            'total': len(draft_ids),
            'successful': 0,
            'failed': 0,
            'sent_message_ids': [],
            'errors': []
        }

        self.logger.info(
            f"Starting spaced sending of {len(draft_ids)} drafts "
            f"with {delay_seconds}s delay between sends"
        )

        for idx, draft_id in enumerate(draft_ids, 1):
            try:
                # Send draft
                sent_message = self.send_draft(draft_id)
                results['successful'] += 1
                results['sent_message_ids'].append(sent_message['id'])

                self.logger.info(
                    f"Sent draft {idx}/{len(draft_ids)} - "
                    f"Draft ID: {draft_id}, Message ID: {sent_message['id']}"
                )

                # Add delay between sends (except after last email)
                if idx < len(draft_ids):
                    self.logger.info(f"Waiting {delay_seconds}s before next send...")
                    time.sleep(delay_seconds)

            except Exception as e:
                results['failed'] += 1
                error_info = {
                    'draft_id': draft_id,
                    'position': idx,
                    'error': str(e)
                }
                results['errors'].append(error_info)
                self.logger.error(f"Failed to send draft {idx}/{len(draft_ids)}: {str(e)}")

                # Continue with next draft even if one fails
                if idx < len(draft_ids):
                    self.logger.info(f"Continuing with next draft after {delay_seconds}s...")
                    time.sleep(delay_seconds)

        self.logger.info(
            f"Spaced sending complete: "
            f"{results['successful']}/{results['total']} successful, "
            f"{results['failed']} failed"
        )

        return results

    def send_emails_with_delay(
        self,
        email_data_list: List[Dict],
        delay_seconds: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Send multiple emails with spacing between sends to avoid spam flags.

        Args:
            email_data_list: List of dictionaries containing email data
                Each dict should have: recipient, subject, html_body, text_body, attachment_path
            delay_seconds: Delay in seconds between sends (uses self.send_delay if None)

        Returns:
            Dictionary with success/failure statistics and details
        """
        if delay_seconds is None:
            delay_seconds = self.send_delay

        results = {
            'total': len(email_data_list),
            'successful': 0,
            'failed': 0,
            'sent_message_ids': [],
            'errors': []
        }

        self.logger.info(
            f"Starting spaced sending of {len(email_data_list)} emails "
            f"with {delay_seconds}s delay between sends"
        )

        for idx, email_data in enumerate(email_data_list, 1):
            try:
                # Send email
                sent_message = self.send_email(
                    recipient=email_data['recipient'],
                    subject=email_data['subject'],
                    html_body=email_data['html_body'],
                    text_body=email_data.get('text_body', ''),
                    attachment_path=email_data.get('attachment_path')
                )

                results['successful'] += 1
                results['sent_message_ids'].append(sent_message['id'])

                self.logger.info(
                    f"Sent email {idx}/{len(email_data_list)} to {email_data['recipient']} - "
                    f"Message ID: {sent_message['id']}"
                )

                # Add delay between sends (except after last email)
                if idx < len(email_data_list):
                    self.logger.info(f"Waiting {delay_seconds}s before next send...")
                    time.sleep(delay_seconds)

            except Exception as e:
                results['failed'] += 1
                error_info = {
                    'recipient': email_data.get('recipient', 'Unknown'),
                    'subject': email_data.get('subject', 'Unknown'),
                    'position': idx,
                    'error': str(e)
                }
                results['errors'].append(error_info)
                self.logger.error(
                    f"Failed to send email {idx}/{len(email_data_list)} "
                    f"to {email_data.get('recipient', 'Unknown')}: {str(e)}"
                )

                # Continue with next email even if one fails
                if idx < len(email_data_list):
                    self.logger.info(f"Continuing with next email after {delay_seconds}s...")
                    time.sleep(delay_seconds)

        self.logger.info(
            f"Spaced sending complete: "
            f"{results['successful']}/{results['total']} successful, "
            f"{results['failed']} failed"
        )

        return results
