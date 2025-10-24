"""
Approval Workflow Module.
Manages CSV-based email approval tracking.
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from .logger import get_logger

logger = get_logger('ApprovalWorkflow')


class ApprovalWorkflow:
    """Manages email approval tracking via CSV."""

    STATUS_PENDING = "Pending"
    STATUS_APPROVED = "Approved"
    STATUS_NEEDS_REVISION = "Needs Revision"
    STATUS_SENT = "Sent"

    def __init__(self, tracking_csv_path: str):
        """
        Initialize approval workflow.

        Args:
            tracking_csv_path: Path to approval tracking CSV file
        """
        self.tracking_path = Path(tracking_csv_path)
        self.logger = logger

        # Ensure tracking file exists with headers
        if not self.tracking_path.exists():
            self._create_tracking_file()

    def _create_tracking_file(self):
        """Create approval tracking CSV with headers."""
        self.tracking_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.tracking_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ClientID',
                'BusinessName',
                'EmailSubject',
                'Status',
                'Notes',
                'ExtractionErrors',
                'CreatedDate',
                'UpdatedDate'
            ])

        self.logger.info(f"Created approval tracking file: {self.tracking_path}")

    def add_for_review(
        self,
        client_id: str,
        business_name: str,
        email_subject: str,
        extraction_errors: List[str] = None
    ):
        """
        Add an email to the approval tracking list.

        Args:
            client_id: Client ID
            business_name: Business name
            email_subject: Email subject line
            extraction_errors: List of extraction errors (if any)
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            errors_str = '; '.join(extraction_errors) if extraction_errors else ''

            # Determine initial status
            status = self.STATUS_NEEDS_REVISION if extraction_errors else self.STATUS_PENDING

            with open(self.tracking_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    client_id,
                    business_name,
                    email_subject,
                    status,
                    '',  # Notes (empty initially)
                    errors_str,
                    timestamp,
                    timestamp
                ])

            self.logger.info(f"Added to review: {business_name} - Status: {status}")

        except Exception as e:
            self.logger.error(f"Failed to add to review tracking: {str(e)}")
            raise

    def get_all_reviews(self) -> List[Dict]:
        """
        Get all review entries.

        Returns:
            List of review dictionaries
        """
        reviews = []

        try:
            with open(self.tracking_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                reviews = list(reader)

            return reviews

        except Exception as e:
            self.logger.error(f"Failed to read review tracking: {str(e)}")
            raise

    def get_approved_reviews(self) -> List[Dict]:
        """
        Get all approved reviews.

        Returns:
            List of approved review dictionaries
        """
        all_reviews = self.get_all_reviews()
        approved = [r for r in all_reviews if r['Status'] == self.STATUS_APPROVED]

        self.logger.info(f"Found {len(approved)} approved emails")
        return approved

    def get_pending_reviews(self) -> List[Dict]:
        """
        Get all pending reviews.

        Returns:
            List of pending review dictionaries
        """
        all_reviews = self.get_all_reviews()
        pending = [
            r for r in all_reviews
            if r['Status'] in [self.STATUS_PENDING, self.STATUS_NEEDS_REVISION]
        ]

        self.logger.info(f"Found {len(pending)} pending reviews")
        return pending

    def update_status(self, client_id: str, new_status: str, notes: str = ""):
        """
        Update the status of a review entry.

        Args:
            client_id: Client ID to update
            new_status: New status value
            notes: Optional notes
        """
        try:
            all_reviews = []

            # Read all reviews
            with open(self.tracking_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                all_reviews = list(reader)

            # Update the matching review
            updated = False
            for review in all_reviews:
                if review['ClientID'] == str(client_id):
                    review['Status'] = new_status
                    if notes:
                        review['Notes'] = notes
                    review['UpdatedDate'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    updated = True
                    break

            if not updated:
                self.logger.warning(f"Client ID {client_id} not found in tracking")
                return

            # Write back
            with open(self.tracking_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_reviews)

            self.logger.info(f"Updated status for Client ID {client_id} to {new_status}")

        except Exception as e:
            self.logger.error(f"Failed to update status: {str(e)}")
            raise

    def clear_tracking(self):
        """Clear all tracking entries (start fresh for new month)."""
        self._create_tracking_file()
        self.logger.info("Cleared approval tracking for new run")

    def get_summary(self) -> Dict:
        """
        Get summary statistics.

        Returns:
            Dictionary with counts by status
        """
        all_reviews = self.get_all_reviews()

        summary = {
            'total': len(all_reviews),
            'approved': 0,
            'pending': 0,
            'needs_revision': 0,
            'sent': 0
        }

        for review in all_reviews:
            status = review['Status']
            if status == self.STATUS_APPROVED:
                summary['approved'] += 1
            elif status == self.STATUS_PENDING:
                summary['pending'] += 1
            elif status == self.STATUS_NEEDS_REVISION:
                summary['needs_revision'] += 1
            elif status == self.STATUS_SENT:
                summary['sent'] += 1

        return summary

    def export_review_html(self, output_path: str):
        """
        Export review tracking to an HTML file for easier viewing.

        Args:
            output_path: Path to save HTML file
        """
        all_reviews = self.get_all_reviews()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Email Approval Tracking</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th { background: #f4f4f4; padding: 12px; text-align: left; border: 1px solid #ddd; }
                td { padding: 10px; border: 1px solid #ddd; }
                tr:nth-child(even) { background: #f9f9f9; }
                .approved { background: #d4edda !important; }
                .pending { background: #fff3cd !important; }
                .needs-revision { background: #f8d7da !important; }
                .sent { background: #d1ecf1 !important; }
            </style>
        </head>
        <body>
            <h1>Email Approval Tracking</h1>
            <table>
                <thead>
                    <tr>
                        <th>Client ID</th>
                        <th>Business Name</th>
                        <th>Email Subject</th>
                        <th>Status</th>
                        <th>Notes</th>
                        <th>Extraction Errors</th>
                        <th>Updated</th>
                    </tr>
                </thead>
                <tbody>
        """

        for review in all_reviews:
            status = review['Status']
            row_class = status.lower().replace(' ', '-')

            html += f"""
                    <tr class="{row_class}">
                        <td>{review['ClientID']}</td>
                        <td>{review['BusinessName']}</td>
                        <td>{review['EmailSubject']}</td>
                        <td><strong>{status}</strong></td>
                        <td>{review.get('Notes', '')}</td>
                        <td>{review.get('ExtractionErrors', '')}</td>
                        <td>{review.get('UpdatedDate', '')}</td>
                    </tr>
            """

        html += """
                </tbody>
            </table>
        </body>
        </html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        self.logger.info(f"Exported review tracking to HTML: {output_path}")
