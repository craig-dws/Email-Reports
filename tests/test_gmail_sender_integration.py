"""
Integration test for Gmail Sender Module.
Tests actual Gmail API interactions (requires valid credentials and token).

Usage:
    python tests/test_gmail_sender_integration.py

Note: This test will create actual Gmail drafts and send test emails.
      Use with caution and ensure you have a test Gmail account.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.gmail_sender import GmailSender
from src.logger import get_logger

logger = get_logger('GmailSenderIntegrationTest')


def test_create_single_draft():
    """Test creating a single Gmail draft."""
    logger.info("=" * 60)
    logger.info("Test 1: Create Single Draft")
    logger.info("=" * 60)

    try:
        # Initialize sender
        sender = GmailSender(
            credentials_path='credentials.json',
            token_path='token.json',
            send_delay=60  # 1 minute delay for testing
        )

        # Create draft
        draft = sender.create_draft(
            recipient='your-test-email@example.com',  # CHANGE THIS
            subject='[TEST] Gmail Sender Integration Test',
            html_body='''
                <html>
                <body>
                    <h1>Gmail Sender Integration Test</h1>
                    <p>This is a test email from the Gmail Sender module.</p>
                    <p>If you receive this, the integration is working correctly.</p>
                    <table border="1" cellpadding="10">
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td>Sessions</td>
                            <td>1,234</td>
                        </tr>
                        <tr>
                            <td>Conversions</td>
                            <td>56</td>
                        </tr>
                    </table>
                </body>
                </html>
            ''',
            text_body='Gmail Sender Integration Test\n\nThis is a test email.'
        )

        logger.info(f"✅ Draft created successfully!")
        logger.info(f"   Draft ID: {draft['id']}")
        logger.info(f"   Check your Gmail drafts folder to verify.")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_create_draft_with_attachment():
    """Test creating a draft with PDF attachment."""
    logger.info("=" * 60)
    logger.info("Test 2: Create Draft with PDF Attachment")
    logger.info("=" * 60)

    try:
        # Check if test PDF exists
        test_pdf_path = Path('tests/fixtures/tgc_seo.pdf')
        if not test_pdf_path.exists():
            logger.warning(f"⚠️  Test PDF not found at {test_pdf_path}")
            logger.info("   Skipping attachment test.")
            return True

        # Initialize sender
        sender = GmailSender(
            credentials_path='credentials.json',
            token_path='token.json'
        )

        # Create draft with attachment
        draft = sender.create_draft(
            recipient='your-test-email@example.com',  # CHANGE THIS
            subject='[TEST] Draft with PDF Attachment',
            html_body='<p>This draft includes a PDF attachment.</p>',
            text_body='This draft includes a PDF attachment.',
            attachment_path=str(test_pdf_path)
        )

        logger.info(f"✅ Draft with attachment created successfully!")
        logger.info(f"   Draft ID: {draft['id']}")
        logger.info(f"   Check your Gmail drafts folder to verify PDF attachment.")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_send_preview_email():
    """Test sending a preview email."""
    logger.info("=" * 60)
    logger.info("Test 3: Send Preview Email")
    logger.info("=" * 60)
    logger.warning("⚠️  This test will send an actual email!")

    response = input("Continue? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("Test skipped by user.")
        return True

    try:
        # Initialize sender
        sender = GmailSender(
            credentials_path='credentials.json',
            token_path='token.json'
        )

        # Send preview email
        result = sender.send_preview_email(
            preview_recipient='your-test-email@example.com',  # CHANGE THIS
            original_recipient='client@example.com',
            subject='Your January 2025 SEO Report',
            html_body='''
                <html>
                <body>
                    <p>Hi John,</p>
                    <p>Please see the data below for ABC Corporation.</p>
                    <p>Great progress this month on your SEO campaigns!</p>
                    <table border="1" cellpadding="10">
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td>Sessions</td>
                            <td>3,456</td>
                        </tr>
                        <tr>
                            <td>Conversions</td>
                            <td>127</td>
                        </tr>
                    </table>
                    <p>Best regards,<br>Your Agency</p>
                </body>
                </html>
            ''',
            text_body='Preview email test content'
        )

        logger.info(f"✅ Preview email sent successfully!")
        logger.info(f"   Message ID: {result['id']}")
        logger.info(f"   Check your inbox for the [PREVIEW] email.")
        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_list_drafts():
    """Test listing existing drafts."""
    logger.info("=" * 60)
    logger.info("Test 4: List Existing Drafts")
    logger.info("=" * 60)

    try:
        # Initialize sender
        sender = GmailSender(
            credentials_path='credentials.json',
            token_path='token.json'
        )

        # List drafts
        drafts = sender.list_drafts(max_results=10)

        logger.info(f"✅ Found {len(drafts)} drafts in Gmail")
        if drafts:
            logger.info("   First few drafts:")
            for draft in drafts[:3]:
                logger.info(f"     - Draft ID: {draft['id']}")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_create_batch_drafts():
    """Test creating multiple drafts in batch."""
    logger.info("=" * 60)
    logger.info("Test 5: Create Batch Drafts (3 drafts)")
    logger.info("=" * 60)

    try:
        # Initialize sender
        sender = GmailSender(
            credentials_path='credentials.json',
            token_path='token.json'
        )

        # Prepare batch data
        draft_data_list = [
            {
                'recipient': 'your-test-email@example.com',  # CHANGE THIS
                'subject': '[TEST BATCH 1] Client Report 1',
                'html_body': '<p>This is batch draft #1</p>',
                'text_body': 'Batch draft #1'
            },
            {
                'recipient': 'your-test-email@example.com',  # CHANGE THIS
                'subject': '[TEST BATCH 2] Client Report 2',
                'html_body': '<p>This is batch draft #2</p>',
                'text_body': 'Batch draft #2'
            },
            {
                'recipient': 'your-test-email@example.com',  # CHANGE THIS
                'subject': '[TEST BATCH 3] Client Report 3',
                'html_body': '<p>This is batch draft #3</p>',
                'text_body': 'Batch draft #3'
            }
        ]

        # Create batch
        results = sender.create_drafts_batch(draft_data_list)

        logger.info(f"✅ Batch creation complete!")
        logger.info(f"   Total: {results['total']}")
        logger.info(f"   Successful: {results['successful']}")
        logger.info(f"   Failed: {results['failed']}")

        if results['draft_ids']:
            logger.info(f"   Draft IDs created:")
            for draft_id in results['draft_ids']:
                logger.info(f"     - {draft_id}")

        if results['errors']:
            logger.error(f"   Errors:")
            for error in results['errors']:
                logger.error(f"     - {error}")

        return results['successful'] == results['total']

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def test_retry_logic():
    """Test retry logic (simulated by checking the implementation)."""
    logger.info("=" * 60)
    logger.info("Test 6: Verify Retry Logic Implementation")
    logger.info("=" * 60)

    try:
        # Initialize sender
        sender = GmailSender(
            credentials_path='credentials.json',
            token_path='token.json'
        )

        # Check retry configuration
        logger.info(f"   Max retries: {sender.MAX_RETRIES}")
        logger.info(f"   Initial backoff: {sender.INITIAL_BACKOFF}s")
        logger.info(f"   Send delay: {sender.send_delay}s")

        # Verify retry method exists
        has_retry_method = hasattr(sender, '_execute_with_retry')
        logger.info(f"   Has retry method: {has_retry_method}")

        if has_retry_method:
            logger.info("✅ Retry logic is implemented")
            return True
        else:
            logger.error("❌ Retry method not found")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all integration tests."""
    logger.info("\n" + "=" * 60)
    logger.info("GMAIL SENDER INTEGRATION TESTS")
    logger.info("=" * 60)
    logger.info("\nIMPORTANT:")
    logger.info("1. Update 'your-test-email@example.com' with your actual test email")
    logger.info("2. Ensure credentials.json and token.json are present")
    logger.info("3. Some tests create drafts, others send actual emails")
    logger.info("=" * 60)

    input("\nPress Enter to start tests...")

    tests = [
        ("Create Single Draft", test_create_single_draft),
        ("Create Draft with Attachment", test_create_draft_with_attachment),
        ("Send Preview Email", test_send_preview_email),
        ("List Drafts", test_list_drafts),
        ("Create Batch Drafts", test_create_batch_drafts),
        ("Verify Retry Logic", test_retry_logic)
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
            print()  # Add spacing between tests
        except Exception as e:
            logger.error(f"Unhandled exception in {test_name}: {str(e)}")
            results[test_name] = False

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("=" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 60)

    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
