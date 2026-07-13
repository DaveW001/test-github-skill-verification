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

### 1. Scope resolution (infer first, ask only if ambiguous)

A retro that tries to cover everything covers nothing. Resolve to a single bounded scope **before** asking any of the six questions, in this order:

**Step 1a - Try to infer scope from invocation context.** The message that triggered the skill - and any context the user already gave earlier in the session - usually implies the scope. Look for explicit signals:

- a named track id (e.g., `conductor-pipeline-improvements-2026-06-30`)
- a named repo, file, or path
- a time window ("this week", "the last session", "yesterday's deploy")
- a named tool, workflow, or recurring job ("PowerShell edit hazards", "the kg weekly sync")
- a described outcome or incident ("the build break", "the kg-weekly-sync corruption")

If the signals resolve to **one** clear scope, adopt it. Do not make the user re-choose what they already told you. State the inferred scope in one line (e.g., "Scope: the kg-weekly-sync corruption from 2026-06-29 - say the word if you meant something else") so the user can correct cheaply before you proceed. A one-line restatement is not a scope picker. When in doubt, prefer inferring from even a single explicit bounded signal (and stating it back) over defaulting to a scope picker.

**Step 1b - Offer choices only when context is genuinely ambiguous.** Ask the user to choose only when invocation context implies **two or more** competing scopes, or is too thin to resolve a single scope. When you must ask, offer concrete, bounded options (not open-ended), for example:

- a single track (e.g., `conductor-pipeline-improvements-2026-06-30`)
- a recurring job and its last failure window
- a tool/workflow class (e.g., "PowerShell edit hazards" across the last 3 tracks)
- a calendar window (e.g., "everything this week")

Do not begin the six questions until scope is resolved - either inferred-and-stated (1a) or user-chosen (1b). Record the resolved scope at the top of the retro and in the filename slug.
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

## Session mode (optional)

Most retros follow the workflow above: scope, six questions, document, codify. When the retro reviews a **coding session** (often the most recent work segment) and the user wants changes applied, use this optional extension. The `/retro` command implies a coding-session review, so it enters Session mode by default. In Session mode, the subsections below take precedence over Step 4 (Codify) detail and the Standard output template for this retro; base Steps 1-3 still apply as written.

### Interactive vs headless

**Interactive** (chatting with the user): follow Step 1 infer-first scope resolution; propose improvements before applying any edit, and apply only on confirmation or explicit opt-in.

**Headless** (`opencode run`): the user must pass scope, repo (if applicable), and audience in the prompt and opt into edits explicitly, e.g. `Run retro scope="last 2 hours" repo="C:/code/my-project" audience="team" apply_changes=true`. Do not ask questions; if required inputs are missing, fail gracefully listing the missing fields. Apply changes only when `apply_changes=true`; otherwise propose only.

### Gather evidence (when a repo is in scope)

Use the least-invasive inspection that covers the scope - never destructive commands:

- Git: `git status`, `git diff`, `git log` (with a window flag) when a repo is present.
- Files: recent specs, plans, or notes.
- Context folders: `.conductor/`, `conductor/`, or `.opencode/`.

If the user declines filesystem inspection, run the retro from the provided narrative and note the evidence limitation.

### Track the work (optional)

Prefer a Conductor track if one exists; otherwise use `todowrite`. Phase it to mirror the retro flow: (1) evidence and summary, (2) systemic improvements identified, (3) changes applied and validated.

### Apply-and-validate loop (permission model)

- **Default:** propose improvements and ask before editing.
- **Apply** when the user says "apply" (interactive) or passes `apply_changes=true` (headless).
- If a change spans global vs project scope, confirm the intended location before editing.
- For each applied change, record a validation step: skills/commands -> confirm OpenCode reloads them (offer a headless run to verify, and prefer it when available); scripts -> run a smoke test; docs -> re-open and confirm the expected content.

### Session output order

Present the retro in this order: Summary, What Changed, Systemic Improvements (by category), Changes Applied (with file paths), Validation (type per change), Conductor/Todo status.

## Worked seed example: 2026-06-30 pipeline mechanics retrospective

This skill was itself seeded by the 2026-06-30 pipeline-mechanics retrospective. That retro took scope = the Conductor Pipeline mechanics surface (prompt rigor, PowerShell edit hazards, mid-run authorization, knowledge-capture loop) - inferred from the invocation, stated back in one line, and adopted without correction. Distilled lessons and their codification targets:

- **What went well:** the Stage 2/3 anti-laziness mandate and body-content verification caught shallow checks before execution; the backup-before-edit pattern prevented data loss on untracked global skill files.
- **What could be improved:** verification snippets sometimes asserted prose ("status: ok") instead of the tool's actual output (`"status": "ok"`); reviewer-added checks were not always dry-run against the real environment.
- **Systemic issues:** PowerShell edits repeatedly hit the same five hazards (parse vs correctness, line-number anchoring, list indentation bleed, regex on structural characters, session-spanning date drift); executors stopped the human for clearly-Tier-0 fixes, hurting throughput.
- **Codification:** five hazards -> `conductor-pipeline\references\powershell-edit-hazards.md`; snippet rigor -> `stage-prompts.md` Stage 1 + Stage 2/3 updates; Tier 0/1/2 model -> `threshold-policy.md#mid-run-authorization`; knowledge-capture loop -> this `retrospective` skill.
- **Flagged, not fixed:** the `skill_find` frontend returned 0 matches with garbage debug output; recorded as a follow-up for opencode-skillful/lazy-vault, not fixed inside the mechanics track.

That retro produced Conductor track `conductor-pipeline-improvements-2026-06-30` as its codification vehicle.

## Anti-patterns

- **Scope creep:** starting the six questions before scope is resolved. Resolve to a single scope first - infer it from invocation context when one scope is clear, and only run a scope picker when context is genuinely ambiguous or competing.
- **Over-asking:** forcing a scope picker when the user already specified the scope in their message. If they named a track, window, repo, or incident, adopt it and state it back; don't make them re-choose.
- **Silent inference:** adopting a scope without stating it back in one line. Always restate the inferred scope so the user can correct cheaply before the six questions begin.
- **Vague lessons:** "be more careful" is not codifiable. Insist on the concrete change and its target home.
- **Burying the codify step:** if every lesson stays inside the retro doc, nothing changes. Promote at least one lesson to a skill/reference/protocol or open a track for it.
- **Fixing frontend bugs inside a retro:** a retro codifies lessons; it does not become a bug-fix track. Flag unrelated tooling issues as follow-ups.

## Notes

- Keep retros grounded in evidence (paths, commands, diffs). Opinions are fine, but attach them to an artifact.
- Reuse the captured date variable for the filename and the document header; do not recompute `Get-Date` mid-retro.
- This skill follows `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md`.