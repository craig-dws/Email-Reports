# Gmail Sender Module - Usage Guide

## Overview

The `GmailSender` module provides comprehensive functionality for creating Gmail drafts and sending emails via the Gmail API. It includes built-in retry logic, rate limiting, and support for spaced-out sending to avoid spam flags.

## Features

- ✅ Create Gmail drafts with HTML content and PDF attachments
- ✅ Send emails directly via Gmail API
- ✅ Send preview emails with visual headers for approval workflow
- ✅ Batch draft creation with error tracking
- ✅ Spaced sending with configurable delays (default: 5 minutes)
- ✅ Exponential backoff retry logic for rate limits
- ✅ Comprehensive error handling and logging
- ✅ Delete and list drafts functionality

## Installation

The module requires the following dependencies (already in `requirements.txt`):

```bash
google-api-python-client>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=0.5.0
```

## Authentication

The module uses OAuth 2.0 authentication with the Gmail API. Required scopes:

```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.compose',  # Create drafts
    'https://www.googleapis.com/auth/gmail.modify',   # Modify drafts
    'https://www.googleapis.com/auth/gmail.send'      # Send emails
]
```

### Setup

1. Place `credentials.json` in project root (from Google Cloud Console)
2. Run initial authentication (will create `token.json`)
3. Token automatically refreshes when expired

## Usage Examples

### 1. Initialize Gmail Sender

```python
from src.gmail_sender import GmailSender

# Basic initialization
sender = GmailSender()

# Custom configuration
sender = GmailSender(
    credentials_path='path/to/credentials.json',
    token_path='path/to/token.json',
    send_delay=300  # 5 minutes between sends (in seconds)
)
```

### 2. Create a Single Draft

```python
# Create draft with HTML content
draft = sender.create_draft(
    recipient='client@example.com',
    subject='Your January 2025 SEO Report',
    html_body='<h1>Monthly Report</h1><p>See attached PDF.</p>',
    text_body='Monthly Report - See attached PDF.',
    attachment_path='data/reports/client_report.pdf'
)

print(f"Draft created: {draft['id']}")
```

### 3. Create Multiple Drafts in Batch

```python
# Prepare draft data
draft_data_list = [
    {
        'recipient': 'client1@example.com',
        'subject': 'Your January 2025 SEO Report',
        'html_body': '<p>Report for Client 1</p>',
        'text_body': 'Report for Client 1',
        'attachment_path': 'data/reports/client1_report.pdf'
    },
    {
        'recipient': 'client2@example.com',
        'subject': 'Your January 2025 Google Ads Report',
        'html_body': '<p>Report for Client 2</p>',
        'text_body': 'Report for Client 2',
        'attachment_path': 'data/reports/client2_report.pdf'
    }
]

# Create batch
results = sender.create_drafts_batch(draft_data_list)

print(f"Created {results['successful']}/{results['total']} drafts")
if results['errors']:
    print(f"Errors: {results['errors']}")
```

### 4. Send Preview Email for Approval

```python
# Send preview to review address with visual header
sender.send_preview_email(
    preview_recipient='owner@agency.com',
    original_recipient='client@example.com',
    subject='Your January 2025 SEO Report',
    html_body='<p>Your monthly report is ready!</p>',
    text_body='Your monthly report is ready!',
    attachment_path='data/reports/client_report.pdf'
)

# The preview email will include:
# - [PREVIEW] tag in subject line
# - Visual header showing original recipient
# - Original email content below
```

### 5. Send Email Directly

```python
# Send email without creating draft first
sent_message = sender.send_email(
    recipient='client@example.com',
    subject='Your Monthly Report',
    html_body='<p>Your report is attached.</p>',
    text_body='Your report is attached.',
    attachment_path='data/reports/report.pdf'
)

print(f"Email sent: {sent_message['id']}")
```

### 6. Send Drafts with Spaced Delay

```python
# Get draft IDs (e.g., from approval workflow)
draft_ids = ['draft_id_1', 'draft_id_2', 'draft_id_3']

# Send drafts with 5-minute delays between each
results = sender.send_drafts_with_delay(
    draft_ids=draft_ids,
    delay_seconds=300  # 5 minutes
)

print(f"Sent {results['successful']}/{results['total']} drafts")
if results['errors']:
    for error in results['errors']:
        print(f"Failed draft {error['draft_id']}: {error['error']}")
```

### 7. Send Emails with Spaced Delay

```python
# Prepare email data
email_data_list = [
    {
        'recipient': 'client1@example.com',
        'subject': 'Report 1',
        'html_body': '<p>Report 1</p>',
        'text_body': 'Report 1',
        'attachment_path': 'data/reports/report1.pdf'
    },
    {
        'recipient': 'client2@example.com',
        'subject': 'Report 2',
        'html_body': '<p>Report 2</p>',
        'text_body': 'Report 2',
        'attachment_path': 'data/reports/report2.pdf'
    }
]

# Send with 5-minute delays
results = sender.send_emails_with_delay(
    email_data_list=email_data_list,
    delay_seconds=300
)

print(f"Sent {results['successful']}/{results['total']} emails")
```

### 8. List and Manage Drafts

```python
# List existing drafts
drafts = sender.list_drafts(max_results=50)
print(f"Found {len(drafts)} drafts")

for draft in drafts:
    print(f"Draft ID: {draft['id']}")

# Delete a draft
sender.delete_draft('draft_id_to_delete')
```

## Error Handling

The module includes robust error handling:

### Automatic Retry Logic

```python
# Automatically retries on:
# - Rate limit errors (429)
# - Server errors (500, 503)
# - Network errors

# Retry configuration:
MAX_RETRIES = 3
INITIAL_BACKOFF = 1  # seconds (exponential: 1s, 2s, 4s)
```

### Exception Handling

```python
from src.gmail_sender import GmailSender

sender = GmailSender()

try:
    draft = sender.create_draft(
        recipient='client@example.com',
        subject='Test',
        html_body='<p>Test</p>'
    )
except FileNotFoundError as e:
    print(f"Credentials not found: {e}")
except Exception as e:
    print(f"Draft creation failed: {e}")
    # Check logs for detailed error information
```

## Configuration Options

### Send Delay

Control spacing between email sends:

```python
# Fast testing (1 minute)
sender = GmailSender(send_delay=60)

# Normal production (5 minutes)
sender = GmailSender(send_delay=300)

# Conservative (10 minutes)
sender = GmailSender(send_delay=600)
```

### Credentials Path

```python
# Custom credential locations
sender = GmailSender(
    credentials_path='/path/to/credentials.json',
    token_path='/path/to/token.json'
)
```

## Best Practices

### 1. Spaced Sending for Large Batches

```python
# For 30 client emails, use 5-10 minute delays
sender = GmailSender(send_delay=300)  # 5 minutes

# Total send time: 30 emails * 5 minutes = ~2.5 hours
# This avoids spam flags and improves deliverability
```

### 2. Use Preview Emails for Approval

```python
# Send previews to review address before creating drafts
for client in clients:
    sender.send_preview_email(
        preview_recipient='owner@agency.com',
        original_recipient=client['email'],
        subject=f"Your {month} {service_type} Report",
        html_body=generated_html,
        attachment_path=client['pdf_path']
    )

# Review previews, then create drafts only for approved emails
```

### 3. Handle Batch Errors Gracefully

```python
results = sender.create_drafts_batch(draft_data_list)

# Log successful drafts
for draft_id in results['draft_ids']:
    log.info(f"Created draft: {draft_id}")

# Handle failures
for error in results['errors']:
    log.error(f"Failed for {error['recipient']}: {error['error']}")
    # Retry individually or flag for manual review
```

### 4. Monitor Logs

```python
# All operations are logged to logs/ folder
# Check logs for:
# - Authentication status
# - Draft creation success/failure
# - Send status
# - Retry attempts
# - Error details
```

## Integration with Email Reports Workflow

### Typical Monthly Workflow

```python
from src.gmail_sender import GmailSender
from src.email_generator import EmailGenerator

# 1. Generate emails
email_generator = EmailGenerator(...)
emails = []

for client in clients:
    email_data = email_generator.generate_email(client, extracted_data)
    emails.append({
        'recipient': client['email'],
        'subject': email_data['subject'],
        'html_body': email_data['html'],
        'text_body': email_data['text'],
        'attachment_path': client['pdf_path']
    })

# 2. Send preview emails for approval
sender = GmailSender()
for email in emails:
    sender.send_preview_email(
        preview_recipient='owner@agency.com',
        original_recipient=email['recipient'],
        subject=email['subject'],
        html_body=email['html_body'],
        text_body=email['text_body'],
        attachment_path=email['attachment_path']
    )

# 3. After approval, create drafts
approved_emails = [e for e in emails if e['approved']]
results = sender.create_drafts_batch(approved_emails)

# 4. User manually sends drafts from Gmail
# (Or use send_drafts_with_delay for automated spaced sending)
```

## Testing

### Unit Tests

```bash
# Run unit tests (mocked Gmail API)
python -m pytest tests/test_gmail_sender.py -v
```

### Integration Tests

```bash
# Run integration tests (requires real credentials)
python tests/test_gmail_sender_integration.py

# Note: Update test email addresses in the script before running
```

## Troubleshooting

### Authentication Issues

```
Error: Credentials file not found
Solution: Ensure credentials.json exists in project root

Error: Token expired
Solution: Delete token.json and re-authenticate
```

### Rate Limiting

```
Error: Rate limit exceeded (429)
Solution: Module automatically retries with backoff
         Increase send_delay for large batches
```

### Attachment Issues

```
Error: Attachment file not found
Solution: Verify PDF path is correct and file exists
         Use absolute paths or Path objects
```

### Draft Creation Failures

```
Error: Failed to create draft
Solution: Check logs/ for detailed error message
         Verify HTML body is valid
         Ensure recipient email is valid
```

## API Reference

### GmailSender Class

```python
class GmailSender:
    def __init__(self,
                 credentials_path: str = 'credentials.json',
                 token_path: str = 'token.json',
                 send_delay: int = 300)

    def create_draft(self,
                     recipient: str,
                     subject: str,
                     html_body: str,
                     text_body: str = "",
                     attachment_path: Optional[str] = None) -> Dict

    def create_drafts_batch(self, draft_data_list: list) -> Dict[str, any]

    def send_email(self,
                   recipient: str,
                   subject: str,
                   html_body: str,
                   text_body: str = "",
                   attachment_path: Optional[str] = None) -> Dict

    def send_preview_email(self,
                          preview_recipient: str,
                          original_recipient: str,
                          subject: str,
                          html_body: str,
                          text_body: str = "",
                          attachment_path: Optional[str] = None) -> Dict

    def send_draft(self, draft_id: str) -> Dict

    def send_drafts_with_delay(self,
                               draft_ids: List[str],
                               delay_seconds: Optional[int] = None) -> Dict[str, any]

    def send_emails_with_delay(self,
                               email_data_list: List[Dict],
                               delay_seconds: Optional[int] = None) -> Dict[str, any]

    def delete_draft(self, draft_id: str)

    def list_drafts(self, max_results: int = 50) -> list
```

## Version History

- **v1.0** (Phase 3): Initial implementation
  - Draft creation with attachments
  - Email sending
  - Preview emails
  - Batch operations
  - Retry logic
  - Spaced sending

## Support

For issues or questions:
1. Check logs in `logs/` folder
2. Review test files for usage examples
3. Refer to CLAUDE.md for project context
