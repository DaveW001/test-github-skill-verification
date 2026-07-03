---
name: retrospective
description: Run structured retrospectives that capture what went well, what to improve, and how to codify lessons into durable skills, references, and protocols. Use when the user mentions retro, retrospective, post-mortem, lessons learned, what went well, or after a track/session/workstream completes.
---

# Retrospective

Run a structured retrospective that turns a finished (or blocked) piece of work into durable improvements. The output is a discoverable retro document plus a concrete codification plan that feeds skills, references, protocols, and the `.conductor\learnings\` folder.

## When to use

- After a Conductor track completes, is blocked, or is abandoned.
- After a recurring job misbehaves or a tool-layer failure recurs.
- At the end of a workstream, sprint, or notable session.
- Whenever the user says "retro", "what did we learn", "post-mortem", or "lessons learned".

## Workflow

### 1. Scope selection (require user choice)

A retro that tries to cover everything covers nothing. Propose scope options and require the user to choose before you start asking questions. Offer concrete, bounded scopes, for example:

- a single track (e.g., `conductor-pipeline-improvements-2026-06-30`)
- a recurring job and its last failure window
- a tool/workflow class (e.g., "PowerShell edit hazards" across the last 3 tracks)
- a calendar window (e.g., "everything this week")

Do not begin the questions until the user picks one scope. Record the chosen scope at the top of the retro.

### 2. Ask the six standard questions

Work through the six questions, in order, gathering concrete evidence (commands, file paths, diffs, timings) rather than vague impressions. The six questions are:

what went well / what could be improved / what to do differently next time / systemic issues / what we learned / how to codify

Guidance per question:

1. **What went well?** - behaviors, tooling, and decisions worth repeating. Be specific (which command, which gate).
2. **What could be improved?** - friction, rework, shallow checks, slow loops. Name the step that hurt.
3. **What to do differently next time?** - the actionable change, phrased so the next agent could apply it.
4. **Systemic issues?** - patterns that recur across tracks, not one-off mistakes. These are codification candidates.
5. **What did we learn?** - the distilled insight, independent of any single fix.
6. **How to codify?** - the durable home for the lesson (skill, reference, protocol, or `.conductor\learnings\`).

### 3. Produce the retro document

Use the standard output template below and write it to the artifact path in the next section.## Artifact path guidance

Write every retro to a discoverable, dated location so future agents and tracks can find it:

`C:\development\02-Kx-to-process\.conductor\retros\YYYY-MM-DD-<slug>.md`

Rules:
- `YYYY-MM-DD` is the retro date (capture once; do not recompute).
- `<slug>` is a short kebab-case label of the scope (e.g., `pipeline-mechanics`, `kg-weekly-sync-corruption`).
- Cross-link related tracks by track id.
- If the run spans midnight, record both dates in the document header.

## Standard output template

```markdown
# Retrospective: <scope>
Date: YYYY-MM-DD
Related tracks: <track-id list, or "none">

## Scope
<one paragraph: what was in scope, what was explicitly out of scope>

## What went well
- ...

## What could be improved
- ...

## What to do differently next time
- ...

## Systemic issues
- ...

## What we learned
- ...

## How to codify
- <lesson> -> <target skill/reference/protocol/learning>
```

## 4. Codify (close the loop)

A retro that is not codified is forgotten. For each systemic issue or lesson, propose a codification target and, if small and in-scope, apply it directly:

- **Skills** - new or updated `C:\Users\DaveWitkin\.config\opencode\skill\<skill>\SKILL.md` (e.g., this `retrospective` skill was created to codify the knowledge-capture loop).
- **References** - durable docs under a skill's `references\` folder (e.g., `conductor-pipeline\references\powershell-edit-hazards.md`).
- **Protocols / prompts** - updates to stage prompts or threshold policy.
- **Learnings** - one-off lessons that do not yet merit a full reference go to `.conductor\learnings\<YYYY-MM-DD>-<slug>.md`.

When codification would be a large effort, do not bolt it onto the retro; open a Conductor track for it and link the track id back in the retro's "How to codify" section.
## Worked seed example: 2026-06-30 pipeline mechanics retrospective

This skill was itself seeded by the 2026-06-30 pipeline-mechanics retrospective. That retro took scope = the Conductor Pipeline mechanics surface (prompt rigor, PowerShell edit hazards, mid-run authorization, knowledge-capture loop). Distilled lessons and their codification targets:

- **What went well:** the Stage 2/3 anti-laziness mandate and body-content verification caught shallow checks before execution; the backup-before-edit pattern prevented data loss on untracked global skill files.
- **What could be improved:** verification snippets sometimes asserted prose ("status: ok") instead of the tool's actual output (`"status": "ok"`); reviewer-added checks were not always dry-run against the real environment.
- **Systemic issues:** PowerShell edits repeatedly hit the same five hazards (parse vs correctness, line-number anchoring, list indentation bleed, regex on structural characters, session-spanning date drift); executors stopped the human for clearly-Tier-0 fixes, hurting throughput.
- **Codification:** five hazards -> `conductor-pipeline\references\powershell-edit-hazards.md`; snippet rigor -> `stage-prompts.md` Stage 1 + Stage 2/3 updates; Tier 0/1/2 model -> `threshold-policy.md#mid-run-authorization`; knowledge-capture loop -> this `retrospective` skill.
- **Flagged, not fixed:** the `skill_find` frontend returned 0 matches with garbage debug output; recorded as a follow-up for opencode-skillful/lazy-vault, not fixed inside the mechanics track.

That retro produced Conductor track `conductor-pipeline-improvements-2026-06-30` as its codification vehicle.

## Anti-patterns

- **Scope creep:** starting questions before the user picks a scope. Always require a choice first.
- **Vague lessons:** "be more careful" is not codifiable. Insist on the concrete change and its target home.
- **Burying the codify step:** if every lesson stays inside the retro doc, nothing changes. Promote at least one lesson to a skill/reference/protocol or open a track for it.
- **Fixing frontend bugs inside a retro:** a retro codifies lessons; it does not become a bug-fix track. Flag unrelated tooling issues as follow-ups.

## Notes

- Keep retros grounded in evidence (paths, commands, diffs). Opinions are fine, but attach them to an artifact.
- Reuse the captured date variable for the filename and the document header; do not recompute `Get-Date` mid-retro.
- This skill follows `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md`.