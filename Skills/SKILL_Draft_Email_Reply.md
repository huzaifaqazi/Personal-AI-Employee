# Draft Email Reply

## Purpose
Create email reply drafts that require human approval

## Instructions
1. Read email from Needs_Action/
2. Analyze sender, subject, content
3. Check Company_Handbook.md for tone guidelines
4. Generate appropriate reply
5. Create draft in Pending_Approval/EMAIL_REPLY_[timestamp].md
6. Include original email for context
7. Provide 2-3 reply options (formal, casual, brief)
8. Never send without approval

## Reply Template
```markdown
---
type: email_approval
to: [original sender]
subject: Re: [original subject]
in_reply_to: [original email file]
created: [timestamp]
requires_approval: true
---

# Email Reply Draft

## Original Email
From: [sender]
Subject: [subject]
[original content]

## Reply Option 1: Professional
[formal reply]

## Reply Option 2: Friendly
[casual but professional reply]

## Reply Option 3: Brief
[short acknowledgment]

---
Choose an option or edit before approving.
```

## Guidelines

### Tone Matching
- Match the sender's formality level
- Professional for business contacts
- Friendly for known colleagues
- Respectful for all communications

### Response Time
- Urgent emails: Draft within 1 hour
- Important emails: Draft within 4 hours
- Regular emails: Draft within 24 hours

### Content Requirements
- Address all questions asked
- Provide clear next steps
- Include relevant context
- Keep concise and actionable

### What to Avoid
- Never commit to deadlines without approval
- Don't share confidential information
- Avoid making financial commitments
- Don't schedule meetings without checking calendar

## Examples

### Example 1: Client Request
**Original:** "Can you send the Q4 report by Friday?"

**Reply Option 1 (Professional):**
"Thank you for your email. I'll prepare the Q4 report and have it ready for your review by Friday afternoon. Please let me know if you need any specific sections highlighted."

**Reply Option 2 (Friendly):**
"Hi! Absolutely, I'll get that Q4 report over to you by Friday. Let me know if there's anything specific you'd like me to focus on."

**Reply Option 3 (Brief):**
"Will do - Q4 report by Friday. Thanks!"

### Example 2: Meeting Request
**Original:** "Are you available for a call next Tuesday at 2pm?"

**Reply Option 1 (Professional):**
"Thank you for reaching out. I need to check my calendar and will confirm availability for Tuesday at 2pm within the next few hours."

**Reply Option 2 (Friendly):**
"Let me check my calendar and get back to you shortly about Tuesday at 2pm!"

**Reply Option 3 (Brief):**
"Checking calendar - will confirm shortly."

## Quality Checklist

Before creating draft:
- [ ] Understood the sender's request
- [ ] Checked for urgency indicators
- [ ] Reviewed company tone guidelines
- [ ] Included all necessary information
- [ ] Provided multiple reply options
- [ ] Flagged any items needing human decision
- [ ] Set appropriate priority level

## Integration

This skill integrates with:
- Gmail Watcher (receives emails)
- Email MCP (sends approved replies)
- Company Handbook (tone guidelines)
- Approval workflow (human review)
