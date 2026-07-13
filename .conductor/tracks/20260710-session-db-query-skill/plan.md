# Plan

Track ID: `20260710-session-db-query-skill`
Track directory: `C:\development\opencode\.conductor\tracks\20260710-session-db-query-skill\`
Recommended pipeline mode: `bookkeeping`
Recommended pipeline path: `1 -> 5 -> 7 -> 9`

## Phase 0 Setup & Preconditions
Objective: Confirm source material and target directories without creating deliverables prematurely.

- [x] 0.1 Verify authoritative source command exists and is readable.
  - Action: Read `C:\Users\DaveWitkin\.config\opencode\commands\session-history.md` using PowerShell and confirm it contains the required database facts before writing the skill.
  - Command:
    ```powershell
    $source = "C:\Users\DaveWitkin\.config\opencode\commands\session-history.md"
    $text = Get-Content -Raw -LiteralPath $source
    [pscustomobject]@{
      Exists = Test-Path -LiteralPath $source
      HasDbPath = $text.Contains("C:\Users\DaveWitkin\.local\share\opencode\opencode.db")
      HasMillisGotcha = $text.Contains("time_created / 1000") -or $text.Contains("milliseconds")
      HasPythonSqlite = $text.Contains("import sqlite3")
    } | ConvertTo-Json -Compress
    ```
  - Authoritative acceptance check: The command prints JSON with `"Exists":true`, `"HasDbPath":true`, `"HasMillisGotcha":true`, and `"HasPythonSqlite":true`.
  - Diagnostic checks: If any value is false, inspect the nearby source text with `Select-String -LiteralPath $source -SimpleMatch "opencode.db", "time_created", "sqlite3"`.
  - Error recovery: If the source file is missing or does not contain required facts, stop and ask the user for the updated authoritative source; do not invent schema details.

- [x] 0.2 Create the lazy-vault skill directory tree.
  - Action: Create `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\` and `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\scripts\` if absent.
  - Command:
    ```powershell
    $root = "C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query"
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    New-Item -ItemType Directory -Force -Path "$root\scripts" | Out-Null
    [pscustomobject]@{
      RootExists = Test-Path -LiteralPath $root
      ScriptsExists = Test-Path -LiteralPath "$root\scripts"
    } | ConvertTo-Json -Compress
    ```
  - Authoritative acceptance check: The command prints JSON with `"RootExists":true` and `"ScriptsExists":true`.
  - Diagnostic checks: Run `Get-ChildItem -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query" -Force` to inspect accidental pre-existing files.
  - Error recovery: If existing files are present, back them up to `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query.backup-YYYYMMDD-HHMMSS\` before overwriting unless the existing files are clearly an incomplete prior attempt for this same track.

Exit criteria: Source material is confirmed and the target lazy-vault directory tree exists.

## Phase 1 Implementation
Objective: Write the three skill deliverables with progressive disclosure and no private data leakage.

- [x] 1.1 Write `SKILL.md` with valid frontmatter and concise trigger-oriented guidance.
  - Action: Create `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\SKILL.md` with YAML frontmatter and a short workflow. Include these exact body concepts: use Python `sqlite3`, do not use the `sqlite3` CLI, write temp scripts instead of complex `python -c`, divide `time_created` by 1000, and do not filter out archived sessions.
  - Required content template:
    ```markdown
    ---
    name: session-db-query
    description: Query the OpenCode session database (opencode.db SQLite) for session history, session lookup, token usage, cost analysis, activity tracking, model usage, project/date filtering, and archived/live session investigation.
    ---

    # Session DB Query

    Use this skill when you need to inspect OpenCode session history or answer questions from `opencode.db`.

    ## Quick Rules
    - DB path: `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`.
    - Use Python `sqlite3`; the `sqlite3` CLI is not installed here.
    - Write reusable Python scripts to temp files; avoid complex `python -c` on Windows.
    - `time_created` is Unix milliseconds; divide by 1000 in SQLite date functions.
    - Do not filter on `time_archived IS NULL`; archived sessions are completed work.

    ## Workflow
    1. Read `reference.md` for schema gotchas and query patterns.
    2. Copy or adapt `scripts/query_sessions.py` for the specific question.
    3. Keep outputs scoped, redacted, and free of private raw message content unless the user explicitly asks.
    ```
  - Authoritative acceptance check: Run `$p="C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\SKILL.md"; $t=Get-Content -Raw -LiteralPath $p; ($t.Contains("name: session-db-query") -and $t.Contains("opencode.db SQLite") -and $t.Contains("Use Python `sqlite3`") -and $t.Contains("time_created` is Unix milliseconds") -and $t.Contains("Do not filter on `time_archived IS NULL`"))` and expect `True`.
  - Diagnostic checks: Run `Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\SKILL.md"` for manual review.
  - Error recovery: If YAML parsing later fails, keep the frontmatter to simple scalar strings and avoid colons in unquoted frontmatter values.

- [x] 1.2 Write `reference.md` with detailed generalized query knowledge.
  - Action: Create `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\reference.md` documenting database path, safe access, timestamp conversion, archived-session semantics, Windows execution pattern, schema/column interpretation, title/agent/status conventions, provider billing classification, and reusable query recipes.
  - Required body sections and literals:
    - `## Database Location and Access`
    - `DATE(time_created / 1000, 'unixepoch', 'localtime')`
    - `Do not filter on time_archived IS NULL`
    - `## Column Interpretation Guide`
    - `agent` examples including `build` and `01-Planner`
    - `status` examples including `arch` and `live`
    - `summary_additions`, `summary_deletions`, and `summary_files` may be `0`
    - `## Provider Billing Classification`
    - `PROVIDER_BILLING` dictionary pattern
    - `## Query Patterns`
  - Authoritative acceptance check: Run `$p="C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\reference.md"; $t=Get-Content -Raw -LiteralPath $p; ($t.Contains("## Database Location and Access") -and $t.Contains("DATE(time_created / 1000, 'unixepoch', 'localtime')") -and $t.Contains("Do not filter on time_archived IS NULL") -and $t.Contains("## Column Interpretation Guide") -and $t.Contains("build") -and $t.Contains("01-Planner") -and $t.Contains("summary_additions") -and $t.Contains("## Provider Billing Classification") -and $t.Contains("PROVIDER_BILLING") -and $t.Contains("## Query Patterns"))` and expect `True`.
  - Diagnostic checks: Run `Select-String -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\reference.md" -SimpleMatch "time_archived", "PROVIDER_BILLING", "Query Patterns"`.
  - Error recovery: If source schema names differ while reading the command, document the confirmed names from the source and add a warning section instead of guessing.

- [x] 1.3 Write `scripts\query_sessions.py` as an adaptable Python query template.
  - Action: Create `C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\scripts\query_sessions.py` using only Python stdlib. It must accept `--db`, `--project-path`, `--start-date`, `--end-date`, `--limit`, and `--format` (`table` or `json`), use parameterized SQL, divide `time_created` by 1000 for local dates, avoid `time_archived IS NULL`, classify provider billing with a `PROVIDER_BILLING` dict, and print structured rows without raw message content.
  - Required implementation notes:
    ```python
    DEFAULT_DB = r"C:\Users\DaveWitkin\.local\share\opencode\opencode.db"
    PROVIDER_BILLING = {
        "openai": "direct_or_subscription",
        "opencode-go": "opencode_go",
        "zai-coding-plan": "zai_coding_plan",
    }
    ```
  - Authoritative acceptance check: Run `python -m py_compile "C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\scripts\query_sessions.py"; if ($LASTEXITCODE -eq 0) { "PY_COMPILE_OK" } else { "PY_COMPILE_FAIL" }` and expect `PY_COMPILE_OK`.
  - Diagnostic checks: Run `python "C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query\scripts\query_sessions.py" --help` and confirm the optional arguments appear.
  - Error recovery: If Python is unavailable on PATH, retry with `py -3 -m py_compile ...`; if schema names differ, keep the script as a template and update SQL comments to tell agents how to inspect `PRAGMA table_info(session)`.

Exit criteria: All three skill files are written and compile/contain required body content.

## Phase 2 Structural Validation & Registration
Objective: Validate skill hygiene and register the track without duplicate ledger entries.

- [x] 2.1 Validate skill structure and frontmatter.
  - Action: Run a deterministic PowerShell/Python validation that checks uppercase filename, directory/frontmatter name match, required files, YAML-like frontmatter delimiters, and required args in the script.
  - Command:
    ```powershell
    $root = "C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query"
    $skill = Get-Content -Raw -LiteralPath "$root\SKILL.md"
    $script = Get-Content -Raw -LiteralPath "$root\scripts\query_sessions.py"
    [pscustomobject]@{
      SkillExists = Test-Path -LiteralPath "$root\SKILL.md"
      ReferenceExists = Test-Path -LiteralPath "$root\reference.md"
      ScriptExists = Test-Path -LiteralPath "$root\scripts\query_sessions.py"
      UppercaseSkillFile = Test-Path -LiteralPath "$root\SKILL.md"
      FrontmatterDelimited = $skill.StartsWith("---") -and $skill.Contains("`n---")
      NameMatchesDirectory = $skill.Contains("name: session-db-query")
      HasRequiredArgs = @("--project-path","--start-date","--end-date","--limit","--format") | ForEach-Object { $script.Contains($_) }
    } | ConvertTo-Json -Compress
    ```
  - Authoritative acceptance check: The command prints JSON with all Boolean fields set to `true` and `HasRequiredArgs` as `[true,true,true,true,true]`.
  - Diagnostic checks: If the lazy-vault has a validator script available, run the skill-creator `quick_validate.py` against the skill folder as an additional check.
  - Error recovery: If frontmatter parsing fails, reduce frontmatter to exactly two fields (`name`, `description`) and move all complex text into the Markdown body.

- [x] 2.2 Upsert row in `.conductor\tracks.md`.
  - Action: Update `C:\development\opencode\.conductor\tracks.md` so there is exactly one table row for `20260710-session-db-query-skill` with status `planned`, blank completed date, and path `C:\development\opencode\.conductor\tracks\20260710-session-db-query-skill`.
  - Command:
    ```powershell
    $p = "C:\development\opencode\.conductor\tracks.md"
    $id = "20260710-session-db-query-skill"
    $row = "| 20260710-session-db-query-skill | Session DB Query Skill | planned |  | C:\development\opencode\.conductor\tracks\20260710-session-db-query-skill |"
    $lines = Get-Content -LiteralPath $p
    $filtered = $lines | Where-Object { $_ -notmatch "^\|\s*20260710-session-db-query-skill\s*\|" }
    Set-Content -Encoding utf8 -LiteralPath $p -Value ($filtered + $row)
    ((Get-Content -LiteralPath $p) | Where-Object { $_ -match "^\|\s*20260710-session-db-query-skill\s*\|" }).Count
    ```
  - Authoritative acceptance check: The command prints `1`.
  - Diagnostic checks: Run `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks.md" -Pattern "^\|\s*20260710-session-db-query-skill\s*\|"`.
  - Error recovery: If table formatting differs, still enforce exactly one line containing the track ID and full track path; do not create duplicates.

- [x] 2.3 Upsert entry in `.conductor\tracks-ledger.md` if it exists.
  - Action: Update `C:\development\opencode\.conductor\tracks-ledger.md` with exactly one active-track bullet for `20260710-session-db-query-skill`.
  - Command:
    ```powershell
    $p = "C:\development\opencode\.conductor\tracks-ledger.md"
    $entry = "- [20260710-session-db-query-skill](./tracks/20260710-session-db-query-skill/spec.md): Create a lazy-vault session-db-query skill that generalizes OpenCode session SQLite database lookup, timestamp, archive, schema, cost, and token query knowledge from the existing /session-history command. (Phase: planned 2026-07-10)"
    if (Test-Path -LiteralPath $p) {
      $lines = Get-Content -LiteralPath $p
      $filtered = $lines | Where-Object { $_ -notmatch "20260710-session-db-query-skill" }
      $activeIndex = [Array]::IndexOf($filtered, "## Active Tracks")
      if ($activeIndex -ge 0) {
        $before = $filtered[0..$activeIndex]
        $after = $filtered[($activeIndex + 1)..($filtered.Count - 1)]
        Set-Content -Encoding utf8 -LiteralPath $p -Value ($before + $entry + $after)
      } else {
        Set-Content -Encoding utf8 -LiteralPath $p -Value ($filtered + $entry)
      }
      ((Get-Content -LiteralPath $p) | Where-Object { $_ -match "20260710-session-db-query-skill" }).Count
    } else { "LEDGER_MISSING" }
    ```
  - Authoritative acceptance check: The command prints `1` when `tracks-ledger.md` exists, or `LEDGER_MISSING` if the repo does not maintain one.
  - Diagnostic checks: Run `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks-ledger.md" -SimpleMatch "20260710-session-db-query-skill"` when the ledger exists.
  - Error recovery: If the Active Tracks heading is missing, append a single bullet at the end and record the formatting deviation in the execution log.

Exit criteria: Skill structure checks pass and Conductor index files contain exactly one registration for the track.

## Final Phase Validation & Handover
Objective: Prove the deliverables satisfy the definition of done and leave auditable handoff artifacts.

- [x] F.1 Run final no-private-data and content validation.
  - Action: Validate required content while checking the skill artifacts do not contain obvious private/token strings or copied full session rows.
  - Command:
    ```powershell
    $root = "C:\Users\DaveWitkin\.opencode-lazy-vault\session-db-query"
    $all = (Get-Content -Raw -LiteralPath "$root\SKILL.md") + "`n" + (Get-Content -Raw -LiteralPath "$root\reference.md") + "`n" + (Get-Content -Raw -LiteralPath "$root\scripts\query_sessions.py")
    [pscustomobject]@{
      HasDbPath = $all.Contains("C:\Users\DaveWitkin\.local\share\opencode\opencode.db")
      HasMillisRule = $all.Contains("time_created / 1000")
      HasArchiveWarning = $all.Contains("time_archived IS NULL")
      HasProviderBilling = $all.Contains("PROVIDER_BILLING")
      NoObviousTokens = -not ($all -match "(?i)(sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,}|refresh_token|access_token)")
    } | ConvertTo-Json -Compress
    ```
  - Authoritative acceptance check: The command prints JSON with all Boolean fields set to `true`.
  - Diagnostic checks: Run `Select-String -LiteralPath "$root\*.md", "$root\scripts\query_sessions.py" -Pattern "(?i)token|secret|session_message"` to manually inspect any matches.
  - Error recovery: If a secret-like string appears, remove it immediately, re-run validation, and log the anomaly without printing the secret value.

- [x] F.2 Create execution log and synchronize metadata after implementation.
  - Action: After execution, write `C:\development\opencode\.conductor\tracks\20260710-session-db-query-skill\execution-log-2026-07-10.md` summarizing files changed, validation commands, skipped stages, deviations, and handoff notes; update `metadata.json` status/progress to match actual completion.
  - Command:
    ```powershell
    $log = "C:\development\opencode\.conductor\tracks\20260710-session-db-query-skill\execution-log-2026-07-10.md"
    Test-Path -LiteralPath $log
    ```
  - Authoritative acceptance check: The command prints `True` after the execution log is created.
  - Diagnostic checks: Confirm the log includes `Validation commands` and `Skipped stages` using `Select-String -LiteralPath $log -SimpleMatch "Validation commands", "Skipped stages"`.
  - Error recovery: If execution completed but the log is missing, create the log from shell history and mark any uncertainty explicitly rather than backfilling unsupported claims.

- [x] F.3 Final Conductor closeout verification. **(Completed by Stage 7 validator + Phase B terminal closeout confirmation; track closed.)**
  - Action: Verify all non-deferred plan tasks are `[x]`, metadata matches the executed path, ledgers are synchronized, and Stage 9 documentation/waiver evidence exists.
  - Command:
    ```powershell
    $track = "C:\development\opencode\.conductor\tracks\20260710-session-db-query-skill"
    $plan = Get-Content -Raw -LiteralPath "$track\plan.md"
    $meta = Get-Content -Raw -LiteralPath "$track\metadata.json" | ConvertFrom-Json
    [pscustomobject]@{
      NoPendingTasks = -not ($plan -match "- \[ \]")
      MetadataMode = $meta.pipeline_mode
      MetadataPath = $meta.pipeline_path
      TracksRowCount = ((Get-Content -LiteralPath "C:\development\opencode\.conductor\tracks.md") | Where-Object { $_ -match "^\|\s*20260710-session-db-query-skill\s*\|" }).Count
      LedgerEntryCount = if (Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks-ledger.md") { ((Get-Content -LiteralPath "C:\development\opencode\.conductor\tracks-ledger.md") | Where-Object { $_ -match "20260710-session-db-query-skill" }).Count } else { 0 }
    } | ConvertTo-Json -Compress
    ```
  - Authoritative acceptance check: The command prints JSON with `"NoPendingTasks":true`, `"MetadataMode":"bookkeeping"`, `"MetadataPath":"1 -> 5 -> 7 -> 9"`, `"TracksRowCount":1`, and `"LedgerEntryCount":1` when the ledger exists.
  - Diagnostic checks: Run `Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260710-session-db-query-skill\metadata.json" | ConvertFrom-Json | ConvertTo-Json -Depth 8`.
  - Error recovery: If pending tasks remain, do not mark the track complete; either finish the task, mark it deferred with rationale, or stop and report blockers.

Exit criteria: All validation checks pass, Conductor bookkeeping is synchronized, and the track is ready for Stage 5 execution under the bookkeeping pipeline.

## Execution-Readiness Checklist
- [x] Target skill location is explicit and outside the always-loaded skill directory.
- [x] Source command path is explicit and authoritative.
- [x] Every task has exactly one `Authoritative acceptance check:` line.
- [x] Verification checks inspect body content, not only headings.
- [x] Commands are PowerShell-compatible and use `-LiteralPath` for Windows paths.
- [x] Common failures have recovery instructions.
- [x] Pipeline metadata recommends `bookkeeping` because this is skill/documentation/process-only work.

## Top 3 Risks and Mitigations
1. Risk: Copying private session data or too much of the existing command. Mitigation: Use only generalized schema/query guidance and validate with a no-secret/no-token scan.
2. Risk: Timestamp queries silently return wrong dates. Mitigation: Require the exact `/ 1000` date-expression literal in docs and script.
3. Risk: Skill is not discoverable due to invalid frontmatter or directory mismatch. Mitigation: Validate `name: session-db-query`, uppercase `SKILL.md`, and required files before closeout.

## First Task to Execute
Start with Phase 0 task 0.1: verify `C:\Users\DaveWitkin\.config\opencode\commands\session-history.md` exists and contains the required database facts.


