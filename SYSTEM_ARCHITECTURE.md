# AI Employee System - Structural Analysis

**Generated:** 2026-02-26
**System Version:** Bronze Tier v1.0

---

## Executive Summary

The AI Employee Vault is a file-based automation system that monitors multiple channels (Gmail, WhatsApp, LinkedIn), processes tasks with priority-based workflows, and maintains human-in-the-loop approval for critical operations. Built with Python and Claude AI, it uses a transparent folder structure for task management and complete audit trails.

---

## System Architecture

### Core Components

```
AI_Employee_Vault/
├── orchestrator.py          # Main process manager
├── scheduler.py             # Time-based task scheduler
├── quick_approve.py         # Fast approval CLI tool
├── watchers/                # Channel monitoring modules
│   ├── file_watcher.py      # Inbox folder monitor
│   ├── gmail_watcher.py     # Email monitoring
│   ├── whatsapp_watcher.py  # WhatsApp integration
│   ├── linkedin_poster.py   # LinkedIn automation
│   ├── linkedin_manual_poster.py
│   ├── linkedin_stealth_poster.py
│   └── email_approval_processor.py
├── mcp_servers/             # MCP server integrations
│   └── email_mcp.py         # Email MCP server
└── Skills/                  # AI skill templates
```

---

## Component Breakdown

### 1. Orchestrator (orchestrator.py)

**Purpose:** Central process manager that coordinates all watchers and handles system lifecycle.

**Key Functions:**
- Starts and monitors all watcher processes
- Handles graceful shutdown on signals
- Manages process health checks
- Updates dashboard with system status
- Logs all orchestrator activities

**Process Management:**
- Uses subprocess.Popen for watcher isolation
- Tracks PIDs for all running watchers
- Implements signal handlers (SIGINT, SIGTERM)
- Automatic restart on watcher failures

**Status Tracking:**
- Active watcher count
- Pending tasks in Needs_Action/
- Approved items waiting for execution
- Last activity timestamp

---

### 2. Scheduler (scheduler.py)

**Purpose:** Creates time-based task files using Python's schedule library.

**Capabilities:**
- Schedule recurring tasks (daily, weekly, hourly)
- Prevent duplicate task creation
- Check for pending tasks before scheduling new ones
- Generate task files with timestamps

**Scheduled Tasks:**
- Dashboard updates (every 4 hours)
- Weekly business reports
- LinkedIn post scheduling
- Custom scheduled operations

**Task File Format:**
```markdown
---
type: scheduled_task
task_name: [name]
scheduled_time: [timestamp]
---

# Task Instructions
[Detailed instructions for Claude]
```

---

### 3. Watchers

#### File Watcher (file_watcher.py)

**Purpose:** Monitors Inbox/ folder for new task files.

**Features:**
- Detects priority from filename (URGENT_, TASK_, INFO_)
- Tracks processed files to avoid duplicates
- Creates task files in Needs_Action/
- Logs all file processing activities

**Priority Detection:**
- 🔴 High: URGENT_, CRITICAL_
- 🟡 Medium: TASK_, TODO_
- 🟢 Low: INFO_, FYI_

**Processing Flow:**
1. Scan Inbox/ for .md files
2. Check against processed_files.json
3. Read file content
4. Detect priority from filename
5. Create task in Needs_Action/
6. Mark as processed

#### Gmail Watcher (gmail_watcher.py)

**Purpose:** Monitors Gmail for unread important emails.

**Features:**
- OAuth 2.0 authentication
- Readonly Gmail API access
- Checks every 2 minutes (configurable)
- Filters important/starred emails
- Extracts email metadata and body
- Creates task files for new emails

**Email Processing:**
- Tracks processed emails in processed_emails.json
- Extracts sender, subject, date, body
- Handles HTML and plain text emails
- Creates structured task files

**Authentication:**
- Uses credentials.json for OAuth setup
- Stores token.json for subsequent runs
- Automatic token refresh

#### WhatsApp Watcher (whatsapp_watcher.py)

**Purpose:** Monitors WhatsApp for incoming messages.

**Features:**
- Session-based authentication
- Message monitoring and extraction
- Alert creation for important messages
- Integration with WhatsApp Web

**Technology:**
- Uses Selenium/Playwright for automation
- Maintains persistent session
- Handles QR code authentication

#### LinkedIn Posters

**Three Variants:**
1. **linkedin_poster.py** - Standard automation
2. **linkedin_manual_poster.py** - Manual posting with automation
3. **linkedin_stealth_poster.py** - Stealth mode with anti-detection

**Features:**
- Automated post scheduling
- Human-like behavior simulation
- Anti-detection measures (stealth mode)
- Post approval workflow
- Optimal timing recommendations

**Technology Stack:**
- Playwright for browser automation
- playwright-stealth for detection avoidance
- Selenium as fallback option

---

### 4. Skills System

**Purpose:** Reusable AI task templates for common operations.

**Available Skills:**

| Skill | Purpose | Auto-Execute |
|-------|---------|--------------|
| Complete_Task | Mark tasks as done | ✅ |
| Draft_Email_Reply | Generate email responses | ❌ (needs approval) |
| Generate_LinkedIn_Post | Create LinkedIn content | ❌ (needs approval) |
| Process_Inbox | Handle inbox items | ✅ |
| Update_Dashboard | Refresh system status | ✅ |
| Weekly_Business_Report | Generate reports | ✅ |
| create_report | Data compilation | ✅ |
| extract_action_items | Meeting notes processing | ✅ |
| organize_files | File categorization | ✅ |
| research_compile | Information gathering | ✅ |
| summarize_document | Document summarization | ✅ |

**Skill Structure:**
```markdown
# Skill Name

## Purpose
[What this skill does]

## Instructions
[Step-by-step process]

## Template
[Output format]

## Integration
[How it connects to other components]
```

---

## Data Flow Architecture

### Task Processing Pipeline

```
1. INPUT CHANNELS
   ├── Inbox/ folder (file_watcher)
   ├── Gmail (gmail_watcher)
   ├── WhatsApp (whatsapp_watcher)
   └── Scheduler (scheduled tasks)
          ↓
2. TASK CREATION
   └── Needs_Action/ (pending tasks)
          ↓
3. HUMAN REVIEW
   ├── Approve → Approved/
   ├── Reject → Rejected/
   └── Modify → Back to Needs_Action/
          ↓
4. EXECUTION
   └── AI processes approved tasks
          ↓
5. COMPLETION
   ├── Done/ (completed tasks)
   └── Logs/ (activity records)
```

### Approval Workflow

**Automatic Processing:**
- Document summarization
- Report generation
- File organization
- Information research
- Dashboard updates

**Requires Approval:**
- Email sending
- Social media posting
- External communications
- File deletion
- Financial operations

---

## Folder Structure

### Working Directories

| Folder | Purpose | Retention |
|--------|---------|-----------|
| Inbox/ | New task submissions | Until processed |
| Needs_Action/ | Tasks awaiting review | Until approved/rejected |
| Pending_Approval/ | Items ready for approval | Until approved |
| Approved/ | Approved tasks ready to execute | Until executed |
| Done/ | Completed tasks archive | Weekly cleanup |
| Rejected/ | Rejected tasks | Manual cleanup |
| Plans/ | Project plans and strategies | Permanent |
| Logs/ | Activity logs | Daily rotation |
| Skills/ | AI skill templates | Permanent |

### Configuration Files

| File | Purpose |
|------|---------|
| .env | Environment variables and secrets |
| credentials.json | Gmail OAuth credentials |
| token.json | Gmail access token |
| processed_emails.json | Tracked email IDs |
| .processed_files.json | Tracked file hashes |
| Company_Handbook.md | Operating rules and priorities |
| Dashboard.md | Real-time system status |
| QUICK_REFERENCE.md | User guide |

---

## Technology Stack

### Core Technologies

**Language:** Python 3.x

**Key Libraries:**
- `google-auth-oauthlib` - Gmail OAuth authentication
- `google-api-python-client` - Gmail API integration
- `playwright` - Browser automation
- `playwright-stealth` - Anti-detection for LinkedIn
- `selenium` - Alternative browser automation
- `webdriver-manager` - WebDriver management
- `schedule` - Task scheduling
- `python-dotenv` - Environment configuration
- `pyperclip` - Clipboard operations
- `faker` - Test data generation

**AI Integration:**
- Claude API (via Claude Code)
- File-based task communication
- Markdown for structured data

**Authentication:**
- OAuth 2.0 for Gmail
- Session-based for WhatsApp
- Cookie-based for LinkedIn

---

## Security & Privacy

### Security Measures

**Credential Management:**
- Environment variables for sensitive data
- OAuth tokens stored locally
- No hardcoded credentials
- .gitignore for sensitive files

**API Access:**
- Gmail: Readonly scope only
- Minimal required permissions
- Token refresh handling
- Secure credential storage

**Approval System:**
- Human-in-the-loop for critical operations
- Complete audit trail in Logs/
- Approval required for external communications
- Rejection workflow for unsafe operations

### Privacy Considerations

**Data Storage:**
- All data stored locally
- No cloud dependencies (except APIs)
- File-based architecture
- User controls all data

**Processing:**
- Transparent operations
- Readable markdown logs
- No black-box decisions
- Full visibility into AI actions

---

## Key Features

### 1. Priority-Based Processing

Tasks are processed based on filename prefixes:
- URGENT_ → Immediate attention
- TASK_ → Normal priority
- INFO_ → Low priority

### 2. Multi-Channel Monitoring

Simultaneous monitoring of:
- File system (Inbox folder)
- Gmail (unread important emails)
- WhatsApp (incoming messages)
- Scheduled tasks (time-based)

### 3. Human-in-the-Loop

Critical operations require explicit approval:
- Email sending
- Social media posting
- External communications
- Data deletion

### 4. Complete Audit Trail

Every action logged:
- Daily log files per component
- Timestamped entries
- Success/failure tracking
- Error reporting

### 5. Extensible Skills System

Custom skills can be added:
- Markdown-based templates
- Reusable task patterns
- Integration with approval workflow
- Reference with @skill:[name]

### 6. Dashboard Monitoring

Real-time status display:
- Active watcher count
- Pending task count
- Last activity timestamp
- Quick action links

---

## Operational Workflows

### Daily Operations

**Morning Routine:**
1. Check Dashboard.md for system status
2. Review Needs_Action/ for pending tasks
3. Process Approved/ items
4. Check Logs/ for overnight activity

**Task Submission:**
1. Create .md file in Inbox/
2. Use priority prefix (URGENT_, TASK_, INFO_)
3. Include clear description and context
4. Wait for processing (file_watcher checks every 30s)

**Approval Process:**
1. Review task in Needs_Action/
2. Evaluate AI's proposed action
3. Move to Approved/ if acceptable
4. Move to Rejected/ with feedback if not
5. Edit and return to Needs_Action/ if needs changes

### Maintenance

**Weekly:**
- Clean Done/ folder
- Review Rejected/ items
- Update Company_Handbook.md if needed
- Check log file sizes

**Monthly:**
- Archive old logs
- Review and update Skills/
- Optimize watcher configurations
- Update dependencies

---

## Performance Characteristics

### Resource Usage

**CPU:** Low (event-driven architecture)
**Memory:** ~200-500MB (all watchers running)
**Disk:** Minimal (text files only)
**Network:** Periodic API calls (Gmail every 2 min)

### Scalability

**Current Capacity:**
- Handles 100+ tasks/day
- 5 concurrent watchers
- Multiple channel monitoring
- Real-time processing

**Limitations:**
- File-based (not suitable for high-volume)
- Single-machine deployment
- Sequential task processing
- Manual approval bottleneck

---

## Future Enhancement Opportunities

### Potential Improvements

1. **Database Integration**
   - Replace file-based storage
   - Better query capabilities
   - Improved performance

2. **Web Dashboard**
   - Real-time UI
   - Task management interface
   - Approval workflow UI

3. **Advanced Scheduling**
   - Cron-like expressions
   - Conditional scheduling
   - Task dependencies

4. **Multi-User Support**
   - Role-based access
   - Team collaboration
   - Shared task pools

5. **Enhanced AI Capabilities**
   - Context learning
   - Pattern recognition
   - Predictive task creation

6. **Integration Expansion**
   - Slack integration
   - Microsoft Teams
   - Calendar sync
   - CRM connections

---

## Troubleshooting Guide

### Common Issues

**Watcher Not Starting:**
- Check venv/bin/python exists
- Verify script permissions (chmod +x)
- Review logs for error messages
- Ensure .env file is configured

**Tasks Not Processing:**
- Verify filename follows convention
- Check file is in correct folder
- Ensure orchestrator is running
- Review processed_files.json

**Gmail Authentication Failed:**
- Delete token.json and re-authenticate
- Check credentials.json is valid
- Verify OAuth consent screen setup
- Ensure Gmail API is enabled

**LinkedIn Posting Issues:**
- Check session cookies are valid
- Verify anti-detection measures
- Review playwright installation
- Try manual poster variant

---

## System Metrics

**Current Status (as of 2026-02-22):**
- Active Watchers: 3/5
- Needs Action: 23 tasks
- Pending Approval: 0 items
- System Uptime: Running
- Last Activity: 13:02:42

**Component Status:**
- ✅ File Watcher: Running
- ✅ Gmail Watcher: Running
- ✅ Scheduler: Running
- ❌ LinkedIn Poster: Stopped
- ❌ WhatsApp Watcher: Stopped

---

## Conclusion

The AI Employee Vault represents a practical implementation of human-AI collaboration. By maintaining transparency through file-based operations, requiring approval for critical actions, and providing complete audit trails, it demonstrates how AI can augment human productivity without replacing human judgment.

The system's modular architecture allows for easy extension and customization, while its simple folder-based interface makes it accessible to non-technical users. The combination of automated monitoring, intelligent task processing, and human oversight creates a balanced approach to workplace automation.

**Key Strengths:**
- Transparent, file-based architecture
- Human-in-the-loop for critical decisions
- Multi-channel monitoring
- Complete audit trails
- Extensible skill system
- No vendor lock-in

**Best Use Cases:**
- Personal productivity automation
- Small team task management
- Email and social media management
- Scheduled reporting
- Information processing and research

---

**Document Version:** 1.0
**Last Updated:** 2026-02-26
**Maintained By:** AI Employee System
