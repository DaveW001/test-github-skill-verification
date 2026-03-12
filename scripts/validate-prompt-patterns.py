#!/usr/bin/env python3
"""Validate prompt pattern files for structure and content quality."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


VARIABLE_RE = re.compile(r"\{\{[a-zA-Z0-9_.-]+\}\}")
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
REQUIRED_SECTIONS = [
    "Prompt Template",
    "Variables",
    "Example Input",
    "Example Output Shape",
]


@dataclass
class ValidationResult:
    file_path: Path
    errors: list[str]


def slugify(text: str) -> str:
    lowered = text.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered)
    return cleaned.strip("-")


def split_sections(text: str) -> dict[str, str]:
    matches = list(HEADING_RE.finditer(text))
    sections: dict[str, str] = {}

    for idx, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[name] = text[start:end].strip()

    return sections


def is_non_empty_section(content: str) -> bool:
    if not content:
        return False
    return bool(re.search(r"[A-Za-z0-9]", content))


def has_variable_bullets(content: str) -> bool:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            return True
    return False


def is_title_case(title: str) -> bool:
    words = [w for w in re.split(r"\s+", title.strip()) if w]
    if not words:
        return False

    for word in words:
        if not re.search(r"[A-Za-z]", word):
            continue
        if word.isupper():
            continue

        first_alpha = next((ch for ch in word if ch.isalpha()), "")
        if not first_alpha:
            continue
        if not first_alpha.isupper():
            return False

    return True


def validate_pattern_file(file_path: Path) -> ValidationResult:
    text = file_path.read_text(encoding="utf-8")
    errors: list[str] = []

    title_match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    if not title_match:
        errors.append("Missing top-level title heading (# Title).")
        return ValidationResult(file_path=file_path, errors=errors)

    title = title_match.group(1).strip()
    if not is_title_case(title):
        errors.append("Title should be Title Case.")

    expected_slug = slugify(title)
    if file_path.stem != expected_slug:
        errors.append(
            f"Filename slug mismatch: expected '{expected_slug}.md' from title, found '{file_path.name}'."
        )

    sections = split_sections(text)
    for section_name in REQUIRED_SECTIONS:
        if section_name not in sections:
            errors.append(f"Missing required section: '## {section_name}'.")

    prompt_template = sections.get("Prompt Template", "")
    if prompt_template and not VARIABLE_RE.search(prompt_template):
        errors.append("Prompt Template must include at least one '{{variable}}'.")

    variables = sections.get("Variables", "")
    if variables and not has_variable_bullets(variables):
        errors.append("Variables section must include at least one bullet item.")

    for section_name in ("Example Input", "Example Output Shape"):
        if section_name in sections and not is_non_empty_section(sections[section_name]):
            errors.append(f"{section_name} section must not be empty.")

    return ValidationResult(file_path=file_path, errors=errors)


def collect_pattern_files(prompts_dir: Path) -> list[Path]:
    files = sorted(prompts_dir.glob("*.md"))
    return [f for f in files if f.name not in {"README.md", "TEMPLATE.md"}]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate markdown prompt patterns.")
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("patterns/prompts"),
        help="Prompt pattern directory (default: patterns/prompts)",
    )
    args = parser.parse_args()

    prompts_dir = args.dir
    if not prompts_dir.exists():
        print(f"ERROR: Prompt pattern directory not found: {prompts_dir}")
        return 1

    pattern_files = collect_pattern_files(prompts_dir)
    if not pattern_files:
        print("ERROR: No prompt pattern files found (excluding README.md and TEMPLATE.md).")
        return 1

    failures: list[ValidationResult] = []
    for file_path in pattern_files:
        result = validate_pattern_file(file_path)
        if result.errors:
            failures.append(result)

    if failures:
        print("Prompt pattern validation failed:\n")
        for failure in failures:
            print(f"- {failure.file_path.as_posix()}")
            for error in failure.errors:
                print(f"  - {error}")
        return 1

    print(f"Prompt pattern validation passed for {len(pattern_files)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
