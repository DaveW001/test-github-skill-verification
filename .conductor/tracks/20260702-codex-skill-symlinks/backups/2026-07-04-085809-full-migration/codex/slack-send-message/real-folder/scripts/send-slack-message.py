#!/usr/bin/env python3
"""
Slack message + file sender (reference implementation).

Based on conductor-reporter/src/slack_sender.py, augmented with upstream
best practices (rate-limit handling, token security, the new file upload API).

Usage:
    python send-slack-message.py --text "Hello!"
    python send-slack-message.py --text "Report ready" --file report.md
    python send-slack-message.py --test

Environment (from .env or environment variables):
    SLACK_BOT_TOKEN  - Bot token (xoxb-...)
    SLACK_USER_ID    - Target user ID for DM (U...)
"""

import os
import sys
import time
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://slack.com/api"


class SlackSender:
    """Send messages and files to Slack via the Web API."""

    def __init__(self, token: str = None, user_id: str = None):
        self.token = token or os.environ.get("SLACK_BOT_TOKEN", "")
        self.user_id = user_id or os.environ.get("SLACK_USER_ID", "")
        if not self.token:
            raise ValueError("SLACK_BOT_TOKEN not set. Check .env or environment.")

    def _headers(self, content_type="application/json"):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": content_type,
        }

    def _handle_response(self, response: requests.Response):
        """Handle Slack's always-200 pattern + rate limiting."""
        # Rate limit: HTTP 429 with Retry-After header
        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", 60))
            print(f"  [RATE LIMIT] Waiting {wait}s (Retry-After header)...")
            time.sleep(wait)
            return None  # Caller should retry

        data = response.json()

        # Slack returns HTTP 200 even on failure - check the body
        if not data.get("ok"):
            error = data.get("error", "Unknown error")
            print(f"  [ERROR] Slack API error: {error}")
            return None

        return data

    def test_connection(self) -> bool:
        """Verify the token is valid."""
        try:
            response = requests.get(
                f"{API_BASE}/auth.test",
                headers=self._headers(),
                timeout=10,
            )
            data = self._handle_response(response)
            if data:
                print(f"  [OK] Connected as: {data.get('user', 'Unknown')}")
                print(f"       Team: {data.get('team', 'Unknown')}")
                return True
            return False
        except requests.RequestException as e:
            print(f"  [ERROR] Connection failed: {e}")
            return False

    def send_message(self, text: str, channel: str = None, thread_ts: str = None,
                     unfurl_links: bool = False, link_names: bool = True,
                     retry: bool = True) -> dict:
        """
        Send a message to a channel or DM.

        Returns the API response dict (contains 'ts' and 'channel').
        """
        target = channel or self.user_id

        payload = {
            "channel": target,
            "text": text,
            "unfurl_links": unfurl_links,
            "link_names": link_names,
        }
        if thread_ts:
            payload["thread_ts"] = thread_ts

        try:
            response = requests.post(
                f"{API_BASE}/chat.postMessage",
                headers=self._headers(),
                json=payload,
                timeout=30,
            )

            # Handle rate limit with retry
            if response.status_code == 429 and retry:
                self._handle_response(response)  # Sleeps per Retry-After
                return self.send_message(text, target, thread_ts,
                                        unfurl_links, link_names, retry=False)

            data = self._handle_response(response)
            if data:
                print(f"  [OK] Message sent (ts: {data.get('ts')})")
                return data
            return {}

        except requests.RequestException as e:
            print(f"  [ERROR] Failed to send: {e}")
            return {}

    def get_dm_channel_id(self, user_id: str = None) -> str:
        """
        Resolve a user ID (U...) to a DM channel ID (D...).
        Required for file uploads.
        """
        target = user_id or self.user_id
        try:
            response = requests.post(
                f"{API_BASE}/conversations.open",
                headers=self._headers(),
                json={"users": target},
                timeout=10,
            )
            data = self._handle_response(response)
            if data:
                return data.get("channel", {}).get("id", "")
            return ""
        except requests.RequestException:
            return ""

    def upload_file(self, file_path: str, channel: str = None,
                    title: str = None, initial_comment: str = None) -> bool:
        """
        Upload a file using the new 3-step API.

        Slack deprecated files.upload (sunset Nov 2025). This uses:
        1. files.getUploadURLExternal - get upload URL + file_id
        2. POST file to upload URL
        3. files.completeUploadExternal - finalize + share to channel
        """
        if not os.path.exists(file_path):
            print(f"  [ERROR] File not found: {file_path}")
            return False

        filename = title or os.path.basename(file_path)

        with open(file_path, "rb") as f:
            file_content = f.read()
        file_size = len(file_content)

        # Step 1: Get upload URL
        try:
            response = requests.post(
                f"{API_BASE}/files.getUploadURLExternal",
                headers=self._headers("application/x-www-form-urlencoded"),
                data={"filename": filename, "length": file_size},
                timeout=30,
            )
            result = self._handle_response(response)
            if not result:
                return False

            upload_url = result["upload_url"]
            file_id = result["file_id"]
        except (requests.RequestException, KeyError) as e:
            print(f"  [ERROR] Failed to get upload URL: {e}")
            return False

        # Step 2: Upload file to URL
        try:
            response = requests.post(
                upload_url,
                files={"file": (filename, file_content, "text/markdown")},
                timeout=60,
            )
            if response.status_code != 200:
                print(f"  [ERROR] Upload failed: HTTP {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"  [ERROR] Upload failed: {e}")
            return False

        # Step 3: Complete upload
        dm_channel = channel or self.get_dm_channel_id()
        complete_data = {"files": [{"id": file_id, "title": filename}]}

        if dm_channel:
            complete_data["channel_id"] = dm_channel
        if initial_comment:
            complete_data["initial_comment"] = initial_comment

        try:
            response = requests.post(
                f"{API_BASE}/files.completeUploadExternal",
                headers=self._headers(),
                json=complete_data,
                timeout=30,
            )
            data = self._handle_response(response)
            if data:
                print(f"  [OK] File uploaded: {filename}")
                return True
            return False
        except requests.RequestException as e:
            print(f"  [ERROR] Complete upload failed: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Send Slack messages and files")
    parser.add_argument("--text", help="Message text to send")
    parser.add_argument("--file", help="File path to upload")
    parser.add_argument("--channel", help="Channel ID (default: SLACK_USER_ID DM)")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--thread", help="Thread timestamp to reply in")
    args = parser.parse_args()

    sender = SlackSender()

    if args.test:
        print("Testing Slack connection...")
        sender.test_connection()
        return

    if args.text:
        print("Sending message...")
        sender.send_message(args.text, channel=args.channel, thread_ts=args.thread)

    if args.file:
        print(f"Uploading file: {args.file}")
        comment = args.text if args.text else None
        sender.upload_file(args.file, channel=args.channel, initial_comment=comment)

    if not args.text and not args.file and not args.test:
        parser.print_help()


if __name__ == "__main__":
    main()