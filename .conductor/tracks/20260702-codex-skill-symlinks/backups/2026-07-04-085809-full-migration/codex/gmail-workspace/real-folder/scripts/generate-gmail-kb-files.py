#!/usr/bin/env python3
"""Generate KB entity files from the Gmail extraction register and export.

Reads the extraction register, groups messages by target file, extracts
relevant content, and creates KB entity files with YAML front matter.
"""

import argparse
import csv
import re
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Gmail export markdown file")
    parser.add_argument("--register", required=True, help="Extraction register markdown")
    parser.add_argument("--source-id", default="source-gmail-high-signal-ingestion", help="Source note ID")
    return parser.parse_args()


def parse_sections(content):
    sections = re.split(r'\n(?=## \d+\. )', content)
    messages = {}
    for section in sections:
        section = section.strip()
        if not section.startswith("## "):
            continue
        header_match = re.match(r'^## (\d+)\.\s+(.*)$', section.split('\n')[0])
        if not header_match:
            continue
        msg_no = int(header_match.group(1))
        subject = header_match.group(2).strip()
        body = extract_body(section)
        from_addr = extract_table_field(section, "From")
        date = extract_table_field(section, "InternalDate")
        messages[msg_no] = {
            "subject": subject,
            "from": from_addr,
            "body": body,
            "date": date,
        }
    return messages


def extract_table_field(section, field_name):
    pattern = rf'\|\s*{re.escape(field_name)}\s*\|\s*`?([^`\n]*)`?\s*\|'
    match = re.search(pattern, section)
    return match.group(1).strip() if match else ""


def extract_body(section):
    lines = section.split('\n')
    body_start = None
    in_table = False
    for i, line in enumerate(lines):
        if line.startswith('| Field | Value |'):
            in_table = True
            continue
        if in_table and line.startswith('|---|---|'):
            continue
        if in_table and line.startswith('|'):
            continue
        if in_table and line.strip() == '':
            body_start = i + 1
            break
    if body_start is None:
        return ""
    body_lines = []
    for line in lines[body_start:]:
        if line.strip() == '---':
            break
        body_lines.append(line)
    return '\n'.join(body_lines).strip()


def parse_register(register_path):
    """Parse extraction register and group by target file."""
    groups = {}
    with open(register_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("| ") or "MessageNo" in line or "---" in line:
                continue
            parts = [p.strip() for p in line.strip().split("|") if p.strip()]
            if len(parts) < 8:
                continue
            msg_no = parts[0]
            subject = parts[1]
            from_addr = parts[2]
            classification = parts[3]
            entities = parts[4]
            decision = parts[5]
            target_path = parts[6]
            notes = parts[7] if len(parts) > 7 else ""

            if decision not in ("create", "update"):
                continue
            if target_path not in groups:
                groups[target_path] = []
            groups[target_path].append({
                "msg_no": msg_no,
                "subject": subject,
                "from": from_addr,
                "classification": classification,
                "entities": entities,
                "notes": notes,
            })
    return groups


def sanitize_body(body):
    """Clean up message body for KB inclusion."""
    # Remove Google Docs footer info
    body = re.sub(r'Google LLC, 1600 Amphitheatre Parkway.*', '', body, flags=re.DOTALL)
    body = re.sub(r'You have received this email because.*', '', body, flags=re.DOTALL)
    body = re.sub(r'Change what Google sends you.*', '', body, flags=re.DOTALL)
    body = re.sub(r'You can reply to this email.*', '', body, flags=re.DOTALL)
    # Remove long URLs
    body = re.sub(r'https?://[^\s]{60,}', '[link]', body)
    # Collapse multiple newlines
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body.strip()


def generate_kb_file(target_path, messages, source_id, export_messages):
    """Generate a KB entity file."""
    # Determine entity type and name from path
    path_parts = target_path.replace("knowledge-base/", "").split("/")
    entity_type = path_parts[0]  # people, organizations, programs, events, concepts, etc.
    filename = path_parts[-1].replace(".md", "")

    # Generate display name from filename
    name = filename.replace(entity_type + "-", "").replace("-", " ").title()

    # Build content
    lines = []
    lines.append("---")
    lines.append(f"id: {filename}")
    lines.append(f"type: {entity_type.rstrip('s')}")  # programs -> program
    lines.append(f"name: {name}")
    lines.append(f"created: 2026-05-03")
    lines.append(f"source: [[{source_id}]]")
    lines.append(f"status: draft")
    lines.append(f"message_count: {len(messages)}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {name}")
    lines.append("")
    lines.append(f"> Extracted from {len(messages)} Gmail messages (dave.witkin@scruminc.com, Feb-May 2026).")
    lines.append("")

    # Add content from messages
    for msg_info in messages:
        msg_no = msg_info["msg_no"]
        if msg_no.isdigit() and int(msg_no) in export_messages:
            msg = export_messages[int(msg_no)]
            body = sanitize_body(msg["body"])
            if len(body) > 50:  # Only include messages with substantive content
                lines.append(f"## From: {msg_info['subject']}")
                lines.append(f"*{msg['from']} — {msg['date']}*")
                lines.append("")
                # Limit body to first 500 chars
                body_excerpt = body[:500] + ("..." if len(body) > 500 else "")
                lines.append(body_excerpt)
                lines.append("")

    return "\n".join(lines)


def main():
    args = parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    export_messages = parse_sections(content)
    groups = parse_register(args.register)

    print(f"Found {len(groups)} target files to create/update")

    for target_path, messages in sorted(groups.items()):
        full_path = Path(f"C:\\development\\02-Kx-to-process\\{target_path}")
        full_path.parent.mkdir(parents=True, exist_ok=True)

        kb_content = generate_kb_file(target_path, messages, args.source_id, export_messages)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(kb_content)

        print(f"  Created: {target_path} ({len(messages)} messages)")

    print(f"\nTotal KB files created: {len(groups)}")


if __name__ == "__main__":
    main()
