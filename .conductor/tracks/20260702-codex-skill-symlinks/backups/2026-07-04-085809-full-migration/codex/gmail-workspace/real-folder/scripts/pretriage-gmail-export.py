#!/usr/bin/env python3
"""Pre-triage a Gmail markdown export: classify, score, collapse threads, write queues.

Usage:
    python pretriage-gmail-export.py \
        --input gmail_export.md \
        --config pretriage-config.json \
        --output-csv pretriage-gmail.csv \
        --triage-md message-triage-auto.md \
        --priority-md priority-review-queue.md \
        --skip-sample-md skip-auto-sample.md \
        --thread-groups-md thread-groups.md \
        --summary-md pretriage-summary.md
"""

import argparse
import csv
import json
import math
import random
import re
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pre-triage a Gmail markdown export into classified review queues."
    )
    parser.add_argument("--input", required=True, help="Path to Gmail markdown export")
    parser.add_argument("--config", required=True, help="Path to pre-triage config JSON")
    parser.add_argument("--output-csv", required=True, help="Path to output CSV")
    parser.add_argument("--triage-md", required=True, help="Path to message-triage-auto.md")
    parser.add_argument("--priority-md", required=True, help="Path to priority-review-queue.md")
    parser.add_argument("--skip-sample-md", required=True, help="Path to skip-auto-sample.md")
    parser.add_argument("--thread-groups-md", required=True, help="Path to thread-groups.md")
    parser.add_argument("--summary-md", required=True, help="Path to pretriage-summary.md")
    return parser.parse_args()


def parse_sections(content):
    """Split markdown export into message sections."""
    sections = re.split(r'\n(?=## \d+\. )', content)
    # First element is header material; skip it
    messages = []
    for section in sections:
        section = section.strip()
        if not section.startswith("## "):
            continue
        msg = parse_section(section)
        if msg:
            messages.append(msg)
    return messages


def parse_section(section):
    """Parse one message section into a dict."""
    # Extract message number and subject from "## {n}. {subject}"
    header_match = re.match(r'^## (\d+)\.\s+(.*)$', section.split('\n')[0])
    if not header_match:
        return None

    msg_no = int(header_match.group(1))
    subject = header_match.group(2).strip()

    # Extract table fields
    message_id = extract_table_field(section, "MessageId")
    thread_id = extract_table_field(section, "ThreadId")
    internal_date = extract_table_field(section, "InternalDate")
    from_addr = extract_table_field(section, "From")
    to_addr = extract_table_field(section, "To")
    cc_addr = extract_table_field(section, "Cc")

    # Extract body: everything after the last table row until --- or end
    body = extract_body(section)

    return {
        "message_no": msg_no,
        "subject": subject,
        "message_id": message_id,
        "thread_id": thread_id,
        "internal_date": internal_date,
        "from_addr": from_addr,
        "to_addr": to_addr,
        "cc_addr": cc_addr,
        "body": body,
        "body_length": len(body),
        "score": 0,
        "classification": "REVIEW",
        "is_thread_representative": True,
    }


def extract_table_field(section, field_name):
    """Extract a value from the markdown table."""
    pattern = rf'\|\s*{re.escape(field_name)}\s*\|\s*`?([^`\n]*)`?\s*\|'
    match = re.search(pattern, section)
    if match:
        return match.group(1).strip()
    return ""


def extract_body(section):
    """Extract body text: everything after the metadata table until --- or end."""
    # Find the end of the table (last | line before blank line)
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


def calculate_score(msg, config):
    """Calculate priority score for a message."""
    score = 0
    subject = msg["subject"]
    from_addr = msg["from_addr"]
    cc_addr = msg["cc_addr"]
    body = msg["body"]
    weights = config["scoreWeights"]

    # Check subject against priority patterns
    for term in config["prioritySubjectPatterns"]:
        if term.lower() in subject.lower():
            score += weights["prioritySubject"]

    # Check sender against priority patterns
    for sender_pattern in config["prioritySenderPatterns"]:
        if re.search(sender_pattern, from_addr, re.IGNORECASE):
            score += weights["prioritySender"]

    # Check subject against auto-skip patterns
    for pattern in config["autoSkipSubjectPatterns"]:
        if re.search(pattern, subject, re.IGNORECASE):
            score += weights["autoSkipSubject"]

    # Check sender against auto-skip patterns
    for pattern in config["autoSkipSenderPatterns"]:
        if re.search(pattern, from_addr, re.IGNORECASE):
            score += weights["autoSkipSender"]

    # Priority terms in body (weighted per occurrence)
    for term in config["prioritySubjectPatterns"]:
        count = body.lower().count(term.lower())
        score += count * weights["bodyPriorityTerm"]

    # Bonus for having Cc recipients
    if cc_addr and cc_addr.strip():
        score += weights["hasCc"]

    # Penalty for messages FROM Dave
    if "dave.witkin" in from_addr.lower():
        score += weights["fromDavePenalty"]

    return score


def classify_message(msg, config):
    """Classify a message based on rules and score."""
    subject = msg["subject"].lower()
    body = msg["body"].lower()
    from_addr = msg["from_addr"].lower()
    score = msg["score"]
    thresholds = config["thresholds"]

    # Rule 1: NEEDS-HUMAN
    for term in config["needsHumanPatterns"]:
        if term.lower() in subject or term.lower() in body:
            return "NEEDS-HUMAN"

    # Rule 2: SKIP-AUTO (if auto-skip patterns match AND no priority patterns match)
    auto_skip_subject = any(
        re.search(p, msg["subject"], re.IGNORECASE)
        for p in config["autoSkipSubjectPatterns"]
    )
    auto_skip_sender = any(
        re.search(p, msg["from_addr"], re.IGNORECASE)
        for p in config["autoSkipSenderPatterns"]
    )
    has_priority_subject = any(
        term.lower() in msg["subject"].lower()
        for term in config["prioritySubjectPatterns"]
    )
    has_priority_sender = any(
        re.search(p, msg["from_addr"], re.IGNORECASE)
        for p in config["prioritySenderPatterns"]
    )

    if (auto_skip_subject or auto_skip_sender) and not (has_priority_subject or has_priority_sender):
        return "SKIP-AUTO"

    # Rule 3: INGEST-CANDIDATE
    if score >= thresholds["ingestCandidateScore"]:
        return "INGEST-CANDIDATE"

    # Rule 4: REVIEW
    if score >= thresholds["reviewScore"]:
        return "REVIEW"

    # Rule 5: SKIP-AUTO (low score)
    if score < thresholds["skipAutoScore"]:
        return "SKIP-AUTO"

    # Rule 6: REVIEW (catch-all)
    return "REVIEW"


def collapse_threads(messages, config):
    """Collapse messages by thread, selecting representatives."""
    threads = {}
    for msg in messages:
        tid = msg["thread_id"]
        if tid not in threads:
            threads[tid] = []
        threads[tid].append(msg)

    sort_order = config.get("threadRepresentativeSort", ["score_desc"])

    for tid, thread_msgs in threads.items():
        if len(thread_msgs) <= 1:
            continue

        def sort_key(m):
            keys = []
            for criterion in sort_order:
                if criterion == "score_desc":
                    keys.append(-m["score"])
                elif criterion == "body_length_desc":
                    keys.append(-m["body_length"])
                elif criterion == "internal_date_desc":
                    keys.append(m["internal_date"])  # string comparison works for ISO
                elif criterion == "message_number_asc":
                    keys.append(m["message_no"])
            return tuple(keys)

        thread_msgs.sort(key=sort_key)
        rep = thread_msgs[0]
        rep_score = rep["score"]

        for m in thread_msgs[1:]:
            if m["score"] > rep_score:
                # Higher score than rep — keep original classification
                pass
            else:
                m["classification"] = "DUPLICATE-CANDIDATE"
                m["is_thread_representative"] = False


def write_csv(messages, output_path):
    """Write pre-triage CSV."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "MessageNo", "MessageId", "ThreadId", "Subject", "From", "To", "Cc",
            "Score", "Classification", "InternalDate", "BodyLength", "IsThreadRepresentative"
        ])
        for msg in messages:
            writer.writerow([
                msg["message_no"],
                msg["message_id"],
                msg["thread_id"],
                msg["subject"],
                msg["from_addr"],
                msg["to_addr"],
                msg["cc_addr"],
                msg["score"],
                msg["classification"],
                msg["internal_date"],
                msg["body_length"],
                msg["is_thread_representative"],
            ])


def write_triage_md(messages, output_path):
    """Write message-triage-auto.md."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    sorted_msgs = sorted(messages, key=lambda m: m["message_no"])
    lines = [
        "# Message Triage — Auto Classification",
        "",
        f"**Total:** {len(messages)} messages",
        "",
        "| MessageNo | Subject | From | Score | Classification |",
        "|-----------|---------|------|-------|----------------|",
    ]
    for msg in sorted_msgs:
        subject = msg["subject"][:60] + ("..." if len(msg["subject"]) > 60 else "")
        from_short = msg["from_addr"][:40]
        lines.append(f"| {msg['message_no']} | {subject} | {from_short} | {msg['score']} | {msg['classification']} |")
    lines.append("")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_priority_md(messages, output_path):
    """Write priority-review-queue.md (INGEST-CANDIDATE + REVIEW only)."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    priority_msgs = [m for m in messages if m["classification"] in ("INGEST-CANDIDATE", "REVIEW")]
    priority_msgs.sort(key=lambda m: -m["score"])
    lines = [
        "# Priority Review Queue",
        "",
        f"**Total:** {len(priority_msgs)} messages",
        "",
        "| Priority | MessageNo | Subject | From | Score | Classification |",
        "|----------|-----------|---------|------|-------|----------------|",
    ]
    for i, msg in enumerate(priority_msgs, 1):
        subject = msg["subject"][:60] + ("..." if len(msg["subject"]) > 60 else "")
        from_short = msg["from_addr"][:40]
        lines.append(f"| {i} | {msg['message_no']} | {subject} | {from_short} | {msg['score']} | {msg['classification']} |")
    lines.append("")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_skip_sample(messages, config, output_path):
    """Write skip-auto-sample.md with PENDING audit decisions."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    skip_msgs = [m for m in messages if m["classification"] == "SKIP-AUTO"]
    total_skip = len(skip_msgs)
    thresholds = config["thresholds"]
    sample_size = max(thresholds["minimumSkipSample"], math.ceil(total_skip * thresholds["samplePercent"] / 100))
    sample_size = min(sample_size, total_skip)

    # Random sample
    sample = random.sample(skip_msgs, sample_size) if sample_size < total_skip else skip_msgs[:]
    sample.sort(key=lambda m: m["message_no"])

    lines = [
        "# Skip-Auto Sample Audit",
        "",
        f"**Sample size:** {len(sample)} of {total_skip}",
        "**Selection:** random sample of SKIP-AUTO messages",
        "",
        "| MessageNo | Subject | From | Audit Decision | Reason |",
        "|-----------|---------|------|---------------|--------|",
    ]
    for msg in sample:
        subject = msg["subject"][:60] + ("..." if len(msg["subject"]) > 60 else "")
        from_short = msg["from_addr"][:40]
        lines.append(f"| {msg['message_no']} | {subject} | {from_short} | `PENDING` | Awaiting review |")
    lines.append("")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_thread_groups(messages, output_path):
    """Write thread-groups.md."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    threads = {}
    for msg in messages:
        tid = msg["thread_id"]
        if tid not in threads:
            threads[tid] = []
        threads[tid].append(msg)

    lines = [
        "# Thread Groups",
        "",
        f"**Total threads:** {len(threads)}",
        "",
    ]
    for tid, thread_msgs in sorted(threads.items(), key=lambda x: min(m["message_no"] for m in x[1])):
        reps = [m for m in thread_msgs if m["is_thread_representative"]]
        rep_no = reps[0]["message_no"] if reps else thread_msgs[0]["message_no"]
        lines.append(f"## Thread: {tid} (Representative: #{rep_no})")
        lines.append("")
        lines.append("| Role | MessageNo | Subject | From | Score | Classification |")
        lines.append("|------|-----------|---------|------|-------|----------------|")
        for m in sorted(thread_msgs, key=lambda x: x["message_no"]):
            role = "REP" if m["is_thread_representative"] else "DUP"
            subject = m["subject"][:50] + ("..." if len(m["subject"]) > 50 else "")
            from_short = m["from_addr"][:35]
            lines.append(f"| {role} | {m['message_no']} | {subject} | {from_short} | {m['score']} | {m['classification']} |")
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_summary(messages, config, output_path):
    """Write pretriage-summary.md."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    counts = {}
    for msg in messages:
        c = msg["classification"]
        counts[c] = counts.get(c, 0) + 1

    total = len(messages)
    threads = len(set(m["thread_id"] for m in messages))
    reps = sum(1 for m in messages if m["is_thread_representative"])

    lines = [
        "# Pre-Triage Summary",
        "",
        "| Classification | Count | Percentage |",
        "|----------------|-------|------------|",
    ]
    for cls in ["INGEST-CANDIDATE", "REVIEW", "SKIP-AUTO", "DUPLICATE-CANDIDATE", "NEEDS-HUMAN"]:
        count = counts.get(cls, 0)
        pct = f"{count / total * 100:.1f}%" if total > 0 else "0.0%"
        lines.append(f"| {cls} | {count} | {pct} |")
    lines.append(f"| **Total** | **{total}** | **100%** |")
    lines.append("")
    lines.append(f"**Threads:** {threads} unique threads")
    lines.append(f"**Thread collapse reduced from {total} to {reps} candidate messages**")
    lines.append("")
    lines.append("**Next steps:**")
    lines.append("1. Review priority-review-queue.md (INGEST-CANDIDATE + REVIEW messages)")
    lines.append(f"2. Audit skip-auto-sample.md ({counts.get('SKIP-AUTO', 0)} messages)")
    lines.append("3. Create extraction register from approved messages")
    lines.append("4. Run KB extraction")
    lines.append("")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    args = parse_args()

    # Load config
    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Parse input
    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    messages = parse_sections(content)
    print(f"Parsed {len(messages)} messages from export.")

    # Score and classify
    for msg in messages:
        msg["score"] = calculate_score(msg, config)
        msg["classification"] = classify_message(msg, config)

    # Collapse threads
    collapse_threads(messages, config)

    # Write all outputs
    write_csv(messages, args.output_csv)
    write_triage_md(messages, args.triage_md)
    write_priority_md(messages, args.priority_md)
    write_skip_sample(messages, config, args.skip_sample_md)
    write_thread_groups(messages, args.thread_groups_md)
    write_summary(messages, config, args.summary_md)

    # Print summary
    counts = {}
    for msg in messages:
        c = msg["classification"]
        counts[c] = counts.get(c, 0) + 1
    print(f"Classification breakdown:")
    for cls in ["INGEST-CANDIDATE", "REVIEW", "SKIP-AUTO", "DUPLICATE-CANDIDATE", "NEEDS-HUMAN"]:
        print(f"  {cls}: {counts.get(cls, 0)}")
    print(f"  Total: {len(messages)}")
    print(f"\nOutputs written:")
    print(f"  CSV: {args.output_csv}")
    print(f"  Triage: {args.triage_md}")
    print(f"  Priority queue: {args.priority_md}")
    print(f"  Skip sample: {args.skip_sample_md}")
    print(f"  Thread groups: {args.thread_groups_md}")
    print(f"  Summary: {args.summary_md}")


if __name__ == "__main__":
    main()
