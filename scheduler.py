#!/usr/bin/env python3
"""
Scheduler - Creates scheduled task files for Claude Code to process
Uses Python's schedule library to trigger tasks at specific times
"""

import os
import time
from datetime import datetime
from pathlib import Path
import schedule
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))
NEEDS_ACTION_DIR = VAULT_PATH / 'Needs_Action'
PLANS_DIR = VAULT_PATH / 'Plans'
LOGS_DIR = VAULT_PATH / 'Logs'
PENDING_APPROVAL_DIR = VAULT_PATH / 'Pending_Approval'

# Ensure directories exist
NEEDS_ACTION_DIR.mkdir(exist_ok=True)
PLANS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Track last execution to prevent duplicates
last_executions = {}


def log_message(message, level="INFO"):
    """Log a message with timestamp to console and file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"

    # Print to console
    print(log_entry)

    # Write to daily log file
    log_date = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f"scheduler_{log_date}.md"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            if not log_file.exists() or log_file.stat().st_size == 0:
                f.write(f"# Scheduler Log - {log_date}\n\n")
            f.write(f"{log_entry}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {e}")


def check_task_pending(task_name):
    """
    Check if a previous task with the same name is still pending

    Args:
        task_name: Name of the task to check

    Returns:
        True if task is still pending, False otherwise
    """
    # Check Needs_Action for pending tasks
    pattern = f"SCHEDULED_{task_name}_*.md"
    pending_files = list(NEEDS_ACTION_DIR.glob(pattern))

    if pending_files:
        log_message(f"Previous {task_name} task still pending, skipping", "WARNING")
        return True

    return False


def create_task_file(task_name, task_type, instructions, output_location=None):
    """
    Create a scheduled task file for Claude to process

    Args:
        task_name: Name of the task (e.g., "dashboard_update")
        task_type: Type of task (e.g., "scheduled_task")
        instructions: Detailed instructions for Claude
        output_location: Where to save the output (optional)

    Returns:
        Path to created task file or None if failed
    """
    try:
        # Check if previous task is still pending
        if check_task_pending(task_name):
            return None

        # Create timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        scheduled_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create filename
        filename = f"SCHEDULED_{task_name}_{timestamp}.md"
        filepath = NEEDS_ACTION_DIR / filename

        # Build task content
        content = f"""---
type: {task_type}
task: {task_name}
scheduled: {scheduled_time}
status: pending
priority: medium
---

# Scheduled Task: {task_name.replace('_', ' ').title()}

## Scheduled Time
{scheduled_time}

## Instructions
{instructions}
"""

        if output_location:
            content += f"""
## Output Location
{output_location}
"""

        content += """
## Completion
When complete:
1. Mark this task as done
2. Move to Done/ folder
3. Log the completion

---
*This is an automated scheduled task*
"""

        # Write task file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        log_message(f"Created scheduled task: {filename}")

        # Track execution
        last_executions[task_name] = datetime.now()

        return filepath

    except Exception as e:
        log_message(f"Failed to create task file: {e}", "ERROR")
        return None


def schedule_dashboard_update():
    """Schedule dashboard update task"""
    log_message("Triggering dashboard update task")

    instructions = """Update the Dashboard.md file with current system status.

Include:
- System status (orchestrator, watchers)
- Active watcher count
- Tasks pending in Needs_Action/
- Items in Pending_Approval/
- Recent activity summary
- Quick action items

Use the current date and time for "Last Updated" field.
"""

    create_task_file(
        task_name="dashboard_update",
        task_type="scheduled_task",
        instructions=instructions,
        output_location="Dashboard.md"
    )


def schedule_daily_briefing():
    """Schedule daily briefing generation"""
    log_message("Triggering daily briefing task")

    date_str = datetime.now().strftime('%Y-%m-%d')

    instructions = f"""Generate a comprehensive daily briefing for {date_str}.

Include:
1. **Tasks Completed Yesterday**
   - Review Done/ folder for yesterday's date
   - Summarize key accomplishments
   - Count emails sent, posts made, etc.

2. **Tasks Pending Today**
   - List items in Needs_Action/
   - Highlight high priority items
   - Note any overdue tasks

3. **System Health**
   - Check all watchers are running
   - Review recent logs for errors
   - Note any issues or warnings

4. **Priorities for Today**
   - Identify most urgent tasks
   - Suggest order of execution
   - Flag any blockers

5. **Reminders**
   - Check Pending_Approval/ folder
   - Review LinkedIn post schedule
   - Monitor WhatsApp alerts

Format as a clear, actionable briefing.
"""

    create_task_file(
        task_name="daily_briefing",
        task_type="scheduled_task",
        instructions=instructions,
        output_location=f"Plans/Daily_Briefing_{date_str}.md"
    )


def schedule_weekly_summary():
    """Schedule weekly summary generation"""
    log_message("Triggering weekly summary task")

    date_str = datetime.now().strftime('%Y-%m-%d')

    instructions = f"""Generate a comprehensive weekly summary for the week ending {date_str}.

Include:
1. **Week Overview**
   - Total tasks completed
   - Emails sent and received
   - LinkedIn posts published
   - WhatsApp alerts handled

2. **Key Accomplishments**
   - Major tasks completed
   - Important emails sent
   - Successful automations

3. **Statistics**
   - Review all logs from the past 7 days
   - Count activities by type
   - Calculate success rates

4. **Issues and Challenges**
   - Any errors or failures
   - Watcher downtime
   - Pending items not completed

5. **Next Week Planning**
   - Carry-over tasks
   - Upcoming priorities
   - System improvements needed

6. **Recommendations**
   - Process improvements
   - Configuration changes
   - New automations to consider

Format as a comprehensive weekly report.
"""

    create_task_file(
        task_name="weekly_summary",
        task_type="scheduled_task",
        instructions=instructions,
        output_location=f"Plans/Weekly_Summary_{date_str}.md"
    )


def schedule_approval_reminder():
    """Schedule reminder to check pending approvals"""
    log_message("Checking pending approvals")

    # Count pending approvals
    pending_count = len(list(PENDING_APPROVAL_DIR.glob('*.md')))

    if pending_count == 0:
        log_message("No pending approvals")
        return

    log_message(f"Found {pending_count} pending approval(s)")

    instructions = f"""**REMINDER:** You have {pending_count} item(s) awaiting approval.

## Action Required

Please review the following:
- Check `Pending_Approval/` folder
- Review each draft carefully
- Approve, reject, or edit as needed

## Pending Items

Location: `Pending_Approval/`
Count: {pending_count}

## Approval Process

1. **Review:** Open each file in Pending_Approval/
2. **Decide:**
   - Approve: Move to Approved/
   - Reject: Move to Rejected/
   - Edit: Modify content, then move to Approved/
3. **Execute:** System will process approved items automatically

## Priority

Items in Pending_Approval/ may include:
- Email drafts requiring your review
- LinkedIn posts ready to publish
- WhatsApp messages to send

Please review within the next hour if possible.

---
*This is an automated reminder - no action needed on this file*
*Just check the Pending_Approval/ folder*
"""

    # Create reminder in Needs_Action
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"REMINDER_pending_approvals_{timestamp}.md"
    filepath = NEEDS_ACTION_DIR / filename

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"""---
type: reminder
task: pending_approvals
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
status: info
priority: high
---

# Reminder: Pending Approvals

{instructions}
""")

        log_message(f"Created approval reminder: {filename}")

    except Exception as e:
        log_message(f"Failed to create reminder: {e}", "ERROR")


def setup_schedule():
    """Configure all scheduled tasks"""
    log_message("=" * 60)
    log_message("Setting up scheduled tasks...")
    log_message("=" * 60)

    # Dashboard update every 4 hours
    schedule.every(4).hours.do(schedule_dashboard_update)
    log_message("Scheduled: Dashboard update every 4 hours")

    # Daily briefing at 8:00 AM
    schedule.every().day.at("08:00").do(schedule_daily_briefing)
    log_message("Scheduled: Daily briefing at 08:00 AM")

    # Weekly summary on Sunday at 8:00 PM
    schedule.every().sunday.at("20:00").do(schedule_weekly_summary)
    log_message("Scheduled: Weekly summary on Sunday at 20:00 PM")

    # Approval reminder every 30 minutes
    schedule.every(30).minutes.do(schedule_approval_reminder)
    log_message("Scheduled: Approval reminder every 30 minutes")

    log_message("=" * 60)
    log_message("All scheduled tasks configured")
    log_message("=" * 60)


def run_scheduler():
    """Main scheduler loop"""
    log_message("Scheduler starting...")

    # Setup all scheduled tasks
    setup_schedule()

    # Run initial checks
    log_message("Running initial approval check...")
    schedule_approval_reminder()

    log_message("Scheduler running. Press Ctrl+C to stop.")

    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    except KeyboardInterrupt:
        log_message("\nScheduler stopped by user")
    except Exception as e:
        log_message(f"Scheduler error: {e}", "ERROR")
        raise


def main():
    """Main function"""
    log_message("=" * 60)
    log_message("AI Employee Scheduler")
    log_message(f"Vault Path: {VAULT_PATH}")
    log_message("=" * 60)

    # Check directories
    if not NEEDS_ACTION_DIR.exists():
        log_message("ERROR: Needs_Action/ directory not found!", "ERROR")
        return

    # Run scheduler
    run_scheduler()


if __name__ == "__main__":
    main()
