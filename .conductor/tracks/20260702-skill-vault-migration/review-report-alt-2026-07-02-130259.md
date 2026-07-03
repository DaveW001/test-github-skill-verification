# Stage 3 Conditional Re-review (Alt): Skill Vault Migration

Timestamp: 2026-07-02-130259
Model: openai/gpt-5.5 (variant low)
Diversity check: satisfied. Stage 3 reviewer model openai/gpt-5.5 differs from immediately preceding Stage 2 reviewer opencode-go/minimax-m3. This is the only extra re-review pass (cap 1).

## Summary

Overall readiness after this pass: 94%. The plan is executable and rigorous enough for Stage 4 after one high-confidence fix applied directly to plan.md: task 5.3 now performs real metadata + tracks.md + tracks-ledger.md upserts and verifies exactly one entry in each index. No blocking items remain.

## Verification-snippet testing performed

- Confirmed Stage 2 PYTHONUTF8 fix behavior on a temp copy of nlm-skill after applying the planned two-field frontmatter replacement: quick_validate.py returned `Skill is valid!` and exit code 0.
- Confirmed current unmodified nlm-skill still fails quick_validate.py because of `version:`; this is expected before Phase 2.2 and proves the Phase 2.2 edit remains necessary.
- Confirmed `plan.md` no longer contains `<fill` placeholders and task 5.3 uses hardcoded metadata values.
- Dry-ran the reviewer-added task 5.3 bookkeeping logic on temp copies of tracks.md/tracks-ledger.md plus a temp metadata.json; the acceptance expression returned `True`.
- Inspected current native/vault inventory: all five target native folders exist; keep-native folders are explicitly named in the plan; enrich_meeting_notes and retrospective are absent from the vault pre-execution, matching Phase 2.4/2.5 creation tasks.

## Direct edits made

- Updated `C:\development\opencode\.conductor\tracks\20260702-skill-vault-migration\plan.md` task 5.3. Prior command wrote metadata.json but only commented that tracks.md/tracks-ledger.md should be upserted; acceptance only checked file existence. New command performs deterministic duplicate-removing upserts and acceptance checks exactly one matching track row and one ledger entry.

## Task-by-task ratings

| Phase | Task | Rating | Notes |
|---|---|---|---|
| Phase 0 | 0.1 Confirm native, vault, backup, validator, and config paths exist | Ready | Explicit paths and Boolean acceptance. Backup directory currently exists. |
| Phase 0 | 0.2 Confirm opencode-skillful base path points to lazy vault | Ready | Deterministic config read; non-goal to edit config is respected. |
| Phase 0 | 0.3 Confirm target native folders and keep-native folders exist | Ready | Explicitly protects all six native skills by name. |
| Phase 1 | 1.1 Back up all five native target folders and write backup-dir.txt | Ready | Backs up all five before edit/delete; acceptance checks SKILL.md presence and nonzero length. |
| Phase 1 | 1.2 Back up existing vault target folders or write nonexistence markers | Ready | Covers pre-existing vault state and missing-folder marker state. |
| Phase 2 | 2.1 Add frontmatter to knowledge_graph_query vault SKILL.md | Ready | Frontmatter is exactly name+description; description includes function and triggers; name matches folder. |
| Phase 2 | 2.2 Replace nlm-skill vault frontmatter with exactly two fields | Ready | Removes version; temp-copy quick_validate with PYTHONUTF8 succeeded after applying planned replacement. |
| Phase 2 | 2.3 Verify pptx-to-pdf-converter vault copy is valid and unchanged | Ready | No edit; frontmatter acceptance is exact and git diff diagnostic supports unversioned comparison. |
| Phase 2 | 2.4 Create vault enrich_meeting_notes from native backup and prepend frontmatter | Ready | Frontmatter is exactly name+description; description includes behavior and triggers; deletion remains gated later. |
| Phase 2 | 2.5 Create vault retrospective from native backup without content edits | Ready | Preserves body and verifies expected valid frontmatter. |
| Phase 3 | 3.1 Run quick_validate.py against all five vault folders | Ready | PYTHONUTF8 prefix present in command and acceptance; native deletion cannot proceed if validation fails. |
| Phase 3 | 3.2 Confirm each vault frontmatter block has exactly name and description | Ready | Uses anchored frontmatter regex and enforces exactly two nonblank fields. |
| Phase 4 | 4.1 Delete the five native target folders | Ready | Ordered after Phase 3; deletes only explicit target array. |
| Phase 4 | 4.2 Confirm exactly six keep-native folders remain | Ready | Strong inventory check; will catch extra or missing native folders. |
| Final | 5.1 Run deterministic skill_find/skill_use resolvability proxy | Ready | Deterministic proxy includes basePath, folder, frontmatter, and quick_validate; restart caveat is elsewhere documented. |
| Final | 5.2 Write execution log with restart caveat | Ready | Contains required restart caveat and validation summary. Minor style note: executor should still prefer bounded PowerShell and avoid interactive tools. |
| Final | 5.3 Synchronize Conductor bookkeeping | Ready after edit | Was Needs Work before this pass because index upsert was a comment and acceptance was shallow. Fixed directly and dry-run on temp copies returned True. |

## Residual observations / non-blocking cautions

1. The plan intentionally uses a deterministic proxy rather than live skill_find/skill_use because OpenCode available_skills is session-start cached; this is acceptable because the restart caveat is explicit in spec and task 5.2.
2. Several diagnostic git diff --no-index commands may return exit code 1 when differences are expected. They are diagnostics, not authoritative checks, so this is acceptable.
3. Task 2.4 and 2.5 stop if the vault folder already exists. Current inspection shows both are absent, so the tasks are executable as written.

## Top 3 priorities for executor

1. Do not delete native folders until Phase 3.1 and 3.2 both pass for all five vault copies.
2. Preserve the six keep-native folders exactly: conductor, conductor-pipeline, osgrep, perplexity-search, git-push, and skill-discovery.
3. Run task 5.3 exactly as updated and confirm the final acceptance check returns `True` with exactly one track row and one ledger entry.

## Overall verdict

Ready for execution. Readiness: 94%. No Blocking items remain.
