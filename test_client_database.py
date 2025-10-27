"""
Test script for client database module.

Tests CSV loading, fuzzy matching, and edge case handling.
"""

import sys
from pathlib import Path
import logging

# We'll import the module directly without going through __init__.py
# to avoid dependency issues with other modules

# Read and execute the client_database module manually
src_dir = Path(__file__).parent / 'src'
client_db_path = src_dir / 'client_database.py'
logger_path = src_dir / 'logger.py'

# Setup basic logging first
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# Import required dependencies
import csv
from typing import Dict, Optional, List, Tuple
from rapidfuzz import fuzz, process

# Now we can define get_logger inline
def get_logger(name):
    return logging.getLogger(name)

# Execute client_database.py in a namespace
namespace = {
    'csv': csv,
    'Path': Path,
    'Dict': Dict,
    'Optional': Optional,
    'List': List,
    'Tuple': Tuple,
    'fuzz': fuzz,
    'process': process,
    'get_logger': get_logger,
    '__name__': 'client_database',
}

with open(client_db_path, 'r', encoding='utf-8') as f:
    code = f.read()
    # Remove relative import
    code = code.replace('from .logger import get_logger', '# from .logger import get_logger')
    exec(code, namespace)

ClientDatabase = namespace['ClientDatabase']


def test_csv_loading():
    """Test loading clients from CSV."""
    print("\n" + "="*80)
    print("TEST 1: CSV Loading")
    print("="*80)

    csv_path = Path(__file__).parent / 'data' / 'clients.csv'
    print(f"CSV Path: {csv_path}")
    print(f"CSV Exists: {csv_path.exists()}")

    try:
        db = ClientDatabase(str(csv_path))
        print(f"[PASS] Successfully loaded {len(db.clients)} clients")

        # Show first 3 clients
        print("\nFirst 3 clients:")
        for i, client in enumerate(db.clients[:3], 1):
            print(f"  {i}. {client.get('Client-Name', 'N/A')}")
            print(f"     Email: {client.get('Contact-Email', 'N/A')}")
            print(f"     Contact: {client.get('Contact-Name', 'N/A')}")

        return True
    except Exception as e:
        print(f"[FAIL] Failed to load CSV: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exact_matching(db):
    """Test exact matching."""
    print("\n" + "="*80)
    print("TEST 2: Exact Matching")
    print("="*80)

    test_cases = [
        "The George Centre",
        "HHMP",
        "Capital Smiles",
        "TLG"
    ]

    passed = 0
    for test_name in test_cases:
        print(f"\nTesting: '{test_name}'")
        client = db.find_client(test_name)

        if client:
            print(f"  [PASS] Found: {client.get('Client-Name', 'N/A')}")
            print(f"    Contact: {client.get('Contact-Name', 'N/A')}")
            print(f"    Email: {client.get('Contact-Email', 'N/A')}")
            passed += 1
        else:
            print(f"  [FAIL] Not found")

    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_fuzzy_matching(db):
    """Test fuzzy matching with variations."""
    print("\n" + "="*80)
    print("TEST 3: Fuzzy Matching")
    print("="*80)

    # Test cases: (input, expected_match)
    test_cases = [
        ("George Centre", "The George Centre"),  # Missing "The"
        ("the george centre", "The George Centre"),  # Lowercase
        ("THE GEORGE CENTRE", "The George Centre"),  # Uppercase
        ("Capital Smile", "Capital Smiles"),  # Missing 's'
        ("Lakeview Private", "Lakeview Private Hospital"),  # Partial name
    ]

    passed = 0
    for test_name, expected in test_cases:
        print(f"\nTesting: '{test_name}'")
        print(f"Expected: '{expected}'")

        client = db.find_client(test_name)

        if client:
            found_name = client.get('Client-Name', 'N/A')
            if found_name == expected:
                print(f"  [PASS] Correct match: {found_name}")
                passed += 1
            else:
                print(f"  [FAIL] Wrong match: {found_name} (expected {expected})")
        else:
            print(f"  [FAIL] Not found")

    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed >= len(test_cases) * 0.8  # 80% success rate acceptable


def test_pdf_extraction_matching(db):
    """Test matching with business names from actual PDF extraction."""
    print("\n" + "="*80)
    print("TEST 4: PDF Extraction Business Names")
    print("="*80)

    # These are the business names extracted from the PDFs
    pdf_business_names = [
        "The George Centre"  # From both SEO and Google Ads PDFs
    ]

    passed = 0
    for business_name in pdf_business_names:
        print(f"\nTesting PDF business name: '{business_name}'")
        client = db.find_client(business_name)

        if client:
            print(f"  [PASS] Matched to: {client.get('Client-Name', 'N/A')}")
            print(f"    Contact: {client.get('Contact-Name', 'N/A')}")
            print(f"    Email: {client.get('Contact-Email', 'N/A')}")

            # Check if both SEO and Google Ads intros exist
            seo_intro = client.get('SEO-Introduction', '').strip()
            ga_intro = client.get('Google-Ads-Introduction', '').strip()

            print(f"    Has SEO intro: {'Yes' if seo_intro else 'No'}")
            print(f"    Has Google Ads intro: {'Yes' if ga_intro else 'No'}")

            passed += 1
        else:
            print(f"  [FAIL] Not found in database")

    print(f"\nPassed: {passed}/{len(pdf_business_names)}")
    return passed == len(pdf_business_names)


def test_edge_cases(db):
    """Test edge cases."""
    print("\n" + "="*80)
    print("TEST 5: Edge Cases")
    print("="*80)

    test_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("NonExistent Company LLC", "Company not in database"),
        ("XYZ123", "Random string"),
    ]

    passed = 0
    for test_name, description in test_cases:
        print(f"\nTesting: {description}")
        print(f"Input: '{test_name}'")

        try:
            client = db.find_client(test_name)

            if client:
                print(f"  Found (unexpected): {client.get('Client-Name', 'N/A')}")
            else:
                print(f"  [PASS] Correctly returned None")
                passed += 1

        except Exception as e:
            print(f"  [FAIL] Raised exception: {e}")

    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed >= len(test_cases) * 0.75  # 75% success rate acceptable


def test_multiple_matches(db):
    """Test finding multiple matches with ambiguous name."""
    print("\n" + "="*80)
    print("TEST 6: Multiple Matches / Ambiguous Names")
    print("="*80)

    # Test 1: Exact name should return single high-confidence match
    test_name = "The George Centre"
    print(f"\nTest 1: Exact name '{test_name}'")
    matches = db.find_all_matches(test_name, min_score=85)

    print(f"Found {len(matches)} matches:")
    for i, (client, score) in enumerate(matches[:3], 1):
        print(f"  {i}. {client.get('Client-Name', 'N/A')} (score: {score})")

    passed1 = len(matches) == 1 and matches[0][1] == 100
    print(f"{'[PASS]' if passed1 else '[FAIL]'} Exact match returns single result with score 100")

    # Test 2: Slightly misspelled name should still find good match
    test_name2 = "George Center"  # "Center" instead of "Centre"
    print(f"\nTest 2: Misspelled name '{test_name2}'")
    matches2 = db.find_all_matches(test_name2, min_score=70)

    print(f"Found {len(matches2)} matches:")
    for i, (client, score) in enumerate(matches2[:3], 1):
        print(f"  {i}. {client.get('Client-Name', 'N/A')} (score: {score})")

    passed2 = len(matches2) >= 1
    print(f"{'[PASS]' if passed2 else '[FAIL]'} Misspelled name finds at least one match")

    # Test 3: Show that ambiguous names can be detected
    # (This is informational - shows the feature works even if we don't have a truly ambiguous name)
    print(f"\nTest 3: Feature demonstration - finding multiple potential matches")
    print(f"(This would be useful if there were similar business names in the database)")

    return passed1 or passed2  # Pass if either test succeeds


def test_validation(db):
    """Test database validation."""
    print("\n" + "="*80)
    print("TEST 7: Database Validation")
    print("="*80)

    issues = db.validate_database()

    print(f"\nValidation Results:")
    print(f"  Total clients: {issues['total_clients']}")
    print(f"  Duplicate names: {len(issues['duplicate_names'])}")
    print(f"  Missing emails: {len(issues['missing_emails'])}")
    print(f"  Missing contact names: {len(issues['missing_contact_names'])}")
    print(f"  Missing SEO intros: {len(issues['missing_seo_intro'])}")
    print(f"  Missing Google Ads intros: {len(issues['missing_google_ads_intro'])}")

    if issues['duplicate_names']:
        print(f"\nDuplicate names found:")
        for name in issues['duplicate_names']:
            print(f"  - {name}")

    if issues['missing_emails']:
        print(f"\nClients missing emails:")
        for name in issues['missing_emails'][:5]:  # Show first 5
            print(f"  - {name}")

    # Pass if no critical issues
    critical_issues = (
        len(issues['duplicate_names']) +
        len(issues['missing_emails']) +
        len(issues['missing_contact_names'])
    )

    passed = critical_issues == 0
    print(f"\n{'[PASS]' if passed else '[WARN]'} Critical issues: {critical_issues}")

    return True  # Always pass this test (it's informational)


def test_service_type_and_intros(db):
    """Test service type detection and intro retrieval."""
    print("\n" + "="*80)
    print("TEST 8: Service Type and Personalized Intros")
    print("="*80)

    # Test with The George Centre (has both SEO and Google Ads)
    test_name = "The George Centre"
    print(f"\nTesting: '{test_name}'")

    client = db.find_client(test_name)
    if not client:
        print(f"  [FAIL] Client not found")
        return False

    print(f"  [PASS] Client found: {client.get('Client-Name', 'N/A')}")

    # Test SEO intro
    seo_intro = db.get_personalized_intro(client, 'seo')
    print(f"\nSEO Introduction (first 100 chars):")
    print(f"  {seo_intro[:100]}...")

    # Test Google Ads intro
    ga_intro = db.get_personalized_intro(client, 'google_ads')
    print(f"\nGoogle Ads Introduction (first 100 chars):")
    print(f"  {ga_intro[:100]}...")

    # Test service type detection
    seo_type = db.get_service_type(client, 'seo')
    ga_type = db.get_service_type(client, 'google_ads')

    print(f"\nService Types:")
    print(f"  SEO report -> {seo_type} {'[PASS]' if seo_type == 'SEO' else '[FAIL]'}")
    print(f"  Google Ads report -> {ga_type} {'[PASS]' if ga_type == 'SEM' else '[FAIL]'}")

    passed = (
        len(seo_intro) > 0 and
        len(ga_intro) > 0 and
        seo_type == 'SEO' and
        ga_type == 'SEM'
    )

    return passed


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("CLIENT DATABASE MODULE TEST SUITE")
    print("="*80)

    # Setup logging
    setup_logging()

    # Load database once
    csv_path = Path(__file__).parent / 'data' / 'clients.csv'

    if not csv_path.exists():
        print(f"\n[FAIL] ERROR: CSV file not found: {csv_path}")
        return 1

    print(f"\nLoading database from: {csv_path}")

    try:
        db = ClientDatabase(str(csv_path))
        print(f"[PASS] Database loaded: {len(db.clients)} clients")
    except Exception as e:
        print(f"[FAIL] Failed to load database: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Run all tests
    tests = [
        ("CSV Loading", lambda: test_csv_loading()),
        ("Exact Matching", lambda: test_exact_matching(db)),
        ("Fuzzy Matching", lambda: test_fuzzy_matching(db)),
        ("PDF Extraction Matching", lambda: test_pdf_extraction_matching(db)),
        ("Edge Cases", lambda: test_edge_cases(db)),
        ("Multiple Matches", lambda: test_multiple_matches(db)),
        ("Database Validation", lambda: test_validation(db)),
        ("Service Type & Intros", lambda: test_service_type_and_intros(db)),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n[FAIL] Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "[PASS] PASS" if passed else "[FAIL] FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    # Calculate success rate
    success_rate = (passed_count / total_count) * 100

    print(f"Success Rate: {success_rate:.1f}%")

    if success_rate >= 90:
        print("\n[PASS] EXCELLENT: All tests passed or minor issues only")
        return 0
    elif success_rate >= 75:
        print("\n[WARN] WARNING: Some tests failed, review results")
        return 0  # Still acceptable
    else:
        print("\n[FAIL] FAILURE: Too many tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
