#!/usr/bin/env python3
"""
File Watcher for AI Employee Vault
Monitors Inbox/ folder and creates tasks in Needs_Action/
"""

import os
import time
import json
from datetime import datetime
from pathlib import Path


class FileWatcher:
    def __init__(self, inbox_dir="Inbox", needs_action_dir="Needs_Action", logs_dir="Logs"):
        self.inbox_dir = Path(inbox_dir)
        self.needs_action_dir = Path(needs_action_dir)
        self.logs_dir = Path(logs_dir)
        self.processed_file = Path(".processed_files.json")
        self.processed_files = self.load_processed_files()

        # Ensure directories exist
        self.inbox_dir.mkdir(exist_ok=True)
        self.needs_action_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    def load_processed_files(self):
        """Load the list of already processed files"""
        if self.processed_file.exists():
            try:
                with open(self.processed_file, 'r') as f:
                    return set(json.load(f))
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Warning: Could not load processed files: {e}")
                return set()
        return set()

    def save_processed_files(self):
        """Save the list of processed files"""
        try:
            with open(self.processed_file, 'w') as f:
                json.dump(list(self.processed_files), f, indent=2)
        except IOError as e:
            print(f"❌ Error saving processed files: {e}")

    def detect_priority(self, filename):
        """Detect priority from filename keywords"""
        filename_upper = filename.upper()

        if "URGENT" in filename_upper or "CRITICAL" in filename_upper:
            return "high"
        elif "IMPORTANT" in filename_upper:
            return "medium"
        else:
            return "normal"

    def create_task(self, file_path):
        """Move file from Inbox to Needs_Action and create task metadata"""
        try:
            # Get file info
            filename = file_path.name
            priority = self.detect_priority(filename)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Move file to Needs_Action
            destination = self.needs_action_dir / filename

            # If file already exists in Needs_Action, add timestamp
            if destination.exists():
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{name_parts[1]}"
                else:
                    new_name = f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                destination = self.needs_action_dir / new_name

            # Move the file
            file_path.rename(destination)

            print(f"✅ Moved to Needs_Action: {destination.name}")
            print(f"   Priority: {priority}")

            # Log the action
            self.log_action(f"Moved {filename} to Needs_Action (priority: {priority})")

            return True

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def log_action(self, message):
        """Log an action to the daily log file"""
        try:
            log_date = datetime.now().strftime('%Y-%m-%d')
            log_file = self.logs_dir / f"file_watcher_{log_date}.md"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(log_file, 'a', encoding='utf-8') as f:
                if not log_file.exists() or log_file.stat().st_size == 0:
                    f.write(f"# File Watcher Log - {log_date}\n\n")
                f.write(f"[{timestamp}] {message}\n")

        except Exception as e:
            print(f"⚠️  Warning: Could not write to log: {e}")

    def watch(self, interval=10):
        """Watch the inbox folder for new files"""
        print(f"👀 Watching {self.inbox_dir} for new files...")
        print(f"📁 Tasks will be created in {self.needs_action_dir}")
        print(f"⏱️  Check interval: {interval} seconds")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                # Get all files in inbox
                inbox_files = list(self.inbox_dir.glob('*'))

                # Filter out directories and already processed files
                new_files = [
                    f for f in inbox_files
                    if f.is_file() and str(f) not in self.processed_files
                ]

                if new_files:
                    print(f"\n📥 Found {len(new_files)} new file(s)")

                    for file_path in new_files:
                        print(f"Processing: {file_path.name}")

                        # Create task
                        if self.create_task(file_path):
                            # Mark as processed
                            self.processed_files.add(str(file_path))
                            self.save_processed_files()

                # Wait before next check
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n👋 File watcher stopped")
            self.save_processed_files()


def main():
    """Main function"""
    watcher = FileWatcher()
    watcher.watch(interval=10)


if __name__ == "__main__":
    main()
