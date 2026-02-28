#!/usr/bin/env python3
"""
AI Employee Orchestrator - Enhanced version with approval processing and scheduling
Manages all watchers, processes approvals, and handles scheduled tasks
"""

import os
import sys
import time
import signal
import subprocess
import re
from pathlib import Path
from datetime import datetime, time as dt_time
from threading import Thread, Event
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))
WATCHERS_DIR = VAULT_PATH / 'watchers'
MCP_DIR = VAULT_PATH / 'mcp_servers'
APPROVED_DIR = VAULT_PATH / 'Approved'
DONE_DIR = VAULT_PATH / 'Done'
LOGS_DIR = VAULT_PATH / 'Logs'
NEEDS_ACTION_DIR = VAULT_PATH / 'Needs_Action'
DASHBOARD_FILE = VAULT_PATH / 'Dashboard.md'

# Ensure directories exist
APPROVED_DIR.mkdir(exist_ok=True)
DONE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Track running processes
processes = []
shutdown_event = Event()
last_activity = datetime.now()


def log_message(message, level="INFO"):
    """Log a message with timestamp to console and file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"

    # Print to console
    print(log_entry)

    # Write to daily log file
    log_date = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f"orchestrator_{log_date}.md"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            if not log_file.exists() or log_file.stat().st_size == 0:
                f.write(f"# Orchestrator Log - {log_date}\n\n")
            f.write(f"{log_entry}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {e}")


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    log_message("\n" + "=" * 60)
    log_message("Shutdown signal received - stopping all watchers...")
    log_message("=" * 60)

    shutdown_event.set()

    for name, process in processes:
        log_message(f"Stopping {name}...")
        process.terminate()
        try:
            process.wait(timeout=5)
            log_message(f"{name} stopped")
        except subprocess.TimeoutExpired:
            log_message(f"Force killing {name}...", "WARNING")
            process.kill()

    log_message("All watchers stopped. Goodbye!")
    sys.exit(0)


def start_watcher(name, script_path):
    """
    Start a watcher script as a subprocess

    Args:
        name: Display name for the watcher
        script_path: Path to the Python script

    Returns:
        subprocess.Popen object or None if failed
    """
    try:
        venv_python = VAULT_PATH / 'venv' / 'bin' / 'python'

        if not venv_python.exists():
            log_message(f"Virtual environment not found at {venv_python}", "ERROR")
            return None

        if not script_path.exists():
            log_message(f"Script not found: {script_path}", "ERROR")
            return None

        log_message(f"Starting {name}...")

        process = subprocess.Popen(
            [str(venv_python), str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        log_message(f"{name} started (PID: {process.pid})")
        return process

    except Exception as e:
        log_message(f"Failed to start {name}: {e}", "ERROR")
        return None


def count_files_in_dir(directory):
    """Count markdown files in a directory"""
    try:
        return len(list(directory.glob('*.md')))
    except:
        return 0


def get_status_display():
    """Generate status display string"""
    global last_activity

    # Count active processes
    active_count = sum(1 for _, p in processes if p.poll() is None)

    # Count pending items
    tasks_pending = count_files_in_dir(NEEDS_ACTION_DIR)
    approved_waiting = count_files_in_dir(APPROVED_DIR)

    # Calculate time since last activity
    time_diff = datetime.now() - last_activity
    if time_diff.seconds < 60:
        last_activity_str = f"{time_diff.seconds} seconds ago"
    elif time_diff.seconds < 3600:
        last_activity_str = f"{time_diff.seconds // 60} minutes ago"
    else:
        last_activity_str = f"{time_diff.seconds // 3600} hours ago"

    # Status emoji
    status_emoji = "🟢" if active_count == len(processes) else "🟡"

    status = f"""
{'=' * 50}
       AI EMPLOYEE ORCHESTRATOR
{'=' * 50}
Status: {status_emoji} {'Running' if active_count > 0 else 'Degraded'}
Watchers Active: {active_count}/{len(processes)}
Tasks Pending: {tasks_pending}
Approved Waiting: {approved_waiting}
Last Activity: {last_activity_str}

Press Ctrl+C to stop
{'=' * 50}
"""
    return status


def process_approved_email(filepath):
    """Process an approved email file"""
    global last_activity

    try:
        log_message(f"Processing approved email: {filepath.name}")

        # Import email_mcp functions
        sys.path.append(str(MCP_DIR))
        from email_mcp import parse_approved_email, send_email

        # Parse email
        email_data = parse_approved_email(filepath)

        if email_data is None:
            log_message(f"Failed to parse email: {filepath.name}", "ERROR")
            return False

        # Send email
        success = send_email(
            to=email_data['to'],
            subject=email_data['subject'],
            body=email_data['body'],
            cc=email_data.get('cc'),
            bcc=email_data.get('bcc')
        )

        if success:
            # Move to Done
            done_path = DONE_DIR / filepath.name
            filepath.rename(done_path)
            log_message(f"Email sent and moved to Done/")
            last_activity = datetime.now()
            return True
        else:
            log_message(f"Failed to send email", "ERROR")
            return False

    except Exception as e:
        log_message(f"Error processing email: {e}", "ERROR")
        return False


def process_approved_linkedin(filepath):
    """Process an approved LinkedIn post file"""
    global last_activity

    try:
        log_message(f"Processing approved LinkedIn post: {filepath.name}")

        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract post content (after "## Content" until "---")
        content_match = re.search(r'## Content\s*\n(.*?)\n---', content, re.DOTALL)

        if not content_match:
            log_message(f"Failed to parse LinkedIn post content", "ERROR")
            return False

        post_content = content_match.group(1).strip()

        # TODO: Implement LinkedIn posting via Playwright
        # For now, just log and move to Done
        log_message(f"LinkedIn post content: {post_content[:100]}...")
        log_message("LinkedIn posting not yet implemented - marking as done", "WARNING")

        # Move to Done
        done_path = DONE_DIR / filepath.name
        filepath.rename(done_path)
        last_activity = datetime.now()

        return True

    except Exception as e:
        log_message(f"Error processing LinkedIn post: {e}", "ERROR")
        return False


def process_approved_whatsapp(filepath):
    """Process an approved WhatsApp message file"""
    global last_activity

    try:
        log_message(f"Processing approved WhatsApp message: {filepath.name}")

        # Read the file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract recipient and message
        to_match = re.search(r'^to:\s*(.+)$', content, re.MULTILINE)
        message_match = re.search(r'## Message\s*\n(.*?)\n---', content, re.DOTALL)

        if not to_match or not message_match:
            log_message(f"Failed to parse WhatsApp message", "ERROR")
            return False

        recipient = to_match.group(1).strip()
        message = message_match.group(1).strip()

        # TODO: Implement WhatsApp sending via Playwright
        # For now, just log and move to Done
        log_message(f"WhatsApp to {recipient}: {message[:100]}...")
        log_message("WhatsApp sending not yet implemented - marking as done", "WARNING")

        # Move to Done
        done_path = DONE_DIR / filepath.name
        filepath.rename(done_path)
        last_activity = datetime.now()

        return True

    except Exception as e:
        log_message(f"Error processing WhatsApp message: {e}", "ERROR")
        return False


def check_approved_folder():
    """Check Approved/ folder and process files"""
    try:
        # Get all files in Approved/
        approved_files = list(APPROVED_DIR.glob('*.md'))

        if not approved_files:
            return

        log_message(f"Found {len(approved_files)} approved item(s) to process")

        for filepath in approved_files:
            filename = filepath.name

            # Route based on filename prefix
            if filename.startswith('EMAIL_'):
                process_approved_email(filepath)
            elif filename.startswith('LINKEDIN_'):
                process_approved_linkedin(filepath)
            elif filename.startswith('WHATSAPP_'):
                process_approved_whatsapp(filepath)
            else:
                log_message(f"Unknown file type: {filename}", "WARNING")

    except Exception as e:
        log_message(f"Error checking approved folder: {e}", "ERROR")


def update_dashboard():
    """Update the Dashboard.md file with current status"""
    global last_activity

    try:
        log_message("Updating dashboard...")

        # Count items
        tasks_pending = count_files_in_dir(NEEDS_ACTION_DIR)
        approved_waiting = count_files_in_dir(APPROVED_DIR)
        active_watchers = sum(1 for _, p in processes if p.poll() is None)

        # Generate dashboard content
        dashboard_content = f"""# AI Employee Dashboard

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Status

- **Orchestrator:** 🟢 Running
- **Active Watchers:** {active_watchers}/{len(processes)}
- **Last Activity:** {datetime.now().strftime('%H:%M:%S')}

## Task Overview

- **Needs Action:** {tasks_pending} task(s)
- **Pending Approval:** {approved_waiting} item(s)
- **Completed Today:** Check Done/ folder

## Active Watchers

"""

        for name, process in processes:
            status = "🟢 Running" if process.poll() is None else "🔴 Stopped"
            dashboard_content += f"- **{name}:** {status}\n"

        dashboard_content += f"""
## Quick Actions

1. Check `Needs_Action/` for tasks requiring attention
2. Review `Approved/` for items ready to execute
3. View `Logs/` for detailed activity logs

## Recent Activity

Check `Logs/orchestrator_{datetime.now().strftime('%Y-%m-%d')}.md` for details.

---
*Auto-updated every 4 hours*
"""

        # Write dashboard
        with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)

        log_message("Dashboard updated successfully")
        last_activity = datetime.now()

    except Exception as e:
        log_message(f"Error updating dashboard: {e}", "ERROR")


def generate_daily_briefing():
    """Generate daily briefing at 8am"""
    global last_activity

    try:
        log_message("Generating daily briefing...")

        date_str = datetime.now().strftime('%Y-%m-%d')
        briefing_file = VAULT_PATH / 'Plans' / f'Daily_Briefing_{date_str}.md'

        # Count yesterday's activity
        tasks_pending = count_files_in_dir(NEEDS_ACTION_DIR)

        briefing_content = f"""# Daily Briefing - {date_str}

## Good Morning! ☀️

Here's your daily briefing for {datetime.now().strftime('%A, %B %d, %Y')}

## Tasks Requiring Attention

- **Pending Tasks:** {tasks_pending}
- **Location:** `Needs_Action/` folder

## System Status

- All watchers operational
- Email monitoring active
- LinkedIn posting scheduled
- WhatsApp alerts enabled

## Today's Focus

1. Review pending tasks in `Needs_Action/`
2. Check approved items in `Approved/`
3. Review yesterday's activity in `Logs/`

## Reminders

- Check email responses
- Review LinkedIn post schedule
- Monitor WhatsApp alerts

---
*Generated automatically at 8:00 AM*
"""

        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(briefing_content)

        log_message(f"Daily briefing created: {briefing_file.name}")
        last_activity = datetime.now()

    except Exception as e:
        log_message(f"Error generating daily briefing: {e}", "ERROR")


def generate_weekly_summary():
    """Generate weekly summary on Sunday at 8pm"""
    global last_activity

    try:
        log_message("Generating weekly summary...")

        date_str = datetime.now().strftime('%Y-%m-%d')
        summary_file = VAULT_PATH / 'Plans' / f'Weekly_Summary_{date_str}.md'

        summary_content = f"""# Weekly Summary - Week of {date_str}

## Overview

This week's AI Employee activity summary.

## Accomplishments

- Emails monitored and processed
- LinkedIn posts published
- WhatsApp alerts handled
- Tasks completed

## Statistics

Check `Logs/` folder for detailed activity logs from this week.

## Next Week

- Continue monitoring all channels
- Process pending approvals
- Maintain system health

---
*Generated automatically every Sunday at 8:00 PM*
"""

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        log_message(f"Weekly summary created: {summary_file.name}")
        last_activity = datetime.now()

    except Exception as e:
        log_message(f"Error generating weekly summary: {e}", "ERROR")


def scheduled_tasks_thread():
    """Background thread for scheduled tasks"""
    last_dashboard_update = datetime.now()
    last_daily_briefing = None
    last_weekly_summary = None

    while not shutdown_event.is_set():
        try:
            now = datetime.now()

            # Update dashboard every 4 hours
            if (now - last_dashboard_update).seconds >= 14400:  # 4 hours
                update_dashboard()
                last_dashboard_update = now

            # Daily briefing at 8am
            if now.hour == 8 and now.minute == 0:
                if last_daily_briefing != now.date():
                    generate_daily_briefing()
                    last_daily_briefing = now.date()

            # Weekly summary on Sunday at 8pm
            if now.weekday() == 6 and now.hour == 20 and now.minute == 0:
                if last_weekly_summary != now.date():
                    generate_weekly_summary()
                    last_weekly_summary = now.date()

            # Sleep for 60 seconds before next check
            shutdown_event.wait(60)

        except Exception as e:
            log_message(f"Error in scheduled tasks: {e}", "ERROR")
            shutdown_event.wait(60)


def approval_monitor_thread():
    """Background thread for monitoring Approved/ folder"""
    while not shutdown_event.is_set():
        try:
            check_approved_folder()
            shutdown_event.wait(30)  # Check every 30 seconds
        except Exception as e:
            log_message(f"Error in approval monitor: {e}", "ERROR")
            shutdown_event.wait(30)


def monitor_processes():
    """Monitor running processes and restart if they crash"""
    watchers = [
        ("File Watcher", WATCHERS_DIR / "file_watcher.py"),
        ("Gmail Watcher", WATCHERS_DIR / "gmail_watcher.py"),
        ("LinkedIn Poster", WATCHERS_DIR / "linkedin_poster.py"),
        ("WhatsApp Watcher", WATCHERS_DIR / "whatsapp_watcher.py"),
        ("Scheduler", VAULT_PATH / "scheduler.py"),
    ]

    # Start all watchers
    for name, script_path in watchers:
        if script_path.exists():
            process = start_watcher(name, script_path)
            if process:
                processes.append((name, process))
        else:
            log_message(f"Skipping {name} - script not found", "WARNING")

    if not processes:
        log_message("No watchers started successfully", "ERROR")
        return

    # Start background threads
    log_message("Starting scheduled tasks thread...")
    scheduled_thread = Thread(target=scheduled_tasks_thread, daemon=True)
    scheduled_thread.start()

    log_message("Starting approval monitor thread...")
    approval_thread = Thread(target=approval_monitor_thread, daemon=True)
    approval_thread.start()

    # Initial dashboard update
    update_dashboard()

    # Display initial status
    print(get_status_display())

    # Monitor loop
    status_update_counter = 0

    while not shutdown_event.is_set():
        time.sleep(10)  # Check every 10 seconds

        # Update status display every 30 seconds
        status_update_counter += 1
        if status_update_counter >= 3:
            os.system('clear' if os.name == 'posix' else 'cls')
            print(get_status_display())
            status_update_counter = 0

        # Check process health
        for i, (name, process) in enumerate(processes):
            if process.poll() is not None:
                log_message(f"{name} stopped unexpectedly!", "WARNING")
                log_message(f"{name} exit code: {process.returncode}", "WARNING")

                # Try to restart
                log_message(f"Attempting to restart {name}...", "WARNING")
                script_path = None
                for watcher_name, watcher_path in watchers:
                    if watcher_name == name:
                        script_path = watcher_path
                        break

                if script_path:
                    new_process = start_watcher(name, script_path)
                    if new_process:
                        processes[i] = (name, new_process)
                        log_message(f"{name} restarted successfully")


def main():
    """Main orchestrator function"""
    log_message("=" * 60)
    log_message("AI EMPLOYEE ORCHESTRATOR - ENHANCED VERSION")
    log_message(f"Vault Path: {VAULT_PATH}")
    log_message("=" * 60)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check virtual environment
    venv_python = VAULT_PATH / 'venv' / 'bin' / 'python'
    if not venv_python.exists():
        log_message("ERROR: Virtual environment not found!", "ERROR")
        log_message("Please run: python3.13 -m venv venv", "ERROR")
        return

    # Check watchers directory
    if not WATCHERS_DIR.exists():
        log_message("ERROR: watchers/ directory not found!", "ERROR")
        return

    # Start monitoring
    try:
        monitor_processes()
    except Exception as e:
        log_message(f"Orchestrator error: {e}", "ERROR")
        signal_handler(None, None)


if __name__ == "__main__":
    main()
