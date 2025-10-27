# Setting Up Your .env File

## Quick Setup Instructions

1. Copy the content below into your `.env` file (located at `c:\Apps\Email Reports\.env`)
2. Replace the placeholder values with your actual information
3. Save the file

---

## Copy This Into Your .env File:

```env
# =============================================================================
# EMAIL REPORTS AUTOMATION - ENVIRONMENT CONFIGURATION
# =============================================================================

# =============================================================================
# GMAIL CONFIGURATION
# =============================================================================
# Your agency Gmail account (the one you authorized with OAuth)
GMAIL_SENDER_EMAIL=your-email@gmail.com

# Looker Studio sender emails (comma-separated, no spaces)
LOOKER_STUDIO_SENDERS=discover.sem.manager@gmail.com,discover.web.seo@gmail.com,discover.web.seo2@gmail.com,discover.web.seo3@gmail.com,luna.digital.seo.au@gmail.com

# =============================================================================
# FILE PATHS (Leave these as-is - they're already correct)
# =============================================================================
CLIENT_DATABASE_PATH=c:/Apps/Email Reports/data/clients.csv
PDF_STORAGE_PATH=c:/Apps/Email Reports/data/pdfs/
PDF_ARCHIVE_PATH=c:/Apps/Email Reports/data/archive/
TEMPLATE_PATH=c:/Apps/Email Reports/templates/email_template.html
APPROVAL_TRACKING_PATH=c:/Apps/Email Reports/data/approval_tracking.csv
LOG_PATH=c:/Apps/Email Reports/logs/

# =============================================================================
# PROCESSING CONFIGURATION (Leave these as-is)
# =============================================================================
FUZZY_MATCH_THRESHOLD=85
LOG_LEVEL=INFO
MAX_PDFS_PER_RUN=50

# =============================================================================
# AGENCY INFORMATION (Replace with your details)
# =============================================================================
AGENCY_NAME=Your Agency Name
AGENCY_EMAIL=your-email@gmail.com
AGENCY_PHONE=+61 (02) XXXX XXXX
AGENCY_WEBSITE=www.youragency.com

# =============================================================================
# EMAIL CONTENT TEXT
# =============================================================================
# Standard paragraph that appears in ALL SEO emails (after the client-specific intro)
STANDARD_SEO_PARAGRAPH=Throughout the month we have been focusing upon on-page and off-page SEO to improve the websites online presence. You can find your current keyword rankings in the same attached SEO report. The following shows some key KPI data for Organic Search Traffic ONLY. These KPIs will help to track visitor traffic resulting from SEO activities.

# Standard paragraph for Google Ads emails
STANDARD_GOOGLE_ADS_PARAGRAPH=Please see attached reports for Your Google Ads Campaign. The following table shows some key KPI data for Google Ads ONLY. These KPIs will help to track visitor traffic resulting from Google Ads activities.

# Closing text that appears AFTER the KPI table in ALL emails
STANDARD_CLOSING_PARAGRAPH=Either myself or Mitch would be happy to take you through the reports if you have any questions please let us know.

# =============================================================================
# EMAIL SIGNATURE
# =============================================================================
AGENCY_SIGNATURE=Thanks
```

---

## What You Need to Change:

### Required Changes:

1. **GMAIL_SENDER_EMAIL** - Your Gmail address (the one you authorized earlier)
2. **AGENCY_NAME** - Your agency's name
3. **AGENCY_EMAIL** - Your contact email
4. **AGENCY_PHONE** - Your phone number
5. **AGENCY_WEBSITE** - Your website URL

### Already Configured (No Changes Needed):

- **LOOKER_STUDIO_SENDERS** - Already has all 5 Looker Studio emails
- **File paths** - Already pointing to the correct directories
- **STANDARD_CLOSING_PARAGRAPH** - Already has your standard text
- **AGENCY_SIGNATURE** - Already set to "Thanks"

---

## System Features Based on Your Requirements:

### ✅ Multiple Looker Studio Emails
The system will check for PDFs from ALL 5 Looker Studio email addresses:
- discover.sem.manager@gmail.com
- discover.web.seo@gmail.com
- discover.web.seo2@gmail.com
- discover.web.seo3@gmail.com
- luna.digital.seo.au@gmail.com

### ✅ Auto-Detection of Report Type
The system automatically detects whether each PDF is:
- **SEO Report** - Extracts: Sessions, Conversions, Active Users, Engagement Rate, Bounce Rate, Avg Session Duration
- **Google Ads Report** - Extracts: Clicks, Conversions, Impressions, CTR, Conversion Rate, Average CPC, Cost

### ✅ Greeting from clients.csv
The greeting ("Hi [Name],") comes from the `Contact-Name` column in your clients.csv

### ✅ Introduction Text from clients.csv
- **SEO emails** use the `SEO-Introduction` column
- **Google Ads emails** use the `Google-Ads-Introduction` column

### ✅ Custom One-Off Text
You can add custom text manually during the approval workflow (e.g., when there's a Google Algorithm update)

---

## Next Steps After Configuring .env:

1. ✅ Configure .env file (you're doing this now)
2. ⏳ Your clients.csv is already populated with 30 clients
3. ⏳ Test the system with sample PDFs
4. ⏳ Run the approval workflow
5. ⏳ Send your first batch of reports!

---

## Questions?

- Check [README.md](README.md) for complete user guide
- Check [QUICKSTART.md](QUICKSTART.md) for step-by-step testing instructions
- Check [PHASE1_COMPLETION_STATUS.md](PHASE1_COMPLETION_STATUS.md) for system status
