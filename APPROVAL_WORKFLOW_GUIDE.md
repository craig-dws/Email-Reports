# Approval Workflow Guide

## Overview

The approval workflow is a critical component of the Email Reports Automation System that allows you to review generated emails before sending them to clients. This ensures quality control and prevents sending incorrect data or malformed emails.

## Workflow Components

### 1. Approval Tracking CSV
**Location:** `data/approval_tracking.csv`

This CSV file tracks the approval status of all generated emails.

**Columns:**
- `ClientID`: Unique identifier for the client
- `BusinessName`: Business name extracted from PDF
- `EmailSubject`: Generated email subject line
- `Status`: Current approval status (see Status Values below)
- `Notes`: Optional notes about the email (for your reference)
- `ExtractionErrors`: Any errors encountered during PDF extraction
- `CreatedDate`: When the review entry was created
- `UpdatedDate`: When the status was last updated

**Status Values:**
- `Pending`: Email generated successfully, awaiting your review
- `Approved`: You've reviewed and approved this email for sending
- `Needs Revision`: Email has issues and requires manual attention
- `Sent`: Email has been sent to the client

### 2. Approval Review HTML
**Location:** `data/approval_review.html`

This HTML file provides a visual overview of all emails for easy review.

**Features:**
- Color-coded status indicators
- All email details in one place
- Extraction errors highlighted
- Easy to spot issues at a glance

**Color Coding:**
- 🟢 **Green (Pending)**: No errors, ready for approval
- 🔴 **Red (Needs Revision)**: Extraction errors, requires manual check
- 🔵 **Blue (Sent)**: Already sent to client
- 🟡 **Yellow (Approved)**: Approved, ready for draft creation

## Step-by-Step Approval Process

### Step 1: Generate Emails

Run the full workflow or process existing PDFs:

```bash
# Full workflow (extract from Gmail + process)
venv\Scripts\python main.py --full

# Or process existing PDFs
venv\Scripts\python main.py --process-pdfs
```

This creates:
- `data/approval_tracking.csv` with all emails
- `data/approval_review.html` for visual review

### Step 2: Open Review HTML

Open `data/approval_review.html` in your web browser to get an overview of all generated emails.

**What to Look For:**
- ❌ Red rows indicate extraction errors (review these first)
- ✅ Green rows indicate successful extraction (still need approval)
- Check that business names match your client database
- Verify KPI data looks reasonable (no negative values, percentages in range, etc.)

### Step 3: Review Each Email

For each email in the review HTML:

1. **Check Business Name**
   - Does it match the client you expect?
   - Is it spelled correctly?

2. **Check Email Subject**
   - Is the month/year correct?
   - Is the report type correct (SEO vs Google Ads)?

3. **Check Extraction Errors**
   - If errors are listed, you'll need to manually verify the email
   - Common errors: missing KPIs, malformed data

### Step 4: Update Approval Status

Open `data/approval_tracking.csv` in Excel or a text editor.

**For Emails with No Errors:**
1. Change `Status` from `Pending` to `Approved`
2. Save the file

**For Emails with Errors:**
1. Change `Status` to `Needs Revision`
2. Add notes in the `Notes` column explaining what needs fixing
3. Save the file

**Example CSV Edit:**

Before:
```csv
1,ABC Corporation,Your January 2025 SEO Report,Pending,,,2025-01-05 09:15:00,2025-01-05 09:15:00
```

After:
```csv
1,ABC Corporation,Your January 2025 SEO Report,Approved,Looks good!,,2025-01-05 09:15:00,2025-01-05 09:15:00
```

### Step 5: Auto-Approve (Optional)

If you've spot-checked several emails and trust the extraction quality, you can auto-approve all emails without extraction errors:

```bash
venv\Scripts\python main.py --approve-all
```

**⚠️ WARNING:** Only use this if:
- You've manually reviewed at least 5-10 emails
- The extraction quality looks consistently good
- You're comfortable taking the risk of sending without full manual review

### Step 6: Create Gmail Drafts

After approving emails, create Gmail drafts:

```bash
venv\Scripts\python main.py --create-drafts
```

This creates draft emails in Gmail for **only** the approved emails.

**Output:**
```
==============================================================
CREATING GMAIL DRAFTS FOR APPROVED EMAILS
==============================================================

[2025-01-05 09:25:00] [INFO] [GmailSender] Creating draft for ABC Corporation
[2025-01-05 09:25:05] [INFO] [GmailSender] Creating draft for XYZ Services
...

==============================================================
DRAFT CREATION COMPLETE
==============================================================
Total drafts created: 28
Failed: 0
==============================================================
```

### Step 7: Review Drafts in Gmail

1. Open Gmail in your web browser
2. Go to **Drafts** folder
3. You'll see all approved emails as drafts

**Final Review:**
- Open each draft and review one last time
- Check that PDF is attached
- Verify recipient email address is correct
- Check that email looks professional and correct

### Step 8: Send Drafts

Send drafts manually with spacing to avoid spam flags.

**Recommended Approach:**
1. Send 5-10 emails
2. Wait 10-15 minutes
3. Send next 5-10 emails
4. Repeat until all sent

**Estimated Time:** 20-30 minutes to send all 30 emails

## Handling Problem Emails

### Email with Extraction Errors

**Scenario:** `ExtractionErrors` column shows errors like "Missing bounce rate" or "Business name not in database"

**Resolution:**
1. Mark status as `Needs Revision` in CSV
2. Manually open the PDF and verify the data
3. If data is missing from PDF, you may need to:
   - Contact client for missing data
   - Skip this client this month
   - Manually create email outside the system

### Business Name Mismatch

**Scenario:** Business name in PDF doesn't match your client database

**Resolution:**
1. Check if it's a fuzzy matching issue (e.g., "ABC Corp" vs "ABC Corporation")
2. Update `data/clients.csv` to match PDF business name exactly
3. Re-run processing: `venv\Scripts\python main.py --process-pdfs`

### Wrong Report Type

**Scenario:** Email subject says "SEO Report" but client should get "Google Ads Report"

**Resolution:**
1. This indicates the PDF was misclassified
2. Check PDF filename - does it contain "Google Ads"?
3. May need to manually update the email or regenerate

### Missing KPI Data

**Scenario:** Extraction errors indicate missing KPI values

**Resolution:**
1. Open the PDF and check if the KPI is actually present
2. If PDF is missing the KPI, mark as `Needs Revision`
3. If PDF has the KPI but extraction failed, this is a bug - report it

## Best Practices

### ✅ DO

- **Review at least 5-10 emails manually** even if using auto-approve
- **Check extraction errors first** - these are most likely to have issues
- **Save the CSV file after every change** - changes won't take effect until saved
- **Spot-check random emails** for quality assurance
- **Keep notes in the Notes column** for future reference

### ❌ DON'T

- **Don't auto-approve without spot-checking** - always verify a sample
- **Don't edit the CSV while the system is running** - wait for processing to complete
- **Don't delete rows from the CSV** - mark as `Needs Revision` instead
- **Don't change the CSV headers** - this will break the system
- **Don't send all drafts at once** - space them out to avoid spam flags

## Troubleshooting

### Problem: CSV file won't open in Excel

**Solution:**
- The file is UTF-8 encoded
- Try opening with Notepad++ or Google Sheets
- Or use Excel's "Get Data" → "From Text/CSV" import feature

### Problem: Changes to CSV not taking effect

**Solution:**
- Make sure you saved the file after editing
- Check that you changed the `Status` column (not a different column)
- Valid status values: `Approved`, `Pending`, `Needs Revision`, `Sent`

### Problem: No emails showing as approved

**Solution:**
- Verify you changed `Status` from `Pending` to `Approved`
- Make sure you saved the CSV file
- Check that status value is exactly `Approved` (case-sensitive)

### Problem: Draft creation fails for some emails

**Solution:**
- Check `logs/` directory for error messages
- Verify Gmail API credentials are working
- Check that approved emails have valid recipient email addresses

## Monthly Workflow Summary

1. **Run full workflow**: `python main.py --full`
2. **Open review HTML**: `data/approval_review.html`
3. **Review emails** for quality and errors
4. **Update CSV**: Change status to `Approved` for good emails
5. **Auto-approve** (optional): `python main.py --approve-all`
6. **Create drafts**: `python main.py --create-drafts`
7. **Review drafts** in Gmail
8. **Send drafts** manually with spacing

**Total Time:** 30-45 minutes per month (for 30 clients)

## Advanced Features

### Exporting Review to Custom HTML

The system automatically generates `data/approval_review.html`, but you can also export programmatically:

```python
from src.approval_workflow import ApprovalWorkflow

workflow = ApprovalWorkflow('data/approval_tracking.csv')
workflow.export_review_html('my_custom_review.html')
```

### Programmatic Status Updates

If you want to build automation on top of the approval workflow:

```python
from src.approval_workflow import ApprovalWorkflow

workflow = ApprovalWorkflow('data/approval_tracking.csv')

# Update status for specific client
workflow.update_status('1', ApprovalWorkflow.STATUS_APPROVED, 'Looks good!')

# Get summary statistics
summary = workflow.get_summary()
print(f"Approved: {summary['approved']}")
print(f"Pending: {summary['pending']}")
print(f"Needs Revision: {summary['needs_revision']}")
```

### Bulk Approval

To approve all emails without extraction errors (use with caution):

```python
from src.approval_workflow import ApprovalWorkflow

workflow = ApprovalWorkflow('data/approval_tracking.csv')

# Get all pending reviews without errors
pending = workflow.get_pending_reviews()

for review in pending:
    if not review['ExtractionErrors']:
        workflow.update_status(
            review['ClientID'],
            ApprovalWorkflow.STATUS_APPROVED,
            'Auto-approved'
        )
```

## Support

If you encounter issues with the approval workflow:

1. Check `logs/` directory for error messages
2. Review this guide for common issues
3. Consult `README.md` for general troubleshooting
4. Check `data/approval_tracking.csv` for data integrity issues

---

**Last Updated:** 2025-10-28
**Version:** 1.0
