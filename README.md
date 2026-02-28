# Personal AI Employee System

## Quick Start Guide

### Overview
A comprehensive AI Employee system that automates your daily workflows including task management, email handling, LinkedIn posting, and WhatsApp monitoring. The system uses file-based task management, scheduled automation, and intelligent watchers to handle routine work while keeping you in control through approval workflows.

### Folder Structure

```
AI_Employee_Vault/
├── Inbox/              # Drop new tasks here
├── Needs_Action/       # Tasks requiring your approval
├── Pending_Approval/   # Email drafts awaiting approval
├── Approved/           # Approved emails ready to send
├── Rejected/           # Rejected items
├── Done/               # Completed tasks archive
├── Plans/              # Project plans and strategies
├── Logs/               # Activity logs and history
├── Skills/             # Custom AI skills and templates
├── watchers/           # Automation watchers
│   ├── gmail_watcher.py
│   ├── linkedin_poster.py
│   ├── whatsapp_watcher.py
│   ├── file_watcher.py
│   └── email_approval_processor.py
├── mcp_servers/        # MCP server implementations
├── orchestrator.py     # Main coordination system
├── scheduler.py        # Scheduled task manager
├── Dashboard.md        # Real-time status overview
├── Company_Handbook.md # Operating rules and priorities
└── README.md           # This file
```

### How to Use

#### 1. Submit Tasks
Create files in the `Inbox/` folder using these naming conventions:
- `URGENT_[description].md` - High priority (🔴)
- `TASK_[description].md` - Medium priority (🟡)
- `INFO_[description].md` - Low priority (🟢)

#### 2. Email Automation
The system automatically monitors your Gmail inbox and:
- Detects new emails requiring responses
- Drafts professional replies based on context
- Saves drafts to `Pending_Approval/` for your review
- Sends approved emails automatically
- Logs all email activity

**Approval Process:**
1. Check `Pending_Approval/` for email drafts
2. Review the drafted response
3. Move to `Approved/` to send, or `Rejected/` to discard
4. System automatically sends approved emails

#### 3. LinkedIn Automation
Post to LinkedIn by creating files in `Plans/LinkedIn_Posts.md`:
- System checks for new posts daily
- Automatically publishes approved content
- Logs posting activity
- Maintains posting schedule

#### 4. WhatsApp Monitoring
The system monitors WhatsApp for important messages and creates tasks in `Needs_Action/` for messages requiring attention.

#### 5. Scheduled Tasks
The scheduler runs automated tasks:
- Daily briefings (8:00 AM)
- Dashboard updates (5:00 AM)
- Pending approval reminders (12:00 PM)
- Custom scheduled tasks

#### 6. Check Status
- View `Dashboard.md` for current status
- Review `Needs_Action/` for items requiring approval
- Check `Pending_Approval/` for email drafts
- Review `Done/` for completed work
- Read `Logs/` for activity history

### Task File Format

```markdown
# Task Title

## Description
What needs to be done

## Context
Background information

## Expected Output
What success looks like

## Deadline (optional)
YYYY-MM-DD
```

### Approval Workflow

**Email Approval:**
1. System drafts email responses in `Pending_Approval/`
2. Review the draft (subject, recipient, content)
3. Move to `Approved/` to send automatically
4. Move to `Rejected/` to discard
5. Edit and keep in `Pending_Approval/` to revise

**Task Approval:**
Tasks requiring approval will be moved to `Needs_Action/` with:
- Original task details
- AI's proposed action
- Approval request

Review and either:
- Approve: Move to Inbox with `APPROVED_` prefix
- Reject: Add feedback and move back to Inbox
- Modify: Edit and move back to Inbox

### System Components

**Orchestrator (`orchestrator.py`):**
- Main coordination system
- Processes inbox tasks
- Manages task lifecycle
- Coordinates with MCP servers

**Scheduler (`scheduler.py`):**
- Runs scheduled tasks
- Daily briefings and updates
- Reminder system
- Configurable task timing

**Watchers:**
- `gmail_watcher.py` - Monitors Gmail inbox, drafts responses
- `linkedin_poster.py` - Posts to LinkedIn on schedule
- `whatsapp_watcher.py` - Monitors WhatsApp messages
- `file_watcher.py` - Watches for file changes
- `email_approval_processor.py` - Sends approved emails

**MCP Servers:**
- `email_mcp.py` - Email operations server
- Extensible for additional integrations

### Automation Rules

The AI can automatically:
- ✅ Summarize documents
- ✅ Create reports from data
- ✅ Organize and categorize files
- ✅ Generate plans and strategies
- ✅ Research and compile information
- ✅ Monitor Gmail inbox for new emails
- ✅ Draft email responses
- ✅ Post to LinkedIn on schedule
- ✅ Monitor WhatsApp messages
- ✅ Run scheduled tasks and briefings
- ✅ Update dashboard and logs

The AI requires approval for:
- ❌ Sending emails (requires moving to Approved/)
- ❌ Financial transactions
- ❌ Deleting files or data
- ❌ External communications without review

### Custom Skills

Add custom skills in the `Skills/` folder:
1. Create `[skill-name].md`
2. Define the skill's purpose and steps
3. Reference in tasks with `@skill:[skill-name]`

### Best Practices

1. **Be Specific**: Clear task descriptions get better results
2. **Use Priorities**: Mark truly urgent items as URGENT_
3. **Check Daily**: Review Dashboard.md each morning
4. **Review Approvals**: Check `Pending_Approval/` for email drafts regularly
5. **Monitor Logs**: Review daily logs to track system activity
6. **Archive Regularly**: Clean out Done/ folder weekly
7. **Update Handbook**: Refine rules based on experience
8. **Test Email Drafts**: Always review before approving emails
9. **Schedule LinkedIn**: Plan posts in advance in LinkedIn_Posts.md
10. **Backup Credentials**: Keep credentials.json and token.json secure

### Features

**Bronze Tier:**
- ✅ File-based task management
- ✅ Priority-based processing
- ✅ Approval workflows
- ✅ Custom skills system
- ✅ Activity logging

**Silver Tier:**
- ✅ Gmail integration and monitoring
- ✅ Automated email draft generation
- ✅ Email approval workflow
- ✅ LinkedIn posting automation
- ✅ WhatsApp monitoring
- ✅ Scheduled task system
- ✅ MCP server architecture
- ✅ Multi-watcher coordination

### Example Tasks

**Research Task:**
```
Filename: TASK_market_research.md
Content: Research top 5 competitors in [industry] and create comparison table
```

**Urgent Request:**
```
Filename: URGENT_client_report.md
Content: Compile Q4 metrics into executive summary by EOD
```

**Information Processing:**
```
Filename: INFO_meeting_notes.md
Content: Summarize attached meeting transcript and extract action items
```

**Email Response:**
System automatically detects incoming emails and creates drafts in `Pending_Approval/` for your review before sending.

**LinkedIn Post:**
Add content to `Plans/LinkedIn_Posts.md` and the system will post on schedule.

### Setup Instructions

**Prerequisites:**
- Python 3.8+
- Gmail API credentials (`credentials.json`)
- LinkedIn session cookies
- WhatsApp Web session (optional)

**Installation:**
```bash
pip install -r requirements.txt
```

**Configuration:**
1. Place Gmail API credentials in `credentials.json`
2. Configure `.env` file with API keys
3. Set up LinkedIn session in `linkedin_session/`
4. Run initial authentication for Gmail

**Running the System:**
```bash
# Start the orchestrator
python orchestrator.py

# Start the scheduler (in separate terminal)
python scheduler.py

# Start individual watchers
python watchers/gmail_watcher.py
python watchers/linkedin_poster.py
python watchers/whatsapp_watcher.py
python watchers/email_approval_processor.py
```

### Troubleshooting

**Task not processing?**
- Check filename follows naming convention
- Verify file is in Inbox/
- Ensure task description is clear
- Check orchestrator logs in `Logs/orchestrator_[date].md`

**Email not being drafted?**
- Verify Gmail watcher is running
- Check `credentials.json` and `token.json` are present
- Review logs in `Logs/gmail_[date].md`
- Ensure Gmail API is enabled

**LinkedIn post not publishing?**
- Check `linkedin_session/` has valid cookies
- Verify post content in `Plans/LinkedIn_Posts.md`
- Review logs in `Logs/linkedin_[date].md`

**Approved email not sending?**
- Ensure email_approval_processor is running
- Check file is in `Approved/` folder
- Review logs in `Logs/emails_sent_[date].md`

**Need to modify a task?**
- Edit the file in its current location
- AI will detect changes and reprocess

**Want to cancel a task?**
- Move file out of Inbox/
- Or prefix with `CANCELLED_`

### Getting Help

- Review `Company_Handbook.md` for operating rules
- Check `EMAIL_WORKFLOW_GUIDE.md` for email automation details
- Read `LINKEDIN_POSTING_GUIDE.md` for LinkedIn posting
- Review `APPROVAL_GUIDE.md` for approval workflows
- Check `SYSTEM_ARCHITECTURE.md` for technical details
- Review `Logs/` for processing history
- Update Dashboard.md manually if needed

### Documentation

- `README.md` - This quick start guide
- `SYSTEM_ARCHITECTURE.md` - Technical architecture and design
- `EMAIL_WORKFLOW_GUIDE.md` - Email automation workflow
- `LINKEDIN_POSTING_GUIDE.md` - LinkedIn posting guide
- `APPROVAL_GUIDE.md` - Approval process details
- `QUICK_REFERENCE.md` - Quick command reference
- `Company_Handbook.md` - Operating rules and priorities

---

**System Version:** Bronze + Silver Tier (Full Automation)
**Last Updated:** 2026-02-28
**Repository:** https://github.com/huzaifaqazi/Personal-AI-Employee

### License
MIT License - Feel free to use and modify for your needs.

### Contributing
Contributions welcome! Please review the system architecture before making changes.
