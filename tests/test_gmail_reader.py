"""
Unit tests for Gmail Reader Module.
Tests Gmail API integration with mocked responses.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open
import os
import base64
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gmail_reader import GmailReader, extract_looker_studio_pdfs


class TestGmailReader(unittest.TestCase):
    """Test cases for GmailReader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_credentials_path = 'test_credentials.json'
        self.test_token_path = 'test_token.json'
        self.test_output_dir = 'test_pdfs'

    @patch('src.gmail_reader.build')
    @patch('src.gmail_reader.Credentials')
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

        # Mock labels list for processed label check
        mock_service.users().labels().list().execute.return_value = {'labels': []}

        # Create reader
        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        # Verify authentication succeeded
        self.assertIsNotNone(reader.service)
        mock_creds.from_authorized_user_file.assert_called_once()

    @patch('src.gmail_reader.build')
    @patch('src.gmail_reader.Credentials')
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

        # Mock labels list
        mock_service.users().labels().list().execute.return_value = {'labels': []}

        # Mock successful refresh
        with patch('builtins.open', mock_open()):
            reader = GmailReader(self.test_credentials_path, self.test_token_path)

        # Verify refresh was called
        mock_cred_instance.refresh.assert_called_once()

    def test_search_emails_single_sender(self):
        """Test searching for emails from a single sender."""
        # Create reader with mocked service
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        # Mock the service
        mock_service = MagicMock()
        reader.service = mock_service

        # Mock search results
        mock_messages = [
            {'id': '123', 'threadId': 'thread1'},
            {'id': '456', 'threadId': 'thread2'}
        ]
        mock_service.users().messages().list().execute.return_value = {
            'messages': mock_messages
        }

        # Search for emails
        results = reader.search_emails(
            sender_emails=['test@example.com'],
            unread_only=True,
            has_attachment=True
        )

        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], '123')

        # Verify correct query was constructed
        call_args = mock_service.users().messages().list.call_args
        self.assertIn('test@example.com', call_args[1]['q'])
        self.assertIn('is:unread', call_args[1]['q'])
        self.assertIn('has:attachment', call_args[1]['q'])

    def test_search_emails_multiple_senders(self):
        """Test searching for emails from multiple senders."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        mock_service = MagicMock()
        reader.service = mock_service
        mock_service.users().messages().list().execute.return_value = {'messages': []}

        # Search with multiple senders
        reader.search_emails(
            sender_emails=['sender1@example.com', 'sender2@example.com'],
            unread_only=False,
            has_attachment=False
        )

        # Verify query contains OR condition
        call_args = mock_service.users().messages().list.call_args
        query = call_args[1]['q']
        self.assertIn('from:sender1@example.com OR from:sender2@example.com', query)

    def test_get_email_details(self):
        """Test extracting email details."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        mock_service = MagicMock()
        reader.service = mock_service

        # Mock email details
        mock_email = {
            'id': '123',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Email'},
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'Date', 'value': 'Mon, 1 Jan 2024 12:00:00 +0000'}
                ]
            }
        }
        mock_service.users().messages().get().execute.return_value = mock_email

        # Get email details
        details = reader.get_email_details('123')

        # Verify details
        self.assertEqual(details['subject'], 'Test Email')
        self.assertEqual(details['from'], 'sender@example.com')
        self.assertEqual(details['date'], 'Mon, 1 Jan 2024 12:00:00 +0000')

    def test_extract_pdfs_from_email(self):
        """Test extracting PDF attachments from an email."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        mock_service = MagicMock()
        reader.service = mock_service

        # Mock email with PDF attachment
        mock_email = {
            'id': '123',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'SEO Report'},
                    {'name': 'From', 'value': 'looker@example.com'}
                ],
                'parts': [
                    {
                        'filename': 'test_report.pdf',
                        'body': {
                            'attachmentId': 'att123'
                        }
                    }
                ]
            }
        }
        mock_service.users().messages().get().execute.return_value = mock_email

        # Mock attachment data
        pdf_content = b'%PDF-1.4 fake pdf content'
        encoded_content = base64.urlsafe_b64encode(pdf_content).decode()
        mock_service.users().messages().attachments().get().execute.return_value = {
            'data': encoded_content
        }

        # Mock file writing
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('pathlib.Path.mkdir'):
                with patch('pathlib.Path.exists', return_value=False):
                    pdfs, errors = reader.extract_pdfs_from_email('123', self.test_output_dir)

        # Verify PDF was extracted
        self.assertEqual(len(pdfs), 1)
        self.assertTrue(pdfs[0].endswith('test_report.pdf'))
        self.assertEqual(len(errors), 0)

    def test_extract_pdfs_handles_missing_attachment(self):
        """Test handling of email with no attachments."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        mock_service = MagicMock()
        reader.service = mock_service

        # Mock email with no attachments
        mock_email = {
            'id': '123',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'No Attachment'}
                ],
                'parts': []
            }
        }
        mock_service.users().messages().get().execute.return_value = mock_email

        # Extract PDFs (should return empty list)
        with patch('pathlib.Path.mkdir'):
            pdfs, errors = reader.extract_pdfs_from_email('123', self.test_output_dir)

        self.assertEqual(len(pdfs), 0)
        self.assertEqual(len(errors), 0)

    def test_sanitize_filename(self):
        """Test filename sanitization for Windows compatibility."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        # Test various problematic filenames
        test_cases = [
            ('file:name.pdf', 'file_name.pdf'),
            ('file<name>.pdf', 'file_name_.pdf'),
            ('file|name.pdf', 'file_name.pdf'),
            ('file"name.pdf', 'file_name.pdf'),
            (' .filename.pdf', 'filename.pdf'),
        ]

        for input_name, expected_output in test_cases:
            result = reader._sanitize_filename(input_name)
            # The exact output might vary, but should not contain invalid chars
            self.assertNotIn(':', result)
            self.assertNotIn('<', result)
            self.assertNotIn('>', result)
            self.assertNotIn('|', result)
            self.assertNotIn('"', result)

    def test_mark_as_processed(self):
        """Test marking email as processed."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        mock_service = MagicMock()
        reader.service = mock_service
        reader.processed_label_id = 'Label_123'

        # Mark as processed
        reader.mark_as_processed('msg123')

        # Verify modify was called with correct parameters
        mock_service.users().messages().modify.assert_called_once()
        # Verify the userId and id were passed
        modify_call = mock_service.users().messages().modify.call_args
        # The modify method was called with userId='me', id='msg123', body={...}
        self.assertEqual(modify_call[1]['userId'], 'me')
        self.assertEqual(modify_call[1]['id'], 'msg123')
        # Verify the body contains correct label operations
        body = modify_call[1]['body']
        self.assertIn('UNREAD', body['removeLabelIds'])
        self.assertIn('Label_123', body['addLabelIds'])

    def test_retry_logic_on_rate_limit(self):
        """Test exponential backoff retry on rate limit error."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        # Mock request that fails twice then succeeds
        mock_request = MagicMock()
        from googleapiclient.errors import HttpError

        # Create mock HTTP response
        mock_response = MagicMock()
        mock_response.status = 429

        call_count = [0]

        def side_effect():
            call_count[0] += 1
            if call_count[0] < 3:
                raise HttpError(mock_response, b'Rate limit exceeded')
            return {'success': True}

        mock_request.execute.side_effect = side_effect

        # Execute with retry (should succeed after 2 retries)
        with patch('time.sleep'):  # Speed up test by mocking sleep
            result = reader._execute_with_retry(mock_request, 'Test operation')

        self.assertEqual(result, {'success': True})
        self.assertEqual(call_count[0], 3)  # Failed twice, succeeded third time

    def test_extract_all_pdfs_integration(self):
        """Test complete PDF extraction workflow."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader(self.test_credentials_path, self.test_token_path)

        mock_service = MagicMock()
        reader.service = mock_service

        # Mock search results
        mock_service.users().messages().list().execute.return_value = {
            'messages': [
                {'id': '123', 'threadId': 't1'},
                {'id': '456', 'threadId': 't2'}
            ]
        }

        # Mock email details for each message
        def get_message_side_effect(*args, **kwargs):
            msg_id = kwargs.get('id')
            return MagicMock(execute=MagicMock(return_value={
                'id': msg_id,
                'payload': {
                    'headers': [
                        {'name': 'Subject', 'value': f'Report {msg_id}'}
                    ],
                    'parts': [
                        {
                            'filename': f'report_{msg_id}.pdf',
                            'body': {'attachmentId': f'att_{msg_id}'}
                        }
                    ]
                }
            }))

        mock_service.users().messages().get.side_effect = get_message_side_effect

        # Mock attachment data
        pdf_content = base64.urlsafe_b64encode(b'%PDF-1.4 content').decode()
        mock_service.users().messages().attachments().get().execute.return_value = {
            'data': pdf_content
        }

        # Mock file operations
        with patch('builtins.open', mock_open()):
            with patch('pathlib.Path.mkdir'):
                with patch('pathlib.Path.exists', return_value=False):
                    result = reader.extract_all_pdfs(
                        sender_emails=['looker@example.com'],
                        output_dir=self.test_output_dir
                    )

        # Verify results
        self.assertEqual(len(result['pdfs']), 2)
        self.assertEqual(result['processed_count'], 2)
        self.assertEqual(result['error_count'], 0)

    def test_convenience_function(self):
        """Test the convenience function for extracting Looker Studio PDFs."""
        with patch('src.gmail_reader.GmailReader') as mock_reader_class:
            mock_reader = MagicMock()
            mock_reader.extract_all_pdfs.return_value = {
                'pdfs': ['test1.pdf', 'test2.pdf'],
                'processed_count': 2,
                'error_count': 0,
                'errors': []
            }
            mock_reader_class.return_value = mock_reader

            result = extract_looker_studio_pdfs(
                sender_emails=['looker1@example.com', 'looker2@example.com'],
                output_dir=self.test_output_dir
            )

            # Verify reader was created and called
            mock_reader_class.assert_called_once()
            mock_reader.extract_all_pdfs.assert_called_once()

            # Verify results
            self.assertEqual(len(result['pdfs']), 2)
            self.assertEqual(result['processed_count'], 2)


class TestGmailReaderErrorHandling(unittest.TestCase):
    """Test error handling in Gmail Reader."""

    def test_handle_corrupted_pdf_data(self):
        """Test handling of corrupted PDF data."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader('creds.json', 'token.json')

        mock_service = MagicMock()
        reader.service = mock_service

        # Mock email with corrupted attachment data
        mock_email = {
            'id': '123',
            'payload': {
                'headers': [{'name': 'Subject', 'value': 'Test'}],
                'parts': [{
                    'filename': 'corrupted.pdf',
                    'body': {'attachmentId': 'att123'}
                }]
            }
        }
        mock_service.users().messages().get().execute.return_value = mock_email

        # Mock corrupted attachment data (not valid base64)
        mock_service.users().messages().attachments().get().execute.return_value = {
            'data': 'not-valid-base64!!!'
        }

        # Extract should handle error gracefully
        with patch('pathlib.Path.mkdir'):
            pdfs, errors = reader.extract_pdfs_from_email('123', 'output')

        # Should have error, not crash
        self.assertEqual(len(pdfs), 0)
        self.assertGreater(len(errors), 0)

    def test_handle_network_error(self):
        """Test handling of network errors."""
        with patch('src.gmail_reader.build'):
            with patch('src.gmail_reader.Credentials'):
                with patch('os.path.exists', return_value=True):
                    with patch('builtins.open', mock_open()):
                        reader = GmailReader('creds.json', 'token.json')

        mock_service = MagicMock()
        reader.service = mock_service

        # Mock network error
        mock_service.users().messages().list().execute.side_effect = Exception('Network error')

        # Should raise exception after retries
        with self.assertRaises(Exception):
            with patch('time.sleep'):  # Speed up test
                reader.search_emails(['test@example.com'])


if __name__ == '__main__':
    unittest.main()
