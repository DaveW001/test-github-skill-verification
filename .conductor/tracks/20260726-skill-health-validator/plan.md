# Plan

## Phase 0 - Setup & Preconditions

- [ ] **Review authoritative architecture and current job wiring.** Read `C:\development\opencode\docs\runbooks\codex-skill-architecture.md`, `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md`, `C:\development\_shared-scripts\skill-health-validator-quiet.ps1`, and the `skill-health-validator` entry in `C:\development\_shared-scripts\scheduler-registry.md` before editing.
  - Authoritative acceptance check: the implementation notes identify the Codex parent-junction rule, `.agents` archived policy, existing launcher path, and no-duplicate-job decision.
  - Diagnostic checks: `Test-Path` for all required paths; inspect the existing job with `get_job` from the `C:\development` scope.
  - Recovery: if any required path is absent, stop and report the exact missing path instead of creating substitute infrastructure.

- [ ] **Define the index authority/rename policy.** Identify whether any current canonical directory has a documented old-name mapping; only such a mapping may trigger a row-local string replacement. Treat all other absent/mismatched entries as flags.
  - Authoritative acceptance check: a written mapping or explicit “no safe rename mappings” result exists before index mutation logic is changed.
  - Diagnostic checks: compare canonical names with the index table and the architecture runbook; inspect current report flags.
  - Recovery: if a possible rename cannot be proven from repository evidence, leave the index unchanged and emit a flag.

## Phase 1 - Validator Hardening

- [ ] **Harden preflight and canonical enumeration** in `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md` (or the implementation artifact chosen by the Build agent), including readable-path checks, runtime date computation, `_` exclusion, and canonical-only scope.
  - Authoritative acceptance check: a controlled run stops with one concise reason for a missing/unreadable preflight dependency and otherwise reports exactly the eligible canonical skill count.
  - Diagnostic checks: enumerate canonical directories and inspect frontmatter delimiters/fields.
  - Recovery: preserve the existing report/log files when preflight fails; do not perform partial repairs.

- [ ] **Implement frontmatter validation as flag-only.** Validate directory/name equality, slug regex, and description length/non-empty constraints without changing `SKILL.md`.
  - Authoritative acceptance check: malformed fixtures produce `FRONTMATTER_ISSUE|...` flags and their source files have unchanged hashes.
  - Diagnostic checks: test missing delimiters, duplicate/missing fields, invalid names, empty descriptions, and descriptions over 1024 characters.
  - Recovery: treat parser ambiguity as a flag rather than guessing or rewriting YAML.

- [ ] **Implement safe index freshness handling.** Detect current canonical names, report missing/stale names, and only replace a proven old name within its exact table row; skip all index writes when no safe stale-name mapping exists.
  - Authoritative acceptance check: a fixture with one proven rename changes only the intended row, while an unknown stale name remains a flag and missing entries are not added.
  - Diagnostic checks: inspect `git diff -- C:\development\opencode\docs\reference\global-skills-index.md` and verify unrelated rows are byte-for-byte unchanged.
  - Recovery: if row boundaries or rename evidence are ambiguous, abort that replacement and record a manual flag.

- [ ] **Implement junction-aware surface consistency.** Resolve the Codex root reparse target, set the parent-junction state only on an exact vault target match, skip all Codex child creation in that state, and preserve the stated legacy behavior only when Codex is a real directory.
  - Authoritative acceptance check: on the current machine no `JUNCTION_CREATED|...|codex` event is emitted and no child is created beneath the Codex parent junction.
  - Diagnostic checks: inspect `Attributes`, `Target`, and child paths without following links for mutation decisions.
  - Recovery: if target resolution is unavailable or differs from the vault, stop the junction phase safely and flag the ambiguity; do not guess.

- [ ] **Harden archive hygiene removal.** Classify each matching Codex/Agents entry as a junction/reparse point versus a real directory before removal; use a junction-safe removal operation and never recurse through a link target. Respect the absent/archived `.agents` policy.
  - Authoritative acceptance check: a junction fixture is removed without deleting its target contents, and the event is recorded as `ORPHAN_REMOVED|<name>|<surface>`.
  - Diagnostic checks: verify target existence and post-removal path state; run a non-destructive archive fixture first.
  - Recovery: if an entry is a real non-orphan directory or classification fails, leave it in place and emit a manual flag.

- [ ] **Make report/log/output behavior deterministic.** Overwrite the latest Markdown report, create the CSV header when absent, suppress a duplicate row for today, calculate issues as auto-fixes plus flags, and emit the exact five-line console contract.
  - Authoritative acceptance check: two runs on the same fixture produce one date row and matching report counts, with output paths named `skill-health-latest.md` and `skill-health-log.csv`.
  - Diagnostic checks: parse Markdown section headings and CSV rows; capture stdout and compare each required label/order.
  - Recovery: write to temporary files and preserve the last valid report if a final write fails; report the failure concisely.

## Phase 2 - Verification & Integration

- [ ] **Run a controlled validation against the live surfaces.** Execute the validator non-interactively through the existing quiet launcher; capture report, CSV, stdout, and any index diff.
  - Authoritative acceptance check: the run ends with the exact output contract and no forbidden Codex child-junction operation.
  - Diagnostic checks: inspect the latest report, CSV tail, and scheduler job logs.
  - Recovery: if live cleanup would be destructive or the architecture state is ambiguous, use fixtures and leave live surfaces untouched.

- [ ] **Verify scheduler idempotency and registry alignment.** Confirm the existing job remains at `0 6 * * *` in the `C:\development` scope, then upsert the registry row only if the job configuration changed.
  - Authoritative acceptance check: `list_jobs` from `C:\development` shows exactly one `skill-health-validator` job and the registry agrees on schedule, workdir, and launcher.
  - Diagnostic checks: `get_job skill-health-validator`; inspect `C:\development\_shared-scripts\scheduler-registry.md`.
  - Recovery: do not create or delete jobs automatically; document drift for an explicit scheduler-management step.

## Final Phase - Validation & Handover

- [ ] Verify every non-deferred task in this plan is `[x]` and update `metadata.json` progress/status.
- [ ] Re-open each modified/created artifact and verify intended body content, not only headings.
- [ ] Record deviations, skipped destructive actions, fixture results, and validation commands in an execution/change log under this track.
- [ ] Verify report and CSV artifacts exist at the absolute paths specified in the spec.
- [ ] Verify `metadata.json` pipeline fields match the actually executed path and do not claim production-code tests that were not run.

## Task Safety Rules

- Any rename/move task must first verify the target does not exist; on collision, stop without overwrite.
- For structured reports, CSVs, and index tables with repeated rows, prefer a complete validated rewrite or row-anchored transformation rather than broad regex replacement.
- Do not use `Remove-Item -Recurse` or equivalent against a junction/reparse point.
