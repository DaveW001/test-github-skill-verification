from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup
from markdownify import markdownify as html_to_markdown
from markitdown import MarkItDown


SUPPORTED_EXTENSIONS = {".pdf", ".html", ".htm"}
SKIP_TAGS = {"script", "style", "noscript", "nav", "footer", "header", "aside", "form"}

SLIDES_KEYWORDS = {
    "proprietary and confidential",
    "confidential",
    "©",
    "all rights reserved",
    "slide",
    "deck",
    "presentation",
    "kick-off",
    "kickoff",
    "webinar",
    "briefing",
}


@dataclass
class ManifestEntry:
    source: str
    target: str | None
    status: str
    converter: str | None = None
    notes: str = ""


def iter_sources(root: Path, recursive: bool) -> Iterable[Path]:
    if root.is_file():
        yield root
        return

    pattern = "**/*" if recursive else "*"
    for path in root.glob(pattern):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def clean_stem(stem: str) -> str:
    cleaned = re.sub(r"\s*_+\s*", " - ", stem)
    cleaned = re.sub(r"\s*\(\d{1,2}\s*-\s*\d{1,2}\s*-\s*\d{4}.*?\)$", "", cleaned)
    cleaned = re.sub(r"(?:\s*-\s*){2,}", " - ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def target_path(source: Path, clean_names: bool) -> Path:
    stem = clean_stem(source.stem) if clean_names else source.stem
    return source.with_name(f"{stem}.md")


def resolve_targets(sources: list[Path], clean_names: bool) -> dict[Path, Path]:
    resolved: dict[Path, Path] = {}
    used: set[Path] = set()

    for source in sources:
        base_target = target_path(source, clean_names)
        candidate = base_target
        suffix = 2

        while candidate in used:
            candidate = base_target.with_name(f"{base_target.stem}-{suffix}{base_target.suffix}")
            suffix += 1

        resolved[source] = candidate
        used.add(candidate)

    return resolved


def extract_html_main(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")
    for tag in soup.find_all(list(SKIP_TAGS)):
        tag.decompose()
    container = soup.find("main") or soup.find("article") or soup.body or soup
    return str(container)


def render_html_fallback(source: Path) -> str:
    text = source.read_text(encoding="utf-8", errors="replace")
    main_html = extract_html_main(text)
    return html_to_markdown(main_html, heading_style="ATX")


def render_pdf_fallback(source: Path) -> str:
    try:
        import pdfplumber
    except Exception as exc:
        raise RuntimeError(f"pdfplumber unavailable: {exc}") from exc

    parts = []
    with pdfplumber.open(source) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                parts.append(text.strip())

    markdown = "\n\n".join(parts).strip()
    if not markdown:
        raise RuntimeError("pdf fallback produced no text")
    return markdown


def convert_source(source: Path, md: MarkItDown) -> tuple[str, str, str]:
    ext = source.suffix.lower()
    if ext == ".pdf":
        try:
            result = md.convert_local(source)
            return result.markdown.strip(), "markitdown", ""
        except Exception as exc:
            return render_pdf_fallback(source), "pdfplumber", f"markitdown failed: {exc}"

    if ext in {".html", ".htm"}:
        try:
            result = md.convert_local(source)
            markdown = (result.markdown or "").strip()
            if len(markdown) < 40:
                raise ValueError("markitdown output too short")
            return markdown, "markitdown", ""
        except Exception as exc:
            return render_html_fallback(source), "markdownify", f"markitdown failed: {exc}"

    raise ValueError(f"Unsupported extension: {ext}")


def should_flag_for_review(markdown: str, source: Path) -> str:
    if not markdown.strip():
        return "empty output"
    if len(markdown) < 80 and source.stat().st_size > 5000:
        return "output suspiciously short"
    if source.suffix.lower() in {".html", ".htm"} and len(markdown) > 0:
        if markdown.count("\n") < 2 and source.stat().st_size > 10000:
            return "possible boilerplate-heavy html output"
    if "\ufffd" in markdown:
        return "encoding artifacts present"
    return ""


# ---------------------------------------------------------------------------
# Document type detection
# ---------------------------------------------------------------------------

def detect_doc_type(markdown: str, source: Path) -> str:
    """Return 'slides' or 'report' based on heuristics."""
    lower = markdown.lower()
    filename_lower = source.stem.lower()

    keyword_hits = sum(1 for kw in SLIDES_KEYWORDS if kw in lower or kw in filename_lower)

    lines = markdown.split("\n")
    nonblank = [ln for ln in lines if ln.strip()]
    if not nonblank:
        return "report"

    avg_line_len = sum(len(ln) for ln in nonblank) / len(nonblank)
    short_lines = sum(1 for ln in nonblank if len(ln.strip()) <= 40)
    short_ratio = short_lines / len(nonblank)
    standalone_numbers = sum(1 for ln in nonblank if re.match(r"^\d{1,3}$", ln.strip()))

    slides_signals = 0
    if keyword_hits >= 2:
        slides_signals += 3
    elif keyword_hits >= 1:
        slides_signals += 1
    if avg_line_len < 50:
        slides_signals += 2
    if short_ratio > 0.55:
        slides_signals += 2
    if standalone_numbers >= 4:
        slides_signals += 2

    return "slides" if slides_signals >= 4 else "report"


# ---------------------------------------------------------------------------
# Reflow engines
# ---------------------------------------------------------------------------

def is_list_line(line: str) -> bool:
    return bool(re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|[•●]\s+)", line))


def is_structural_line(line: str) -> bool:
    stripped = line.strip()
    return (
        not stripped
        or stripped.startswith("#")
        or stripped.startswith(">")
        or stripped.startswith("![")
        or stripped.startswith("[")
        or stripped.startswith("```")
        or stripped.startswith("|")
        or is_list_line(stripped)
    )


def reflow_report(markdown: str) -> str:
    """Aggressive paragraph reflow for structured reports and memos."""
    lines = markdown.split("\n")
    out: list[str] = []
    paragraph: list[str] = []
    current_list_item: str | None = None

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(" ".join(part.strip() for part in paragraph if part.strip()))
            paragraph = []

    def flush_list_item() -> None:
        nonlocal current_list_item
        if current_list_item is not None:
            out.append(re.sub(r"\s+", " ", current_list_item).strip())
            current_list_item = None

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            next_nonblank = ""
            j = i + 1
            while j < len(lines):
                if lines[j].strip():
                    next_nonblank = lines[j].strip()
                    break
                j += 1

            if current_list_item is not None and next_nonblank and not is_structural_line(next_nonblank):
                i += 1
                continue
            flush_paragraph()
            flush_list_item()
            if out and out[-1] != "":
                out.append("")
            i += 1
            continue

        if stripped.startswith("#") or stripped.startswith(">") or stripped.startswith("```") or stripped.startswith("|") or stripped.startswith("!["):
            flush_paragraph()
            flush_list_item()
            out.append(stripped)
            i += 1
            continue

        if is_list_line(stripped):
            flush_paragraph()
            flush_list_item()
            current_list_item = stripped
            i += 1
            continue

        if current_list_item is not None:
            current_list_item += " " + stripped
            i += 1
            continue

        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    flush_list_item()
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def reflow_slides(markdown: str) -> str:
    """Gentle reflow for presentation decks: join obvious hard wraps within
    the same visual block but preserve blank-line-separated blocks."""
    lines = markdown.split("\n")
    out: list[str] = []
    block: list[str] = []

    def flush_block() -> None:
        nonlocal block
        if not block:
            return
        joined = " ".join(ln.strip() for ln in block if ln.strip())
        out.append(joined)
        block = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush_block()
            if out and out[-1] != "":
                out.append("")
            continue

        if stripped.startswith("#") or stripped.startswith("```") or stripped.startswith("|") or stripped.startswith("!["):
            flush_block()
            out.append(stripped)
            continue

        block.append(stripped)

    flush_block()
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Normalize
# ---------------------------------------------------------------------------

def normalize_markdown(markdown: str, source: Path, mode: str = "auto") -> str:
    markdown = markdown.replace("\r\n", "\n").replace("\r", "\n")
    markdown = re.sub(r"^\+\s*\n+", "", markdown)
    lines: list[str] = []
    for line in markdown.splitlines():
        line = line.replace("\f", "").replace("\x0c", "")
        if line.strip() == "+":
            continue
        if not line.strip() and lines and not lines[-1].strip():
            continue
        lines.append(line)
    markdown = "\n".join(lines)

    if source.suffix.lower() == ".pdf":
        effective = mode
        if effective == "auto":
            effective = detect_doc_type(markdown, source)

        if effective == "slides":
            markdown = reflow_slides(markdown)
        else:
            markdown = reflow_report(markdown)

    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Convert PDF and HTML files to Markdown.")
    parser.add_argument("path", help="File or directory to convert")
    parser.add_argument("--recursive", action="store_true", default=True, help="Recurse into subdirectories when the path is a directory")
    parser.add_argument("--no-recursive", dest="recursive", action="store_false", help="Only convert files in the top level of the target directory")
    parser.add_argument("--clean-names", action="store_true", help="Clean saved-web-page filenames before writing output")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing .md files")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files; only report what would happen")
    parser.add_argument("--mode", choices=["auto", "report", "slides"], default="auto", help="Document type mode: auto (detect), report (aggressive reflow), slides (gentle reflow)")
    parser.add_argument("--manifest", default="conversion-manifest.json", help="Path to manifest JSON output")
    args = parser.parse_args()

    root = Path(args.path)
    md = MarkItDown()
    entries: list[ManifestEntry] = []
    sources = list(iter_sources(root, args.recursive))
    target_map = resolve_targets(sources, args.clean_names)

    for source in sources:
        target = target_map[source]
        if target.exists() and not args.overwrite:
            entries.append(ManifestEntry(str(source), str(target), "skipped-existing", notes="target already exists"))
            continue

        try:
            markdown, converter, notes = convert_source(source, md)
            markdown = normalize_markdown(markdown, source, mode=args.mode)
            review_note = should_flag_for_review(markdown, source)
            if args.dry_run:
                status = "manual-review" if review_note else "converted"
                entries.append(ManifestEntry(str(source), str(target), status, converter, review_note or notes))
                continue

            target.write_text(markdown.rstrip() + "\n", encoding="utf-8")
            status = "manual-review" if review_note else "converted"
            entries.append(ManifestEntry(str(source), str(target), status, converter, review_note or notes))
        except Exception as exc:
            entries.append(ManifestEntry(str(source), str(target), "failed", notes=str(exc)))

    manifest_path = Path(args.manifest)
    manifest_path.write_text(
        json.dumps(
            {
                "generated": datetime.now().isoformat(timespec="seconds"),
                "root": str(root),
                "mode": args.mode,
                "dry_run": args.dry_run,
                "entries": [asdict(entry) for entry in entries],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
