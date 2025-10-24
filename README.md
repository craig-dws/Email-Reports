# Email Reports Automation System

**Version 1.0 - Phase 1 (MVP)**

Automated email reporting system that transforms Looker Studio PDF reports into personalized, data-rich client emails with minimal manual intervention.

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Monthly Workflow](#monthly-workflow)
6. [Managing Client Database](#managing-client-database)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Overview

This system automates the monthly client reporting workflow:

1. **Extract** PDF reports from Gmail
2. **Parse** business names and KPI data from PDFs
3. **Match** PDFs to clients in database
4. **Generate** personalized HTML emails
5. **Review** emails via approval workflow
6. **Create** Gmail drafts for approved emails
7. **Send** drafts manually from Gmail

---

## System Requirements

- **Operating System:** Windows 10/11
- **Python:** 3.8 or higher
- **Gmail Account:** Google Workspace account with OAuth access
- **Internet Connection:** Required for Gmail API access
- **Disk Space:** Minimum 500MB for PDFs and logs

---

## Installation & Setup

### Step 1: Verify Python Installation

Open Command Prompt and run:

```bash
py --version
```

You should see Python 3.8 or higher. If not installed, download from [python.org](https://www.python.org/downloads/).

### Step 2: Navigate to Project Directory

```bash
cd "c:\Apps\Email Reports"
```

### Step 3: Install Dependencies

The virtual environment and dependencies should already be set up. To verify:

```bash
venv\Scripts\pip list
```

If dependencies are missing, install them:

```bash
venv\Scripts\pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file with your information:
   - Update `GMAIL_SENDER_EMAIL` with your Gmail address
   - Update `LOOKER_STUDIO_SENDER` with Looker Studio's email
   - Update agency information (name, email, phone, website)
   - Review and customize standard email paragraphs

### Step 5: Set Up Gmail API Credentials

**IMPORTANT:** This is a one-time setup requiring Google Cloud Console access.

#### 5a. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Email Reports Automation"
3. Select the project

#### 5b. Enable Gmail API

1. Go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click **Enable**

#### 5c. Create OAuth Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Configure consent screen (if prompted):
   - User Type: **Internal** (for Google Workspace)
   - App name: "Email Reports Automation"
   - User support email: Your email
   - Developer contact: Your email
4. Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: "Email Reports Desktop"
5. Click **Download JSON**
6. Save downloaded file as `credentials.json` in project root (`c:\Apps\Email Reports\`)

#### 5d. First-Time Authorization

Run the test authentication:

```bash
venv\Scripts\python
>>> from src.gmail_reader import GmailReader
>>> reader = GmailReader()
```

This will:
1. Open your web browser
2. Ask you to log in to Google
3. Request permission to access Gmail
4. Create `token.json` file (stores authorization)

**Note:** `token.json` is created automatically and will be reused for future runs.

### Step 6: Set Up Client Database

1. Open `data\clients.csv` in Excel or Google Sheets
2. Add your client information (see [Managing Client Database](#managing-client-database))
3. Save as CSV

---

## Configuration

### Environment Variables (.env file)

| Variable | Description | Example |
|----------|-------------|---------|
| `GMAIL_SENDER_EMAIL` | Your Gmail address | `youragency@gmail.com` |
| `LOOKER_STUDIO_SENDER` | Looker Studio sender email | `noreply-looker@google.com` |
| `CLIENT_DATABASE_PATH` | Path to clients.csv | `c:/Apps/Email Reports/data/clients.csv` |
| `PDF_STORAGE_PATH` | Where to save PDFs | `c:/Apps/Email Reports/data/pdfs/` |
| `FUZZY_MATCH_THRESHOLD` | Matching sensitivity (0-100) | `85` |
| `AGENCY_NAME` | Your agency name | `Digital Marketing Pro` |
| `AGENCY_EMAIL` | Contact email | `contact@youragency.com` |
| `AGENCY_PHONE` | Contact phone | `(555) 123-4567` |
| `STANDARD_SEO_PARAGRAPH` | Default SEO text | See `.env.example` |
| `STANDARD_SEM_PARAGRAPH` | Default SEM text | See `.env.example` |

---

## Monthly Workflow

### Overview

Each month, follow these steps to send reports to all 30 clients:

1. Wait for Looker Studio PDFs to arrive in Gmail
2. Run extraction and email generation
3. Review generated emails
4. Approve emails in CSV
5. Create Gmail drafts
6. Manually send drafts from Gmail

### Detailed Steps

#### Step 1: Wait for PDFs

Looker Studio sends PDF reports to your Gmail at the start of each month. Wait until all ~30 PDFs have arrived (usually within a few hours).

#### Step 2: Run Full Workflow

Open Command Prompt and navigate to project directory:

```bash
cd "c:\Apps\Email Reports"
venv\Scripts\python main.py --full
```

This will:
- Extract all PDFs from Gmail
- Parse business names and KPIs
- Match to clients in database
- Generate personalized emails
- Create approval tracking CSV and HTML

**Expected Output:**
```
==============================================================
RUNNING FULL WORKFLOW
==============================================================

[2025-01-05 09:15:00] [INFO] [EmailReports] Starting monthly report processing
[2025-01-05 09:15:05] [INFO] [GmailReader] Found 30 emails from looker-studio@google.com
[2025-01-05 09:15:10] [INFO] [PDFExtractor] Extracting data from: ABC Corporation - January 2025.pdf
...
[2025-01-05 09:20:00] [INFO] [EmailReports] Processing complete

==============================================================
WORKFLOW SUMMARY
==============================================================
Total PDFs processed: 30
Emails generated: 28
Approved: 0
Pending: 26
Needs Revision: 2
==============================================================
```

#### Step 3: Review Generated Emails

Open the approval review HTML file:

```
c:\Apps\Email Reports\data\approval_review.html
```

This shows all generated emails with status:

- **Pending** (green): No errors, ready for approval
- **Needs Revision** (red): Extraction errors, requires manual check

Review each email carefully:
- Check business name matches client
- Verify KPI data looks reasonable
- Confirm personalized text is appropriate
- Check for extraction errors

#### Step 4: Approve Emails

Open the approval tracking CSV:

```
c:\Apps\Email Reports\data\approval_tracking.csv
```

For each row, update the **Status** column:
- Change `Pending` to `Approved` (for emails you've reviewed and approved)
- Change `Pending` to `Needs Revision` (if you found issues)
- Add notes in **Notes** column if needed

**Save the file** after making changes.

**Quick Approve (Use with Caution):**

To auto-approve all emails without extraction errors:

```bash
venv\Scripts\python main.py --approve-all
```

**WARNING:** Only use this if you've spot-checked several emails and trust the extraction quality.

#### Step 5: Create Gmail Drafts

After approving emails in the CSV, create Gmail drafts:

```bash
venv\Scripts\python main.py --create-drafts
```

This creates draft emails in your Gmail account for all approved emails.

#### Step 6: Send Drafts Manually

1. Open Gmail in your browser
2. Go to **Drafts** folder
3. Open each draft, review one final time
4. Click **Send**

**Recommended Sending Pace:**
- Send 5-10 emails
- Wait 10-15 minutes
- Send next batch
- This spacing helps avoid spam flags

**Estimated Time:** 20-30 minutes to send all 30 emails

---

## Managing Client Database

### Database Location

```
c:\Apps\Email Reports\data\clients.csv
```

### Database Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `ClientID` | Auto | Unique ID (auto-generated) | `1` |
| `FirstName` | Yes | Client's first name | `John` |
| `BusinessName` | Yes | Company name (must match PDF) | `ABC Corporation` |
| `Email` | Yes | Client email address | `john@abc.com` |
| `ServiceType` | Yes | `SEO` or `SEM` | `SEO` |
| `PersonalizedText` | No | Custom 1-2 lines for email | `Great work on content updates.` |
| `Active` | Yes | `TRUE` or `FALSE` | `TRUE` |
| `CreatedDate` | Auto | Date added | `2024-01-15` |
| `LastModifiedDate` | Auto | Last updated | `2025-01-05` |

### Adding a New Client

1. Open `data\clients.csv` in Excel
2. Add new row at bottom
3. Fill in: FirstName, BusinessName, Email, ServiceType, PersonalizedText
4. Set Active to `TRUE`
5. Leave ClientID, CreatedDate, LastModifiedDate blank (auto-generated)
6. Save file

### Updating Client Information

1. Open `data\clients.csv`
2. Find client row
3. Edit fields as needed
4. Update `LastModifiedDate` to today's date
5. Save file

### Deactivating a Client

Change `Active` from `TRUE` to `FALSE`. The client won't appear in future matching.

### Backup Recommendation

**Back up `clients.csv` weekly** to Google Drive or external storage.

---

## Troubleshooting

### "Gmail credentials not found"

**Problem:** Missing `credentials.json` file

**Solution:**
1. Follow [Step 5: Set Up Gmail API Credentials](#step-5-set-up-gmail-api-credentials)
2. Download credentials from Google Cloud Console
3. Save as `credentials.json` in project root

### "Client database not found"

**Problem:** Missing or misnamed `clients.csv`

**Solution:**
1. Check file exists: `c:\Apps\Email Reports\data\clients.csv`
2. Verify path in `.env` file matches actual location

### "No PDFs found to process"

**Problem:** No PDFs in Gmail or storage directory

**Solution:**
- Check Gmail inbox for Looker Studio emails
- Verify `LOOKER_STUDIO_SENDER` email in `.env` is correct
- Try manually running: `python main.py --extract-only`

### "No match found for business name"

**Problem:** PDF business name doesn't match any client in database

**Solution:**
1. Check spelling in PDF (open PDF manually)
2. Check spelling in `clients.csv`
3. Fuzzy matching allows minor differences (85% similarity)
4. Add client to database if they're new

### "Failed to extract KPI data"

**Problem:** PDF format changed or table structure different

**Solution:**
1. Open problematic PDF manually
2. Check if KPI table exists and is readable
3. If format changed significantly, contact support (may need code update)

### Emails going to spam

**Problem:** Clients report emails in spam folder

**Solution:**
- Send emails in smaller batches (5-10 at a time)
- Space sends 10-15 minutes apart
- Ask clients to add your email to contacts
- Check Google Workspace SPF/DKIM records

---

## FAQ

### How often should I back up the client database?

**Weekly** or before any major changes. Copy `data\clients.csv` to Google Drive or external backup.

### Can I customize the email template?

Yes. Edit `templates\email_template.html`. Use Jinja2 syntax for dynamic content. Be careful with HTML email formatting (inline CSS required for email client compatibility).

### What if Looker Studio changes the PDF format?

The system may fail to extract data correctly. Contact technical support for an update to the PDF extraction logic.

### Can I add new KPIs beyond the default 6?

Yes, but requires code modification. The current system extracts: Sessions, Conversions, Active Users, Engagement Rate, Bounce Rate, Average Session Duration.

### What happens to PDFs after processing?

PDFs remain in `data\pdfs\` directory. You can manually move them to `data\archive\` for long-term storage.

### Can I run this on a schedule?

Not in Phase 1 (MVP). Phase 2 will add automated scheduling. For now, run manually each month.

### How do I update personalized text for a client?

1. Open `data\clients.csv`
2. Find client row
3. Update `PersonalizedText` column
4. Update `LastModifiedDate` to current date
5. Save file

### What if I accidentally approve the wrong email?

Before creating drafts:
1. Open `data\approval_tracking.csv`
2. Change Status back to `Pending` or `Needs Revision`
3. Save file

After creating drafts:
1. Go to Gmail Drafts
2. Delete the incorrect draft
3. Regenerate after fixing in CSV

---

## Support & Feedback

For issues, questions, or feedback:

1. Check logs in `logs\` directory for detailed error information
2. Review this README and troubleshooting section
3. Contact system administrator

---

**Email Reports Automation System v1.0**
*Built for efficiency, designed for reliability*
