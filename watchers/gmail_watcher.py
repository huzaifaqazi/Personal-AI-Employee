#!/usr/bin/env python3
"""
Gmail Watcher - Monitors Gmail for unread important emails
Checks every 2 minutes and creates task files for new emails
"""

import os
import json
import time
import base64
from datetime import datetime
from pathlib import Path
from email.utils import parsedate_to_datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Gmail API scopes - using readonly for safety
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Load environment variables
load_dotenv()

# Configuration from .env
VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))
CREDENTIALS_PATH = VAULT_PATH / os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
TOKEN_PATH = VAULT_PATH / os.getenv('GMAIL_TOKEN_PATH', 'token.json')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 120))
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'

# Paths for task files and logs
NEEDS_ACTION_DIR = VAULT_PATH / 'Needs_Action'
LOGS_DIR = VAULT_PATH / 'Logs'
PROCESSED_EMAILS_FILE = VAULT_PATH / 'processed_emails.json'

# Ensure directories exist
NEEDS_ACTION_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


def log_message(message, level="INFO"):
    """
    Log a message to both console and daily log file

    Args:
        message: The message to log
        level: Log level (INFO, WARNING, ERROR)
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"

    # Print to console
    print(log_entry)

    # Write to daily log file
    log_date = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f"gmail_{log_date}.md"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            if not log_file.exists() or log_file.stat().st_size == 0:
                f.write(f"# Gmail Watcher Log - {log_date}\n\n")
            f.write(f"{log_entry}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {e}")


def authenticate_gmail():
    """
    Authenticate with Gmail API using OAuth 2.0

    First run: Opens browser for user authorization
    Subsequent runs: Uses saved token.json

    Returns:
        Gmail API service object
    """
    creds = None

    # Check if we have a saved token
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
            log_message("Loaded existing credentials from token.json")
        except Exception as e:
            log_message(f"Failed to load token: {e}", "WARNING")

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                log_message("Refreshing expired token...")
                creds.refresh(Request())
                log_message("Token refreshed successfully")
            except Exception as e:
                log_message(f"Failed to refresh token: {e}", "ERROR")
                creds = None

        if not creds:
            # First time authentication - requires browser
            if not CREDENTIALS_PATH.exists():
                log_message(f"ERROR: credentials.json not found at {CREDENTIALS_PATH}", "ERROR")
                log_message("Please download credentials.json from Google Cloud Console", "ERROR")
                log_message("Visit: https://console.cloud.google.com/apis/credentials", "ERROR")
                raise FileNotFoundError(f"credentials.json not found at {CREDENTIALS_PATH}")

            log_message("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES)

            # Try to open browser, fallback to console if fails
            try:
                log_message("Attempting to open browser for authorization...")
                creds = flow.run_local_server(port=0, open_browser=True)
                log_message("Authorization successful!")
            except Exception as e:
                log_message(f"Browser opening failed: {e}", "WARNING")
                log_message("=" * 70)
                log_message("MANUAL AUTHORIZATION REQUIRED")
                log_message("=" * 70)
                log_message("Please follow these steps:")
                log_message("1. Copy the URL that will appear below")
                log_message("2. Open it in your browser (Windows/Mac)")
                log_message("3. Login and authorize the app")
                log_message("4. Copy the authorization code from browser")
                log_message("5. Paste it back here when prompted")
                log_message("=" * 70)
                creds = flow.run_console()
                log_message("Authorization successful!")

        # Save credentials for next run
        try:
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
            log_message(f"Saved credentials to {TOKEN_PATH}")
        except Exception as e:
            log_message(f"Failed to save token: {e}", "WARNING")

    # Build and return Gmail service
    try:
        service = build('gmail', 'v1', credentials=creds)
        log_message("Gmail API service initialized successfully")
        return service
    except Exception as e:
        log_message(f"Failed to build Gmail service: {e}", "ERROR")
        raise


def load_processed_emails():
    """
    Load the set of already processed email IDs

    Returns:
        Set of email IDs that have been processed
    """
    if PROCESSED_EMAILS_FILE.exists():
        try:
            with open(PROCESSED_EMAILS_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('processed_ids', []))
        except Exception as e:
            log_message(f"Failed to load processed emails: {e}", "WARNING")
            return set()
    return set()


def save_processed_emails(processed_ids):
    """
    Save the set of processed email IDs to disk

    Args:
        processed_ids: Set of email IDs that have been processed
    """
    try:
        with open(PROCESSED_EMAILS_FILE, 'w') as f:
            json.dump({
                'processed_ids': list(processed_ids),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        log_message(f"Failed to save processed emails: {e}", "ERROR")


def decode_email_body(payload):
    """
    Extract and decode email body from Gmail API payload

    Args:
        payload: Email payload from Gmail API

    Returns:
        Decoded email body text (truncated to 1000 chars)
    """
    body = ""

    # Handle multipart emails
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html' and not body:
                # Fallback to HTML if no plain text
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')

    # Handle simple emails
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    # Clean up and truncate
    body = body.strip()
    if len(body) > 1000:
        body = body[:1000] + "..."

    return body if body else "[No body content]"


def extract_email_details(service, email_id):
    """
    Extract detailed information from an email

    Args:
        service: Gmail API service object
        email_id: ID of the email to extract

    Returns:
        Dictionary with email details or None if failed
    """
    try:
        # Get full email message
        message = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()

        # Extract headers
        headers = {h['name']: h['value'] for h in message['payload']['headers']}

        # Parse sender
        sender_raw = headers.get('From', 'Unknown')
        sender_email = sender_raw
        sender_name = sender_raw

        # Try to parse "Name <email>" format
        if '<' in sender_raw and '>' in sender_raw:
            sender_name = sender_raw.split('<')[0].strip()
            sender_email = sender_raw.split('<')[1].split('>')[0].strip()

        # Parse date
        date_str = headers.get('Date', '')
        try:
            received_time = parsedate_to_datetime(date_str)
        except:
            received_time = datetime.now()

        # Extract subject
        subject = headers.get('Subject', '[No Subject]')

        # Extract body
        body = decode_email_body(message['payload'])

        return {
            'id': email_id,
            'sender_name': sender_name,
            'sender_email': sender_email,
            'subject': subject,
            'body': body,
            'received': received_time,
            'snippet': message.get('snippet', '')
        }

    except HttpError as e:
        log_message(f"HTTP error extracting email {email_id}: {e}", "ERROR")
        return None
    except Exception as e:
        log_message(f"Error extracting email {email_id}: {e}", "ERROR")
        return None


def create_task_file(email_details):
    """
    Create a task file in Needs_Action/ directory

    Args:
        email_details: Dictionary with email information

    Returns:
        Path to created task file or None if failed
    """
    try:
        # Create safe filename from subject and timestamp
        timestamp = email_details['received'].strftime('%Y%m%d_%H%M%S')
        safe_subject = "".join(c for c in email_details['subject'] if c.isalnum() or c in (' ', '-', '_'))
        safe_subject = safe_subject[:50].strip()  # Limit length
        filename = f"email_{timestamp}_{safe_subject}.md"
        filepath = NEEDS_ACTION_DIR / filename

        # Format received time
        received_formatted = email_details['received'].strftime('%Y-%m-%d %H:%M:%S')

        # Create task file content
        content = f"""---
type: email
source: gmail
from: {email_details['sender_email']}
subject: {email_details['subject']}
received: {received_formatted}
priority: high
status: pending
requires_approval: true
---

# Email: {email_details['subject']}

## From
**Sender:** {email_details['sender_name']} <{email_details['sender_email']}>
**Received:** {received_formatted}

## Subject
{email_details['subject']}

## Content
{email_details['body']}

## Suggested Actions
- [ ] Read full email
- [ ] Draft reply
- [ ] Forward if needed
- [ ] Mark as processed

## Auto-Response Options
1. Acknowledge receipt
2. Request more information
3. Schedule meeting
4. Decline politely

**IMPORTANT:** All email replies require human approval before sending.
"""

        # Write task file
        if DRY_RUN:
            log_message(f"[DRY RUN] Would create task file: {filepath}")
            return filepath

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        log_message(f"Created task file: {filename}")
        return filepath

    except Exception as e:
        log_message(f"Failed to create task file: {e}", "ERROR")
        return None


def check_new_emails(service, processed_ids):
    """
    Check for new unread important emails

    Args:
        service: Gmail API service object
        processed_ids: Set of already processed email IDs

    Returns:
        List of newly processed email IDs
    """
    try:
        # Query for unread important emails
        query = "is:unread is:important"
        log_message(f"Checking for emails with query: {query}")

        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=10  # Limit to prevent overwhelming
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            log_message("No new unread important emails found")
            return []

        log_message(f"Found {len(messages)} unread important email(s)")

        new_processed = []

        for message in messages:
            email_id = message['id']

            # Skip if already processed
            if email_id in processed_ids:
                log_message(f"Skipping already processed email: {email_id}")
                continue

            log_message(f"Processing new email: {email_id}")

            # Extract email details
            email_details = extract_email_details(service, email_id)

            if email_details:
                # Create task file
                task_file = create_task_file(email_details)

                if task_file:
                    new_processed.append(email_id)
                    log_message(f"Successfully processed email from {email_details['sender_email']}")
                else:
                    log_message(f"Failed to create task for email {email_id}", "WARNING")
            else:
                log_message(f"Failed to extract details for email {email_id}", "WARNING")

        return new_processed

    except HttpError as e:
        log_message(f"HTTP error checking emails: {e}", "ERROR")
        return []
    except Exception as e:
        log_message(f"Error checking emails: {e}", "ERROR")
        return []


def main():
    """
    Main function - runs continuous email checking loop
    """
    log_message("=" * 60)
    log_message("Gmail Watcher Starting")
    log_message(f"Vault Path: {VAULT_PATH}")
    log_message(f"Check Interval: {CHECK_INTERVAL} seconds")
    log_message(f"Dry Run Mode: {DRY_RUN}")
    log_message("=" * 60)

    # Authenticate with Gmail
    try:
        service = authenticate_gmail()
    except Exception as e:
        log_message(f"Failed to authenticate: {e}", "ERROR")
        log_message("Exiting...", "ERROR")
        return

    # Load processed emails
    processed_ids = load_processed_emails()
    log_message(f"Loaded {len(processed_ids)} previously processed email IDs")

    # Main monitoring loop
    log_message("Starting monitoring loop...")
    check_count = 0

    try:
        while True:
            check_count += 1
            log_message(f"Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Check for new emails
            new_processed = check_new_emails(service, processed_ids)

            # Update processed IDs
            if new_processed:
                processed_ids.update(new_processed)
                save_processed_emails(processed_ids)
                log_message(f"Processed {len(new_processed)} new email(s)")

            # Wait before next check
            log_message(f"Waiting {CHECK_INTERVAL} seconds until next check...")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("\nReceived interrupt signal - shutting down gracefully...")
        save_processed_emails(processed_ids)
        log_message("Gmail Watcher stopped")
    except Exception as e:
        log_message(f"Unexpected error in main loop: {e}", "ERROR")
        save_processed_emails(processed_ids)
        raise


if __name__ == "__main__":
    main()
