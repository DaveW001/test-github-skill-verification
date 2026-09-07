# Plan: Skill Health Validator

## Phase 0 — Setup & Preconditions

Implementation cannot start until Stage 2 independent review is `EXECUTION_READY`.
Baseline: `C:\development\opencode\.conductor\baselines\baseline-report-2026-09-02-skill-health-validator.md` (`PASS`). The architecture runbook controls over conflicting legacy prompt instructions.

- [ ] **T0.1a Reconcile track authority.** Write `scope-reconciliation-2026-09-02.md` naming this track authoritative and documenting dispositions for `20260716-skill-health-validator-scope-fix` and `20260801-skill-health-validator`, without deleting history. **Authoritative acceptance check:** a line-anchored PowerShell check finds one exact disposition line for each track ID.
- [ ] **T0.1b Upsert ledger state.** Upsert exactly one current row in `C:\development\opencode\.conductor\tracks.md` and one canonical entry in `C:\development\opencode\.conductor\tracks-ledger.md`. **Authoritative acceptance check:** a structural PowerShell check finds one exact row/entry for each of the three track IDs and expected statuses.
- [ ] **T0.2 Rebuild pre-review baseline.** Parse current metadata, verify nonempty spec/plan and structural task IDs, verify all prerequisite paths and Codex parent target, and record exact commands, outputs, exit codes, and totals in a fresh baseline report. **Authoritative acceptance check:** the report ends with exactly `**Verdict: PASS**` and includes every probe's exit code.

## Phase 1 — RED fixture harness

- [ ] **T1.1 Create isolated harness shell.** Create `C:\development\opencode\scripts\validate-skill-health.tests.ps1`; mutable data may exist only under `C:\development\opencode\.conductor\tracks\20260831-skill-health-validator\fixtures`; reject paths equal to or beneath all live roots. **Authoritative acceptance check:** `pwsh -NoProfile -NonInteractive -File "C:\development\opencode\scripts\validate-skill-health.tests.ps1" -FixtureOnly -Case fixture-isolation` exits 0 and prints `Case=fixture-isolation Result=PASS`.
- [ ] **T1.2a Add inventory/index RED cases.** Cover union deduplication, exclusions, frontmatter rules, curated missing suppression, stale index names, and exact rename rows. **Authoritative acceptance check:** `... -FixtureOnly -Group inventory-index -ExpectRed` exits nonzero with only named behavioral failures.
- [ ] **T1.2b Add topology RED cases.** Cover healthy/wrong/missing/real Codex roots, self-reference, absent/type-invalid Agents root, junction-only cleanup, real/unknown retention; no test creates Codex children or an Agents root. **Authoritative acceptance check:** `... -FixtureOnly -Group topology -ExpectRed` exits nonzero with only named behavioral failures.
- [ ] **T1.2c Add persistence RED cases.** Cover exact report, CSV same-date replacement, duplicate prevention, no-write preflight, rollback hashes, and second-run idempotency. **Authoritative acceptance check:** `... -FixtureOnly -Group persistence -ExpectRed` exits nonzero with only named behavioral failures.
- [ ] **T1.3 Confirm valid RED state.** Run each RED group once and map failures to acceptance criteria. **Authoritative acceptance check:** each group reports `RedState=True` and no syntax/setup failure.

## Phase 2 — Implementation and scheduler integration

- [ ] **T2.1a Implement inventory/frontmatter/index core** in `C:\development\opencode\scripts\validate-skill-health.ps1`; no mutation beyond fixture persistence. **Authoritative acceptance check:** inventory-index fixture group exits 0 with `Failed=0`.
- [ ] **T2.1b Implement topology/archive policy** with Codex fail-closed checks, self-reference flags, absent Agents preservation, exact directory-junction detection, and `cmd /c rmdir` only for confirmed orphan junctions. **Authoritative acceptance check:** topology fixture group exits 0 with `Failed=0`.
- [ ] **T2.1c Implement persistence/idempotency** with backups, byte-difference report writes, same-date CSV replacement, event records, and exact console output. **Authoritative acceptance check:** persistence fixture group exits 0 with `Failed=0`.
- [ ] **T2.2a Migrate launcher safely.** Back up `C:\development\_shared-scripts\skill-health-validator-quiet.ps1` and `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md`; update effective delegation to the validated script without changing scheduler metadata. **Authoritative acceptance check:** scheduler-adapter fixture emits `DelegatesToValidatedImplementation=True`.
- [ ] **T2.2b Verify scheduler contract.** Parse `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\development-88876ee600f5\jobs\development-skill-health-validator.json` and assert `schedule=0 6 * * *`, `workdir=C:\development`, `timeoutSeconds=300`, and the unchanged launcher invocation. **Authoritative acceptance check:** bounded PowerShell command exits 0 only when all exact values match.
- [ ] **T2.3 Validate isolated rollback.** Restore fixture copies of launcher, prompt, index, report, CSV, and log from the backup manifest; never restore to live roots or recreate Agents. **Authoritative acceptance check:** rollback case emits `Launcher=True Prompt=True Index=True Report=True Csv=True Log=True LiveWriteCount=0`.

## Final Phase — Validation & Handover

- [ ] **T3.1 Run GREEN fixture suite.** **Authoritative acceptance check:** `pwsh -NoProfile -NonInteractive -File "C:\development\opencode\scripts\validate-skill-health.tests.ps1" -FixtureOnly` exits 0 and prints `Failed=0`.
- [ ] **T3.2 Prove live dry-run.** Snapshot hashes for index/report/CSV/launcher/prompt and topology metadata for Codex, vault junctions, and Agents; run implementation with `-WhatIf`; compare snapshots. **Authoritative acceptance check:** live-dry-run emits `FileHashesIdentical=True TopologyIdentical=True LiveWriteCount=0 StdoutContract=True`.
- [ ] **T3.3a Write readiness artifacts.** Write execution and validation logs, synchronize plan and metadata, and record Stage 9 readiness. **Authoritative acceptance check:** structural closeout check finds all non-deferred tasks complete, required artifacts present, and validator verdict `Ready to close`.
- [ ] **T3.3b Complete documentation/terminal closeout.** Write Stage 9 doc-update log or explicit waiver, post-doc validation if semantic, and upsert final rows in both ledgers. **Authoritative acceptance check:** line-anchored check proves one current ledger row each, matching metadata, and doc artifact or waiver.

## Risks and rollback

1. Junction deletion: confirmed reparse type, target snapshot, `cmd /c rmdir`, fixture proof; rollback is metadata-only for removed links.
2. Index false positives: active union plus curated-index semantics and exact-row rename map.
3. Scheduler drift: launcher backup plus exact JSON structural check.

**First task after independent review:** T0.1a.
