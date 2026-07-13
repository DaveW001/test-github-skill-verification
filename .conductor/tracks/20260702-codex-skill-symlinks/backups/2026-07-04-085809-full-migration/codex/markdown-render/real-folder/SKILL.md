---
name: markdown-render
description: |
  Convert markdown files into polished, branded, static HTML pages with strong readability and content parity.

  Triggers when user mentions:
  - "render markdown"
  - "markdown to HTML"
  - "convert markdown to page"
  - "make this markdown look better"
---

# markdown-render

Render any structured markdown file into a clean, branded HTML page that preserves meaning while improving readability.

## Quick Usage

When asked to render markdown:

1. Read source markdown
2. Map markdown patterns to the component map below
3. Copy Radikal fonts to local output `assets/fonts/` (if not present)
4. Generate a self-contained HTML file with embedded CSS
5. Validate parity (no dropped decision-relevant content)

## Required Inputs

- Source markdown path (absolute)
- Output HTML path (absolute)

## Optional Inputs

- Override title/subtitle
- Override output asset path
- Include print-optimized layout (default: yes)

## Output Requirements

- Static HTML file (single file, embedded CSS)
- Local font references via `./assets/fonts/*.woff2`
- Readable in browser when opened from local filesystem
- Core meaning preserved from markdown source

## Canonical Brand Sources

- HTML style precedent:
  - `C:\development\marketing\content\templates\lead-magnet-checklist-template.html`
- Font token precedent:
  - `C:\development\marketing\graphics\fmqsmo-award\src\index.css`
- Brand voice:
  - `C:\development\marketing\strategy\docs\90-archive\context\brand-voice.md`

## Canonical Font Copy-From Path

- `C:\development\marketing\content\topics\ai-washing-procurement\lead-magnet\assets\fonts\`

Copy these six files into the output-side `assets/fonts/` directory:
- `Radikal.woff2`
- `Radikal-Italic.woff2`
- `Radikal-Medium.woff2`
- `Radikal-MediumItalic.woff2`
- `Radikal-Bold.woff2`
- `Radikal-BoldItalic.woff2`

## Color Tokens

- `#0086CA` PA Blue
- `#FDBA31` PA Gold
- `#1a1a2e` PA Dark
- `#4a4a5a` PA Gray
- `#f8f9fa` PA Light
- `#0A2342` Supporting Navy
- `#147BBB` Secondary Blue

## Component Map

Use this mapping for markdown-to-HTML rendering:

| Markdown Pattern | HTML Component |
|---|---|
| `# Title` | header with H1 |
| metadata lines (`**X:** value`) | meta cards with explicit order: Working title -> Description -> Audience |
| `**Total Estimated Cost:**` metadata line | separate full-width estimated-cost card below metadata cards |
| `## Section` | section with numbered header |
| `### Subsection` | subsection H3 |
| paragraphs | `<p>` |
| unordered lists | `<ul><li>` |
| ordered lists | `<ol><li>` |
| `[bracketed editorial notes]` | editorial note aside/callout |
| proof/evidence blocks | proof-point card |
| pricing/cost bullets | pricing card |
| risk sections | risk card |
| open question sections | question card |
| blockquotes | blockquote with left border |
| inline code | `<code>` |
| `---` | `<hr>` |

## Detection Heuristics

- Metadata normalization: if Working title/Description/Audience/Total Estimated Cost fields are present, render the first three as standard metadata cards and Estimated Cost as a separate full-width card.
- Prefer preserving source heading text; if user explicitly requests heading cleanup, apply display/markdown normalization (for example, remove ordinal/page-count wrappers).

- Editorial notes: bracketed standalone lines like `[Addresses ...]`
- Proof points: lines containing "Proof Point", "Supporting Analog", or "Evidence"
- Pricing blocks: lines containing `$`, `M`, `cost`, `pricing`, `contract value`
- Risk blocks: section titles/lines containing `risk`, `failure`, `turnover trap`
- Open questions: sections titled `Open questions` or list items ending in `?`

## Fallback Rule (Required)

If a markdown pattern is unknown, render it as semantic HTML with default body styling.

**Never drop content. Never collapse decision-relevant detail.**

## Readiness Gate

Before first document render, verify:

1. This SKILL.md exists with valid frontmatter
2. Workflow steps are present
3. Component map is available
4. Font copy path and color tokens are defined
5. Fallback rule is defined

Only then proceed to generate the output HTML.
