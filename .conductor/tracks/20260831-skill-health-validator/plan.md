# Plan: Skill Health Validator (Revised)

## Phase 0 — Setup & Preconditions

Implementation cannot start until a fresh independent review of this corrected plan ends `EXECUTION_READY`.

- [ ] **T0.1 Reconcile authority** — Compare `20260716-skill-health-validator-scope-fix`, `20260801-skill-health-validator`, and this track; document one authoritative scope and mark the other tracks superseded/deferred without deleting history. **Authoritative acceptance check:** `pwsh -NoProfile -NonInteractive -Command "$p='C:\development\opencode\.conductor\tracks-ledger.md'; $s=Get-Content -Raw -LiteralPath $p; if (([regex]::Matches($s,'skill-health-validator')).Count -ne 3) { exit 1 }; exit 0"` exits 0 after the ledger records the three distinct dispositions.
- [ ] **T0.2 Rebuild baseline evidence** — Replace the abbreviated baseline with exact bounded commands, working directory, exit codes, outputs, and pass/fail totals for all preflight roots and Codex target detection. **Authoritative acceptance check:** `pwsh -NoProfile -NonInteractive -File 'C:\development\opencode\scripts\validate-skill-health.tests.ps1' -BaselineOnly` exits 0 and reports `Verdict=PASS` plus `ChecksPassed=7`.

## Phase 1 — RED fixture tests

- [ ] **T1.1 Create fixture harness** — Create `C:\development\opencode\scripts\validate-skill-health.tests.ps1` with isolated roots and no live-root writes. **Authoritative acceptance check:** `pwsh -NoProfile -NonInteractive -File 'C:\development\opencode\scripts\validate-skill-health.tests.ps1' -FixtureOnly -Case fixture-isolation` exits 0 with `Case=fixture-isolation Result=PASS`.
- [ ] **T1.2 Encode safety acceptance tests** — Add cases for frontmatter, curated index, explicit rename, parent junction, unexpected topology, self-reference, reparse-only cleanup, real-directory retention, preflight, report, and CSV semantics. **Authoritative acceptance check:** the same harness with `-FixtureOnly -ExpectRed` exits nonzero and reports only expected behavioral assertion failures, not parser/setup failures.
- [ ] **T1.3 RED gate** — Run the exact fixture command once and record failing case names mapped to criteria. **Authoritative acceptance check:** `pwsh -NoProfile -NonInteractive -File 'C:\development\opencode\scripts\validate-skill-health.tests.ps1' -FixtureOnly -ExpectRed` returns a nonzero exit with `RedState=True`.

## Phase 2 — Implementation and scheduler integration

- [ ] **T2.1 Implement bounded validator** — Create `C:\development\opencode\scripts\validate-skill-health.ps1` with fail-closed preflight, union inventory, typed events, no live Codex child operations, reparse-only Agents cleanup, backups, and report/log generation. **Authoritative acceptance check:** `pwsh -NoProfile -NonInteractive -File 'C:\development\opencode\scripts\validate-skill-health.tests.ps1' -FixtureOnly` exits 0 with `Failed=0`.
- [ ] **T2.2 Migrate launcher safely** — Back up `C:\development\_shared-scripts\skill-health-validator-quiet.ps1` and `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md`, then update the launcher to invoke the validated script without changing the scheduled job's schedule/scope/workdir/timeout. **Authoritative acceptance check:** a structural job check reads `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\development-88876ee600f5\jobs\development-skill-health-validator.json` and returns `schedule=0 6 * * *`, `workdir=C:\development`, `timeoutSeconds=300`, and the launcher path.
- [ ] **T2.3 Validate rollback package** — Verify hashes and restore the launcher/index/report/log into an isolated temp copy, never live roots. **Authoritative acceptance check:** `pwsh -NoProfile -NonInteractive -File 'C:\development\opencode\scripts\validate-skill-health.tests.ps1' -FixtureOnly -Case rollback` exits 0 with `RestoredHashMatch=True`.

## Final Phase — Validation & Handover

- [ ] **T3.1 GREEN and regression tests** — Run `pwsh -NoProfile -NonInteractive -File 'C:\development\opencode\scripts\validate-skill-health.tests.ps1' -FixtureOnly`. **Authoritative acceptance check:** exit code 0 and exact `Failed=0`.
- [ ] **T3.2 Live dry-run** — Run `pwsh -NoProfile -NonInteractive -File 'C:\development\opencode\scripts\validate-skill-health.ps1' -WhatIf` against the live roots. **Authoritative acceptance check:** pre/post hashes and junction metadata are identical and stdout contains exactly the five required output-contract lines.
- [ ] **T3.3 Closeout docs** — Write execution, validation, and documentation logs; Upsert row for this track in both `C:\development\opencode\.conductor\tracks.md` and `C:\development\opencode\.conductor\tracks-ledger.md`. **Authoritative acceptance check:** a structural closeout command finds exactly one current row in each ledger, every non-deferred checkbox is `[x]`, and all claimed artifacts exist.

## Risks / mitigations

1. Junction target deletion: reparse-only type gate, target metadata backup, `cmd /c rmdir`, fixture proof.
2. Curated-index false positives: active-union inventory and no missing-entry flags for valid vault skills.
3. Scheduled job drift: exact JSON structural check and launcher backup/rollback.

**First task after fresh independent review:** T0.1.
