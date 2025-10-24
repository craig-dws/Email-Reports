# Gmail OAuth Setup Guide

**Step-by-Step Instructions for Setting Up Gmail API Access**

---

## Prerequisites

- Google Workspace account (your business Gmail)
- Admin access to Google Cloud Console
- Email Reports system installed on your computer

---

## Step 1: Create Google Cloud Project

1. Open your web browser and go to: [https://console.cloud.google.com/](https://console.cloud.google.com/)

2. Sign in with your Google Workspace account

3. Click **Select a project** (top left, near "Google Cloud")

4. Click **NEW PROJECT**

5. Enter project details:
   - **Project name:** `Email Reports Automation`
   - **Organization:** (Select your organization if available)
   - **Location:** (Leave as default or select your organization)

6. Click **CREATE**

7. Wait for project creation (takes ~30 seconds)

8. Select your new project from the dropdown

---

## Step 2: Enable Gmail API

1. In Google Cloud Console, click the **hamburger menu** (☰) top left

2. Go to **APIs & Services** > **Library**

3. In the search box, type: `Gmail API`

4. Click **Gmail API** from the results

5. Click **ENABLE** button

6. Wait for activation (~10 seconds)

---

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen** (left sidebar)

2. Select user type:
   - Choose **Internal** (for Google Workspace users)
   - Click **CREATE**

3. Fill in OAuth consent screen details:

   **App information:**
   - **App name:** `Email Reports Automation`
   - **User support email:** Your email address

   **App domain (optional - can skip):**
   - Leave blank for now

   **Developer contact information:**
   - **Email addresses:** Your email address

4. Click **SAVE AND CONTINUE**

5. **Scopes page:**
   - Click **ADD OR REMOVE SCOPES**
   - Filter by "Gmail API"
   - Select these scopes:
     - `https://www.googleapis.com/auth/gmail.readonly` (Read emails)
     - `https://www.googleapis.com/auth/gmail.compose` (Create drafts)
     - `https://www.googleapis.com/auth/gmail.modify` (Modify emails)
   - Click **UPDATE**
   - Click **SAVE AND CONTINUE**

6. **Test users page:**
   - You don't need to add test users (internal app)
   - Click **SAVE AND CONTINUE**

7. **Summary page:**
   - Review your settings
   - Click **BACK TO DASHBOARD**

---

## Step 4: Create OAuth Credentials

1. Go to **APIs & Services** > **Credentials** (left sidebar)

2. Click **CREATE CREDENTIALS** (top)

3. Select **OAuth client ID**

4. Configure OAuth client:
   - **Application type:** Select **Desktop app**
   - **Name:** `Email Reports Desktop Client`

5. Click **CREATE**

6. **OAuth client created** dialog appears:
   - Click **DOWNLOAD JSON**
   - Save the file

7. **IMPORTANT:** Rename the downloaded file to `credentials.json`

8. Move `credentials.json` to your Email Reports folder:
   ```
   c:\Apps\Email Reports\credentials.json
   ```

---

## Step 5: First-Time Authorization

Now you'll authorize the application to access your Gmail account.

1. Open Command Prompt

2. Navigate to Email Reports directory:
   ```bash
   cd "c:\Apps\Email Reports"
   ```

3. Run the setup verification script:
   ```bash
   venv\Scripts\python setup_verify.py
   ```

4. Check that credentials.json is detected

5. Test the Gmail connection:
   ```bash
   venv\Scripts\python main.py --extract-only
   ```

6. **Authorization flow will begin:**
   - A web browser window will open automatically
   - You'll see: "Email Reports Automation wants to access your Google Account"
   - Click your Google account
   - Click **Allow** to grant permissions
   - You'll see: "The authentication flow has completed"
   - Close the browser window

7. **Authorization complete!**
   - A file called `token.json` has been created
   - This stores your authorization
   - You won't need to re-authorize unless you revoke access

---

## Step 6: Verify Everything Works

Run a test to make sure Gmail access is working:

```bash
cd "c:\Apps\Email Reports"
venv\Scripts\python -c "from src.gmail_reader import GmailReader; reader = GmailReader(); print('✓ Gmail connection successful!')"
```

If you see `✓ Gmail connection successful!` - you're all set!

---

## Troubleshooting

### "credentials.json not found"

**Solution:**
- Make sure you downloaded the credentials file from Google Cloud Console
- Rename it to exactly `credentials.json` (not `credentials (1).json`)
- Place it in `c:\Apps\Email Reports\` (project root directory)

### "Access blocked: This app's request is invalid"

**Solution:**
- Make sure you selected **Desktop app** (not Web application)
- Make sure OAuth consent screen is configured for **Internal** users
- Check that Gmail API is enabled

### "The application has not been verified"

This message appears for **External** apps. Solutions:
- Change consent screen to **Internal** (for Google Workspace)
- Or click **Advanced** > **Go to Email Reports Automation (unsafe)**
  - This is safe for your own app
  - Google shows this warning for unverified apps

### "Authorization failed" or browser doesn't open

**Solution:**
- Check your firewall settings
- Try manually opening the URL shown in Command Prompt
- Make sure you're logged into the correct Google account

---

## Security Notes

### What is stored in token.json?

`token.json` contains:
- **Access token:** Temporary token (expires after 1 hour)
- **Refresh token:** Used to get new access tokens automatically
- **Scope information:** What permissions were granted

### Is it safe to store credentials.json and token.json?

- **DO NOT** commit these files to Git or share them publicly
- Both files are listed in `.gitignore` to prevent accidental commits
- Store backups in a secure location (encrypted drive, password manager)

### How to revoke access

If you need to revoke the application's access:

1. Go to: [https://myaccount.google.com/permissions](https://myaccount.google.com/permissions)
2. Find "Email Reports Automation"
3. Click **Remove Access**
4. Delete `token.json` from your computer
5. Re-run authorization to grant access again

---

## OAuth Scopes Explained

The application requests these permissions:

| Scope | Permission | Why Needed |
|-------|------------|------------|
| `gmail.readonly` | Read emails | Extract PDF attachments from Looker Studio emails |
| `gmail.compose` | Create drafts | Create draft emails for your review |
| `gmail.modify` | Modify emails | Mark emails as read after processing (optional) |

**Note:** The app CANNOT:
- Delete emails
- Send emails on your behalf (drafts only)
- Access emails from other accounts
- Share your data with third parties

---

## Next Steps

After completing OAuth setup:

1. ✓ OAuth credentials configured
2. ✓ First authorization completed
3. → Configure `.env` file with your settings
4. → Add clients to `data/clients.csv`
5. → Run full workflow: `python main.py --full`

See [README.md](README.md) for complete usage instructions.

---

**Need Help?**

If you encounter issues not covered in this guide:
1. Check the troubleshooting section above
2. Review error messages in `logs/` directory
3. Verify all steps were completed in order
4. Contact your system administrator

---

*OAuth Setup Guide for Email Reports Automation System v1.0*
