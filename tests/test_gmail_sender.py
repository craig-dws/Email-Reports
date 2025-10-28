"""
Unit tests for Gmail Sender Module.
Tests Gmail API integration with mocked responses.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open, call
import os
import base64
import time
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gmail_sender import GmailSender


class TestGmailSender(unittest.TestCase):
    """Test cases for GmailSender class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_credentials_path = 'test_credentials.json'
        self.test_token_path = 'test_token.json'
        self.test_send_delay = 60  # 1 minute for testing

    @patch('src.gmail_sender.build')
    @patch('src.gmail_sender.Credentials')
    @patch('os.path.exists')
    def test_authentication_with_existing_token(self, mock_exists, mock_creds, mock_build):
        """Test authentication using existing valid token."""
        # Mock existing token file
        mock_exists.return_value = True

        # Mock valid credentials
        mock_cred_instance = MagicMock()
        mock_cred_instance.valid = True
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance

        # Mock Gmail service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Create sender
        sender = GmailSender(
            self.test_credentials_path,
            self.test_token_path,
            send_delay=self.test_send_delay
        )

        # Verify authentication succeeded
        self.assertIsNotNone(sender.service)
        self.assertEqual(sender.send_delay, self.test_send_delay)
        mock_creds.from_authorized_user_file.assert_called_once()

    @patch('src.gmail_sender.build')
    @patch('src.gmail_sender.Credentials')
    @patch('os.path.exists')
    def test_authentication_with_expired_token(self, mock_exists, mock_creds, mock_build):
        """Test authentication with expired token that needs refresh."""
        # Mock existing token file
        mock_exists.return_value = True

        # Mock expired credentials that can be refreshed
        mock_cred_instance = MagicMock()
        mock_cred_instance.valid = False
        mock_cred_instance.expired = True
        mock_cred_instance.refresh_token = 'refresh_token_123'
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance

        # Mock Gmail service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock successful refresh
        with patch('builtins.open', mock_open()):
            sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Verify refresh was called
        mock_cred_instance.refresh.assert_called_once()

    def test_create_draft_success(self):
        """Test successful draft creation."""
        # Create sender with mocked service
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock draft creation response
        mock_draft_response = {'id': 'draft_123', 'message': {'id': 'msg_123'}}
        mock_service.users().drafts().create().execute.return_value = mock_draft_response

        # Test data
        recipient = 'test@example.com'
        subject = 'Test Subject'
        html_body = '<h1>Test Email</h1>'
        text_body = 'Test Email'

        # Create draft
        result = sender.create_draft(recipient, subject, html_body, text_body)

        # Verify result
        self.assertEqual(result['id'], 'draft_123')
        mock_service.users().drafts().create.assert_called_once()

    def test_create_draft_with_attachment(self):
        """Test draft creation with PDF attachment."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open(read_data=b'PDF content')):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock draft creation response
        mock_draft_response = {'id': 'draft_456', 'message': {'id': 'msg_456'}}
        mock_service.users().drafts().create().execute.return_value = mock_draft_response

        # Mock file existence check
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=b'PDF content')):
                result = sender.create_draft(
                    recipient='test@example.com',
                    subject='Test with PDF',
                    html_body='<p>See attachment</p>',
                    attachment_path='test.pdf'
                )

        # Verify draft was created
        self.assertEqual(result['id'], 'draft_456')

    def test_create_drafts_batch(self):
        """Test batch draft creation."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock draft creation responses
        mock_service.users().drafts().create().execute.side_effect = [
            {'id': 'draft_1', 'message': {'id': 'msg_1'}},
            {'id': 'draft_2', 'message': {'id': 'msg_2'}},
            {'id': 'draft_3', 'message': {'id': 'msg_3'}}
        ]

        # Test data
        draft_data_list = [
            {
                'recipient': 'client1@example.com',
                'subject': 'Report 1',
                'html_body': '<p>Report 1</p>',
                'text_body': 'Report 1'
            },
            {
                'recipient': 'client2@example.com',
                'subject': 'Report 2',
                'html_body': '<p>Report 2</p>',
                'text_body': 'Report 2'
            },
            {
                'recipient': 'client3@example.com',
                'subject': 'Report 3',
                'html_body': '<p>Report 3</p>',
                'text_body': 'Report 3'
            }
        ]

        # Create batch
        results = sender.create_drafts_batch(draft_data_list)

        # Verify results
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['successful'], 3)
        self.assertEqual(results['failed'], 0)
        self.assertEqual(len(results['draft_ids']), 3)
        self.assertEqual(results['draft_ids'][0], 'draft_1')

    def test_create_drafts_batch_with_failures(self):
        """Test batch draft creation with some failures."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock draft creation responses (second one fails)
        mock_service.users().drafts().create().execute.side_effect = [
            {'id': 'draft_1', 'message': {'id': 'msg_1'}},
            Exception('API Error'),
            {'id': 'draft_3', 'message': {'id': 'msg_3'}}
        ]

        # Test data
        draft_data_list = [
            {'recipient': 'client1@example.com', 'subject': 'Report 1', 'html_body': '<p>Report 1</p>'},
            {'recipient': 'client2@example.com', 'subject': 'Report 2', 'html_body': '<p>Report 2</p>'},
            {'recipient': 'client3@example.com', 'subject': 'Report 3', 'html_body': '<p>Report 3</p>'}
        ]

        # Create batch
        results = sender.create_drafts_batch(draft_data_list)

        # Verify results
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['successful'], 2)
        self.assertEqual(results['failed'], 1)
        self.assertEqual(len(results['errors']), 1)
        self.assertEqual(results['errors'][0]['recipient'], 'client2@example.com')

    def test_send_email_success(self):
        """Test successful direct email sending."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock send response
        mock_send_response = {'id': 'msg_789', 'labelIds': ['SENT']}
        mock_service.users().messages().send().execute.return_value = mock_send_response

        # Send email
        result = sender.send_email(
            recipient='test@example.com',
            subject='Test Email',
            html_body='<p>Test content</p>',
            text_body='Test content'
        )

        # Verify result
        self.assertEqual(result['id'], 'msg_789')
        mock_service.users().messages().send.assert_called_once()

    def test_send_preview_email(self):
        """Test sending preview email with header."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock send response
        mock_send_response = {'id': 'preview_msg_123', 'labelIds': ['SENT']}
        mock_service.users().messages().send().execute.return_value = mock_send_response

        # Send preview
        result = sender.send_preview_email(
            preview_recipient='owner@agency.com',
            original_recipient='client@example.com',
            subject='Your Monthly Report',
            html_body='<p>Report content</p>',
            text_body='Report content'
        )

        # Verify result
        self.assertEqual(result['id'], 'preview_msg_123')
        mock_service.users().messages().send.assert_called_once()

        # Verify that the sent message included preview header (check the call args)
        call_args = mock_service.users().messages().send.call_args
        sent_body = call_args[1]['body']
        decoded_message = base64.urlsafe_b64decode(sent_body['raw']).decode('utf-8', errors='ignore')
        self.assertIn('[PREVIEW]', decoded_message)
        self.assertIn('EMAIL PREVIEW', decoded_message)

    def test_send_draft_success(self):
        """Test sending a draft."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock send draft response
        mock_send_response = {'id': 'msg_sent_123', 'labelIds': ['SENT']}
        mock_service.users().drafts().send().execute.return_value = mock_send_response

        # Send draft
        result = sender.send_draft('draft_123')

        # Verify result
        self.assertEqual(result['id'], 'msg_sent_123')
        mock_service.users().drafts().send.assert_called_once()

    @patch('time.sleep', return_value=None)  # Mock sleep to speed up test
    def test_send_drafts_with_delay(self, mock_sleep):
        """Test sending multiple drafts with delays."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(
                            self.test_credentials_path,
                            self.test_token_path,
                            send_delay=60
                        )

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock send responses
        mock_service.users().drafts().send().execute.side_effect = [
            {'id': 'sent_1', 'labelIds': ['SENT']},
            {'id': 'sent_2', 'labelIds': ['SENT']},
            {'id': 'sent_3', 'labelIds': ['SENT']}
        ]

        # Send drafts with delay
        draft_ids = ['draft_1', 'draft_2', 'draft_3']
        results = sender.send_drafts_with_delay(draft_ids)

        # Verify results
        self.assertEqual(results['total'], 3)
        self.assertEqual(results['successful'], 3)
        self.assertEqual(results['failed'], 0)
        self.assertEqual(len(results['sent_message_ids']), 3)

        # Verify sleep was called between sends (2 times for 3 emails)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(60)

    @patch('time.sleep', return_value=None)
    def test_send_emails_with_delay(self, mock_sleep):
        """Test sending multiple emails with delays."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(
                            self.test_credentials_path,
                            self.test_token_path,
                            send_delay=120
                        )

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock send responses
        mock_service.users().messages().send().execute.side_effect = [
            {'id': 'msg_1', 'labelIds': ['SENT']},
            {'id': 'msg_2', 'labelIds': ['SENT']}
        ]

        # Email data
        email_data_list = [
            {
                'recipient': 'client1@example.com',
                'subject': 'Report 1',
                'html_body': '<p>Report 1</p>',
                'text_body': 'Report 1'
            },
            {
                'recipient': 'client2@example.com',
                'subject': 'Report 2',
                'html_body': '<p>Report 2</p>',
                'text_body': 'Report 2'
            }
        ]

        # Send emails with delay
        results = sender.send_emails_with_delay(email_data_list)

        # Verify results
        self.assertEqual(results['total'], 2)
        self.assertEqual(results['successful'], 2)
        self.assertEqual(results['failed'], 0)

        # Verify sleep was called once (between 2 emails)
        self.assertEqual(mock_sleep.call_count, 1)
        mock_sleep.assert_called_with(120)

    def test_retry_logic_on_rate_limit(self):
        """Test retry logic when hitting rate limits."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Create a mock HttpError for rate limiting
        from googleapiclient.errors import HttpError
        from unittest.mock import Mock

        # Mock rate limit error (429) then success
        rate_limit_error = HttpError(
            resp=Mock(status=429),
            content=b'Rate limit exceeded'
        )

        mock_service.users().messages().send().execute.side_effect = [
            rate_limit_error,
            {'id': 'msg_success', 'labelIds': ['SENT']}
        ]

        # Send email (should retry and succeed)
        with patch('time.sleep', return_value=None):  # Speed up test
            result = sender.send_email(
                recipient='test@example.com',
                subject='Test',
                html_body='<p>Test</p>'
            )

        # Verify success after retry
        self.assertEqual(result['id'], 'msg_success')
        self.assertEqual(mock_service.users().messages().send().execute.call_count, 2)

    def test_delete_draft(self):
        """Test draft deletion."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Delete draft
        sender.delete_draft('draft_to_delete')

        # Verify delete was called
        mock_service.users().drafts().delete.assert_called_once_with(
            userId='me',
            id='draft_to_delete'
        )

    def test_list_drafts(self):
        """Test listing existing drafts."""
        with patch('src.gmail_sender.build'):
            with patch('src.gmail_sender.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        sender = GmailSender(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        sender.service = mock_service

        # Mock list response
        mock_list_response = {
            'drafts': [
                {'id': 'draft_1', 'message': {'id': 'msg_1'}},
                {'id': 'draft_2', 'message': {'id': 'msg_2'}}
            ]
        }
        mock_service.users().drafts().list().execute.return_value = mock_list_response

        # List drafts
        drafts = sender.list_drafts()

        # Verify result
        self.assertEqual(len(drafts), 2)
        self.assertEqual(drafts[0]['id'], 'draft_1')
        mock_service.users().drafts().list.assert_called_once()


if __name__ == '__main__':
    unittest.main()
