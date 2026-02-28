#!/usr/bin/env python3
"""
Email MCP Server - Handles email drafting and sending with approval workflow
Integrates with Gmail API for actual email sending
"""

import os
import json
import time
import base64
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Gmail API scopes - need send permission
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))
CREDENTIALS_PATH = VAULT_PATH / os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
TOKEN_PATH = VAULT_PATH / os.getenv('GMAIL_TOKEN_PATH', 'token.json')

# Paths
PENDING_APPROVAL_DIR = VAULT_PATH / 'Pending_Approval'
APPROVED_DIR = VAULT_PATH / 'Approved'
REJECTED_DIR = VAULT_PATH / 'Rejected'
LOGS_DIR = VAULT_PATH / 'Logs'

# Ensure directories exist
PENDING_APPROVAL_DIR.mkdir(exist_ok=True)
APPROVED_DIR.mkdir(exist_ok=True)
REJECTED_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


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
    log_file = LOGS_DIR / f"emails_sent_{log_date}.md"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            if not log_file.exists() or log_file.stat().st_size == 0:
                f.write(f"# Email Activity Log - {log_date}\n\n")
            f.write(f"{log_entry}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {e}")


def authenticate_gmail():
    """
    Authenticate with Gmail API using OAuth 2.0
    Requires send permissions

    Returns:
        Gmail API service object or None if failed
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
                return None

            log_message("Starting OAuth flow...")
            log_message("NOTE: You'll need to grant SEND permissions this time", "WARNING")
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
                log_message("4. Grant SEND permissions when asked")
                log_message("5. Copy the authorization code from browser")
                log_message("6. Paste it back here when prompted")
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
        return None


def draft_email(to, subject, body, cc=None, bcc=None):
    """
    Create an email draft for approval

    Args:
        to: Recipient email address (or list of addresses)
        subject: Email subject
        body: Email body content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)

    Returns:
        Path to created draft file or None if failed
    """
    try:
        # Handle multiple recipients
        if isinstance(to, list):
            to_str = ', '.join(to)
        else:
            to_str = to

        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        created_formatted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create safe filename
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_'))
        safe_subject = safe_subject[:50].strip()
        filename = f"EMAIL_{timestamp}_{safe_subject}.md"
        filepath = PENDING_APPROVAL_DIR / filename

        # Build draft content
        content = f"""---
type: email_approval
to: {to_str}
subject: {subject}
created: {created_formatted}
status: pending_approval
---

# Email Draft for Approval

## To
{to_str}
"""

        # Add CC if provided
        if cc:
            cc_str = ', '.join(cc) if isinstance(cc, list) else cc
            content += f"\n## CC\n{cc_str}\n"

        # Add BCC if provided
        if bcc:
            bcc_str = ', '.join(bcc) if isinstance(bcc, list) else bcc
            content += f"\n## BCC\n{bcc_str}\n"

        content += f"""
## Subject
{subject}

## Body
{body}

---
**To Approve:** Move this file to Approved/ folder
**To Reject:** Move this file to Rejected/ folder
**To Edit:** Modify the body above, then move to Approved/
"""

        # Write draft file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        log_message(f"Created email draft: {filename}")
        log_message(f"Recipient: {to_str}")
        log_message(f"Subject: {subject}")

        return filepath

    except Exception as e:
        log_message(f"Failed to create email draft: {e}", "ERROR")
        return None


def parse_approved_email(filepath):
    """
    Parse an approved email file to extract details

    Args:
        filepath: Path to the approved email file

    Returns:
        Dictionary with email details or None if failed
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata from frontmatter
        import re

        to_match = re.search(r'^to:\s*(.+)$', content, re.MULTILINE)
        subject_match = re.search(r'^subject:\s*(.+)$', content, re.MULTILINE)
        cc_match = re.search(r'^cc:\s*(.+)$', content, re.MULTILINE)
        bcc_match = re.search(r'^bcc:\s*(.+)$', content, re.MULTILINE)

        # Extract body (everything after "## Body" until "---")
        body_match = re.search(r'## Body\s*\n(.*?)\n---', content, re.DOTALL)

        if not to_match or not subject_match or not body_match:
            log_message(f"Failed to parse email file: {filepath}", "ERROR")
            return None

        email_data = {
            'to': to_match.group(1).strip(),
            'subject': subject_match.group(1).strip(),
            'body': body_match.group(1).strip(),
            'cc': cc_match.group(1).strip() if cc_match else None,
            'bcc': bcc_match.group(1).strip() if bcc_match else None
        }

        return email_data

    except Exception as e:
        log_message(f"Error parsing approved email: {e}", "ERROR")
        return None


def create_message(to, subject, body, cc=None, bcc=None):
    """
    Create a MIME message for Gmail API

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)

    Returns:
        Encoded message ready for Gmail API
    """
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject

    if cc:
        message['cc'] = cc
    if bcc:
        message['bcc'] = bcc

    # Add body
    msg_body = MIMEText(body, 'plain')
    message.attach(msg_body)

    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def send_email(to, subject, body, cc=None, bcc=None, service=None):
    """
    Send an email via Gmail API with retry logic

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        service: Gmail API service (will authenticate if not provided)

    Returns:
        True if sent successfully, False otherwise
    """
    # Authenticate if service not provided
    if service is None:
        service = authenticate_gmail()
        if service is None:
            log_message("Failed to authenticate with Gmail", "ERROR")
            return False

    # Create message
    try:
        message = create_message(to, subject, body, cc, bcc)
    except Exception as e:
        log_message(f"Failed to create message: {e}", "ERROR")
        return False

    # Attempt to send with retries
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log_message(f"Sending email (attempt {attempt}/{MAX_RETRIES})...")
            log_message(f"To: {to}")
            log_message(f"Subject: {subject}")

            result = service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            log_message(f"Email sent successfully! Message ID: {result['id']}")

            # Log to sent emails file
            log_sent_email(to, subject, body, cc, bcc, result['id'])

            return True

        except HttpError as e:
            log_message(f"HTTP error sending email (attempt {attempt}): {e}", "ERROR")

            if attempt < MAX_RETRIES:
                log_message(f"Retrying in {RETRY_DELAY} seconds...", "WARNING")
                time.sleep(RETRY_DELAY)
            else:
                log_message("Max retries reached. Email not sent.", "ERROR")
                return False

        except Exception as e:
            log_message(f"Unexpected error sending email (attempt {attempt}): {e}", "ERROR")

            if attempt < MAX_RETRIES:
                log_message(f"Retrying in {RETRY_DELAY} seconds...", "WARNING")
                time.sleep(RETRY_DELAY)
            else:
                log_message("Max retries reached. Email not sent.", "ERROR")
                return False

    return False


def log_sent_email(to, subject, body, cc, bcc, message_id):
    """
    Log a sent email to the daily log file

    Args:
        to: Recipient
        subject: Subject
        body: Body content
        cc: CC recipients
        bcc: BCC recipients
        message_id: Gmail message ID
    """
    try:
        log_date = datetime.now().strftime('%Y-%m-%d')
        log_file = LOGS_DIR / f"emails_sent_{log_date}.md"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(log_file, 'a', encoding='utf-8') as f:
            if not log_file.exists() or log_file.stat().st_size == 0:
                f.write(f"# Sent Emails Log - {log_date}\n\n")

            f.write(f"## Email Sent at {timestamp}\n\n")
            f.write(f"**To:** {to}\n")
            if cc:
                f.write(f"**CC:** {cc}\n")
            if bcc:
                f.write(f"**BCC:** {bcc}\n")
            f.write(f"**Subject:** {subject}\n")
            f.write(f"**Message ID:** {message_id}\n\n")
            f.write(f"**Body:**\n```\n{body[:500]}{'...' if len(body) > 500 else ''}\n```\n\n")
            f.write("---\n\n")

    except Exception as e:
        log_message(f"Failed to log sent email: {e}", "WARNING")


def process_approved_emails():
    """
    Process all emails in the Approved/ folder and send them

    Returns:
        Number of emails successfully sent
    """
    # Get all markdown files in Approved/
    approved_files = list(APPROVED_DIR.glob('EMAIL_*.md'))

    if not approved_files:
        log_message("No approved emails to process")
        return 0

    log_message(f"Found {len(approved_files)} approved email(s) to send")

    # Authenticate once for all emails
    service = authenticate_gmail()
    if service is None:
        log_message("Failed to authenticate. Cannot send emails.", "ERROR")
        return 0

    sent_count = 0

    for filepath in approved_files:
        log_message(f"Processing: {filepath.name}")

        # Parse email details
        email_data = parse_approved_email(filepath)

        if email_data is None:
            log_message(f"Skipping {filepath.name} due to parse error", "WARNING")
            continue

        # Send email
        success = send_email(
            to=email_data['to'],
            subject=email_data['subject'],
            body=email_data['body'],
            cc=email_data.get('cc'),
            bcc=email_data.get('bcc'),
            service=service
        )

        if success:
            sent_count += 1

            # Move to Done/ folder
            done_path = VAULT_PATH / 'Done' / filepath.name
            try:
                filepath.rename(done_path)
                log_message(f"Moved {filepath.name} to Done/")
            except Exception as e:
                log_message(f"Failed to move file to Done/: {e}", "WARNING")
        else:
            log_message(f"Failed to send {filepath.name}", "ERROR")

    log_message(f"Sent {sent_count}/{len(approved_files)} email(s)")
    return sent_count


# Example usage and testing
if __name__ == "__main__":
    import sys

    log_message("=" * 60)
    log_message("Email MCP Server - Test Mode")
    log_message("=" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == "process":
        # Process approved emails
        log_message("Processing approved emails...")
        count = process_approved_emails()
        log_message(f"Processing complete. {count} email(s) sent.")

    elif len(sys.argv) > 1 and sys.argv[1] == "draft":
        # Create a test draft
        log_message("Creating test email draft...")
        draft_email(
            to="test@example.com",
            subject="Test Email from AI Employee",
            body="This is a test email created by the AI Employee system.\n\nPlease approve or reject this draft."
        )
        log_message("Test draft created in Pending_Approval/")

    else:
        print("\nUsage:")
        print("  python email_mcp.py draft    - Create a test draft")
        print("  python email_mcp.py process  - Process approved emails")
        print("\nOr import this module to use draft_email() and send_email() functions")
