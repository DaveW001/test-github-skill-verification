---
name: perplexity-search
description: Perform web-grounded research with Perplexity (Sonar) via LiteLLM/OpenRouter and return answers with citations. Use for up-to-date facts, recent papers, and verifying claims beyond the model's training cutoff ("search the web", "latest", "2025", "find web sources for", "cite").
triggers:
  intent:
    - web-grounded research
    - factual verification
    - citation-backed answers
  user_phrases:
    - search the web
    - find web sources for
    - latest facts with sources
  file_context:
    extensions: [md, txt]
    paths: [docs/**, research/**]
  tool_context:
    before_tools: [webfetch, read]
    with_tools: [bash]
  error_context:
    - outdated model knowledge
    - no citation available
  priority: medium
  suggest_only: true
license: MIT license
compatibility: Requires internet access, Python 3.9+, `litellm`, and either `PERPLEXITYAI_API_KEY` or `OPENROUTER_API_KEY`.
metadata:
  skill-author: K-Dense Inc.
---

# Perplexity Search

Use Perplexity when you need **current, web-sourced answers** (with links) instead of best-effort offline recall.

## Decision Tree

Use this skill when the user asks for:
- "latest" / "recent" / "this year" updates, changing facts, product pricing, policy changes
- primary sources: papers, announcements, specs, changelogs, release notes
- verification: "is it true that...", "find web sources for", "cite this"

Do not use this skill when:
- the task is pure reasoning/math or code that doesn't require current web data
- the user needs you to run code/tests locally (use normal tools)

If the user provided specific URLs and only wants those analyzed, prefer `google_search` (with `urls`) or `webfetch` instead of broad search.

## Quick Start (CLI)

1) Preflight:
```bash
python scripts/perplexity_search.py --check-setup
```

2) Run a search:
```bash
python scripts/perplexity_search.py "What changed in <topic> in the last 6 months? Include source links."
```

3) Save structured output:
```bash
python scripts/perplexity_search.py "<query>" --output results.json
```

## Activation Examples

Use this skill for prompts like:
- "Find recent papers (2024-2026) about X and summarize the findings with citations"
- "What are the latest changes in Y since 2025? Link the release notes"
- "Verify this claim and give me 3 credible sources"

## Provider / Model Selection (Short)

Default:
- Use `sonar-pro` for most searches.

Escalate when needed:
- Use `sonar-pro-search` for multi-step research ("compare", "evaluate", "trace the history").
- Use `sonar-reasoning-pro` when you need explicit reasoning plus sources.

See `references/model_comparison.md` for details.

## Query Patterns That Work Well

- Add a time window: "past 6 months", "since 2025", "in 2024"
- Ask for sources explicitly: "include citations", "link the sources"
- Constrain the domain: "peer-reviewed", "RFC/spec", "vendor docs", "government"

See `references/search_strategies.md` for more.

## Gotchas / Guardrails

- Never paste API keys into chat logs; don't commit `.env` files.
- Prefer smaller models for simple lookups (cost control).
- If results look weak, rephrase the query with tighter scope and an explicit time range.

## Files In This Skill

- Script: `scripts/perplexity_search.py`
- Setup helper: `scripts/setup_env.py`
- Setup/security: `references/openrouter_setup.md`
- Query design: `references/search_strategies.md`
- Model guide: `references/model_comparison.md`
- Example env file: `assets/.env.example`
