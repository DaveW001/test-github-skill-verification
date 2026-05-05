# Track Spec — Lazy Skill Discovery Regression

## Problem Statement

In current OpenCode sessions, lazy-loaded skills (especially Outlook/email skills such as `outlook-email-search` and `outlook-inbox-triage`) are not discoverable/loadable via `skill_find` and `skill_use`.

Observed behavior in-session:
- `skill_find "outlook"` → 0 matches
- `skill_find "email"` → 0 matches
- `skill_find "*"` → only 4 skills: `conductor`, `git_push`, `osgrep`, `perplexity_search`
- `skill_use` for Outlook skills returns not found

This blocks Outlook workflows that were previously migrated to Graph PowerShell and documented in prior tracks.

## Context

- Prior completed track: `20260501-skill-token-optimization` (lazy-load architecture with `@zenobius/opencode-skillful`)
- Current runtime still shows only native/core skills even though plugin is configured
- Current config files observed:
  - `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` includes `"@zenobius/opencode-skillful"`
  - `C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json` points to `C:\Users\DaveWitkin\.opencode-lazy-vault`
- Lazy vault exists and is populated (~49 skill folders), including:
  - `outlook-email-search\SKILL.md`
  - `outlook-inbox-triage\SKILL.md`
  - multiple email/calendar/google skills

## Scope

### In Scope
- Diagnose why skill discovery sees only 4 native skills.
- Determine whether failure is caused by plugin load failure, runtime/tooling incompatibility, config path mismatch, skill parser rejection, or stale process state.
- Produce a safe remediation plan and verification checklist.
- Update documentation impacted by root cause.

### Out of Scope
- Rewriting Outlook skill logic/content unless parser failures require minimal metadata fixes.
- Any production application code unrelated to skill discovery.

## Requirements

### R1 — Reproducibility
- [ ] Capture a deterministic reproduction protocol for the failure in a fresh session.
- [ ] Record expected vs actual output for `skill_find` and `skill_use`.

### R2 — Root-Cause Isolation
- [ ] Verify plugin registration, load health, and startup behavior.
- [ ] Validate `.opencode-skillful.json` semantics against plugin expectations.
- [ ] Confirm lazy-vault path visibility/permissions for OpenCode runtime context.
- [ ] Test whether parser rejects lazy skills (frontmatter or schema drift).
- [ ] Test whether discovery is constrained to system-injected `available_skills` rather than plugin source.

### R3 — Remediation
- [ ] Define minimal-risk fix(es) to restore lazy skill discovery.
- [ ] Include rollback steps if a fix regresses prompt/token optimization.

### R4 — Validation
- [ ] `skill_find "email"` returns email-related lazy skills.
- [ ] `skill_find "outlook"` returns Outlook lazy skills.
- [ ] `skill_use "outlook-email-search"` loads successfully.
- [ ] `skill_use "outlook-inbox-triage"` loads successfully.
- [ ] `skill_find "*"` includes significantly more than 4 skills.

## Risks

- Plugin API/behavior changed since migration track; docs may be stale.
- Runtime session may cache skill index and ignore config changes until full restart.
- Skill naming normalization differences (hyphen vs underscore) can cause false negatives.
- Over-correcting by moving skills back to native folder would increase system-prompt tokens.

## Dependencies

- OpenCode runtime/plugin loader behavior for `@zenobius/opencode-skillful`
- Local filesystem path availability: `C:\Users\DaveWitkin\.opencode-lazy-vault`
- Skill metadata compatibility with current loader/parser

## Success Criteria

This track is complete when lazy skill discovery/loading is restored and validated for Outlook/email skills without regressing the low-token architecture.
