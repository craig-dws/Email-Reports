"""
Interactive test script for current implementation (Phases 1-3)
Tests: PDF extraction → Client matching → Email generation → Gmail draft creation

This script allows you to test the complete workflow with real data.
"""

import os
import sys
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Now we can import as modules
from src.pdf_extractor import PDFExtractor
from src.client_database import ClientDatabase
from src.email_generator import EmailGenerator
from src.gmail_sender import GmailSender


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def test_pdf_extraction():
    """Test PDF extraction with available sample PDFs"""
    print_section("STEP 1: PDF EXTRACTION")

    fixtures_dir = Path(__file__).parent / "tests" / "fixtures"
    pdf_files = list(fixtures_dir.glob("*.pdf"))

    if not pdf_files:
        print("❌ No PDF files found in tests/fixtures/")
        print(f"   Please add sample PDFs to: {fixtures_dir}")
        return None

    print(f"Found {len(pdf_files)} PDF file(s):")
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_path.name}")

    print("\nSelect a PDF to test (enter number): ", end="")
    try:
        choice = int(input().strip())
        if choice < 1 or choice > len(pdf_files):
            print("❌ Invalid choice")
            return None

        selected_pdf = pdf_files[choice - 1]
        print(f"\n📄 Testing with: {selected_pdf.name}")

        # Extract data
        print("\n⏳ Extracting PDF data...")
        extractor = PDFExtractor()
        pdf_data = extractor.extract_report_data(str(selected_pdf))

        if not pdf_data:
            print("❌ Failed to extract PDF data: No data returned")
            return None

        # Check for extraction errors
        errors = pdf_data.get('extraction_errors', [])
        if errors:
            print(f"⚠️  Extraction completed with warnings:")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ PDF extraction successful!")

        print(f"\n   Business Name: {pdf_data.get('business_name', 'N/A')}")
        print(f"   Report Date: {pdf_data.get('report_date', 'N/A')}")
        print(f"   Report Month: {pdf_data.get('report_month', 'N/A')}")
        print(f"   Report Type: {pdf_data.get('report_type', 'N/A')}")
        print(f"\n   KPIs extracted:")

        kpis = pdf_data.get('kpis', {})
        if not kpis:
            print("     ⚠️  No KPIs extracted")
        else:
            for metric, data in kpis.items():
                value = data.get('value', 'N/A')
                change = data.get('change', 'N/A')
                print(f"     - {metric}: {value} (change: {change})")

        return {
            'pdf_path': selected_pdf,
            'pdf_data': pdf_data
        }

    except (ValueError, KeyboardInterrupt):
        print("\n❌ Cancelled")
        return None


def test_client_matching(pdf_data):
    """Test client database matching"""
    print_section("STEP 2: CLIENT DATABASE MATCHING")

    business_name = pdf_data.get('business_name')
    if not business_name:
        print("❌ No business name extracted from PDF")
        return None

    print(f"🔍 Looking for client match: '{business_name}'")

    # Load client database
    db_path = Path(__file__).parent / "data" / "clients.csv"
    if not db_path.exists():
        print(f"❌ Client database not found: {db_path}")
        return None

    db = ClientDatabase(str(db_path))

    # Find client (uses exact match first, then fuzzy matching)
    client = db.find_client(business_name)

    if not client:
        print("❌ No match found in database")
        print(f"   Tried to match: '{business_name}'")
        print(f"   Available clients: {len(db.clients)}")
        return None

    print("✅ Match found!")

    print(f"\n   Client ID: {client.get('Client-ID', 'N/A')}")
    print(f"   Contact Name: {client.get('Contact-Name', 'N/A')}")
    print(f"   Email: {client.get('Contact-Email', 'N/A')}")
    print(f"   Service Type: {client.get('Service-Type', 'N/A')}")

    return client


def test_email_generation(pdf_data, client):
    """Test email generation"""
    print_section("STEP 3: EMAIL GENERATION")

    print("📧 Generating personalized email...")

    # Initialize email generator with test config
    template_path = Path(__file__).parent / "templates" / "email_template.html"

    # Create test configuration
    test_config = {
        'AGENCY_NAME': 'NFM Agency',
        'AGENCY_EMAIL': 'info@nfmagency.com.au',
        'AGENCY_PHONE': '(02) 1234 5678',
        'AGENCY_WEBSITE': 'https://www.nfmagency.com.au'
    }

    generator = EmailGenerator(str(template_path), test_config)

    # Generate email
    try:
        email_data = generator.generate_email(
            client_data=client,
            extracted_data=pdf_data
        )

        print("✅ Email generation successful!")
        print(f"\n   Subject: {email_data['subject']}")
        print(f"   To: {email_data['recipient_email']} ({email_data['recipient_name']})")
        print(f"   Business: {email_data['business_name']}")
        print(f"   HTML length: {len(email_data['html_body'])} characters")
        print(f"   Text length: {len(email_data['text_body'])} characters")

        # Save preview
        output_dir = Path(__file__).parent / "output" / "test_preview"
        output_dir.mkdir(parents=True, exist_ok=True)

        html_path = output_dir / "preview_email.html"
        text_path = output_dir / "preview_email.txt"

        html_path.write_text(email_data['html_body'], encoding='utf-8')
        text_path.write_text(email_data['text_body'], encoding='utf-8')

        print(f"\n   Preview saved to:")
        print(f"   - {html_path}")
        print(f"   - {text_path}")

        print(f"\n   Open in browser? (y/n): ", end="")
        if input().strip().lower() == 'y':
            import webbrowser
            webbrowser.open(f"file:///{html_path.absolute()}")

        return email_data

    except Exception as e:
        print(f"❌ Email generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_gmail_operations(email_data, pdf_path):
    """Test Gmail draft creation (optional)"""
    print_section("STEP 4: GMAIL OPERATIONS (OPTIONAL)")

    print("This will connect to Gmail API and create a draft.")
    print("⚠️  This requires valid Gmail API credentials (token.json)")
    print("\nProceed? (y/n): ", end="")

    if input().strip().lower() != 'y':
        print("⏭️  Skipping Gmail operations")
        return

    try:
        # Initialize Gmail sender
        sender = GmailSender()

        print("\n✅ Gmail API authenticated successfully")

        # Ask what to do
        print("\nWhat would you like to test?")
        print("  1. Send preview email (to yourself)")
        print("  2. Create draft (in your Gmail drafts)")
        print("  3. Skip")
        print("\nChoice (1-3): ", end="")

        choice = input().strip()

        if choice == "1":
            print("\n📧 Send preview email to which address?")
            print("   (Your email for testing): ", end="")
            preview_to = input().strip()

            if not preview_to:
                print("❌ Preview email address required")
                return

            print(f"\n⏳ Sending preview email to {preview_to}...")

            result = sender.send_preview_email(
                preview_recipient=preview_to,
                original_recipient=email_data['recipient_email'],
                subject=email_data['subject'],
                html_body=email_data['html_body'],
                text_body=email_data['text_body'],
                attachment_path=str(pdf_path)
            )

            if result['success']:
                print(f"✅ Preview email sent! Message ID: {result['message_id']}")
            else:
                print(f"❌ Failed to send: {result['error']}")

        elif choice == "2":
            print(f"\n⏳ Creating Gmail draft...")

            result = sender.create_draft(
                recipient=email_data['recipient_email'],
                subject=email_data['subject'],
                html_body=email_data['html_body'],
                text_body=email_data['text_body'],
                attachment_path=str(pdf_path)
            )

            if result['success']:
                print(f"✅ Draft created! Draft ID: {result['draft_id']}")
                print(f"   Check your Gmail drafts folder")
            else:
                print(f"❌ Failed to create draft: {result['error']}")

        else:
            print("⏭️  Skipped")

    except FileNotFoundError:
        print("❌ Gmail credentials not found (token.json)")
        print("   Run setup_gmail_oauth first")
    except Exception as e:
        print(f"❌ Gmail operation failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run interactive test"""
    print("\n" + "=" * 70)
    print("  EMAIL REPORTS AUTOMATION - IMPLEMENTATION TEST")
    print("  Testing Phases 1-3: PDF → Client Match → Email → Gmail")
    print("=" * 70)

    # Step 1: PDF Extraction
    result = test_pdf_extraction()
    if not result:
        print("\n❌ Test aborted at PDF extraction")
        return

    pdf_path = result['pdf_path']
    pdf_data = result['pdf_data']

    # Step 2: Client Matching
    client = test_client_matching(pdf_data)
    if not client:
        print("\n❌ Test aborted at client matching")
        return

    # Step 3: Email Generation
    email_data = test_email_generation(pdf_data, client)
    if not email_data:
        print("\n❌ Test aborted at email generation")
        return

    # Step 4: Gmail Operations (optional)
    test_gmail_operations(email_data, pdf_path)

    # Summary
    print_section("TEST SUMMARY")
    print("✅ PDF extraction: SUCCESS")
    print("✅ Client matching: SUCCESS")
    print("✅ Email generation: SUCCESS")
    print("\n🎉 All implemented components are working correctly!")
    print("\n📝 Next steps:")
    print("   1. Review the generated email preview")
    print("   2. Test with more PDF samples")
    print("   3. Proceed to Phase 4: Approval Workflow")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
