#!/usr/bin/env python3
"""
Quick Approve Script - Python version
Move files from Pending_Approval to Approved with preview
"""

import sys
from pathlib import Path
from datetime import datetime

# Configuration
VAULT_PATH = Path.cwd()
PENDING_DIR = VAULT_PATH / 'Pending_Approval'
APPROVED_DIR = VAULT_PATH / 'Approved'

# Colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'


def print_color(text, color):
    """Print colored text"""
    print(f"{color}{text}{NC}")


def list_pending_files():
    """List all pending approval files"""
    files = list(PENDING_DIR.glob('*.md'))
    if not files:
        print("  (none)")
        return []

    for f in files:
        print(f"  {f.name}")
    return files


def preview_file(filepath):
    """Show preview of file content"""
    print_color("\nPreview of file to approve:", YELLOW)
    print("=" * 50)

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]
            print(''.join(lines))
    except Exception as e:
        print_color(f"Error reading file: {e}", RED)
        return False

    print("=" * 50)
    return True


def approve_file(filename):
    """Approve a file by moving it to Approved/"""
    pending_file = PENDING_DIR / filename
    approved_file = APPROVED_DIR / filename

    # Check if file exists
    if not pending_file.exists():
        print_color(f"Error: File not found: {pending_file}", RED)
        print("\nAvailable files:")
        list_pending_files()
        return False

    # Show preview
    if not preview_file(pending_file):
        return False

    # Confirm approval
    print()
    response = input("Approve this file? (y/n): ").strip().lower()

    if response != 'y':
        print_color("Approval cancelled", YELLOW)
        return False

    # Move file
    try:
        pending_file.rename(approved_file)
        print_color(f"\n✅ Approved: {filename}", GREEN)
        print(f"File moved to: Approved/")
        print("Will be processed within 30 seconds by orchestrator")
        print()
        print("Monitor execution:")
        print(f"  tail -f Logs/orchestrator_{datetime.now().strftime('%Y-%m-%d')}.md")
        return True
    except Exception as e:
        print_color(f"Error moving file: {e}", RED)
        return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print_color("Usage: python quick_approve.py <filename>", YELLOW)
        print("\nAvailable files in Pending_Approval/:")
        list_pending_files()
        sys.exit(1)

    filename = sys.argv[1]

    # Ensure directories exist
    if not PENDING_DIR.exists():
        print_color("Error: Pending_Approval/ directory not found", RED)
        sys.exit(1)

    if not APPROVED_DIR.exists():
        APPROVED_DIR.mkdir(exist_ok=True)

    # Approve the file
    success = approve_file(filename)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
