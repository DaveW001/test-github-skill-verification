#!/usr/bin/env python3
"""Create a bounded Markdown transcript from an OpenCode JSON session export.

Only visible user/assistant text parts are included. Reasoning, tool calls,
patches, ignored text, and step metadata are intentionally excluded.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from datetime import datetime, timezone
from pathlib import Path


KEY_LINE = re.compile(
    r"(?i)(summary|result|status|decision|complete|failed|error|warning|next|"
    r"remaining|recommend|stop|process|opencode|database|session|verify|pass)"
)
DCP_TAG = re.compile(r"<dcp-message-id>.*?</dcp-message-id>", re.DOTALL)


def timestamp(value: object) -> str:
    if not isinstance(value, (int, float)):
        return "time unavailable"
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).astimezone().isoformat(timespec="seconds")


def remove_code_blocks(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    in_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            if not in_fence:
                output.append("[Code block omitted from readable edition.]")
            in_fence = not in_fence
            continue
        if not in_fence:
            output.append(line)
    return "\n".join(output)


def wrap_text(text: str) -> list[str]:
    text = DCP_TAG.sub("", remove_code_blocks(text)).strip()
    output: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            if output and output[-1] != "":
                output.append("")
            continue
        if line.startswith(("#", "- ", "* ", "> ")):
            output.extend(textwrap.wrap(line, width=120, subsequent_indent="  ") or [line])
        else:
            output.extend(textwrap.wrap(line, width=120) or [line])
    while output and output[-1] == "":
        output.pop()
    return output


def key_excerpt(lines: list[str], role: str) -> list[str]:
    cap = 22 if role == "user" else 16
    if len(lines) <= cap:
        return lines

    chosen = set(range(min(7, len(lines))))
    chosen.update(range(max(0, len(lines) - 4), len(lines)))
    for index, line in enumerate(lines):
        if KEY_LINE.search(line):
            chosen.add(index)
        if len(chosen) >= cap:
            break
    ordered = sorted(chosen)[:cap]
    result: list[str] = []
    previous = -1
    for index in ordered:
        if previous >= 0 and index > previous + 1:
            result.append("[… visible text shortened …]")
        result.append(lines[index])
        previous = index
    return result


def render(data: dict, source: Path, line_limit: int) -> str:
    info = data.get("info") or {}
    sections: list[list[str]] = []
    omitted = {"reasoning": 0, "tool": 0, "patch": 0, "step": 0, "ignored_text": 0}

    for message in data.get("messages") or []:
        message_info = message.get("info") or {}
        role = message_info.get("role")
        if role not in {"user", "assistant"}:
            continue
        visible: list[str] = []
        for part in message.get("parts") or []:
            part_type = part.get("type")
            if part_type == "text" and not part.get("ignored") and part.get("text"):
                visible.extend(wrap_text(str(part["text"])))
            elif part_type == "text" and part.get("ignored"):
                omitted["ignored_text"] += 1
            elif part_type in {"reasoning", "tool", "patch"}:
                omitted[part_type] += 1
            elif isinstance(part_type, str) and part_type.startswith("step-"):
                omitted["step"] += 1
        if not visible:
            continue
        label = "User" if role == "user" else "Assistant"
        created = (message_info.get("time") or {}).get("created")
        section = [f"## {label} — {timestamp(created)}", ""]
        section.extend(key_excerpt(visible, role))
        section.append("")
        sections.append(section)

    header = [
        "# Readable OpenCode Session Discussion",
        "",
        f"- Session: `{info.get('id', 'unknown')}`",
        f"- Title: {info.get('title', 'Untitled')}",
        f"- Source export: `{source}`",
        f"- Messages in raw export: {len(data.get('messages') or [])}",
        "- Included: visible user and assistant text, shortened where needed.",
        "- Excluded: hidden reasoning, tool payloads, patches, ignored text, and step metadata.",
        "",
        "## Omission counts",
        "",
        f"- Reasoning parts: {omitted['reasoning']}",
        f"- Tool parts: {omitted['tool']}",
        f"- Patch parts: {omitted['patch']}",
        f"- Step metadata parts: {omitted['step']}",
        f"- Ignored text parts: {omitted['ignored_text']}",
        "",
    ]
    lines = header + [line for section in sections for line in section]
    if len(lines) > line_limit:
        lines = lines[: line_limit - 2]
        lines.extend(["", "[… transcript stopped at configured line limit …]"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--line-limit", type=int, default=1000)
    args = parser.parse_args()
    if args.line_limit < 100:
        parser.error("--line-limit must be at least 100")
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    markdown = render(data, args.input, args.line_limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(args.output), "lines": len(markdown.splitlines())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
