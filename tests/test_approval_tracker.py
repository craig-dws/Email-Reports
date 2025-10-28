"""
Unit tests for Approval Tracker Module.
Tests Google Sheets integration with mocked responses.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.approval_tracker import ApprovalTracker


class TestApprovalTracker(unittest.TestCase):
    """Test cases for ApprovalTracker class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_credentials_path = 'test_token.json'
        self.test_sheet_name = 'Test Email Approvals - January 2025'
        self.test_sheet_id = 'test_sheet_123456789'

        # Sample email data for testing
        self.sample_email_data = [
            {
                'client_name': 'John Doe',
                'business_name': 'ABC Corporation',
                'recipient_email': 'john@abccorp.com',
                'report_type': 'SEO',
                'extraction_errors': ''
            },
            {
                'client_name': 'Sarah Smith',
                'business_name': 'XYZ Services',
                'recipient_email': 'sarah@xyzservices.com',
                'report_type': 'SEM',
                'extraction_errors': 'Missing bounce rate'
            },
            {
                'client_name': 'Michael Johnson',
                'business_name': 'Tech Solutions LLC',
                'recipient_email': 'michael@techsolutions.com',
                'report_type': 'SEO',
                'extraction_errors': ''
            }
        ]

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_initialization(self, mock_gspread, mock_creds):
        """Test ApprovalTracker initialization."""
        tracker = ApprovalTracker(credentials_path=self.test_credentials_path)

        self.assertEqual(tracker.credentials_path, self.test_credentials_path)
        self.assertIsNone(tracker.gc)
        self.assertIsNone(tracker.sheet)
        self.assertIsNotNone(tracker.logger)

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_authenticate_success(self, mock_gspread, mock_creds):
        """Test successful authentication with Google Sheets API."""
        # Mock credentials
        mock_cred_instance = MagicMock()
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance

        # Mock gspread client
        mock_gc = MagicMock()
        mock_gspread.authorize.return_value = mock_gc

        # Create tracker and authenticate
        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.authenticate()

        # Verify authentication
        mock_creds.from_authorized_user_file.assert_called_once_with(self.test_credentials_path)
        mock_gspread.authorize.assert_called_once_with(mock_cred_instance)
        self.assertEqual(tracker.gc, mock_gc)

    @patch('src.approval_tracker.Credentials')
    def test_authenticate_missing_credentials(self, mock_creds):
        """Test authentication failure with missing credentials file."""
        # Mock missing file
        mock_creds.from_authorized_user_file.side_effect = FileNotFoundError('File not found')

        tracker = ApprovalTracker(self.test_credentials_path)

        # Verify exception is raised
        with self.assertRaises(FileNotFoundError):
            tracker.authenticate()

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_authenticate_api_failure(self, mock_gspread, mock_creds):
        """Test authentication failure with API error."""
        # Mock credentials
        mock_cred_instance = MagicMock()
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance

        # Mock API failure
        mock_gspread.authorize.side_effect = Exception('API connection failed')

        tracker = ApprovalTracker(self.test_credentials_path)

        # Verify exception is raised
        with self.assertRaises(Exception):
            tracker.authenticate()

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_create_approval_sheet_success(self, mock_gspread, mock_creds):
        """Test successful creation of approval sheet."""
        # Setup mocks
        mock_cred_instance = MagicMock()
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance

        mock_gc = MagicMock()
        mock_gspread.authorize.return_value = mock_gc

        # Mock spreadsheet creation
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.id = self.test_sheet_id
        mock_sheet = MagicMock()
        mock_sheet.id = 'worksheet_id_123'
        mock_sheet.spreadsheet = mock_spreadsheet
        mock_spreadsheet.sheet1 = mock_sheet
        mock_gc.create.return_value = mock_spreadsheet

        # Create tracker
        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.gc = mock_gc

        # Create approval sheet
        result_sheet_id = tracker.create_approval_sheet(
            sheet_name=self.test_sheet_name,
            email_data_list=self.sample_email_data
        )

        # Verify sheet was created
        mock_gc.create.assert_called_once_with(self.test_sheet_name)
        self.assertEqual(result_sheet_id, self.test_sheet_id)
        self.assertEqual(tracker.sheet, mock_sheet)

        # Verify header row was set
        mock_sheet.update.assert_called()

        # Verify formatting methods were called
        mock_sheet.format.assert_called()
        mock_sheet.freeze.assert_called_once_with(rows=1)
        mock_sheet.columns_auto_resize.assert_called_once()

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_create_approval_sheet_auto_authenticate(self, mock_gspread, mock_creds):
        """Test create_approval_sheet auto-authenticates if not already authenticated."""
        # Setup mocks
        mock_cred_instance = MagicMock()
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance

        mock_gc = MagicMock()
        mock_gspread.authorize.return_value = mock_gc

        mock_spreadsheet = MagicMock()
        mock_spreadsheet.id = self.test_sheet_id
        mock_sheet = MagicMock()
        mock_sheet.id = 'worksheet_id_123'
        mock_sheet.spreadsheet = mock_spreadsheet
        mock_spreadsheet.sheet1 = mock_sheet
        mock_gc.create.return_value = mock_spreadsheet

        # Create tracker WITHOUT authenticating
        tracker = ApprovalTracker(self.test_credentials_path)

        # Create sheet (should trigger authentication)
        result_sheet_id = tracker.create_approval_sheet(
            sheet_name=self.test_sheet_name,
            email_data_list=self.sample_email_data
        )

        # Verify authentication was called
        mock_creds.from_authorized_user_file.assert_called_once()
        mock_gspread.authorize.assert_called_once()
        self.assertEqual(tracker.gc, mock_gc)

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    @patch('src.approval_tracker.datetime')
    def test_populate_sheet(self, mock_datetime, mock_gspread, mock_creds):
        """Test populating sheet with email data."""
        # Mock current time
        mock_now = MagicMock()
        mock_now.strftime.return_value = '2025-01-15 14:30'
        mock_datetime.now.return_value = mock_now

        # Setup mocks
        mock_gc = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_sheet = MagicMock()
        mock_sheet.spreadsheet = mock_spreadsheet
        mock_spreadsheet.sheet1 = mock_sheet
        mock_gc.create.return_value = mock_spreadsheet

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.gc = mock_gc

        # Create sheet
        tracker.create_approval_sheet(
            sheet_name=self.test_sheet_name,
            email_data_list=self.sample_email_data
        )

        # Verify data was populated (check that update was called with rows)
        update_calls = [call for call in mock_sheet.update.call_args_list
                       if 'A2:H' in str(call)]
        self.assertTrue(len(update_calls) > 0)

        # Verify the data structure
        data_call = update_calls[0]
        rows_data = data_call[0][1]  # Second argument is the rows

        self.assertEqual(len(rows_data), 3)  # 3 sample emails

        # Verify first row data
        first_row = rows_data[0]
        self.assertEqual(first_row[0], 'John Doe')  # Client name
        self.assertEqual(first_row[1], 'ABC Corporation')  # Business name
        self.assertEqual(first_row[2], 'john@abccorp.com')  # Email
        self.assertEqual(first_row[3], 'SEO')  # Report type
        self.assertEqual(first_row[4], 'Pending')  # Status (default)
        self.assertEqual(first_row[5], '')  # Notes (empty)
        self.assertEqual(first_row[6], '')  # Extraction errors (none)
        self.assertEqual(first_row[7], '2025-01-15 14:30')  # Generated date

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_populate_sheet_with_empty_data(self, mock_gspread, mock_creds):
        """Test populating sheet with empty email list."""
        # Setup mocks
        mock_gc = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_sheet = MagicMock()
        mock_spreadsheet.sheet1 = mock_sheet
        mock_gc.create.return_value = mock_spreadsheet

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.gc = mock_gc

        # Create sheet with empty data
        tracker.create_approval_sheet(
            sheet_name=self.test_sheet_name,
            email_data_list=[]
        )

        # Verify headers were still set but no data rows
        header_calls = [call for call in mock_sheet.update.call_args_list
                       if 'A1:H1' in str(call)]
        self.assertTrue(len(header_calls) > 0)

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_open_existing_sheet_success(self, mock_gspread, mock_creds):
        """Test opening an existing sheet by ID."""
        # Setup mocks
        mock_cred_instance = MagicMock()
        mock_creds.from_authorized_user_file.return_value = mock_cred_instance

        mock_gc = MagicMock()
        mock_gspread.authorize.return_value = mock_gc

        mock_spreadsheet = MagicMock()
        mock_sheet = MagicMock()
        mock_spreadsheet.sheet1 = mock_sheet
        mock_gc.open_by_key.return_value = mock_spreadsheet

        # Create tracker and authenticate
        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.gc = mock_gc

        # Open existing sheet
        tracker.open_existing_sheet(self.test_sheet_id)

        # Verify sheet was opened
        mock_gc.open_by_key.assert_called_once_with(self.test_sheet_id)
        self.assertEqual(tracker.sheet, mock_sheet)

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_open_existing_sheet_not_found(self, mock_gspread, mock_creds):
        """Test opening non-existent sheet raises error."""
        # Setup mocks
        mock_gc = MagicMock()
        mock_gc.open_by_key.side_effect = Exception('Sheet not found')

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.gc = mock_gc

        # Verify exception is raised
        with self.assertRaises(Exception):
            tracker.open_existing_sheet('invalid_sheet_id')

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_get_approved_clients_success(self, mock_gspread, mock_creds):
        """Test getting list of approved clients."""
        # Mock sheet data
        mock_records = [
            {
                'Client Name': 'John Doe',
                'Business Name': 'ABC Corporation',
                'Status': 'Approved',
                'Email': 'john@abccorp.com'
            },
            {
                'Client Name': 'Sarah Smith',
                'Business Name': 'XYZ Services',
                'Status': 'Pending',
                'Email': 'sarah@xyzservices.com'
            },
            {
                'Client Name': 'Michael Johnson',
                'Business Name': 'Tech Solutions LLC',
                'Status': 'Approved',
                'Email': 'michael@techsolutions.com'
            },
            {
                'Client Name': 'Emily Davis',
                'Business Name': 'Green Earth Landscaping',
                'Status': 'Needs Revision',
                'Email': 'emily@greenearthlandscaping.com'
            }
        ]

        mock_sheet = MagicMock()
        mock_sheet.get_all_records.return_value = mock_records

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        # Get approved clients
        approved = tracker.get_approved_clients()

        # Verify results
        self.assertEqual(len(approved), 2)
        self.assertIn('John Doe', approved)
        self.assertIn('Michael Johnson', approved)
        self.assertNotIn('Sarah Smith', approved)
        self.assertNotIn('Emily Davis', approved)

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_get_approved_clients_no_sheet_open(self, mock_gspread, mock_creds):
        """Test get_approved_clients raises error when no sheet is open."""
        tracker = ApprovalTracker(self.test_credentials_path)
        # Don't set tracker.sheet

        with self.assertRaises(ValueError) as context:
            tracker.get_approved_clients()

        self.assertIn('No sheet is open', str(context.exception))

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_get_approved_clients_empty_list(self, mock_gspread, mock_creds):
        """Test getting approved clients when none are approved."""
        # Mock sheet with no approved clients
        mock_records = [
            {'Client Name': 'John Doe', 'Status': 'Pending'},
            {'Client Name': 'Sarah Smith', 'Status': 'Needs Revision'}
        ]

        mock_sheet = MagicMock()
        mock_sheet.get_all_records.return_value = mock_records

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        approved = tracker.get_approved_clients()

        self.assertEqual(len(approved), 0)

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_get_needs_revision_clients_success(self, mock_gspread, mock_creds):
        """Test getting list of clients needing revision with notes."""
        # Mock sheet data
        mock_records = [
            {
                'Client Name': 'John Doe',
                'Business Name': 'ABC Corporation',
                'Status': 'Approved',
                'Notes': '',
                'Extraction Errors': ''
            },
            {
                'Client Name': 'Sarah Smith',
                'Business Name': 'XYZ Services',
                'Status': 'Needs Revision',
                'Notes': 'Missing conversion data',
                'Extraction Errors': 'Could not parse KPI table'
            },
            {
                'Client Name': 'Emily Davis',
                'Business Name': 'Green Earth Landscaping',
                'Status': 'Needs Revision',
                'Notes': 'Wrong business name',
                'Extraction Errors': ''
            }
        ]

        mock_sheet = MagicMock()
        mock_sheet.get_all_records.return_value = mock_records

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        # Get needs-revision clients
        needs_revision = tracker.get_needs_revision_clients()

        # Verify results
        self.assertEqual(len(needs_revision), 2)

        # Check first revision entry
        self.assertEqual(needs_revision[0]['client_name'], 'Sarah Smith')
        self.assertEqual(needs_revision[0]['business_name'], 'XYZ Services')
        self.assertEqual(needs_revision[0]['notes'], 'Missing conversion data')
        self.assertEqual(needs_revision[0]['errors'], 'Could not parse KPI table')

        # Check second revision entry
        self.assertEqual(needs_revision[1]['client_name'], 'Emily Davis')
        self.assertEqual(needs_revision[1]['business_name'], 'Green Earth Landscaping')
        self.assertEqual(needs_revision[1]['notes'], 'Wrong business name')

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_get_needs_revision_clients_no_sheet_open(self, mock_gspread, mock_creds):
        """Test get_needs_revision_clients raises error when no sheet is open."""
        tracker = ApprovalTracker(self.test_credentials_path)

        with self.assertRaises(ValueError) as context:
            tracker.get_needs_revision_clients()

        self.assertIn('No sheet is open', str(context.exception))

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_get_approval_summary_success(self, mock_gspread, mock_creds):
        """Test getting summary of approval statuses."""
        # Mock sheet data with various statuses
        mock_records = [
            {'Client Name': 'Client 1', 'Status': 'Approved'},
            {'Client Name': 'Client 2', 'Status': 'Approved'},
            {'Client Name': 'Client 3', 'Status': 'Approved'},
            {'Client Name': 'Client 4', 'Status': 'Pending'},
            {'Client Name': 'Client 5', 'Status': 'Pending'},
            {'Client Name': 'Client 6', 'Status': 'Needs Revision'},
        ]

        mock_sheet = MagicMock()
        mock_sheet.get_all_records.return_value = mock_records

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        # Get summary
        summary = tracker.get_approval_summary()

        # Verify counts
        self.assertEqual(summary['total'], 6)
        self.assertEqual(summary['approved'], 3)
        self.assertEqual(summary['pending'], 2)
        self.assertEqual(summary['needs_revision'], 1)

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_get_approval_summary_no_sheet_open(self, mock_gspread, mock_creds):
        """Test get_approval_summary raises error when no sheet is open."""
        tracker = ApprovalTracker(self.test_credentials_path)

        with self.assertRaises(ValueError) as context:
            tracker.get_approval_summary()

        self.assertIn('No sheet is open', str(context.exception))

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_get_approval_summary_empty_sheet(self, mock_gspread, mock_creds):
        """Test getting summary from empty sheet."""
        mock_sheet = MagicMock()
        mock_sheet.get_all_records.return_value = []

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        summary = tracker.get_approval_summary()

        self.assertEqual(summary['total'], 0)
        self.assertEqual(summary['approved'], 0)
        self.assertEqual(summary['pending'], 0)
        self.assertEqual(summary['needs_revision'], 0)

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_update_status_success(self, mock_gspread, mock_creds):
        """Test updating status of a specific client."""
        # Mock finding the client
        mock_cell = MagicMock()
        mock_cell.row = 3  # Client is in row 3

        mock_sheet = MagicMock()
        mock_sheet.find.return_value = mock_cell

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        # Update status
        tracker.update_status(
            client_name='John Doe',
            new_status='Approved',
            notes='Looks good'
        )

        # Verify find was called
        mock_sheet.find.assert_called_once_with('John Doe')

        # Verify batch_update was called with correct values
        mock_sheet.batch_update.assert_called_once()
        update_call = mock_sheet.batch_update.call_args[0][0]

        # Check status update
        self.assertEqual(update_call[0]['range'], 'E3')
        self.assertEqual(update_call[0]['values'], [['Approved']])

        # Check notes update
        self.assertEqual(update_call[1]['range'], 'F3')
        self.assertEqual(update_call[1]['values'], [['Looks good']])

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_update_status_no_sheet_open(self, mock_gspread, mock_creds):
        """Test update_status raises error when no sheet is open."""
        tracker = ApprovalTracker(self.test_credentials_path)

        with self.assertRaises(ValueError) as context:
            tracker.update_status('John Doe', 'Approved')

        self.assertIn('No sheet is open', str(context.exception))

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_update_status_invalid_status(self, mock_gspread, mock_creds):
        """Test update_status raises error for invalid status."""
        mock_sheet = MagicMock()

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        with self.assertRaises(ValueError) as context:
            tracker.update_status('John Doe', 'Invalid Status')

        self.assertIn('Invalid status', str(context.exception))

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_update_status_client_not_found(self, mock_gspread, mock_creds):
        """Test update_status raises error when client not found."""
        mock_sheet = MagicMock()
        mock_sheet.find.return_value = None

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        with self.assertRaises(ValueError) as context:
            tracker.update_status('Nonexistent Client', 'Approved')

        self.assertIn('Client not found', str(context.exception))

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_update_status_to_needs_revision(self, mock_gspread, mock_creds):
        """Test updating status to Needs Revision with notes."""
        mock_cell = MagicMock()
        mock_cell.row = 5

        mock_sheet = MagicMock()
        mock_sheet.find.return_value = mock_cell

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        # Update to needs revision with detailed notes
        tracker.update_status(
            client_name='Sarah Smith',
            new_status='Needs Revision',
            notes='KPI extraction failed for bounce rate. PDF may be corrupted.'
        )

        # Verify update
        update_call = mock_sheet.batch_update.call_args[0][0]
        self.assertEqual(update_call[0]['values'], [['Needs Revision']])
        self.assertEqual(update_call[1]['values'], [['KPI extraction failed for bounce rate. PDF may be corrupted.']])

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_status_constants(self, mock_gspread, mock_creds):
        """Test status constants are properly defined."""
        tracker = ApprovalTracker(self.test_credentials_path)

        self.assertEqual(tracker.STATUS_PENDING, 'Pending')
        self.assertEqual(tracker.STATUS_APPROVED, 'Approved')
        self.assertEqual(tracker.STATUS_NEEDS_REVISION, 'Needs Revision')

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_column_constants(self, mock_gspread, mock_creds):
        """Test column index constants are properly defined."""
        tracker = ApprovalTracker(self.test_credentials_path)

        self.assertEqual(tracker.COL_CLIENT_NAME, 0)
        self.assertEqual(tracker.COL_BUSINESS_NAME, 1)
        self.assertEqual(tracker.COL_EMAIL, 2)
        self.assertEqual(tracker.COL_REPORT_TYPE, 3)
        self.assertEqual(tracker.COL_STATUS, 4)
        self.assertEqual(tracker.COL_NOTES, 5)
        self.assertEqual(tracker.COL_EXTRACTION_ERRORS, 6)
        self.assertEqual(tracker.COL_GENERATED_DATE, 7)

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_create_approval_sheet_api_failure(self, mock_gspread, mock_creds):
        """Test create_approval_sheet handles API failures gracefully."""
        mock_gc = MagicMock()
        mock_gc.create.side_effect = Exception('API quota exceeded')

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.gc = mock_gc

        with self.assertRaises(Exception) as context:
            tracker.create_approval_sheet(
                sheet_name=self.test_sheet_name,
                email_data_list=self.sample_email_data
            )

        self.assertIn('API quota exceeded', str(context.exception))

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_get_approved_clients_api_failure(self, mock_gspread, mock_creds):
        """Test get_approved_clients handles API failures."""
        mock_sheet = MagicMock()
        mock_sheet.get_all_records.side_effect = Exception('Connection timeout')

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        with self.assertRaises(Exception):
            tracker.get_approved_clients()

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_update_status_api_failure(self, mock_gspread, mock_creds):
        """Test update_status handles API failures."""
        mock_cell = MagicMock()
        mock_cell.row = 3

        mock_sheet = MagicMock()
        mock_sheet.find.return_value = mock_cell
        mock_sheet.batch_update.side_effect = Exception('Write permission denied')

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.sheet = mock_sheet

        with self.assertRaises(Exception):
            tracker.update_status('John Doe', 'Approved')

    @patch('src.approval_tracker.Credentials')
    @patch('src.approval_tracker.gspread')
    def test_create_approval_sheet_preserves_email_errors(self, mock_gspread, mock_creds):
        """Test that extraction errors are preserved in approval sheet."""
        # Setup mocks
        mock_gc = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_spreadsheet.id = self.test_sheet_id
        mock_sheet = MagicMock()
        mock_sheet.spreadsheet = mock_spreadsheet
        mock_spreadsheet.sheet1 = mock_sheet
        mock_gc.create.return_value = mock_spreadsheet

        tracker = ApprovalTracker(self.test_credentials_path)
        tracker.gc = mock_gc

        # Email data with errors
        email_data_with_errors = [
            {
                'client_name': 'Problem Client',
                'business_name': 'Failed Extraction Inc',
                'recipient_email': 'client@example.com',
                'report_type': 'SEO',
                'extraction_errors': 'Could not parse KPI table - format changed'
            }
        ]

        # Create sheet
        tracker.create_approval_sheet(
            sheet_name=self.test_sheet_name,
            email_data_list=email_data_with_errors
        )

        # Verify errors were included in the data
        update_calls = [call for call in mock_sheet.update.call_args_list
                       if 'A2:H' in str(call)]
        rows_data = update_calls[0][0][1]

        # Check extraction errors column (index 6)
        self.assertEqual(rows_data[0][6], 'Could not parse KPI table - format changed')


if __name__ == '__main__':
    unittest.main()
