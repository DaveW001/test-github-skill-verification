# Stage 2 Independent Plan Review

## Verdict

**BLOCKED** — the plan is not execution-ready. The blocking defects are in the plan and metadata, not an instruction-file remediation finding.

## Reviewer independence

- Plan creator: `root` on `gpt-5.6-sol`
- Reviewer: `conductor-plan-reviewer` on `gpt-5.6-terra`
- Gate: PASS — identities and models differ.

## Evidence reviewed

- `C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\baseline-report-2026-07-31-170000.md` — standalone `PASS` verdict present.
- `C:\development\opencode\.conductor\tracks\20260731-agents-md-cross-harness-remediation\spec.md`, `plan.md`, and `metadata.json`.
- OpenCode/Codex global instructions, agent-writer skill and both references, and the three OpenCode standards documents.
- Read-only dry runs: target-path existence/size inventory; redacted config-key inventory; installed OpenCode CLI help; official OpenCode agent/config documentation; and Conductor anomaly-schema inspection. No target AGENTS/config/skill file was edited and no credential value was intentionally read or recorded.

## Blocking findings

### B1 — Stage 2 status contract is internally inconsistent

Plan task 0.2 accepts only `metadata.json.review_status == EXECUTION_READY`, while this Stage 2 handoff requires `accepted` or `blocked`. The current metadata value is `pending`. The executor therefore has no single valid status to test.

**Required plan repair:** choose and document one status vocabulary, use it consistently in task 0.2, phase exit criteria, metadata template/fields, and the validation script. For this review, use `blocked`; after remediation, use `accepted` (or revise the requester contract before rerunning review).

### B2 — Task inventory and metadata progress are wrong

`plan.md` contains 15 numbered tasks (0.1–0.2, 1.1–1.2, 2.1–2.3, 3.1–3.3, 4.1–4.3, F.1–F.2), but `metadata.json.progress.totalTasks` is 17. This defeats the Final Phase acceptance check that metadata/ledgers agree.

**Required plan repair:** set the count to the actual tracked total and name which deferred work, if any, is excluded. Add a deterministic task-ID/count check to the final validator.

### B3 — Pipeline classification understates configuration/credential risk

Metadata declares `track_type: bookkeeping`, `classification: certain`, and the bookkeeping path, but task 4.1 changes an authentication-bearing global configuration field. The Pipeline policy says automatic bookkeeping selection is not available when secrets or shared infrastructure are touched. The plan also does not identify the one approved provider field and its environment-variable name.

**Required plan repair:** set `classification: uncertain` and pause for pipeline determination/authorization, or select the applicable higher-risk path with recorded rationale. Name the exact JSONC property and the exact existing `.env` variable name; use OpenCode's documented `{env:VARIABLE_NAME}` syntax. State that `.env` is backup/read-only in this task and its value is never rewritten, printed, compared, or placed in a report.

### B4 — Backup scope is not an executable, complete contract

Task 1.1 says to back up “every target file,” but the plan never supplies a closed manifest of pre-existing files versus created files. Later tasks include global configuration, five project instruction files, skill references, three standards documents, and new modules/runbook/script. A manifest cannot prove completeness from this wording, and a new file has no backup pre-image.

**Required plan repair:** add a closed target table with absolute path, operation (`modify`/`create`), owner, and rollback action. Make task 1.1 create a pre-edit SHA-256 backup only for `modify` entries and record `created-no-preimage` for `create` entries. Preserve and compare pre-existing dirty Git state before and after each repository-scoped edit.

### B5 — The authoritative acceptance checks are not deterministic enough

Several task checks are prose predicates rather than bounded executable checks: “contains … rules,” “compare extracted rules,” “correct controls,” “single canonical owner,” “skill smoke check,” and “selected project commands do not disappear.” Task 3.2's unspecified smoke check could invoke a model and create cost rather than prove local parsing. Task 4.3 requires a validator that has not yet been specified and uses its own exit code as the sole proof.

**Required plan repair:** for every task, add one named acceptance harness/command with an expected exit code and exact report path; keep exploratory comparisons under diagnostics. The new validator must parse JSONC without emitting scalar configuration values, resolve every local reference relative to its declared root, check the closed target/ownership matrix, reject deprecated active permission forms, and fail on an inline credential in the specifically approved field. Include a read-only negative-fixture/self-test for each check so a false-green script cannot be its own only evidence.

### B6 — Agent-frontmatter migration rule is over-broad and conflicts with current OpenCode semantics

Task 3.1 requires that no active template contain a `tools:` key. Current OpenCode documentation labels agent `tools` configuration deprecated in general, but still documents `tools.skill: false` as the mechanism to disable skills; the current templates instead use deprecated capability entries (`tools.write`, `tools.edit`, `tools.bash`). The plan must distinguish the deprecated capability map from the narrowly documented tool-disable exception, rather than mechanically rejecting every `tools:` occurrence. It must reject plural `permissions:` and `write: allow`, while retaining singular `permission:` with `edit`, `bash`, `task`, and `skill` controls.

**Required plan repair:** define an explicit frontmatter lint policy and fixtures: reject `permissions:`, `tools.write`, `tools.edit`, `tools.bash`, and `permission.write`; require `permission.edit`, `permission.bash`, and `permission.task` for the applicable template type. Treat any retained `tools.skill: false` as an intentional, documented exception only after local CLI/current-doc verification.

### B7 — OpenCode instruction wiring is assumed, not proved

Task 2.3 only requires JSONC validation and list inspection. That cannot show that the active global `opencode.jsonc` accepts the configured instruction paths, expands intended files, loads the intended core exactly once, and leaves specialized documents trigger-based. OpenCode combines configured `instructions` with `AGENTS.md`; a reference text in an adapter is not automatically parsed.

**Required plan repair:** name the exact `instructions` entries and add a redacted, bounded effective-config check plus a fresh-process/read-only harness that verifies resolved paths, uniqueness, and absence of specialized modules from always-on instructions. Do not use a conversational model response as acceptance evidence.

## Non-blocking but required plan clarifications

- Every command must include a concrete timeout/noninteractive form, including JSONC parsing, Git inspection, and CLI configuration inspection; the plan currently names no executable commands for most tasks.
- Task 2.1/2.2 byte ceilings must be diagnostic budget limits, not proof that safety rules survived extraction. Require a source-to-destination rule matrix with an allowlisted always-on set.
- Task 1.2 recovery must list the seven created modules and remove only paths marked `created-no-preimage`; it must not broadly remove the directory.
- Task 4.1 must not scan all config values or depend on matching the prior secret value. Inspect property type and the exact `{env:...}` reference only, then test only that the variable name is defined in the central `.env` without outputting its value.
- Task 4.2 needs a project-by-project source-to-destination command/constraint matrix before editing; headings alone are not a preservation test.
- Final validation must check that no `tools:` capability map or plural `permissions:` remains in the active agent templates, that all pointers resolve under their stated roots, and that backups/rollback records cover exactly the closed target table.

## Acceptance condition for a re-review

Revise `plan.md` and `metadata.json` to resolve B1–B7, preserve this report as historical evidence, then repeat Stage 2 with a different reviewer identity and model. Do not begin Phase 1 while any blocker remains.
