#!/usr/bin/env python3
"""Export Gmail messages for a date window into a deterministic markdown file.

Read-only scope. No mailbox mutation.

Usage:
    python export-gmail-window.py \\
        --account dave.witkin@scruminc.com \\
        --start-date 2026-02-01 \\
        --end-date-exclusive 2026-05-01 \\
        --output "60 archive/2026-05-03/gmail_export_90days.md" \\
        --manifest .conductor/tracks/gmail-high-signal-ingestion/gmail-export-manifest.md \\
        --credentials /path/to/credentials.json \\
        --token /path/to/token.json \\
        [--max-results 5] [--dry-run]
"""

import argparse
import base64
import os
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# HTML stripping
from bs4 import BeautifulSoup

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export Gmail messages for a date window into markdown."
    )
    parser.add_argument("--account", required=True, help="Gmail account email")
    parser.add_argument("--start-date", required=True, help="Start date (ISO format, e.g. 2026-02-01)")
    parser.add_argument("--end-date-exclusive", required=True, help="End date exclusive (ISO format)")
    parser.add_argument("--output", required=True, help="Path to output markdown file")
    parser.add_argument("--manifest", required=True, help="Path to output manifest file")
    parser.add_argument("--credentials", required=True, help="Path to OAuth client_secret JSON")
    parser.add_argument("--token", required=True, help="Path to OAuth token JSON (created on first run)")
    parser.add_argument("--max-results", type=int, default=None, help="Limit number of messages exported")
    parser.add_argument("--dry-run", action="store_true", help="Authenticate and count only; do not write export file")
    return parser.parse_args()


def authenticate(credentials_path, token_path):
    """OAuth 2.0 flow — read-only scope."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())
    return creds


def query_messages(service, account, start_date_str, end_date_exclusive_str, max_results):
    """List message IDs with date filter and pagination."""
    start_dt = datetime.fromisoformat(start_date_str).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(end_date_exclusive_str).replace(tzinfo=timezone.utc)
    start_epoch = int(start_dt.timestamp())
    end_epoch = int(end_dt.timestamp())
    query = f"after:{start_epoch} before:{end_epoch}"

    messages = []
    page_token = None
    while True:
        batch_size = min(500, max_results - len(messages)) if max_results else 500
        results = service.users().messages().list(
            userId=account,
            q=query,
            maxResults=batch_size,
            pageToken=page_token,
        ).execute()
        batch = results.get("messages", [])
        messages.extend(batch)
        page_token = results.get("nextPageToken")
        if not page_token or (max_results and len(messages) >= max_results):
            break

    if max_results and len(messages) > max_results:
        messages = messages[:max_results]

    return messages


def fetch_message_detail(service, account, message_id):
    """Fetch full message detail including headers and body parts."""
    return service.users().messages().get(
        userId=account,
        id=message_id,
        format="full",
    ).execute()


def extract_header(headers, name):
    """Extract a header value by name (case-insensitive)."""
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def strip_html(html_text):
    """Convert HTML email body to plain text."""
    soup = BeautifulSoup(html_text, "lxml")
    return soup.get_text(separator="\n", strip=True)


def extract_body(payload):
    """Extract plain text body from Gmail message payload."""
    if "parts" in payload:
        # Prefer text/plain
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                if data:
                    return base64.urlsafe_b64decode(data + "===").decode("utf-8", errors="replace")
        # Fall back to text/html
        for part in payload["parts"]:
            if part["mimeType"] == "text/html":
                data = part["body"].get("data", "")
                if data:
                    html = base64.urlsafe_b64decode(data + "===").decode("utf-8", errors="replace")
                    return strip_html(html)
    # Single-part message
    if payload.get("mimeType") == "text/plain":
        data = payload["body"].get("data", "")
        if data:
            return base64.urlsafe_b64decode(data + "===").decode("utf-8", errors="replace")
    if payload.get("mimeType") == "text/html":
        data = payload["body"].get("data", "")
        if data:
            html = base64.urlsafe_b64decode(data + "===").decode("utf-8", errors="replace")
            return strip_html(html)
    return "(no body)"


def format_internal_date(internal_date_str):
    """Convert Gmail internalDate (ms since epoch) to ISO 8601."""
    try:
        ts = int(internal_date_str) / 1000.0
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (ValueError, TypeError, OSError):
        return internal_date_str


def format_markdown_section(n, msg):
    """Format one message as a markdown section."""
    headers = msg["payload"].get("headers", [])
    subject = extract_header(headers, "Subject") or "(no subject)"
    from_addr = extract_header(headers, "From") or ""
    to_addr = extract_header(headers, "To") or ""
    cc_addr = extract_header(headers, "Cc") or ""
    date_str = extract_header(headers, "Date") or ""
    message_id = extract_header(headers, "Message-ID") or ""
    thread_id = msg.get("threadId", "")
    internal_date = format_internal_date(msg.get("internalDate", ""))
    labels = ", ".join(msg.get("labelIds", []))
    snippet = msg.get("snippet", "")
    body = extract_body(msg["payload"])

    lines = []
    lines.append(f"## {n}. {subject}")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|-------|-------|")
    lines.append(f"| MessageId | `{message_id}` |")
    lines.append(f"| ThreadId | `{thread_id}` |")
    lines.append(f"| InternalDate | `{internal_date}` |")
    lines.append(f"| From | `{from_addr}` |")
    if to_addr:
        lines.append(f"| To | `{to_addr}` |")
    if cc_addr:
        lines.append(f"| Cc | `{cc_addr}` |")
    lines.append(f"| Labels | `{labels}` |")
    lines.append(f"| Snippet | `{snippet}` |")
    lines.append("")
    lines.append(body)
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def write_manifest(manifest_path, account, start_date, end_date_exclusive,
                   output_path, message_count, dry_run, command):
    """Write a human-readable manifest file."""
    lines = []
    lines.append(f"Account: {account}")
    lines.append(f"StartDate: {start_date}")
    lines.append(f"EndDateExclusive: {end_date_exclusive}")
    lines.append(f"ExportPath: {output_path}")
    lines.append(f"Messages: {message_count}")
    lines.append(f"DryRun: {str(dry_run).lower()}")
    lines.append(f"ExportCommand: {command}")
    lines.append(f"GeneratedAt: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("")
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    args = parse_args()

    # Build the command string for the manifest
    command = " ".join(sys.argv)

    print(f"Authenticating as {args.account}...")
    creds = authenticate(args.credentials, args.token)
    service = build("gmail", "v1", credentials=creds)

    print(f"Querying messages: after {args.start_date}, before {args.end_date_exclusive}...")
    messages = query_messages(
        service, args.account, args.start_date, args.end_date_exclusive, args.max_results
    )
    total = len(messages)
    print(f"Found {total} messages.")

    if args.dry_run:
        print("Dry-run mode: writing manifest only, skipping export.")
        write_manifest(
            args.manifest, args.account, args.start_date, args.end_date_exclusive,
            args.output, total, True, command
        )
        print(f"Manifest written to {args.manifest}")
        return

    # Fetch full details and write markdown
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"# Gmail Export — {args.account}\n\n")
        f.write(f"**Window:** {args.start_date} through {args.end_date_exclusive} exclusive\n")
        f.write(f"**Total messages:** {total}\n\n")
        f.write("---\n\n")

        for i, msg_info in enumerate(messages, 1):
            if i % 50 == 0:
                print(f"  Exporting message {i}/{total}...")
            try:
                msg = fetch_message_detail(service, args.account, msg_info["id"])
                section = format_markdown_section(i, msg)
                f.write(section)
            except HttpError as e:
                print(f"  WARNING: Failed to fetch message {i} (id={msg_info['id']}): {e}")
                f.write(f"## {i}. (fetch error)\n\n(ERROR: {e})\n\n---\n\n")

    print(f"Export written to {args.output}")

    # Write manifest
    write_manifest(
        args.manifest, args.account, args.start_date, args.end_date_exclusive,
        args.output, total, False, command
    )
    print(f"Manifest written to {args.manifest}")


if __name__ == "__main__":
    main()
