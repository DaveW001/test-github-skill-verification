---
name: content-trend-researcher
description: Research content and topic trends across web/social sources and produce data-driven article ideas + outlines. Use for "topic research", "content ideas", "what's trending", "keyword intent", "outline", "content gaps".
compatibility: Requires internet access for web research tools (e.g. google_search/webfetch). Optional local Python helpers live in this skill folder.
---

# Content Trend Researcher

Use this skill to turn a topic into a research-backed content brief: trends, user intent, content gaps, and 1-3 outlines.

## Decision Tree

Use this skill when the user asks for:
- trend research ("what's trending", "what are people talking about", "recent discussions")
- content strategy ("what should I write", "content gap analysis", "angles")
- SEO/user intent ("search intent", "keywords", "questions people ask")
- an outline that is grounded in current sources

Do not use this skill when:
- the user already has the full outline and only needs editing/polish
- the task is purely offline writing with no need for current sources

## Output / File Handling

Before research, ask where to save the report and propose a default path.

Naming convention:
- `{topic-slug}-trend-info-{YYYY-MM-DD}.md`

See `HOW_TO_USE.md` for the full save workflow and header format.

## Quick Start

1) Ask for constraints:
- target audience
- region (if relevant)
- time window (e.g. "last 6 months")
- platforms (all vs. specific)

2) Research:
- Use `google_search` to find sources and recent discussion.
- Use `webfetch` only for the specific URLs you decide to cite.
- If you need faster multi-source synthesis, load `perplexity-search`.

3) Write the report:
- include links for each major claim
- include: trend summary, intent breakdown, content gaps, and 1-3 outlines

## Activation Examples

Use this skill for prompts like:
- "Research current trends and give me 3 article outline ideas about <topic>"
- "Do a content gap analysis for <topic> and propose angles"
- "What's the search intent behind queries like <list>?"
- "Give me a 2026 trend report for <topic> with sources"

## References

- Detailed workflow + required header: `HOW_TO_USE.md`
- Sample inputs: `sample_input.json`, `expected_output.json`
- Optional Python helpers: `intent_analyzer.py`, `trend_analyzer.py`, `outline_generator.py`
