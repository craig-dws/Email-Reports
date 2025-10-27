# Next Steps - Complete Gmail OAuth Setup

**Current Status:** Phase 1 is 90% complete. You need to run the OAuth flow to finish setup.

---

## Quick Start: Complete OAuth Setup (5 minutes)

### Step 1: Open Terminal/Command Prompt

Open a new terminal window and navigate to the project:

```cmd
cd "c:\Apps\Email Reports"
```

### Step 2: Activate Virtual Environment

```cmd
venv\Scripts\activate
```

You should see `(venv)` appear in your command prompt.

### Step 3: Run OAuth Setup Script

```cmd
python test_oauth.py
```

### Step 4: Complete Browser Authorization

1. A browser window will automatically open
2. Sign in with your Gmail account (the account you want to send reports from)
3. You'll see a Google consent screen asking for permissions:
   - **Read emails** (to extract Looker Studio PDFs)
   - **Compose drafts** (to create Gmail drafts)
   - **Send emails** (for future auto-send feature)
4. Click "Allow" or "Continue"
5. Browser will show "Authentication successful" or redirect to localhost
6. Return to terminal

### Step 5: Verify Success

The script will:
- Save credentials to `token.pickle`
- Test Gmail API connection
- List some of your Gmail labels

You should see:
```
[SUCCESS] Token saved successfully!
[SUCCESS] Gmail API connection successful!
[INFO] Found XX labels in your Gmail account
```

---

## What Just Happened?

- ✓ Python dependencies installed (38 packages)
- ✓ Project structure created (all directories ready)
- ✓ Google Cloud project configured (email-reports-475210)
- ✓ OAuth credentials ready (credentials.json)
- ⏳ **You're about to:** Generate OAuth token (token.pickle)

---

## After OAuth Setup

Once `test_oauth.py` completes successfully, you'll have:

1. **token.pickle** - OAuth credentials for Gmail API access
2. **Verified Gmail connection** - System can read/write your Gmail

Then proceed to:

### Next: Configure Your Agency Details

Edit `.env` file with your information:

```bash
# Your agency details
AGENCY_NAME=Your Agency Name
AGENCY_EMAIL=your@agency.com
AGENCY_PHONE=+1-555-123-4567
AGENCY_WEBSITE=https://youragency.com

# Gmail settings
GMAIL_USER_EMAIL=your@gmail.com
LOOKER_STUDIO_SENDER=noreply-looker-studio@google.com
```

### Next: Add Your Clients

Edit `data/clients.csv` with your 30 clients:

```csv
ClientID,FirstName,BusinessName,Email,ServiceType,PersonalizedText,Active
1,John,ABC Corporation,john@abc.com,SEO,"Great progress on content updates.",TRUE
2,Sarah,XYZ Services,sarah@xyz.com,SEM,"Ad performance improving nicely.",TRUE
```

**Important:** BusinessName must match exactly what appears in Looker Studio PDF headers.

### Next: Test with Sample PDFs

1. Place 2-3 test PDFs in `data/pdfs/`
2. Run test: `python main.py --process-pdfs`
3. Review output in `data/approval_review.html`
4. Check logs in `logs/` directory

---

## Troubleshooting

### Browser Doesn't Open?

If browser doesn't open automatically:
1. Look for a URL in the terminal output
2. Copy and paste it into your browser manually
3. Complete authorization
4. Copy the authorization code back to terminal (if prompted)

### "Access Blocked" Error?

If you see "Access Blocked: This app isn't verified":
1. Click "Advanced" (or small link at bottom)
2. Click "Go to Email Reports Automation (unsafe)"
3. This is normal for personal OAuth apps
4. Continue with authorization

### Permission Denied?

Make sure you're signing in with:
- The Gmail account you want to use for sending reports
- An account you have admin access to

### Still Having Issues?

Check:
1. credentials.json exists in project directory
2. You're in the virtual environment (see `(venv)` in prompt)
3. Internet connection is active
4. Gmail account is accessible

---

## Full Documentation

- **README.md** - Complete user guide
- **OAUTH_SETUP_GUIDE.md** - Detailed OAuth instructions
- **PROJECT_STATUS.md** - System capabilities
- **PHASE1_COMPLETION_STATUS.md** - What's been completed
- **task_deps.md** - All project tasks

---

## Need Help?

If you encounter issues:
1. Check logs in `logs/` directory
2. Review error messages carefully
3. Consult OAUTH_SETUP_GUIDE.md for detailed steps
4. Verify credentials.json is valid (from Google Cloud Console)

---

**Ready to complete OAuth setup?**

```cmd
cd "c:\Apps\Email Reports"
venv\Scripts\activate
python test_oauth.py
```

Good luck! The system is almost ready to automate your monthly reports.
