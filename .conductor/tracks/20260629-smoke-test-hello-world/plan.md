# Plan: Append Hello World Smoke-Test Section

Track ID: `20260629-smoke-test-hello-world`
Title: Append Hello World smoke-test section
Status: planning
Created: 2026-06-29
Workspace root: `C:\development\opencode`
Target file: `C:\development\opencode\.conductor\smoke-test\hello-world.md`
Repo-relative target: `.conductor/smoke-test/hello-world.md`
Backup file: `C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md`

## Goal / Outcome
Append one new Markdown section to `C:\development\opencode\.conductor\smoke-test\hello-world.md`: the heading `## Hello World` followed by exactly one prose paragraph of 3-6 sentences stating that the section is a toy / sanity-check documentation example created by the Conductor pipeline as a smoke test.

## Constraints / Non-goals
- Modify only `C:\development\opencode\.conductor\smoke-test\hello-world.md`.
- Do not modify, remove, or reorder existing content in the target file.
- Do not touch any other file except creating the temporary sidecar backup `C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md` for verification/recovery.
- Use PowerShell 7+ commands on Windows with absolute paths.
- The target file is currently UNTRACKED in the working tree (verified: `git -C C:\development\opencode status` shows `?? .conductor/smoke-test/hello-world.md`). All diff-based scope verification MUST therefore use `git diff --no-index` between the pre-edit backup and the post-edit target, NOT path-scoped `git diff -- <path>` (which returns empty for untracked files). The pre-edit sidecar backup is the source of truth for byte-exact preservation.
- Unrelated pre-existing dirty paths in the repo must be ignored by isolating this task by backup-based diff; do not assume a clean working tree.
- If a `## Hello World` section already exists, stop and report; do not double-append.

## Definition of Done
- The target file contains the new `## Hello World` section at the end.
- The current target file has the byte-exact pre-edit backup as an unchanged prefix.
- The new section contains exactly one heading line and exactly one prose paragraph of 3 sentences.
- `git -C C:\development\opencode diff --no-index -- "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md" "C:\development\opencode\.conductor\smoke-test\hello-world.md"` shows only added lines for the new section, with `--numstat` showing a `0` in the deletion column.
- Verification confirms no deletions or modifications to pre-existing target-file lines.

## Phase 0 Setup & Preconditions
Objective: Confirm the target is present, capture the recovery/verification baseline, and establish repo context before any append occurs. All diff-related commands use `git diff --no-index` (not path-scoped `git diff -- <path>`) because the target is untracked.

- [x] **0.1 Confirm the target file exists.**
  Command:
  ```powershell
  if (-not (Test-Path -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" -PathType Leaf)) { throw "Target file missing: C:\development\opencode\.conductor\smoke-test\hello-world.md" }
  ```
  Verification command:
  ```powershell
  Get-Item -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" | Select-Object FullName,Length,LastWriteTime
  ```
  Error recovery: If missing, stop immediately and report the failed precondition. Do not create a replacement target file.

- [x] **0.2 Confirm the target lives inside the workspace git repository (tracking status not required).**
  Command:
  ```powershell
  $toplevel = ((git -C "C:\development\opencode" rev-parse --show-toplevel).Trim() -replace '/', '\'); $targetFull = (Resolve-Path -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md").ProviderPath; if (-not $targetFull.StartsWith($toplevel, [System.StringComparison]::OrdinalIgnoreCase)) { throw "Target is outside repo toplevel: toplevel='$toplevel' target='$targetFull'" }; "Target is inside repo toplevel: $toplevel"
  ```
  Verification command:
  ```powershell
  git -C "C:\development\opencode" rev-parse --show-toplevel; git -C "C:\development\opencode" status --short -- ".conductor/smoke-test/hello-world.md"
  ```
  Note: The file is currently UNTRACKED (`??`), so `git ls-files --error-unmatch` would fail. That is expected and does not block scope verification because `git diff --no-index <backup> <target>` works for any two files on disk.
  Error recovery: If the target is outside the repo toplevel, stop and report. If `git rev-parse` fails, stop and report that no git repo is available. Do not `git add` the file (that would mutate repo state and the user did not request staging).

- [x] **0.3 Capture a byte-exact pre-edit sidecar backup.**
  Command:
  ```powershell
  Copy-Item -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" -Destination "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md" -Force
  ```
  Verification command:
  ```powershell
  $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md").Hash; $backupHash = (Get-FileHash -Algorithm SHA256 -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md").Hash; if ($sourceHash -ne $backupHash) { throw "Backup hash mismatch" }; "Backup SHA256 verified: $backupHash"
  ```
  Error recovery: If hashes differ, delete the backup, recopy once, and rerun verification. If still failing, stop.

- [x] **0.4 Record the target file's pre-edit blob hash and an untracked-aware baseline diff.**
  Command:
  ```powershell
  git -C "C:\development\opencode" hash-object -- "C:\development\opencode\.conductor\smoke-test\hello-world.md"
  ```
  Verification command:
  ```powershell
  $baselineHash = git -C "C:\development\opencode" hash-object -- "C:\development\opencode\.conductor\smoke-test\hello-world.md"; "Pre-edit blob hash: $baselineHash"; $diffLines = git -C "C:\development\opencode" diff --no-index --numstat -- /dev/null "C:\development\opencode\.conductor\smoke-test\hello-world.md" 2>$null; "Pre-edit no-index numstat (expected: 'X 0' where X is current line count, deletion column 0): $diffLines"
  ```
  Note: Path-scoped `git diff -- <path>` and `git diff --stat -- <path>` are NOT used because they return empty for untracked files. `git diff --no-index` works for any file and produces a meaningful baseline.
  Error recovery: If `git hash-object` fails, stop and report that git cannot read the target. The backup from 0.3 remains the source of truth for preserving all pre-edit content regardless of git state.

- [x] **0.5 Enforce the idempotency guard before appending.**
  Command:
  ```powershell
  $path = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; $matches = Select-String -LiteralPath $path -Pattern '^## Hello World$'; if ($matches) { $matches | ForEach-Object { "Existing heading at line $($_.LineNumber): $($_.Line)" }; throw "Idempotency guard failed: ## Hello World already exists. Stop without appending." } else { "No existing ## Hello World heading found; safe to append." }
  ```
  Verification command:
  ```powershell
  (Select-String -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" -Pattern '^## Hello World$').Count
  ```
  Expected output: `0`.
  Error recovery: If count is not `0`, stop and report that no append was performed.

Exit criteria: Target file exists, lives inside the repo, backup matches pre-edit bytes, baseline was recorded, and no existing `## Hello World` heading is present.

## Phase 1 Implementation
Objective: Append exactly one new Markdown section to the target file and no other file.

- [x] **1.1 Append the exact Markdown snippet to the target file.**
  Command:
  ```powershell
  $path = "C:\development\opencode\.conductor\smoke-test\hello-world.md"
  $snippet = @'

## Hello World
This section is a toy documentation example created by the Conductor pipeline as a smoke test. It is a sanity-check addition that proves the pipeline can append a small, well-scoped Markdown section without disturbing existing content. The example is intentionally simple so reviewers can verify the change quickly and confidently.
'@
  Add-Content -LiteralPath $path -Value $snippet -Encoding utf8
  ```
  Exact snippet being appended (single leading blank line, 3 sentences):
  ```markdown

## Hello World
This section is a toy documentation example created by the Conductor pipeline as a smoke test. It is a sanity-check addition that proves the pipeline can append a small, well-scoped Markdown section without disturbing existing content. The example is intentionally simple so reviewers can verify the change quickly and confidently.
  ```
  Verification command:
  ```powershell
  $tailLines = @(Get-Content -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" -Tail 4); $expected = @('', '## Hello World', 'This section is a toy documentation example created by the Conductor pipeline as a smoke test. It is a sanity-check addition that proves the pipeline can append a small, well-scoped Markdown section without disturbing existing content. The example is intentionally simple so reviewers can verify the change quickly and confidently.'', ''); for ($i = 0; $i -lt $expected.Count; $i++) { if ($tailLines[$i] -ne $expected[$i]) { throw "Tail line $($i+1) mismatch: expected '$($expected[$i])' got '$($tailLines[$i])'" } }; "Tail of 4 lines matches expected snippet."
  ```
  Error recovery: If the append partially fails or the tail does not match, restore with `Copy-Item -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md" -Destination "C:\development\opencode\.conductor\smoke-test\hello-world.md" -Force`, then rerun 0.5 before trying again.

- [x] **1.2 Confirm there is exactly one `## Hello World` heading after the append.**
  Command:
  ```powershell
  $count = (Select-String -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" -Pattern '^## Hello World$').Count; if ($count -ne 1) { throw "Expected exactly one ## Hello World heading, found $count" }; "Heading count verified: $count"
  ```
  Verification command:
  ```powershell
  Select-String -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" -Pattern '^## Hello World$' | ForEach-Object { "Line $($_.LineNumber): $($_.Line)" }
  ```
  Error recovery: If count is greater than 1, restore from backup and stop for human review. If count is 0, rerun 1.1 only after confirming the target still matches the backup prefix.

Exit criteria: The target file ends with exactly the requested section and exactly one `## Hello World` heading exists.

## Final Phase Validation & Handover
Objective: Prove the append is correct, pre-existing content was untouched, and this task's footprint is isolated to the target file plus the sidecar backup. All diff-based checks use `git diff --no-index` (not path-scoped `git diff -- <path>`) because the target is untracked.

- [x] **2.1 Show native git diff between the pre-edit backup and the post-edit target (uses --no-index because target is untracked).**
  Command:
  ```powershell
  $backupPath = "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md"; $targetPath = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; git -C "C:\development\opencode" diff --no-index -- $backupPath $targetPath
  ```
  Verification command:
  ```powershell
  $backupPath = "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md"; $targetPath = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; $numstat = git -C "C:\development\opencode" diff --no-index --numstat -- $backupPath $targetPath 2>$null; if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne 1) { throw "git diff --no-index failed with exit code $LASTEXITCODE" }; $fields = ($numstat -split "`t"); if ($fields.Count -lt 2) { throw "Could not parse numstat output: '$numstat'" }; $adds = [int]$fields[0]; $dels = [int]$fields[1]; if ($dels -ne 0) { throw "Expected 0 deletions, got $dels. numstat: $numstat" }; if ($adds -lt 3) { throw "Expected at least 3 added lines (blank, heading, paragraph), got $adds. numstat: $numstat" }; "Diff OK: $adds additions, $dels deletions. numstat: $numstat"
  ```
  Expected: `--numstat` reports `0` in the deletion column and a positive value (around 3) in the addition column. Path-scoped `git diff -- <path>` is NOT used (returns empty for untracked files) and is NOT asserted on.
  Error recovery: If deletions are shown, restore from the backup and redo Phase 1. Do not manually edit around damaged content.

- [x] **2.2 Assert the pre-edit backup is an unchanged prefix of the current file (byte-level and line-level).**
  Command:
  ```powershell
  $backupPath = "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md"; $targetPath = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; $backupBytes = [System.IO.File]::ReadAllBytes($backupPath); $targetBytes = [System.IO.File]::ReadAllBytes($targetPath); if ($targetBytes.Length -lt $backupBytes.Length) { throw "Target is shorter than backup" }; for ($i = 0; $i -lt $backupBytes.Length; $i++) { if ($backupBytes[$i] -ne $targetBytes[$i]) { throw "Pre-edit content changed at byte offset $i" } }; "Backup prefix verified: $($backupBytes.Length) bytes unchanged"
  ```
  Verification command:
  ```powershell
  $backupPath = "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md"; $targetPath = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; $backupLines = @(Get-Content -LiteralPath $backupPath); $targetPrefix = @(Get-Content -LiteralPath $targetPath | Select-Object -First $backupLines.Count); $diffs = @(Compare-Object -ReferenceObject $backupLines -DifferenceObject $targetPrefix); if ($diffs.Count -gt 0) { $diffs | ForEach-Object { throw "Line-level prefix mismatch: $($_SideIndicator) '$($_.InputObject)'" } }; "Line-level prefix comparison found no removed or changed pre-existing lines."
  ```
  Error recovery: If either prefix check fails, restore from backup immediately and stop for review.

- [x] **2.3 Verify the appended paragraph has 3-6 sentences and is exactly one paragraph.**
  Command:
  ```powershell
  $path = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; $lines = @(Get-Content -LiteralPath $path); $headingIndex = [Array]::FindLastIndex([string[]]$lines, [Predicate[string]]{ param($line) $line -eq '## Hello World' }); if ($headingIndex -lt 0) { throw "Heading not found" }; $after = @($lines[($headingIndex + 1)..($lines.Count - 1)]); $nonEmptyAfter = @($after | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }); if ($nonEmptyAfter.Count -ne 1) { throw "Expected exactly one non-empty paragraph line after heading, found $($nonEmptyAfter.Count) non-empty line(s) (raw lines after heading: $($after.Count))" }; $paragraph = $nonEmptyAfter[0].Trim(); $sentences = [regex]::Matches($paragraph, '(?<=[.!?])(?:\s+|$)').Count; if ($sentences -lt 3 -or $sentences -gt 6) { throw "Expected 3-6 sentences, found $sentences" }; "Paragraph sentence count verified: $sentences. Paragraph: $paragraph"
  ```
  Verification command:
  ```powershell
  $path = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; Get-Content -LiteralPath $path | Select-Object -Last 1
  ```
  Error recovery: If sentence count or paragraph shape fails, restore from backup and rerun 1.1 with the exact snippet only.

- [x] **2.4 Guard that this task's diff touches only the target file (verified via --no-index, not path-scoped).**
  Command:
  ```powershell
  $backupPath = "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md"; $targetPath = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; $expected = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; $changed = @(git -C "C:\development\opencode" diff --no-index --name-only -- $backupPath $targetPath 2>$null); $normChanged = @($changed | ForEach-Object { $_ -replace '^"', '' -replace '"$', '' -replace '\\\\', '\' }); if ($normChanged.Count -ne 1) { throw "Expected exactly 1 file in --no-index diff, got $($normChanged.Count): $($normChanged -join ', ')" }; $got = $normChanged[0]; if ($got -ne $expected) { throw "Unexpected file in --no-index diff: expected '$expected', got '$got'" }; "Scoped task diff touches only: $got"
  ```
  Verification command:
  ```powershell
  $backupPath = "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md"; $targetPath = "C:\development\opencode\.conductor\smoke-test\hello-world.md"; git -C "C:\development\opencode" diff --no-index --name-status -- $backupPath $targetPath 2>$null
  ```
  Note: The repository may already have unrelated dirty paths. This task's footprint is isolated by `--no-index` diff against the sidecar backup plus a backup-prefix check; do not fail solely because unrelated files appear in unscoped `git status`. Path-scoped `git diff -- <path>` is NOT used (returns empty for untracked files).
  Error recovery: If the diff reports a path other than the target, stop and investigate before proceeding; do not stage or commit anything.

- [x] **2.5 Decide whether to retain or remove the sidecar backup after validation.**
  Command:
  ```powershell
  Test-Path -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md"
  ```
  Verification command:
  ```powershell
  Get-Item -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md" | Select-Object FullName,Length
  ```
  Guidance: Keep the backup until validation is complete. If handover explicitly requires removing it so the only final file touched is the target, remove it only after all validation output is captured with `Remove-Item -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md"`.
  Error recovery: If the backup is missing before validation completes, stop and report that the recovery source is unavailable.

Exit criteria: `--no-index` diff between backup and target displays intended additions only; deletion count is zero; backup prefix verification passes; sentence-count verification passes; handover notes identify the target and retained/removed backup status.

## Execution-Readiness Checklist
- [x] All commands use absolute Windows paths or explicit repo root `C:\development\opencode`.
- [x] The append command targets only `C:\development\opencode\.conductor\smoke-test\hello-world.md`.
- [x] The idempotency guard prevents duplicate `## Hello World` sections.
- [x] The sidecar backup provides restore and prefix-verification source of truth.
- [x] Final validation uses native `git diff --no-index` between the pre-edit backup and the post-edit target (NOT path-scoped `git diff -- <path>`, which is empty for untracked files).
- [x] The plan accounts for the target being UNTRACKED and for unrelated pre-existing dirty files in the repo.

## Top 3 Risks + Mitigations
1. **Duplicate section on rerun.** Mitigation: Phase 0 task 0.5 stops execution if `## Hello World` already exists.
2. **Existing content accidentally changes due to encoding/newline handling.** Mitigation: Phase 0 creates a byte-exact backup; Phase 2 task 2.2 validates backup bytes are an unchanged prefix at the byte level.
3. **Path-scoped `git diff` returns empty for the untracked target, producing false-positive verification.** Mitigation: All diff-based scope checks (tasks 0.4, 2.1, 2.4) use `git diff --no-index <backup> <target>`, which works for untracked files and produces a real diff with asserted zero deletions.

## First Task to Execute
Start with Phase 0 task 0.1: confirm `C:\development\opencode\.conductor\smoke-test\hello-world.md` exists.
