#!/usr/bin/env python3
"""
OAuth Test Script for Email Reports Automation
This script completes the Gmail API OAuth flow and generates token.pickle
"""

import os
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Gmail API scopes required
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send'
]

def get_gmail_credentials():
    """
    Complete OAuth flow and return credentials.
    Creates token.pickle for future use.
    """
    creds = None
    token_path = Path('token.pickle')
    credentials_path = Path('credentials.json')

    # Check if credentials.json exists
    if not credentials_path.exists():
        print("[ERROR] credentials.json not found!")
        print("Please download OAuth credentials from Google Cloud Console")
        print("and save as credentials.json in this directory.")
        return None

    # Check for existing token
    if token_path.exists():
        print("[INFO] Found existing token.pickle file")
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("[INFO] Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("[INFO] Starting OAuth authorization flow...")
            print("\nINSTRUCTIONS:")
            print("1. A browser window will open")
            print("2. Sign in with your Gmail account")
            print("3. Grant permissions (read, compose, send)")
            print("4. Return to this terminal\n")

            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next time
        print("[INFO] Saving credentials to token.pickle...")
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print("[SUCCESS] Token saved successfully!")
    else:
        print("[SUCCESS] Valid credentials found!")

    return creds

def test_gmail_connection(creds):
    """Test Gmail API connection by listing labels."""
    try:
        print("\n[TEST] Testing Gmail API connection...")
        service = build('gmail', 'v1', credentials=creds)

        # Try to list labels
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        print(f"[SUCCESS] Gmail API connection successful!")
        print(f"[INFO] Found {len(labels)} labels in your Gmail account")
        print("\nSample labels:")
        for label in labels[:5]:
            print(f"  - {label['name']}")

        return True
    except Exception as e:
        print(f"[ERROR] Error testing Gmail API: {str(e)}")
        return False

def main():
    """Main execution."""
    print("=" * 60)
    print("Gmail OAuth Setup - Email Reports Automation")
    print("=" * 60)
    print()

    # Get or create credentials
    creds = get_gmail_credentials()

    if not creds:
        print("\n[ERROR] Failed to get credentials. Please check your setup.")
        return False

    # Test the connection
    success = test_gmail_connection(creds)

    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] OAuth setup complete!")
        print("\nNext steps:")
        print("1. Run: python setup_verify.py (to verify full setup)")
        print("2. Configure .env file with your agency details")
        print("3. Add clients to data/clients.csv")
        print("4. Test with sample PDFs")
    else:
        print("[ERROR] Setup incomplete. Please check errors above.")
    print("=" * 60)

    return success

if __name__ == '__main__':
    main()
