#!/usr/bin/env python3
"""Analyze Gmail export messages and generate a draft extraction register.

Scans the export, identifies messages with extractable KB entity content,
and produces a draft register with recommended target paths.
"""

import argparse
import re
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Gmail export markdown file")
    parser.add_argument("--priority-csv", required=True, help="Pre-triage CSV")
    parser.add_argument("--output", required=True, help="Output extraction register markdown")
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
        messages[msg_no] = {
            "subject": subject,
            "from": from_addr,
            "body": body,
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


def analyze_message(msg_no, msg):
    """Analyze a message and return (decision, target_path, entities, notes)."""
    subject = msg["subject"].lower()
    body = msg["body"].lower()
    full_text = subject + " " + body
    from_addr = msg["from"].lower()

    # Skip patterns - these are calendar/meeting logistics with no extractable entities
    skip_patterns = [
        "invitation:", "updated invitation:", "accepted:", "declined:",
        "tentative:", "new event:", "new time:", "proposed new time:",
        "canceled event:", "event has been",
    ]
    for pattern in skip_patterns:
        if pattern in msg["subject"].lower():
            return ("no-new-entity", "—", "Calendar/meeting logistics", "Scheduling email — no extractable entity content")

    # High-value patterns
    # Workshop agendas, leadership discussions
    if "workshop agenda" in full_text or "leadership workshop" in full_text:
        return ("update", "knowledge-base/events/event-c2-pae-leadership-workshop.md",
                "Workshop agenda", "Contains workshop planning content")

    # Transformation questions/observations
    if "transformation" in full_text and ("question" in full_text or "observation" in full_text):
        return ("update", "knowledge-base/programs/program-c2-cc2-pae.md",
                "PAE Transformation", "Transformation questions/observations")

    # Why statement, north star, comms strategy
    if "why statement" in full_text:
        return ("create", "knowledge-base/concepts/concept-c2-cc2-why-statement.md",
                "C2/CC2 Why Statement", "Program foundational document")

    if "comms strategy" in full_text:
        return ("update", "knowledge-base/programs/program-c2-cc2-pae.md",
                "Comms Strategy", "Communication planning for C2/CC2")

    if "5g experiment" in full_text or "5g problem" in full_text:
        return ("update", "knowledge-base/programs/program-c2-cc2-5g-experiment.md",
                "5G Experiment", "C2/CC2 5G experiment planning")

    # Interview-related content
    if "interview" in full_text and ("result" in full_text or "analysis" in full_text or "storyboard" in full_text):
        return ("update", "knowledge-base/events/event-c2-cc2-interviews.md",
                "Interview analysis", "Interview results/analysis planning")

    # Product mapping
    if "product mapping" in full_text:
        return ("update", "knowledge-base/programs/program-c2-cc2-pae.md",
                "Product Mapping", "Product mapping workshop prep")

    # ASALT
    if "asalt" in full_text:
        return ("update", "knowledge-base/organizations/org-asalt.md",
                "ASALT", "ASALT transformation planning")

    # WAS Transformation
    if "was transformation" in full_text:
        return ("update", "knowledge-base/programs/program-was-transformation.md",
                "WAS Transformation", "WAS transformation observations")

    # Team alignment / working session
    if "team alignment" in full_text or "working session" in full_text:
        return ("update", "knowledge-base/programs/program-c2-cc2-pae.md",
                "Team Alignment", "Team alignment session content")

    # Sprint review / refinement
    if "sprint review" in full_text or "refinement" in full_text:
        return ("update", "knowledge-base/programs/program-c2-cc2-pae.md",
                "Sprint Review", "Sprint review/refinement planning")

    # Clearances / CACs
    if "clearance" in full_text or "cac" in full_text:
        return ("update", "knowledge-base/concepts/concept-security-clearances.md",
                "Security Clearances", "Clearance/CAC coordination")

    # Task order introduction
    if "task order" in full_text:
        return ("update", "knowledge-base/programs/program-c2-cc2-pae.md",
                "Task Order", "Task order introduction/workshop")

    # Walk through
    if "walk through" in full_text:
        return ("update", "knowledge-base/programs/program-c2-cc2-pae.md",
                "Walk Through", "C2 walk-through planning")

    # Open work / next steps
    if "open work" in full_text or "next steps" in full_text:
        return ("update", "knowledge-base/programs/program-c2-cc2-pae.md",
                "Open Work", "Open work sync and next steps")

    # Schedule weeks
    if "schedule weeks" in full_text:
        return ("update", "knowledge-base/programs/program-c2-cc2-pae.md",
                "Schedule Planning", "Weeks 2-6 schedule discussion")

    # Dave and Tim sync
    if "dave and tim sync" in full_text:
        return ("no-new-entity", "—", "1:1 sync", "Internal sync meeting — no extractable entity content")

    # OOO (out of office)
    if "ooo" in full_text:
        return ("no-new-entity", "—", "OOO notification", "Out of office notification — no extractable entity content")

    # Quick connect / debrief
    if "quick connect" in full_text or "debrief" in full_text:
        return ("no-new-entity", "—", "Quick connect/debrief", "Meeting logistics — no extractable entity content")

    # PAE interview
    if "pae interview" in full_text:
        return ("update", "knowledge-base/events/event-c2-cc2-interviews.md",
                "PAE Interview", "PAE interview reference")

    # Week 3 workshops revised proposal
    if "week 3 workshops revised proposal" in full_text:
        return ("update", "knowledge-base/events/event-c2-pae-leadership-workshop.md",
                "Workshop Proposal", "Revised workshop proposal")

    # Default: no new entity for remaining INGEST-CANDIDATE messages
    return ("no-new-entity", "—", "Meeting logistics", "No extractable entity content beyond scheduling")


def main():
    args = parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    messages = parse_sections(content)

    # Load priority CSV to get INGEST-CANDIDATE and REVIEW messages
    import csv
    ingest_messages = []
    with open(args.priority_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Classification"] in ("INGEST-CANDIDATE", "REVIEW"):
                msg_no = int(row["MessageNo"])
                if msg_no in messages:
                    ingest_messages.append((msg_no, messages[msg_no], row["Classification"]))

    ingest_messages.sort(key=lambda x: x[0])

    # Analyze each message
    register_rows = []
    for msg_no, msg, classification in ingest_messages:
        decision, target_path, entities, notes = analyze_message(msg_no, msg)
        register_rows.append({
            "message_no": msg_no,
            "subject": msg["subject"],
            "from": msg["from"],
            "classification": classification,
            "decision": decision,
            "target_path": target_path,
            "entities": entities,
            "notes": notes,
        })

    # Write register
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("# Extraction Register — Gmail High-Signal Ingestion\n\n")
        f.write(f"Source: `C:\\development\\02-Kx-to-process\\60 archive\\2026-05-03\\gmail_export_90days.md`\n\n")
        f.write(f"Total messages analyzed: {len(register_rows)}\n\n")

        # Summary counts
        create_count = sum(1 for r in register_rows if r["decision"] == "create")
        update_count = sum(1 for r in register_rows if r["decision"] == "update")
        no_entity_count = sum(1 for r in register_rows if r["decision"] == "no-new-entity")
        f.write(f"| Decision | Count |\n|----------|-------|\n")
        f.write(f"| create | {create_count} |\n")
        f.write(f"| update | {update_count} |\n")
        f.write(f"| no-new-entity | {no_entity_count} |\n\n")

        f.write("Only process rows marked `create` or `update`. Use `email-ingestion-rules.md` before recommending any create/update.\n\n")
        f.write("| MessageNo | Subject | From | Classification | Entities Detected | Decision | Exact Target File Path | Evidence / Notes |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")

        for row in register_rows:
            subject = row["subject"][:50] + ("..." if len(row["subject"]) > 50 else "")
            from_short = row["from"][:35]
            f.write(f"| {row['message_no']} | {subject} | {from_short} | {row['classification']} | {row['entities']} | {row['decision']} | {row['target_path']} | {row['notes']} |\n")

    print(f"Extraction register written to {args.output}")
    print(f"Total analyzed: {len(register_rows)}")
    print(f"  create: {create_count}")
    print(f"  update: {update_count}")
    print(f"  no-new-entity: {no_entity_count}")


if __name__ == "__main__":
    main()
