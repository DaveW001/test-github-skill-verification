# Plan: Skill Creation Functional Testing Harness

## Restatement

### Goal / Outcome
Build a sustainable confirmed-skill validation system: a first-class `skill-test-harness` skill, a reusable PowerShell smoke-test script, a mandatory functional test-case convention, and Conductor/skill-writer documentation that makes structural + functional validation the expected quality bar for new skills.

### Constraints / Non-Goals
- Use PowerShell-first execution only because native file tools are failing with `Bun is not defined`.
- Use `-LiteralPath`, double-quoted Windows paths, `Get-Content -Raw`, `Set-Content -Encoding utf8 -NoNewline`, and literal string operations.
- Do not print or inspect secret values. Do not call real external APIs or production systems.
- Do not modify OpenCode runtime or Conductor subagent code. This track updates reusable skills, references, templates, and the plan convention.
- The PowerShell harness prints the functional prompt; the orchestrator must launch the Task sub-agent and save its report.

### Definition of Done
All deliverables in `spec.md` exist, the harness script parses and runs, one real functional smoke-test report is recorded, `skill-writer` and Conductor references point to the harness, the base Conductor plan template includes task-authoring standards, and Conductor bookkeeping is synchronized.

## Tool Preflight
- file-tool status: BROKEN. Native file tools return `Bun is not defined`.
- fallback shell: PowerShell-first via `bash`.
- every executor bash call must include an explicit timeout.

---

## Phase 0 Setup & Backups

### Objective
Confirm prerequisites and create reversible backups before editing global skill/reference files.

- [x] 0.1 Confirm prerequisite paths exist.
  - Command:
    ```powershell
    $paths = @(
      "C:\Users\DaveWitkin\.opencode-lazy-vault",
      "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-writer\reference.md",
      "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\SKILL.md",
      "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references",
      "C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md"
    )
    $missing = $paths | Where-Object { -not (Test-Path -LiteralPath $_) }
    if ($missing.Count -eq 0) { "PREREQUISITES_PRESENT" } else { $missing; exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `PREREQUISITES_PRESENT`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault" -Directory | Select-Object Name`.
  - Error recovery: If any prerequisite is missing, stop and report the exact path.

- [x] 0.2 Create timestamped backups for files to modify.
  - Command:
    ```powershell
    $backupRoot = "C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\backups-20260703"
    New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
    Copy-Item -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-writer\reference.md" -Destination "$backupRoot\skill-writer-reference.md.bak" -Force
    Copy-Item -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md" -Destination "$backupRoot\conductor-track-plan-template.md.bak" -Force
    if (Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\skill-creation-testing.md") { Copy-Item -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\skill-creation-testing.md" -Destination "$backupRoot\skill-creation-testing.md.bak" -Force }
    if ((Test-Path -LiteralPath "$backupRoot\skill-writer-reference.md.bak") -and (Test-Path -LiteralPath "$backupRoot\conductor-track-plan-template.md.bak")) { "BACKUPS_CREATED" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `BACKUPS_CREATED`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath "C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\backups-20260703"`.
  - Error recovery: If backup fails, stop before editing global files.

---

## Phase 1 Build First-Class `skill-test-harness` Skill

### Objective
Create a discoverable lazy-vault skill that owns the harness and its conventions.

- [x] 1.1 Create skill directories.
  - Command:
    ```powershell
    New-Item -ItemType Directory -Force -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts" | Out-Null
    New-Item -ItemType Directory -Force -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\templates" | Out-Null
    if ((Test-Path -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts") -and (Test-Path -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\templates")) { "HARNESS_DIRS_CREATED" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `HARNESS_DIRS_CREATED`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness"`.
  - Error recovery: If access denied, stop and report permission issue.

- [x] 1.2 Create `SKILL.md` for `skill-test-harness`.
  - Command: Write `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\SKILL.md` with valid frontmatter: `name: skill-test-harness`, description containing `confirmed skill`, and instructions to run `scripts\skill-smoke-test.ps1`.
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $skillMd = "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\SKILL.md"
    if (-not (Test-Path -LiteralPath $skillMd)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $skillMd
    if ($c.Contains('name: skill-test-harness') -and $c.Contains('confirmed skill')) { "True" } else { "False" }
    ```
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\SKILL.md" -SimpleMatch 'scripts\skill-smoke-test.ps1'`.
  - Error recovery: If frontmatter is invalid, rewrite the file from the skill-writer frontmatter standards.

- [x] 1.3 Create `scripts\skill-smoke-test.ps1` with explicit implementation structure.
  - Command: Write `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1` with these functions exactly: `Add-Result`, `Get-SkillFrontmatter`, `Test-SkillStructure`, `Test-MarkdownLinks`, `Test-ReferencedFiles`, `Test-ScriptSyntax`, `Write-FunctionalPrompt`, `Write-Summary`, and `Main`.
  - Required behavior:
    - Parameters: `[Parameter(Mandatory=$true)][string]$SkillPath`, `[switch]$PrintFunctionalPrompt`.
    - Output headings: `SKILL SMOKE TEST SUMMARY`, `STRUCTURE:`, `REFERENCES:`, `SCRIPT SYNTAX:`, `FUNCTIONAL PROMPT TEMPLATE`.
    - Summary line: `RESULT: PASS` when no failures, `RESULT: FAIL` otherwise.
    - Exit code `0` on no failures, `1` on failures.
    - Warnings do not fail the run unless a check cannot be performed on a file that exists.
    - No external API calls.
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $harness = "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1"
    if (-not (Test-Path -LiteralPath $harness)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $harness
    $required = @(
      'function Add-Result','function Get-SkillFrontmatter','function Test-SkillStructure',
      'function Test-MarkdownLinks','function Test-ReferencedFiles','function Test-ScriptSyntax',
      'function Write-FunctionalPrompt','function Write-Summary','function Main',
      'RESULT: PASS','RESULT: FAIL','FUNCTIONAL PROMPT TEMPLATE',
      'STRUCTURE:','REFERENCES:','SCRIPT SYNTAX:',
      '[Parameter(Mandatory=$true)][string]$SkillPath','[switch]$PrintFunctionalPrompt'
    )
    $missing = $required | Where-Object { -not $c.Contains($_) }
    if ($missing.Count -eq 0) { "True" } else { $missing -join ', ' ; "False" }
    ```
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1" -Pattern '^function '`
  - Error recovery: If the implementation becomes too large for one write, write in chunks and rerun task 1.4.

- [x] 1.4 Parse-check the harness script.
  - Command:
    ```powershell
    $errors = $null
    [System.Management.Automation.PSParser]::Tokenize((Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1"), [ref]$errors) | Out-Null
    if ($errors.Count -eq 0) { "HARNESS_PARSE_VALID" } else { $errors; exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `HARNESS_PARSE_VALID`.
  - Diagnostic checks: `Get-Command pwsh -ErrorAction SilentlyContinue`.
  - Error recovery: Fix only the parser-reported lines and rerun.

---

## Phase 2 Add Test Convention Documentation

### Objective
Define a mandatory functional test-case convention.

- [x] 2.1 Create `reference.md` for harness behavior and limitations.
  - Command: Write `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\reference.md` documenting output schema, checks performed, limitations, and the mandatory sub-agent report step.
  - Required exact sentence: `A skill is confirmed only when structural checks, script checks when applicable, and at least one representative functional smoke test pass.`
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $ref = "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\reference.md"
    if (-not (Test-Path -LiteralPath $ref)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $ref
    $required = @(
      'A skill is confirmed only when structural checks, script checks when applicable, and at least one representative functional smoke test pass.',
      '## Output Schema','## Limitations','## Sub-Agent Smoke Test',
      'skill-smoke-test.ps1'
    )
    $missing = $required | Where-Object { -not $c.Contains($_) }
    if ($missing.Count -eq 0) { "True" } else { $missing -join ', ' ; "False" }
    ```
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\reference.md" -SimpleMatch 'RESULT: PASS'`.
  - Error recovery: If required sentence is absent, rewrite the file.

- [x] 2.2 Create `templates\test-case.template.md`.
  - Command: Write `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\templates\test-case.template.md` with headings `# Skill Functional Test Case`, `## Skill Under Test`, `## Representative User Request`, `## Expected Behavior`, `## Forbidden Actions`, `## Acceptance Checks`, and `## Sub-Agent Prompt`.
  - Required exact sentence: `Every new skill MUST include at least one functional test case in tests/ or explicitly document that it is structurally valid but functionally unconfirmed.`
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $tpl = "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\templates\test-case.template.md"
    if (-not (Test-Path -LiteralPath $tpl)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $tpl
    $required = @(
      '# Skill Functional Test Case',
      '## Skill Under Test','## Representative User Request',
      '## Expected Behavior','## Forbidden Actions',
      '## Acceptance Checks','## Sub-Agent Prompt',
      'Every new skill MUST include at least one functional test case in tests/ or explicitly document that it is structurally valid but functionally unconfirmed.'
    )
    $missing = $required | Where-Object { -not $c.Contains($_) }
    if ($missing.Count -eq 0) { "True" } else { $missing -join ', ' ; "False" }
    ```
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\templates\test-case.template.md" -Pattern '^## '`
  - Error recovery: Rewrite from template if headings are malformed.

---

## Phase 3 Integrate with skill-writer and Conductor Docs

### Objective
Make the harness the canonical skill-creation validation path and close the Conductor template quality gap.

- [x] 3.1 Repair and update `skill-writer\reference.md` Step 10.
  - Command: Replace the full Step 10 section from `### Step 10` up to but not including `### Step 11` with guidance that uses `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1`, requires a Task sub-agent report, and distinguishes structural validation from functional confirmation.
  - Additional required validation: no standalone line containing only a backtick may remain in Step 10.
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $ref = "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-writer\reference.md"
    if (-not (Test-Path -LiteralPath $ref)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $ref
    # Required updated-wording markers (Step 10 must call out the harness, sub-agent, and a test-case-or-unconfirmed rule)
    $required = @(
      'C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1',
      'FUNCTIONAL_SMOKE_TEST_PASSED',
      'FUNCTIONAL_SMOKE_TEST_FAILED',
      'tests\',
      'sub-agent'
    )
    $missing = $required | Where-Object { -not $c.Contains($_) }
    # Backtick-only-line guard: no line in Step 10 (between `### Step 10` and `### Step 11`) may be exactly a single backtick
    $step10 = ($c -split '(?m)^### Step 11')[0] -split '(?m)^### Step 10'
    $step10Body = $step10[1]
    $badLine = $step10Body -split "`r?`n" | Where-Object { $_ -cmatch '^`$' }
    if ($missing.Count -eq 0 -and $badLine.Count -eq 0) { "True" } else { "missing=$($missing -join ', '); badLines=$($badLine.Count)" ; "False" }
    ```
  - Diagnostic checks: `Select-String -LiteralPath $ref -SimpleMatch '### Step 10' | Select-Object LineNumber`.
  - Error recovery: Restore from `backups-20260703\skill-writer-reference.md.bak` and retry with whole-section replacement (`### Step 10` up to but not including `### Step 11`) if formatting is corrupted or the backtick guard fails.

- [x] 3.2 Create Conductor pipeline integration reference.
  - Command: Write `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\skill-creation-testing.md` documenting that skill-creation tracks add a harness run plus actual Task sub-agent smoke-test report after structural validation and before closeout.
  - Required exact sentence: `Skill creation tracks are not confirmed until a functional-test report records FUNCTIONAL_SMOKE_TEST_PASSED or FUNCTIONAL_SMOKE_TEST_FAILED with explicit reasons.`
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $ref = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\skill-creation-testing.md"
    if (-not (Test-Path -LiteralPath $ref)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $ref
    $required = @(
      'Skill creation tracks are not confirmed until a functional-test report records FUNCTIONAL_SMOKE_TEST_PASSED or FUNCTIONAL_SMOKE_TEST_FAILED with explicit reasons.',
      'Task sub-agent','skill-smoke-test.ps1','FUNCTIONAL PROMPT TEMPLATE',
      '## When to add the harness','## Required closeout artifact'
    )
    $missing = $required | Where-Object { -not $c.Contains($_) }
    if ($missing.Count -eq 0) { "True" } else { $missing -join ', ' ; "False" }
    ```
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\skill-creation-testing.md" -SimpleMatch 'Task sub-agent'`.
  - Error recovery: If write fails under global skill path, stop and report permission issue.

- [x] 3.3 Create/update/verify base Conductor `track-plan.template.md` task-authoring standards.
  - Command: Append or insert (or verify already present) a section titled `## Task Authoring Standards` in `C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md`.
  - Required body bullets: atomic tasks, exact file paths, explicit commands, one `Authoritative acceptance check:` per task, separate `Diagnostic checks:`, `Error recovery:`, body-content verification, and idempotency.
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $tpl = "C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md"
    if (-not (Test-Path -LiteralPath $tpl)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $tpl
    $required = @(
      '## Task Authoring Standards',
      'Authoritative acceptance check:',
      '**Atomic tasks**',
      '**Exact file paths**',
      '**Explicit commands**',
      '**One authoritative acceptance check**',
      '**Diagnostic checks separated**',
      '**Error recovery**',
      '**Body-content verification**',
      '**Idempotency**'
    )
    $missing = $required | Where-Object { -not $c.Contains($_) }
    if ($missing.Count -eq 0) { "True" } else { $missing -join ', ' ; "False" }
    ```
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md" -SimpleMatch 'atomic tasks'`.
  - Error recovery: Restore backup if the template structure is corrupted.

---

## Phase 4 End-to-End Confirmation

### Objective
Prove the harness works and record an actual sub-agent functional smoke-test outcome.

- [x] 4.1 Run harness against `slack-send-message`.
  - Command:
    ```powershell
    pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1" -SkillPath "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message" -PrintFunctionalPrompt
    ```
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $harness = "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1"
    $skill   = "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message"
    $log = "$env:TEMP\harness-out-$(Get-Date -Format yyyyMMdd-HHmmss).txt"
    pwsh -NoProfile -ExecutionPolicy Bypass -File $harness -SkillPath $skill *> $log
    $LASTEXITCODE | Out-Null
    $out = Get-Content -Raw -LiteralPath $log
    $ok = $out.Contains('SKILL SMOKE TEST SUMMARY') -and $out.Contains('SCRIPT SYNTAX:') -and ($out.Contains('RESULT: PASS') -or $out.Contains('RESULT: FAIL'))
    # Hard fail if the SCRIPT SYNTAX section is empty (i.e., the script-syntax check did not run)
    $syntaxBlock = ($out -split 'SCRIPT SYNTAX:')[1]
    if ($syntaxBlock -and ($syntaxBlock -split "`r?`n")[0].Trim() -eq '') { $ok = $false }
    if ($ok) { "True" } else { "False (exit=$LASTEXITCODE; see $log)" }
    ```
  - Diagnostic checks: `Get-Content -Raw -LiteralPath $log` to inspect the full harness output.
  - Error recovery: If `slack-send-message` has legitimate failures, record them in the execution log; do not modify that skill in this track unless explicitly authorized. Re-run after any harness-script fix.

- [x] 4.2 Run actual Task sub-agent functional smoke test.
  - Command/Action: Copy the `FUNCTIONAL PROMPT TEMPLATE` from task 4.1 into a Task sub-agent. The test case should be safe and offline: ask the sub-agent to use the `slack-send-message` skill instructions to draft a plan for sending a Slack DM without sending any API request or using any token. Save the returned report to `C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\functional-test-report-2026-07-03.md`.
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $r = "C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\functional-test-report-2026-07-03.md"
    if (-not (Test-Path -LiteralPath $r)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $r
    $verdict = if ($c.Contains('FUNCTIONAL_SMOKE_TEST_PASSED')) {'PASSED'} elseif ($c.Contains('FUNCTIONAL_SMOKE_TEST_FAILED')) {'FAILED'} else {''}
    $required = @(
      'slack-send-message','## Instructions followed','## Expected output produced',
      '## Forbidden actions avoided','## Verdict'
    )
    $missing = $required | Where-Object { -not $c.Contains($_) }
    # Hard reject if the report leaks a Slack token value or claims a chat.postMessage call was sent
    $leak = ($c -match 'xoxb-[A-Za-z0-9-]{10,}') -or ($c -match '(?i)chat\.postMessage.*Sent')
    if ($verdict -and $missing.Count -eq 0 -and -not $leak) { "True" } else { "verdict=$verdict; missing=$($missing -join ', '); leak=$leak" ; "False" }
    ```
  - Diagnostic checks: `Select-String -LiteralPath $r -SimpleMatch 'FUNCTIONAL_SMOKE_TEST_'`; review report body for forbidden actions.
  - Error recovery: If the sub-agent cannot perform the task, record `FUNCTIONAL_SMOKE_TEST_FAILED` with reasons in each of the four required sub-bullets and mark the skill unconfirmed in the execution log. Do not record a synthetic PASS.

- [x] 4.3 Validate all deliverable acceptance strings.
  - Command (the original naive .Contains pattern silently swallowed $null and falsely reported ALL_DELIVERABLE_STRINGS_PRESENT when files were missing; the version below guards every read with Test-Path and an explicit null check):
    ```powershell
    $checks = @(
      @("C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\SKILL.md", "name: skill-test-harness"),
      @("C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1", "function Test-ScriptSyntax"),
      @("C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\reference.md", "A skill is confirmed only when structural checks"),
      @("C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\templates\test-case.template.md", "Every new skill MUST include"),
      @("C:\Users\DaveWitkin\.opencode-lazy-vault\skill-writer\reference.md", "FUNCTIONAL_SMOKE_TEST_PASSED"),
      @("C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\skill-creation-testing.md", "Skill creation tracks are not confirmed"),
      @("C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md", "## Task Authoring Standards")
    )
    $failed = @()
    foreach ($c in $checks) {
      if (-not (Test-Path -LiteralPath $c[0])) { $failed += "$($c[0]) missing file" ; continue }
      $content = Get-Content -Raw -LiteralPath $c[0]
      if ($null -eq $content) { $failed += "$($c[0]) unreadable" ; continue }
      if (-not $content.Contains($c[1])) { $failed += "$($c[0]) missing literal '$($c[1])'" }
    }
    if ($failed.Count -eq 0) { "ALL_DELIVERABLE_STRINGS_PRESENT" } else { $failed ; exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `ALL_DELIVERABLE_STRINGS_PRESENT`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness" -Recurse | Select-Object FullName,Length`.
  - Error recovery: Return to the failed deliverable task and rerun.

---

## Final Phase Closeout

### Objective
Synchronize Conductor artifacts and leave auditable evidence.

- [x] 5.1 Create execution log.
  - Command: Write `C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\execution-log-2026-07-03.md` with changed files, validation commands, Task sub-agent result, deviations, and unresolved follow-ups.
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $log = "C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\execution-log-2026-07-03.md"
    if (-not (Test-Path -LiteralPath $log)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $log
    $required = @('Task sub-agent result','Changed files','Validation commands','Deviations','Unresolved follow-ups')
    $missing = $required | Where-Object { -not $c.Contains($_) }
    if ($missing.Count -eq 0) { "True" } else { $missing -join ', ' ; "False" }
    ```
  - Diagnostic checks: `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\execution-log-2026-07-03.md"`.
  - Error recovery: If functional test failed, log it honestly and do not mark the skill confirmed.

- [x] 5.2 Update metadata and ledgers at closeout.
  - Command: Upsert `metadata.json`, `tracks.md`, and `tracks-ledger.md` so they reflect the actual final status and task count.
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $meta = "C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\metadata.json"
    $trk  = "C:\development\opencode\.conductor\tracks.md"
    $ldg  = "C:\development\opencode\.conductor\tracks-ledger.md"
    $failed = @()
    if (-not (Test-Path -LiteralPath $meta)) { $failed += "$meta missing" }
    if (-not (Test-Path -LiteralPath $trk))  { $failed += "$trk missing" }
    if (-not (Test-Path -LiteralPath $ldg))  { $failed += "$ldg missing" }
    if ($failed.Count -gt 0) { $failed -join ', ' ; "False" ; exit 1 }
    $m = Get-Content -Raw -LiteralPath $meta
    $t = Get-Content -Raw -LiteralPath $trk
    $l = Get-Content -Raw -LiteralPath $ldg
    $checks = @(
      @($m,'"status": "completed"'),
      @($m,'"completed_at": "2026-07-03"'),
      @($t,'20260703-skill-creation-functional-testing'),
      @($t,'completed'),
      @($l,'20260703-skill-creation-functional-testing')
    )
    $miss = @()
    foreach ($c in $checks) { if (-not $c[0].Contains($c[1])) { $miss += "missing literal '$($c[1])'" } }
    if ($miss.Count -eq 0) { "True" } else { $miss -join ', ' ; "False" }
    ```
  - Diagnostic checks: Parse `metadata.json` with `ConvertFrom-Json`.
  - Error recovery: Avoid duplicate ledger rows; update existing rows in place.

- [x] 5.3 Create validation report.
  - Command: Write `C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\validation-report-2026-07-03.md` summarizing deliverables, checks, and whether the skill-test harness itself is confirmed.
  - Authoritative acceptance check (run verbatim; outputs `True` or `False`):
    ```powershell
    $v = "C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\validation-report-2026-07-03.md"
    if (-not (Test-Path -LiteralPath $v)) { "False" ; exit 1 }
    $c = Get-Content -Raw -LiteralPath $v
    $required = @('Closeout Verdict','Evidence Checked','Mismatches Found','Required Fixes Before Close','functional-test-report-2026-07-03.md')
    $missing = $required | Where-Object { -not $c.Contains($_) }
    if ($missing.Count -eq 0) { "True" } else { $missing -join ', ' ; "False" }
    ```
  - Diagnostic checks: `Get-ChildItem -LiteralPath "C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing" -File`.
  - Error recovery: If validation finds blockers, write them explicitly and leave metadata status non-completed.

## Execution-Readiness Checklist
- [x] Every implementation task has one authoritative acceptance check.
- [x] The harness is first-class and discoverable as `skill-test-harness`.
- [x] Functional confirmation requires an actual Task sub-agent report, not just a printed prompt.
- [x] Every new skill MUST include a test case or be labeled unconfirmed.
- [x] The base Conductor template exposes task-authoring quality standards.
- [x] No step calls real external APIs or uses secrets.

## Top 3 Risks + Mitigations
1. Risk: The harness parser is too strict and flags examples as missing files. Mitigation: Treat ambiguous references as warnings; fail only explicit local paths with known extensions.
2. Risk: Task sub-agent smoke test is skipped because it is not shell-automated. Mitigation: Make `functional-test-report-2026-07-03.md` a closeout acceptance artifact.
3. Risk: Global skill docs are corrupted by partial edits. Mitigation: Use whole-section replacement and restore from backups if validation fails.

## First Task to Execute
Start with task 0.1: confirm prerequisite paths exist.