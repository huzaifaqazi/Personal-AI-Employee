#!/usr/bin/env python3
"""
WhatsApp Watcher - Monitors WhatsApp Web for urgent messages
Checks every 60 seconds for messages with specific keywords
"""

import os
import re
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))
WHATSAPP_SESSION_PATH = Path(os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session'))
CHECK_INTERVAL = 60  # 60 seconds

# Keywords to monitor (case-insensitive)
URGENT_KEYWORDS = ["urgent", "invoice", "payment", "help", "asap"]

# Paths
NEEDS_ACTION_DIR = VAULT_PATH / 'Needs_Action'
LOGS_DIR = VAULT_PATH / 'Logs'
PROCESSED_MESSAGES_FILE = VAULT_PATH / 'processed_whatsapp.txt'

# Ensure directories exist
NEEDS_ACTION_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
WHATSAPP_SESSION_PATH.mkdir(exist_ok=True)


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
    log_file = LOGS_DIR / f"whatsapp_{log_date}.md"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            if not log_file.exists() or log_file.stat().st_size == 0:
                f.write(f"# WhatsApp Watcher Log - {log_date}\n\n")
            f.write(f"{log_entry}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {e}")


def load_processed_messages():
    """
    Load the set of already processed message IDs

    Returns:
        Set of message IDs that have been processed
    """
    if PROCESSED_MESSAGES_FILE.exists():
        try:
            with open(PROCESSED_MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f if line.strip())
        except Exception as e:
            log_message(f"Failed to load processed messages: {e}", "WARNING")
            return set()
    return set()


def save_processed_message(message_id):
    """
    Save a processed message ID to disk

    Args:
        message_id: Unique identifier for the message
    """
    try:
        with open(PROCESSED_MESSAGES_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{message_id}\n")
    except Exception as e:
        log_message(f"Failed to save processed message: {e}", "ERROR")


def contains_urgent_keyword(text):
    """
    Check if text contains any urgent keywords

    Args:
        text: Message text to check

    Returns:
        Tuple of (bool, list of matched keywords)
    """
    if not text:
        return False, []

    text_lower = text.lower()
    matched = [kw for kw in URGENT_KEYWORDS if kw in text_lower]
    return len(matched) > 0, matched


def create_task_file(contact_name, message_text, matched_keywords):
    """
    Create a task file in Needs_Action/ directory

    Args:
        contact_name: Name of the contact who sent the message
        message_text: The message content
        matched_keywords: List of keywords that triggered this task

    Returns:
        Path to created task file or None if failed
    """
    try:
        # Create safe filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_contact = "".join(c for c in contact_name if c.isalnum() or c in (' ', '-', '_'))
        safe_contact = safe_contact[:30].strip()
        filename = f"whatsapp_{timestamp}_{safe_contact}.md"
        filepath = NEEDS_ACTION_DIR / filename

        # Format timestamp
        received_formatted = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create task file content
        content = f"""---
type: whatsapp
from: {contact_name}
received: {received_formatted}
priority: high
status: pending
requires_approval: true
keywords: {', '.join(matched_keywords)}
---

# WhatsApp: {contact_name}

## Message
{message_text}

## Matched Keywords
{', '.join(matched_keywords)}

## Suggested Responses
1. "Thanks for reaching out! I'll get back to you shortly."
2. "Received. Let me check and respond by end of day."
3. "Could you provide more details about this?"

**IMPORTANT:** All WhatsApp replies require human approval.
"""

        # Write task file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        log_message(f"Created task file: {filename}")
        return filepath

    except Exception as e:
        log_message(f"Failed to create task file: {e}", "ERROR")
        return None


def wait_for_whatsapp_login(page):
    """
    Wait for user to scan QR code and login to WhatsApp Web

    Args:
        page: Playwright page object

    Returns:
        True if login successful, False otherwise
    """
    try:
        log_message("Waiting for WhatsApp Web to load...")
        page.goto('https://web.whatsapp.com', wait_until='load', timeout=60000)

        # Wait for page to stabilize
        time.sleep(5)

        # Check if already logged in
        try:
            page.wait_for_selector('[data-testid="chat-list"]', timeout=5000)
            log_message("Already logged in to WhatsApp Web!")
            return True
        except PlaywrightTimeout:
            pass

        # Wait for QR code
        log_message("=" * 60)
        log_message("WAITING FOR QR CODE...")
        log_message("=" * 60)

        # Try multiple selectors for QR code
        qr_selectors = [
            'canvas[aria-label*="QR"]',
            'canvas[aria-label*="Scan"]',
            'div[data-ref] canvas',
            'canvas'
        ]

        qr_found = False
        for selector in qr_selectors:
            try:
                page.wait_for_selector(selector, timeout=5000)
                log_message(f"QR code element found with selector: {selector}")
                qr_found = True
                break
            except PlaywrightTimeout:
                continue

        if qr_found:
            log_message("Waiting for QR code to fully render...")
            time.sleep(5)  # Extra wait for rendering
        else:
            log_message("QR code element not found, taking full page screenshot...", "WARNING")

        # Take full page screenshot
        qr_screenshot_path = VAULT_PATH / 'whatsapp_qr_code.png'
        page.screenshot(path=str(qr_screenshot_path), full_page=True)
        log_message(f"Screenshot saved to: {qr_screenshot_path}")

        log_message("=" * 60)
        log_message("PLEASE SCAN THE QR CODE:")
        log_message(f"1. Open this file in Windows: {qr_screenshot_path}")
        log_message("2. Open WhatsApp on your phone")
        log_message("3. Go to: Settings > Linked Devices > Link a Device")
        log_message("4. Scan the QR code from the screenshot")
        log_message("5. Waiting up to 120 seconds for scan...")
        log_message("=" * 60)

        # Wait for chat list to appear (indicates successful login)
        try:
            page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
            log_message("QR code scanned successfully!")
            time.sleep(3)  # Wait for full load
            return True
        except PlaywrightTimeout:
            log_message("QR code scan timeout", "ERROR")
            return False

    except Exception as e:
        log_message(f"Error during WhatsApp login: {e}", "ERROR")
        return False


def check_for_urgent_messages(page, processed_ids):
    """
    Check for unread messages containing urgent keywords

    Args:
        page: Playwright page object
        processed_ids: Set of already processed message IDs

    Returns:
        Number of new urgent messages processed
    """
    try:
        # Check if still logged in
        try:
            page.wait_for_selector('[data-testid="chat-list"]', timeout=5000)
        except PlaywrightTimeout:
            log_message("Not logged in to WhatsApp Web", "ERROR")
            return 0

        # Find all unread chats (chats with unread badge)
        unread_chats = page.query_selector_all('[data-testid="cell-frame-container"]:has([data-testid="icon-unread-count"])')

        if not unread_chats:
            log_message("No unread messages found")
            return 0

        log_message(f"Found {len(unread_chats)} unread chat(s)")
        urgent_count = 0

        for chat in unread_chats[:10]:  # Limit to first 10 to avoid overwhelming
            try:
                # Get contact name from the chat
                contact_elem = chat.query_selector('[data-testid="cell-frame-title"]')
                if not contact_elem:
                    continue

                contact_name = contact_elem.inner_text().strip()

                # Click on the chat to open it
                chat.click()
                time.sleep(1)

                # Get the last message in the chat
                messages = page.query_selector_all('[data-testid="msg-container"]')
                if not messages:
                    continue

                # Check last few messages for urgent keywords
                for message in messages[-3:]:  # Check last 3 messages
                    try:
                        # Get message text
                        text_elem = message.query_selector('.selectable-text')
                        if not text_elem:
                            continue

                        message_text = text_elem.inner_text().strip()

                        # Create unique message ID
                        message_id = f"{contact_name}_{message_text[:50]}"

                        # Skip if already processed
                        if message_id in processed_ids:
                            continue

                        # Check for urgent keywords
                        is_urgent, matched_keywords = contains_urgent_keyword(message_text)

                        if is_urgent:
                            log_message(f"Urgent message from {contact_name}: {matched_keywords}")
                            log_message(f"Preview: {message_text[:100]}...")

                            # Create task file
                            task_file = create_task_file(contact_name, message_text, matched_keywords)

                            if task_file:
                                save_processed_message(message_id)
                                processed_ids.add(message_id)
                                urgent_count += 1
                                log_message(f"Created task for urgent message from {contact_name}")

                    except Exception as e:
                        log_message(f"Error processing message: {e}", "WARNING")
                        continue

                # Go back to chat list
                back_button = page.query_selector('[data-testid="back"]')
                if back_button:
                    back_button.click()
                    time.sleep(0.5)

            except Exception as e:
                log_message(f"Error processing chat: {e}", "WARNING")
                continue

        return urgent_count

    except Exception as e:
        log_message(f"Error checking messages: {e}", "ERROR")
        return 0


def main():
    """
    Main function - runs continuous WhatsApp monitoring loop
    """
    log_message("=" * 60)
    log_message("WhatsApp Watcher Starting")
    log_message(f"Vault Path: {VAULT_PATH}")
    log_message(f"Session Path: {WHATSAPP_SESSION_PATH}")
    log_message(f"Check Interval: {CHECK_INTERVAL} seconds")
    log_message(f"Monitoring Keywords: {', '.join(URGENT_KEYWORDS)}")
    log_message("=" * 60)

    # Load processed messages
    processed_ids = load_processed_messages()
    log_message(f"Loaded {len(processed_ids)} previously processed message IDs")

    check_count = 0

    try:
        with sync_playwright() as p:
            # Launch browser with persistent context (saves session)
            log_message("Launching browser...")

            # First run: not headless to allow QR code scan
            # Subsequent runs: headless if session exists
            session_exists = WHATSAPP_SESSION_PATH.exists() and len(list(WHATSAPP_SESSION_PATH.glob('*'))) > 0
            headless = session_exists

            if not headless:
                log_message("First run detected - browser will open for QR code scan")

            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(WHATSAPP_SESSION_PATH),
                headless=headless,
                args=['--no-sandbox']
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            # Login to WhatsApp Web
            if not wait_for_whatsapp_login(page):
                log_message("Failed to login to WhatsApp Web", "ERROR")
                browser.close()
                return

            log_message("Starting monitoring loop...")

            while True:
                check_count += 1
                log_message(f"Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Check for urgent messages
                urgent_count = check_for_urgent_messages(page, processed_ids)

                if urgent_count > 0:
                    log_message(f"Processed {urgent_count} urgent message(s)")

                # Wait before next check
                log_message(f"Waiting {CHECK_INTERVAL} seconds until next check...")
                time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("\nReceived interrupt signal - shutting down gracefully...")
        log_message("WhatsApp Watcher stopped")
    except Exception as e:
        log_message(f"Unexpected error in main loop: {e}", "ERROR")
        raise


if __name__ == "__main__":
    main()
