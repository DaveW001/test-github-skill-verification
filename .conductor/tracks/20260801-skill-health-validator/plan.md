# Plan

`plan.md` is the authoritative source of truth for execution progress.

## Outcome, Constraints, and Definition of Done

### Goal / outcome

Deliver the scheduled-job implementation and deterministic fixture-based checks for the Skill Health Validator described in `spec.md`, without changing production application code or mutating the live skill surfaces during tests.

### Constraints / non-goals

- The implementation path is authoritative: `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md`. It must not create per-skill Codex junctions when the Codex root targets the lazy vault.
- Live cleanup is consequential filesystem mutation. Only confirmed orphan reparse-point links may be auto-removed with `cmd /c rmdir`; real directories are always flagged and left in place. Ambiguous collisions or unexpected root topology must stop the affected phase and be surfaced rather than guessed.
- Existing reports are historical evidence, not a source of truth. Do not erase the log or rewrite the global index unless the precise stale-name replacement rule is satisfied.
- No credentials, network calls, publication, deployment, or schedule registration are in scope.
- The evidence-backed rename map is explicitly empty for this track; no inferred rename may be edited.
- The archive source is the immediate child names of `C:\Users\DaveWitkin\.config\opencode\_archived_skills`; only an Agents reparse-point child with the same name and a target outside the archive is a removable orphan.

### Definition of done

- The validator artifact and deterministic checks exist at exact paths chosen by the executor and are documented in the execution log.
- The required report and CSV output contracts, parent-junction guard, archive deletion safety, and idempotency checks pass.
- Independent review is `EXECUTION_READY`; validation reports zero blocking findings; Conductor metadata and ledgers agree.

## Phase 0: Setup & Preconditions

1. - [x] 0.1 Mandatory Baseline: capture the pre-change state.
   - Files: `.conductor/tracks/20260801-skill-health-validator/baseline-report-2026-08-01-000000.md`
   - Authoritative acceptance check: Read the baseline and confirm it contains `**Verdict**: PASS`; expected output: `True`.

2. - [x] 0.2 Independent Plan Review: review this plan with a different agent identity and model.
   - Files: `.conductor/tracks/20260801-skill-health-validator/review-report-<timestamp>.md`, `.conductor/tracks/20260801-skill-health-validator/review-diff-summary-<timestamp>.md`, `metadata.json`
   - Prerequisites: `0.1`.
   - Body requirements: Check that the plan resolves the parent-junction architecture conflict, uses safe deletion semantics, defines deterministic acceptance checks, and preserves the exact output contract. Record creator/reviewer identities and models.
   - Authoritative acceptance check: `review-report-2026-08-01-003000.md` contains `EXECUTION_READY` and `Blocking findings: 0`; expected output: `True`.
   - Error recovery: unresolved blocking finding keeps the track blocked; revise only documentation artifacts and obtain a fresh independent review.

## Phase 1: Implementation

1. - [ ] 1.1 Back up and update the authoritative scheduled-job validator prompt without changing application source.
   - Files: `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md`; `.conductor/tracks/20260801-skill-health-validator\backups\skill-health-validator.md.<timestamp>.bak`; `.conductor/tracks/20260801-skill-health-validator\tests\prompt-contract.ps1`; `.conductor/tracks/20260801-skill-health-validator/execution-log-<date>.md`
   - Prerequisites: `0.2` is `EXECUTION_READY`.
   - Body requirements: Preserve current production wiring: the scheduler JSON invokes `C:\development\_shared-scripts\skill-health-validator-quiet.ps1`, which reads the prompt and passes its contents to `C:\development\_shared-scripts\opencode-run-safe.ps1 --title "Skill Health Validator" -- $prompt`. The literal `opencode run "Read and execute the exact instructions in C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md"` is historical scheduler-command evidence only, not the current executable wrapper. Encode the five checks, preflight, empty rename map, parent-junction hard stop for every child operation including cleanup, cleanup-only Agents behavior, exact report template, CSV semantics, idempotency, and exact five-line summary. Preflight failure uses the five-line contract with `Status: issues`, zero counts, and no report/log overwrite.
   - Command: `& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoProfile -NonInteractive -ExecutionPolicy Bypass -File 'C:\development\_shared-scripts\skill-health-validator-quiet.ps1'` (bounded diagnostic only; do not invoke during planning).
   - Authoritative acceptance check: Run `& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoProfile -NonInteractive -ExecutionPolicy Bypass -File 'C:\development\opencode\.conductor\tracks\20260801-skill-health-validator\tests\prompt-contract.ps1' -PromptPath 'C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md'`; expected output: `PromptContract: PASS` and exit code 0. The parser must validate clause/order presence, not isolated headings: Codex parent mode suppresses all child operations, `cmd /c rmdir` is Agents-reparse-only, real directories are retained, empty rename map, exact report template, CSV semantics, five stdout lines, and preflight failure behavior.
   - Error recovery: If the authoritative prompt or launcher is unavailable, restore the backup, record the blocker, and do not invent a new scheduler integration. The backup hash verifies rollback integrity; the prompt-contract parser verifies the revised prompt before a scheduled run. Rollback is `Copy-Item -LiteralPath <backup> -Destination 'C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md' -Force`.

2. - [ ] 1.2 Add isolated deterministic fixtures/checks at `.conductor/tracks/20260801-skill-health-validator/fixtures/` and `.conductor/tracks/20260801-skill-health-validator/tests/skill-health-validator-fixture.ps1`.
   - Files: `.conductor/tracks/20260801-skill-health-validator/fixtures/`, `.conductor/tracks/20260801-skill-health-validator/tests/skill-health-validator-fixture.ps1`; no live-surface deletion.
   - Prerequisites: `1.1`.
   - Body requirements: Assert frontmatter is flag-only; empty rename map and missing/stale index semantics; parent junction suppresses every Codex child operation including cleanup; unexpected live Codex topology stops; legacy Codex fixture cleanup is also reparse-only with real directories retained; Agents reparse points are removed with `rmdir`; real directories remain; the literal report template and counts; CSV header/date replacement semantics; exactly five stdout lines with concrete status values; preflight path matrix; and second-run normalized report/index/filesystem equivalence.
   - Command: `& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoProfile -NonInteractive -ExecutionPolicy Bypass -File 'C:\development\opencode\.conductor\tracks\20260801-skill-health-validator\tests\skill-health-validator-fixture.ps1' -FixtureRoot 'C:\development\opencode\.conductor\tracks\20260801-skill-health-validator\fixtures'`
   - Authoritative acceptance check: The harness output contains `0 failed` and named cases `parent-junction-zero-child-ops`, `legacy-codex-child-creation-fixture-only`, `legacy-codex-archive-reparse-only`, `unexpected-codex-topology-stop`, `preflight-stop`, `agents-root-absent-healthy`, `frontmatter`, `archive-reparse-only`, `index-empty-rename-map`, `report-template`, `stdout-contract`, `csv-same-date-retain-or-replace`, and `idempotency`; expected output: `0 failed`.
   - Error recovery: Keep failing fixtures isolated, classify unrelated environment failures, and stop before touching live paths.

## Final Phase: Validation & Handover

1. - [ ] F.1 Run the validator/fixture checks and verify artifacts, output contracts, and Conductor synchronization.
   - Files: implementation artifact, generated report/log paths, `.conductor/tracks/20260801-skill-health-validator/execution-log-<date>.md`, `metadata.json`, `.conductor/tracks.md`, `.conductor/tracks-ledger.md` if used.
   - Prerequisites: `1.1`, `1.2`.
   - Body requirements: Record skipped stages and any live-surface mutations; verify no Codex child operation exists under parent-junction mode, today's CSV row is unique, and the console summary is exact. Stage 7 reports closeout readiness; the orchestrator confirms terminal closeout only after Stage 9.
   - Authoritative acceptance check: Re-run the exact fixture command from Task 1.2 from `C:\development\opencode`; require exit code 0, `0 failed`, and a machine-readable pass record for every named case (`parent-junction-zero-child-ops`, `legacy-codex-child-creation-fixture-only`, `legacy-codex-archive-reparse-only`, `unexpected-codex-topology-stop`, `preflight-stop`, `agents-root-absent-healthy`, `frontmatter`, `archive-reparse-only`, `index-empty-rename-map`, `report-template`, `stdout-contract`, `csv-same-date-retain-or-replace`, `idempotency`). Then inspect the generated artifacts and Conductor state as diagnostics. Stage 7's separate report must say `closeout readiness: ready`; terminal closeout remains post-Stage-9.
   - Error recovery: Route implementation failures to the executor; route plan/metadata drift to bookkeeping correction; stop on destructive or ambiguous filesystem findings.

Phase exit criteria: Every non-deferred plan task is `[x]`; validation passes; artifacts exist; logs record deviations/skips; metadata and ledgers agree; pipeline fields reflect the bookkeeping path.

## Pipeline Determination

- Track type: `bookkeeping`
- Production code changes: no
- Baseline: `PASS` (deterministic preflight/structural smoke check)
- Test framework: `none` for production code; fixture/static harness required for this validator artifact
- Risk: low because live cleanup is reparse-point-only; real directories and unexpected Codex topology are flag-and-stop cases
- Selected `pipeline_mode`: `bookkeeping`
- Selected path: `0 -> 1 -> 2 -> 5 -> 7 -> 9`
- Skipped stages: RED/Test Writing, RED gate, and Test Runner because this track changes skill/job/configuration artifacts rather than application behavior; conditional re-review/re-validation skipped unless review or validation finds a blocker.

Preflight matrix: required and readable are canonical skills, global index, reports directory, Codex root, vault root, archived-skills root, prompt, and report/log parent; `.agents\skills` is optional and absent is healthy. Any required failure emits the five-line `Status: issues` contract and preserves prior report/log files. The exact supplemental baseline command and its captured JSON output are recorded verbatim in `baseline-report-2026-08-01-000000.md`; it is guarded with `-ErrorAction SilentlyContinue`, enumerates only immediate children of listed containers, and never enumerates Codex children after parent-junction detection.

## Top 3 Implementation Risks + Mitigations

1. **Self-referential Codex junctions** — identify the parent target before any child operation and make parent-junction mode a hard no-create branch; stop on unexpected live topology.
2. **Unsafe archive cleanup** — inspect reparse attributes first; use `rmdir` for links; flag and retain real directories.
3. **False index repair or duplicate logs** — use an explicitly empty rename map, anchored table-row parsing, and an exact date-row existence check.

## First Task to Execute Immediately

After Stage 2 approval, locate the authoritative scheduled-job artifact and implement the parent-junction-safe validator behavior, recording the exact path before adding fixtures.
