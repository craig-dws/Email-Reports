"""
Integration test for Gmail Reader.
Tests actual connection to Gmail API (requires valid credentials).

This script tests:
1. Gmail API authentication
2. Searching for emails from Looker Studio senders
3. Extracting PDF attachments (if any found)

Note: This requires valid credentials.json and will create/use token.json
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gmail_reader import GmailReader
from src.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger('GmailIntegrationTest')


def test_gmail_authentication():
    """Test Gmail API authentication."""
    print("\n" + "="*60)
    print("TEST 1: Gmail API Authentication")
    print("="*60)

    try:
        reader = GmailReader(
            credentials_path='credentials.json',
            token_path='token.json'
        )
        print("✓ Successfully authenticated with Gmail API")
        print(f"✓ Service initialized: {reader.service is not None}")
        print(f"✓ Processed label ID: {reader.processed_label_id}")
        return reader
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return None


def test_search_looker_studio_emails(reader):
    """Test searching for emails from Looker Studio senders."""
    print("\n" + "="*60)
    print("TEST 2: Search for Looker Studio Emails")
    print("="*60)

    # Get Looker Studio sender emails from .env
    looker_senders = os.getenv('LOOKER_STUDIO_SENDERS', '').split(',')
    looker_senders = [s.strip() for s in looker_senders if s.strip()]

    if not looker_senders:
        print("✗ No LOOKER_STUDIO_SENDERS configured in .env")
        return []

    print(f"Searching for emails from: {looker_senders}")

    try:
        # Search for unread emails with attachments
        messages = reader.search_emails(
            sender_emails=looker_senders,
            unread_only=True,
            has_attachment=True,
            max_results=10
        )

        print(f"✓ Found {len(messages)} unread emails with attachments")

        # Get details for first few messages
        for i, msg in enumerate(messages[:3], 1):
            try:
                details = reader.get_email_details(msg['id'])
                print(f"\n  Email {i}:")
                print(f"    Subject: {details['subject']}")
                print(f"    From: {details['from']}")
                print(f"    Date: {details['date']}")
            except Exception as e:
                print(f"  ✗ Failed to get details for message {msg['id']}: {e}")

        return messages

    except Exception as e:
        print(f"✗ Search failed: {e}")
        return []


def test_extract_pdfs(reader, messages):
    """Test extracting PDFs from found messages."""
    print("\n" + "="*60)
    print("TEST 3: Extract PDF Attachments")
    print("="*60)

    if not messages:
        print("⚠ No messages to extract PDFs from")
        return

    # Use test output directory
    output_dir = Path(__file__).parent / 'data' / 'test_pdfs'
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}")
    print(f"Processing {min(len(messages), 3)} emails...")

    total_pdfs = 0
    total_errors = 0

    # Extract PDFs from first 3 messages only (for testing)
    for i, msg in enumerate(messages[:3], 1):
        try:
            print(f"\n  Processing email {i}...")
            pdfs, errors = reader.extract_pdfs_from_email(
                message_id=msg['id'],
                output_dir=str(output_dir)
            )

            if pdfs:
                print(f"  ✓ Extracted {len(pdfs)} PDF(s):")
                for pdf in pdfs:
                    pdf_name = Path(pdf).name
                    pdf_size = Path(pdf).stat().st_size if Path(pdf).exists() else 0
                    print(f"    - {pdf_name} ({pdf_size:,} bytes)")
                total_pdfs += len(pdfs)

            if errors:
                print(f"  ✗ Encountered {len(errors)} error(s):")
                for error in errors:
                    print(f"    - {error}")
                total_errors += len(errors)

            if not pdfs and not errors:
                print(f"  ⚠ No PDFs found in this email")

        except Exception as e:
            print(f"  ✗ Failed to process message: {e}")
            total_errors += 1

    print(f"\n{'='*60}")
    print(f"Summary: {total_pdfs} PDFs extracted, {total_errors} errors")
    print(f"{'='*60}")


def test_extract_all_pdfs_batch(reader):
    """Test batch extraction of all PDFs."""
    print("\n" + "="*60)
    print("TEST 4: Batch PDF Extraction (Full Workflow)")
    print("="*60)

    # Get Looker Studio sender emails from .env
    looker_senders = os.getenv('LOOKER_STUDIO_SENDERS', '').split(',')
    looker_senders = [s.strip() for s in looker_senders if s.strip()]

    if not looker_senders:
        print("✗ No LOOKER_STUDIO_SENDERS configured in .env")
        return

    output_dir = Path(__file__).parent / 'data' / 'test_pdfs_batch'
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting PDFs from: {looker_senders}")
    print(f"Output directory: {output_dir}")
    print(f"⚠ Note: This will NOT mark emails as processed (dry run)\n")

    try:
        # Extract all PDFs but don't mark as processed
        result = reader.extract_all_pdfs(
            sender_emails=looker_senders,
            output_dir=str(output_dir),
            mark_as_processed=False,  # Don't mark as processed for testing
            unread_only=True
        )

        print(f"\n✓ Batch extraction complete!")
        print(f"  PDFs extracted: {len(result['pdfs'])}")
        print(f"  Emails processed: {result['processed_count']}")
        print(f"  Errors: {result['error_count']}")

        if result['pdfs']:
            print(f"\n  Extracted PDFs:")
            for pdf in result['pdfs']:
                pdf_name = Path(pdf).name
                print(f"    - {pdf_name}")

        if result['errors']:
            print(f"\n  Errors encountered:")
            for error in result['errors']:
                print(f"    - {error}")

    except Exception as e:
        print(f"✗ Batch extraction failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all integration tests."""
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Gmail Reader Integration Tests".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "═"*58 + "╝")

    # Test 1: Authentication
    reader = test_gmail_authentication()
    if not reader:
        print("\n✗ Cannot proceed without authentication. Exiting.")
        return

    # Test 2: Search for emails
    messages = test_search_looker_studio_emails(reader)

    # Test 3: Extract PDFs from individual messages
    if messages:
        test_extract_pdfs(reader, messages)
    else:
        print("\n⚠ Skipping PDF extraction test (no emails found)")

    # Test 4: Batch extraction
    test_extract_all_pdfs_batch(reader)

    print("\n" + "="*60)
    print("All tests complete!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
