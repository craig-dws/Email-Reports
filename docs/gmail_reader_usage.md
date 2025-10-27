# Gmail Reader Module - Usage Guide

## Overview

The `gmail_reader.py` module provides comprehensive Gmail API integration for extracting PDF attachments from Looker Studio reports. It handles authentication, email searching, PDF extraction, and email processing tracking.

## Features

- **Automatic OAuth 2.0 Authentication**: Handles token refresh automatically
- **Multi-Sender Support**: Search emails from multiple Looker Studio accounts
- **Robust Error Handling**: Exponential backoff retry logic for rate limits and network errors
- **Email Processing Tracking**: Marks processed emails with custom labels
- **Batch PDF Extraction**: Process multiple emails efficiently
- **Windows-Compatible**: Sanitizes filenames for Windows file systems
- **Comprehensive Logging**: Detailed logs for troubleshooting

## Prerequisites

1. **Gmail API Credentials**:
   - `credentials.json` file from Google Cloud Console
   - See `OAUTH_SETUP_GUIDE.md` for setup instructions

2. **Environment Variables** (in `.env` file):
   ```env
   LOOKER_STUDIO_SENDERS=sender1@gmail.com,sender2@gmail.com
   PDF_STORAGE_PATH=c:/Apps/Email Reports/data/pdfs/
   ```

3. **Python Dependencies**:
   ```bash
   pip install google-api-python-client google-auth-oauthlib
   ```

## Quick Start

### Option 1: Using the Convenience Function

```python
from src.gmail_reader import extract_looker_studio_pdfs

# Extract all PDFs from Looker Studio emails
result = extract_looker_studio_pdfs(
    sender_emails=['discover.sem.manager@gmail.com', 'discover.web.seo@gmail.com'],
    output_dir='data/pdfs'
)

print(f"Extracted {len(result['pdfs'])} PDFs")
print(f"Processed {result['processed_count']} emails")
print(f"Errors: {result['error_count']}")
```

### Option 2: Using the GmailReader Class

```python
from src.gmail_reader import GmailReader

# Initialize reader (will prompt for OAuth if needed)
reader = GmailReader(
    credentials_path='credentials.json',
    token_path='token.json'
)

# Search for specific emails
messages = reader.search_emails(
    sender_emails=['looker@example.com'],
    unread_only=True,
    has_attachment=True,
    max_results=50
)

# Extract PDFs from all found emails
result = reader.extract_all_pdfs(
    sender_emails=['looker@example.com'],
    output_dir='data/pdfs',
    mark_as_processed=True,
    unread_only=True
)
```

## API Reference

### GmailReader Class

#### Constructor

```python
reader = GmailReader(
    credentials_path: str = 'credentials.json',
    token_path: str = 'token.json'
)
```

**Parameters:**
- `credentials_path`: Path to OAuth credentials JSON file
- `token_path`: Path to store/load OAuth token

**First Run:** Opens browser for OAuth authorization

#### search_emails()

```python
messages = reader.search_emails(
    sender_emails: List[str],
    unread_only: bool = True,
    has_attachment: bool = True,
    max_results: int = 50
) -> List[Dict]
```

**Parameters:**
- `sender_emails`: List of email addresses to search for
- `unread_only`: Only return unread emails (default: True)
- `has_attachment`: Only return emails with attachments (default: True)
- `max_results`: Maximum number of emails to return (default: 50)

**Returns:** List of email metadata dictionaries with 'id' and 'threadId'

**Example:**
```python
messages = reader.search_emails(
    sender_emails=['sender1@gmail.com', 'sender2@gmail.com'],
    unread_only=True,
    has_attachment=True
)
print(f"Found {len(messages)} emails")
```

#### get_email_details()

```python
details = reader.get_email_details(message_id: str) -> Dict
```

**Parameters:**
- `message_id`: Gmail message ID

**Returns:** Dictionary with email details:
```python
{
    'id': 'message_id',
    'subject': 'Email Subject',
    'from': 'sender@example.com',
    'date': 'Mon, 1 Jan 2024 12:00:00 +0000',
    'payload': {...}
}
```

#### extract_pdfs_from_email()

```python
pdfs, errors = reader.extract_pdfs_from_email(
    message_id: str,
    output_dir: str,
    sanitize_filename: bool = True
) -> Tuple[List[str], List[str]]
```

**Parameters:**
- `message_id`: Gmail message ID
- `output_dir`: Directory to save PDFs
- `sanitize_filename`: Clean filenames for Windows compatibility (default: True)

**Returns:** Tuple of (list of PDF paths, list of error messages)

**Example:**
```python
pdfs, errors = reader.extract_pdfs_from_email(
    message_id='123abc',
    output_dir='data/pdfs'
)

for pdf in pdfs:
    print(f"Extracted: {pdf}")

for error in errors:
    print(f"Error: {error}")
```

#### extract_all_pdfs()

```python
result = reader.extract_all_pdfs(
    sender_emails: List[str],
    output_dir: str,
    mark_as_processed: bool = True,
    unread_only: bool = True
) -> Dict
```

**Parameters:**
- `sender_emails`: List of email addresses to extract PDFs from
- `output_dir`: Directory to save PDFs
- `mark_as_processed`: Mark emails as processed after extraction (default: True)
- `unread_only`: Only process unread emails (default: True)

**Returns:** Dictionary with extraction results:
```python
{
    'pdfs': ['path/to/pdf1.pdf', 'path/to/pdf2.pdf'],
    'processed_count': 2,
    'error_count': 0,
    'errors': []
}
```

#### mark_as_processed()

```python
reader.mark_as_processed(message_id: str)
```

Marks an email as processed by:
1. Removing the 'UNREAD' label
2. Adding the 'EmailReports/Processed' custom label

#### mark_as_read()

```python
reader.mark_as_read(message_id: str)
```

Marks an email as read (removes 'UNREAD' label without adding custom label).

## Error Handling

The Gmail Reader includes comprehensive error handling:

### Rate Limiting

Automatically retries with exponential backoff on rate limit errors (HTTP 429):
- Attempt 1: Wait 1 second
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds

### Network Errors

Retries transient network errors (HTTP 500, 503) up to 3 times.

### File Handling

- **Corrupted PDFs**: Logs error and continues with next attachment
- **Duplicate Filenames**: Automatically appends `_1`, `_2`, etc.
- **Missing Attachments**: Logs warning and continues

### Example Error Handling

```python
try:
    result = reader.extract_all_pdfs(
        sender_emails=['looker@example.com'],
        output_dir='data/pdfs'
    )

    # Check for errors
    if result['error_count'] > 0:
        print(f"Encountered {result['error_count']} errors:")
        for error in result['errors']:
            print(f"  - {error}")

    # Process successfully extracted PDFs
    for pdf in result['pdfs']:
        print(f"Successfully extracted: {pdf}")

except Exception as e:
    print(f"Critical error: {e}")
```

## Logging

The module logs all operations with different severity levels:

- **INFO**: Successful operations, progress updates
- **WARNING**: Recoverable issues (retries, missing data)
- **ERROR**: Failed operations, extraction errors

**Log Format:**
```
[2025-01-05 14:23:45] [INFO] [GmailReader] Searching emails with query: from:looker@example.com is:unread has:attachment
[2025-01-05 14:23:46] [INFO] [GmailReader] Found 5 matching emails
[2025-01-05 14:23:50] [INFO] [GmailReader] Extracted PDF: report.pdf (1,234,567 bytes)
```

Logs are saved to `logs/YYYY-MM-DD.log` and displayed in console.

## Testing

### Run Unit Tests

```bash
# Run all tests
python -m unittest tests/test_gmail_reader.py -v

# Run specific test
python -m unittest tests.test_gmail_reader.TestGmailReader.test_search_emails_single_sender
```

### Run Integration Tests

```bash
# Test with actual Gmail account (requires credentials.json)
python test_gmail_integration.py
```

**Integration tests:**
1. Authenticate with Gmail API
2. Search for Looker Studio emails
3. Extract PDFs from found emails
4. Test batch extraction workflow

## Common Issues & Solutions

### Issue: "Credentials file not found"

**Solution:**
1. Download `credentials.json` from Google Cloud Console
2. Place in project root directory
3. Ensure path is correct in code

### Issue: "Token expired" or "Invalid credentials"

**Solution:**
1. Delete `token.json` file
2. Re-run script - will prompt for OAuth authorization
3. Grant permissions in browser

### Issue: "No emails found"

**Possible causes:**
- All emails already processed (marked as read)
- Wrong sender email addresses
- No unread emails with attachments

**Solution:**
```python
# Search all emails (including read)
messages = reader.search_emails(
    sender_emails=['looker@example.com'],
    unread_only=False,
    has_attachment=True
)
```

### Issue: "Rate limit exceeded"

**Solution:** The module automatically retries with exponential backoff. If issue persists:
1. Reduce `max_results` parameter
2. Process emails in smaller batches
3. Add delays between operations

### Issue: "File path too long" (Windows)

**Solution:** Enable long path support or use shorter output directory path:
```python
# Short path
output_dir = 'C:/pdfs'  # Instead of long nested path
```

## Best Practices

### 1. Environment-Specific Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

looker_senders = os.getenv('LOOKER_STUDIO_SENDERS', '').split(',')
pdf_dir = os.getenv('PDF_STORAGE_PATH', 'data/pdfs')

result = extract_looker_studio_pdfs(
    sender_emails=looker_senders,
    output_dir=pdf_dir
)
```

### 2. Dry Run Before Processing

```python
# First, check what emails would be processed
messages = reader.search_emails(
    sender_emails=['looker@example.com'],
    unread_only=True,
    has_attachment=True
)

print(f"Would process {len(messages)} emails")

# View email subjects
for msg in messages:
    details = reader.get_email_details(msg['id'])
    print(f"  - {details['subject']}")

# Confirm before processing
if input("Process these emails? (y/n): ").lower() == 'y':
    result = reader.extract_all_pdfs(...)
```

### 3. Monitor Extraction Results

```python
result = reader.extract_all_pdfs(...)

# Log summary
print(f"\nExtraction Summary:")
print(f"  Total PDFs: {len(result['pdfs'])}")
print(f"  Emails processed: {result['processed_count']}")
print(f"  Errors: {result['error_count']}")

# Alert if errors exceed threshold
if result['error_count'] > 0.1 * result['processed_count']:
    print("⚠ Warning: High error rate!")
    # Send notification, log alert, etc.
```

### 4. Secure Credential Management

```python
# DO NOT commit credentials to version control
# Add to .gitignore:
# credentials.json
# token.json
# .env

# Use environment variables for sensitive paths
credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
token_path = os.getenv('GMAIL_TOKEN_PATH', 'token.json')

reader = GmailReader(credentials_path, token_path)
```

## Advanced Usage

### Process Only Specific Date Range

```python
# Search with custom query
from datetime import datetime, timedelta

# Last 7 days
date_str = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
query = f'from:looker@example.com after:{date_str} has:attachment'

# Note: Would need to modify search_emails() to accept custom query
```

### Batch Processing with Progress Bar

```python
from tqdm import tqdm

messages = reader.search_emails(...)

for msg in tqdm(messages, desc="Extracting PDFs"):
    pdfs, errors = reader.extract_pdfs_from_email(
        message_id=msg['id'],
        output_dir='data/pdfs'
    )
    if pdfs:
        reader.mark_as_processed(msg['id'])
```

### Integration with PDF Extractor

```python
from src.gmail_reader import extract_looker_studio_pdfs
from src.pdf_extractor import PDFExtractor

# Extract PDFs from Gmail
result = extract_looker_studio_pdfs(
    sender_emails=['looker@example.com'],
    output_dir='data/pdfs'
)

# Process extracted PDFs
extractor = PDFExtractor()
for pdf_path in result['pdfs']:
    data = extractor.extract_report_data(pdf_path)
    print(f"Business: {data['business_name']}")
    print(f"KPIs: {data['kpis']}")
```

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review error messages in extraction results
3. Refer to CLAUDE.md for project documentation
4. Check Google Gmail API documentation: https://developers.google.com/gmail/api
