# Planner Handoff — Skill Health Validator

**Prepared**: 2026-08-13
**Track**: `20260801-skill-health-validator`
**Disposition**: Execution-ready bookkeeping track; implementation remains for the Build agent.

## Evidence reviewed

- Authoritative architecture: `C:\development\opencode\docs\runbooks\codex-skill-architecture.md`.
- Authoritative scheduled-job prompt: `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md`.
- Current launcher: `C:\development\_shared-scripts\skill-health-validator-quiet.ps1` -> `opencode-run-safe.ps1`.
- Schedule: daily at `06:00`, timeout 300 seconds, hidden PowerShell invocation.
- Existing Conductor review: `review-report-2026-08-01-003000.md`, verdict `EXECUTION_READY`, zero blocking findings.

## Required implementation decisions

1. Treat the native `skill\` directory as the validator's canonical scope. Do not expand scope to the lazy vault or project-local/package-managed skills unless the track is explicitly revised and re-reviewed.
2. Detect the Codex root's reparse-point target before any child inspection or mutation. When it targets the lazy vault, suppress every Codex child operation, including archive cleanup and junction creation.
3. If Codex is not in the expected parent-junction topology, stop that live phase and flag it. Legacy child-junction creation is permitted only inside isolated fixtures, never as an implicit live repair.
4. Treat `.agents\skills` as optional and non-authoritative. An absent root is healthy; never recreate it. Cleanup may remove only a confirmed orphan reparse point, using `cmd /c rmdir`; retain and flag real directories.
5. Keep the rename map explicitly empty. Do not infer renames from index text; flag missing/stale index entries rather than adding or guessing mappings.
6. Preserve the exact report headings, UTF-8 output, CSV header, same-date replacement/retention semantics, and five-line stdout contract from `spec.md`.

## Main risks and checks

| Risk | Required guard | Fixture/check |
|---|---|---|
| Self-referential or destructive Codex mutation | Parent-junction hard stop before child operations | `parent-junction-zero-child-ops`, `unexpected-codex-topology-stop` |
| Deleting archived content | Reparse-only `rmdir`; real directories remain | `archive-reparse-only`, `legacy-codex-archive-reparse-only` |
| False index repair | Empty evidence-backed rename map; anchored row handling | `index-empty-rename-map` |
| Repeated daily execution drift | Normalize report/index/filesystem and retain one date row | `csv-same-date-retain-or-replace`, `idempotency` |

## Build-agent boundary

The Build agent may edit only the scheduled prompt and track-local fixtures/checks described in `plan.md`, with a timestamped backup and execution log. It must not modify application source, recreate `.agents\skills`, create Codex child junctions under the parent junction, or run destructive live cleanup during fixture validation.

## Validation handoff

Run the exact PowerShell fixture command in `plan.md` from `C:\development\opencode`. Require exit code 0, `0 failed`, all 13 named cases, exact report/CSV/stdout contracts, and synchronized Conductor artifacts before closeout.
