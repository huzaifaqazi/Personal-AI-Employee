# Bronze Tier AI Employee System

## Quick Start Guide

### Overview
This is a file-based AI Employee system that helps you manage tasks, organize work, and automate routine processes. The AI monitors the Inbox folder and processes tasks according to priority rules defined in the Company Handbook.

### Folder Structure

```
AI_Employee_Vault/
├── Inbox/           # Drop new tasks here
├── Needs_Action/    # Tasks requiring your approval
├── Done/            # Completed tasks archive
├── Plans/           # Project plans and strategies
├── Logs/            # Activity logs and history
├── Skills/          # Custom AI skills and templates
├── Dashboard.md     # Real-time status overview
├── Company_Handbook.md  # Operating rules and priorities
└── README.md        # This file
```

### How to Use

#### 1. Submit Tasks
Create files in the `Inbox/` folder using these naming conventions:
- `URGENT_[description].md` - High priority (🔴)
- `TASK_[description].md` - Medium priority (🟡)
- `INFO_[description].md` - Low priority (🟢)

#### 2. Task Processing
The AI Employee will:
- Monitor the Inbox folder
- Process tasks by priority
- Move completed work to Done/
- Flag items needing approval in Needs_Action/

#### 3. Check Status
- View `Dashboard.md` for current status
- Review `Needs_Action/` for items requiring approval
- Check `Done/` for completed work
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

Tasks requiring approval will be moved to `Needs_Action/` with:
- Original task details
- AI's proposed action
- Approval request

Review and either:
- Approve: Move to Inbox with `APPROVED_` prefix
- Reject: Add feedback and move back to Inbox
- Modify: Edit and move back to Inbox

### Automation Rules

The AI can automatically:
- ✅ Summarize documents
- ✅ Create reports from data
- ✅ Organize and categorize files
- ✅ Generate plans and strategies
- ✅ Research and compile information

The AI requires approval for:
- ❌ Sending emails or messages
- ❌ Financial transactions
- ❌ Deleting files or data
- ❌ External communications

### Custom Skills

Add custom skills in the `Skills/` folder:
1. Create `[skill-name].md`
2. Define the skill's purpose and steps
3. Reference in tasks with `@skill:[skill-name]`

### Best Practices

1. **Be Specific**: Clear task descriptions get better results
2. **Use Priorities**: Mark truly urgent items as URGENT_
3. **Check Daily**: Review Dashboard.md each morning
4. **Archive Regularly**: Clean out Done/ folder weekly
5. **Update Handbook**: Refine rules based on experience

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

### Troubleshooting

**Task not processing?**
- Check filename follows naming convention
- Verify file is in Inbox/
- Ensure task description is clear

**Need to modify a task?**
- Edit the file in its current location
- AI will detect changes and reprocess

**Want to cancel a task?**
- Move file out of Inbox/
- Or prefix with `CANCELLED_`

### Getting Help

- Review `Company_Handbook.md` for operating rules
- Check `Logs/` for processing history
- Update Dashboard.md manually if needed

---

**System Version:** Bronze Tier v1.0
**Last Updated:** 2026-02-16
