---
name: visual-ocr
description: Extract structured content from visual slide images (org charts, timelines, diagrams, tables, relationship maps) using vision AI. Use when processing slide deck PNG/JPG images that contain visual structures beyond plain text, when existing OCR output is garbled or missing visual relationships, or when ingesting presentation graphics into the knowledge graph. Triggers on "extract visual content", "OCR this slide", "read this diagram", "process slide images", "visual extraction", or when working with PNG/JPG slide images that have org charts, timelines, portfolios, or diagrams.
---

# Visual OCR

Extract structured markdown from visual slide images using vision AI models.

## Quick Start

Process a single image:
```bash
python scripts/extract_visual.py "path/to/slide.png" --output-dir ./output
```

Batch process a directory:
```bash
python scripts/extract_visual.py "path/to/slides/" --output-dir ./output --batch
```

With specific visual type:
```bash
python scripts/extract_visual.py "path/to/org-chart.png" --prompt-type org-chart
```

## Models

**Primary: Gemini 2.5 Flash** (direct Google API, free tier)
- Cost: Free (Google AI Studio tier)
- Best for: All visual types, especially diagrams and charts
- API key: Auto-loaded from `~/.local/gemini-proxy/api_keys.txt` or `GEMINI_API_KEY` env var

**Fallback: gpt-5.4-mini** (via OpenRouter)
- Used automatically when Gemini fails
- Cost: ~$0.003 per slide
- Requires `OPENROUTER_API_KEY` env var

## Prompt Types

| Type | Use For |
|------|---------|
| `auto` (default) | Mixed/unknown content — model detects all visual structures |
| `org-chart` | Hierarchical org charts with names, roles, units |
| `timeline` | Roadmaps, milestones, Gantt-style visuals |
| `table` | Comparison matrices, portfolio status tables |
| `diagram` | Relationship maps, flow charts, process diagrams |

## Output Format

Each image produces a markdown file with:
- YAML frontmatter (source file, model used, visual type detected)
- Semantic sections preserving visual relationships
- Markdown tables for tabular data
- Hierarchical lists for org charts
- Chronological lists for timelines

## Workflow

1. Identify image(s) needing visual extraction
2. Run `extract_visual.py` with appropriate `--prompt-type`
3. Review output markdown for accuracy
4. Feed structured markdown into knowledge graph ingestion pipeline

## Resources

- **scripts/extract_visual.py** — Main extraction script (run directly)
- **references/prompt-templates.md** — System prompts for each visual type (for prompt tuning)
- **references/visual-types.md** — Supported content types with output format schemas
