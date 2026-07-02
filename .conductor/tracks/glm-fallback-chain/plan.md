# Plan: GLM fallback chain

Track ID: `glm-fallback-chain`

## Stage 1 restatement

### Goal / outcome
Implement a procedural three-tier fallback chain for Conductor pipeline GLM-5.2 failures: retry `zai-coding-plan/glm-5.2`, then route Stage 4 execution to `zai-coding-plan/glm-5.1`, then to `opencode-go/qwen3.7-plus`, with provider timeouts that identify failures and documentation that explains the orchestrator self-swap limitation.

### Constraints / non-goals
- Do not add or rely on nonexistent native OpenCode fallback such as `fallbackModels`.
- Do not claim the orchestrator can override subagent models or swap its own model at runtime.
- Scope is limited to the two GLM-5.2 pipeline agents, provider timeout configuration, fallback executor agents, and Conductor pipeline docs.
- Preserve validator/executor model diversity.
- Execute shell-first via PowerShell 7+ through `bash`; do not retry native file tools if `Bun is not defined` appears.
- Use `-LiteralPath` and double-quoted Windows paths.
- Back up `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` before editing.

### Definition of done
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` and `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md` contain the exact three-tier fallback table, failure signals, retry counts, subagent names, diversity note, and orchestrator self-swap limitation.
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md` and `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md` exist with `hidden: true` and correct pinned models.
- The orchestrator permission block and body allow/describe routing to all three executor variants.
- `opencode.jsonc` contains timeout options for `zai-coding-plan` and `opencode-go`, and a timestamped backup exists.
- Final validation confirms model availability, agent frontmatter, JSONC parse, and orchestrator executor permissions.

## Tool / environment preflight for executor
- Native Read/Edit/Write/glob/grep status: unavailable in this session due to `Bun is not defined`.
- Fallback shell: PowerShell 7+ via `bash`.
- Cmdlet mapping: read with `Get-Content -Raw`; write with `Set-Content -Encoding utf8`; locate with `Select-String`; literal edits with `[string]::Replace()`; do not use regex `-replace` for structural edits.
- Path quoting: use `-LiteralPath` and double-quoted paths.

## Phase 0 Setup & Preconditions

Objective: Establish a safe backup and confirm target anchors before edits.

- [x] Task 0.1: Create a timestamped backup of `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
  - Action command:
    ```powershell
    $ts = Get-Date -Format "yyyyMMdd-HHmmss"; $src = "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"; $backup = "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.glm-fallback-chain.$ts.bak"; if (-not (Test-Path -LiteralPath $src)) { throw "Missing source: $src" }; Copy-Item -LiteralPath $src -Destination $backup; $backup | Set-Content -Encoding utf8 -LiteralPath "C:\development\opencode\.conductor\tracks\glm-fallback-chain\opencode-jsonc-backup-path.txt"
    ```
  - Authoritative acceptance check:
    ```powershell
    $backup = (Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\glm-fallback-chain\opencode-jsonc-backup-path.txt").Trim(); $source = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"; $copy = Get-Content -Raw -LiteralPath $backup; if ($source -ne $copy) { throw "Backup body does not exactly match opencode.jsonc" }; "OK backup exact body copy: $backup"
    ```
  - Diagnostic checks:
    ```powershell
    Get-Item -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"
    ```
  - Error recovery: If the track folder is missing, create it with `New-Item -ItemType Directory -Force -Path "C:\development\opencode\.conductor\tracks\glm-fallback-chain"` and rerun.

- [x] Task 0.2: Verify existing orchestrator and executor body anchors.
  - Action command:
    ```powershell
    $files = @("C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md", "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md"); foreach ($file in $files) { if (-not (Test-Path -LiteralPath $file)) { throw "Missing required file: $file" } }
    ```
  - Authoritative acceptance check:
    ```powershell
    $orch = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md"; $exec = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md"; if (-not ($orch.Contains("model: zai-coding-plan/glm-5.2") -and $orch.Contains("conductor-track-executor") -and $exec.Contains("model: zai-coding-plan/glm-5.2") -and $exec.Contains("You are a Conductor track execution specialist"))) { throw "Required body anchors missing" }; "OK existing GLM-5.2 orchestrator/executor body anchors verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md" -SimpleMatch "conductor-track-executor", "model: zai-coding-plan/glm-5.2"
    ```
  - Error recovery: If anchors differ, print the first 80 lines with `Get-Content -LiteralPath "<file>" -TotalCount 80` and ask for review.

Exit criteria: Backup exists and required source anchors are verified.

## Phase 1 Provider timeout detection

Objective: Add provider timeout options so freezes become detectable failures.

- [x] Task 1.1: Add timeout options to the `zai-coding-plan` provider block in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
  - Required body content:
    ```jsonc
    "options": {
      "timeout": 600000,
      "headerTimeout": 60000,
      "chunkTimeout": 120000
    }
    ```
  - Action command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"; $text = Get-Content -Raw -LiteralPath $path; $zcIdx = $text.IndexOf('"zai-coding-plan"'); if ($zcIdx -lt 0) { throw "Missing zai-coding-plan provider" }; $i = $text.IndexOf('{', $zcIdx); $depth = 0; $blockEnd = -1; for ($k = $i; $k -lt $text.Length; $k++) { $ch = $text[$k]; if ($ch -eq '{') { $depth++ } elseif ($ch -eq '}') { $depth--; if ($depth -eq 0) { $blockEnd = $k; break } } }; if ($blockEnd -lt 0) { throw "Could not locate end of zai-coding-plan block" }; $insertion = "," + "`n      " + [char]34 + "options" + [char]34 + ": {" + "`n        " + [char]34 + "timeout" + [char]34 + ": 600000," + "`n        " + [char]34 + "headerTimeout" + [char]34 + ": 60000," + "`n        " + [char]34 + "chunkTimeout" + [char]34 + ": 120000" + "`n      }" + "`n    "; $text = $text.Substring(0, $blockEnd) + $insertion + $text.Substring($blockEnd); Set-Content -Encoding utf8 -LiteralPath $path -Value $text
    ```
  - Authoritative acceptance check:
    ```powershell
    $text = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"; $i = $text.IndexOf('"zai-coding-plan"'); if ($i -lt 0) { throw "Missing zai-coding-plan provider" }; $w = $text.Substring($i, [Math]::Min(2500, $text.Length - $i)); foreach ($literal in @('"options": {','"timeout": 600000','"headerTimeout": 60000','"chunkTimeout": 120000')) { if (-not $w.Contains($literal)) { throw "zai-coding-plan provider body missing $literal" } }; "OK zai-coding-plan provider timeout body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -SimpleMatch '"zai-coding-plan"', '"timeout": 600000'
    ```
  - Error recovery: If JSONC becomes invalid, restore from the backup path in `opencode-jsonc-backup-path.txt` and reapply narrowly.

- [x] Task 1.2: Add an `opencode-go` provider block with matching timeout options in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
  - Required body content:
    ```jsonc
    "opencode-go": {
      "options": {
        "timeout": 600000,
        "headerTimeout": 60000,
        "chunkTimeout": 120000
      }
    }
    ```
  - Action command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"; $text = Get-Content -Raw -LiteralPath $path; if ($text.Contains('"opencode-go"')) { "opencode-go provider already present, skipping" } else { $zcIdx = $text.IndexOf('"zai-coding-plan"'); if ($zcIdx -lt 0) { throw "Missing zai-coding-plan provider" }; $i = $text.IndexOf('{', $zcIdx); $depth = 0; $zcBlockEnd = -1; for ($k = $i; $k -lt $text.Length; $k++) { $ch = $text[$k]; if ($ch -eq '{') { $depth++ } elseif ($ch -eq '}') { $depth--; if ($depth -eq 0) { $zcBlockEnd = $k; break } } }; if ($zcBlockEnd -lt 0) { throw "Could not locate end of zai-coding-plan block" }; $ogIns = "," + "`n    " + [char]34 + "opencode-go" + [char]34 + ": {" + "`n      " + [char]34 + "options" + [char]34 + ": {" + "`n        " + [char]34 + "timeout" + [char]34 + ": 600000," + "`n        " + [char]34 + "headerTimeout" + [char]34 + ": 60000," + "`n        " + [char]34 + "chunkTimeout" + [char]34 + ": 120000" + "`n      }" + "`n    }"; $text = $text.Insert($zcBlockEnd + 1, $ogIns); Set-Content -Encoding utf8 -LiteralPath $path -Value $text }
    ```
  - Authoritative acceptance check:
    ```powershell
    $text = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"; $i = $text.IndexOf('"opencode-go"'); if ($i -lt 0) { throw "Missing opencode-go provider block" }; $w = $text.Substring($i, [Math]::Min(1200, $text.Length - $i)); foreach ($literal in @('"options": {','"timeout": 600000','"headerTimeout": 60000','"chunkTimeout": 120000')) { if (-not $w.Contains($literal)) { throw "opencode-go provider body missing $literal" } }; "OK opencode-go provider timeout body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -SimpleMatch '"opencode-go"', '"chunkTimeout": 120000'
    ```
  - Error recovery: If placement is unclear, stop and inspect the top-level provider section; do not add a duplicate top-level key.

Exit criteria: Both providers contain identical timeout option bodies.

## Phase 2 Fallback executor subagents

Objective: Create concrete fallback executor agents and self-failure reporting.

- [x] Task 2.1: Create `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md` from the primary executor with `model: zai-coding-plan/glm-5.1`, `hidden: true`, and a Tier 2 note.
  - Required body note: `Fallback tier: Tier 2 executor for the Conductor pipeline. Invoke only after `conductor-track-executor` on `zai-coding-plan/glm-5.2` is unavailable after the documented retry policy.`
  - Action command:
    ```powershell
    $src = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md"; $dst = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md"; $text = Get-Content -Raw -LiteralPath $src; $text = $text.Replace("model: zai-coding-plan/glm-5.2", "model: zai-coding-plan/glm-5.1"); if (-not $text.Contains("hidden: true")) { $text = $text.Replace("---`nname:", "---`nhidden: true`nname:") }; $tierNote = @'Fallback tier: Tier 2 executor for the Conductor pipeline. Invoke only after `conductor-track-executor` on `zai-coding-plan/glm-5.2` is unavailable after the documented retry policy.'@; if (-not $text.Contains($tierNote)) { $text = $text.TrimEnd() + "`n`n" + $tierNote + "`n" }; Set-Content -Encoding utf8 -LiteralPath $dst -Value $text
    ```
  - Authoritative acceptance check:
    ```powershell
    $b = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md"; foreach ($literal in @('model: zai-coding-plan/glm-5.1', 'hidden: true', 'Fallback tier: Tier 2 executor for the Conductor pipeline. Invoke only after `conductor-track-executor` on `zai-coding-plan/glm-5.2` is unavailable after the documented retry policy.', 'You are the **Conductor Track Executor** (Stage 4).')) { if (-not $b.Contains($literal)) { throw "GLM-5.1 fallback executor body missing $literal" } }; "OK GLM-5.1 fallback executor body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md" -SimpleMatch "model: zai-coding-plan/glm-5.1", "hidden: true"
    ```
  - Error recovery: If `hidden: true` is outside frontmatter, rewrite the frontmatter between the opening and closing `---` markers.

- [x] Task 2.2: Create `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md` from the primary executor with `model: opencode-go/qwen3.7-plus`, `hidden: true`, and a Tier 3 note.
  - Required body note: `Fallback tier: Tier 3 last-resort executor for the Conductor pipeline. Invoke only after `conductor-track-executor-glm51` on `zai-coding-plan/glm-5.1` is unavailable after the documented retry policy.`
  - Action command:
    ```powershell
    $src = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md"; $dst = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md"; $text = Get-Content -Raw -LiteralPath $src; $text = $text.Replace("model: zai-coding-plan/glm-5.2", "model: opencode-go/qwen3.7-plus"); if (-not $text.Contains("hidden: true")) { $text = $text.Replace("---`nname:", "---`nhidden: true`nname:") }; $tierNote = @'Fallback tier: Tier 3 last-resort executor for the Conductor pipeline. Invoke only after `conductor-track-executor-glm51` on `zai-coding-plan/glm-5.1` is unavailable after the documented retry policy.'@; if (-not $text.Contains($tierNote)) { $text = $text.TrimEnd() + "`n`n" + $tierNote + "`n" }; Set-Content -Encoding utf8 -LiteralPath $dst -Value $text
    ```
  - Authoritative acceptance check:
    ```powershell
    $b = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md"; foreach ($literal in @('model: opencode-go/qwen3.7-plus', 'hidden: true', 'Fallback tier: Tier 3 last-resort executor for the Conductor pipeline. Invoke only after `conductor-track-executor-glm51` on `zai-coding-plan/glm-5.1` is unavailable after the documented retry policy.', 'You are the **Conductor Track Executor** (Stage 4).')) { if (-not $b.Contains($literal)) { throw "Qwen fallback executor body missing $literal" } }; "OK Qwen fallback executor body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md" -SimpleMatch "model: opencode-go/qwen3.7-plus", "hidden: true"
    ```
  - Error recovery: If the source executor changed during this task, recreate both fallback agents from the updated source.

- [x] Task 2.3: Update `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md` to report `model-unavailable` when its own provider/model fails mid-task.
  - Required body content: `If this executor detects its own model/provider failing mid-task (timeout, abort, HTTP 429/5xx, connection refused, no or empty response, chunk timeout, freeze, or unreachable provider), stop immediately and report `model-unavailable` with the attempted model, stage, track ID, failure signal, and last completed task. Leave incomplete tasks unchecked so the orchestrator can route the track to the next fallback tier.`
  - Action command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md"; $text = Get-Content -Raw -LiteralPath $path; $insert = @'If this executor detects its own model/provider failing mid-task (timeout, abort, HTTP 429/5xx, connection refused, no or empty response, chunk timeout, freeze, or unreachable provider), stop immediately and report `model-unavailable` with the attempted model, stage, track ID, failure signal, and last completed task. Leave incomplete tasks unchecked so the orchestrator can route the track to the next fallback tier.'@; if (-not $text.Contains($insert)) { $text = $text + "`r`n`r`n" + $insert + "`r`n"; Set-Content -Encoding utf8 -LiteralPath $path -Value $text }
    ```
  - Authoritative acceptance check:
    ```powershell
    $b = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md"; $literal = @'If this executor detects its own model/provider failing mid-task (timeout, abort, HTTP 429/5xx, connection refused, no or empty response, chunk timeout, freeze, or unreachable provider), stop immediately and report `model-unavailable` with the attempted model, stage, track ID, failure signal, and last completed task. Leave incomplete tasks unchecked so the orchestrator can route the track to the next fallback tier.'@; if (-not $b.Contains($literal)) { throw "Executor self-failure body content missing" }; "OK executor model-unavailable body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md" -SimpleMatch "model-unavailable", "next fallback tier"
    ```
  - Error recovery: If the sentence is duplicated, remove duplicate copies with literal `[string]::Replace()` and leave one complete copy.

Exit criteria: Fallback agents exist and primary executor reports model failure clearly.

## Phase 3 Orchestrator routing

Objective: Allow and instruct the orchestrator to use all executor tiers.

- [x] Task 3.1: Update `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md` `permission.task` to include `conductor-track-executor`, `conductor-track-executor-glm51`, and `conductor-track-executor-qwen`.
  - Action command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md"; $text = Get-Content -Raw -LiteralPath $path; if (-not $text.Contains("conductor-track-executor-glm51")) { $marker = "    conductor-track-executor: allow"; if (([regex]::Matches($text, [regex]::Escape($marker))).Count -ne 1) { throw "Expected exactly 1 permission marker line; got $(([regex]::Matches($text, [regex]::Escape($marker))).Count)" }; $text = $text.Replace($marker, $marker + "`n    conductor-track-executor-glm51: allow`n    conductor-track-executor-qwen: allow"); Set-Content -Encoding utf8 -LiteralPath $path -Value $text }
    ```
  - Authoritative acceptance check:
    ```powershell
    $b = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md"; $i = $b.IndexOf("permission:"); if ($i -lt 0) { throw "Missing permission block" }; $w = $b.Substring($i, [Math]::Min(1500, $b.Length - $i)); foreach ($agent in @("conductor-track-executor", "conductor-track-executor-glm51", "conductor-track-executor-qwen")) { if (-not $w.Contains($agent)) { throw "Orchestrator permission body missing $agent" } }; "OK orchestrator permission body lists all executor variants"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md" -SimpleMatch "conductor-track-executor-glm51", "conductor-track-executor-qwen"
    ```
  - Error recovery: If entries duplicate, normalize the `permission.task` list manually to one line per executor.

- [x] Task 3.2: Add explicit Stage 4 retry/fallback routing instructions to the orchestrator body.
  - Required body content: `Stage 4 model fallback chain: first invoke `conductor-track-executor` on `zai-coding-plan/glm-5.2`. On transient failure signals (timeout, abort, HTTP 429/5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze), retry the same tier up to two additional attempts with brief backoff. If Tier 1 remains unavailable, log `model-unavailable` and route to `conductor-track-executor-glm51` on `zai-coding-plan/glm-5.1` with the same retry policy. If Tier 2 remains unavailable, log `model-unavailable` and route to `conductor-track-executor-qwen` on `opencode-go/qwen3.7-plus` with the same retry policy. If Tier 3 fails, log `model-unavailable` with the attempted model, stage, tier, and failure signal, then stop and ask the user. Record the tier actually used in the execution handoff/log. Diversity remains intact because every executor tier differs from validator `opencode-go/minimax-m3`.`
  - Action command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md"; $text = Get-Content -Raw -LiteralPath $path; $insert = @'Stage 4 model fallback chain: first invoke `conductor-track-executor` on `zai-coding-plan/glm-5.2`. On transient failure signals (timeout, abort, HTTP 429/5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze), retry the same tier up to two additional attempts with brief backoff. If Tier 1 remains unavailable, log `model-unavailable` and route to `conductor-track-executor-glm51` on `zai-coding-plan/glm-5.1` with the same retry policy. If Tier 2 remains unavailable, log `model-unavailable` and route to `conductor-track-executor-qwen` on `opencode-go/qwen3.7-plus` with the same retry policy. If Tier 3 fails, log `model-unavailable` with the attempted model, stage, tier, and failure signal, then stop and ask the user. Record the tier actually used in the execution handoff/log. Diversity remains intact because every executor tier differs from validator `opencode-go/minimax-m3`.'@; if (-not $text.Contains($insert)) { Set-Content -Encoding utf8 -LiteralPath $path -Value ($text.TrimEnd() + "`n`n## Stage 4 model fallback routing`n`n" + $insert + "`n") }
    ```
  - Authoritative acceptance check:
    ```powershell
    $b = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md"; foreach ($literal in @('Stage 4 model fallback chain: first invoke `conductor-track-executor` on `zai-coding-plan/glm-5.2`.', 'retry the same tier up to two additional attempts with brief backoff', 'route to `conductor-track-executor-glm51` on `zai-coding-plan/glm-5.1`', 'route to `conductor-track-executor-qwen` on `opencode-go/qwen3.7-plus`', 'Record the tier actually used in the execution handoff/log')) { if (-not $b.Contains($literal)) { throw "Orchestrator fallback routing body missing $literal" } }; "OK orchestrator fallback routing body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md" -SimpleMatch "Stage 4 model fallback chain", "Record the tier actually used"
    ```
  - Error recovery: If duplicate sections appear, keep one complete section and remove incomplete duplicates.

Exit criteria: Orchestrator permissions and body support all fallback tiers.

## Phase 4 Documentation synchronization

Objective: Keep pipeline docs aligned with implemented behavior.

- [x] Task 4.1: Add a concrete fallback chain section to `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`.
  - Action command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md"; $text = Get-Content -Raw -LiteralPath $path; $section = @'

## Model fallback chain

| Tier | Stage 4 executor subagent | Model | Use |
|---|---|---|---|
| 1 | `conductor-track-executor` | `zai-coding-plan/glm-5.2` | Primary GLM-5.2 executor via Z.AI |
| 2 | `conductor-track-executor-glm51` | `zai-coding-plan/glm-5.1` | First fallback via Z.AI |
| 3 | `conductor-track-executor-qwen` | `opencode-go/qwen3.7-plus` | Last-resort fallback via OpenCode Go |

Transient failure signals: timeout/abort, HTTP 429, HTTP 5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze, or stream stall.

Retry policy: retry the same tier up to two additional attempts with brief backoff, then escalate to the next tier. If Tier 3 fails, log `model-unavailable` with attempted model, stage, tier, and failure signal, then stop and ask the user.

Diversity note: executor fallback preserves validation diversity because `zai-coding-plan/glm-5.2`, `zai-coding-plan/glm-5.1`, and `opencode-go/qwen3.7-plus` all differ from validator `opencode-go/minimax-m3`.

Orchestrator self-swap limitation: the orchestrator is pinned to `zai-coding-plan/glm-5.2` and cannot self-swap at runtime. Provider timeouts prevent indefinite hangs; if the orchestrator's own model is unavailable, restart OpenCode after the failure is surfaced, optionally after changing the orchestrator `model:` line to a fallback tier so configuration is re-read on startup.
'@; if (-not $text.Contains("## Model fallback chain")) { Set-Content -Encoding utf8 -LiteralPath $path -Value ($text.TrimEnd() + $section) } else { throw "Update existing Model fallback chain section in place to match required body content" }
    ```
  - Authoritative acceptance check:
    ```powershell
    $b = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md"; foreach ($literal in @('| 1 | `conductor-track-executor` | `zai-coding-plan/glm-5.2` | Primary GLM-5.2 executor via Z.AI |', '| 2 | `conductor-track-executor-glm51` | `zai-coding-plan/glm-5.1` | First fallback via Z.AI |', '| 3 | `conductor-track-executor-qwen` | `opencode-go/qwen3.7-plus` | Last-resort fallback via OpenCode Go |', 'Transient failure signals: timeout/abort, HTTP 429, HTTP 5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze, or stream stall.', 'Retry policy: retry the same tier up to two additional attempts with brief backoff', 'Orchestrator self-swap limitation: the orchestrator is pinned to `zai-coding-plan/glm-5.2` and cannot self-swap at runtime.')) { if (-not $b.Contains($literal)) { throw "threshold-policy.md missing body literal: $literal" } }; "OK threshold-policy fallback body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md" -SimpleMatch "Model fallback chain", "Orchestrator self-swap limitation"
    ```
  - Error recovery: If the old vague fallback line remains, replace it with a pointer to `## Model fallback chain`.

- [x] Task 4.2: Add a fallback chain section to `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`.
  - Action command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md"; $text = Get-Content -Raw -LiteralPath $path; $section = @'

## Model fallback chain

Stage 4 execution uses a procedural fallback chain because OpenCode agents have one pinned `model:` and no native `fallbackModels` field.

| Tier | Subagent | Model |
|---|---|---|
| 1 | `conductor-track-executor` | `zai-coding-plan/glm-5.2` |
| 2 | `conductor-track-executor-glm51` | `zai-coding-plan/glm-5.1` |
| 3 | `conductor-track-executor-qwen` | `opencode-go/qwen3.7-plus` |

Retry transient failure signals (timeout/abort, HTTP 429/5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze) on the same tier up to two additional attempts, then escalate. If Tier 3 fails, log `model-unavailable` and stop.

Diversity remains intact because each executor tier differs from validator `opencode-go/minimax-m3`.

Orchestrator limitation: the orchestrator itself remains pinned to `zai-coding-plan/glm-5.2` and cannot self-swap at runtime; provider timeouts fail fast, and recovery is to restart OpenCode, optionally after changing the orchestrator `model:` line to a fallback tier.
'@; if (-not $text.Contains("## Model fallback chain")) { Set-Content -Encoding utf8 -LiteralPath $path -Value ($text.TrimEnd() + $section) } else { throw "Update existing Model fallback chain section in place to match required body content" }
    ```
  - Authoritative acceptance check:
    ```powershell
    $b = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md"; foreach ($literal in @('Stage 4 execution uses a procedural fallback chain because OpenCode agents have one pinned `model:` and no native `fallbackModels` field.', '| 2 | `conductor-track-executor-glm51` | `zai-coding-plan/glm-5.1` |', '| 3 | `conductor-track-executor-qwen` | `opencode-go/qwen3.7-plus` |', 'Retry transient failure signals (timeout/abort, HTTP 429/5xx, connection refused, unreachable provider, no or empty response, chunk timeout, freeze) on the same tier up to two additional attempts, then escalate.', 'Diversity remains intact because each executor tier differs from validator `opencode-go/minimax-m3`.', 'Orchestrator limitation: the orchestrator itself remains pinned to `zai-coding-plan/glm-5.2` and cannot self-swap at runtime;')) { if (-not $b.Contains($literal)) { throw "SKILL.md missing body literal: $literal" } }; "OK SKILL.md fallback body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md" -SimpleMatch "Model fallback chain", "conductor-track-executor-qwen"
    ```
  - Error recovery: If a fallback section already exists, update it in place; do not create duplicate competing policies.

- [x] Task 4.3: Add a Stage 4 fallback model table to `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md`.
  - Action command:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md"; $text = Get-Content -Raw -LiteralPath $path; $section = @'

## Stage 4 fallback model table

| Tier | Subagent | Model | Notes |
|---|---|---|---|
| 1 | `conductor-track-executor` | `zai-coding-plan/glm-5.2` | Primary executor |
| 2 | `conductor-track-executor-glm51` | `zai-coding-plan/glm-5.1` | First fallback after Tier 1 retries fail |
| 3 | `conductor-track-executor-qwen` | `opencode-go/qwen3.7-plus` | Last resort after Tier 2 retries fail |

The orchestrator remains pinned to `zai-coding-plan/glm-5.2`; it uses this table only to route Stage 4 executor subagents after detectable failures.
'@; if (-not $text.Contains("## Stage 4 fallback model table")) { Set-Content -Encoding utf8 -LiteralPath $path -Value ($text.TrimEnd() + $section) } else { throw "Update existing Stage 4 fallback model table in place to match required body content" }
    ```
  - Authoritative acceptance check:
    ```powershell
    $b = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md"; foreach ($literal in @('| 1 | `conductor-track-executor` | `zai-coding-plan/glm-5.2` | Primary executor |', '| 2 | `conductor-track-executor-glm51` | `zai-coding-plan/glm-5.1` | First fallback after Tier 1 retries fail |', '| 3 | `conductor-track-executor-qwen` | `opencode-go/qwen3.7-plus` | Last resort after Tier 2 retries fail |', 'The orchestrator remains pinned to `zai-coding-plan/glm-5.2`; it uses this table only to route Stage 4 executor subagents after detectable failures.')) { if (-not $b.Contains($literal)) { throw "README.md missing body literal: $literal" } }; "OK README fallback body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md" -SimpleMatch "Stage 4 fallback model table", "orchestrator remains pinned"
    ```
  - Error recovery: If README has an existing model section, place this table there but preserve exact body content.

Exit criteria: Policy, SKILL, and README all state the fallback chain in body text.

## Final Phase Validation & Handover

Objective: Prove model IDs, frontmatter, JSONC, permissions, and docs are correct.

- [x] Task 5.1: Validate `opencode models` contains all three model IDs.
  - Action command:
    ```powershell
    opencode models | Set-Content -Encoding utf8 -LiteralPath "C:\development\opencode\.conductor\tracks\glm-fallback-chain\opencode-models-output.txt"
    ```
  - Authoritative acceptance check:
    ```powershell
    $b = Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\glm-fallback-chain\opencode-models-output.txt"; foreach ($model in @("zai-coding-plan/glm-5.2", "zai-coding-plan/glm-5.1", "opencode-go/qwen3.7-plus")) { if (-not $b.Contains($model)) { throw "opencode models output missing $model" } }; "OK all fallback model IDs present"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\glm-fallback-chain\opencode-models-output.txt" -SimpleMatch "zai-coding-plan/glm-5.2", "zai-coding-plan/glm-5.1", "opencode-go/qwen3.7-plus"
    ```
  - Error recovery: If `opencode models` fails due to auth/network, rerun once; if it still fails, record the failure and stop.

- [x] Task 5.2: Validate agent frontmatter and orchestrator permissions.
  - Action command:
    ```powershell
    "Run the authoritative acceptance check for agent body content."
    ```
  - Authoritative acceptance check:
    ```powershell
    $primary = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md"; $glm51 = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md"; $qwen = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md"; $orch = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md"; if (-not $primary.Contains("model: zai-coding-plan/glm-5.2")) { throw "Primary executor model pin wrong" }; if (-not ($glm51.Contains("model: zai-coding-plan/glm-5.1") -and $glm51.Contains("hidden: true"))) { throw "GLM-5.1 fallback frontmatter wrong" }; if (-not ($qwen.Contains("model: opencode-go/qwen3.7-plus") -and $qwen.Contains("hidden: true"))) { throw "Qwen fallback frontmatter wrong" }; $perm = $orch.Substring($orch.IndexOf("permission:"), [Math]::Min(1500, $orch.Length - $orch.IndexOf("permission:"))); foreach ($agent in @("conductor-track-executor", "conductor-track-executor-glm51", "conductor-track-executor-qwen")) { if (-not $perm.Contains($agent)) { throw "Orchestrator permission block missing $agent" } }; "OK agent frontmatter and orchestrator permission body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md" -SimpleMatch "model: opencode-go/qwen3.7-plus", "hidden: true"
    ```
  - Error recovery: If the permission block is longer than 1500 characters, increase the window to 3000 and rerun before editing.

- [x] Task 5.3: Validate `opencode.jsonc` parses with a JSONC-tolerant parser and provider timeout bodies are present.
  - Action command:
    ```powershell
    node -e "const fs=require('fs'); const p='C:\\Users\\DaveWitkin\\.config\\opencode\\opencode.jsonc'; let s=fs.readFileSync(p,'utf8'); s=s.replace(/\/\*[\s\S]*?\*\//g,'').replace(/(^|[^:])\/\/.*$/gm,'$1').replace(/,\s*([}\]])/g,'$1'); JSON.parse(s); console.log('JSONC parse OK')"
    ```
  - Authoritative acceptance check:
    ```powershell
    $path = "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"; node -e "const fs=require('fs'); const p=process.argv[1]; let s=fs.readFileSync(p,'utf8'); s=s.replace(/\/\*[\s\S]*?\*\//g,'').replace(/(^|[^:])\/\/.*$/gm,'$1').replace(/,\s*([}\]])/g,'$1'); const cfg=JSON.parse(s); const providers=cfg.provider || cfg.providers || {}; for (const name of ['zai-coding-plan','opencode-go']) { const b=providers[name]; if(!b||!b.options||b.options.timeout!==600000||b.options.headerTimeout!==60000||b.options.chunkTimeout!==120000){ throw new Error(name+' timeout options missing or wrong'); }} console.log('OK JSONC parses and provider timeout option bodies verified');" $path
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -SimpleMatch '"zai-coding-plan"', '"opencode-go"', '"chunkTimeout": 120000'
    ```
  - Error recovery: If parsing fails, restore from backup and reapply provider edits narrowly.

- [x] Task 5.4: Validate docs contain full body content for the chain, failure signals, retry count, subagents, diversity, and limitation.
  - Action command:
    ```powershell
    "Run the authoritative acceptance check for documentation body content."
    ```
  - Authoritative acceptance check:
    ```powershell
    $skill = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md"; $policy = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md"; foreach ($literal in @('`zai-coding-plan/glm-5.2`', '`zai-coding-plan/glm-5.1`', '`opencode-go/qwen3.7-plus`', 'timeout/abort', 'HTTP 429', 'HTTP 5xx', 'retry the same tier up to two additional attempts', 'conductor-track-executor-glm51', 'conductor-track-executor-qwen', 'Diversity', 'cannot self-swap at runtime')) { if (-not ($skill.Contains($literal) -and $policy.Contains($literal))) { throw "Docs missing required body literal in both files: $literal" } }; "OK SKILL.md and threshold-policy.md documentation body verified"
    ```
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md" -SimpleMatch "Model fallback chain", "cannot self-swap at runtime"
    ```
  - Error recovery: If a literal is missing, update the relevant fallback section; do not add disconnected keywords just to pass the check.

- [x] Task 5.5: Write execution log for `glm-fallback-chain`.
  - Action command:
    ```powershell
    $date = Get-Date -Format "yyyy-MM-dd"; $log = "C:\development\opencode\.conductor\tracks\glm-fallback-chain\execution-log-$date.md"; @"
# Execution Log: glm-fallback-chain

Date: $date

## Changed files
- C:\Users\DaveWitkin\.config\opencode\opencode.jsonc
- C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md
- C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md
- C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md
- C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md
- C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md
- C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md
- C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md

## Validation performed
Record exact results from Tasks 5.1 through 5.4.

## Deviations / skipped items / ambiguity
Record any deviations. If none, write: No deviations, skipped items, or ambiguities.
"@ | Set-Content -Encoding utf8 -LiteralPath $log
    ```
  - Authoritative acceptance check:
    ```powershell
    $date = Get-Date -Format "yyyy-MM-dd"; $log = "C:\development\opencode\.conductor\tracks\glm-fallback-chain\execution-log-$date.md"; $b = Get-Content -Raw -LiteralPath $log; foreach ($literal in @("# Execution Log: glm-fallback-chain", "## Changed files", "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md", "## Validation performed", "## Deviations / skipped items / ambiguity")) { if (-not $b.Contains($literal)) { throw "Execution log missing body literal: $literal" } }; "OK execution log body verified: $log"
    ```
  - Diagnostic checks:
    ```powershell
    Get-Item -LiteralPath "C:\development\opencode\.conductor\tracks\glm-fallback-chain"
    ```
  - Error recovery: If any validation task failed, document the unresolved failure and leave the track open.

Exit criteria: Model IDs, frontmatter, JSONC, permissions, docs, and handover log are verified.

## Execution-readiness checklist
- [ ] Execute tasks strictly in order.
- [ ] Check off each completed task immediately in this plan.
- [ ] Use PowerShell-first commands through `bash`, with `-LiteralPath` and double-quoted Windows paths.
- [ ] Do not rely on native fallback schema support or `fallbackModels`.
- [ ] Back up `opencode.jsonc` before editing.
- [ ] Use exactly one authoritative acceptance check per task and keep diagnostics separate.
- [ ] Verify body content, not just headings.

## Top 3 risks and mitigations
1. Risk: `opencode.jsonc` provider structure differs from expected and edits create invalid JSONC. Mitigation: back up first, scope edits narrowly, validate with JSONC-tolerant parser, restore on failure.
2. Risk: Orchestrator permission edit duplicates or corrupts the task list. Mitigation: use the body-window acceptance check and normalize to one executor per line.
3. Risk: Documentation contains keywords without usable procedure. Mitigation: acceptance checks require full body literals for table, signals, retry count, diversity, and limitation.

## First task to execute
Start with Task 0.1: create and verify a timestamped backup of `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` before any edits.







