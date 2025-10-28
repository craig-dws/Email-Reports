"""
Unit tests for Approval Workflow module.
"""

import os
import sys
import unittest
import csv
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.approval_workflow import ApprovalWorkflow


class TestApprovalWorkflow(unittest.TestCase):
    """Test cases for ApprovalWorkflow class."""

    def setUp(self):
        """Set up test fixtures with temporary directory."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.tracking_path = Path(self.test_dir) / "test_approval_tracking.csv"

        # Initialize approval workflow
        self.workflow = ApprovalWorkflow(str(self.tracking_path))

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization_creates_csv(self):
        """Test that initialization creates tracking CSV with headers."""
        self.assertTrue(self.tracking_path.exists())

        # Verify headers
        with open(self.tracking_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)

        expected_headers = [
            'ClientID',
            'BusinessName',
            'EmailSubject',
            'Status',
            'Notes',
            'ExtractionErrors',
            'CreatedDate',
            'UpdatedDate'
        ]
        self.assertEqual(headers, expected_headers)

    def test_add_for_review_without_errors(self):
        """Test adding an email for review without extraction errors."""
        self.workflow.add_for_review(
            client_id='1',
            business_name='ABC Corporation',
            email_subject='Your January 2025 SEO Report'
        )

        reviews = self.workflow.get_all_reviews()
        self.assertEqual(len(reviews), 1)

        review = reviews[0]
        self.assertEqual(review['ClientID'], '1')
        self.assertEqual(review['BusinessName'], 'ABC Corporation')
        self.assertEqual(review['EmailSubject'], 'Your January 2025 SEO Report')
        self.assertEqual(review['Status'], ApprovalWorkflow.STATUS_PENDING)
        self.assertEqual(review['ExtractionErrors'], '')

    def test_add_for_review_with_errors(self):
        """Test adding an email with extraction errors."""
        errors = ['Missing bounce rate', 'Business name not in database']

        self.workflow.add_for_review(
            client_id='2',
            business_name='XYZ Services',
            email_subject='Your January 2025 Google Ads Report',
            extraction_errors=errors
        )

        reviews = self.workflow.get_all_reviews()
        self.assertEqual(len(reviews), 1)

        review = reviews[0]
        self.assertEqual(review['Status'], ApprovalWorkflow.STATUS_NEEDS_REVISION)
        self.assertEqual(review['ExtractionErrors'], 'Missing bounce rate; Business name not in database')

    def test_add_multiple_reviews(self):
        """Test adding multiple reviews."""
        self.workflow.add_for_review(
            client_id='1',
            business_name='ABC Corporation',
            email_subject='Your January 2025 SEO Report'
        )
        self.workflow.add_for_review(
            client_id='2',
            business_name='XYZ Services',
            email_subject='Your January 2025 Google Ads Report'
        )

        reviews = self.workflow.get_all_reviews()
        self.assertEqual(len(reviews), 2)

    def test_get_approved_reviews(self):
        """Test getting only approved reviews."""
        # Add several reviews with different statuses
        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')
        self.workflow.add_for_review('2', 'XYZ Inc', 'Subject 2')
        self.workflow.add_for_review('3', 'DEF LLC', 'Subject 3')

        # Update statuses
        self.workflow.update_status('1', ApprovalWorkflow.STATUS_APPROVED)
        self.workflow.update_status('2', ApprovalWorkflow.STATUS_NEEDS_REVISION)
        self.workflow.update_status('3', ApprovalWorkflow.STATUS_APPROVED)

        approved = self.workflow.get_approved_reviews()
        self.assertEqual(len(approved), 2)

        approved_ids = [r['ClientID'] for r in approved]
        self.assertIn('1', approved_ids)
        self.assertIn('3', approved_ids)

    def test_get_pending_reviews(self):
        """Test getting pending reviews (including needs revision)."""
        # Add several reviews
        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')
        self.workflow.add_for_review('2', 'XYZ Inc', 'Subject 2', ['Error'])
        self.workflow.add_for_review('3', 'DEF LLC', 'Subject 3')

        # Update one to approved
        self.workflow.update_status('1', ApprovalWorkflow.STATUS_APPROVED)

        pending = self.workflow.get_pending_reviews()
        self.assertEqual(len(pending), 2)

        # Should include both PENDING and NEEDS_REVISION
        statuses = [r['Status'] for r in pending]
        self.assertIn(ApprovalWorkflow.STATUS_PENDING, statuses)
        self.assertIn(ApprovalWorkflow.STATUS_NEEDS_REVISION, statuses)

    def test_update_status(self):
        """Test updating review status."""
        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')

        # Update status
        self.workflow.update_status(
            '1',
            ApprovalWorkflow.STATUS_APPROVED,
            'Looks good!'
        )

        reviews = self.workflow.get_all_reviews()
        review = reviews[0]

        self.assertEqual(review['Status'], ApprovalWorkflow.STATUS_APPROVED)
        self.assertEqual(review['Notes'], 'Looks good!')

    def test_update_status_nonexistent_client(self):
        """Test updating status for nonexistent client ID."""
        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')

        # Try to update nonexistent client (should not raise error)
        self.workflow.update_status('999', ApprovalWorkflow.STATUS_APPROVED)

        # Original review should be unchanged
        reviews = self.workflow.get_all_reviews()
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['Status'], ApprovalWorkflow.STATUS_PENDING)

    def test_clear_tracking(self):
        """Test clearing all tracking entries."""
        # Add multiple reviews
        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')
        self.workflow.add_for_review('2', 'XYZ Inc', 'Subject 2')

        # Clear tracking
        self.workflow.clear_tracking()

        # Should have no reviews (only headers)
        reviews = self.workflow.get_all_reviews()
        self.assertEqual(len(reviews), 0)

    def test_get_summary(self):
        """Test getting summary statistics."""
        # Add reviews with different statuses
        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')
        self.workflow.add_for_review('2', 'XYZ Inc', 'Subject 2')
        self.workflow.add_for_review('3', 'DEF LLC', 'Subject 3', ['Error'])
        self.workflow.add_for_review('4', 'GHI Ltd', 'Subject 4')

        # Update statuses
        self.workflow.update_status('1', ApprovalWorkflow.STATUS_APPROVED)
        self.workflow.update_status('2', ApprovalWorkflow.STATUS_APPROVED)
        self.workflow.update_status('4', ApprovalWorkflow.STATUS_SENT)

        summary = self.workflow.get_summary()

        self.assertEqual(summary['total'], 4)
        self.assertEqual(summary['approved'], 2)
        self.assertEqual(summary['pending'], 0)
        self.assertEqual(summary['needs_revision'], 1)
        self.assertEqual(summary['sent'], 1)

    def test_get_summary_empty(self):
        """Test summary with no reviews."""
        summary = self.workflow.get_summary()

        self.assertEqual(summary['total'], 0)
        self.assertEqual(summary['approved'], 0)
        self.assertEqual(summary['pending'], 0)
        self.assertEqual(summary['needs_revision'], 0)
        self.assertEqual(summary['sent'], 0)

    def test_export_review_html(self):
        """Test exporting review tracking to HTML."""
        # Add some test data
        self.workflow.add_for_review(
            '1',
            'ABC Corporation',
            'Your January 2025 SEO Report'
        )
        self.workflow.add_for_review(
            '2',
            'XYZ Services',
            'Your January 2025 Google Ads Report',
            ['Missing conversion data']
        )

        # Export to HTML
        html_path = Path(self.test_dir) / "test_review.html"
        self.workflow.export_review_html(str(html_path))

        # Verify file exists
        self.assertTrue(html_path.exists())

        # Verify HTML contains expected content
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        self.assertIn('ABC Corporation', html_content)
        self.assertIn('XYZ Services', html_content)
        self.assertIn('Pending', html_content)
        self.assertIn('Needs Revision', html_content)
        self.assertIn('Missing conversion data', html_content)

    def test_timestamps_created(self):
        """Test that timestamps are created for new reviews."""
        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')

        reviews = self.workflow.get_all_reviews()
        review = reviews[0]

        # Verify timestamps exist and are valid
        self.assertTrue(review['CreatedDate'])
        self.assertTrue(review['UpdatedDate'])

        # Verify timestamp format (YYYY-MM-DD HH:MM:SS)
        created_date = datetime.strptime(review['CreatedDate'], '%Y-%m-%d %H:%M:%S')
        updated_date = datetime.strptime(review['UpdatedDate'], '%Y-%m-%d %H:%M:%S')

        self.assertIsInstance(created_date, datetime)
        self.assertIsInstance(updated_date, datetime)

    def test_timestamp_updated_on_status_change(self):
        """Test that UpdatedDate changes when status is updated."""
        import time

        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')

        reviews = self.workflow.get_all_reviews()
        original_updated = reviews[0]['UpdatedDate']

        # Wait a moment to ensure different timestamp
        time.sleep(0.1)

        # Update status
        self.workflow.update_status('1', ApprovalWorkflow.STATUS_APPROVED)

        reviews = self.workflow.get_all_reviews()
        new_updated = reviews[0]['UpdatedDate']

        # Updated timestamp should be different
        self.assertNotEqual(original_updated, new_updated)

    def test_empty_extraction_errors_list(self):
        """Test handling empty extraction errors list."""
        self.workflow.add_for_review(
            '1',
            'ABC Corp',
            'Subject 1',
            []  # Empty list
        )

        reviews = self.workflow.get_all_reviews()
        review = reviews[0]

        self.assertEqual(review['ExtractionErrors'], '')
        self.assertEqual(review['Status'], ApprovalWorkflow.STATUS_PENDING)

    def test_status_constants(self):
        """Test that status constants are defined."""
        self.assertEqual(ApprovalWorkflow.STATUS_PENDING, "Pending")
        self.assertEqual(ApprovalWorkflow.STATUS_APPROVED, "Approved")
        self.assertEqual(ApprovalWorkflow.STATUS_NEEDS_REVISION, "Needs Revision")
        self.assertEqual(ApprovalWorkflow.STATUS_SENT, "Sent")

    def test_multiple_status_updates(self):
        """Test updating status multiple times."""
        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')

        # Update to Approved
        self.workflow.update_status('1', ApprovalWorkflow.STATUS_APPROVED)
        reviews = self.workflow.get_all_reviews()
        self.assertEqual(reviews[0]['Status'], ApprovalWorkflow.STATUS_APPROVED)

        # Update to Needs Revision
        self.workflow.update_status('1', ApprovalWorkflow.STATUS_NEEDS_REVISION, 'Found issue')
        reviews = self.workflow.get_all_reviews()
        self.assertEqual(reviews[0]['Status'], ApprovalWorkflow.STATUS_NEEDS_REVISION)
        self.assertEqual(reviews[0]['Notes'], 'Found issue')

        # Update to Sent
        self.workflow.update_status('1', ApprovalWorkflow.STATUS_SENT)
        reviews = self.workflow.get_all_reviews()
        self.assertEqual(reviews[0]['Status'], ApprovalWorkflow.STATUS_SENT)

    def test_special_characters_in_data(self):
        """Test handling special characters in business names and subjects."""
        self.workflow.add_for_review(
            '1',
            'ABC Corporation & Co., Ltd.',
            'Your "January" 2025 SEO Report'
        )

        reviews = self.workflow.get_all_reviews()
        review = reviews[0]

        self.assertEqual(review['BusinessName'], 'ABC Corporation & Co., Ltd.')
        self.assertEqual(review['EmailSubject'], 'Your "January" 2025 SEO Report')

    def test_unicode_characters(self):
        """Test handling Unicode characters."""
        self.workflow.add_for_review(
            '1',
            'Café Münchën',
            'Your Résumé Report'
        )

        reviews = self.workflow.get_all_reviews()
        review = reviews[0]

        self.assertEqual(review['BusinessName'], 'Café Münchën')
        self.assertEqual(review['EmailSubject'], 'Your Résumé Report')

    def test_get_all_reviews_empty(self):
        """Test getting all reviews when none exist."""
        reviews = self.workflow.get_all_reviews()
        self.assertEqual(len(reviews), 0)
        self.assertIsInstance(reviews, list)

    def test_workflow_initialization_existing_file(self):
        """Test initialization when tracking file already exists."""
        # Create a file with existing data
        self.workflow.add_for_review('1', 'ABC Corp', 'Subject 1')

        # Create new workflow instance with same path
        workflow2 = ApprovalWorkflow(str(self.tracking_path))

        # Should read existing data
        reviews = workflow2.get_all_reviews()
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]['BusinessName'], 'ABC Corp')


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
