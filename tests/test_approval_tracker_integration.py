"""
Integration test for Approval Tracker Module.
Tests actual Google Sheets API interactions (requires valid credentials and token).

Usage:
    python tests/test_approval_tracker_integration.py

Note: This test will create actual Google Sheets and modify them.
      Use with caution and ensure you have proper Google Sheets API access.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.approval_tracker import ApprovalTracker
from src.logger import get_logger

logger = get_logger('ApprovalTrackerIntegrationTest')


def test_create_approval_sheet():
    """Test creating a new approval sheet with sample data."""
    logger.info("=" * 60)
    logger.info("Test 1: Create Approval Sheet")
    logger.info("=" * 60)

    try:
        # Initialize tracker
        tracker = ApprovalTracker(token_path='token.json')
        tracker.authenticate()

        # Sample email data
        email_data_list = [
            {
                'client_name': 'John Smith',
                'business_name': 'ABC Corporation',
                'recipient_email': 'john@abccorp.com',
                'report_type': 'SEO',
                'extraction_errors': ''
            },
            {
                'client_name': 'Sarah Johnson',
                'business_name': 'XYZ Services',
                'recipient_email': 'sarah@xyzservices.com',
                'report_type': 'SEM',
                'extraction_errors': ''
            },
            {
                'client_name': 'Michael Brown',
                'business_name': 'Tech Solutions LLC',
                'recipient_email': 'michael@techsolutions.com',
                'report_type': 'SEO',
                'extraction_errors': 'Missing bounce rate metric'
            }
        ]

        # Create sheet
        current_month = datetime.now().strftime('%B %Y')
        sheet_name = f"[TEST] Email Approvals - {current_month}"

        logger.info(f"Creating approval sheet: {sheet_name}")
        sheet_id = tracker.create_approval_sheet(sheet_name, email_data_list)

        logger.info(f"✅ Sheet created successfully!")
        logger.info(f"   Sheet ID: {sheet_id}")
        logger.info(f"   URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
        logger.info(f"   Populated with {len(email_data_list)} test emails")
        logger.info(f"   Check the sheet to verify formatting and data")

        return sheet_id

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return None


def test_read_approval_status(sheet_id: str):
    """Test reading approval status from existing sheet."""
    logger.info("=" * 60)
    logger.info("Test 2: Read Approval Status")
    logger.info("=" * 60)

    if not sheet_id:
        logger.warning("⚠️  No sheet ID provided, skipping test")
        return False

    try:
        # Initialize tracker
        tracker = ApprovalTracker(token_path='token.json')
        tracker.authenticate()

        # Open existing sheet
        logger.info(f"Opening sheet: {sheet_id}")
        tracker.open_existing_sheet(sheet_id)

        # Get approval summary
        summary = tracker.get_approval_summary()

        logger.info(f"✅ Successfully read approval status!")
        logger.info(f"   Total emails: {summary['total']}")
        logger.info(f"   Approved: {summary['approved']}")
        logger.info(f"   Pending: {summary['pending']}")
        logger.info(f"   Needs Revision: {summary['needs_revision']}")

        # Get approved clients
        approved = tracker.get_approved_clients()
        if approved:
            logger.info(f"   Approved clients: {', '.join(approved)}")
        else:
            logger.info(f"   No clients approved yet")

        # Get needs revision clients
        needs_revision = tracker.get_needs_revision_clients()
        if needs_revision:
            logger.info(f"   Clients needing revision:")
            for client in needs_revision:
                logger.info(f"     - {client['client_name']}: {client['notes']}")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_update_status(sheet_id: str):
    """Test updating approval status for a client."""
    logger.info("=" * 60)
    logger.info("Test 3: Update Approval Status")
    logger.info("=" * 60)

    if not sheet_id:
        logger.warning("⚠️  No sheet ID provided, skipping test")
        return False

    logger.warning("⚠️  This test will modify the Google Sheet!")
    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("Test skipped by user.")
        return True

    try:
        # Initialize tracker
        tracker = ApprovalTracker(token_path='token.json')
        tracker.authenticate()

        # Open existing sheet
        tracker.open_existing_sheet(sheet_id)

        # Update first client to Approved
        logger.info("Updating 'John Smith' status to Approved")
        tracker.update_status(
            client_name='John Smith',
            new_status=tracker.STATUS_APPROVED,
            notes='Test approval - email looks good'
        )

        # Update third client to Needs Revision
        logger.info("Updating 'Michael Brown' status to Needs Revision")
        tracker.update_status(
            client_name='Michael Brown',
            new_status=tracker.STATUS_NEEDS_REVISION,
            notes='Missing bounce rate - need to re-extract PDF'
        )

        # Get updated summary
        summary = tracker.get_approval_summary()

        logger.info(f"✅ Successfully updated statuses!")
        logger.info(f"   Updated summary:")
        logger.info(f"   Approved: {summary['approved']}")
        logger.info(f"   Pending: {summary['pending']}")
        logger.info(f"   Needs Revision: {summary['needs_revision']}")
        logger.info(f"   Check the sheet to verify color formatting")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_get_approved_list(sheet_id: str):
    """Test getting list of approved clients for draft creation."""
    logger.info("=" * 60)
    logger.info("Test 4: Get Approved Clients List")
    logger.info("=" * 60)

    if not sheet_id:
        logger.warning("⚠️  No sheet ID provided, skipping test")
        return False

    try:
        # Initialize tracker
        tracker = ApprovalTracker(token_path='token.json')
        tracker.authenticate()

        # Open existing sheet
        tracker.open_existing_sheet(sheet_id)

        # Get approved clients
        approved = tracker.get_approved_clients()

        logger.info(f"✅ Retrieved approved clients list!")
        logger.info(f"   Total approved: {len(approved)}")

        if approved:
            logger.info(f"   Ready for draft creation:")
            for client_name in approved:
                logger.info(f"     - {client_name}")
        else:
            logger.info(f"   No clients approved yet")
            logger.info(f"   Approve some clients in the sheet and run this test again")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_workflow_simulation():
    """Test complete approval workflow simulation."""
    logger.info("=" * 60)
    logger.info("Test 5: Complete Workflow Simulation")
    logger.info("=" * 60)

    try:
        # Initialize tracker
        tracker = ApprovalTracker(token_path='token.json')
        tracker.authenticate()

        # Step 1: Create approval sheet
        logger.info("Step 1: Creating approval sheet with 5 test emails")
        email_data_list = [
            {
                'client_name': f'Client {i}',
                'business_name': f'Business {i} Inc',
                'recipient_email': f'client{i}@example.com',
                'report_type': 'SEO' if i % 2 == 0 else 'SEM',
                'extraction_errors': 'Missing conversion data' if i == 4 else ''
            }
            for i in range(1, 6)
        ]

        current_month = datetime.now().strftime('%B %Y')
        sheet_name = f"[TEST WORKFLOW] Approvals - {current_month}"
        sheet_id = tracker.create_approval_sheet(sheet_name, email_data_list)

        logger.info(f"   Created sheet: {sheet_id}")
        logger.info(f"   URL: https://docs.google.com/spreadsheets/d/{sheet_id}")

        # Step 2: Simulate user review
        logger.info("\nStep 2: Simulating user review and approvals")
        logger.info("   (In real workflow, user would manually update sheet)")

        logger.warning("\n⚠️  Please update the sheet manually now:")
        logger.info("   1. Open the URL above")
        logger.info("   2. Change some statuses to 'Approved'")
        logger.info("   3. Change one status to 'Needs Revision' with notes")
        logger.info("   4. Leave some as 'Pending'")

        input("\nPress Enter when you're done updating the sheet...")

        # Step 3: Read approval results
        logger.info("\nStep 3: Reading approval results")
        tracker.open_existing_sheet(sheet_id)
        summary = tracker.get_approval_summary()

        logger.info(f"   Approval summary:")
        logger.info(f"     Total: {summary['total']}")
        logger.info(f"     Approved: {summary['approved']}")
        logger.info(f"     Pending: {summary['pending']}")
        logger.info(f"     Needs Revision: {summary['needs_revision']}")

        # Step 4: Get approved list for draft creation
        logger.info("\nStep 4: Getting approved clients for draft creation")
        approved = tracker.get_approved_clients()

        if approved:
            logger.info(f"   ✅ Ready to create drafts for {len(approved)} clients:")
            for client_name in approved:
                logger.info(f"      - {client_name}")
        else:
            logger.info(f"   ⚠️  No clients approved - would skip draft creation")

        # Step 5: Handle needs revision
        logger.info("\nStep 5: Handling clients needing revision")
        needs_revision = tracker.get_needs_revision_clients()

        if needs_revision:
            logger.info(f"   ⚠️  {len(needs_revision)} clients need revision:")
            for client in needs_revision:
                logger.info(f"      - {client['client_name']}: {client['notes']}")
        else:
            logger.info(f"   ✅ No revisions needed")

        logger.info("\n✅ Workflow simulation complete!")
        logger.info(f"   In production, would create drafts for {len(approved)} approved clients")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_error_handling():
    """Test error handling for common issues."""
    logger.info("=" * 60)
    logger.info("Test 6: Error Handling")
    logger.info("=" * 60)

    try:
        tracker = ApprovalTracker(token_path='token.json')
        tracker.authenticate()

        # Test 1: Opening non-existent sheet
        logger.info("Testing non-existent sheet ID...")
        try:
            tracker.open_existing_sheet('invalid_sheet_id_12345')
            logger.error("   ❌ Should have raised an error")
            return False
        except Exception as e:
            logger.info(f"   ✅ Correctly raised error: {type(e).__name__}")

        # Test 2: Updating status without opening sheet
        logger.info("Testing update without opening sheet...")
        tracker_new = ApprovalTracker(token_path='token.json')
        tracker_new.authenticate()
        try:
            tracker_new.update_status('Test Client', 'Approved')
            logger.error("   ❌ Should have raised an error")
            return False
        except ValueError as e:
            logger.info(f"   ✅ Correctly raised ValueError: {str(e)}")

        # Test 3: Invalid status value
        logger.info("Testing invalid status value...")
        # Create a dummy sheet first
        email_data = [{'client_name': 'Test', 'business_name': 'Test',
                      'recipient_email': 'test@test.com', 'report_type': 'SEO',
                      'extraction_errors': ''}]
        sheet_id = tracker.create_approval_sheet('[TEST ERROR] Invalid Status', email_data)
        tracker.open_existing_sheet(sheet_id)

        try:
            tracker.update_status('Test', 'InvalidStatus')
            logger.error("   ❌ Should have raised an error")
            return False
        except ValueError as e:
            logger.info(f"   ✅ Correctly raised ValueError: {str(e)}")

        logger.info("\n✅ Error handling tests passed!")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all integration tests."""
    logger.info("\n" + "=" * 60)
    logger.info("APPROVAL TRACKER INTEGRATION TESTS")
    logger.info("=" * 60)
    logger.info("\nIMPORTANT:")
    logger.info("1. Ensure token.json exists with Google Sheets API access")
    logger.info("2. Required OAuth scopes:")
    logger.info("   - https://www.googleapis.com/auth/spreadsheets")
    logger.info("   - https://www.googleapis.com/auth/drive.file")
    logger.info("3. These tests create real Google Sheets")
    logger.info("4. You may need to manually update sheets during some tests")
    logger.info("=" * 60)

    input("\nPress Enter to start tests...")

    # Test 1: Create sheet
    sheet_id = test_create_approval_sheet()
    print()

    if not sheet_id:
        logger.error("Could not create sheet. Stopping tests.")
        return False

    # Test 2: Read status
    test_read_approval_status(sheet_id)
    print()

    # Test 3: Update status
    test_update_status(sheet_id)
    print()

    # Test 4: Get approved list
    test_get_approved_list(sheet_id)
    print()

    # Test 5: Workflow simulation
    test_workflow_simulation()
    print()

    # Test 6: Error handling
    test_error_handling()
    print()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info("✅ All integration tests completed!")
    logger.info(f"\nTest sheet created: https://docs.google.com/spreadsheets/d/{sheet_id}")
    logger.info("You can delete this test sheet manually when done.")
    logger.info("=" * 60)

    return True


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
