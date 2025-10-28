# Approval Tracker Module - Usage Guide

## Overview

The `ApprovalTracker` module provides a Google Sheets-based approval workflow for reviewing and tracking email approval status. It creates formatted spreadsheets with dropdown validation, conditional formatting, and collaborative editing capabilities.

## Features

- ✅ Create approval sheets with automatic formatting
- ✅ Dropdown validation for status values (Pending, Approved, Needs Revision)
- ✅ Conditional formatting (color-coded status cells)
- ✅ Collaborative editing via Google Sheets
- ✅ Retrieve approved clients for draft creation
- ✅ Track clients needing revision with notes
- ✅ Get approval summary statistics
- ✅ Update statuses programmatically
- ✅ Comprehensive error handling and logging

## Installation

The module requires the following dependencies (already in `requirements.txt`):

```bash
gspread>=5.7.0
google-auth>=2.16.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
```

## Authentication Setup

### 1. Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Enable the following APIs:
   - **Google Sheets API**
   - **Google Drive API**

### 2. Configure OAuth Scopes

The module requires these OAuth scopes (add to `credentials.json` configuration):

```python
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',  # Read/write sheets
    'https://www.googleapis.com/auth/drive.file'     # Create/manage files
]
```

### 3. Update Token Generation

If you're using the existing `token.json` from Gmail API, ensure it includes the Sheets scopes. You may need to:

1. Delete existing `token.json`
2. Re-run authentication with updated scopes
3. Grant permissions when prompted

### 4. Verify Token

The module uses the same `token.json` as `GmailSender`, so authentication is shared:

```python
from src.approval_tracker import ApprovalTracker

tracker = ApprovalTracker(token_path='token.json')
tracker.authenticate()  # Will prompt for login if token missing/invalid
```

## Usage Examples

### 1. Initialize Approval Tracker

```python
from src.approval_tracker import ApprovalTracker

# Basic initialization (uses token.json)
tracker = ApprovalTracker()
tracker.authenticate()

# Custom token path
tracker = ApprovalTracker(token_path='path/to/token.json')
tracker.authenticate()
```

### 2. Create Approval Sheet

```python
# Prepare email data from your workflow
email_data_list = [
    {
        'client_name': 'John Smith',
        'business_name': 'ABC Corporation',
        'recipient_email': 'john@abccorp.com',
        'report_type': 'SEO',
        'extraction_errors': ''  # Empty if no errors
    },
    {
        'client_name': 'Sarah Johnson',
        'business_name': 'XYZ Services',
        'recipient_email': 'sarah@xyzservices.com',
        'report_type': 'SEM',
        'extraction_errors': 'Missing bounce rate metric'
    }
]

# Create sheet
from datetime import datetime
current_month = datetime.now().strftime('%B %Y')
sheet_name = f"Email Approvals - {current_month}"

sheet_id = tracker.create_approval_sheet(sheet_name, email_data_list)
print(f"Sheet created: https://docs.google.com/spreadsheets/d/{sheet_id}")
```

**What happens:**
- Creates new Google Sheet with formatted header
- Populates with email data (all start as "Pending")
- Adds dropdown validation for Status column
- Applies conditional formatting (green=Approved, yellow=Pending, red=Needs Revision)
- Freezes header row
- Auto-resizes columns

### 3. Open Existing Sheet

```python
# Open previously created sheet by ID
sheet_id = '1a2b3c4d5e6f...'  # From create_approval_sheet() or Sheet URL
tracker.open_existing_sheet(sheet_id)
```

### 4. Get Approval Summary

```python
# Get counts for each status
summary = tracker.get_approval_summary()

print(f"Total emails: {summary['total']}")
print(f"Approved: {summary['approved']}")
print(f"Pending: {summary['pending']}")
print(f"Needs Revision: {summary['needs_revision']}")
```

**Output:**
```
Total emails: 30
Approved: 25
Pending: 3
Needs Revision: 2
```

### 5. Get Approved Clients for Draft Creation

```python
# Retrieve list of approved client names
approved_clients = tracker.get_approved_clients()

print(f"Ready to create drafts for {len(approved_clients)} clients:")
for client_name in approved_clients:
    print(f"  - {client_name}")

# Use approved list to filter email data
approved_emails = [
    email for email in all_emails
    if email['client_name'] in approved_clients
]

# Create Gmail drafts for approved emails only
gmail_sender.create_drafts_batch(approved_emails)
```

### 6. Get Clients Needing Revision

```python
# Retrieve clients marked for revision
needs_revision = tracker.get_needs_revision_clients()

print(f"Clients needing revision: {len(needs_revision)}")
for client in needs_revision:
    print(f"  - {client['client_name']} ({client['business_name']})")
    print(f"    Notes: {client['notes']}")
    print(f"    Errors: {client['errors']}")
```

**Output:**
```
Clients needing revision: 2
  - Michael Brown (Tech Solutions LLC)
    Notes: Double-check conversion numbers
    Errors: Missing bounce rate metric
  - Emily Davis (Green Earth Landscaping)
    Notes: Wrong month in subject line
    Errors:
```

### 7. Update Status Programmatically

```python
# Update a client's status
tracker.update_status(
    client_name='John Smith',
    new_status=tracker.STATUS_APPROVED,
    notes='Email looks perfect'
)

# Valid status values:
# - tracker.STATUS_PENDING
# - tracker.STATUS_APPROVED
# - tracker.STATUS_NEEDS_REVISION

# Mark client for revision
tracker.update_status(
    client_name='Sarah Johnson',
    new_status=tracker.STATUS_NEEDS_REVISION,
    notes='PDF extraction failed - need to re-extract'
)
```

## Complete Workflow Example

### Monthly Approval Workflow

```python
from src.approval_tracker import ApprovalTracker
from src.email_generator import EmailGenerator
from src.gmail_sender import GmailSender
from datetime import datetime

# Step 1: Generate emails (from your email generation workflow)
email_generator = EmailGenerator(...)
generated_emails = []

for client in clients:
    email_data = email_generator.generate_email(client, extracted_data)
    generated_emails.append({
        'client_name': client['first_name'] + ' ' + client['last_name'],
        'business_name': client['business_name'],
        'recipient_email': client['email'],
        'report_type': client['service_type'],
        'extraction_errors': email_data.get('errors', ''),
        # Store full email data for later
        'email_subject': email_data['subject'],
        'email_html': email_data['html'],
        'email_text': email_data['text'],
        'pdf_path': email_data['pdf_path']
    })

# Step 2: Create approval sheet
tracker = ApprovalTracker()
tracker.authenticate()

current_month = datetime.now().strftime('%B %Y')
sheet_name = f"Email Approvals - {current_month}"
sheet_id = tracker.create_approval_sheet(sheet_name, generated_emails)

print(f"\n{'='*60}")
print(f"APPROVAL SHEET CREATED")
print(f"{'='*60}")
print(f"URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
print(f"\nPlease review the emails and update statuses:")
print(f"  - Change 'Pending' to 'Approved' for good emails")
print(f"  - Change to 'Needs Revision' if issues found")
print(f"  - Add notes for any revisions needed")
print(f"{'='*60}\n")

input("Press Enter when you've completed your review...")

# Step 3: Read approval results
tracker.open_existing_sheet(sheet_id)
summary = tracker.get_approval_summary()

print(f"\nApproval Summary:")
print(f"  Total: {summary['total']}")
print(f"  Approved: {summary['approved']}")
print(f"  Pending: {summary['pending']}")
print(f"  Needs Revision: {summary['needs_revision']}")

# Step 4: Get approved clients
approved_clients = tracker.get_approved_clients()

# Filter emails to approved only
approved_emails = [
    email for email in generated_emails
    if email['client_name'] in approved_clients
]

# Step 5: Create Gmail drafts for approved emails
gmail_sender = GmailSender()

draft_data = [
    {
        'recipient': email['recipient_email'],
        'subject': email['email_subject'],
        'html_body': email['email_html'],
        'text_body': email['email_text'],
        'attachment_path': email['pdf_path']
    }
    for email in approved_emails
]

results = gmail_sender.create_drafts_batch(draft_data)

print(f"\n{'='*60}")
print(f"DRAFT CREATION COMPLETE")
print(f"{'='*60}")
print(f"Created {results['successful']}/{results['total']} drafts")
print(f"Check your Gmail drafts folder")
print(f"{'='*60}\n")

# Step 6: Handle clients needing revision
needs_revision = tracker.get_needs_revision_clients()

if needs_revision:
    print(f"\n⚠️  Clients needing revision:")
    for client in needs_revision:
        print(f"  - {client['client_name']}")
        print(f"    Notes: {client['notes']}")
        if client['errors']:
            print(f"    Errors: {client['errors']}")
    print("\nPlease address these issues and re-run for these clients.\n")
```

## Sheet Structure

### Columns

| Column | Description | Editable | Notes |
|--------|-------------|----------|-------|
| Client Name | Client's first and last name | No | Auto-populated from email data |
| Business Name | Company name | No | Auto-populated from email data |
| Email | Recipient email address | No | Auto-populated from email data |
| Report Type | SEO or SEM | No | Auto-populated from email data |
| **Status** | Approval status | **Yes** | **Dropdown: Pending, Approved, Needs Revision** |
| **Notes** | Reviewer notes | **Yes** | **Add comments about revisions** |
| Extraction Errors | Errors from PDF extraction | No | Auto-populated if errors occurred |
| Generated Date | Date email was generated | No | Auto-populated timestamp |

### Status Values

- **Pending** (Yellow): Default status, awaiting review
- **Approved** (Green): Email ready for draft creation
- **Needs Revision** (Red): Issues found, requires manual correction

### Visual Formatting

- **Header Row**: Dark blue background, white bold text, frozen
- **Status Column**: Color-coded based on value
  - Green background for Approved
  - Yellow background for Pending
  - Red background for Needs Revision
- **Dropdown**: Status column has dropdown for easy selection
- **Auto-resize**: All columns automatically sized for content

## Best Practices

### 1. Use Descriptive Sheet Names

```python
# Include month/year for easy identification
from datetime import datetime

current_month = datetime.now().strftime('%B %Y')
sheet_name = f"Email Approvals - {current_month}"
# Result: "Email Approvals - January 2025"
```

### 2. Review All Extraction Errors First

```python
# Filter emails with errors before creating sheet
emails_with_errors = [
    email for email in generated_emails
    if email.get('extraction_errors')
]

if emails_with_errors:
    print("⚠️  Emails with extraction errors:")
    for email in emails_with_errors:
        print(f"  - {email['client_name']}: {email['extraction_errors']}")
    print("These will be flagged in the approval sheet.")
```

### 3. Handle Partial Approvals Gracefully

```python
# Get summary first
summary = tracker.get_approval_summary()

if summary['pending'] > 0:
    print(f"⚠️  {summary['pending']} emails still pending")
    response = input("Create drafts for approved emails only? (yes/no): ")
    if response.lower() != 'yes':
        print("Workflow cancelled. Please complete approval first.")
        sys.exit(0)

# Proceed with approved emails only
approved_clients = tracker.get_approved_clients()
```

### 4. Log All Approval Decisions

```python
from src.logger import get_logger

logger = get_logger('ApprovalWorkflow')

# Log approval summary
summary = tracker.get_approval_summary()
logger.info(f"Approval summary: {summary['approved']} approved, "
            f"{summary['needs_revision']} need revision, "
            f"{summary['pending']} pending")

# Log each approved client
for client_name in approved_clients:
    logger.info(f"Approved for draft creation: {client_name}")

# Log revisions
for client in needs_revision:
    logger.warning(f"Needs revision: {client['client_name']} - {client['notes']}")
```

### 5. Archive Approval Sheets

```python
# Save sheet ID for future reference
import json

approval_record = {
    'month': datetime.now().strftime('%Y-%m'),
    'sheet_id': sheet_id,
    'sheet_url': f"https://docs.google.com/spreadsheets/d/{sheet_id}",
    'total_emails': summary['total'],
    'approved': summary['approved'],
    'date_created': datetime.now().isoformat()
}

# Save to approval history
with open('data/approval_history.json', 'a') as f:
    f.write(json.dumps(approval_record) + '\n')
```

## Error Handling

### Common Errors

```python
from src.approval_tracker import ApprovalTracker

tracker = ApprovalTracker()

try:
    tracker.authenticate()
except FileNotFoundError:
    print("Error: token.json not found")
    print("Run Gmail authentication first to generate token.json")

try:
    sheet_id = tracker.create_approval_sheet(sheet_name, email_data)
except Exception as e:
    print(f"Failed to create sheet: {e}")
    print("Check Google Sheets API is enabled")
    print("Verify OAuth scopes include spreadsheets access")

try:
    tracker.open_existing_sheet('invalid_id')
except Exception as e:
    print(f"Failed to open sheet: {e}")
    print("Verify sheet ID is correct")
    print("Ensure you have access to the sheet")

try:
    tracker.update_status('Unknown Client', 'Approved')
except ValueError as e:
    print(f"Error: {e}")
    print("Client not found in sheet")
```

## Testing

### Unit Tests

```bash
# Run unit tests (mocked Google Sheets API)
python -m pytest tests/test_approval_tracker.py -v
```

### Integration Tests

```bash
# Run integration tests (requires real credentials)
python tests/test_approval_tracker_integration.py

# Note: This creates real Google Sheets for testing
```

## Troubleshooting

### Authentication Issues

```
Error: Credentials file not found
Solution: Ensure token.json exists with Sheets API access
          Delete token.json and re-authenticate if needed
          Verify OAuth scopes include spreadsheets

Error: Insufficient permissions
Solution: Re-authenticate with correct scopes:
          - https://www.googleapis.com/auth/spreadsheets
          - https://www.googleapis.com/auth/drive.file
```

### Sheet Access Issues

```
Error: Cannot open sheet
Solution: Verify sheet ID is correct
          Check sheet exists and you have access
          Ensure sheet wasn't deleted

Error: Cannot update sheet
Solution: Verify you have edit permissions
          Check sheet isn't protected
          Ensure cell references are valid
```

### Data Validation Issues

```
Error: Invalid status value
Solution: Use only these status values:
          - tracker.STATUS_PENDING
          - tracker.STATUS_APPROVED
          - tracker.STATUS_NEEDS_REVISION

Error: Client not found
Solution: Verify client_name matches exactly
          Check for extra spaces or formatting
          Use sheet.get_all_records() to see all values
```

## API Reference

### ApprovalTracker Class

```python
class ApprovalTracker:
    # Status constants
    STATUS_PENDING = 'Pending'
    STATUS_APPROVED = 'Approved'
    STATUS_NEEDS_REVISION = 'Needs Revision'

    def __init__(self, credentials_path: str = 'token.json')

    def authenticate(self)

    def create_approval_sheet(
        self,
        sheet_name: str,
        email_data_list: List[Dict]
    ) -> str
    # Returns: sheet_id

    def open_existing_sheet(self, sheet_id: str)

    def get_approved_clients(self) -> List[str]
    # Returns: List of approved client names

    def get_needs_revision_clients(self) -> List[Dict]
    # Returns: List of dicts with client_name, business_name, notes, errors

    def get_approval_summary(self) -> Dict
    # Returns: {'total': int, 'approved': int, 'pending': int, 'needs_revision': int}

    def update_status(
        self,
        client_name: str,
        new_status: str,
        notes: str = ''
    )
```

### Email Data Dictionary Format

```python
{
    'client_name': str,           # Required: Client's name
    'business_name': str,         # Required: Company name
    'recipient_email': str,       # Required: Email address
    'report_type': str,           # Required: 'SEO' or 'SEM'
    'extraction_errors': str      # Optional: Error messages (empty string if none)
}
```

## Integration with Email Reports Workflow

### Complete Monthly Process

```python
# 1. PDF extraction → KPI parsing → Email generation
# (Previous workflow steps...)

# 2. Create approval sheet
tracker = ApprovalTracker()
tracker.authenticate()
sheet_id = tracker.create_approval_sheet(sheet_name, email_data_list)

# 3. User reviews in Google Sheets (manual step)
print(f"Review sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")
input("Press Enter when done...")

# 4. Get approved clients
tracker.open_existing_sheet(sheet_id)
approved = tracker.get_approved_clients()

# 5. Create Gmail drafts for approved only
gmail_sender = GmailSender()
approved_emails = [e for e in emails if e['client_name'] in approved]
gmail_sender.create_drafts_batch(approved_emails)

# 6. Handle revisions
needs_revision = tracker.get_needs_revision_clients()
# Process revisions manually or flag for next run
```

## Version History

- **v1.0** (Phase 3): Initial implementation
  - Create formatted approval sheets
  - Dropdown validation and conditional formatting
  - Read approval status
  - Get approved/needs revision clients
  - Update statuses programmatically
  - Full Google Sheets API integration

## Support

For issues or questions:
1. Check logs in `logs/` folder
2. Review test files for usage examples
3. Verify OAuth scopes include Sheets API access
4. Refer to CLAUDE.md for project context
