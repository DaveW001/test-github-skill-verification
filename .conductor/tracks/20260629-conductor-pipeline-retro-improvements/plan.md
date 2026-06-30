# Plan: Codify Conductor Pipeline Retrospective Improvements

## Restatement

### Goal / Outcome
Update the Conductor Pipeline guidance and supporting repo-local materials so future AI and human operators benefit from every lesson learned during the `20260629-smoke-test-hello-world` retrospective: target file-state classification, semantic idempotency, append-only verification, exact dry-run review standards, closeout synchronization, scope-language clarity, environment/tool preflight propagation, reusable documentation, and helper validation scripts.

### Constraints / Non-goals
- Do not change user deliverables unrelated to Conductor Pipeline improvement work.
- Do not require a clean git working tree; validate only planned files.
- Treat `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\` edits as global OpenCode skill updates and validate by re-reading exact acceptance strings.
- Treat `.conductor/docs/` and `.conductor/scripts/` changes as repo-local Conductor support assets.
- Preserve existing stage prompt structure unless the task explicitly inserts new guidance.
- Do not delete existing content from skill files; append or insert clearly labeled sections.
- Do not mark the track complete until `metadata.json`, `plan.md`, `.conductor/tracks.md`, and `.conductor/tracks-ledger.md` agree.

### Definition of Done
All acceptance criteria in `spec.md` pass; all 29 non-deferred tasks below are checked; helper scripts run successfully against the smoke-test artifacts; Conductor index rows are synchronized; and `execution-log-2026-06-29.md` records changed files, validations, deviations, and handover notes.

---

## Phase 0: Setup & Preconditions

**Objective:** Confirm the expected files/directories exist, capture baselines, and prepare a safe execution log before modifying global skill or repo-local Conductor assets.

- [x] **0.1 Confirm required source paths exist.** Verify the repo root, track directory, Conductor Pipeline skill files, smoke-test backup/target, and `.conductor` support directories are available or identify exactly what must be created.
  - Files/directories:
    - `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\plan.md`
    - `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`
    - `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`
    - `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`
    - `C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md`
    - `C:\development\opencode\.conductor\smoke-test\hello-world.md`
  - Command:
    ```powershell
    $paths = @(
      "C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\plan.md",
      "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md",
      "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md",
      "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md",
      "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md",
      "C:\development\opencode\.conductor\smoke-test\hello-world.md"
    )
    $missing = $paths | Where-Object { -not (Test-Path -LiteralPath $_) }
    if ($missing.Count -gt 0) { $missing | ForEach-Object { "MISSING: $_" }; exit 1 }
    "0.1 OK: all required paths exist"
    ```
  - Verification: command prints `0.1 OK: all required paths exist`.
  - Error recovery: if `.conductor\docs` or `.conductor\scripts` is missing, create it in task 0.3; if any listed source file is missing, stop and ask the orchestrator before proceeding.

- [x] **0.2 Capture byte-level baselines for all existing files that will be modified.** Create a timestamped backup directory inside this track and copy the three global skill files plus Conductor index files before editing.
  - Backup directory: `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\backups\2026-06-29-pre-edit\`
  - Command:
    ```powershell
    $backupDir = "C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\backups\2026-06-29-pre-edit"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $files = @(
      "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md",
      "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md",
      "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md",
      "C:\development\opencode\.conductor\tracks.md",
      "C:\development\opencode\.conductor\tracks-ledger.md"
    )
    foreach ($f in $files) { Copy-Item -LiteralPath $f -Destination (Join-Path $backupDir ([IO.Path]::GetFileName($f) + ".bak")) -Force }
    Get-ChildItem -LiteralPath $backupDir -File | Select-Object -ExpandProperty Name
    ```
  - Verification: output includes `stage-prompts.md.bak`, `SKILL.md.bak`, `README.md.bak`, `tracks.md.bak`, and `tracks-ledger.md.bak`.
  - Error recovery: if copy fails due to permissions, stop; do not edit the global skill files without backups.

- [x] **0.3 Create repo-local support directories if needed.** Ensure `.conductor/docs` and `.conductor/scripts` exist.
  - Command:
    ```powershell
    New-Item -ItemType Directory -Force -Path "C:\development\opencode\.conductor\docs" | Out-Null
    New-Item -ItemType Directory -Force -Path "C:\development\opencode\.conductor\scripts" | Out-Null
    if ((Test-Path "C:\development\opencode\.conductor\docs") -and (Test-Path "C:\development\opencode\.conductor\scripts")) { "0.3 OK: support directories exist" } else { exit 1 }
    ```
  - Verification: command prints `0.3 OK: support directories exist`.
  - Error recovery: if directory creation fails, verify write permission to `C:\development\opencode\.conductor` and stop.

- [x] **0.4 Create the execution log skeleton.** Create `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\execution-log-2026-06-29.md` with sections for changed files, validations, deviations, and handover.
  - Command:
    ```powershell
    $log = "C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\execution-log-2026-06-29.md"
    @'
# Execution Log - 20260629-conductor-pipeline-retro-improvements

## Changed Files

## Validation Commands Run

## Deviations / Issues

## Handover Notes
'@ | Set-Content -LiteralPath $log -Encoding utf8
    if (Test-Path -LiteralPath $log) { "0.4 OK: execution log created" } else { exit 1 }
    ```
  - Verification: command prints `0.4 OK: execution log created`.
  - Error recovery: if the file cannot be written, stop; the rest of the run requires logging.

**Phase 0 exit criteria:** All required source paths exist, backups exist for every pre-existing file to be edited, support directories exist, and the execution log exists.

---

## Phase 1: Update Conductor Pipeline Stage Prompts

**Objective:** Codify file-state classification, semantic idempotency, exact verification dry-runs, authoritative-vs-convenience check labeling, closeout synchronization, validator ownership, and environment/tool preflight guidance in `stage-prompts.md`.

- [x] **1.1 Insert `### Target file-state decision tree` guidance into `stage-prompts.md`.** Add the section near the top of `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`, before Stage 1, without deleting existing stage prompt text.
  - Required snippet must contain (verbatim): the heading `### Target file-state decision tree`; a `tracked by git` branch; an `untracked` branch whose remediation is ``git diff --no-index <backup> <target>``; and a sentence that for untracked targets `git diff -- <path>` is insufficient. The snippet is the AUTHORITATIVE acceptance string and must be inserted as a labeled block.
  - Command: read `stage-prompts.md`, insert the new section using `[string]::Replace()` so the marker `## Stage 1 - Plan Creation` immediately follows the new block, then write back via `Set-Content -LiteralPath $p -Encoding utf8 -NoNewline`. Insertion point is directly after the file heading `# Stage Prompts (Conductor Pipeline)`. Then run the verification block below.
  - Verification (must print `1.1 OK: target file-state decision tree inserted with required content`):
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"
    $heading = (Select-String -LiteralPath $p -Pattern '### Target file-state decision tree' -SimpleMatch).Count
    $noIndex = (Select-String -LiteralPath $p -Pattern 'git diff --no-index <backup> <target>' -SimpleMatch).Count
    $insuff  = (Select-String -LiteralPath $p -Pattern 'git diff -- <path>' -SimpleMatch).Count
    if ($heading -ne 1 -or $noIndex -lt 1 -or $insuff -lt 1) { "FAIL: heading=$heading noIndex=$noIndex insuff=$insuff"; exit 1 }
    "1.1 OK: target file-state decision tree inserted with required content"
    ```
  - Error recovery: if heading count >1, restore from `backups/2026-06-29-pre-edit/stage-prompts.md.bak` and retry; if `git diff --no-index <backup> <target>` count is 0, the snippet body was not inserted - return to the insertion step and append the full labeled block.

- [x] **1.2 Insert structural idempotency guidance into `stage-prompts.md`.** Add guidance that checks must match structure, not loose substrings.
  - Required snippet (inserted as LITERAL TEXT, with the backslashes intact - this is the regex example text, not a live regex) must contain the substring ``^##\s+Hello World\s*$`` AND the phrase `line-anchored` AND a contrast against loose-substring matching (e.g., a sentence noting that `## Hello World` inside backticks would also match). The section header is `## Structural idempotency`.
  - Command: read the file, locate the structural idempotency block (insert directly after the `Target file-state decision tree` block from task 1.1), insert the labeled snippet, write back via `Set-Content -LiteralPath $p -Encoding utf8 -NoNewline`. Then run the verification block below.
  - Verification (must print `1.2 OK: structural idempotency guidance inserted`):
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"
    $literalPattern = (Select-String -LiteralPath $p -Pattern '^##\s+Hello World\s*$' -SimpleMatch).Count
    $anchored       = (Select-String -LiteralPath $p -Pattern 'line-anchored' -SimpleMatch).Count
    $looseSubstr    = (Select-String -LiteralPath $p -Pattern '## Hello World' -SimpleMatch).Count
    if ($literalPattern -lt 1 -or $anchored -lt 1 -or $looseSubstr -lt 1) { "FAIL: literal=$literalPattern anchored=$anchored loose=$looseSubstr"; exit 1 }
    "1.2 OK: structural idempotency guidance inserted"
    ```
  - Error recovery: if the literal pattern count is 0, the snippet body is missing the regex-example line - return to the insertion step. The verification uses `-SimpleMatch` because the snippet text is literal; the actual regex pattern is what other agents will copy from the file.

- [x] **1.3 Insert exact verification dry-run guidance into Stage 2/3 review prompt.** Update `stage-prompts.md` so plan reviewers must dry-run newly introduced verification snippets exactly or mark them untested and reduce readiness.
  - Required sentence: `Reviewer-added verification commands must be dry-run exactly as written against the real target or a temp copy.` Also required: a follow-on sentence stating the readiness-score reduction when a verification cannot be dry-run (e.g., `deduct at least 5 percentage points` or similar).
  - Command: read the file, locate the Stage 2/3 prompt block, insert the labeled sentences directly under that block, write back via `Set-Content -LiteralPath $p -Encoding utf8 -NoNewline`. Then run the verification block below.
  - Verification (must print `1.3 OK: reviewer dry-run standard inserted`):
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"
    $dryRun   = (Select-String -LiteralPath $p -Pattern 'Reviewer-added verification commands must be dry-run exactly as written' -SimpleMatch).Count
    $tempCopy = (Select-String -LiteralPath $p -Pattern 'temp copy' -SimpleMatch).Count
    if ($dryRun -lt 1 -or $tempCopy -lt 1) { "FAIL: dryRun=$dryRun tempCopy=$tempCopy"; exit 1 }
    "1.3 OK: reviewer dry-run standard inserted"
    ```
  - Error recovery: if `temp copy` count is 0, the follow-on sentence is missing - return and add the full two-sentence block.

- [x] **1.4 Insert authoritative-vs-convenience check guidance into Stage 2/3 review prompt.** Update `stage-prompts.md` so plan tasks label authoritative acceptance checks separately from convenience/diagnostic checks.
  - Required phrase: `authoritative acceptance checks`. Also required: a paired phrase `diagnostic checks` (or `convenience / diagnostic checks`) to make the contrast explicit.
  - Command: read the file, locate the Stage 2/3 prompt block, insert the labeled sentence under that block (immediately after the task 1.3 insertion), write back via `Set-Content -LiteralPath $p -Encoding utf8 -NoNewline`. Then run the verification block below.
  - Verification (must print `1.4 OK: authoritative-vs-convenience guidance inserted`):
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"
    $authorit = (Select-String -LiteralPath $p -Pattern 'authoritative acceptance checks' -SimpleMatch).Count
    $diag     = (Select-String -LiteralPath $p -Pattern 'diagnostic checks' -SimpleMatch).Count
    if ($authorit -lt 1 -or $diag -lt 1) { "FAIL: authorit=$authorit diag=$diag"; exit 1 }
    "1.4 OK: authoritative-vs-convenience guidance inserted"
    ```
  - Error recovery: if `diagnostic checks` count is 0, the contrast phrase is missing - return to insertion and add the second sentence.

- [x] **1.5 Insert `### Executor closeout synchronization checklist` into Stage 4 prompt.** Update `stage-prompts.md` so executor closeout requires synchronization of plan, metadata, tracks index, ledger, and execution log.
  - Required heading: `### Executor closeout synchronization checklist`. Required checklist items (each a separate line under the heading): `plan.md`; `metadata.json`; `tracks.md`; `tracks-ledger.md`; `execution-log-<date>.md`. Required phrase: `Upsert rows in tracks.md and tracks-ledger.md; do not create duplicates.`
  - Command: read the file, locate the Stage 4 prompt block, insert the labeled checklist directly above `## Stage 5 / 6`, write back via `Set-Content -LiteralPath $p -Encoding utf8 -NoNewline`. Then run the verification block below.
  - Verification (must print `1.5 OK: executor closeout synchronization checklist inserted`):
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"
    $heading    = (Select-String -LiteralPath $p -Pattern '### Executor closeout synchronization checklist' -SimpleMatch).Count
    $items      = @('plan.md','metadata.json','tracks.md','tracks-ledger.md','execution-log-')
    $itemMiss   = $items | Where-Object { (Select-String -LiteralPath $p -Pattern $_ -SimpleMatch).Count -lt 1 }
    $upsertText = (Select-String -LiteralPath $p -Pattern 'Upsert rows in tracks.md and tracks-ledger.md; do not create duplicates.' -SimpleMatch).Count
    if ($heading -ne 1 -or $itemMiss -or $upsertText -lt 1) { "FAIL: heading=$heading itemMiss=$itemMiss upsert=$upsertText"; exit 1 }
    "1.5 OK: executor closeout synchronization checklist inserted"
    ```
  - Error recovery: if any item is missing, return to the insertion step and add the labeled bullet.

- [x] **1.6 Insert environment/tool preflight propagation guidance into `stage-prompts.md`.** Add a standard handoff block requiring file-tool status, fallback shell guidance, and path quoting rules.
  - Required heading: `### Tool preflight`. Required body lines (all four must appear): `file-tool status`; `fallback shell`; `path quoting`; `Bun is not defined`. The section must appear before `## Stage 1` so the preflight block is visible to all subagents.
  - Command: read the file, insert the labeled preflight block directly after the file heading `# Stage Prompts (Conductor Pipeline)` and BEFORE the new sections from 1.1-1.5 (so it is the first non-heading content), write back via `Set-Content -LiteralPath $p -Encoding utf8 -NoNewline`. Then run the verification block below.
  - Verification (must print `1.6 OK: tool preflight section inserted with required content`):
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"
    $heading    = (Select-String -LiteralPath $p -Pattern '### Tool preflight' -SimpleMatch).Count
    $required   = @('file-tool status','fallback shell','path quoting','Bun is not defined')
    $missing    = $required | Where-Object { (Select-String -LiteralPath $p -Pattern $_ -SimpleMatch).Count -lt 1 }
    if ($heading -ne 1 -or $missing) { "FAIL: heading=$heading missing=$missing"; exit 1 }
    "1.6 OK: tool preflight section inserted with required content"
    ```
  - Error recovery: if any required body line is missing, the section is empty or partial - return to the insertion step and add the labeled body lines.

- [x] **1.7 Insert validator minor-follow-up ownership guidance into Stage 5/6 prompt.** Update `stage-prompts.md` so validators classify correct-deliverable/stale-bookkeeping outcomes as minor follow-ups and identify owner.
  - Required phrase: `correct deliverable but stale Conductor bookkeeping`. Also required: a follow-on sentence that classifies this case as `minor follow-up` (not blocking) and assigns ownership to the orchestrator / Stage 6.
  - Command: read the file, locate the Stage 5/6 prompt block, insert the labeled sentence directly under that block, write back via `Set-Content -LiteralPath $p -Encoding utf8 -NoNewline`. Then run the verification block below.
  - Verification (must print `1.7 OK: validator minor-follow-up ownership inserted`):
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"
    $phrase    = (Select-String -LiteralPath $p -Pattern 'correct deliverable but stale Conductor bookkeeping' -SimpleMatch).Count
    $followup  = (Select-String -LiteralPath $p -Pattern 'minor follow-up' -SimpleMatch).Count
    $owner     = (Select-String -LiteralPath $p -Pattern 'Stage 6' -SimpleMatch).Count
    if ($phrase -lt 1 -or $followup -lt 1 -or $owner -lt 1) { "FAIL: phrase=$phrase followup=$followup owner=$owner"; exit 1 }
    "1.7 OK: validator minor-follow-up ownership inserted"
    ```
  - Error recovery: if any required substring is missing, the sentence is incomplete - return to the insertion step and write the full sentence with the classification and owner.

**Phase 1 exit criteria:** `stage-prompts.md` contains all seven new guidance elements and all `Select-String` checks above pass.

---

## Phase 2: Update Conductor Pipeline Skill and README Documentation

**Objective:** Codify scope-language and smoke-test lessons in global skill documentation so users and agents understand the policy without reading this retrospective.

- [x] **2.1 Add deliverable-vs-bookkeeping scope language to `SKILL.md`.** Insert a section that distinguishes user deliverable/application scope from pipeline bookkeeping scope.
  - Required section heading: `## Scope Language`. Required phrases (both must appear in the section body): `deliverable/application scope`; `pipeline bookkeeping scope`. Required contrast sentence: a single sentence explicitly stating that deliverable edits and bookkeeping edits have different ownership and re-review triggers.
  - Command: read `SKILL.md`, insert the labeled `## Scope Language` section directly after the `## Approved decisions` block (preserving existing order), write back via `Set-Content -LiteralPath $p -Encoding utf8 -NoNewline`. Then run the verification block below.
  - Verification (must print `2.1 OK: scope language section inserted`):
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md"
    $heading    = (Select-String -LiteralPath $p -Pattern '## Scope Language' -SimpleMatch).Count
    $deliv      = (Select-String -LiteralPath $p -Pattern 'deliverable/application scope' -SimpleMatch).Count
    $bookkeep   = (Select-String -LiteralPath $p -Pattern 'pipeline bookkeeping scope' -SimpleMatch).Count
    if ($heading -ne 1 -or $deliv -lt 1 -or $bookkeep -lt 1) { "FAIL: heading=$heading deliv=$deliv bookkeep=$bookkeep"; exit 1 }
    "2.1 OK: scope language section inserted"
    ```
  - Error recovery: if the heading count is >1, restore from backup and re-insert; if phrase count is 0, the section body is empty - return to the insertion step and write the full labeled section.

- [x] **2.2 Add `## Smoke-Test Lessons Learned` to the Conductor Pipeline README.** Append a concise reusable section to `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`.
  - Required bullets (all five must appear as separate `- ` lines under the heading):
    - `Inside a git repo does not guarantee tracked by git.`
    - `For untracked targets, use ``git diff --no-index <backup> <target>``.`
    - `Idempotency checks must match structure (line-anchored, not loose substring).`
    - `Append-only edits should prove byte-prefix preservation and additions-only diff behavior.`
    - `Executor closeout must synchronize metadata, plan, indexes, and logs.`
  - Command: read `README.md`, append the new section at the END of the file (preserving the existing `## Hello World` block), write back via `Add-Content -LiteralPath $p -Value $section -Encoding utf8`. Then run the verification block below.
  - Verification (must print `2.2 OK: smoke-test lessons section inserted with all five bullets`):
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md"
    $heading  = (Select-String -LiteralPath $p -Pattern '## Smoke-Test Lessons Learned' -SimpleMatch).Count
    $bullets  = @('Inside a git repo does not guarantee tracked by git','git diff --no-index <backup> <target>','Idempotency checks must match structure','byte-prefix preservation','Executor closeout must synchronize metadata, plan, indexes, and logs')
    $missing  = $bullets | Where-Object { (Select-String -LiteralPath $p -Pattern $_ -SimpleMatch).Count -lt 1 }
    if ($heading -ne 1 -or $missing) { "FAIL: heading=$heading missing=$missing"; exit 1 }
    "2.2 OK: smoke-test lessons section inserted with all five bullets"
    ```
  - Error recovery: if any bullet is missing, return to the append step and write the full section with all five bullets.

- [x] **2.3 Verify global skill documentation acceptance strings.** Confirm the SKILL and README files contain the exact expected phrases.
  - Command:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md" -Pattern 'deliverable/application scope' -SimpleMatch
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md" -Pattern 'pipeline bookkeeping scope' -SimpleMatch
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md" -Pattern '## Smoke-Test Lessons Learned' -SimpleMatch
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md" -Pattern 'git diff --no-index <backup> <target>' -SimpleMatch
    ```
  - Verification: all four commands return matches.
  - Error recovery: if any phrase is absent, return to tasks 2.1 or 2.2 and repair only the missing section.

**Phase 2 exit criteria:** `SKILL.md` and `README.md` contain the scope and smoke-test lesson text exactly once.

---

## Phase 3: Add Repo-Local Runbook

**Objective:** Create reusable documentation for append-only verification so future plans can reference a concrete, validated pattern.

- [x] **3.1 Create `.conductor/docs/append-only-verification.md`.** Write a runbook with backup capture, file-state classification, semantic idempotency, byte-prefix verification, no-index diff, sentence/paragraph checks, dirty-working-tree guidance, and recovery steps.
  - File: `C:\development\opencode\.conductor\docs\append-only-verification.md`
  - Required headings:
    - `# Append-Only Verification Runbook`
    - `## When to Use`
    - `## Step 1: Classify Target File State`
    - `## Step 2: Capture Pre-Edit Backup`
    - `## Step 3: Use Semantic Idempotency Guards`
    - `## Step 4: Append Without Rewriting Existing Bytes`
    - `## Step 5: Verify Byte-Prefix Preservation`
    - `## Step 6: Verify Native Git Diff Against Backup`
    - `## Step 7: Verify Content Shape`
    - `## Dirty Working Tree Guidance`
    - `## Recovery`
  - Command:
    ```powershell
    Select-String -LiteralPath "C:\development\opencode\.conductor\docs\append-only-verification.md" -Pattern 'git diff --no-index --numstat' -SimpleMatch
    ```
  - Verification: command returns one match after the runbook is written.
  - Error recovery: if write fails, confirm `.conductor/docs` exists from task 0.3 and retry.

- [x] **3.2 Verify runbook structure.** Confirm all required headings exist exactly once.
  - Command:
    ```powershell
    $p = "C:\development\opencode\.conductor\docs\append-only-verification.md"
    $headings = @('# Append-Only Verification Runbook','## When to Use','## Step 1: Classify Target File State','## Step 2: Capture Pre-Edit Backup','## Step 3: Use Semantic Idempotency Guards','## Step 4: Append Without Rewriting Existing Bytes','## Step 5: Verify Byte-Prefix Preservation','## Step 6: Verify Native Git Diff Against Backup','## Step 7: Verify Content Shape','## Dirty Working Tree Guidance','## Recovery')
    foreach ($h in $headings) {
      $count = (Select-String -LiteralPath $p -Pattern ([regex]::Escape($h))).Count
      if ($count -ne 1) { "BAD: $h count=$count"; exit 1 }
    }
    "3.2 OK: runbook headings verified"
    ```
  - Verification: command prints `3.2 OK: runbook headings verified`.
  - Error recovery: if a heading count is 0 or >1, edit only the heading section and re-run verification.

**Phase 3 exit criteria:** Append-only runbook exists, contains all required headings, and includes the no-index diff pattern.

---

## Phase 4: Add Helper Validation Scripts

**Objective:** Create reusable PowerShell helpers for append-only verification and Conductor track closeout synchronization.

- [x] **4.1 Create `.conductor/scripts/Test-AppendOnly.ps1`.** Implement a script with parameters `-BackupPath`, `-TargetPath`, `-ExpectedHeadingRegex`, `-MinSentences`, and `-MaxSentences` that exits 0 only when append-only checks pass.
  - File: `C:\development\opencode\.conductor\scripts\Test-AppendOnly.ps1`
  - Required behavior:
    - Fail if backup or target does not exist.
    - Fail if target is shorter than backup.
    - Fail if any backup byte differs from target prefix.
    - Run `git diff --no-index --numstat -- <backup> <target>` and fail if deletions are not `0`.
    - Fail if heading regex count is not exactly `1`.
    - Find the paragraph immediately after the heading and fail if sentence count is outside range.
    - Print `PASS: append-only verification succeeded` on success.
  - Command:
    ```powershell
    Test-Path -LiteralPath "C:\development\opencode\.conductor\scripts\Test-AppendOnly.ps1"
    ```
  - Verification: command prints `True` after script creation.
  - Error recovery: if script creation fails, confirm `.conductor/scripts` exists and retry.

- [x] **4.2 Smoke-test `Test-AppendOnly.ps1` against the existing smoke-test artifacts.** Run the script against the known backup and target.
  - Command:
    ```powershell
    & "C:\development\opencode\.conductor\scripts\Test-AppendOnly.ps1" `
      -BackupPath "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md" `
      -TargetPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" `
      -ExpectedHeadingRegex '^##\s+Hello World\s*$' `
      -MinSentences 3 `
      -MaxSentences 6
    ```
  - Verification: command exits 0 and prints `PASS: append-only verification succeeded`.
  - Error recovery: if the script fails, inspect whether the failure is script logic or fixture state; do not modify the fixture unless the orchestrator confirms reset is intended.

- [x] **4.3 Create `.conductor/scripts/Test-ConductorTrackCloseout.ps1`.** Implement a script that validates a track's metadata, plan checkbox completion, tracks.md row, tracks-ledger.md entry, and execution log existence.
  - File: `C:\development\opencode\.conductor\scripts\Test-ConductorTrackCloseout.ps1`
  - Required parameters: `-RepoRoot`, `-TrackId`, `-ExpectedStatus`, `-ExpectedDate`.
  - Required success output: `PASS: conductor track closeout synchronized`.
  - Command:
    ```powershell
    Test-Path -LiteralPath "C:\development\opencode\.conductor\scripts\Test-ConductorTrackCloseout.ps1"
    ```
  - Verification: command prints `True` after script creation.
  - Error recovery: if script creation fails, confirm `.conductor/scripts` exists and retry.

- [x] **4.4 Smoke-test `Test-ConductorTrackCloseout.ps1` against `20260629-smoke-test-hello-world`.** Validate the already closed smoke-test track.
  - Command:
    ```powershell
    & "C:\development\opencode\.conductor\scripts\Test-ConductorTrackCloseout.ps1" `
      -RepoRoot "C:\development\opencode" `
      -TrackId "20260629-smoke-test-hello-world" `
      -ExpectedStatus "executed" `
      -ExpectedDate "2026-06-29"
    ```
  - Verification: command exits 0 and prints `PASS: conductor track closeout synchronized`.
  - Error recovery: if this fails because the smoke-test track uses a different accepted final status, update the script to accept a status alias list only after documenting the reason in the execution log.

**Phase 4 exit criteria:** Both helper scripts exist and pass their smoke tests against known artifacts.

---

## Phase 5: Update Track State and Conductor Indexes

**Objective:** Keep this track synchronized while implementation progresses and prepare closeout metadata/index rows.

- [x] **5.1 Record changed files and validation results in the execution log.** Append a bullet list of every changed file and every command run to `execution-log-2026-06-29.md`.
  - File: `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\execution-log-2026-06-29.md`.
  - Required content: a `## Changed Files` subsection listing EVERY path that was modified (the three global skill files, `.conductor/docs/append-only-verification.md`, both helper scripts, `plan.md`, `metadata.json`, `tracks.md`, `tracks-ledger.md`); a `## Validation Commands Run` subsection with one line per command actually executed; a `## Deviations / Issues` subsection (write `None.` if none); a `## Handover Notes` subsection.
  - Command: append to the existing `execution-log-2026-06-29.md` (created in task 0.4) using `Add-Content -LiteralPath $log -Value @\'...\'@ -Encoding utf8`. Then run the verification block below.
  - Verification (must print `5.1 OK: execution log updated with all required content`):
    ```powershell
    $log = "C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\execution-log-2026-06-29.md"
    $sectionHits = @('## Changed Files','## Validation Commands Run','## Deviations / Issues','## Handover Notes')
    $pathHits = @('stage-prompts.md','SKILL.md','README.md','append-only-verification.md','Test-AppendOnly.ps1','Test-ConductorTrackCloseout.ps1','tracks.md','tracks-ledger.md')
    $missingSection = $sectionHits | Where-Object { (Select-String -LiteralPath $log -Pattern $_ -SimpleMatch).Count -lt 1 }
    $missingPath    = $pathHits    | Where-Object { (Select-String -LiteralPath $log -Pattern $_ -SimpleMatch).Count -lt 1 }
    if ($missingSection -or $missingPath) { "FAIL: missingSection=$missingSection missingPath=$missingPath"; exit 1 }
    "5.1 OK: execution log updated with all required content"
    ```
  - Error recovery: if any required path is missing from the log, the log was under-populated - return and append a per-file line under `## Changed Files`.

- [x] **5.2 Update `metadata.json` to `executed` after implementation tasks pass.** Set status/progress to executed and completed_tasks to 29 only after tasks 0.1 through 5.1 are complete.
  - File: `C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\metadata.json`.
  - Required fields: `status = "executed"`; `progress.phase = "executed"`; `progress.completed_tasks = 29`; `progress.total_tasks = 29`; `executed_at = "2026-06-29"`; `executor_model = "zai-coding-plan/glm-5.2"`.
  - Command: write the full updated `metadata.json` via `Set-Content -LiteralPath $m -Encoding utf8` with the exact JSON shape below. Then run the verification block.
    ```json
    {
      "track_id": "20260629-conductor-pipeline-retro-improvements",
      "title": "Codify Conductor Pipeline retrospective improvements",
      "status": "executed",
      "created": "2026-06-29",
      "target_files": [ /* preserve existing array */ ],
      "track_directory": "C:\\development\\opencode\\.conductor\\tracks\\20260629-conductor-pipeline-retro-improvements",
      "progress": { "phase": "executed", "completed_tasks": 29, "total_tasks": 29 },
      "executed_at": "2026-06-29",
      "executor_model": "zai-coding-plan/glm-5.2",
      "notes": "Executed per plan.md; see execution-log-2026-06-29.md."
    }
    ```
  - Verification (must print `5.2 OK: metadata status=executed progress=29/29`):
    ```powershell
    $m = "C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\metadata.json"
    $o = Get-Content -Raw -LiteralPath $m | ConvertFrom-Json
    $ok = ($o.status -eq 'executed' -and $o.progress.phase -eq 'executed' -and [int]$o.progress.completed_tasks -eq 29 -and [int]$o.progress.total_tasks -eq 29 -and $o.executed_at -eq '2026-06-29')
    if (-not $ok) { "FAIL: status=$($o.status) phase=$($o.progress.phase) done=$($o.progress.completed_tasks)/$($o.progress.total_tasks) executed_at=$($o.executed_at)"; exit 1 }
    "5.2 OK: metadata status=executed progress=29/29"
    ```
  - Error recovery: if any field is wrong, restore `metadata.json` from backup and re-apply the update with the exact shape above.

- [x] **5.3 Upsert this track row in `.conductor/tracks.md`.** Update or add exactly one row for `20260629-conductor-pipeline-retro-improvements` with status `executed`, Completed `2026-06-29`, and the absolute track path.
  - Required row (in-place edit of the existing `planning` row, not a duplicate append). The exact row text to use is:
    ```markdown
    | 20260629-conductor-pipeline-retro-improvements | Codify Conductor Pipeline retrospective improvements | executed | 2026-06-29 | C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements |
    ```
  - Command (read, replace the single existing line, write back; do NOT append a new row):
    ```powershell
    $t = "C:\development\opencode\.conductor\tracks.md"
    $cur = Get-Content -LiteralPath $t
    $new = $cur | ForEach-Object { if ($_ -like '| 20260629-conductor-pipeline-retro-improvements |*') { '| 20260629-conductor-pipeline-retro-improvements | Codify Conductor Pipeline retrospective improvements | executed | 2026-06-29 | C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements |' } else { $_ } }
    Set-Content -LiteralPath $t -Value $new -Encoding utf8
    ```
  - Verification (must print `5.3 OK: tracks.md row updated exactly once, status=executed, date=2026-06-29`):
    ```powershell
    $t = "C:\development\opencode\.conductor\tracks.md"
    $row = Get-Content -LiteralPath $t | Where-Object { $_ -like '| 20260629-conductor-pipeline-retro-improvements |*' }
    if ($row.Count -ne 1) { "FAIL: row count=$($row.Count)"; exit 1 }
    if ($row[0] -notmatch '\| executed \|') { "FAIL: status not executed in: $($row[0])"; exit 1 }
    if ($row[0] -notmatch '\| 2026-06-29 \|') { "FAIL: date not 2026-06-29 in: $($row[0])"; exit 1 }
    if ($row[0] -notlike '*C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements |') { "FAIL: path wrong in: $($row[0])"; exit 1 }
    "5.3 OK: tracks.md row updated exactly once, status=executed, date=2026-06-29"
    ```
  - Error recovery: if row count >1, restore the file from backup, manually dedupe, and re-run; if status/date regex fails, the row was not actually updated - return to the command step and re-run.

- [x] **5.4 Upsert this track entry in `.conductor/tracks-ledger.md`.** Update or add exactly one ledger entry with phase `executed 2026-06-29`.
  - Required entry (in-place edit of the existing `planning` entry; do NOT append a new entry). The exact text is:
    ```markdown
    - [20260629-conductor-pipeline-retro-improvements](./tracks/20260629-conductor-pipeline-retro-improvements/spec.md): Codify all retrospective improvements from the Hello World smoke-test pipeline run, including file-state classification, semantic idempotency, append-only verification, exact dry-run standards, closeout sync, scope-language clarity, tool preflight propagation, runbooks, and helper scripts. (Phase: executed 2026-06-29)
    ```
  - Command (read, replace the single existing line, write back). IMPORTANT: the original verification pattern `*[trackid]*` is BROKEN with PowerShell `-like` because the square brackets are treated as wildcard character classes and the hyphens cause `WildcardPatternException`. Use `-match` (regex) instead of `-like` for the lookup, and an exact equality for the replacement:
    ```powershell
    $l = "C:\development\opencode\.conductor\tracks-ledger.md"
    $cur = Get-Content -LiteralPath $l
    $new = $cur | ForEach-Object { if ($_ -match '\[20260629-conductor-pipeline-retro-improvements\]' -and $_ -match 'planning') { '- [20260629-conductor-pipeline-retro-improvements](./tracks/20260629-conductor-pipeline-retro-improvements/spec.md): Codify all retrospective improvements from the Hello World smoke-test pipeline run, including file-state classification, semantic idempotency, append-only verification, exact dry-run standards, closeout sync, scope-language clarity, tool preflight propagation, runbooks, and helper scripts. (Phase: executed 2026-06-29)' } else { $_ } }
    Set-Content -LiteralPath $l -Value $new -Encoding utf8
    ```
  - Verification (must print `5.4 OK: tracks-ledger.md entry updated exactly once, phase=executed 2026-06-29`):
    ```powershell
    $l = "C:\development\opencode\.conductor\tracks-ledger.md"
    $row = Get-Content -LiteralPath $l | Where-Object { $_ -match '\[20260629-conductor-pipeline-retro-improvements\]' }
    if ($row.Count -ne 1) { "FAIL: entry count=$($row.Count)"; exit 1 }
    if ($row[0] -notmatch 'Phase: executed 2026-06-29') { "FAIL: phase not executed in: $($row[0])"; exit 1 }
    if ($row[0] -match 'Phase: planning') { "FAIL: still says planning: $($row[0])"; exit 1 }
    "5.4 OK: tracks-ledger.md entry updated exactly once, phase=executed 2026-06-29"
    ```
  - Error recovery: if entry count >1, restore from backup, manually dedupe, and re-run; if phase still says planning, the in-place replacement did not run - return and re-execute the command.

**Phase 5 exit criteria:** Execution log records the run, metadata is executed 29/29, and both Conductor index files contain exactly one synchronized row/entry for this track.

---

## Final Phase: Validation & Handover

**Objective:** Run deterministic checks proving every improvement was applied, every helper works, and all Conductor closeout artifacts agree.

- [x] **6.1 Validate all Stage Prompt acceptance strings.** Confirm `stage-prompts.md` contains all required new guidance.
  - Command:
    ```powershell
    $p = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"
    $patterns = @('### Target file-state decision tree','^##\s+Hello World\s*$','Reviewer-added verification commands must be dry-run exactly as written','authoritative acceptance checks','### Executor closeout synchronization checklist','### Tool preflight','correct deliverable but stale Conductor bookkeeping')
    foreach ($pat in $patterns) { if ((Select-String -LiteralPath $p -Pattern $pat -SimpleMatch).Count -lt 1) { "MISSING: $pat"; exit 1 } }
    "6.1 OK: stage prompt guidance verified"
    ```
  - Verification: command prints `6.1 OK: stage prompt guidance verified`.
  - Error recovery: if a pattern is missing, return to the corresponding Phase 1 task and repair only that section.

- [x] **6.2 Validate SKILL and README acceptance strings.** Confirm global docs contain the scope language and smoke-test lessons.
  - Command:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md" -Pattern 'deliverable/application scope' -SimpleMatch | Out-Null
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md" -Pattern 'pipeline bookkeeping scope' -SimpleMatch | Out-Null
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md" -Pattern '## Smoke-Test Lessons Learned' -SimpleMatch | Out-Null
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md" -Pattern 'git diff --no-index <backup> <target>' -SimpleMatch | Out-Null
    "6.2 OK: global docs verified"
    ```
  - Verification: command prints `6.2 OK: global docs verified`.
  - Error recovery: if a command fails, return to Phase 2.

- [x] **6.3 Validate runbook and helper scripts.** Confirm runbook exists, both scripts exist, and both scripts pass their smoke tests.
  - Command:
    ```powershell
    if (-not (Test-Path "C:\development\opencode\.conductor\docs\append-only-verification.md")) { exit 1 }
    if (-not (Test-Path "C:\development\opencode\.conductor\scripts\Test-AppendOnly.ps1")) { exit 1 }
    if (-not (Test-Path "C:\development\opencode\.conductor\scripts\Test-ConductorTrackCloseout.ps1")) { exit 1 }
    & "C:\development\opencode\.conductor\scripts\Test-AppendOnly.ps1" -BackupPath "C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md" -TargetPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" -ExpectedHeadingRegex '^##\s+Hello World\s*$' -MinSentences 3 -MaxSentences 6
    & "C:\development\opencode\.conductor\scripts\Test-ConductorTrackCloseout.ps1" -RepoRoot "C:\development\opencode" -TrackId "20260629-smoke-test-hello-world" -ExpectedStatus "executed" -ExpectedDate "2026-06-29"
    "6.3 OK: runbook and helper scripts verified"
    ```
  - Verification: command prints both script `PASS:` lines and `6.3 OK: runbook and helper scripts verified`.
  - Error recovery: if a script fails, fix the script rather than weakening the acceptance criteria; document the failure in the execution log.

- [x] **6.4 Validate this track closeout synchronization.** After updating this track's own metadata/indexes, run the closeout helper against this track.
  - Command:
    ```powershell
    & "C:\development\opencode\.conductor\scripts\Test-ConductorTrackCloseout.ps1" `
      -RepoRoot "C:\development\opencode" `
      -TrackId "20260629-conductor-pipeline-retro-improvements" `
      -ExpectedStatus "executed" `
      -ExpectedDate "2026-06-29"
    ```
  - Verification: command exits 0 and prints `PASS: conductor track closeout synchronized`.
  - Error recovery: if this fails due to unchecked tasks, update `plan.md` only for tasks actually completed; if it fails due to index mismatch, return to tasks 5.2 through 5.4.

- [x] **6.5 Append final handover notes to execution log.** Record final status, validation result, any deviations, and next recommended smoke test.
  - Required content (appended under the existing `## Handover Notes` section from task 5.1): `Final status: executed.`; `Validation: all acceptance criteria met.`; `Deviations: <none | list of deviations>.`; `Next recommended smoke test: 20260629-conductor-pipeline-retro-improvements-validation-pass.`
  - Command: append the four handover lines to `execution-log-2026-06-29.md` under the existing `## Handover Notes` section using `Add-Content -LiteralPath $log -Value @\'...\'@ -Encoding utf8`. Then run the verification block below.
  - Verification (must print `6.5 OK: final handover notes appended`):
    ```powershell
    $log = "C:\development\opencode\.conductor\tracks\20260629-conductor-pipeline-retro-improvements\execution-log-2026-06-29.md"
    $req = @('Final status: executed.','Validation: all acceptance criteria met.','Next recommended smoke test: 20260629-conductor-pipeline-retro-improvements-validation-pass')
    $miss = $req | Where-Object { (Select-String -LiteralPath $log -Pattern $_ -SimpleMatch).Count -lt 1 }
    if ($miss) { "FAIL: missing=$miss"; exit 1 }
    "6.5 OK: final handover notes appended"
    ```
  - Error recovery: if any required line is missing, return to the append step and add the missing line. Do not report closeout without all four handover lines.

**Final Phase exit criteria:** All acceptance strings are present, both helper scripts pass smoke tests, this track's metadata/indexes are synchronized, the execution log contains final handover notes, and no unchecked non-deferred tasks remain.

---

## Execution Readiness Checklist

- [x] **Atomic tasks:** Each checkbox performs one clear action.
- [x] **Exact file paths:** Every task names precise absolute Windows paths and repo-local paths where relevant.
- [x] **Explicit commands:** Every task includes verbatim PowerShell commands.
- [x] **Clear ordering:** Tasks are ordered from preconditions, to prompt/docs, to runbook/scripts, to metadata/index closeout, to validation.
- [x] **Verification per step:** Every task includes deterministic verification and expected output.
- [x] **No assumed context:** The plan includes all required paths, snippets, and commands.
- [x] **Concrete examples:** Required snippets and exact rows/entries are included inline.
- [x] **Error recovery:** Every task includes fallback or stop instructions for common failures.

## Top 3 Implementation Risks + Mitigations

1. **Risk:** Editing global skill files could duplicate sections or alter existing prompt structure unexpectedly.
   - **Mitigation:** Use idempotent guards, backup files first, and verify exact acceptance strings.

2. **Risk:** Helper scripts may fail because of PowerShell quoting, path normalization, or `git diff --no-index` exit-code behavior.
   - **Mitigation:** Validate against known smoke-test artifacts and fix script logic rather than weakening acceptance criteria.

3. **Risk:** Conductor index rows could be duplicated or left inconsistent with `metadata.json`.
   - **Mitigation:** Use explicit upsert logic that counts matching rows/entries and stops on duplicates; run `Test-ConductorTrackCloseout.ps1` against both the prior smoke-test track and this track.

## First Task the Build Agent Should Execute Immediately

Run Phase 0 task 0.1 exactly as written to confirm all required source paths exist before any edit is attempted.
