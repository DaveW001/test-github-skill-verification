# Plan: Conductor Pipeline `write`-Permission Fix + Anomaly Logging

## Conventions used in every task
- **Timestamp format for backups and rotation archives:** `yyyyMMdd-HHmmss` (PowerShell: `(Get-Date).ToString('yyyyMMdd-HHmmss')`). Captured once at session start; reused everywhere.
- **Anchored PowerShell edit pattern:** for every "add `write: allow`" task, the executor MUST use literal `[string]::Replace()` with a verbatim multi-line `oldString` (NOT regex `-replace`). See `references/powershell-edit-hazards.md` in the conductor-pipeline skill.
- **Native file tools may be down (`Bun is not defined`):** when that happens, the session is shell-first via `bash`. Use `Get-Content -Raw -LiteralPath`, `[string]::Replace()`, and `Set-Content -Encoding utf8 -LiteralPath`. Do not retry the failing native tool per-call.
- **Authoritative acceptance check vs. diagnostic checks:** each task names exactly ONE authoritative check (the single command that proves success). Diagnostic checks are listed under "Diagnostic checks:" and do not count as proof.
- **Frontmatter parse-safety:** opencode.jsonc currently has duplicate `Retro`/`retro` keys, so it does NOT parse with bare `ConvertFrom-Json`. All JSON parse checks MUST use `ConvertFrom-Json -AsHashtable`.

## Phase 1 - Backups
- [x] 1.1 Timestamped backup of `opencode.jsonc` (path `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` -> `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.pre-write-permission-fix-<ts>`, where `<ts>` is captured once at session start via `$ts = (Get-Date).ToString('yyyyMMdd-HHmmss')`).
  - **Authoritative acceptance check:** `Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.pre-write-permission-fix-$ts"` returns `True`; backup file byte count equals source file byte count: `(Get-Item -LiteralPath "source").Length -eq (Get-Item -LiteralPath "backup").Length`.
  - **Diagnostic checks:** `Get-FileHash` of backup matches source at the moment of backup; `git diff --no-index` against backup produces no diff for a fresh backup.

- [x] 1.2 For each of the nine agent files in `C:\Users\DaveWitkin\.config\opencode\agent\` (conductor-plan-creator.md, conductor-plan-reviewer.md, conductor-plan-reviewer-alt.md, conductor-track-executor.md, conductor-track-executor-glm51.md, conductor-track-executor-qwen.md, conductor-pipeline-orchestrator.md, conductor-track-validator.md, conductor-track-validator-alt.md), copy to a sibling `.<name>.pre-write-permission-fix.bak` next to the source (e.g. `conductor-plan-creator.md.pre-write-permission-fix.bak`).
  - **Authoritative acceptance check:** for each of the nine agents, both `Test-Path -LiteralPath "<agent>.pre-write-permission-fix.bak"` returns `True` AND `(Get-Item "<agent>").Length -eq (Get-Item "<agent>.pre-write-permission-fix.bak").Length`.
  - **Error recovery:** if a `.bak` already exists from a prior run, do not overwrite silently; rename the existing one to `.<name>.pre-write-permission-fix.bak.<ts>.archive` and record the rename in the execution log.

- [x] 1.3 Backup three reference files: `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`, `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`, and `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md`. Use the same `.pre-write-permission-fix.bak` suffix pattern, sitting next to each source.
  - **Authoritative acceptance check:** each `.<source>.pre-write-permission-fix.bak` exists and matches source byte count.

## Phase 2 - Global Config Fix (primary)
- [x] 2.1 Add `"write": "allow"` to the `permission` block of `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
  - **Exact edit:** anchor on this 2-line literal in the file (one occurrence only):
    ```
        "read": "allow",
        "glob": "allow",
    ```
    Replace with:
    ```
        "read": "allow",
        "write": "allow",
        "glob": "allow",
    ```
    Use `[string]::Replace()` (literal, not regex). Placement puts `write` next to `read` and before `glob`, preserving the existing 2-space indentation and trailing comma.

- [x] 2.2 **Authoritative acceptance check** (must print `OK`):
  ```powershell
  $path = "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"
  $text = Get-Content -Raw -LiteralPath $path
  $permStart = $text.IndexOf('"permission"')
  $braceStart = $text.IndexOf('{', $permStart)
  $depth = 0; $permEnd = $permStart
  for ($i = $braceStart; $i -lt $text.Length; $i++) {
      if ($text[$i] -eq '{') { $depth++ }
      elseif ($text[$i] -eq '}') { $depth--; if ($depth -eq 0) { $permEnd = $i; break } }
  }
  $permBlock = $text.Substring($permStart, $permEnd - $permStart + 1)
  $null = $text | ConvertFrom-Json -AsHashtable   # JSONC parses (Retro/retro duplicate keys force -AsHashtable)
  $expected = '"write": "allow"'
  $regressions = @('"bash": "allow"','"read": "allow"','"task": "allow"') | Where-Object { -not $permBlock.Contains($_) }
  if ($regressions.Count -gt 0) { throw "permission regression: $($regressions -join ', ')" }
  if (-not $permBlock.Contains($expected)) { throw "write: allow not in permission block" }
  "OK"
  ```
  **Diagnostic checks:** `Select-String -SimpleMatch '"write": "allow"'` reports exactly 1 match in the file; the line index of `"write": "allow"` is between the line indices of `"read": "allow"` and `"glob": "allow"` (proves insertion order, not just presence).

## Phase 3 - Conductor Agent Hardening (defense in depth)
The 2-line anchor `permission:` + `  edit: allow` is unique in each non-validator agent file; for the two validators the anchor is `permission:` + `  edit: deny`. Place `write: allow` immediately under `permission:`, so the inserted lines read `  write: allow` then the original `  edit: ...` line. This is a literal `[string]::Replace()` edit; do NOT use regex `-replace` (it would eat the structural indentation).

- [x] 3.1 `C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-creator.md`: add `  write: allow` above `  edit: allow`. Anchor: the two lines `permission:` then `  edit: allow` (one match). KEEP all other frontmatter (bash allow, task deny, skill allow).
  - **Diagnostic check:** `Select-String -SimpleMatch 'permission:\n  edit: allow'` returns exactly 1 match before edit, 0 after.

- [x] 3.2 `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md`: add `  write: allow` above `  edit: allow`. KEEP bash destructive `ask` rules (`"rm *": ask`, `"git reset*": ask`, `"git clean*": ask`, `"del *": ask`).
  - **Diagnostic check:** all four destructive-ask literals still present (`Select-String -SimpleMatch` returns 1 each).

- [x] 3.3 `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md`: add `  write: allow` above `  edit: allow`. KEEP destructive-ask rules.

- [x] 3.4 `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md`: add `  write: allow` above `  edit: allow`. KEEP destructive-ask rules.

- [x] 3.5 `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md`: add `  write: allow` above `  edit: deny` (the `edit: deny` line MUST remain unchanged). Anchor: `permission:` then `  edit: deny`.

- [x] 3.6 `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`: add `  write: allow` above `  edit: allow`. KEEP the full `task:` block (it is the orchestrator's allow-list for subagent delegation; not touched).

- [x] 3.7 `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator-alt.md`: add `  write: allow` above `  edit: deny`. The alt validator emits a re-validation `validation-report-<ts>.md` (and possibly `validation-blockers-<ts>.md`), so it writes files - it MUST receive `write: allow`. KEEP `edit: deny`.

- [x] 3.8 `C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-reviewer.md`: add `  write: allow` above `  edit: allow`. The Stage 2 reviewer writes `review-report-<ts>.md` and `review-diff-summary-<ts>.md`.

- [x] 3.9 `C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-reviewer-alt.md`: add `  write: allow` above `  edit: allow`. Stage 3 re-reviewer writes a second `review-report-<ts>.md`.

- [x] 3.10 **Authoritative acceptance check** (loops over all nine agents; must print `ALL OK`):
  ```powershell
  $agents = @(
      @{ Path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-creator.md";         ExpectEdit = 'allow' },
      @{ Path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-reviewer.md";        ExpectEdit = 'allow' },
      @{ Path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-reviewer-alt.md";    ExpectEdit = 'allow' },
      @{ Path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md";        ExpectEdit = 'allow' },
      @{ Path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md"; ExpectEdit = 'allow' },
      @{ Path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md";   ExpectEdit = 'allow' },
      @{ Path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md";ExpectEdit = 'allow' },
      @{ Path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md";      ExpectEdit = 'deny'  },
      @{ Path = "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator-alt.md";   ExpectEdit = 'deny'  }
  )
  $bad = @()
  foreach ($a in $agents) {
      $text = Get-Content -Raw -LiteralPath $a.Path
      $lines = $text -split "`n"
      $dc = 0; $fm = ''
      foreach ($l in $lines) {
          if ($l -eq '---') { $dc++; if ($dc -eq 2) { break }; continue }
          if ($dc -eq 1) { $fm += $l + "`n" }
      }
      $writeOk = $fm.Contains('write: allow')
      $editOk  = if ($a.ExpectEdit -eq 'deny') { $fm.Contains('edit: deny') } else { $fm.Contains('edit: allow') }
      if (-not $writeOk -or -not $editOk) { $bad += "$(Split-Path $a.Path -Leaf): writeOk=$writeOk editOk=$editOk" }
  }
  if ($bad.Count -gt 0) { throw ($bad -join "`n") }
  "ALL OK"
  ```

## Phase 4 - Anomaly Logging Reference + Stage-Prompt Wiring
- [x] 4.1 Create `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\anomaly-logging.md` with the EXACT content below (verbatim - the executor must not paraphrase required section headings or required string literals because the acceptance check searches for those literals). Use the native `Write` tool with the content as the tool arg; if native tools are down, stage the body to a temp file then `Copy-Item` to the target path. Do not use a PowerShell here-string bundled into a single `-Command` blob (Windows Defender heuristic + quoting-fragility trap; see `references/artifact-output-format.md`).
  - **Required body** (the file MUST contain all of: the heading `## Anomaly Logging (Conductor Pipeline)`, the literal path `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl`, the literal `5000` (unhyphenated, not `5,000`), the literal `FIFO` used in the rotation rule, the closed taxonomy values `permission-prompt`, `tool-error`, `model-fallback`, `destructive-ask`, `deviation`, `retry`, `other`, the seven schema keys `ts`, `track`, `stage`, `subagent`, `type`, `severity`, `detail`, the closeout-summary line that says the validator filters by track id and writes `anomaly-summary-<date>.md`, and the platform-limitation note that permission events at the opencode platform layer are not always visible to the triggering subagent). Required markdown body (use verbatim):

    ```markdown
    # Anomaly Logging (Conductor Pipeline)

    ## Anomaly Logging (Conductor Pipeline)

    ## Purpose
    Capture operational anomalies (permission prompts, tool errors, model fallbacks, destructive-ask, deviations, retries, other) in a single append-only JSONL store so they are queryable per-run and as cross-track trend data.

    ## Log location
    - **Primary store:** `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` (append-only, one JSON object per line).
    - **Archived history:** `pipeline-anomalies.archive-<ts>.jsonl` (see Rotation).
    - **Per-track view:** `anomaly-summary-<date>.md` generated at validation closeout by filtering the JSONL for the current track id (see Per-track summary).

    ## Taxonomy
    Closed set of values for the `type` field:
    - `permission-prompt`
    - `tool-error`
    - `model-fallback`
    - `destructive-ask`
    - `deviation`
    - `retry`
    - `other`

    ## Severity
    - `info` - normal operational signal.
    - `warn` - noteworthy but not blocking.
    - `error` - failure that affected progress.

    ## JSONL schema
    Each line is a single JSON object with exactly these seven keys:
    - `ts` (string, ISO-8601 UTC, e.g. `2026-07-03T14:25:00Z`)
    - `track` (string, track id)
    - `stage` (string, e.g. `stage-1`, `stage-2`, `stage-4`, `orchestrator`)
    - `subagent` (string, e.g. `conductor-track-executor`)
    - `type` (string, one of the taxonomy values)
    - `severity` (string, `info` | `warn` | `error`)
    - `detail` (string, terse human-readable)

    Example (one line, no trailing comma, no comments):
    `{"ts":"2026-07-03T14:25:00Z","track":"20260703-write-permission-fix","stage":"stage-4","subagent":"conductor-track-executor","type":"tool-error","severity":"warn","detail":"bash returned exit 1"}`

    ## Rotation (FIFO archive, NOT truncate)
    - **Cap:** 5000 lines.
    - **Action when cap exceeded:** rename the current `pipeline-anomalies.jsonl` to `pipeline-anomalies.archive-<ts>.jsonl` (ts = the moment of rotation, `yyyyMMdd-HHmmss`) and start a new empty `pipeline-anomalies.jsonl`. The previous contents are PRESERVED in the archive, not deleted.
    - **Rationale:** at ~250 bytes/line, 5000 lines ~ 1.25 MB; archived history is retained for trend analysis. Truncation is forbidden - the log is append-only and historical.

    ## All-stages-append rule
    Every Conductor stage (Stage 1 plan-creator, Stage 2/3 reviewer, Stage 4 executor, Stage 5/6 validator, and the orchestrator) appends its observed anomalies to the global JSONL. Agents do not maintain per-track logs; the global store is the single source of truth.

    ## Per-track summary (closeout)
    At validation closeout, the validator filters the JSONL for the current track id and writes `anomaly-summary-<date>.md` into the track folder for human reading. This is the only summary view; the JSONL remains the source of truth.

    ## Platform limitation (honest scope note)
    A permission prompt at the opencode PLATFORM layer is not always visible to the triggering subagent (it surfaces to the user/main thread). The agent-emitted log captures everything agents CAN observe. Full automatic capture of every platform permission-event requires an opencode feature (permission-event hook / DCP plugin event) and is OUT OF SCOPE for the config-only fix in this track.
    ```

- [x] 4.2 `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`: add an "Anomaly logging" bullet to the Tool preflight section.
  - **Exact edit:** anchor on the literal line that begins `**Artifact output format** - write report/log/summary files with the native `Write` tool` (one occurrence in the file - confirm with `Select-String -SimpleMatch` first). Insert the following line immediately AFTER that line and BEFORE the next blank line:
    ```
    - **Anomaly logging** - if an anomaly is observed during this stage (permission prompt, tool error, model fallback, destructive-ask, deviation, retry, or other), append exactly one JSONL line to `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` using the seven-key schema documented in `references/anomaly-logging.md`. One append per anomaly; never modify or delete past lines; never truncate.
    ```

- [x] 4.3 `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`: add the same append instruction to EACH stage closeout (Stage 1, Stage 2/3, Stage 4, Stage 5/6).
  - **Exact edits:** for each of the four stage-prompt blocks, anchor on the closing context line of that block (e.g. for Stage 1 the line `Give a fully qualified path to the plan document.`; for Stage 2/3 the line `Give a fully qualified path to the plan document.`; for Stage 4 the line `fully qualified Windows paths to the log, updated plan.md, and other updated files.`; for Stage 5/6 the lines ending `one concise sentence`). Append the following sentence at the end of each stage's prompt block, as a new bullet or new sentence on a new line (preserve any trailing punctuation style of that block):
    ```
    - **Closeout append:** append a one-line JSONL anomaly record to `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` for any anomaly observed during this stage (use `type=other`, `severity=info` if no specific class applies); see `references/anomaly-logging.md`.
    ```

- [x] 4.4 `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`: add `anomaly-logging.md` to the "Related references" list.
  - **Exact edit:** anchor on the line that begins `PowerShell edit hazards, including parse-check limitations, content-anchored edits` (one occurrence). Insert a new sentence immediately after that line:
    `Anomaly logging taxonomy, JSONL schema, FIFO-archive rotation, all-stages-append rule, and closeout summary generation live in references/anomaly-logging.md.`

- [x] 4.5 **Authoritative acceptance check** (must print `OK`):
  ```powershell
  $aPath = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\anomaly-logging.md"
  $sPath = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md"
  $kPath = "C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md"
  $a = Get-Content -Raw -LiteralPath $aPath
  $s = Get-Content -Raw -LiteralPath $sPath
  $k = Get-Content -Raw -LiteralPath $kPath
  $requiredInA = @(
      'pipeline-anomalies.jsonl',
      'FIFO',
      '5000',
      'permission-prompt','tool-error','model-fallback','destructive-ask','deviation','retry','other',
      '"ts"','"track"','"stage"','"subagent"','"type"','"severity"','"detail"',
      'anomaly-summary-<date>.md',
      'PLATFORM layer'
  )
  $missingA = $requiredInA | Where-Object { -not $a.Contains($_) }
  if ($missingA.Count -gt 0) { throw "anomaly-logging.md missing: $($missingA -join ', ')" }
  if (-not $s.Contains('Anomaly logging')) { throw 'stage-prompts.md missing Anomaly logging bullet' }
  if (-not $k.Contains('anomaly-logging.md')) { throw 'SKILL.md missing anomaly-logging.md reference' }
  "OK"
  ```

## Phase 5 - Global Log Store Bootstrap
- [x] 5.1 Create the directory `C:\development\opencode\.conductor\logs\` (if it does not already exist).
  - **Authoritative acceptance check:** `Test-Path -LiteralPath "C:\development\opencode\.conductor\logs\" -PathType Container` returns `True`.

- [x] 5.2 Create empty `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` (zero-byte file is acceptable as the starting state).
  - **Authoritative acceptance check:** `Test-Path -LiteralPath "...\pipeline-anomalies.jsonl"` returns `True`; `(Get-Item "...\pipeline-anomalies.jsonl").Length -ge 0`.

- [x] 5.3 Create `C:\development\opencode\.conductor\logs\pipeline-anomalies.README.md` documenting the format (JSONL cannot hold inline comments so a sibling README is required). Body MUST contain all of: the literal path `pipeline-anomalies.jsonl`, the seven schema keys `ts` `track` `stage` `subagent` `type` `severity` `detail`, the closed taxonomy list (`permission-prompt`, `tool-error`, `model-fallback`, `destructive-ask`, `deviation`, `retry`, `other`), the literal `5000` (unhyphenated), the literal `FIFO` in the rotation context, and the explicit instruction `Do not modify or delete past lines.` (verbatim). Recommended template the executor may adapt (the executor may add prose, but MUST keep all literal strings in the bulleted list above):
  ```markdown
  # Pipeline Anomalies Log

  ## Purpose
  Append-only operational anomaly store for the Conductor pipeline. See `conductor-pipeline/references/anomaly-logging.md` for the full schema and rotation policy.

  ## File
  - Primary store: `pipeline-anomalies.jsonl` (one JSON object per line, UTF-8, no trailing comma, no comments).

  ## Schema (one line, seven keys)
  - `ts` (string, ISO-8601 UTC, e.g. `2026-07-03T14:25:00Z`)
  - `track` (string, track id)
  - `stage` (string, e.g. `stage-1`, `stage-2`, `stage-4`, `orchestrator`)
  - `subagent` (string, e.g. `conductor-track-executor`)
  - `type` (string, closed taxonomy)
  - `severity` (string, `info` | `warn` | `error`)
  - `detail` (string, terse)

  ## Taxonomy (closed)
  `permission-prompt` | `tool-error` | `model-fallback` | `destructive-ask` | `deviation` | `retry` | `other`

  ## Rotation
  - Cap: 5000 lines.
  - Action: rename `pipeline-anomalies.jsonl` to `pipeline-anomalies.archive-<ts>.jsonl` and start a new empty `pipeline-anomalies.jsonl`. The previous contents are PRESERVED (FIFO archive, not truncate).

  ## Rules
  - One JSON object per line. Do not modify or delete past lines.
  - Never insert comments. JSONL is line-oriented; use a sibling markdown file for prose.
  - Never use bare `ConvertFrom-Json` over the whole file - it parses only the FIRST line. Use a per-line parse loop.
  ```

- [x] 5.4 Append EXACTLY this one JSONL line to `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` as the live seed example (this very fix run, type `permission-prompt`, severity `info`). The line MUST be byte-exact:
  ```
  {"ts":"2026-07-03T00:00:00Z","track":"20260703-write-permission-fix","stage":"stage-1","subagent":"conductor-plan-creator","type":"permission-prompt","severity":"info","detail":"write tool was unlisted - fix in progress"}
  ```
  Use `Add-Content -LiteralPath` (or `Set-Content` followed by appending the seed to whatever was already there) with the literal line above. Do not add a trailing newline after the JSON if `Add-Content` already supplies one. Do not reformat the JSON.
  - **Diagnostic check:** line ends with `}` (not `},`); line does not contain a literal newline inside the JSON; the line is parseable by `ConvertFrom-Json` and has all seven required keys.

- [x] 5.5 **Authoritative acceptance check** (must print `OK`):
  ```powershell
  $path = "C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl"
  if (-not (Test-Path -LiteralPath $path)) { throw "jsonl missing" }
  $lines = Get-Content -LiteralPath $path | Where-Object { $_.Trim() -ne '' }
  if ($lines.Count -lt 1) { throw "jsonl has no non-empty lines" }
  $required = @('ts','track','stage','subagent','type','severity','detail')
  $ok = $false
  foreach ($ln in $lines) {
      try {
          $obj = $ln | ConvertFrom-Json
          $keys = $obj.PSObject.Properties.Name
          if (($required | Where-Object { $keys -notcontains $_ }).Count -eq 0) { $ok = $true; break }
      } catch { continue }
  }
  if (-not $ok) { throw "no jsonl line has all seven required keys" }
  "OK"
  ```

## Phase 6 - Permission-Baseline Codification
- [x] 6.1 Add a "Permission baseline for file-creating agents" section to `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md` (single, unambiguous target; do NOT also add it to AGENTS.md - the standards doc is the global authority). The new section MUST contain all of these literal strings in the same section: the words `Permission baseline` (as a section heading), `write: allow`, `edit: allow`, and a one-sentence rule that "agents that create files must grant both `write` and `edit` in the agent frontmatter AND the global `opencode.jsonc` permission block must also contain `write: allow`". Required body (use verbatim):
  ```markdown
  ## Permission baseline for file-creating agents

  The Conductor pipeline and any other agent that creates files follows a two-layer permission baseline:

  1. The global `opencode.jsonc` `permission` block MUST include `write: allow`. (Without it, every file-creating stage triggers an ASK prompt. `bash: allow` already grants equivalent file-write power, so this is friction removal, not a security boundary - the destructive-bash `ask` rules are the real guardrail.)
  2. Every agent frontmatter that creates files MUST include `write: allow` AND `edit: allow` in its `permission:` block (validators may keep `edit: deny` if they only need to create new files but never modify existing ones).

  Concretely: agents that create files must grant both `write` and `edit` in the agent frontmatter. Verify the global `opencode.jsonc` `permission` block also contains `write: allow`. Do not grant `write` in an agent frontmatter without confirming the global block already has it; do not omit `write` from an agent that creates files.
  ```

- [x] 6.2 Cross-link the retro doc. Anchor on a unique line in the standards doc (e.g. the `**Authority:**` line, or the line `Update this document when:`). Insert a new bullet item that mentions `conductor-pipeline-write-permission-retro-2026-07-02.md` and a one-line summary "establishes the permission-baseline rule". Recommended insertion: under `## When to Update This Standard`, add `- 2026-07-03: Permission baseline for file-creating agents added (see retro conductor-pipeline-write-permission-retro-2026-07-02.md).`
  - **Diagnostic check:** `Select-String -SimpleMatch 'conductor-pipeline-write-permission-retro-2026-07-02.md'` returns exactly 1 match in the standards doc.

- [x] 6.3 **Authoritative acceptance check** (must print `OK`):
  ```powershell
  $path = "C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md"
  $text = Get-Content -Raw -LiteralPath $path
  $required = @('Permission baseline', 'write: allow', 'edit: allow', 'conductor-pipeline-write-permission-retro-2026-07-02.md')
  $missing = $required | Where-Object { -not $text.Contains($_) }
  if ($missing.Count -gt 0) { throw "standards doc missing: $($missing -join ', ')" }
  "OK"
  ```

## Phase 7 - Validation (the Stage 5/6 validator runs these)
- [x] 7.1 Run the Phase 2.2 authoritative check verbatim. Must print `OK`.
- [x] 7.2 Run the Phase 3.10 authoritative check verbatim. Must print `ALL OK`.
- [x] 7.3 Confirm destructive-bash `ask` rules unchanged in the three executor agent files:
  ```powershell
  $executorFiles = @(
      "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor.md",
      "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md",
      "C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md"
  )
  $bad = @()
  foreach ($f in $executorFiles) {
      $t = Get-Content -Raw -LiteralPath $f
      foreach ($pat in @('"rm *": ask','"git reset*": ask','"git clean*": ask','"del *": ask')) {
          $hits = Select-String -InputObject $t -SimpleMatch $pat
          if ($hits.Count -ne 1) { $bad += "$(Split-Path $f -Leaf): '$pat' matches = $($hits.Count)" }
      }
  }
  if ($bad.Count -gt 0) { throw ($bad -join "`n") }
  "OK"
  ```
- [x] 7.4 Run the Phase 4.5 authoritative check verbatim. Must print `OK`.
- [x] 7.5 Run the Phase 5.5 authoritative check verbatim. Must print `OK`.
- [x] 7.6 Run the Phase 6.3 authoritative check verbatim. Must print `OK`.
- [x] 7.7 Confirm no production/application code was touched. `git status` (run in `C:\development\opencode`) shows no modified/added/deleted files under non-`.conductor` paths EXCEPT for the expected changes in `C:\Users\DaveWitkin\.config\opencode\` (the global config), `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\` (skill docs), `C:\Users\DaveWitkin\.config\opencode\agent-development-standards.md` (standards doc), and the new `C:\development\opencode\.conductor\logs\` directory. Any other change is a regression.
- [x] 7.8 Generate the per-track anomaly summary at closeout. Use the following PowerShell (the validator must actually run it and the resulting file must exist with the required sections):
  ```powershell
  $trackId = "20260703-write-permission-fix"
  $date = (Get-Date).ToString('yyyy-MM-dd')
  $src = "C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl"
  $dst = "C:\development\opencode\.conductor\tracks\$trackId\anomaly-summary-$date.md"
  $lines = Get-Content -LiteralPath $src | Where-Object { $_.Trim() -ne ' -and $_.Contains($trackId) }
  $body = @()
  $body += "# Anomaly Summary - $trackId - $date"
  $body += ""
  $body += ("Total anomalies for this track: {0}" -f $lines.Count)
  $body += ""
  $body += "## Entries"
  $body += ""
  if ($lines.Count -eq 0) {
      $body += "_No anomalies recorded for this track._"
  } else {
      $body += "| ts | stage | subagent | type | severity | detail |"
      $body += "|---|---|---|---|---|---|"
      foreach ($ln in $lines) {
          try {
              $o = $ln | ConvertFrom-Json
              $body += "| $($o.ts) | $($o.stage) | $($o.subagent) | $($o.type) | $($o.severity) | $($o.detail) |"
          } catch { $body += "| (unparseable) | | | | | |" }
      }
  }
  $body += ""
  $body += "## Source"
  $body += ('`{0}` (FIFO archive cap 5000)' -f $src)
  Set-Content -Encoding utf8 -LiteralPath $dst -Value ($body -join "`n")
  ```
  **Authoritative acceptance check:** `Test-Path -LiteralPath $dst` returns `True`; the file contains the literal `Total anomalies for this track:`; the file contains the literal `pipeline-anomalies.jsonl`.
- [x] 7.9 Write `validation-report-<ts>.md` and update `metadata.json` (`status` -> `validated`, `progress_phase` -> `validated`, `executed_at` -> the captured `$ts` from session start, `completed_tasks` -> match the actual checked-off count). Standard closeout.

## Notes
- If file tools (Bun) are down, use PowerShell-first via `bash`: `Get-Content -Raw` to read, literal `[string]::Replace()` to edit (NOT regex `-replace`), `Set-Content -Encoding utf8` to write. For large artifacts (the new reference doc, the validation report), stage the body in a temp file then `Copy-Item` into the target path; do not bundle a here-string + `Set-Content` into one inline `-Command` blob (Defender heuristic + quoting fragility; see `references/artifact-output-format.md`).
- This is config/documentation-only work; executor model `zai-coding-plan/glm-5.2`.
- Per anomaly-logging.md (created in Phase 4), this executor appends any anomaly it encounters to `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl`.
- Backup file extension for agents: `.<source-name>.pre-write-permission-fix.bak` (sits next to each source). For the global opencode.jsonc: `opencode.jsonc.pre-write-permission-fix-<ts>` (in the same directory as the source).
- Total task count (Phase 1-6 executable, Phase 7 validation): 28 executable checkboxes (3+2+10+5+5+3) + 9 validation checkboxes = 37. Update metadata.json 	ask_count to 28.



