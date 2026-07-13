# Source Conversion

This document describes how to convert each source type into readable text or markdown for entity extraction. Always attempt the simplest conversion method first.

## Markdown and Text Sources

**Extensions:** `.md`, `.txt`, `.markdown`

These require no conversion. Read directly using the Read tool.

```powershell
# Verify the file is readable
Get-Content -LiteralPath "C:\path\to\source.md" -TotalCount 5
```

Rules:
- Preserve all headings, tables, and list structures.
- Do not strip frontmatter from markdown files; it may contain metadata useful for provenance.

## PDF Sources

**Extension:** `.pdf`

Use the `doc-to-markdown` skill for PDF conversion. This skill handles text extraction, heading preservation, and table conversion.

```powershell
# Trigger the doc-to-markdown skill with the PDF path
# The skill will convert and return structured markdown
```

If the `doc-to-markdown` skill is unavailable:
1. Try `python -c "import fitz; ..."` (PyMuPDF) for text extraction.
2. Fall back to reading the PDF directly with the Read tool, which supports PDF content extraction.
3. If the PDF is scanned (image-only), flag for OCR processing and note in the ingest log.

Rules:
- Preserve heading hierarchy (`#`, `##`, `###`).
- Tables should remain tabular in markdown format.
- Page numbers and headers/footers may be discarded unless they contain entity information.

## DOCX, PPTX, and XLSX Sources

**Extensions:** `.docx`, `.pptx`, `.xlsx`

These are ZIP archives containing XML. Use Python zipfile extraction:

```python
import zipfile
from xml.etree import ElementTree

def extract_docx_text(path):
    with zipfile.ZipFile(path) as z:
        with z.open('word/document.xml') as f:
            tree = ElementTree.parse(f)
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            return ' '.join(t.text for t in tree.findall('.//w:t', ns) if t.text)
```

For batch extraction, the repo provides:
```powershell
python scripts\extract-docx.py --input "path\to\file.docx" --output "path\to\output.md"
```

Rules:
- `.docx`: Extract body text, headers, and tables. Discard formatting-only markup.
- `.pptx`: Extract slide text and notes. Preserve slide separators.
- `.xlsx`: Extract cell values as a markdown table. First row is typically the header.
- If a script is not available for a specific format, use the Read tool which supports these formats.

## Email and Slack Exports

### Email Exports (Outlook `.msg`, `.eml`)

Use the `doc-to-markdown` skill or direct parsing:

```powershell
# For .eml files (plain text RFC 822)
Get-Content -LiteralPath "path\to\email.eml" -Raw
```

For `.msg` files (Outlook native):
- Use Python `extract-msg` library, or
- Use the Read tool which can parse `.msg` content.

Rules:
- Extract: sender, recipients (names only, not email addresses per PII rules), date, subject, body.
- Strip email signatures and disclaimers unless they contain entity information.
- Attachments: list attachment filenames but do not extract content unless specifically requested.

### Slack Exports (`.json`)

Slack exports are JSON files containing message arrays:

```powershell
Get-Content -LiteralPath "path\to\slack-export.json" -Raw | ConvertFrom-Json
```

Rules:
- Extract message text, sender name, timestamp, and channel.
- Thread replies should be linked to parent messages.
- Reactions and emoji are not entity information; skip them.
- File attachments referenced in messages should be noted but not downloaded.

## Google-Native Shortcuts

**Extensions:** `.gdoc`, `.gsheet`, `.gslides`, `.gdraw`

**These are NOT readable source files.** They are Google Drive shortcut files (typically a few hundred bytes of JSON pointing to a Google Docs URL).

**You MUST NOT attempt to read these as document content.** Instead:

1. Inform the user: "This file is a Google Drive shortcut, not a readable document."
2. Ask the user to export the file:
   - `.gdoc` -> Export as `.docx` or `.pdf` from Google Docs
   - `.gsheet` -> Export as `.xlsx` or `.csv` from Google Sheets
   - `.gslides` -> Export as `.pptx` or `.pdf` from Google Slides
3. Once exported, process the converted file using the appropriate method above.

```powershell
# Detect Google shortcut files
$ext = [System.IO.Path]::GetExtension($sourcePath)
if ($ext -in @('.gdoc','.gsheet','.gslides','.gdraw')) {
    Write-Error "Google shortcut detected. Ask user to export to Office/PDF format first."
}
```

## Conversion Failure Recovery

| Failure | Recovery |
|---------|----------|
| PDF is image-only (scanned) | Flag for OCR; note in ingest log; skip extraction |
| DOCX/PPTX XML parsing error | Try Read tool as fallback; if still fails, flag for manual review |
| Email has no text body (HTML-only) | Strip HTML tags; extract plain text |
| Slack JSON is malformed | Validate with `ConvertFrom-Json`; if fails, flag for manual review |
| Google shortcut encountered | Stop and ask user for exported copy; do not attempt to parse |
| Encoding error (mojibake) | Try UTF-8, then Windows-1252, then Latin-1; note actual encoding in source node |
| File is password-protected | Stop and ask user for password or unprotected copy |
| File is corrupt (0 bytes or truncated) | Log as extraction failure; do not create entity notes from partial content |