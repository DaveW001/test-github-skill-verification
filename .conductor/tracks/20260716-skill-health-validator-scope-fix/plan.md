# Plan

Track: `20260716-skill-health-validator-scope-fix`
Target file (single edit surface): `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md` (the prompt the scheduled job executes).
Supporting surfaces: `C:\development\opencode\docs\reports\skill-health-latest.md`, `C:\development\opencode\docs\reports\skill-health-log.csv`.

> **Planner note:** This track *plans* the edits; the Build/executor agent applies them. The instruction file is a `.md` prompt (config-style), not application code. Edits are string-anchored against the verified on-disk content (156 lines, clean em-dash).

## Phase 0 — Setup & Preconditions
- [x] Track dir + spec.md + plan.md + metadata.json created
- [x] Verified architecture facts captured in spec.md Background table

## Phase 1 — Fix the scope (Defect A, critical)

### Task 1.1 — Define the union skill set in Paths/Preflight
In `skill-health-validator.md`, add a "Skill set" definition that makes the **vault** primary and canonical secondary, deduped.
- Add to **Paths (constants)**:
  ```
  - **Vault (primary skill store)**: `C:\Users\DaveWitkin\.opencode-lazy-vault\`
  - **Canonical (always-on)**: `C:\Users\DaveWitkin\.config\opencode\skill\`
  - **Skill set for checks** = all child dirs of Vault ∪ Canonical that contain `SKILL.md`, skipping names starting with `_` OR `.`, deduped by resolved path.
  ```
- In **Runtime Values**, add:
  ```powershell
  $vaultRoot     = 'C:\Users\DaveWitkin\.opencode-lazy-vault'
  $canonicalRoot = 'C:\Users\DaveWitkin\.config\opencode\skill'
  # Build deduped skill set (resolved-path keyed)
  $skills = @{}
  foreach ($root in @($vaultRoot,$canonicalRoot)) {
    Get-ChildItem -LiteralPath $root -Directory -Force -ErrorAction SilentlyContinue |
      Where-Object { $_.Name -notmatch '^[_\.]' -and (Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md')) } |
      ForEach-Object { $rp = (Resolve-Path -LiteralPath $_.FullName).Path; if (-not $skills.ContainsKey($rp)) { $skills[$rp] = $_ } }
  }
  $skillDirs = @($skills.Values)
  ```
- **Authoritative acceptance check:** `Select-String -LiteralPath '<file>' -Pattern 'Skill set for checks'` returns a match AND the `$skills`/`$skillDirs` snippet exists verbatim.
- **Error recovery:** if the `Where-Object` anchor differs, locate the "## Runtime Values" heading and insert the block immediately after the `$TODAY` line.

### Task 1.2 — Reword Check 1 to use the union set
Change Check 1 opener from "For every subdirectory in the canonical skills path that contains a `SKILL.md` file (skip directories starting with `_`)" to "For every entry in `$skillDirs` (the Vault ∪ Canonical skill set defined above)".
- Update the skip note to: "skip names starting with `_` or `.`".
- **Authoritative acceptance check:** Check 1 body references `$skillDirs` and no longer contains the phrase "in the canonical skills path".
- **Diagnostic checks:** `Select-String -Pattern 'canonical skills path' -LiteralPath '<file>'` should return 0 matches inside Check 1.

### Task 1.3 — Fix Check 2 INDEX_STALE to compare against the union set
Change "For each skill name in the index that does NOT have a matching canonical directory" → "does NOT have a matching entry in `$skillDirs` (Vault ∪ Canonical, by name)".
- **Authoritative acceptance check:** Check 2 INDEX_STALE arm references `$skillDirs` / "Vault ∪ Canonical", not "canonical directory".
- **Idempotency:** precise wording replacement only; do not restructure the section.

## Phase 2 — Index authoritativeness (Defect B)

### Task 2.1 — Mark the index curated/non-authoritative in Check 2
Add a lead note to Check 2:
> The global index is a **curated, non-authoritative** subset (its own header says "Historical index; not authoritative"). It is NOT an exhaustive list of all skills. Therefore: do NOT emit `INDEX_MISSING` for skills absent from the index (a curated index omits skills by design), and only flag `INDEX_STALE` for an index entry that matches no skill in `$skillDirs`.
- Remove or downgrade the `INDEX_MISSING|<name>` recording rule to an INFO line that is **not counted** in the Flags total.
- Keep the stale-name auto-fix (precise row string-replace) for unambiguous known renames.
- **Authoritative acceptance check:** Check 2 contains "curated, non-authoritative" and the `INDEX_MISSING` rule is explicitly suppressed/not-counted.
- **Error recovery:** if the exact `INDEX_MISSING|<name>` sentence is absent, search for "do NOT add it" and replace that clause with the suppression note.

## Phase 3 — Add the missing architecture checks (Defects E, F)

### Task 3.1 — Add Check 3b: self-referential vault junction scan
Insert a new subsection after Check 3:
```
## Check 3b: Self-Referential Junction Scan
Scan Vault reparse-point children whose Target equals their own FullName:
  Get-ChildItem -LiteralPath $vaultRoot -Directory -Force |
    Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } |
    ForEach-Object { $t=(Get-Item -LiteralPath $_.FullName).Target; if($t -is [array]){$t=$t[0]}; if($t -eq $_.FullName){ "SELF_REFERENTIAL|$($_.Name)" } }
Action: FLAG ONLY as SELF_REFERENTIAL|<name>. NEVER auto-remove. Remediation per runbook = snapshot, then `cmd /c rmdir "<path>"` only after backup (see codex-skill-architecture.md "What if I find a self-referential junction?").
```
- **Authoritative acceptance check:** a "Check 3b: Self-Referential Junction Scan" heading exists and the action line says "FLAG ONLY" and "NEVER auto-remove".
- **Diagnostic checks:** running the scan snippet live must return empty (0 self-ref) on the current vault.

### Task 3.2 — Add Codex parent-junction health assertion (Preflight)
In Preflight, after computing `$isCodexParentJunction`, add:
```
If $isCodexParentJunction is FALSE -> record flag CODEX_SURFACE_NOT_PARENT_JUNCTION (manual review; do NOT auto-recreate the junction — recreating is destructive). If TRUE -> record as healthy in the report summary.
```
- **Authoritative acceptance check:** Preflight body contains `CODEX_SURFACE_NOT_PARENT_JUNCTION` and "do NOT auto-recreate".
- **Idempotency:** detection logic already exists; this only adds reporting.

## Phase 4 — Robustness & report template (Defects C, D, G)

### Task 4.1 — Extend skip rule + .agents note (Defect C/D)
- Everywhere the skip rule appears, ensure it reads "skip names starting with `_` or `.`".
- Add a one-line note under Paths: "`.agents\skills` is intentionally absent (archived 2026-07-06); do NOT recreate it. Its absence is healthy, not a defect."
- **Authoritative acceptance check:** `Select-String -Pattern 'do NOT recreate' -LiteralPath '<file>'` matches the `.agents` note; skip rule mentions the dot prefix.

### Task 4.2 — Clean up the report template (Defect G)
In the Check 5 report template:
- Ensure the title line uses a clean em-dash: `# Skill Health Report — <TODAY>` (the on-disk file is already clean; do NOT paste the corrupted `â€"` version).
- Replace the stale example summary "All 41 skills healthy" with a generic placeholder that references `<N>` skills checked (remove the hard-coded `41`).
- **Authoritative acceptance check:** report template contains `— <TODAY>` (em-dash) and no literal `41` in the summary example.
- **Error recovery:** if `41` is absent (already generic), no-op and note it.

## Phase 5 — Verification (manual dry-run of the revised prompt)

### Task 5.1 — Execute the revised validator once (dry-run) and capture counts
Run the validator logic against the live filesystem and record:
- total skills checked (expect ~79),
- Codex surface = parent-junction-to-vault (healthy),
- self-referential count (expect 0),
- false INDEX_STALE / INDEX_MISSING count (expect 0).
- **Authoritative acceptance check:** the run reports ~79 skills checked and 0 false index flags; `skill-health-log.csv` has exactly one row for today (no duplicate).
- **Diagnostic checks:** `(Get-Content skill-health-log.csv | Select-String (Get-Date -Format yyyy-MM-dd)).Count -eq 1`.

### Task 5.2 — Idempotency re-run
Run the validator a second time; confirm identical auto-fix/flag counts and no duplicate CSV row, no duplicate junctions, and the index unchanged when no renames found.
- **Authoritative acceptance check:** second run auto-fixes == first run auto-fixes; CSV still has one today-row.

## Final Phase — Validation & Handover
- [ ] Verify all non-deferred plan tasks above are checked `[x]`
- [ ] Verify `metadata.json` status/progress synchronized with plan completion
- [ ] Upsert row in `C:\development\opencode\.conductor\tracks-ledger.md` (Active Tracks) with final phase + date
- [ ] Create execution/change log noting deviations, skipped items, and the dry-run counts
- [ ] Re-open `skill-health-validator.md` and confirm R1–R8 acceptance strings from spec.md are present
- [ ] Confirm no application code was modified (only the `.md` prompt + report/log artifacts)

Checkbox states: `[ ]` pending · `[~]` in progress · `[x]` completed. plan.md is the authoritative source of truth for task progress.

## Task Safety Rules
- **Collision Guard:** not applicable (no rename/move of files; in-place edit of one `.md`).
- **Edit Safety:** single-file, string-anchored edits with surrounding context; prefer the Edit tool over full rewrite. Do NOT overwrite the clean on-disk file with the encoding-corrupted pasted copy.
- **Junction safety:** never `Remove-Item` a reparse point; if any junction remediation were ever needed, use `cmd /c rmdir` after backup (runbook rule) — but this track does NOT remediate, it only flags.
