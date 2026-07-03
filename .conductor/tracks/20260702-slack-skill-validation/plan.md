# Plan: Slack Skill Validation and Documentation Cross-References

## Restatement Before Tasks

### Goal / Outcome
Validate the new `slack-send-message` skill for quality, accuracy, structure, naming, cross-references, and documented Slack API behavior; then close the identified documentation gaps with minimal safe edits.

### Constraints / Non-Goals
- Do not expose, print, copy, or commit Slack token values.
- Do not modify `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` or any MCP configuration.
- Do not rewrite existing `slack-messaging` MCP instructions; only add a cross-reference.
- Native file tools are broken with active `Bun is not defined`; use PowerShell through `bash` with explicit timeouts.
- Use `Get-Content -Raw`, `Set-Content -Encoding utf8 -NoNewline`, `Select-String`, `Get-ChildItem -Recurse`, and literal `[string]::Replace()` / string operations.
- Use `-LiteralPath` and double-quoted paths.
- Keep edits minimal and surgical.

### Definition of Done
1. `slack-send-message` passes validation: frontmatter YAML valid, name matches directory, description under 1024 characters, all referenced files exist, and no broken internal links.
2. `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc` includes `email-triage` as a Slack bot token consumer.
3. `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` has a discoverable Slack skills reference.
4. Both Slack skills cross-reference each other.
5. `execution-log-2026-07-02.md` and `validation-report-2026-07-02.md` exist in this track.

## Phase 0 Setup & Preconditions
Objective: Confirm files exist, create backups, and capture starting state without exposing secrets.

- [x] 0.1 Confirm all target files exist.
  - Command:
    ```powershell
    $paths = @("C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\SKILL.md","C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\reference.md","C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\gotchas.md","C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\scripts\send-slack-message.py","C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\scripts\Send-SlackMessage.ps1","C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\.env.example","C:\Users\DaveWitkin\.opencode-lazy-vault\slack-messaging\SKILL.md","C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc","C:\Users\DaveWitkin\.config\opencode\AGENTS.md")
    $missing = $paths | Where-Object { -not (Test-Path -LiteralPath $_) }
    if ($missing.Count -gt 0) { $missing; exit 1 }
    "ALL_TARGET_FILES_EXIST"
    ```
  - Authoritative acceptance check: Output is exactly `ALL_TARGET_FILES_EXIST`.
  - Diagnostic checks: If any path is missing, stop and report the exact missing path; do not infer alternate locations.
  - Error recovery: If a path typo is suspected, ask the user before changing the plan.

- [x] 0.2 Create backups of mutable files.
  - Command:
    ```powershell
    $backupDir = "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\backups-20260702"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    Copy-Item -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc" -Destination "$backupDir\secrets-index.jsonc.bak" -Force
    Copy-Item -LiteralPath "C:\Users\DaveWitkin\.config\opencode\AGENTS.md" -Destination "$backupDir\AGENTS.md.bak" -Force
    Copy-Item -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-messaging\SKILL.md" -Destination "$backupDir\slack-messaging-SKILL.md.bak" -Force
    Copy-Item -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\SKILL.md" -Destination "$backupDir\slack-send-message-SKILL.md.bak" -Force
    if ((Test-Path -LiteralPath "$backupDir\secrets-index.jsonc.bak") -and (Test-Path -LiteralPath "$backupDir\AGENTS.md.bak") -and (Test-Path -LiteralPath "$backupDir\slack-messaging-SKILL.md.bak") -and (Test-Path -LiteralPath "$backupDir\slack-send-message-SKILL.md.bak")) { "BACKUPS_CREATED" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `BACKUPS_CREATED`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\backups-20260702"`.
  - Error recovery: If copying fails due to permissions, stop and report the denied file.

## Phase 1 Implementation
Objective: Validate the new skill and apply minimal documentation fixes.

- [x] 1.1 Validate `slack-send-message` frontmatter and required files.
  - Command:
    ```powershell
    $skillDir = "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message"
    $skill = Get-Content -Raw -LiteralPath "$skillDir\SKILL.md"
    if (-not $skill.StartsWith("---`n")) { throw "Missing opening frontmatter fence" }
    $end = $skill.IndexOf("`n---`n", 4); if ($end -lt 0) { throw "Missing closing frontmatter fence" }
    $fm = $skill.Substring(4, $end - 4)
    $nameLine = ($fm -split "`r?`n") | Where-Object { $_ -like "name:*" } | Select-Object -First 1
    $descLine = ($fm -split "`r?`n") | Where-Object { $_ -like "description:*" } | Select-Object -First 1
    $name = $nameLine.Substring($nameLine.IndexOf(":") + 1).Trim().Trim('"')
    $desc = $descLine.Substring($descLine.IndexOf(":") + 1).Trim().Trim('"')
    $required = @("reference.md","gotchas.md","scripts\send-slack-message.py","scripts\Send-SlackMessage.ps1",".env.example")
    $missing = $required | Where-Object { -not (Test-Path -LiteralPath (Join-Path $skillDir $_)) }
    if ($name -ne "slack-send-message") { throw "Name mismatch: $name" }
    if ($desc.Length -ge 1024) { throw "Description too long: $($desc.Length)" }
    if ($missing.Count -gt 0) { throw "Missing files: $($missing -join ', ')" }
    "SKILL_FRONTMATTER_AND_FILES_VALID"
    ```
  - Authoritative acceptance check: Output is exactly `SKILL_FRONTMATTER_AND_FILES_VALID`.
  - Diagnostic checks: Inspect thrown error text only; do not print environment variables.
  - Error recovery: Fix only the frontmatter line or missing reference that failed, then rerun this task.

- [x] 1.2 Validate internal file references in `slack-send-message` docs.
  - Command:
    ```powershell
    $skillDir = "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message"
    $docs = Get-ChildItem -LiteralPath $skillDir -File -Filter "*.md"
    $broken = New-Object System.Collections.Generic.List[string]
    foreach ($doc in $docs) {
      $text = Get-Content -Raw -LiteralPath $doc.FullName
      $matches = [regex]::Matches($text, '\[[^\]]+\]\(([^)]+)\)')
      foreach ($m in $matches) {
        $href = $m.Groups[1].Value
        if ($href.StartsWith("http") -or $href.StartsWith("#") -or $href.StartsWith("mailto:")) { continue }
        $clean = ($href -split '#')[0]; if ($clean.Length -eq 0) { continue }
        if (-not (Test-Path -LiteralPath (Join-Path $skillDir $clean))) { $broken.Add("$($doc.Name) -> $href") }
      }
    }
    if ($broken.Count -gt 0) { $broken; exit 1 }
    "NO_BROKEN_INTERNAL_LINKS"
    ```
  - Authoritative acceptance check: Output is exactly `NO_BROKEN_INTERNAL_LINKS`.
  - Diagnostic checks: If broken links are listed, inspect only the listed file and target.
  - Error recovery: Correct the link target or add the missing referenced file only if clearly intended.

- [x] 1.3 Update `secrets-index.jsonc` to add `email-triage` as a Slack bot token consumer.
  - Command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc"
    $text = Get-Content -Raw -LiteralPath $path
    # JSONC stores Windows backslashes as escaped pairs (\\). The "email-triage" consumer
    # must be inserted as the full path "C:\\development\\email-triage" to match the schema.
    $consumerNeedle = '"C:\\development\\email-triage"'
    if ($text.Contains($consumerNeedle)) { "SECRETS_INDEX_ALREADY_HAS_EMAIL_TRIAGE"; exit 0 }
    $old = '"consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\conductor-reporter"]'
    $new = '"consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\conductor-reporter", "C:\\development\\email-triage"]'
    if (-not $text.Contains($old)) { throw "slack.bot_token consumers array literal not found; inspect only the slack.bot_token block and do not print token values" }
    Set-Content -Encoding utf8 -NoNewline -LiteralPath $path -Value $text.Replace($old, $new)
    $verify = Get-Content -Raw -LiteralPath $path
    if ($verify.Contains($consumerNeedle) -and -not $verify.Contains("xoxb-")) { "SECRETS_INDEX_EMAIL_TRIAGE_CONSUMER_PRESENT" } else { throw "Post-write verification failed" }
    ```
  - Authoritative acceptance check: Output is exactly `SECRETS_INDEX_EMAIL_TRIAGE_CONSUMER_PRESENT` or `SECRETS_INDEX_ALREADY_HAS_EMAIL_TRIAGE`.
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc" -SimpleMatch 'email-triage'`.
  - Error recovery: If the consumers array literal differs, stop and inspect only the `slack.bot_token` metadata block; never print token values. If the post-write check finds `xoxb-` anywhere it did not before, the edit accidentally added a token literal; abort and restore from the Task 0.2 backup.
- [x] 1.4 Add an `AGENTS.md` Reference Index entry for Slack messaging skills.
  - Command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\AGENTS.md"
    $text = Get-Content -Raw -LiteralPath $path
    $block = "### Slack Messaging`n**Trigger:** Slack, send Slack message, Slack notification, Slack alert, Slack DM, Slack webhook.`n**Action:** Use ``skill_find \"slack\"`` first. Prefer ``slack-send-message`` for scripted bot-token automation and ``slack-messaging`` for MCP-based interactive Slack workflows.`n`n"
    if ($text.Contains('### Slack Messaging')) { "AGENTS_SLACK_REFERENCE_ALREADY_PRESENT"; exit 0 }
    $anchor = "### Microsoft 365 / Outlook / Email / Calendar"
    if (-not $text.Contains($anchor)) { throw "Reference Index anchor not found" }
    Set-Content -Encoding utf8 -NoNewline -LiteralPath $path -Value $text.Replace($anchor, $block + $anchor)
    if ((Get-Content -Raw -LiteralPath $path).Contains('Prefer `slack-send-message` for scripted bot-token automation and `slack-messaging` for MCP-based interactive Slack workflows.')) { "AGENTS_SLACK_REFERENCE_PRESENT" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `AGENTS_SLACK_REFERENCE_PRESENT` or `AGENTS_SLACK_REFERENCE_ALREADY_PRESENT`.
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\AGENTS.md" -SimpleMatch '### Slack Messaging'`.
  - Error recovery: If the anchor is missing, stop and ask where to insert the Reference Index entry.

- [x] 1.5 Add a minimal cross-reference to `slack-messaging`.
  - Command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-messaging\SKILL.md"
    $text = Get-Content -Raw -LiteralPath $path
    if ($text.Contains('slack-send-message')) { "SLACK_MESSAGING_CROSS_REFERENCE_ALREADY_PRESENT"; exit 0 }
    $block = "`n`n## Related Skills`n`n- Use ``slack-send-message`` when you need scripted Slack bot-token automation, reusable Python or PowerShell helpers, file-upload automation, or non-interactive notification workflows.`n"
    Set-Content -Encoding utf8 -NoNewline -LiteralPath $path -Value ($text.TrimEnd() + $block)
    if ((Get-Content -Raw -LiteralPath $path).Contains('Use `slack-send-message` when you need scripted Slack bot-token automation')) { "SLACK_MESSAGING_CROSS_REFERENCE_PRESENT" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `SLACK_MESSAGING_CROSS_REFERENCE_PRESENT` or `SLACK_MESSAGING_CROSS_REFERENCE_ALREADY_PRESENT`.
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-messaging\SKILL.md" -SimpleMatch 'slack-send-message'`.
  - Error recovery: If there is already a Related Skills section, add only the bullet under it instead of appending a duplicate heading.

- [x] 1.6 Verify `slack-send-message` cross-reference back to `slack-messaging` is clear.
  - Command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\SKILL.md"
    $text = Get-Content -Raw -LiteralPath $path
    if ($text.Contains('slack-messaging') -and ($text.Contains('MCP') -or $text.Contains('interactive'))) { "SLACK_SEND_MESSAGE_BACK_REFERENCE_CLEAR" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `SLACK_SEND_MESSAGE_BACK_REFERENCE_CLEAR`.
  - Diagnostic checks: `Select-String -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\SKILL.md" -SimpleMatch 'slack-messaging'`.
  - Error recovery: If unclear, add one sentence near the comparison table: `For MCP-based interactive Slack workflows, use the companion slack-messaging skill.` Then rerun this task.

## Final Phase Validation & Handover
Objective: Prove all deliverables are complete and leave auditable track artifacts.

- [x] 2.1 Run final content validation across modified docs.
  - Command:
    ```powershell
    $secretsText = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc"
    $agentsText = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\AGENTS.md"
    $mcpText = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-messaging\SKILL.md"
    $sendText = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message\SKILL.md"
    $agentsCheck = 'Prefer `slack-send-message` for scripted bot-token automation and `slack-messaging` for MCP-based interactive Slack workflows.'
    $mcpCheck = 'Use `slack-send-message` when you need scripted Slack bot-token automation'
    $checks = [ordered]@{
      secrets = $secretsText.Contains("C:\\development\\email-triage")
      agents = $agentsText.Contains($agentsCheck)
      mcpSkill = $mcpText.Contains($mcpCheck)
      sendSkill = $sendText.Contains("slack-messaging")
      noTokenAdded = -not $secretsText.Contains("xoxb-")
    }
    $failed = $checks.GetEnumerator() | Where-Object { -not $_.Value } | ForEach-Object { $_.Key }
    if ($failed.Count -gt 0) { $failed; exit 1 }
    "FINAL_CONTENT_VALIDATION_PASSED"
    ```
  - Authoritative acceptance check: Output is exactly `FINAL_CONTENT_VALIDATION_PASSED`.
  - Diagnostic checks: For each failed key, `Get-Content -Raw -LiteralPath <path>` and `Select-String -SimpleMatch <substring>` to inspect what is actually there.
  - Error recovery: Return to the exact failed task and rerun that task only. If `noTokenAdded` fails, restore `secrets-index.jsonc` from the Task 0.2 backup and stop.
- [x] 2.2 Create execution log.
  - Command:
    ```powershell
    $path = "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\execution-log-2026-07-02.md"
    $body = "# Execution Log: Slack Skill Validation`n`n## Completed Tasks`n- Fill in tasks completed during execution.`n`n## Deviations / Skipped Items / Ambiguities`n- If none, write: No deviations, skipped items, or ambiguities.`n`n## Validation Performed`n- Fill in exact commands run and final outputs.`n`n## Secret Handling`n- No Slack token values were printed, copied, or committed.`n"
    Set-Content -Encoding utf8 -NoNewline -LiteralPath $path -Value $body
    if ((Get-Content -Raw -LiteralPath $path).Contains('No Slack token values were printed, copied, or committed.')) { "EXECUTION_LOG_CREATED" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `EXECUTION_LOG_CREATED`.
  - Diagnostic checks: `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\execution-log-2026-07-02.md"` returns `True`.
  - Error recovery: If writing fails, verify track directory exists and retry once.

- [x] 2.3 Create validation report.
  - Command:
    ```powershell
    $path = "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\validation-report-2026-07-02.md"
    $body = "# Validation Report: Slack Skill Validation`n`n## Verdict`nPending executor completion.`n`n## Evidence Checked`n- slack-send-message skill files`n- secrets-index.jsonc`n- AGENTS.md`n- slack-messaging SKILL.md`n`n## Required Acceptance Evidence`n- SKILL_FRONTMATTER_AND_FILES_VALID`n- NO_BROKEN_INTERNAL_LINKS`n- FINAL_CONTENT_VALIDATION_PASSED`n`n## Mismatches Found`nPending executor completion.`n"
    Set-Content -Encoding utf8 -NoNewline -LiteralPath $path -Value $body
    if ((Get-Content -Raw -LiteralPath $path).Contains('FINAL_CONTENT_VALIDATION_PASSED')) { "VALIDATION_REPORT_CREATED" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `VALIDATION_REPORT_CREATED`.
  - Diagnostic checks: `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\validation-report-2026-07-02.md"` returns `True`.
  - Error recovery: If writing fails, verify track directory exists and retry once.

- [x] 2.3a Create metadata.json for the track.
  - Command:
    ```powershell
    $path = "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\metadata.json"
    $body = '{"track_id":"20260702-slack-skill-validation","status":"active","created_at":"2026-07-02","executor_model":"pending","task_count":15,"completed_tasks":0,"progress_phase":"execution"}'
    Set-Content -Encoding utf8 -NoNewline -LiteralPath $path -Value $body
    $metadata = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json
    if (($metadata.track_id -eq "20260702-slack-skill-validation") -and ($metadata.task_count -eq 15)) { "METADATA_JSON_CREATED" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `METADATA_JSON_CREATED`.
  - Diagnostic checks: `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\metadata.json"` returns `True`.
  - Error recovery: If writing fails, verify track directory exists and retry once. If `task_count` changes later, update this value to match the number of plan checkboxes before execution.

- [x] 2.3b Add track row to tracks.md.
  - Command:
    ```powershell
    $tracksPath = "C:\development\opencode\.conductor\tracks.md"
    $trackId = "20260702-slack-skill-validation"
    $title = "Slack Skill Validation and Doc Updates"
    $status = "active"
    $completed = ""
    $trackPath = "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation"
    $row = "| $trackId | $title | $status | $completed | $trackPath |"
    if (Test-Path -LiteralPath $tracksPath) {
      $tracks = Get-Content -Raw -LiteralPath $tracksPath
      if ($tracks.Contains($trackId)) {
        $lines = $tracks -split "`r?`n"
        $lines = $lines | ForEach-Object { if ($_.Contains("| $trackId |")) { $row } else { $_ } }
        Set-Content -Encoding utf8 -NoNewline -LiteralPath $tracksPath -Value ($lines -join "`n")
      } else {
        Set-Content -Encoding utf8 -NoNewline -LiteralPath $tracksPath -Value ($tracks.TrimEnd() + "`n" + $row + "`n")
      }
    } else {
      $header = "# Conductor Tracks`n`n| Track ID | Title | Status | Completed | Path |`n"
      Set-Content -Encoding utf8 -NoNewline -LiteralPath $tracksPath -Value ($header + $row)
    }
    $verify = Get-Content -Raw -LiteralPath $tracksPath
    $rowCount = (($verify -split "`r?`n") | Where-Object { $_.Contains("| $trackId |") }).Count
    if (($rowCount -eq 1) -and $verify.Contains($trackPath)) { "TRACKS_MD_ROW_PRESENT" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `TRACKS_MD_ROW_PRESENT`.
  - Diagnostic checks: `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks.md" -SimpleMatch "20260702-slack-skill-validation"`.
  - Error recovery: If tracks.md format differs, preserve the existing file, append one row at the end with the active status and absolute track path, and document the format deviation.
- [x] 2.3c Add track entry to tracks-ledger.md.
  - Command:
    ```powershell
    $ledgerPath = "C:\development\opencode\.conductor\tracks-ledger.md"
    $trackId = "20260702-slack-skill-validation"
    $entry = "- [$trackId](./tracks/$trackId/spec.md): Validate slack-send-message skill quality and add Slack documentation cross-references. (Phase: active 2026-07-02)"
    if (Test-Path -LiteralPath $ledgerPath) {
      $ledger = Get-Content -Raw -LiteralPath $ledgerPath
      if ($ledger.Contains($trackId)) {
        $lines = $ledger -split "`r?`n"
        $lines = $lines | ForEach-Object { if ($_.Contains("[$trackId]")) { $entry } else { $_ } }
        Set-Content -Encoding utf8 -NoNewline -LiteralPath $ledgerPath -Value ($lines -join "`n")
      } elseif ($ledger.Contains("## Active Tracks")) {
        Set-Content -Encoding utf8 -NoNewline -LiteralPath $ledgerPath -Value $ledger.Replace("## Active Tracks", "## Active Tracks`n`n$entry")
      } else {
        Set-Content -Encoding utf8 -NoNewline -LiteralPath $ledgerPath -Value ($ledger.TrimEnd() + "`n`n" + $entry + "`n")
      }
    } else {
      $body = "# Conductor Tracks Ledger`n`n## Active Tracks`n`n$entry`n"
      Set-Content -Encoding utf8 -NoNewline -LiteralPath $ledgerPath -Value $body
    }
    $verify = Get-Content -Raw -LiteralPath $ledgerPath
    $entryCount = (($verify -split "`r?`n") | Where-Object { $_.Contains("[$trackId]") }).Count
    if ($entryCount -eq 1) { "TRACKS_LEDGER_ENTRY_PRESENT" } else { exit 1 }
    ```
  - Authoritative acceptance check: Output is exactly `TRACKS_LEDGER_ENTRY_PRESENT`.
  - Diagnostic checks: `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks-ledger.md" -SimpleMatch "20260702-slack-skill-validation"`.
  - Error recovery: If tracks-ledger.md format differs, preserve existing content, append one entry at the end, and document the format deviation.
- [x] 2.4 Review diffs without exposing secrets.
  - Command:
    ```powershell
    $backupDir = "C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\backups-20260702"
    $pairs = @(
      @{ backup = "$backupDir\secrets-index.jsonc.bak"; target = "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc" }
      @{ backup = "$backupDir\AGENTS.md.bak"; target = "C:\Users\DaveWitkin\.config\opencode\AGENTS.md" }
      @{ backup = "$backupDir\slack-messaging-SKILL.md.bak"; target = "C:\Users\DaveWitkin\.opencode-lazy-vault\slack-messaging\SKILL.md" }
    )
    $diffLines = 0
    foreach ($p in $pairs) {
      if (-not (Test-Path -LiteralPath $p.backup)) { throw "Missing backup: $($p.backup)" }
      if (-not (Test-Path -LiteralPath $p.target)) { throw "Missing target: $($p.target)" }
      $diffOutput = git diff --no-index --no-color $p.backup $p.target 2>&1
      $rc = $LASTEXITCODE
      if ($rc -eq 0) { continue }                 # no change (idempotent rerun)
      if ($rc -ne 1) { throw "git diff --no-index failed for $($p.target): $diffOutput" }
      $diffText = ($diffOutput | Out-String)
      if ($diffText -match "xoxb-|xoxp-|xoxo-") { throw "Refusing to display diff: token literal detected in $diffText" }
      $diffLines += ($diffText -split "`n" | Where-Object { $_ -match "^[-+]" -and $_ -notmatch "^---" -and $_ -notmatch "^\+\+\+" }).Count
    }
    if ($diffLines -eq 0) { throw "No diffs found across modified files; expected changes from Tasks 1.3-1.5" }
    "DIFF_REVIEW_COMMAND_COMPLETED lines=$diffLines"
    ```
  - Authoritative acceptance check: Output ends with `DIFF_REVIEW_COMMAND_COMPLETED lines=<N>` where `<N> >= 1` and contains no `xoxb-`, `xoxp-`, or `xoxo-` literal.
  - Diagnostic checks: Manually re-run `git diff --no-index <backup> <target>` for any pair that surprises you.
  - Error recovery: If `git diff --no-index` reports a hard error (exit 128), check that both backup and target paths exist. If a token literal is detected in the diff output, stop, restore the affected file from the Task 0.2 backup, and notify the user.
## Phase Exit Criteria
- Phase 0 exits when all target files exist and backups are present.
- Phase 1 exits when skill validation passes and documentation gaps A-D are resolved or verified already resolved.
- Final phase exits when final validation, execution log, validation report, and safe diff review are complete.

## Execution-Readiness Checklist
- [x] All paths are absolute Windows paths.
- [x] Every command is PowerShell-compatible for the `bash` tool with an explicit timeout.
- [x] Every task has exactly one `Authoritative acceptance check:`.
- [x] No task requires native Read/Edit/Write/glob/grep tools.
- [x] No task prints environment variables or token values.
- [x] Edits are minimal and reversible using backups.

## Top 3 Risks and Mitigations
1. Risk: `secrets-index.jsonc` structure differs from expected literal consumers array. Mitigation: stop and inspect only the `slack.bot_token` metadata block; do not perform broad regex edits.
2. Risk: `AGENTS.md` Reference Index anchor has changed. Mitigation: stop and ask user where to insert Slack guidance.
3. Risk: Existing skill already has a Related Skills section. Mitigation: add only the new bullet under the existing section; avoid duplicate headings.

## First Task to Execute
Start with Task 0.1: Confirm all target files exist.
