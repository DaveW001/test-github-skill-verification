---
name: youtube-shorts
description: Generate B2G YouTube Shorts scripts with a skeptical CIO ("Claire") review loop, evidence-first hooks, and visual prompt guidance.
compatibility: Requires Python 3.10+; Gemini CLI installed and authenticated; access to a content repo with knowledge-base inputs (configure via CONTENT_ROOT)
---

## What this skill does

Creates short-form (YouTube Shorts) scripts tailored for business-to-government (B2G) audiences, then runs an automated "Claire" CIO persona critique to catch buzzwords, weak evidence, and generic advice.

## When to use this skill (triggers)

Use this skill when the user asks for any of the following:

- A "YouTube Shorts" / "short form" script
- A B2G / government / public sector angle on a topic
- A punchy hook + tight 5-beat structure for retention
- A skeptical CIO / reviewer pass to de-fluff the script

## Quickstart

Run the interactive wizard:
```bash
python scripts/create_script.py
```

Run in non-interactive mode (topic, optional evidence):
```bash
python scripts/create_script.py "Zero Trust procurement" "OMB M-22-09"
```

Skip the automatic CIO review step:
```bash
python scripts/create_script.py "Modernizing legacy apps" --skip-review
```

## Expected repo layout (portable)

This skill pulls context from a content repository (e.g., "content-marketing") and expects a knowledge base file similar to:

- `knowledge-base/02_case_studies_and_performance/packaged-agile-company-profile.md`

To keep this skill portable across machines, set `CONTENT_ROOT` to the root of that repo before running.

See `references/02-compatibility-and-setup.md` for setup examples.

## Outputs

- Saves scripts under a topic slug folder (see `references/03-workflow-and-artifacts.md`)
- Naming convention: `sfXX-{slug}-script.md`
- Saves a timestamped Claire review file: `YYYY-MM-DD-HHMM-critic-review.md`

## Activation Examples

See `references/01-activation-examples.md`.
