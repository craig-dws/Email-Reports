# Email Reports Automation - Quick Start Guide

**Get up and running in 30 minutes!**

---

## ⚡ Quick Setup Checklist

### 1. Verify Installation (5 minutes)

```bash
cd "c:\Apps\Email Reports"
venv\Scripts\python setup_verify.py
```

✅ **Expected:** All checks should pass except Gmail credentials

❌ **If dependencies fail:** Run this command:
```bash
venv\Scripts\pip install -r requirements.txt
```

---

### 2. Configure Agency Settings (5 minutes)

Edit the `.env` file:

```bash
notepad .env
```

**Replace these values:**

```ini
# Your Gmail address
GMAIL_SENDER_EMAIL=youragency@gmail.com

# Looker Studio's sender email (check your Gmail)
LOOKER_STUDIO_SENDER=noreply-looker@google.com

# Your agency information
AGENCY_NAME=Your Agency Name
AGENCY_EMAIL=contact@youragency.com
AGENCY_PHONE=(555) 123-4567
AGENCY_WEBSITE=www.youragency.com
```

**Save and close**

---

### 3. Set Up Gmail OAuth (10 minutes)

**Follow the detailed guide:** [OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)

**Quick version:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project "Email Reports Automation"
3. Enable Gmail API
4. Create OAuth credentials (Desktop app)
5. Download `credentials.json`
6. Place in `c:\Apps\Email Reports\`

**First authorization:**
```bash
venv\Scripts\python main.py --extract-only
```
- Browser opens → Login → Allow permissions
- Creates `token.json` automatically

---

### 4. Add Your Clients (10 minutes)

Open the client database:

```bash
notepad data\clients.csv
```

**Add your clients** (one row per client):

```csv
ClientID,FirstName,BusinessName,Email,ServiceType,PersonalizedText,Active,CreatedDate,LastModifiedDate
1,John,ABC Corporation,john@abc.com,SEO,"Great work on content updates.",TRUE,2025-01-01,2025-01-01
2,Sarah,XYZ Services,sarah@xyz.com,SEM,"Your new ads are converting well.",TRUE,2025-01-01,2025-01-01
```

**Important:** `BusinessName` must match the name in your Looker Studio PDFs!

**Save and close**

---

### 5. Test Run (5 minutes)

**Option A:** Test with existing PDFs

1. Place 2-3 test PDFs in `data\pdfs\`
2. Run:
   ```bash
   venv\Scripts\python main.py --process-pdfs
   ```

**Option B:** Extract from Gmail

```bash
venv\Scripts\python main.py --full
```

**Check results:**
- Open `data\approval_review.html` in browser
- Verify emails look correct
- Check `logs\` for any errors

---

## 🎯 Monthly Workflow (After Setup)

### When Looker Studio PDFs Arrive

**Step 1: Extract & Generate** (2 minutes)
```bash
cd "c:\Apps\Email Reports"
venv\Scripts\python main.py --full
```

**Step 2: Review** (5-10 minutes)
- Open `data\approval_review.html`
- Check for extraction errors
- Verify data looks correct

**Step 3: Approve** (2 minutes)
```bash
# Quick approve all (if everything looks good)
venv\Scripts\python main.py --approve-all

# OR manually edit data\approval_tracking.csv
notepad data\approval_tracking.csv
# Change Status from "Pending" to "Approved"
```

**Step 4: Create Drafts** (1 minute)
```bash
venv\Scripts\python main.py --create-drafts
```

**Step 5: Send** (10-15 minutes)
- Open Gmail
- Go to Drafts
- Send each email (5-10 minutes apart)

**Total Time: ~20-30 minutes** ✅

---

## 🆘 Common Issues

### "credentials.json not found"
→ You need to set up Gmail OAuth (see Step 3)
→ Download from Google Cloud Console

### "Client database not found"
→ Create `data\clients.csv` (see Step 4)
→ Or check path in `.env` file

### "No PDFs found"
→ Check Gmail for Looker Studio emails
→ Verify `LOOKER_STUDIO_SENDER` email is correct
→ Try `--extract-only` first

### "No match found for business name"
→ Business name in PDF doesn't match `clients.csv`
→ Check spelling in both places
→ System allows 85% similarity (typos OK)

### Email looks wrong
→ Edit `templates\email_template.html`
→ Or update standard paragraphs in `.env`

---

## 📚 Full Documentation

- **[README.md](README.md)** - Complete user guide
- **[OAUTH_SETUP_GUIDE.md](OAUTH_SETUP_GUIDE.md)** - OAuth detailed instructions
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - System architecture & status
- **[CLAUDE.md](CLAUDE.md)** - Original project requirements

---

## ✅ Verify Everything Works

Run the verification script:

```bash
venv\Scripts\python setup_verify.py
```

**All checks should pass:**
- ✓ Python Version
- ✓ Dependencies
- ✓ Directory Structure
- ✓ Configuration Files
- ✓ Environment Configuration

---

## 🎉 You're Ready!

Once all 5 setup steps are complete, you can process your monthly reports in **under 30 minutes**.

**First time?** Run a test with 2-3 PDFs to verify everything works.

**Questions?** Check the [README.md](README.md) troubleshooting section.

---

*Quick Start Guide - Email Reports Automation v1.0*
