# Plan: Prompt Schema Overhead Research

## Brief Restatement

### Goal / Outcome

Measure and explain the remaining OpenCode system-prompt overhead, prioritizing Codex Authenticator / Codex account tooling, MCP/plugin tool schemas, native tool schemas, and task/subagent tool definitions. Produce a final recommendation on whether the 15,000-token target is reachable through local config changes or requires upstream OpenCode/runtime changes.

### Constraints / Non-Goals

- Do not modify OpenCode application source code.
- Do not permanently disable user capabilities without explicit approval.
- Do not commit, push, or create PRs.
- Redact secrets from all artifacts.
- Use timestamped backups before config A/B tests and restore original config afterward.
- Do not execute destructive account or OAuth operations.
- Do not execute this plan from the planning session that created it; a build agent should execute it in a fresh session.

### Definition of Done

- Fresh baseline and controlled A/B token measurements are captured or blockers are documented.
- Codex tool origin is identified with evidence.
- MCP/plugin, native tool, and task/subagent overhead are measured or bounded.
- Candidate savings are ranked by token impact, reversibility, risk, and confidence.
- Final report clearly states whether 15,000 tokens is reachable safely, reachable only with aggressive local toggles, or requires upstream changes.
- All changed config files are restored after tests.
- Track artifacts and ledgers are synchronized.

---

## Phase 0: Setup & Preconditions

**Objective:** Prepare a safe measurement workspace, preserve current config, and record the exact starting state before running experiments.

1. - [x] **Task 0.1: Confirm the active track directory exists**
     - File/path: `.conductor/tracks/20260531-prompt-schema-overhead-research/`
     - Command: `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research"`
     - Verification: Expected output is `True`.
     - Error recovery: If output is `False`, stop and report `Track directory missing: C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research`.

2. - [x] **Task 0.2: Create required artifact and backup directories**
     - File/path: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/` and `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/config-backups/`
     - Command: `New-Item -ItemType Directory -Path "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts" -Force; New-Item -ItemType Directory -Path "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\config-backups" -Force`
     - Verification: Run `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\config-backups"` and confirm `True`.
     - Error recovery: If directory creation fails, stop; do not modify config files.

3. - [x] **Task 0.3: Create execution log start entry**`n     - File/path: `.conductor/tracks/20260531-prompt-schema-overhead-research/execution-log.md``n     - Command (run these lines sequentially in PowerShell):`n       ```powershell`n       $logPath = "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\execution-log.md"`n       $header = "# Execution Log``n``n## $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Start"`n       $body = "- Action: Begin prompt schema overhead research.``n- Result: started"`n       Set-Content -LiteralPath $logPath -Value $header -Encoding utf8`n       Add-Content -LiteralPath $logPath -Value $body -Encoding utf8`n       ```

4. - [x] **Task 0.4: Back up current OpenCode config files**
     - File/path targets: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`, `C:\Users\DaveWitkin\.config\opencode\tui.json`, `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
     - Command: `$ts=Get-Date -Format 'yyyyMMdd-HHmmss'; $dest="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\config-backups"; @("C:\Users\DaveWitkin\.config\opencode\opencode.jsonc","C:\Users\DaveWitkin\.config\opencode\tui.json","C:\Users\DaveWitkin\.config\opencode\AGENTS.md") | ForEach-Object { if (Test-Path -LiteralPath $_) { Copy-Item -LiteralPath $_ -Destination (Join-Path $dest ((Split-Path $_ -Leaf) + ".backup-$ts")) -Force } else { "MISSING $_" | Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\execution-log.md" } }`
     - Verification: Run `Get-ChildItem -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\config-backups" | Measure-Object` and confirm at least one backup exists for every existing source file.
     - Error recovery: If a source file is missing, record it in `execution-log.md` and continue only if `opencode.jsonc` was backed up or explicitly missing.

5. - [x] **Task 0.5: Record current git status without modifying it**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/git-status-start.txt`
     - Command: `git status --short | Out-File -FilePath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\git-status-start.txt" -Encoding utf8`
     - Verification: Run `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\git-status-start.txt"` and confirm `True`.
     - Error recovery: If git command fails, write the error text to `execution-log.md` and continue; this is non-blocking.

**Phase 0 Exit Criteria:** Track directory exists, artifacts directory exists, config backups exist, execution log exists, and starting git status is captured or a non-blocking failure is logged.

---

## Phase 1: Baseline Measurement and Existing Evidence Capture

**Objective:** Capture a fresh baseline and consolidate prior evidence before changing any config.

1. - [x] **Task 1.1: Start a brand-new OpenCode session before measuring**
     - Required action: Close this planning session and open a new OpenCode session in `C:\development\opencode`.
     - Command in new session: `Get-Location`
     - Verification: Expected output includes `C:\development\opencode`.
     - Error recovery: If the working directory is different, reopen OpenCode with working directory `C:\development\opencode` before continuing.

2. - [x] **Task 1.2: Run baseline tokenscope in the fresh session**
     - File/path output: \.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/baseline-tokenscope.txt     - IMPORTANT: \	okenscope\ is an OpenCode tool, NOT a shell command. Do NOT run \	okenscope | Out-File\ from PowerShell.
     - Step A: In the fresh OpenCode session, invoke the \	okenscope\ tool (use the tool call, not a terminal command). Wait for it to complete.
     - Step B: After tokenscope completes, locate its output file. Default path: \C:\\Users\\DaveWitkin\\token-usage-output.txt\. If that file does not exist, search for it: \Get-ChildItem -Path "C:\\Users\\DaveWitkin" -Filter "token-usage-output.txt" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName     - Step C: Copy the output to the artifact: \Copy-Item -LiteralPath "<ACTUAL_PATH_FROM_STEP_B>" -Destination "C:\\development\\opencode\\.conductor\\tracks\\20260531-prompt-schema-overhead-research\\artifacts\\baseline-tokenscope.txt" -Force     - Verification: Run \Select-String -LiteralPath "C:\\development\\opencode\\.conductor\\tracks\\20260531-prompt-schema-overhead-research\\artifacts\\baseline-tokenscope.txt" -Pattern "System \\(inferred from API telemetry\\)"\ and confirm at least one match.
     - Error recovery: If tokenscope tool call fails or output file cannot be found after Step B search, write \aseline tokenscope unavailable - tokenscope tool failed or output path unknown\ to \xecution-log.md\ and continue with validation marked incomplete.

3. - [x] **Task 1.3: Extract baseline summary fields**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/baseline-summary.md`
     - Command: `$src="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\baseline-tokenscope.txt"; $out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\baseline-summary.md"; @("# Baseline Summary", "", "Source: $src", "", "## Matching Lines") + (Select-String -LiteralPath $src -Pattern "Session |System \(inferred|Input \(fresh\)|Cache read|Provider total|AVAILABLE SKILLS|AVAILABLE SUBAGENTS|Full skill tool description|Full task tool description|Total: ~" | ForEach-Object { "Line $($_.LineNumber): $($_.Line)" }) | Set-Content -LiteralPath $out -Encoding utf8`
     - Verification: Run `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\baseline-summary.md" -Pattern "Baseline Summary"` and confirm a match.
     - Error recovery: If `Select-String` fails, manually copy relevant lines from `baseline-tokenscope.txt` into `baseline-summary.md` and log the fallback.

4. - [x] **Task 1.4: Copy prior audit estimates into this track**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/prior-estimates.md`
     - Command: `$prior="C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\token-breakdown.md"; $out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\prior-estimates.md"; @("# Prior Estimates", "", "Source: $prior", "") + (Select-String -LiteralPath $prior -Pattern "Task/subagent|Subagent|Native Tool|MCP Tool|Codex|Agent Base|Skill Tool|Estimated Tokens|Total estimated MCP|Best single estimate" | ForEach-Object { "Line $($_.LineNumber): $($_.Line)" }) | Set-Content -LiteralPath $out -Encoding utf8`
     - Verification: Run `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\prior-estimates.md" -Pattern "Native Tool|MCP Tool|Codex"` and confirm matches.
     - Error recovery: If the prior file is missing, record `prior token-breakdown.md missing` in `execution-log.md` and continue.

**Phase 1 Exit Criteria:** Baseline tokenscope exists or is explicitly unavailable, baseline summary exists, and prior estimates are copied or their absence is logged.

---

## Phase 2: Effective Config and Tool Surface Inventory

**Objective:** Identify which config, plugins, MCP servers, and tool surfaces are actually contributing to prompt overhead.

1. - [x] **Task 2.1: Create redacted effective config inventory**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/effective-config-inventory.md`
     - Command: `$out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\effective-config-inventory.md"; $cfg="C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"; $tui="C:\Users\DaveWitkin\.config\opencode\tui.json"; "# Effective Config Inventory`n" | Set-Content -LiteralPath $out -Encoding utf8; "## Files`n- $cfg exists: $(Test-Path -LiteralPath $cfg)`n- $tui exists: $(Test-Path -LiteralPath $tui)`n" | Add-Content -LiteralPath $out; "## Redacted opencode.jsonc excerpts`n" | Add-Content -LiteralPath $out; if(Test-Path -LiteralPath $cfg){ (Get-Content -LiteralPath $cfg -Raw) -replace '"SLACK_MCP_XOXP_TOKEN"\s*:\s*"[^"]+"','"SLACK_MCP_XOXP_TOKEN":"<redacted>"' -replace '"apiKey"\s*:\s*"[^"]+"','"apiKey":"<redacted>"' | Add-Content -LiteralPath $out }`
     - Verification: Run `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\effective-config-inventory.md" -Pattern "<redacted>|mcp|plugin"` and confirm matches.
     - Error recovery: If redaction command fails, do not write raw config. Instead write only `plugin`, `mcp`, and `permission` keys manually with secrets omitted.

2. - [x] **Task 2.2: Record enabled and disabled MCP servers from config**
     - File/path output: append to `artifacts/effective-config-inventory.md`
     - Command: `$cfg="C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"; $out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\effective-config-inventory.md"; "`n## MCP Server Status`n" | Add-Content -LiteralPath $out; Select-String -LiteralPath $cfg -Pattern '"mcp"|"playwright"|"control-chrome"|"slack"|"enabled"' | ForEach-Object { "Line $($_.LineNumber): $($_.Line)" } | Add-Content -LiteralPath $out`
     - Verification: Confirm `effective-config-inventory.md` contains `MCP Server Status` and at least one MCP server name.
     - Error recovery: If parsing config is difficult because JSONC comments or formatting changed, copy the redacted `mcp` block manually into the artifact.

3. - [x] **Task 2.3: Inventory visible developer tool namespaces from current session**
     - File/path output: .conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/tool-surface-inventory.md
     - Step A: Create the artifact skeleton:
       `powershell
       $out = "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\tool-surface-inventory.md"
       @("# Tool Surface Inventory", "", "## Visible tools recorded from session", "", "| Tool Name | Namespace | Category (native/plugin/MCP/unknown) | Notes |", "|---|---|---|---|") | Set-Content -LiteralPath $out -Encoding utf8
       `
     - Step B: In the active OpenCode session, examine the tool list visible to the agent. For EACH visible tool, append a row to the artifact:
       `powershell
       Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\tool-surface-inventory.md" -Value "| bash | native | native | Shell execution |"
       # Repeat for each tool: read, glob, grep, edit, write, task, skill, tokenscope, webfetch, websearch, and any codex-* or MCP-derived tools
       `
     - Step C: After recording all tools, append a summary section:
       `powershell
       Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\tool-surface-inventory.md" -Value "
## Summary
- Total native tools: <count>
- Total plugin/MCP tools: <count>
- Total task/subagent tools: <count>
- Notes: <any observations about tool surface size>"
       `
     - Verification: Run Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\tool-surface-inventory.md" -Pattern "Tool Surface Inventory|bash|Summary" and confirm all three patterns match.
     - Error recovery: If the session tool list cannot be inspected programmatically, manually record the tools you can see from the session context and note 
ecorded from session observation in the Notes column.

4. - [x] **Task 2.4: Identify Codex tool origin candidates**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/codex-tool-origin-analysis.md`
     - Command: `$out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\codex-tool-origin-analysis.md"; @("# Codex Tool Origin Analysis", "", "## Config evidence to inspect", "- C:\Users\DaveWitkin\.config\opencode\opencode.jsonc plugin array", "- C:\Users\DaveWitkin\.config\opencode\tui.json plugin array", "- package.json and package-lock.json under C:\Users\DaveWitkin\.config\opencode", "", "## Search results") | Set-Content -LiteralPath $out -Encoding utf8; Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc","C:\Users\DaveWitkin\.config\opencode\tui.json","C:\Users\DaveWitkin\.config\opencode\package.json","C:\Users\DaveWitkin\.config\opencode\package-lock.json" -Pattern "codex|auth|mcp|plugin" -CaseSensitive:$false | ForEach-Object { "$($_.Path):$($_.LineNumber): $($_.Line)" } | Add-Content -LiteralPath $out`
     - Verification: Run `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\codex-tool-origin-analysis.md" -Pattern "codex|plugin"` and confirm matches.
     - Error recovery: If the search returns no matches, record `No Codex plugin/config matches found` and proceed to runtime A/B testing.

**Phase 2 Exit Criteria:** Effective config, MCP status, visible tool surface, and Codex-origin candidate artifacts exist.

---

## Phase 3: Restore or Replace Tokenscope Context Export

**Objective:** Obtain direct or near-direct schema component measurements, prioritizing MCP/plugin and native tool schemas.

1. - [x] **Task 3.1: Attempt tokenscope context export diagnostic**
     - File/path output: .conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/tokenscope-export-diagnostic.txt
     - IMPORTANT: 	okenscope is an OpenCode tool, NOT a shell command. Do NOT run 	okenscope | Out-File from PowerShell.
     - Step A: In the current OpenCode session, invoke the 	okenscope tool. Wait for it to complete.
     - Step B: Locate the tokenscope output file. Default path: C:\Users\DaveWitkin\token-usage-output.txt. If not found, search: Get-ChildItem -Path "C:\Users\DaveWitkin" -Filter "token-usage-output.txt" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
     - Step C: Copy the output to the diagnostic artifact: Copy-Item -LiteralPath "<ACTUAL_PATH_FROM_STEP_B>" -Destination "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\tokenscope-export-diagnostic.txt" -Force
     - Verification: Run Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\tokenscope-export-diagnostic.txt" -Pattern "System \(inferred from API telemetry\)|AVAILABLE SKILLS|export failed" and confirm at least one match.
     - Error recovery: If tokenscope tool call fails or output file cannot be found, write 	okenscope export unavailable - tool failed or output path unknown to the diagnostic file and proceed to Task 3.2 with fallback measurement.

2. - [x] **Task 3.2: Check whether the missing Bun package path exists**
     - File/path output: append to `artifacts/tokenscope-export-diagnostic.txt`
     - Command: `$out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\tokenscope-export-diagnostic.txt"; "`n## Bun package path checks`n" | Add-Content -LiteralPath $out; @("C:\Users\DaveWitkin\.cache\opencode\packages\@ramtinj95\opencode-tokenscope@latest\node_modules\bun\index.js", "C:\Users\DaveWitkin\.cache\opencode\packages\@ramtinj95\opencode-tokenscope@latest\node_modules\@ramtinj95\opencode-tokenscope\dist\tokenscope-lib\context.js") | ForEach-Object { "$_ exists: $(Test-Path -LiteralPath $_)" } | Add-Content -LiteralPath $out`
     - Verification: Artifact contains `Bun package path checks` and `exists:` lines.
     - Error recovery: If paths differ, search only under `C:\Users\DaveWitkin\.cache\opencode\packages\@ramtinj95` for `context.js` and record the located path.

3. - [x] **Task 3.3: Decide and record whether to repair tokenscope export or use fallback**
     - File/path output: append decision to rtifacts/tokenscope-export-diagnostic.txt
     - Step A: Check the Bun package path results from Task 3.2. If the context.js file exists, tokenscope export may be repairable.
     - Step B: Record the decision:
       `powershell
       $diag = "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\tokenscope-export-diagnostic.txt"
       $contextExists = (Get-Content -LiteralPath $diag | Select-String "context.js exists: True").Count -gt 0
       if ($contextExists) {
           $decision = "## Decision
- context.js found. Attempt tokenscope repair by reinstalling dependencies. Document results.
- If repair fails, fall back to A/B telemetry deltas."
       } else {
           $decision = "## Decision
- context.js NOT found. Tokenscope export cannot be repaired without editing OpenCode source.
- Proceeding with fallback: A/B telemetry deltas and schema text extraction."
       }
       Add-Content -LiteralPath $diag -Value $decision -Encoding utf8
       `
     - Verification: Confirm artifact contains ## Decision and either context.js found or context.js NOT found.
     - Error recovery: If uncertain, default to fallback measurement (safer - no source edits).

4. - [x] **Task 3.4: Create schema-token-estimates artifact skeleton**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/schema-token-estimates.md`
     - Command: `@("# Schema Token Estimates", "", "| Component | Method | Tokens | Confidence | Evidence |", "|---|---|---:|---|---|", "| Codex/account tool surface | pending | 0 | pending | pending |", "| MCP tool schemas | pending | 0 | pending | pending |", "| Native tool schemas | pending | 0 | pending | pending |", "| Task/subagent tool definition | pending | 0 | pending | pending |", "| Session/runtime scaffolding | pending | 0 | pending | pending |") | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\schema-token-estimates.md" -Encoding utf8`
     - Verification: Confirm file contains `Schema Token Estimates`.
     - Error recovery: If file write fails, stop and report artifact write failure.

**Phase 3 Exit Criteria:** Tokenscope export status is known, fallback method is chosen if needed, and schema estimate artifact exists.

---

## Phase 4: Codex Authenticator / Account Tooling A/B Test

**Objective:** Determine whether Codex Authenticator or account-management tooling contributes a large prompt schema cost and whether disabling/replacing it can save 2,000-3,500 tokens.

1. - [x] **Task 4.1: Identify exact config entries controlling Codex tooling**
     - File/path output: append to `artifacts/codex-tool-origin-analysis.md`
     - Command: `$out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\codex-tool-origin-analysis.md"; "`n## Candidate config controls`n" | Add-Content -LiteralPath $out; Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc","C:\Users\DaveWitkin\.config\opencode\tui.json" -Pattern "oc-codex|codex|multi-auth|authenticator|plugin" -CaseSensitive:$false | ForEach-Object { "$($_.Path):$($_.LineNumber): $($_.Line)" } | Add-Content -LiteralPath $out`
     - Verification: Confirm artifact lists the plugin/config line that appears to control Codex tooling, or explicitly says no config entry was found.
     - Error recovery: If no entry is found, do not guess; mark Codex A/B test as blocked pending manual tool-origin research.

2. - [ ] **Task 4.2: [DEFERRED] Create a temporary Codex-disabled config variant**
     - File/path target: C:\Users\DaveWitkin\.config\opencode\opencode.jsonc
     - Step A: Back up the current config:
       `powershell
       Copy-Item -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Destination "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\config-backups\opencode.jsonc.pre-codex-ab-test" -Force
       `
     - Step B: Remove the Codex plugin entry using a Python script that also cleans up trailing commas (prevents JSONC corruption):
       `powershell
       python -c "import pathlib,re; p=pathlib.Path(r'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc'); s=p.read_text(encoding='utf-8'); s=re.sub(r'\s*,?\s*\"oc-codex-multi-auth[^\"]*\"', '', s); s=re.sub(r',\s*]', ']', s); s=re.sub(r',\s*}', '}', s); p.write_text(s,encoding='utf-8')"
       `
       NOTE: The regex \s*,?\s*\"oc-codex-multi-auth[^\"]*\" removes the entry with optional surrounding comma and whitespace. The cleanup patterns ,\s*] and ,\s*} fix any trailing commas left behind.
     - Step C: Validate the edited JSONC is still parseable:
       `powershell
       python -c "import json,pathlib; p=pathlib.Path(r'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc'); import re; s=re.sub(r'//.*','',p.read_text(encoding='utf-8')); json.loads(s); print('JSONC valid')"
       `
     - Verification: (a) Run Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern "oc-codex-multi-auth" and expect NO matches. (b) Step C output should say JSONC valid.
     - Error recovery: If Step C reports invalid JSON or OpenCode fails to start, restore immediately: Copy-Item -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\config-backups\opencode.jsonc.pre-codex-ab-test" -Destination "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Force and mark this A/B test as blocked.

3. - [ ] **Task 4.3: [DEFERRED] Measure Codex-disabled system tokens in a fresh session**
     - File/path output: .conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/codex-disabled-tokenscope.txt
     - IMPORTANT: 	okenscope is an OpenCode tool, NOT a shell command.
     - Step A: Close the current session. Open a brand-new OpenCode session in C:\development\opencode (this session will use the Codex-disabled config from Task 4.2).
     - Step B: In the new session, invoke the 	okenscope tool as early as possible. Wait for it to complete.
     - Step C: Locate the output file (default: C:\Users\DaveWitkin\token-usage-output.txt). If not found, search: Get-ChildItem -Path "C:\Users\DaveWitkin" -Filter "token-usage-output.txt" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
     - Step D: Copy to artifact: Copy-Item -LiteralPath "<ACTUAL_PATH_FROM_STEP_C>" -Destination "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\codex-disabled-tokenscope.txt" -Force
     - Verification: Run Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts/codex-disabled-tokenscope.txt" -Pattern "System \(inferred from API telemetry\)" and confirm at least one match.
     - Error recovery: If OpenCode cannot start with the modified config, restore immediately using the command in Task 4.2 error recovery, then record Codex A/B blocked - config edit prevented OpenCode startup in xecution-log.md. If tokenscope tool fails, record 	okenscope unavailable in Codex-disabled session and proceed to Phase 4 restore (Task 4.4).

4. - [ ] **Task 4.4: [DEFERRED] Restore Codex config immediately after measurement**
     - File/path target: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
     - Command: `Copy-Item -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\config-backups\opencode.jsonc.pre-codex-ab-test" -Destination "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Force`
     - Verification: Run `Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern "oc-codex-multi-auth|plugin"` and confirm the original Codex plugin line is restored if it existed before the test.
     - Error recovery: If restore file is missing, restore from the newest `opencode.jsonc.backup-*` in `artifacts/config-backups/` and log the incident.

5. - [ ] **Task 4.5: [DEFERRED] Record Codex A/B delta**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/ab-test-results.md`
     - Command: `@("# A/B Test Results", "", "## Codex tooling disabled", "- Baseline artifact: artifacts/baseline-tokenscope.txt", "- Codex-disabled artifact: artifacts/codex-disabled-tokenscope.txt", "- System token delta: TODO calculate from artifacts", "- Interpretation: TODO", "- Config restored: TODO yes/no") | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\ab-test-results.md" -Encoding utf8`
     - Verification: Confirm file contains `Codex tooling disabled`.
     - Error recovery: If Codex A/B test was blocked, record `Codex A/B blocked` and the exact reason instead of inventing a delta.

**Phase 4 Exit Criteria:** Codex origin is identified or blocked with reason, Codex-disabled A/B measurement exists or failure is logged, and original config is restored.

---

## Phase 5: MCP and Native Tool Schema Measurement

**Objective:** Quantify MCP/plugin and native tool schema overhead, using direct export if available or controlled deltas/fallback estimates if not.

1. - [x] **Task 5.1: Confirm current MCP servers are disabled or enabled**
     - File/path output: append to `artifacts/schema-token-estimates.md`
     - Command: `$out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\schema-token-estimates.md"; "`n## MCP current config status`n" | Add-Content -LiteralPath $out; Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern '"playwright"|"control-chrome"|"slack"|"enabled"|"mcp"' | ForEach-Object { "Line $($_.LineNumber): $($_.Line)" } | Add-Content -LiteralPath $out`
     - Verification: Artifact contains `MCP current config status`.
     - Error recovery: If config file is missing, stop MCP measurement and record blocker.

2. - [x] **Task 5.2: Measure MCP-enabled delta only if user approval is present**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/mcp-enabled-test-decision.md`
     - Command: `@("# MCP Enabled Test Decision", "", "Do not enable Playwright, Control Chrome, Slack, or any other MCP server unless the user explicitly approves this A/B test.", "", "Approval present: no", "Action taken: none") | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\mcp-enabled-test-decision.md" -Encoding utf8`
     - Verification: File exists and says `Approval present: no` unless explicit user approval was given later.
     - Error recovery: If approval is later given, update this artifact before editing config and follow the same backup/restore pattern as Phase 4.

3. - [x] **Task 5.3: Estimate native tool schema overhead from available artifacts**
     - File/path output: append to `artifacts/schema-token-estimates.md`
     - Command: `$prior="C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\token-breakdown.md"; $out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\schema-token-estimates.md"; "`n## Native tool schema evidence`n" | Add-Content -LiteralPath $out; Select-String -LiteralPath $prior -Pattern "Native Tool Schemas|15 native tools|Estimated tokens|task:|bash:|read:|glob:|grep:" | ForEach-Object { "Line $($_.LineNumber): $($_.Line)" } | Add-Content -LiteralPath $out`
     - Verification: Artifact contains `Native tool schema evidence` and `Estimated tokens`.
     - Error recovery: If prior artifact is missing, estimate native schemas from the current visible tool descriptions and document the manual method.

4. - [x] **Task 5.4: Estimate task/subagent overhead from current tokenscope**
     - File/path output: append to `artifacts/schema-token-estimates.md`
     - Command: `$base="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\baseline-tokenscope.txt"; $out="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\schema-token-estimates.md"; "`n## Task/subagent evidence`n" | Add-Content -LiteralPath $out; Select-String -LiteralPath $base -Pattern "AVAILABLE SUBAGENTS|Total: ~|Full task tool description|task tool definition" | ForEach-Object { "Line $($_.LineNumber): $($_.Line)" } | Add-Content -LiteralPath $out`
     - Verification: Artifact contains `Task/subagent evidence`.
     - Error recovery: If baseline lacks this section, copy the same lines from `artifacts/post-reduction-tokenscope-fresh.txt` in the prior track and mark confidence lower.

5. - [x] **Task 5.5: Rank schema overhead savings opportunities**
     - File/path output: append to `artifacts/schema-token-estimates.md`
     - Command: `Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\schema-token-estimates.md" -Value "`n## Savings Opportunity Ranking Template`n`n| Rank | Candidate | Estimated Savings | Reversibility | User Impact | Confidence | Next Action |`n|---:|---|---:|---|---|---|---|`n| 1 | Codex/account tooling | TODO | reversible config test | medium | TODO | evaluate A/B delta |`n| 2 | MCP tool schemas | TODO | reversible config test | medium/high | TODO | measure only with approval |`n| 3 | Native tool schema compaction | TODO | upstream/runtime | low local, high upstream | TODO | upstream issue |`n| 4 | Task/subagent schema compaction | TODO | config/upstream | medium | TODO | investigate config support |`n"`
     - Verification: Artifact contains `Savings Opportunity Ranking Template`.
     - Error recovery: If ranking cannot be completed due missing measurements, fill `TODO` with `blocked` and explain blockers.

**Phase 5 Exit Criteria:** MCP status is documented, native and task/subagent estimates are recorded, and savings opportunities are ranked or blockers are explicit.

---

## Phase 6: Final Analysis and Recommendation

**Objective:** Convert measurements into a decision about the 15,000-token target and next actions.

1. - [x] **Task 6.1: Create final report skeleton**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/final-report.md`
     - Command: `@("# Final Report: Prompt Schema Overhead Research", "", "## Executive Summary", "", "## Measurements", "", "## Codex Tooling Findings", "", "## MCP Schema Findings", "", "## Native Tool Schema Findings", "", "## Task/Subagent Findings", "", "## Can We Reach 15,000 Tokens?", "", "## Recommended Next Actions", "", "## Caveats") | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\final-report.md" -Encoding utf8`
     - Verification: Confirm all headings appear with `Select-String`.
     - Error recovery: If final report already exists, append missing headings rather than overwriting evidence.

2. - [x] **Task 6.2: Add measured token comparison table**
     - File/path target: `artifacts/final-report.md`
     - Command: `Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\final-report.md" -Value "`n| Scenario | System Tokens | Delta vs Baseline | Artifact | Confidence |`n|---|---:|---:|---|---|`n| Baseline | TODO | 0 | artifacts/baseline-tokenscope.txt | TODO |`n| Codex disabled | TODO | TODO | artifacts/codex-disabled-tokenscope.txt | TODO |`n| MCP enabled/disabled tests | TODO | TODO | artifacts/mcp-enabled-test-decision.md | TODO |`n"`
     - Verification: Final report contains `Scenario | System Tokens`.
     - Error recovery: If a measurement is unavailable, write `unavailable` and explain why in `## Caveats`.

3. - [x] **Task 6.3: Write the 15,000-token conclusion using one required line**
     - File/path target: rtifacts/final-report.md
     - Decision criteria (use the FIRST matching rule):
       1. If baseline system tokens <= 15,000: choose Safe local config changes can reach 15,000 tokens.
       2. If baseline > 15,000 AND (Codex A/B delta >= 2,000 OR combined candidate savings from ranking table >= baseline - 15,000): choose Aggressive reversible local toggles may reach 15,000 tokens, but safe defaults do not.
       3. If baseline > 15,000 AND candidate savings from ranking table show that even aggressive local toggles fall short: choose 15,000 tokens requires upstream OpenCode/runtime changes.
       4. If baseline measurement is unavailable OR Codex A/B test was blocked AND no fallback estimates exist: choose Validation incomplete; 15,000-token reachability cannot be concluded.
     - Required conclusion options (choose exactly one based on criteria above):
       - Safe local config changes can reach 15,000 tokens.
       - Aggressive reversible local toggles may reach 15,000 tokens, but safe defaults do not.
       - 15,000 tokens requires upstream OpenCode/runtime changes.
       - Validation incomplete; 15,000-token reachability cannot be concluded.
     - Command: Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\final-report.md" -Value "
## Conclusion
<REPLACE WITH EXACTLY ONE REQUIRED CONCLUSION LINE FROM ABOVE>
"
     - Verification: Before marking complete, confirm exactly one required conclusion line appears (verbatim match) and no TODO or <REPLACE text remains.
     - Error recovery: If measurements conflict or criteria are ambiguous, choose Validation incomplete; 15,000-token reachability cannot be concluded. and explain what must be re-run in the Caveats section.

4. - [x] **Task 6.4: Draft upstream issue recommendations if needed**
     - File/path output: `.conductor/tracks/20260531-prompt-schema-overhead-research/artifacts/upstream-issue-draft.md`
     - Command: `@("# Upstream Issue Draft", "", "## Problem", "OpenCode system prompt overhead remains high after local prompt reductions.", "", "## Requested Improvements", "- Compact/native tool schema mode.", "- Lazy-loaded MCP/plugin tool schemas.", "- Configurable Codex/account-management tool loading.", "- Compact task/subagent schema mode.", "- Tokenscope/context export reliability fix for missing Bun package import.", "", "## Evidence", "TODO: add measured artifacts and token deltas.") | Set-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\upstream-issue-draft.md" -Encoding utf8`
     - Verification: File exists and contains `Requested Improvements`.
     - Error recovery: If upstream changes are not needed, keep this file as optional and state `not needed based on measurements`.

**Phase 6 Exit Criteria:** Final report exists, measurement table is populated or unavailable measurements are explained, and conclusion line is selected.

---

## Final Phase: Validation & Handover

**Objective:** Verify artifacts, restore config, remove secrets/control characters, and prepare the track for review.

1. - [x] **Task 7.1: Verify original config was restored**
     - File/path target: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
     - Command: `Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Pattern "oc-codex-multi-auth|plugin|mcp"`
     - Verification: Output matches the expected original plugin/MCP state recorded in `effective-config-inventory.md`.
     - Error recovery: If config is not restored, restore from `artifacts/config-backups/opencode.jsonc.pre-codex-ab-test` or the newest `opencode.jsonc.backup-*` before continuing.

2. - [x] **Task 7.2: Run artifact existence check**
     - File/path output: append to `execution-log.md`
     - Command: `@("spec.md","plan.md","metadata.json","execution-log.md","artifacts\baseline-tokenscope.txt","artifacts\effective-config-inventory.md","artifacts\tool-surface-inventory.md","artifacts\codex-tool-origin-analysis.md","artifacts\schema-token-estimates.md","artifacts\ab-test-results.md","artifacts\final-report.md") | ForEach-Object { $p="C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\$_"; if(Test-Path -LiteralPath $p){ "OK $p" } else { "MISSING $p" } } | Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\execution-log.md"`
     - Verification: Execution log contains only acceptable `OK` lines, or missing optional artifacts are explained.
     - Error recovery: Create missing required artifacts or mark validation incomplete.

3. - [x] **Task 7.3: Run secret and control-character scan**
     - File/path output: append to xecution-log.md
     - Step A: Write the scan script to a temporary file (avoids PowerShell escaping issues with inline Python):
       `powershell
        = @"
import pathlib, re
base = pathlib.Path(r'C:\\development\\opencode\\.conductor\\tracks\\20260531-prompt-schema-overhead-research')
bad = []
secret = []
pats = [
    re.compile(r'xox[pbar]-[A-Za-z0-9-]+'),
    re.compile(r'sk-[A-Za-z0-9_-]{20,}'),
]
for p in base.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.md', '.txt', '.json'}:
        s = p.read_text(encoding='utf-8', errors='replace')
        for i, ch in enumerate(s):
            if (ord(ch) < 32 and ch not in '\\n\\r\\t') or ch == '\\ufffd':
                bad.append((str(p), i, ord(ch)))
        for pat in pats:
            if pat.search(s):
                secret.append(str(p))
print(f'CONTROL_BAD {len(bad)}')
print(f'SECRET_HITS {len(set(secret))}')
if bad:
    for b in bad[:5]:
        print(f'  CONTROL: {b[0]} pos={b[1]} ord={b[2]}')
if secret:
    for s in set(secret):
        print(f'  SECRET: {s}')
"@
        = "C:\\Users\\DaveWitkin\\AppData\\Local\\Temp\\opencode\\scan-secrets.py"
       Set-Content -LiteralPath  -Value  -Encoding utf8
       `
     - Step B: Run the scan script and append results to execution log:
       `powershell
       python "C:\\Users\\DaveWitkin\\AppData\\Local\\Temp\\opencode\\scan-secrets.py" | Add-Content -LiteralPath "C:\\development\\opencode\\.conductor\\tracks\\20260531-prompt-schema-overhead-research\\execution-log.md"
       `
     - Verification: Expected appended output includes CONTROL_BAD 0 and SECRET_HITS 0.
     - Error recovery: If hits are found, redact the secrets in the listed files (replace token values with <redacted>) and replace control characters with spaces, then rerun Step B.

4. - [x] **Task 7.4: Update metadata status**
     - File/path target: `.conductor/tracks/20260531-prompt-schema-overhead-research/metadata.json`
     - Command: `python -c "import json,pathlib,datetime; p=pathlib.Path(r'C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\metadata.json'); d=json.loads(p.read_text(encoding='utf-8')); d['status']='completed'; d['completed']=datetime.date.today().isoformat(); d['progress']={'completedTasks':37,'totalTasks':37,'percentage':100}; p.write_text(json.dumps(d,indent=2),encoding='utf-8')"`
     - Verification: Run `python -m json.tool "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\metadata.json"` and confirm valid JSON.
     - Error recovery: If any task remains blocked, set `status` to `blocked` or `active` and adjust completed task count rather than marking complete.

5. - [x] **Task 7.5: Update Conductor indexes**
     - File/path targets: .conductor/tracks.md, .conductor/tracks-ledger.md
     - Step A: Read the status from metadata.json to determine current phase:
       `powershell
        = Get-Content -LiteralPath "C:\\development\\opencode\\.conductor\\tracks\\20260531-prompt-schema-overhead-research\\metadata.json" -Raw | ConvertFrom-Json
        = .status
       `
     - Step B: Update tracks-ledger.md:
       `powershell
       Add-Content -LiteralPath "C:\\development\\opencode\\.conductor\\tracks-ledger.md" -Value "`n- [20260531-prompt-schema-overhead-research](./tracks/20260531-prompt-schema-overhead-research/spec.md): Research OpenCode prompt schema overhead from Codex/account tooling, MCP/plugin schemas, native tools, and task/subagent definitions. (Status: )"
       `
     - Step C: Update tracks.md - first check if an entry already exists:
       `powershell
        = "C:\\development\\opencode\\.conductor\\tracks.md"
        = Get-Content -LiteralPath  -Raw
       if ( -match '20260531-prompt-schema-overhead-research') {
           Write-Host "Entry already exists in tracks.md - verify status matches metadata.json"
       } else {
           Add-Content -LiteralPath  -Value "`n- [20260531-prompt-schema-overhead-research](./tracks/20260531-prompt-schema-overhead-research/spec.md): Prompt Schema Overhead Research (Status: )"
       }
       `
     - Verification: Run Select-String -LiteralPath "C:\\development\\opencode\\.conductor\\tracks.md" -Pattern "20260531-prompt-schema-overhead-research" and Select-String -LiteralPath "C:\\development\\opencode\\.conductor\\tracks-ledger.md" -Pattern "20260531-prompt-schema-overhead-research" - each should return exactly one match with status matching metadata.json.
     - Error recovery: If duplicate entries exist, keep the most current one and remove stale duplicates manually.

6. - [x] **Task 7.6: Append final handover summary**
     - File/path target: `.conductor/tracks/20260531-prompt-schema-overhead-research/execution-log.md`
     - Command: `Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\execution-log.md" -Value "`n## User Handover Summary`n- Track updated: yes`n- Final status: TODO completed|active|blocked`n- Final report path: C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\artifacts\final-report.md`n- Plan path: C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research\plan.md`n- Config restored: TODO yes/no`n- Recommended next action: TODO`n"`
     - Verification: Execution log contains `User Handover Summary` and absolute Windows paths.
     - Error recovery: If handover contains TODO values at final completion, do not mark metadata completed.

**Final Phase Exit Criteria:** Config is restored, required artifacts exist, scans pass, metadata and indexes agree, and handover summary is complete.

---

## Execution Readiness Checklist

| # | Standard | Pass/Fail | Evidence |
|---|---|---|---|
| 1 | Atomic tasks | PASS | Each checkbox has one primary action. Multi-step tasks are broken into labeled sub-steps (A, B, C). |
| 2 | Exact file paths | PASS | Every task names exact absolute Windows paths or repo-relative paths. |
| 3 | Explicit commands | PASS | Commands are written verbatim. 	okenscope tool invocations are explicitly distinguished from shell commands. |
| 4 | Clear ordering | PASS | Backups precede edits; baseline precedes A/B tests; restore precedes completion. Sub-steps are lettered sequentially. |
| 5 | Verification per step | PASS | Every task includes expected output, artifact validation, or a Select-String pattern check. |
| 6 | No assumed context | PASS | Token-usage output path search is documented. Tool-origin evidence paths are explicit. Prior artifact paths are absolute. |
| 7 | Concrete examples | PASS | Tables, conclusion decision criteria with numeric thresholds, artifact templates, and code blocks are included inline. |
| 8 | Error recovery | PASS | Every task includes fallback, restore, or stop instructions. JSONC corruption prevention added in Task 4.2.

## Top 3 Implementation Risks + Mitigations

1. **Codex tooling may not be controlled by the expected plugin line.**
   - Mitigation: Phase 4 requires identifying origin evidence first. If origin is unknown, the A/B test is blocked rather than guessed.

2. **Tokenscope context export may remain broken because of the missing Bun package import.**
   - Mitigation: Phase 3 documents export diagnostics and permits fallback measurement through fresh-session telemetry deltas and schema text estimates.

3. **A/B config edits could temporarily break OpenCode startup.**
   - Mitigation: Phase 0 and Phase 4 create backups before edits, require immediate restore after measurement, and provide exact restore commands.

## First Task the Build Agent Should Execute Immediately

Execute **Task 0.1: Confirm the active track directory exists** with:

```powershell
Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260531-prompt-schema-overhead-research"
```

Continue to Task 0.2 only if the command returns `True`.







