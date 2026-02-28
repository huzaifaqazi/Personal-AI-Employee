#!/usr/bin/env python3
"""
LinkedIn Poster - Automates posting to LinkedIn from a queue
Checks every 30 minutes for scheduled posts and publishes them
"""

import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '.'))
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')
CHECK_INTERVAL = 1800  # 30 minutes in seconds
MAX_POSTS_PER_DAY = 5

# Paths
PLANS_DIR = VAULT_PATH / 'Plans'
DONE_DIR = VAULT_PATH / 'Done'
LOGS_DIR = VAULT_PATH / 'Logs'
LINKEDIN_POSTS_FILE = PLANS_DIR / 'LinkedIn_Posts.md'
SESSION_DIR = VAULT_PATH / 'linkedin_session'

# Ensure directories exist
PLANS_DIR.mkdir(exist_ok=True)
DONE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
SESSION_DIR.mkdir(exist_ok=True)


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
    log_file = LOGS_DIR / f"linkedin_{log_date}.md"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            if not log_file.exists() or log_file.stat().st_size == 0:
                f.write(f"# LinkedIn Poster Log - {log_date}\n\n")
            f.write(f"{log_entry}\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {e}")


def parse_posts_file():
    """
    Parse LinkedIn_Posts.md file to extract pending posts

    Returns:
        List of dictionaries with post details
    """
    if not LINKEDIN_POSTS_FILE.exists():
        log_message("LinkedIn_Posts.md not found, creating template...", "WARNING")
        create_template_file()
        return []

    try:
        with open(LINKEDIN_POSTS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        posts = []
        # Split by post headers (## Post N)
        post_sections = re.split(r'\n## Post \d+\n', content)[1:]  # Skip header

        for section in post_sections:
            # Extract status
            status_match = re.search(r'Status:\s*(\w+)', section)
            status = status_match.group(1) if status_match else 'unknown'

            # Extract scheduled time
            scheduled_match = re.search(r'Scheduled:\s*(.+)', section)
            scheduled_str = scheduled_match.group(1).strip() if scheduled_match else None

            # Parse scheduled time
            scheduled_time = None
            if scheduled_str:
                try:
                    scheduled_time = datetime.strptime(scheduled_str, '%Y-%m-%d %H:%M')
                except ValueError:
                    log_message(f"Invalid date format: {scheduled_str}", "WARNING")

            # Extract content (everything after "Content:" until "---" or end)
            content_match = re.search(r'Content:\s*\n(.*?)(?:\n---|\Z)', section, re.DOTALL)
            content = content_match.group(1).strip() if content_match else ''

            if content and status == 'pending' and scheduled_time:
                posts.append({
                    'status': status,
                    'scheduled': scheduled_time,
                    'content': content,
                    'raw_section': section
                })

        return posts

    except Exception as e:
        log_message(f"Error parsing posts file: {e}", "ERROR")
        return []


def create_template_file():
    """Create a template LinkedIn_Posts.md file"""
    template = """# LinkedIn Posts Queue

## Post 1
Status: pending
Scheduled: 2026-01-10 10:00

Content:
Excited to share our new AI automation tool! 🚀
Built with Claude Code and Python.
#AI #Automation #Tech

---

## Post 2
Status: pending
Scheduled: 2026-01-10 15:00

Content:
Just completed our Bronze Tier AI Employee!
Check out the results...
#Hackathon #AIEmployee

---
"""
    try:
        with open(LINKEDIN_POSTS_FILE, 'w', encoding='utf-8') as f:
            f.write(template)
        log_message("Created template LinkedIn_Posts.md")
    except Exception as e:
        log_message(f"Failed to create template: {e}", "ERROR")


def update_post_status(content_to_find, new_status, posted_time=None):
    """
    Update a post's status in the LinkedIn_Posts.md file

    Args:
        content_to_find: Content of the post to update
        new_status: New status (e.g., 'posted')
        posted_time: Timestamp when posted
    """
    try:
        with open(LINKEDIN_POSTS_FILE, 'r', encoding='utf-8') as f:
            file_content = f.read()

        # Find the post section containing this content
        # Replace Status: pending with Status: posted
        pattern = r'(## Post \d+\s*\nStatus:\s*)pending(\s*\nScheduled:.*?\nContent:\s*\n' + re.escape(content_to_find[:50]) + ')'

        replacement = r'\1posted\2'
        if posted_time:
            replacement += f'\nPosted: {posted_time}'

        updated_content = re.sub(pattern, replacement, file_content, count=1, flags=re.DOTALL)

        with open(LINKEDIN_POSTS_FILE, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        log_message("Updated post status to 'posted'")

    except Exception as e:
        log_message(f"Failed to update post status: {e}", "ERROR")


def archive_posted_content(content, posted_time):
    """
    Archive posted content to Done/ directory

    Args:
        content: The posted content
        posted_time: When it was posted
    """
    try:
        date_str = datetime.now().strftime('%Y-%m-%d')
        archive_file = DONE_DIR / f"LinkedIn_Posted_{date_str}.md"

        # Create or append to archive file
        mode = 'a' if archive_file.exists() else 'w'
        with open(archive_file, mode, encoding='utf-8') as f:
            if mode == 'w':
                f.write(f"# LinkedIn Posts - {date_str}\n\n")

            f.write(f"## Posted at {posted_time}\n\n")
            f.write(f"{content}\n\n")
            f.write("---\n\n")

        log_message(f"Archived post to {archive_file.name}")

    except Exception as e:
        log_message(f"Failed to archive post: {e}", "ERROR")


def count_posts_today():
    """
    Count how many posts were made today

    Returns:
        Number of posts made today
    """
    try:
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = LOGS_DIR / f"linkedin_{date_str}.md"

        if not log_file.exists():
            return 0

        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Count "Successfully posted" messages
        return content.count("Successfully posted to LinkedIn")

    except Exception as e:
        log_message(f"Error counting today's posts: {e}", "WARNING")
        return 0


def login_to_linkedin(page, headless=False):
    """
    Login to LinkedIn and save session

    Args:
        page: Playwright page object
        headless: Whether running in headless mode

    Returns:
        True if login successful, False otherwise
    """
    try:
        log_message("Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/login', wait_until='load', timeout=60000)

        # Check if already logged in
        if 'feed' in page.url or 'mynetwork' in page.url:
            log_message("Already logged in!")
            return True

        # Fill login form
        log_message("Filling login credentials...")
        page.fill('input[id="username"]', LINKEDIN_EMAIL)
        page.fill('input[id="password"]', LINKEDIN_PASSWORD)

        # Click sign in
        page.click('button[type="submit"]')
        log_message("Submitted login form, waiting for navigation...")

        # Wait for navigation (with timeout)
        try:
            page.wait_for_url('**/feed/**', timeout=30000)
            log_message("Login successful!")
            return True
        except PlaywrightTimeout:
            # Check if we're on a verification page
            if 'checkpoint' in page.url or 'challenge' in page.url:
                log_message("LinkedIn requires verification!", "WARNING")
                log_message("Please complete verification in the browser window", "WARNING")

                if not headless:
                    log_message("Waiting 60 seconds for manual verification...", "WARNING")
                    time.sleep(60)

                    # Check if verification was completed
                    if 'feed' in page.url:
                        log_message("Verification completed!")
                        return True

                log_message("Verification not completed", "ERROR")
                return False
            else:
                log_message(f"Login timeout. Current URL: {page.url}", "ERROR")
                return False

    except Exception as e:
        log_message(f"Login error: {e}", "ERROR")
        return False


def post_to_linkedin(page, content):
    """
    Create a new LinkedIn post

    Args:
        page: Playwright page object
        content: Post content

    Returns:
        True if post successful, False otherwise
    """
    try:
        log_message("Navigating to LinkedIn feed...")
        # Increased timeout to 60 seconds and using 'load' instead of 'networkidle'
        page.goto('https://www.linkedin.com/feed/', wait_until='load', timeout=60000)

        # Wait a bit for page to stabilize
        time.sleep(5)

        # Take screenshot for debugging
        screenshot_path = VAULT_PATH / 'linkedin_feed_debug.png'
        page.screenshot(path=str(screenshot_path))
        log_message(f"Screenshot saved to {screenshot_path}")

        # Debug: List all buttons
        try:
            buttons = page.query_selector_all('button')
            log_message(f"Found {len(buttons)} buttons on page")
            for i, btn in enumerate(buttons[:15]):  # First 15 buttons
                try:
                    text = btn.inner_text()[:50] if btn.inner_text() else ""
                    aria_label = btn.get_attribute('aria-label') or ""
                    class_name = btn.get_attribute('class') or ""
                    if text or aria_label:
                        log_message(f"Button {i}: text='{text}', aria='{aria_label}', class='{class_name[:50]}'")
                except:
                    pass
        except Exception as e:
            log_message(f"Debug error: {e}", "WARNING")

        # Click "Start a post" - LinkedIn uses a share box
        log_message("Opening post composer...")

        # Try specific selectors for the share box (most specific first)
        selectors = [
            'div.share-box-feed-entry__trigger',  # Main share box
            'button.share-box-feed-entry__trigger',  # Button variant
            'div.share-creation-state__text-editor',  # Direct editor
            'div[data-test-share-box-trigger]',  # Data attribute
            '.share-box__trigger',  # Alternative
            'div.artdeco-hoverable-trigger--content',  # Hoverable content
            'div[aria-label*="Start"]',  # Div with Start in aria-label
            'input[placeholder*="Start"]',  # Input placeholder
        ]

        clicked = False
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=2000):
                    element.click(timeout=5000)
                    clicked = True
                    log_message(f"Clicked share box using: {selector}")
                    time.sleep(2)  # Wait for modal to open
                    break
            except:
                continue

        if not clicked:
            raise Exception("Could not find share box trigger")

        # Wait for editor - try multiple selectors
        log_message("Waiting for post editor...")
        editor_selectors = [
            '.ql-editor',  # Quill editor
            'div[contenteditable="true"]',  # Any contenteditable div
            'div[role="textbox"]',  # Textbox role
        ]

        editor_found = False
        for editor_sel in editor_selectors:
            try:
                page.wait_for_selector(editor_sel, timeout=5000)
                log_message(f"Found editor using: {editor_sel}")

                # Type content
                log_message("Typing post content...")
                page.fill(editor_sel, content)
                time.sleep(2)

                editor_found = True
                break  # Exit loop after successfully typing
            except:
                continue

        if not editor_found:
            raise Exception("Could not find post editor after clicking share box")

        # Click Post button - try multiple selectors
        log_message("Looking for Post button...")
        post_button_selectors = [
            'button[aria-label*="Post"]',  # Button with "Post" in aria-label
            'button.share-actions__primary-action',  # Primary action button
            'button[data-test-share-box-post-button]',  # Data attribute
            'button:has-text("Post")',  # English text
            'button.artdeco-button--primary',  # Primary button class
            'button[type="submit"]',  # Submit button
        ]

        posted = False
        for btn_sel in post_button_selectors:
            try:
                page.click(btn_sel, timeout=5000)
                log_message(f"Clicked Post button using: {btn_sel}")
                posted = True
                break
            except:
                continue

        if not posted:
            raise Exception("Could not find Post button")

        time.sleep(3)
        log_message("Post published successfully!")
        return True

    except Exception as e:
        log_message(f"Error posting to LinkedIn: {e}", "ERROR")
        return False


def main():
    """
    Main function - runs continuous LinkedIn posting loop
    """
    log_message("=" * 60)
    log_message("LinkedIn Poster Starting")
    log_message(f"Vault Path: {VAULT_PATH}")
    log_message(f"Check Interval: {CHECK_INTERVAL} seconds (30 minutes)")
    log_message(f"Max Posts Per Day: {MAX_POSTS_PER_DAY}")
    log_message("=" * 60)

    # Validate credentials
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        log_message("ERROR: LinkedIn credentials not found in .env", "ERROR")
        log_message("Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD", "ERROR")
        return

    check_count = 0

    try:
        with sync_playwright() as p:
            # Launch browser with persistent context (saves session)
            log_message("Launching browser...")

            # First run: not headless to allow manual verification
            # Subsequent runs: headless
            headless = SESSION_DIR.exists() and len(list(SESSION_DIR.glob('*'))) > 0

            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(SESSION_DIR),
                headless=headless,
                args=['--no-sandbox']
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            # Login once at startup
            log_message("Attempting LinkedIn login...")
            if not login_to_linkedin(page, headless):
                log_message("Failed to login to LinkedIn", "ERROR")
                browser.close()
                return

            log_message("Starting monitoring loop...")

            while True:
                check_count += 1
                log_message(f"Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Check rate limit
                posts_today = count_posts_today()
                if posts_today >= MAX_POSTS_PER_DAY:
                    log_message(f"Rate limit reached: {posts_today}/{MAX_POSTS_PER_DAY} posts today")
                    log_message(f"Waiting until next check...")
                    time.sleep(CHECK_INTERVAL)
                    continue

                # Parse posts file
                pending_posts = parse_posts_file()
                log_message(f"Found {len(pending_posts)} pending post(s)")

                # Check for posts ready to publish
                now = datetime.now()
                for post in pending_posts:
                    if post['scheduled'] <= now:
                        log_message(f"Post scheduled for {post['scheduled']} is ready!")
                        log_message(f"Content preview: {post['content'][:50]}...")

                        # Check rate limit again
                        if count_posts_today() >= MAX_POSTS_PER_DAY:
                            log_message("Rate limit reached, skipping remaining posts")
                            break

                        # Post to LinkedIn
                        if post_to_linkedin(page, post['content']):
                            posted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            # Update status
                            update_post_status(post['content'], 'posted', posted_time)

                            # Archive
                            archive_posted_content(post['content'], posted_time)

                            log_message("Successfully posted to LinkedIn")

                            # Wait between posts
                            time.sleep(10)
                        else:
                            log_message("Failed to post, will retry next cycle", "WARNING")

                # Wait before next check
                log_message(f"Waiting {CHECK_INTERVAL} seconds until next check...")
                time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_message("\nReceived interrupt signal - shutting down gracefully...")
        log_message("LinkedIn Poster stopped")
    except Exception as e:
        log_message(f"Unexpected error in main loop: {e}", "ERROR")
        raise


if __name__ == "__main__":
    main()
