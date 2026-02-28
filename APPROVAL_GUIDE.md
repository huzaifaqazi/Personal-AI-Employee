# Approval Workflow Guide

## How It Works

The AI Employee uses a human-in-the-loop approval system for all outgoing communications and important actions. This ensures you maintain full control while benefiting from AI automation.

## Workflow Steps

### 1. AI Creates Draft

When the AI needs to send an email, post to LinkedIn, or send a WhatsApp message, it creates a draft file in `Pending_Approval/`:

```
Pending_Approval/
├── EMAIL_20260220_143000_Project_Update.md
├── LINKEDIN_20260220_150000_New_Feature.md
└── WHATSAPP_20260220_153000_Client_Response.md
```

### 2. You Review

Open the file in your editor (VS Code, vim, etc.) and review the content:

- Read the draft carefully
- Check recipient, subject, and content
- Verify tone and accuracy
- Edit directly in the file if needed

### 3. You Decide

Take one of three actions:

#### ✅ Approve
Move the file to `Approved/` folder:
```bash
mv Pending_Approval/EMAIL_*.md Approved/
```

#### ❌ Reject
Move the file to `Rejected/` folder:
```bash
mv Pending_Approval/EMAIL_*.md Rejected/
```

#### ✏️ Edit & Approve
1. Open the file
2. Modify the content (body, subject, etc.)
3. Save changes
4. Move to `Approved/`

### 4. AI Executes

The orchestrator monitors `Approved/` every 30 seconds:

- Detects approved files
- Executes the action (sends email, posts, etc.)
- Moves file to `Done/`
- Logs the action to `Logs/`

## File Types Requiring Approval

### EMAIL_*.md
All outgoing emails require approval.

**Format:**
```markdown
---
type: email_approval
to: recipient@example.com
subject: Project Update
created: 2026-02-20 14:30:00
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

### LINKEDIN_*.md
Social media posts require approval.

**Format:**
```markdown
---
type: linkedin_approval
scheduled: 2026-02-20 15:00:00
status: pending_approval
---

# LinkedIn Post for Approval

## Content
Excited to announce our new feature! 🚀
#ProductLaunch #Innovation

---
**To Approve:** Move this file to Approved/ folder
```

### WHATSAPP_*.md
WhatsApp messages require approval.

**Format:**
```markdown
---
type: whatsapp_approval
to: Client Name
status: pending_approval
---

# WhatsApp Message for Approval

## To
Client Name

## Message
Thanks for reaching out! I'll get back to you by end of day.

---
**To Approve:** Move this file to Approved/ folder
```

### PAYMENT_*.md (Future)
Any financial actions will require approval.

## Quick Approval Commands

### Bash Script
Create `quick_approve.sh`:

```bash
#!/bin/bash
# Quick approve a pending file

if [ -z "$1" ]; then
    echo "Usage: ./quick_approve.sh <filename>"
    exit 1
fi

FILE="Pending_Approval/$1"

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

mv "$FILE" "Approved/"
echo "✅ Approved: $1"
echo "Will be processed within 30 seconds"
```

Usage:
```bash
./quick_approve.sh EMAIL_20260220_143000_Project_Update.md
```

### Python Script
Create `quick_approve.py`:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python quick_approve.py <filename>")
    sys.exit(1)

filename = sys.argv[1]
pending = Path("Pending_Approval") / filename
approved = Path("Approved") / filename

if not pending.exists():
    print(f"Error: File not found: {pending}")
    sys.exit(1)

pending.rename(approved)
print(f"✅ Approved: {filename}")
print("Will be processed within 30 seconds")
```

Usage:
```bash
python quick_approve.py EMAIL_20260220_143000_Project_Update.md
```

## Best Practices

### Daily Routine

**Morning (8:00 AM):**
1. Check `Pending_Approval/` for overnight drafts
2. Review and approve/reject each item
3. Check `Needs_Action/` for new tasks

**Midday (12:00 PM):**
1. Quick check of `Pending_Approval/`
2. Approve time-sensitive items

**Evening (6:00 PM):**
1. Final review of `Pending_Approval/`
2. Approve any remaining items
3. Review `Done/` for completed actions

### Review Checklist

Before approving any draft:

- [ ] Recipient is correct
- [ ] Subject/topic is appropriate
- [ ] Content is accurate
- [ ] Tone is professional
- [ ] No typos or errors
- [ ] Timing is appropriate
- [ ] No sensitive information exposed

### Editing Guidelines

When editing drafts:

1. **Preserve metadata:** Don't modify the frontmatter (between `---`)
2. **Edit content only:** Modify the body, subject, or message text
3. **Keep formatting:** Maintain markdown structure
4. **Save changes:** Ensure file is saved before moving to Approved/

### Security Notes

⚠️ **IMPORTANT:**

- Never approve without reading
- Verify recipients carefully
- Check for sensitive data
- Review links and attachments
- Confirm financial amounts
- Validate external communications

## Monitoring

### Check Pending Count

```bash
# Count pending approvals
ls -1 Pending_Approval/*.md 2>/dev/null | wc -l

# List pending files
ls -lh Pending_Approval/
```

### View Recent Approvals

```bash
# Check recently approved items
ls -lt Approved/*.md | head -5

# Check recently completed items
ls -lt Done/EMAIL_*.md Done/LINKEDIN_*.md Done/WHATSAPP_*.md | head -10
```

### Review Logs

```bash
# View today's sent emails
cat Logs/emails_sent_$(date +%Y-%m-%d).md

# View orchestrator activity
cat Logs/orchestrator_$(date +%Y-%m-%d).md
```

## Troubleshooting

### File Not Processing

**Problem:** Approved file not executing

**Solutions:**
1. Check orchestrator is running: `ps aux | grep orchestrator`
2. Verify file is in `Approved/` folder
3. Check filename starts with EMAIL_, LINKEDIN_, or WHATSAPP_
4. Review `Logs/orchestrator_[date].md` for errors

### Approval Reminders

The system sends reminders every 30 minutes if items are pending:

- Check `Needs_Action/` for REMINDER_pending_approvals_*.md
- These are informational only
- Just review `Pending_Approval/` folder

### Accidental Approval

**Problem:** Approved wrong file

**Solution:**
1. Quickly move from `Approved/` back to `Pending_Approval/`
2. If already processed, check `Done/` folder
3. For emails, cannot unsend (contact recipient if needed)

## Statistics

Track your approval activity:

```bash
# Count approvals today
ls -1 Done/EMAIL_*.md Done/LINKEDIN_*.md Done/WHATSAPP_*.md 2>/dev/null | \
  xargs ls -l | grep "$(date +%Y-%m-%d)" | wc -l

# Count rejections
ls -1 Rejected/*.md 2>/dev/null | wc -l

# Average approval time
# (Time between file creation and approval)
```

## Tips

1. **Set up notifications:** Use file system watchers to get notified of new pending items
2. **Batch review:** Review multiple items at once during scheduled times
3. **Use templates:** Create response templates for common scenarios
4. **Archive regularly:** Clean out `Rejected/` and old `Done/` files weekly
5. **Review patterns:** Check if certain types of drafts always need editing

## Integration with VS Code

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Check Pending Approvals",
      "type": "shell",
      "command": "ls -lh Pending_Approval/",
      "problemMatcher": []
    },
    {
      "label": "Approve Current File",
      "type": "shell",
      "command": "mv '${file}' Approved/",
      "problemMatcher": []
    }
  ]
}
```

---

**Version:** 1.0
**Last Updated:** 2026-02-20
**Status:** Production Ready
