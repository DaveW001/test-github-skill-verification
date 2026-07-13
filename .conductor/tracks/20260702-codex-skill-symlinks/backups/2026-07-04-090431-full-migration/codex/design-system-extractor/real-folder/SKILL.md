---
name: design-system-extractor
description: Extract design tokens and system elements from URLs or graphic files without external dependencies. Use when user provides a URL/image and asks to extract design system, reverse engineer styles, or get design tokens.
---

# Design System Extractor

Extracts design tokens (colors, typography, spacing, etc.) from live websites or graphic files using LLM capabilities. Zero external dependencies.

Supports three output contracts:
- Legacy Markdown report
- Legacy JSON schema
- Google-style `DESIGN.md` draft format (YAML front matter + ordered rationale sections)

## Activation Triggers

- User provides URL + mentions "design system", "design tokens", "extract styles", "reverse engineer"
- User provides graphic file path + mentions "design system", "design tokens", "extract colors"
- User asks "what fonts/colors does [site] use?"

## Input Modes

### Mode 1: URL Extraction
**Use when:** User provides a live website URL

**Tools:** `webfetch` (HTML/CSS retrieval)

**Process:**
1. Fetch HTML content via webfetch
2. Extract inline styles, `<style>` blocks, linked CSS
3. Parse design tokens from CSS variables and computed styles
4. Output structured documentation

**Best for:** Live sites, CSS-rich applications

### Mode 2: File Extraction
**Use when:** User provides image file path (`.png`, `.jpg`, `.jpeg`, `.svg`, `.webp`)

**Tools:** `Read` (vision analysis)

**Process:**
1. Read graphic file using vision capabilities
2. Analyze perceived colors, typography, spacing
3. Note values as "perceived" vs "exact"
4. Output structured documentation with confidence notes

**Best for:** Screenshots, mockups, reference images

### Mode 3: Hybrid Validation
**Use when:** User provides both URL and screenshots for cross-validation

**Tools:** `webfetch` + `Read`

**Process:**
1. Extract tokens from URL
2. Extract perceived tokens from image
3. Compare and reconcile differences
4. Output with confidence ratings

## Canonical Extraction Model

Before rendering any output format, normalize extracted values into one canonical model with provenance:

- `exact`: directly observed in source styles (highest confidence)
- `perceived`: visually estimated from images
- `inferred`: reasoned from partial evidence

This enables consistent rendering to Markdown, JSON, and `DESIGN.md`.

## Output Formats

### Markdown (Default)
Human-readable design system documentation. See `reference.md` for structure.

### JSON
Structured data for programmatic use. See `reference.md` for schema.

### DESIGN.md
Google-style draft format:
- Optional YAML front matter for machine-readable tokens (`colors`, `typography`, `rounded`, `spacing`, `components`)
- Ordered `##` rationale sections for design intent and usage guidance

`DESIGN.md` is generated only when explicitly requested (to preserve backward-compatible defaults).

## Decision Tree

```
Input provided?
├── URL only → Mode 1 (URL Extraction)
├── File path only → Mode 2 (File Extraction)
├── Both URL + file → Mode 3 (Hybrid)
└── Neither → Ask user for input

Output preference?
├── Explicit "DESIGN.md" / "design-md" → DESIGN.md format
├── "JSON" or programmatic → JSON format
├── "both" or "all" → generate requested set (e.g., markdown+json, markdown+design-md, all)
└── Default (no explicit format) → Markdown format
```

## Token Categories

| Category | URL Mode | File Mode |
|----------|----------|-----------|
| Colors | Exact (CSS) | Perceived |
| Typography | Exact (CSS) | Perceived |
| Spacing | Exact (CSS) | Approximate |
| Borders | Exact (CSS) | Approximate |
| Shadows | Exact (CSS) | Approximate |
| Components | Identified | Identified |
| Layout | Exact (CSS) | Approximate |

## Tool Requirements

- **URL Mode:** `webfetch` (built-in)
- **File Mode:** `Read` tool with vision (built-in)
- **Hybrid:** Both tools

No external CLI tools or npm packages required.

## DESIGN.md Safety Rules

- Use conservative prose when evidence is weak; do not invent brand intent as fact.
- Omit unsupported token groups rather than fabricating values.
- Preserve section order for any included `##` sections.
- Duplicate section headings are **invalid** and must not be generated (per Google spec: "Error; reject the file").
- Use token references in components where applicable (e.g., `{colors.primary}`).

## Files in This Skill

- `SKILL.md` - This file (activation, modes, decision tree)
- `reference.md` - Output schemas + DESIGN.md mapping/spec notes
- `workflows.md` - Step-by-step extraction and rendering workflows
- `examples.md` - Sample outputs including DESIGN.md
