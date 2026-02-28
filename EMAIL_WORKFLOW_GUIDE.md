# Email Approval Workflow Guide

## Overview

The Email MCP (Model Context Protocol) server enables Claude Code to draft emails that require human approval before sending. This ensures all outgoing emails are reviewed and approved by you.

## Workflow

```
1. Claude drafts email → Pending_Approval/
2. You review → Move to Approved/ or Rejected/
3. System sends → Logs to emails_sent_[date].md
4. File moves → Done/
```

## Directory Structure

```
AI_Employee_Vault/
├── Pending_Approval/     # Drafts awaiting your review
├── Approved/             # Approved emails ready to send
├── Rejected/             # Rejected drafts (not sent)
├── Done/                 # Sent emails archive
└── Logs/
    └── emails_sent_[date].md  # Sent email log
```

## How to Use

### For Claude Code (Programmatic Use)

```python
from mcp_servers.email_mcp import draft_email, send_email

# Draft an email (requires approval)
draft_email(
    to="recipient@example.com",
    subject="Project Update",
    body="Here's the latest update on the project..."
)

# Process approved emails (called by orchestrator)
process_approved_emails()
```

### For Humans (Manual Approval)

1. **Check Pending_Approval/** for new drafts
2. **Review the email content**
3. **Take action:**
   - **Approve:** Move file to `Approved/`
   - **Reject:** Move file to `Rejected/`
   - **Edit:** Modify the body, then move to `Approved/`

### Email Draft Format

```markdown
---
type: email_approval
to: recipient@example.com
subject: Project Update
created: 2026-02-20 16:00:00
status: pending_approval
---

# Email Draft for Approval

## To
recipient@example.com

## Subject
Project Update

## Body
Here's the latest update on the project...

---
**To Approve:** Move this file to Approved/ folder
**To Reject:** Move this file to Rejected/ folder
**To Edit:** Modify the body above, then move to Approved/
```

## Testing the System

### Create a Test Draft

```bash
source venv/bin/activate
python mcp_servers/email_mcp.py draft
```

This creates a test draft in `Pending_Approval/`

### Process Approved Emails

```bash
python mcp_servers/email_mcp.py process
```

This sends all emails in `Approved/` folder

### Run with Orchestrator

The email approval processor runs automatically when you start the orchestrator:

```bash
python orchestrator.py
```

It checks every 5 minutes for approved emails.

## Features

### ✅ Safety Features
- **No auto-send:** All emails require explicit approval
- **Retry logic:** 3 attempts with 5-second delays
- **Error handling:** Graceful failure with detailed logging
- **Audit trail:** All sent emails logged with timestamps

### 📧 Email Capabilities
- **Recipients:** To, CC, BCC support
- **Multiple recipients:** Comma-separated list
- **Plain text:** Simple, reliable email format
- **Gmail integration:** Uses your Gmail account

### 🔐 Authentication
- Uses same Gmail credentials as gmail_watcher
- Requires additional "send" permission on first run
- Browser will open for OAuth authorization
- Token saved for future use

## First Run Setup

1. **Ensure credentials.json exists** in vault root
2. **Run email_mcp.py** for first time:
   ```bash
   python mcp_servers/email_mcp.py draft
   ```
3. **Browser opens** for Gmail authorization
4. **Grant send permissions** when prompted
5. **Token saved** to token.json

## Approval Workflow Examples

### Example 1: Approve as-is

1. Draft appears in `Pending_Approval/EMAIL_20260220_160000_Project_Update.md`
2. You review it
3. Move to `Approved/`
4. System sends within 5 minutes
5. File moves to `Done/`

### Example 2: Edit before approval

1. Draft appears in `Pending_Approval/`
2. You open the file
3. Edit the "## Body" section
4. Save changes
5. Move to `Approved/`
6. System sends the edited version

### Example 3: Reject

1. Draft appears in `Pending_Approval/`
2. You review it
3. Move to `Rejected/`
4. Email is NOT sent
5. File stays in `Rejected/` for your records

## Monitoring

### Check Logs

```bash
# View today's sent emails
cat Logs/emails_sent_$(date +%Y-%m-%d).md

# View recent activity
tail -f Logs/emails_sent_*.md
```

### Check Status

```bash
# Pending approval
ls -l Pending_Approval/

# Approved (waiting to send)
ls -l Approved/

# Rejected
ls -l Rejected/

# Sent (archived)
ls -l Done/EMAIL_*.md
```

## Error Handling

### Email Send Failures

If an email fails to send:
- System retries 3 times (5 seconds between attempts)
- Detailed error logged to `Logs/emails_sent_[date].md`
- File remains in `Approved/` for manual retry
- Check logs for specific error message

### Common Issues

**"credentials.json not found"**
- Download from Google Cloud Console
- Place in vault root directory

**"Failed to authenticate"**
- Delete token.json
- Run email_mcp.py again
- Re-authorize in browser

**"Permission denied"**
- Ensure you granted "send" permission during OAuth
- May need to re-authorize with full permissions

## Security Notes

⚠️ **IMPORTANT:**
- All emails require human approval
- No automated sending without explicit approval
- Credentials stored securely in token.json
- Token.json is in .gitignore (never committed)
- All sent emails logged for audit trail

## Integration with Claude Code

Claude Code can use this system to:
1. Draft replies to important emails
2. Send scheduled notifications
3. Forward information to team members
4. Send reports and summaries

All with your approval before sending.

## Rate Limits

- **Gmail API:** 100 emails per day (free tier)
- **Approval processor:** Checks every 5 minutes
- **Retry attempts:** 3 per email
- **No artificial limits** on drafts

## Best Practices

1. **Review daily:** Check `Pending_Approval/` each morning
2. **Edit carefully:** Modify body text only, not metadata
3. **Archive regularly:** Clean out `Done/` and `Rejected/` weekly
4. **Monitor logs:** Review sent emails for accuracy
5. **Test first:** Use test@example.com for initial testing

---

**Version:** 1.0
**Last Updated:** 2026-02-20
**Status:** Production Ready
