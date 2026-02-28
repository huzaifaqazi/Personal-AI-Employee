#!/usr/bin/env python3
"""
Email Approval Processor - Monitors Approved/ folder and sends emails
Runs as part of the orchestrator system
"""

import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import email MCP functions
import sys
sys.path.append(str(Path(__file__).parent.parent / 'mcp_servers'))
from email_mcp import process_approved_emails, log_message

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))
CHECK_INTERVAL = 300  # 5 minutes

# Paths
APPROVED_DIR = VAULT_PATH / 'Approved'
LOGS_DIR = VAULT_PATH / 'Logs'

# Ensure directories exist
APPROVED_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


def main():
    """
    Main function - runs continuous email approval processing loop
    """
    log_message("=" * 60)
    log_message("Email Approval Processor Starting")
    log_message(f"Vault Path: {VAULT_PATH}")
    log_message(f"Check Interval: {CHECK_INTERVAL} seconds (5 minutes)")
    log_message("=" * 60)

    check_count = 0

    try:
        while True:
            check_count += 1
            log_message(f"Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Check for approved emails
            approved_files = list(APPROVED_DIR.glob('EMAIL_*.md'))

            if approved_files:
                log_message(f"Found {len(approved_files)} approved email(s)")

                # Process approved emails
                sent_count = process_approved_emails()

                if sent_count > 0:
                    log_message(f"Successfully sent {sent_count} email(s)")
            else:
                log_message("No approved emails to process")

            # Wait before next check
            log_message(f"Waiting {CHECK_INTERVAL} seconds until next check...")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("\nReceived interrupt signal - shutting down gracefully...")
        log_message("Email Approval Processor stopped")
    except Exception as e:
        log_message(f"Unexpected error in main loop: {e}", "ERROR")
        raise


if __name__ == "__main__":
    main()
