"""
Approval Tracker Module - Google Sheets Integration
Manages email approval workflow using Google Sheets for collaborative review.
"""

import gspread
from google.oauth2.credentials import Credentials
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from .logger import get_logger

logger = get_logger('ApprovalTracker')


class ApprovalTracker:
    """Manages email approval tracking using Google Sheets."""

    # Status values
    STATUS_PENDING = 'Pending'
    STATUS_APPROVED = 'Approved'
    STATUS_NEEDS_REVISION = 'Needs Revision'

    # Column indices (0-based)
    COL_CLIENT_NAME = 0
    COL_BUSINESS_NAME = 1
    COL_EMAIL = 2
    COL_REPORT_TYPE = 3
    COL_STATUS = 4
    COL_NOTES = 5
    COL_EXTRACTION_ERRORS = 6
    COL_GENERATED_DATE = 7

    def __init__(self, credentials_path: str = 'token.json'):
        """
        Initialize approval tracker with Google Sheets authentication.

        Args:
            credentials_path: Path to OAuth token file
        """
        self.credentials_path = credentials_path
        self.logger = logger
        self.gc = None
        self.sheet = None

    def authenticate(self):
        """Authenticate with Google Sheets API using OAuth credentials."""
        try:
            creds = Credentials.from_authorized_user_file(self.credentials_path)
            self.gc = gspread.authorize(creds)
            self.logger.info("Successfully authenticated with Google Sheets API")
        except FileNotFoundError:
            self.logger.error(f"Credentials file not found: {self.credentials_path}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to authenticate with Google Sheets: {e}")
            raise

    def create_approval_sheet(
        self,
        sheet_name: str,
        email_data_list: List[Dict]
    ) -> str:
        """
        Create a new Google Sheet for approval tracking.

        Args:
            sheet_name: Name for the new sheet (e.g., "Email Approvals - January 2025")
            email_data_list: List of generated email data dictionaries

        Returns:
            Sheet ID (can be used to construct URL)
        """
        if not self.gc:
            self.authenticate()

        try:
            # Create new spreadsheet
            spreadsheet = self.gc.create(sheet_name)
            self.sheet = spreadsheet.sheet1
            sheet_id = spreadsheet.id

            self.logger.info(f"Created approval sheet: {sheet_name} (ID: {sheet_id})")

            # Set up headers
            headers = [
                'Client Name',
                'Business Name',
                'Email',
                'Report Type',
                'Status',
                'Notes',
                'Extraction Errors',
                'Generated Date'
            ]
            self.sheet.update('A1:H1', [headers])

            # Format header row
            self.sheet.format('A1:H1', {
                'backgroundColor': {'red': 0.2, 'green': 0.3, 'blue': 0.4},
                'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True},
                'horizontalAlignment': 'CENTER'
            })

            # Populate with email data
            self._populate_sheet(email_data_list)

            # Add data validation for Status column
            self._add_status_validation()

            # Add conditional formatting
            self._add_conditional_formatting()

            # Freeze header row
            self.sheet.freeze(rows=1)

            # Auto-resize columns
            self.sheet.columns_auto_resize(0, 7)

            # Share with user (make them owner)
            # spreadsheet.share(None, perm_type='anyone', role='writer')

            sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
            self.logger.info(f"Approval sheet ready: {sheet_url}")

            return sheet_id

        except Exception as e:
            self.logger.error(f"Failed to create approval sheet: {e}")
            raise

    def _populate_sheet(self, email_data_list: List[Dict]):
        """
        Populate sheet with email data.

        Args:
            email_data_list: List of email data dictionaries
        """
        if not email_data_list:
            self.logger.warning("No email data to populate")
            return

        rows = []
        generated_date = datetime.now().strftime('%Y-%m-%d %H:%M')

        for email_data in email_data_list:
            rows.append([
                email_data.get('client_name', ''),
                email_data.get('business_name', ''),
                email_data.get('recipient_email', ''),
                email_data.get('report_type', ''),
                self.STATUS_PENDING,  # Default status
                '',  # Notes (empty)
                email_data.get('extraction_errors', ''),
                generated_date
            ])

        # Update all rows at once (more efficient)
        self.sheet.update(f'A2:H{len(rows) + 1}', rows)
        self.logger.info(f"Populated {len(rows)} emails in approval sheet")

    def _add_status_validation(self):
        """Add dropdown validation for Status column."""
        try:
            # Get the sheet for data validation
            worksheet = self.sheet

            # Define validation rule for Status column (E)
            validation_rule = {
                'condition': {
                    'type': 'ONE_OF_LIST',
                    'values': [
                        {'userEnteredValue': self.STATUS_PENDING},
                        {'userEnteredValue': self.STATUS_APPROVED},
                        {'userEnteredValue': self.STATUS_NEEDS_REVISION}
                    ]
                },
                'showCustomUi': True,
                'strict': True
            }

            # Apply to all rows in Status column (E2:E1000)
            worksheet.set_data_validation('E2:E1000', validation_rule)
            self.logger.info("Added status dropdown validation")

        except Exception as e:
            self.logger.warning(f"Could not add data validation: {e}")

    def _add_conditional_formatting(self):
        """Add conditional formatting for status colors."""
        try:
            # Green for Approved
            approved_rule = {
                'ranges': [{'sheetId': self.sheet.id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 4, 'endColumnIndex': 5}],
                'booleanRule': {
                    'condition': {
                        'type': 'TEXT_EQ',
                        'values': [{'userEnteredValue': self.STATUS_APPROVED}]
                    },
                    'format': {
                        'backgroundColor': {'red': 0.7, 'green': 0.9, 'blue': 0.7}
                    }
                }
            }

            # Yellow for Pending
            pending_rule = {
                'ranges': [{'sheetId': self.sheet.id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 4, 'endColumnIndex': 5}],
                'booleanRule': {
                    'condition': {
                        'type': 'TEXT_EQ',
                        'values': [{'userEnteredValue': self.STATUS_PENDING}]
                    },
                    'format': {
                        'backgroundColor': {'red': 1, 'green': 0.95, 'blue': 0.7}
                    }
                }
            }

            # Red for Needs Revision
            needs_revision_rule = {
                'ranges': [{'sheetId': self.sheet.id, 'startRowIndex': 1, 'endRowIndex': 1000, 'startColumnIndex': 4, 'endColumnIndex': 5}],
                'booleanRule': {
                    'condition': {
                        'type': 'TEXT_EQ',
                        'values': [{'userEnteredValue': self.STATUS_NEEDS_REVISION}]
                    },
                    'format': {
                        'backgroundColor': {'red': 0.95, 'green': 0.7, 'blue': 0.7}
                    }
                }
            }

            # Apply rules
            spreadsheet = self.gc.open_by_key(self.sheet.spreadsheet.id)
            requests = [
                {'addConditionalFormatRule': {'rule': approved_rule, 'index': 0}},
                {'addConditionalFormatRule': {'rule': pending_rule, 'index': 1}},
                {'addConditionalFormatRule': {'rule': needs_revision_rule, 'index': 2}}
            ]
            spreadsheet.batch_update({'requests': requests})

            self.logger.info("Added conditional formatting")

        except Exception as e:
            self.logger.warning(f"Could not add conditional formatting: {e}")

    def open_existing_sheet(self, sheet_id: str):
        """
        Open an existing approval sheet by ID.

        Args:
            sheet_id: Google Sheets ID
        """
        if not self.gc:
            self.authenticate()

        try:
            spreadsheet = self.gc.open_by_key(sheet_id)
            self.sheet = spreadsheet.sheet1
            self.logger.info(f"Opened existing sheet: {sheet_id}")
        except Exception as e:
            self.logger.error(f"Failed to open sheet {sheet_id}: {e}")
            raise

    def get_approved_clients(self) -> List[str]:
        """
        Get list of approved client names.

        Returns:
            List of client names with 'Approved' status
        """
        if not self.sheet:
            raise ValueError("No sheet is open. Call open_existing_sheet() first.")

        try:
            # Get all records
            records = self.sheet.get_all_records()

            approved = []
            for record in records:
                if record.get('Status') == self.STATUS_APPROVED:
                    client_name = record.get('Client Name', '').strip()
                    if client_name:
                        approved.append(client_name)

            self.logger.info(f"Found {len(approved)} approved clients")
            return approved

        except Exception as e:
            self.logger.error(f"Failed to get approved clients: {e}")
            raise

    def get_needs_revision_clients(self) -> List[Dict]:
        """
        Get list of clients needing revision with notes.

        Returns:
            List of dictionaries with client info and notes
        """
        if not self.sheet:
            raise ValueError("No sheet is open. Call open_existing_sheet() first.")

        try:
            records = self.sheet.get_all_records()

            needs_revision = []
            for record in records:
                if record.get('Status') == self.STATUS_NEEDS_REVISION:
                    needs_revision.append({
                        'client_name': record.get('Client Name', ''),
                        'business_name': record.get('Business Name', ''),
                        'notes': record.get('Notes', ''),
                        'errors': record.get('Extraction Errors', '')
                    })

            self.logger.info(f"Found {len(needs_revision)} clients needing revision")
            return needs_revision

        except Exception as e:
            self.logger.error(f"Failed to get needs-revision clients: {e}")
            raise

    def get_approval_summary(self) -> Dict:
        """
        Get summary of approval statuses.

        Returns:
            Dictionary with counts for each status
        """
        if not self.sheet:
            raise ValueError("No sheet is open. Call open_existing_sheet() first.")

        try:
            records = self.sheet.get_all_records()

            summary = {
                'total': len(records),
                'approved': 0,
                'pending': 0,
                'needs_revision': 0
            }

            for record in records:
                status = record.get('Status', '')
                if status == self.STATUS_APPROVED:
                    summary['approved'] += 1
                elif status == self.STATUS_PENDING:
                    summary['pending'] += 1
                elif status == self.STATUS_NEEDS_REVISION:
                    summary['needs_revision'] += 1

            return summary

        except Exception as e:
            self.logger.error(f"Failed to get approval summary: {e}")
            raise

    def update_status(self, client_name: str, new_status: str, notes: str = ''):
        """
        Update the status of a specific client.

        Args:
            client_name: Name of client to update
            new_status: New status value
            notes: Optional notes
        """
        if not self.sheet:
            raise ValueError("No sheet is open. Call open_existing_sheet() first.")

        if new_status not in [self.STATUS_PENDING, self.STATUS_APPROVED, self.STATUS_NEEDS_REVISION]:
            raise ValueError(f"Invalid status: {new_status}")

        try:
            # Find the row
            cell = self.sheet.find(client_name)
            if not cell:
                raise ValueError(f"Client not found: {client_name}")

            row = cell.row

            # Update status and notes
            updates = [
                {'range': f'E{row}', 'values': [[new_status]]},
                {'range': f'F{row}', 'values': [[notes]]}
            ]
            self.sheet.batch_update(updates)

            self.logger.info(f"Updated {client_name} status to {new_status}")

        except Exception as e:
            self.logger.error(f"Failed to update status for {client_name}: {e}")
            raise
