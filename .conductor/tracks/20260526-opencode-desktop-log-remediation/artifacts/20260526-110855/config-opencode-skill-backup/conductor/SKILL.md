---
name: conductor
description: Manage Context-Driven Development using the Conductor protocol. Use when user mentions conductor, tracks, specs, plans, status, or wants to scaffold structured context in .conductor/.
triggers:
  intent:
    - planning
    - conductor track management
    - project context scaffolding
  user_phrases:
    - create a conductor plan
    - start a track
    - show track status
  file_context:
    extensions: [md, json]
    paths: [.conductor/**, conductor/**]
  tool_context:
    before_tools: [read, write, edit]
    with_tools: [bash]
  error_context:
    - missing project plan
    - unclear implementation path
  priority: high
  suggest_only: true
compatibility: Works when operating inside a repo/worktree; reads and writes project context under .conductor/ (prefers .conductor/, can read conductor/ if it already exists).
---

# Conductor

Keep project intelligence (product, tech stack, workflow, and track state) in a predictable repo-local structure.

## When to Use

Use this skill when the user asks to:
- Initialize Conductor in a repo (create `.conductor/`)
- Start a new track (spec/plan/metadata + ledger update)
- Check progress/status of the active track
- Retrieve/share context for a track (spec + plan + repo context)
- Work "with Conductor" / "tracks" / "spec" / "plan"

## Activation Examples

- "Initialize Conductor for this repo and create the foundation files."
- "Start a new track for adding Stripe billing."
- "Show status for the active track and summarize progress."
- "Give me context for the active track (spec + plan) to hand off to another agent."

## Conventions (Short)

- Preferred directory: `.conductor/`
- Legacy fallback (read-only if already present): `conductor/`

## Completion Hygiene (Required)

- After finishing a task within an active track, immediately update the related `.conductor/tracks/<track-id>/` artifacts before closing work.
- At minimum, keep these current when task status changes:
  - `plan.md` checkboxes/status/blockers
  - `metadata.json` status/phase when applicable
  - Session handoff note for meaningful milestones (recommended)
- Never report a task "done" until Conductor status is synchronized.

### Completion Gate (Required Before Closing Any Track)

Before marking a track `complete`, verify ALL of the following:

1. **plan.md**: every non-deferred task checkbox is `[x]` or explicitly marked completed
2. **validation**: run the track's verification command (e.g., `validate-kg.py`) — must report **0 FAIL**
3. **artifacts**: every claimed created/modified/deleted file verified on disk
4. **logs**: execution log exists and records deviations, skipped items, and validation performed
5. **ledgers**: `tracks.md` and `tracks-ledger.md` both updated and agree on status/date

If **any check fails**, the track is NOT complete. Fix the gap or document it as an explicit deviation in the execution log.

## References (Templates)

This skill keeps templates and longer reference material out of `SKILL.md`.

- `references/templates/tracks-ledger.template.md`
- `references/templates/track-spec.template.md`
- `references/templates/track-plan.template.md`
- `references/templates/track-metadata.template.json`
- `references/templates/product.template.md`
- `references/templates/tech-stack.template.md`
- `references/templates/workflow.template.md`
- `references/templates/product-guidelines.template.md`
