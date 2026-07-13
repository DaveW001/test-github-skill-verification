# doc-to-markdown reference

## Conversion strategy

Primary converter:
- `markitdown`

Fallbacks:
- HTML: `markdownify` + `beautifulsoup4`
- PDF text fallback: `pdfplumber`/`pypdf` if MarkItDown fails

Install:
- `pip install markitdown markdownify beautifulsoup4 pdfplumber`

## Naming policy

- Default output is `<source stem>.md`
- Optional cleanup may replace `_` with `-` and trim saved-web-page timestamps
- One source document should resolve to one stable Markdown target
- Never create `-2`, `-3`, etc. on reruns for the same source; reruns should overwrite or skip the same target
- Only append a safe suffix when two different sources in the same run normalize to the same cleaned target name
- Never overwrite an existing `.md` unless explicitly requested

## Manifest fields

- `source`
- `target`
- `status` (`converted`, `skipped-existing`, `failed`, `manual-review`)
- `converter`
- `notes`

## Review heuristics

Flag manual review when:
- output is empty or extremely short
- headings disappear from a long source
- tables flatten badly
- HTML boilerplate dominates output
- encoding artifacts appear

## Consolidation and paragraph reflow

- PDF-style hard-wrapped prose should be reflowed into normal paragraphs where safe
- Bullet items may span multiple physical lines in the source but should become single logical bullet items in Markdown
- This workflow is intended to produce **one Markdown file per source document**, not multiple fragments from one source
- If the source itself is a multi-page PDF or long HTML article, it should still remain one `.md` unless the user explicitly requests chunking

## Document type modes

The `--mode` flag controls how aggressively PDF text is reflowed:

### `auto` (default)
Heuristic detection based on:
- average line length (shorter → slides signal)
- ratio of short lines ≤40 chars
- count of standalone page numbers
- keyword signals: "PROPRIETARY AND CONFIDENTIAL", "Kick-Off", "Webinar", "Presentation", "©"
- If slides signals ≥ 4 → `slides` mode, otherwise → `report` mode

### `report` mode
- Aggressive paragraph reflow: joins consecutive plain-text lines into paragraphs
- Merges split bullet items into single logical lines
- Best for: structured reports, memos, plans, policy documents

### `slides` mode
- Gentle reflow: joins obvious hard wraps within visual blocks but preserves blank-line-separated groupings
- Keeps slide-style short text blocks intact
- Best for: presentation decks, visual handouts, kick-off slide decks

### Overriding auto-detection
```bash
# Force slides mode for a deck
python scripts/convert_to_markdown.py "deck.pdf" --mode slides --clean-names --overwrite

# Force report mode for a document that was misdetected
python scripts/convert_to_markdown.py "report.pdf" --mode report --clean-names --overwrite
```

## Notes

This skill is intentionally focused on document conversion. If the source is already Markdown, skip it rather than rewriting it.
