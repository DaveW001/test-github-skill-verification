# Plan: Add Hello World Section to Conductor Pipeline README

## Restatement Before Tasks

### Goal / Outcome
Add a one-paragraph Markdown section titled `Hello World` to the Conductor Pipeline README at `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md` (the user-configuration skill copy; the only existing README at that relative path).

### Constraints / Non-Goals
Only `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md` may be modified during execution. Do not change existing README sections, add tooling, run formatters, or modify any other file (including the workspace git repo `C:\development\opencode`, which must remain untouched).

### Definition of Done
The target README contains exactly one `## Hello World` heading followed by exactly one prose paragraph of 3-6 sentences explaining that the section is a toy/sanity-check documentation example and that it was created by the Conductor pipeline as a smoke test. A `Compare-Object` check of a pre-edit backup against the post-edit file shows ONLY additions (no existing line removed or changed).

### Out-of-Repo Verification Note
The target file is OUTSIDE the workspace git repo, so `git diff` scope checks do not apply. The plan uses a pre-edit backup file plus `Compare-Object` for scope verification.

## Phase 0 Setup & Preconditions

### Objective
Confirm the executor knows the correct workspace for context, the target README exists, capture a pre-edit backup, and check that the section is not already present.

### Ordered Checklist
- [x] **0.1 Confirm the workspace root is `C:\development\opencode` (context only; the target file is elsewhere).**
  Command: `Get-Location`
  Expected verification: output path is `C:\development\opencode` (the track lives here). If the executor uses the bash tool, set `workdir="C:\development\opencode"`.
  Error recovery: if the path differs, rerun with the correct `workdir`; do not rely on relative paths for the target file.

- [x] **0.2 Confirm the target file exists at `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`.**
  Command: `Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md"`
  Expected verification: command prints `True`.
  Error recovery: if it prints `False`, STOP and report the target README is missing; do not create a replacement.

- [x] **0.3 Capture a pre-edit backup of the target file (primary scope-control artifact).**
  Command: `Copy-Item -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md" -Destination "C:\development\opencode\.conductor\tracks\readme-hello-world-section\README.pre-edit.bak.md" -Force`
  Expected verification: `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\readme-hello-world-section\README.pre-edit.bak.md"` prints `True`.
  Error recovery: if the copy fails, STOP; the post-edit scope comparison depends on this backup.

- [x] **0.4 Check whether `## Hello World` already exists in the target README.**
  Command: `Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md" -Pattern '^## Hello World$'`
  Expected verification: no output means the section is absent and implementation can proceed.
  Error recovery: if a match is returned, STOP and report the README already contains the section; do not add a duplicate.

### Exit Criteria
Workspace context confirmed, target README exists, pre-edit backup captured, and no existing `## Hello World` heading is present.

## Phase 1 Implementation

### Objective
Append the requested `Hello World` section to the existing README without altering existing content.

### Ordered Checklist
- [x] **1.1 Append the exact approved Markdown section to the target README.**
  Command:
  ```powershell
  $path = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md"
  $section = "`r`n`r`n## Hello World`r`n`r`nThis hello-world section is a small toy documentation example for the Conductor Pipeline README. It exists as a sanity check that the pipeline can plan, execute, and validate a minimal documentation-only change without touching code or tooling. The paragraph is intentionally simple and self-contained so reviewers can confirm the change quickly. It was created by the Conductor pipeline as a smoke test of the track workflow."
  Add-Content -LiteralPath $path -Value $section -Encoding utf8
  ```
  Expected verification: `Select-String -LiteralPath $path -Pattern '^## Hello World$'` returns exactly one match.
  Error recovery: if `Add-Content` fails due to permissions, STOP and report; do not escalate privileges unless authorized. If duplicate headings appear, restore from the Phase 0.3 backup: `Copy-Item ... README.pre-edit.bak.md -> target` and ask for guidance.

- [x] **1.2 Verify the inserted paragraph contains the required smoke-test wording.**
  Command: `Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md" -Pattern 'created by the Conductor pipeline as a smoke test'`
  Expected verification: one match.
  Error recovery: if no match, re-edit only the new `## Hello World` paragraph to match the approved snippet.

### Exit Criteria
The README contains one appended `## Hello World` section whose paragraph includes the required Conductor pipeline smoke-test statement.

## Final Phase Validation & Handover

### Objective
Prove the change is documentation-only, scoped to the target file only (no existing content altered), and satisfies the one-paragraph section requirement.

### Ordered Checklist
- [x] **2.1 Verify there is exactly one `## Hello World` heading.**
  Command: `$m = Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md" -Pattern '^## Hello World$'; $m.Count`
  Expected verification: output is `1`.
  Error recovery: if `0`, return to 1.1; if `>1`, restore from backup and re-run 1.1 once.

- [x] **2.2 Verify the `Hello World` section has one paragraph of 3-6 sentences.**
  Command:
  ```powershell
  $content = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md"
  $section = [regex]::Match($content, '(?ms)^## Hello World\r?\n\r?\n(.+?)(\r?\n## |\z)').Groups[1].Value.Trim()
  $paragraphs = @($section -split "\r?\n\s*\r?\n" | Where-Object { $_.Trim().Length -gt 0 })
  "paragraphs=$($paragraphs.Count)"
  $sentences = [regex]::Matches($paragraphs[0], '[.!?](?=\s|$)').Count
  "sentences=$sentences"
  ```
  Expected verification: output includes `paragraphs=1` and `sentences=4` (3-6 acceptable).
  Error recovery: if counts are out of range, edit only the new section to use the approved snippet.

- [x] **2.3 Verify ONLY additions were made (no existing line removed or changed).**
  Command:
  ```powershell
  $before = Get-Content -LiteralPath "C:\development\opencode\.conductor\tracks\readme-hello-world-section\README.pre-edit.bak.md"
  $after  = Get-Content -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md"
  $diff = Compare-Object -ReferenceObject $before -DifferenceObject $after
  # SideIndicator '=>' = added (in after only); '<=' = removed/changed (in before only)
  $removed = @($diff | Where-Object { $_.SideIndicator -eq '<=' })
  "removed_count=$($removed.Count)"
  $diff | Where-Object { $_.SideIndicator -eq '=>' } | ForEach-Object { $_.InputObject }
  ```
  Expected verification: `removed_count=0` and the printed added lines are exactly the `## Hello World` heading, a blank line, the single paragraph, and the surrounding blank lines.
  Error recovery: if `removed_count` > 0, an existing line was altered; restore from the backup, then re-run 1.1 carefully with `Add-Content` only.

- [x] **2.4 Confirm the workspace git repo `C:\development\opencode` is untouched by this doc change.**
  Command: `git status --porcelain`
  Expected verification: output (within the workspace repo) contains NO line referencing `README` under any `skill/conductor-pipeline` path and shows only pre-existing unrelated entries (if any). The target file is outside this repo so it MUST NOT appear here.
  Error recovery: if a README under the workspace appears changed, that is an unintended change; revert it with `git checkout -- <path>`.

### Exit Criteria
All validation commands pass: exactly one heading, one paragraph of 3-6 sentences, only additions vs. backup, and the workspace repo is unaffected.

## Execution-Readiness Checklist
- [x] The target file path is exact: `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`.
- [x] A pre-edit backup artifact is required (Phase 0.3) because the target is outside the git repo.
- [x] Every task has a deterministic PowerShell verification command.
- [x] The implementation is documentation-only and requires no dependency installation.
- [x] Recovery instructions exist for missing file, duplicate heading, permission failure, and unintended diffs.

## Top 3 Risks + Mitigations
1. **Risk:** Editing the wrong README copy (the workspace repo has no such file; a stray one could be created).
   **Mitigation:** All commands use the absolute config path `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`; Phase 0.2 asserts existence.
2. **Risk:** Duplicating a `## Hello World` section.
   **Mitigation:** Phase 0.4 searches before editing; Phase 2.1 asserts count == 1 after.
3. **Risk:** Altering existing README content or touching the workspace git repo.
   **Mitigation:** Use `Add-Content` only; Phase 0.3 backup + Phase 2.3 `Compare-Object` proves no existing line changed; Phase 2.4 asserts the workspace repo is untouched.

## First Task to Execute
Start with Phase 0, Task 0.1: run `Get-Location` and confirm the workspace context is `C:\development\opencode` (the target file itself lives under the user-configuration skill directory).
