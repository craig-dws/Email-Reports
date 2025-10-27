"""Debug Google Ads extraction."""

import pdfplumber
import re

expected_fields = [
    'Clicks',
    'Impressions',
    'CTR',
    'Conversions',
    'Conv. rate',
    'Avg. CPC',
    'Cost'
]

with pdfplumber.open('tgc_google_ads.pdf') as pdf:
    text = pdf.pages[0].extract_text()
    lines = text.split('\n')

    print("Searching for header line containing expected fields...")
    print(f"Expected fields: {expected_fields}\n")

    for i, line in enumerate(lines):
        fields_found = [field for field in expected_fields if field.lower() in line.lower()]

        if len(fields_found) > 0:
            print(f"Line {i}: {fields_found} fields found")
            print(f"  Text: {line[:100]}")

            if len(fields_found) >= 3:
                print(f"  *** MATCH! Found {len(fields_found)} fields ***")
                print(f"  Header line: {line}")
                if i + 1 < len(lines):
                    print(f"  Values line: {lines[i+1]}")
                if i + 2 < len(lines):
                    print(f"  Changes line: {lines[i+2]}")
                print()
