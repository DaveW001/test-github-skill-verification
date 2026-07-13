---
name: doc-to-markdown
description: Convert PDF and HTML source files to structured Markdown, preserve headings/tables/lists, and batch-convert document folders. Use when the user asks to convert documents to markdown, turn PDFs or HTML into .md, or build a reusable document-to-markdown workflow.
---

# doc-to-markdown

Convert source documents into clean Markdown with provenance and safe re-runs.

## Quick start

```bash
python "C:\Users\DaveWitkin\.config\opencode\skills\doc-to-markdown\scripts\convert_to_markdown.py" "C:\path\to\documents" --dry-run
python "C:\Users\DaveWitkin\.config\opencode\skills\doc-to-markdown\scripts\convert_to_markdown.py" "C:\path\to\documents" --clean-names
```

## What this skill does

- Converts `.pdf`, `.html`, and `.htm` files to `.md`
- Produces one stable Markdown target per source document
- Preserves headings, lists, links, and tables where possible
- Reflows PDF-style hard line breaks intelligently based on document type
- Skips existing Markdown files unless overwrite is requested
- Writes a manifest for converted, skipped, failed, and review-needed files
- Supports dry-run and resumable batch execution

## Document type modes (`--mode`)

The skill adjusts its paragraph reflow behavior based on document type:

| Mode | When to use | Behavior |
|------|-------------|----------|
| `auto` | Default | Detects document type automatically using heuristics |
| `report` | Structured reports, memos, plans | Aggressive paragraph reflow: joins wrapped prose, merges split bullets |
| `slides` | Decks, presentations, visual handouts | Gentle reflow: joins obvious hard wraps within blocks but preserves visual grouping |

Auto-detection looks for slide-deck signals: short average line length, many standalone page numbers, keywords like "PROPRIETARY AND CONFIDENTIAL", "Kick-Off", "Webinar", etc.

```bash
python "C:\Users\DaveWitkin\.config\opencode\skills\doc-to-markdown\scripts\convert_to_markdown.py" "C:\path\to\slides.pdf" --mode slides --clean-names
```

## Use this skill when

- You need to convert a folder of source documents into Markdown
- You need a safe, repeatable PDF/HTML to Markdown workflow
- You want a single command to process mixed document types

## Requirements

```bash
pip install markitdown markdownify beautifulsoup4 pdfplumber
```

## Workflow

1. Run a dry-run on the target folder.
2. Review the manifest and filename mapping.
3. Run the conversion with safe defaults.
4. Review any files flagged for manual cleanup.

## Advanced usage

See [reference.md](reference.md) for heuristics, fallback policy, and manifest format.

Run the helper script:

```bash
python scripts/convert_to_markdown.py "C:\path\to\folder" --manifest conversion-manifest.json
```
