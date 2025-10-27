"""
Integration test for Email Generation.
Tests the complete workflow: PDF extraction -> Client matching -> Email generation.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.pdf_extractor import PDFExtractor
from src.client_database import ClientDatabase
from src.email_generator import EmailGenerator


def test_email_generation():
    """Test complete email generation workflow."""

    print("=" * 70)
    print("EMAIL GENERATION INTEGRATION TEST")
    print("=" * 70)
    print()

    # Load environment
    load_dotenv()

    # Configuration
    config = {
        'AGENCY_NAME': os.getenv('AGENCY_NAME', 'NFM Agency'),
        'AGENCY_EMAIL': os.getenv('AGENCY_EMAIL', 'contact@nfmagency.com.au'),
        'AGENCY_PHONE': os.getenv('AGENCY_PHONE', '+61 123 456 789'),
        'AGENCY_WEBSITE': os.getenv('AGENCY_WEBSITE', 'www.nfmagency.com.au'),
        'STANDARD_SEO_PARAGRAPH': os.getenv(
            'STANDARD_SEO_PARAGRAPH',
            'Your keyword rankings continue to improve across target search terms. '
            'We\'re monitoring performance closely and will continue optimizing your content strategy to maintain upward momentum.'
        ),
        'STANDARD_SEM_PARAGRAPH': os.getenv(
            'STANDARD_SEM_PARAGRAPH',
            'Your Google Ads campaigns continue to drive quality traffic and conversions. '
            'We\'re actively monitoring performance and making bid adjustments to maximize your ROI.'
        ),
        'STANDARD_CLOSING_PARAGRAPH': os.getenv(
            'STANDARD_CLOSING_PARAGRAPH',
            'Please review the attached PDF for your complete monthly report. '
            'If you have any questions or would like to discuss these results in more detail, don\'t hesitate to reach out.'
        )
    }

    # Initialize modules
    pdf_extractor = PDFExtractor()
    client_db = ClientDatabase(csv_path='data/clients.csv')
    email_generator = EmailGenerator(
        template_path='templates/email_template.html',
        config=config
    )

    # Test PDFs
    test_pdfs = [
        {
            'path': 'tgc_seo.pdf',
            'expected_client': 'The George Centre',
            'expected_type': 'SEO'
        },
        {
            'path': 'tgc_google_ads.pdf',
            'expected_client': 'The George Centre',
            'expected_type': 'Google Ads'
        }
    ]

    results = []

    for test_pdf in test_pdfs:
        print(f"\n{'-' * 70}")
        print(f"Processing: {test_pdf['path']}")
        print(f"{'-' * 70}\n")

        # Step 1: Extract data from PDF
        print("Step 1: Extracting data from PDF...")
        extracted_data = pdf_extractor.extract_report_data(test_pdf['path'])

        print(f"  Business Name: {extracted_data['business_name']}")
        print(f"  Report Type: {extracted_data['report_type']}")
        print(f"  Report Month: {extracted_data['report_month']}")
        print(f"  KPIs extracted: {len(extracted_data['kpis'])}")

        if extracted_data['extraction_errors']:
            print(f"  Extraction errors: {extracted_data['extraction_errors']}")

        # Step 2: Match to client database
        print("\nStep 2: Matching to client database...")
        client = client_db.find_client(extracted_data['business_name'])

        if not client:
            print(f"  ERROR: No client match found for '{extracted_data['business_name']}'")
            results.append({
                'pdf': test_pdf['path'],
                'success': False,
                'error': 'No client match'
            })
            continue

        print(f"  Matched client: {client['Client-Name']}")
        print(f"  Contact: {client['Contact-Name']}")
        print(f"  Email: {client['Contact-Email']}")

        # Step 3: Generate email
        print("\nStep 3: Generating email...")
        try:
            email_data = email_generator.generate_email(client, extracted_data)

            print(f"  Subject: {email_data['subject']}")
            print(f"  To: {email_data['recipient_email']}")
            print(f"  Recipient Name: {email_data['recipient_name']}")
            print(f"  HTML Body Length: {len(email_data['html_body'])} characters")
            print(f"  Text Body Length: {len(email_data['text_body'])} characters")

            # Save HTML output for manual inspection
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)

            html_filename = f"{test_pdf['path'].replace('.pdf', '')}_email.html"
            html_path = output_dir / html_filename

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(email_data['html_body'])

            print(f"\n  [OK] Email HTML saved to: {html_path}")

            # Save text version too
            text_filename = f"{test_pdf['path'].replace('.pdf', '')}_email.txt"
            text_path = output_dir / text_filename

            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(email_data['text_body'])

            print(f"  [OK] Email text saved to: {text_path}")

            # Verification
            print("\nStep 4: Verification...")

            # Check KPIs are in email
            kpi_count = 0
            for kpi_name in extracted_data['kpis'].keys():
                if kpi_name in email_data['html_body']:
                    kpi_count += 1

            print(f"  [OK] KPIs in HTML: {kpi_count}/{len(extracted_data['kpis'])}")

            # Check personalization
            checks = {
                'Contact name in greeting': client['Contact-Name'].split('&')[0].strip() in email_data['html_body'],
                'Business name in email': client['Client-Name'] in email_data['html_body'],
                'Report month in subject': extracted_data['report_month'] in email_data['subject'],
                'Report type in subject': extracted_data['report_type'] in email_data['subject'] or
                                         ('SEO' in email_data['subject'] and extracted_data['report_type'] == 'SEO'),
                'Agency name in signature': config['AGENCY_NAME'] in email_data['html_body'],
            }

            for check, passed in checks.items():
                status = '[PASS]' if passed else '[FAIL]'
                print(f"  {status} {check}")

            all_passed = all(checks.values())

            results.append({
                'pdf': test_pdf['path'],
                'success': all_passed,
                'checks': checks,
                'email_data': email_data
            })

        except Exception as e:
            print(f"  ERROR: Failed to generate email: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                'pdf': test_pdf['path'],
                'success': False,
                'error': str(e)
            })

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}\n")

    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)

    print(f"Tests passed: {success_count}/{total_count}")

    for result in results:
        status = '[PASS]' if result['success'] else '[FAIL]'
        print(f"  {status}: {result['pdf']}")
        if not result['success'] and 'error' in result:
            print(f"    Error: {result['error']}")

    print()

    if success_count == total_count:
        print("SUCCESS: All integration tests passed!")
        print("\nYou can now view the generated emails in the 'output/' directory.")
        print("Open the HTML files in a web browser to see how they will look.")
        return True
    else:
        print("WARNING: Some tests failed. Please review the errors above.")
        return False


if __name__ == '__main__':
    success = test_email_generation()
    sys.exit(0 if success else 1)
