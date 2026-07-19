# Spec

## Goal

Audit and correct the **Skill Health Validator** instruction prompt so it checks the *real* skill store (the lazy vault, 82 dirs / 79 skills) instead of only the 7 always-on canonical skills, and so it aligns with the architecture runbook and the report's own "future health-check guidance." The validator is a daily scheduled job (`skill-health-validator`, 06:00) whose `run.command` reads and executes `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md`.

## Background — Verified Architecture (2026-07-16)

Authoritative runbook: `C:\development\opencode\docs\runbooks\codex-skill-architecture.md`.

| Surface | Path | Live state (verified) |
|---|---|---|
| Lazy vault (primary skill store) | `C:\Users\DaveWitkin\.opencode-lazy-vault` | **82 dirs** — 79 with `SKILL.md`, 3 without (`_archived_skills`, `.system`, `codex-primary-runtime` — all legitimate non-skill folders). 7 reparse-point children = native-backed always-on junctions. **0 self-referential junctions (clean).** |
| Codex skills | `C:\Users\DaveWitkin\.codex\skills` | **Parent junction → vault** (`IsReparsePoint=True`, target = vault). Healthy. |
| Canonical always-on | `C:\Users\DaveWitkin\.config\opencode\skill` | **7 skills**: conductor, conductor-pipeline, git-push, opencode-scheduler, osgrep, perplexity-search, skill-discovery. |
| Agents skills | `C:\Users\DaveWitkin\.agents\skills` | **Absent** (archived 2026-07-06 to `.agents\archive\skills-20260706-144958`). Intentionally not recreated. |
| Global index | `C:\development\opencode\docs\reference\global-skills-index.md` | Header explicitly says **"Historical index; not authoritative."** A *curated subset* (categories), NOT an exhaustive list of all 79 skills. |
| Report / log | `docs\reports\skill-health-latest.md`, `docs\reports\skill-health-log.csv` | Last real run 2026-05-05; latest report is a 2026-07-06 architecture snapshot, not a check run. |

Scheduled job definition: `C:\Users\DaveWitkin\.config\opencode\scheduler\scopes\development-88876ee600f5\jobs\development-skill-health-validator.json` (scope `development`, workdir `C:\development`, schedule `0 6 * * *`, timeout 300 s, quiet wrapper `C:\development\_shared-scripts\skill-health-validator-quiet.ps1`).

## Defect Register (evidence-based)

| ID | Severity | Defect | Evidence |
|---|---|---|---|
| **A** | **Critical** | **Scope mismatch.** Check 1 & Check 2 iterate "every subdirectory in the **canonical** skills path" = 7 skills. The real store is the **vault** (79 skills). | Prompt Check 1 line "For every subdirectory in the canonical skills path"; canonical dir has 7 entries; vault has 79 skills. |
| **B** | Medium | Check 2 treats the index as authoritative/exhaustive. It would flag every vault-only skill as `INDEX_STALE` (no canonical dir) and emit `INDEX_MISSING` noise. | Index header: "Historical index; not authoritative"; index lists a curated subset, not all 79. |
| **C** | Low | Check 4 / Check 3 reference `.agents\skills`, which is intentionally absent. Guards make it safe, but skip rule only covers `_`-prefix, not dot-folders (`.system`). | `.agents\skills` Test-Path = False; runbook archived 2026-07-06. |
| **D** | Non-issue (robustness) | 3 vault dirs lack `SKILL.md`. | All 3 are non-skill folders (`_archived_skills`, `.system`, `codex-primary-runtime`). Add dot-folder to skip rule for clarity. |
| **E** | Medium (latent) | **No self-referential junction check.** Runbook's future-checklist item #2 requires it; currently clean but unguarded. | Runbook "Health-check guidance" #2; live scan = 0 self-ref. |
| **F** | Low-Med | Preflight *detects* Codex parent-junction status but never *reports* it as a health assertion. | Prompt Preflight branches on it but emits no flag; runbook future-checklist #1. |
| **G** | Low | Report-template example says "41 skills" (stale count); pasted copy has encoding-corrupted chars (`â€"`, stray quotes). | On-disk file is clean (em-dash OK); only pasted text corrupted. |

## Requirements

- [ ] **R1 (Defect A):** Validator iterates the **vault** as the primary skill set, unioned with canonical and **deduped by resolved path** (canonical skills also appear in the vault as native-backed junctions). Check 1 frontmatter scan covers all ~79 skills.
- [ ] **R2 (Defect A):** Check 2 `INDEX_STALE` comparison uses the **union skill set** (vault ∪ canonical), not canonical-only, so vault-only skills are not falsely flagged stale.
- [ ] **R3 (Defect B):** Index is treated as a **curated, non-authoritative** subset: `INDEX_MISSING` is suppressed/downgraded (a skill absent from a curated index is not a defect); unambiguous known-rename stale-name auto-fix is retained (safe, precise row replace).
- [ ] **R4 (Defect E):** New check scans vault reparse-point children whose target equals their own path → flag `SELF_REFERENTIAL|<name>`. **Flag-only** (never auto-remove; runbook mandates `cmd /c rmdir` with backup).
- [ ] **R5 (Defect F):** Preflight asserts Codex parent-junction health: if `IsReparsePoint` and target ≠ vault → flag `CODEX_SURFACE_NOT_PARENT_JUNCTION` (manual review; no auto-fix). Healthy state recorded in report.
- [ ] **R6 (Defect C/D):** Skip rule extended to dot-folders (`.system`) alongside `_`-prefix; explicit note that `.agents\skills` is intentionally absent and must not be recreated.
- [ ] **R7 (Defect G):** Report template uses a clean em-dash, well-formed summary line, and a generic count placeholder (remove stale "41 skills" example).
- [ ] **R8:** Output Contract, Idempotency Rules, and Exclusions preserved; a manual dry-run of the revised prompt reports ~79 skills checked, 0 self-referential, Codex surface healthy, and no false `INDEX_STALE`/`INDEX_MISSING` spam.

## Non-Requirements

- [ ] Do NOT change the job schedule, timeout, scope, wrapper, or `run.command` pointer (the `.md` path stays the execution surface).
- [ ] Do NOT auto-create/recreate `.agents\skills`.
- [ ] Do NOT auto-fix frontmatter (Check 1 stays flag-only).
- [ ] Do NOT auto-remove any junction (self-referential or otherwise) — flag only.
- [ ] Do NOT rewrite the global index beyond precise known-rename row replacements.
- [ ] Do NOT change the architecture runbook (it is the input authority, not an output).

## Acceptance Criteria

- [ ] Revised `skill-health-validator.md` iterates vault ∪ canonical (deduped); a counted dry-run reports ~79 skills, not 7.
- [ ] Revised Check 2 produces **zero** false `INDEX_STALE` for vault-only skills and **zero** `INDEX_MISSING` flags against the curated index.
- [ ] New self-referential scan present and flag-only; Codex parent-junction assertion present.
- [ ] All defects A–G addressed or explicitly justified as no-op.
- [ ] `skill-health-log.csv` gains today's row (idempotent — no duplicate date row); `skill-health-latest.md` regenerates cleanly.
- [ ] All tasks in `plan.md` marked `[x]`; `metadata.json` status/progress synchronized.
