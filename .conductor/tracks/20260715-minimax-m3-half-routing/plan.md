# Implementation Plan: MiniMax M3 Half-Usage Agent Routing

## Restatement before tasks

- **Goal/outcome:** determine OpenCode's real model-routing capability, then reduce explicit MiniMax M3 usage approximately in half with ChatGPT 5.6 Tera Medium while preserving auditable pipeline diversity.
- **Constraints/non-goals:** do not invent schema, alter history, overwrite existing changes, require GLM-5.2, or execute unrelated configuration work. Work from backups and retain GLM-5.1 -> Qwen as the current Stage 5 operational fallback.
- **Definition of done:** complete active/historical inventory, evidence-backed routing decision, approved edits, rollback, deterministic validation, restart-aware live testing, and synchronized handoff artifacts.

> Executor preflight: native file tools are known to fail with `Bun is not defined`; use PowerShell 7 through the `bash` tool for the entire run. Every shell call must set an explicit tool timeout. Use `-LiteralPath` and quoted Windows paths. Do not use `Read-Host`, `Wait-Process`, `Start-Process -Wait`, watch/server commands, or uncapped network calls. Append one seven-key JSONL record per observed anomaly; never truncate `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl`.

## Phase 0 Setup & Preconditions

**Objective:** freeze scope, protect existing work, and establish reproducible discovery inputs.

- [x] **0.1 Capture repository and runtime preflight.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/preflight.json` containing UTC timestamp, `opencode --version`, PowerShell version, workspace `git status --porcelain=v1`, and the recursively discovered Git roots under `C:\development` (a directory is a Git root when `git -C <directory> rev-parse --show-toplevel` returns that same canonical path). Use bounded commands: `opencode --version`; `git status --porcelain=v1`; and `Get-ChildItem -LiteralPath "C:\development" -Directory -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName '.git') }`. De-duplicate canonical roots and include `C:\development\opencode`.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$p='C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\preflight.json'; $j=Get-Content -Raw -LiteralPath $p | ConvertFrom-Json; [bool]($j.utc_timestamp -and $j.opencode_version -and $j.powershell_version -and $null -ne $j.workspace_git_status -and @($j.git_roots).Count -gt 0 -and @($j.git_roots).Contains('C:\development\opencode'))"` must print `True`.
  - **Diagnostic checks:** `Get-Content -Raw -LiteralPath "C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\preflight.json"`.
  - **Error recovery:** if recursive discovery hits access errors, record each inaccessible directory in `preflight.json`; do not silently omit it or elevate.

- [x] **0.2 Create immutable target-state and backup manifests.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/baseline-manifest.json` with the pre-existing workspace status and SHA-256 records for every later-approved target; create timestamped sibling backups named `<file>.bak-<yyyyMMdd-HHmmss>` immediately before editing and record target, backup, pre-hash, git root, and tracked/untracked state. The manifest body must include `"bulk_restore_forbidden": true` and `"preserve_preexisting_changes": true`.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\baseline-manifest.json' | ConvertFrom-Json; [bool]($j.bulk_restore_forbidden -eq $true -and $j.preserve_preexisting_changes -eq $true -and $null -ne $j.preexisting_git_status -and $null -ne $j.targets)"` must print `True`.
  - **Diagnostic checks:** compare `git status --porcelain=v1` with the status captured by Task 0.1.
  - **Error recovery:** if any target cannot be read, hashed, or backed up, stop before editing that target and log a `tool-error` anomaly.

**Exit criteria:** preflight captures all Git roots, current runtime version, and existing changes; backup policy is explicit.

## Phase 1 Capability Determination

**Objective:** prove whether native weighted routing exists before selecting a mechanism.

- [x] **1.1 Produce the evidence-backed native-routing decision.** Inspect bounded local evidence first: `opencode --version`, `opencode run --help`, `opencode agent --help` (record a nonzero exit if subcommand absent), active config schemas/source references discoverable under the installed OpenCode package, and official OpenCode docs fetched with `Invoke-WebRequest -TimeoutSec 20 -MaximumRedirection 5` only if local evidence is insufficient. Create `.conductor/tracks/20260715-minimax-m3-half-routing/routing-decision.md` with exact sections `Installed version`, `Evidence inspected`, `Native 50/50 finding`, `Invocation-level enforceability`, `Selected mechanism`, and `Diversity consequences`. A native finding requires a documented exact field/CLI option and a parseable minimal dry-run; otherwise write `Native 50/50 finding: Unsupported by verified evidence` and select fixed pins plus paired agents/deterministic persisted selection.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$s=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\routing-decision.md'; [bool]($s.Contains('## Installed version') -and $s.Contains('## Evidence inspected') -and $s.Contains('## Native 50/50 finding') -and $s.Contains('## Invocation-level enforceability') -and $s.Contains('## Selected mechanism') -and $s.Contains('## Diversity consequences') -and ($s.Contains('Unsupported by verified evidence') -or $s.Contains('Supported by verified evidence')) -and $s.Contains('openai/gpt-5.6'))"` must print `True`.
  - **Diagnostic checks:** preserve command outputs in `.conductor/tracks/20260715-minimax-m3-half-routing/evidence/`; treat network failure as non-authoritative.
  - **Error recovery:** if the schema/source cannot be located, classify native weighting as unverified/unsupported and use fixed pins; never guess a property name.

**Exit criteria:** the routing mechanism is selected from verified capabilities, with invocation-level limits and diversity effects explicit.

## Phase 2 Complete M3 Inventory and Approved Mapping

**Objective:** enumerate every explicit active M3 selection and separate it from historical evidence.

- [x] **2.1 Generate the exhaustive M3 inventory.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/m3-inventory.json` by scanning both `C:\Users\DaveWitkin\.config\opencode\agent` and `...\agents` when present, plus active configuration/agent paths in every Git root from Task 0.1. Search case-insensitively for `minimax`, `m3`, and exact discovered model IDs; exclude `.git` from traversal but record hits in `.bak*`, archives, logs, handoffs, sessions, and `.conductor` as `historical`, not active. Every record must have `path`, `repository`, `classification`, `agent`, `model`, and `reason`; include `scanned_roots`, `missing_roots`, and `unreadable_paths` arrays.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\m3-inventory.json' | ConvertFrom-Json; $required=@('path','repository','classification','agent','model','reason'); $valid=@($j.records | Where-Object { $o=$_; @($required | Where-Object { -not ($o.PSObject.Properties.Name -contains $_) }).Count -eq 0 -and @('active','historical').Contains($o.classification) }).Count; [bool](@($j.scanned_roots).Contains('C:\Users\DaveWitkin\.config\opencode\agent') -and $valid -eq @($j.records).Count -and $null -ne $j.missing_roots -and $null -ne $j.unreadable_paths)"` must print `True`.
  - **Diagnostic checks:** emit `.conductor/tracks/20260715-minimax-m3-half-routing/m3-scan-raw.txt` with path, line number, and matched line for reconciliation.
  - **Error recovery:** any unreadable active root makes inventory incomplete; stop routing edits and report the root rather than treating zero hits as success.

- [x] **2.2 Define the approved routing map and diversity matrix.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/approved-routing-map.json` from active inventory records. Each record must include `path`, `agent`, `old_model`, `new_model`, `new_variant`, `selection_bucket`, `invocation_rule`, `role_family`, and `diversity_counterpart`. Use the exact Tera model ID and Medium variant verified in Task 1.1. Assign the nearest possible half to Tera, targeting 40%-60%; pipeline pairings must not put creator/reviewer or executor/validator in the same model family. Include `approval_required: true`, `approval_status: pending`, and a plain-language summary for user approval before Task 3.1.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\approved-routing-map.json' | ConvertFrom-Json; $n=@($j.assignments).Count; $t=@($j.assignments | Where-Object selection_bucket -eq 'tera-medium').Count; $ratio=if($n){$t/$n}else{0}; [bool]($j.approval_required -eq $true -and $j.approval_status -eq 'pending' -and $n -gt 0 -and (($ratio -ge .4 -and $ratio -le .6) -or $j.indivisible_count_exception) -and @($j.assignments | Where-Object { -not $_.invocation_rule -or -not $_.diversity_counterpart }).Count -eq 0)"` must print `True`.
  - **Diagnostic checks:** print assignments with `ConvertTo-Json -Depth 8`; manually inspect role pairs before requesting approval.
  - **Error recovery:** if the exact Tera model/Medium variant is unavailable, stop and request a target-model decision; do not silently substitute SOL, generic GPT, or another thinking level.

**Exit criteria:** all active M3 pins are accounted for, the proposed split is measurable, and user approval is a hard gate.

## Phase 3 Implementation

**Objective:** apply only the approved, backed-up routing changes.

- [x] **3.1 Record approval and finalize the change set.** After explicit user approval, update only `.conductor/tracks/20260715-minimax-m3-half-routing/approved-routing-map.json` to `"approval_status": "approved"`, add `approved_at` and `approved_summary`, and freeze a SHA-256 `map_hash`. Do not edit runtime files in this task.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\approved-routing-map.json' | ConvertFrom-Json; [bool]($j.approval_status -eq 'approved' -and $j.approved_at -and $j.approved_summary -and $j.map_hash)"` must print `True`.
  - **Diagnostic checks:** compare the approved assignment count to active records in `m3-inventory.json`.
  - **Error recovery:** if approval differs from the proposal, revise the map, recalculate ratio/diversity, and obtain approval again.

- [x] **3.2 Apply approved agent routing edits.** For each approved assignment, create and hash its timestamped backup, then edit only the explicit model/variant frontmatter or create only the approved paired-agent file. Use fixed `model:` and `variant:` values unless Task 1.1 proved a native weighted field. If paired agents are used, preserve body/permissions byte-for-byte except identity, model, variant, and the documented deterministic invocation rule. Do not modify historical files.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$map=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\approved-routing-map.json' | ConvertFrom-Json; $ok=$true; foreach($a in $map.assignments){$s=Get-Content -Raw -LiteralPath $a.path; if(-not $s.Contains(('model: '+$a.new_model)) -or ($a.new_variant -and -not $s.Contains(('variant: '+$a.new_variant)))){$ok=$false}}; $ok"` must print `True`.
  - **Diagnostic checks:** for tracked files use `git diff -- <path>`; for untracked/global files use `git diff --no-index <backup> <target>` and accept exit code 1 as “differences found.”
  - **Error recovery:** on any unexpected diff, restore only that file from its recorded backup, verify pre-hash, and stop before later targets.

- [x] **3.3 Update pipeline routing and current GLM quota fallback documentation/configuration.** Edit only approved active pipeline agent/routing files identified in the inventory. Preserve canonical Stage 5 chain text `zai-coding-plan/glm-5.2` -> `zai-coding-plan/glm-5.1` -> `opencode-go/qwen3.7-plus`, add an operational quota note that current Stage 5 starts with GLM-5.1 then Qwen while GLM-5.2 is exhausted, and ensure Stage 1/planning plus deterministic validation do not depend on GLM-5.2. Maintain independent model families across review pairs.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$files=(Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\approved-routing-map.json' | ConvertFrom-Json).pipeline_files; $body=($files | ForEach-Object { Get-Content -Raw -LiteralPath $_ }) -join "`n"; [bool]($body.Contains('zai-coding-plan/glm-5.2') -and $body.Contains('zai-coding-plan/glm-5.1') -and $body.Contains('opencode-go/qwen3.7-plus') -and $body.Contains('GLM-5.2 quota exhausted') -and $body.Contains('start with GLM-5.1, then Qwen'))"` must print `True`.
  - **Diagnostic checks:** inspect path-scoped diffs and confirm no permission/tool blocks changed.
  - **Error recovery:** if existing fallback syntax differs from documentation, preserve executable syntax and amend the report; do not replace a working fallback with prose-only behavior.

**Exit criteria:** only approved active files changed, all have backups, and pipeline diversity/fallback intent remains explicit.

## Phase 4 Deterministic Validation and Rollback Proof

**Objective:** prove syntax, completeness, distribution, diversity, and reversibility without consuming model quota.

- [x] **4.1 Parse every edited configuration and agent frontmatter.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/parse-validation.json` with one record per edited file, parser used, exit code, and error; JSON uses `ConvertFrom-Json`, JSONC uses the repository's existing parser/`opencode debug config` only if bounded, and Markdown agents require exactly one `model:` plus the expected `variant:` in frontmatter.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\parse-validation.json' | ConvertFrom-Json; [bool](@($j.files).Count -gt 0 -and @($j.files | Where-Object { $_.status -ne 'ok' -or $_.exit_code -ne 0 }).Count -eq 0)"` must print `True`.
  - **Diagnostic checks:** include parser stderr in each failed record, but never expose secrets.
  - **Error recovery:** restore only failed files from manifest backups and rerun the same parser once; if still failing, stop.

- [x] **4.2 Re-scan and reconcile active/historical M3 references.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/post-change-inventory.json` using the identical roots/classifier from Task 2.1 and reconcile each active result to an approved M3-retained assignment. Include `unexplained_active_count`, `historical_unchanged_count`, and `coverage_complete`.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\post-change-inventory.json' | ConvertFrom-Json; [bool]($j.coverage_complete -eq $true -and $j.unexplained_active_count -eq 0 -and $null -ne $j.historical_unchanged_count -and @($j.unreadable_paths).Count -eq 0)"` must print `True`.
  - **Diagnostic checks:** diff pre/post inventories by canonical path and agent name.
  - **Error recovery:** treat any new unreadable path or unexplained hit as validation failure; do not relabel it historical merely to pass.

- [x] **4.3 Validate ratio, invocation auditability, and independent-review diversity.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/diversity-validation.json` containing active assignment counts, Tera ratio, deterministic/persisted invocation-rule proof, and explicit creator-reviewer and executor-validator family pairs. Set `status` to `ok` only if ratio is 40%-60% (or nearest mathematically possible split is documented), every selection is auditable, and same-family pair count is zero.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\diversity-validation.json' | ConvertFrom-Json; [bool]($j.status -eq 'ok' -and $j.same_family_pair_count -eq 0 -and $j.auditable_selection_count -eq $j.assignment_count -and (($j.tera_ratio -ge .4 -and $j.tera_ratio -le .6) -or $j.indivisible_count_exception))"` must print `True`.
  - **Diagnostic checks:** print the full pair matrix and bucket counts.
  - **Error recovery:** rebalance only through a revised approved map; never silently switch a review counterpart.

- [x] **4.4 Prove backup integrity and rollback commands without restoring.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/rollback-validation.json`; verify every backup exists and hashes to the manifest pre-hash, and store per-file literal `Copy-Item -LiteralPath <backup> -Destination <target> -Force` commands plus post-restore hash checks. Do not execute restore commands during a successful run.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\rollback-validation.json' | ConvertFrom-Json; [bool](@($j.files).Count -gt 0 -and @($j.files | Where-Object { -not $_.backup_exists -or -not $_.pre_hash_matches -or -not $_.restore_command -or -not $_.post_restore_hash_command }).Count -eq 0)"` must print `True`.
  - **Diagnostic checks:** compare current hashes to post-change hashes in the manifest.
  - **Error recovery:** if a backup hash fails, stop and do not claim rollback readiness; recover from a separately verified source only with user approval.

**Exit criteria:** all deterministic gates pass and rollback is file-scoped and hash-verifiable.

## Final Phase Validation & Handover

**Objective:** determine restart needs, perform safe live checks when possible, and leave an auditable closeout.

- [x] **5.1 Determine restart requirement before live testing.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/restart-decision.json` from documented OpenCode config-reload behavior and the current host/session state. Include `restart_required`, `evidence`, `safe_to_test_now`, and `reason`. If agent definitions/config are cached or uncertain, set restart required and do not claim pre-restart tests prove effectiveness.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$j=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\restart-decision.json' | ConvertFrom-Json; [bool]($null -ne $j.restart_required -and @($j.evidence).Count -gt 0 -and $null -ne $j.safe_to_test_now -and $j.reason)"` must print `True`.
  - **Diagnostic checks:** record running OpenCode process IDs without waiting on or terminating them.
  - **Error recovery:** when uncertain, require restart and defer live effectiveness claims.

- [x] **5.2 Run bounded live model-resolution smoke tests after any required restart.** For one M3-retained and one Tera-Medium assignment, run the narrowest supported non-interactive `opencode run`/agent invocation with explicit `--model`/`--variant` where available, `--format json`, and tool timeout 120 seconds; prompt `Reply with exactly: routing-ready`. Create `.conductor/tracks/20260715-minimax-m3-half-routing/runtime-validation.md` with command, exit code, selected model evidence, response, restart state, and verdict. Do not call GLM-5.2. If `Error: Session not found` occurs, label deterministic validation passed/runtime blocked and do not retry in a loop.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$s=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\runtime-validation.md'; [bool]($s.Contains('## Restart state') -and $s.Contains('## MiniMax M3 result') -and $s.Contains('## Tera Medium result') -and $s.Contains('## Selected model evidence') -and $s.Contains('## Verdict') -and ($s.Contains('runtime passed') -or $s.Contains('runtime blocked: Error: Session not found')))"` must print `True`.
  - **Diagnostic checks:** retain redacted JSON output in the track evidence directory.
  - **Error recovery:** on quota/auth/provider failure, record exact provider/model/error and stop; do not substitute GLM-5.2 or an unapproved model.

- [x] **5.3 Write final validation and handover report.** Create `.conductor/tracks/20260715-minimax-m3-half-routing/final-validation.md` summarizing changed files, active/historical counts, Tera ratio, routing decision, diversity result, GLM quota workaround, deterministic gates, restart/runtime status, rollback readiness, anomalies, and any deferred live test. Update track bookkeeping only after body evidence exists.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$s=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\final-validation.md'; $required=@('## Changed files','## Inventory reconciliation','## Tera usage ratio','## Routing decision','## Independent-review diversity','## GLM-5.2 quota workaround','## Deterministic validation','## Restart and runtime validation','## Rollback readiness','## Anomalies and deferrals'); [bool](@($required | Where-Object { -not $s.Contains($_) }).Count -eq 0 -and $s.Contains('GLM-5.1') -and $s.Contains('Qwen'))"` must print `True`.
  - **Diagnostic checks:** compare all claimed files with `baseline-manifest.json` and current `git status --porcelain=v1`.
  - **Error recovery:** if any claim lacks an artifact, mark it incomplete/deferred rather than filling with an unsupported success statement.

- [x] **5.4 Upsert Conductor bookkeeping.** Upsert (check then update in place; never duplicate) the track rows in `.conductor/tracks.md` and `.conductor/tracks-ledger.md`, and synchronize `.conductor/tracks/20260715-minimax-m3-half-routing/metadata.json` status/progress/completed counts, pipeline path, execution model, and runtime state. Append anomalies individually under the seven-key schema.
  - **Authoritative acceptance check:** `powershell -NoProfile -Command "$id='20260715-minimax-m3-half-routing'; $a=@(Get-Content -LiteralPath 'C:\development\opencode\.conductor\tracks.md' | Where-Object { $_.Contains($id) }); $b=@(Get-Content -LiteralPath 'C:\development\opencode\.conductor\tracks-ledger.md' | Where-Object { $_.Contains($id) }); $m=Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\metadata.json' | ConvertFrom-Json; [bool]($a.Count -eq 1 -and $b.Count -eq 1 -and $m.track_id -eq $id -and $m.completed_tasks -le $m.total_tasks -and $m.pipeline_mode -eq 'bookkeeping')"` must print `True`.
  - **Diagnostic checks:** validate each anomaly line with `ConvertFrom-Json` and exactly seven property names.
  - **Error recovery:** if duplicate rows exist, consolidate in place while preserving the most complete status; never append a second canonical row.

**Exit criteria:** deterministic work is proven, live status is honestly classified, and all handoff/bookkeeping artifacts agree.

## Execution-readiness checklist

- [ ] User approval is required after the evidence-backed routing map and before runtime edits.
- [ ] Native weighted routing is never assumed; unsupported means fixed pins/paired agents with persisted deterministic selection.
- [ ] Exact Tera model ID and Medium variant are verified before use.
- [ ] Both global `agent`/`agents` paths and every recursive Git root under `C:\development` are covered.
- [ ] Existing uncommitted changes are captured and protected.
- [ ] Stage 5 can start with GLM-5.1 and fall back to Qwen without calling exhausted GLM-5.2.
- [ ] Every command is bounded and non-interactive.
- [ ] Restart precedes any effectiveness claim when caching is possible.

## Top 3 risks and mitigations

1. **Unsupported weighted-routing syntax:** verify installed-version schema/docs; fall back to fixed paired agents and persisted deterministic invocation selection.
2. **Incomplete inventory or accidental historical edits:** scan all recursive Git roots and both user agent spellings, retain raw evidence, classify history separately, and fail on unreadable active paths.
3. **Diversity regression or quota-driven substitution:** validate explicit role-family pairs and preserve Stage 5 GLM-5.2 -> GLM-5.1 -> Qwen policy while operationally starting at GLM-5.1 during the outage.

## First task to execute

Task 0.1: create `preflight.json` with the installed OpenCode version, existing workspace status, and complete recursive Git-root list.
