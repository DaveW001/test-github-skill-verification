# SkillShare Adoption Plan

Track ID: `skillshare-adoption`

## Restatement Before Tasks

- **Goal/outcome:** Document Dave's decision to adopt SkillShare, prove locally that SkillShare can sync a sample skill into an AI-client target directory on Windows, and publish a simple team quickstart.
- **Constraints/non-goals:** Use PowerShell-first execution because native file tools are reported as `Bun is not defined`; do not roll out to 5 users; do not build profiles, daemon scheduling, or hardening; do not block on `packaged-agile` GitHub repo creation.
- **Definition of done:** Decision doc and quickstart doc exist with required body content; SkillShare binary works; a minimal skill is synced into a local target with a deterministic artifact check; future-work gaps are explicit; optional GitHub work is non-blocking.

## Tool / Environment Preflight for Executor

- File-tool status: shell-first. Treat native Read/Edit/Write/glob/grep as unavailable due to `Bun is not defined`.
- Fallback shell: use the `bash` tool running PowerShell 7+ (`pwsh`). Map Read to `Get-Content -Raw -LiteralPath`, Write to `Set-Content -Encoding utf8` only if native Write is unavailable, Edit to `Select-String` plus `[string]::Replace()` rather than regex `-replace`, glob to `Get-ChildItem -Recurse`, and grep to `Select-String`.
- Path quoting: always quote Windows paths with `-LiteralPath "..."`.
- Bounded commands: every `bash` call must include an explicit timeout.
- Artifact writes: avoid bundling a large report into a single inline PowerShell here-string; write small files carefully or use the available file-writing mechanism.

## Phase 0 Setup & Preconditions

Objective: Confirm the workspace and docs directory are ready before installing or writing project artifacts.

- [ ] 0.1 Confirm workspace root and required directories exist.
  - Action: Run this command from `C:\development\opencode`:
    ```powershell
    $ErrorActionPreference = 'Stop';
    if ((Get-Location).Path -ne 'C:\development\opencode') { throw 'Run from C:\development\opencode' }
    if (-not (Test-Path -LiteralPath 'C:\development\opencode\docs\skill-share')) { New-Item -ItemType Directory -Path 'C:\development\opencode\docs\skill-share' | Out-Null }
    if (-not (Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\skillshare-adoption')) { throw 'Missing conductor track directory' }
    'Workspace preconditions ready: docs/skill-share and .conductor/tracks/skillshare-adoption exist.'
    ```
  - Authoritative acceptance check:
    ```powershell
    $ok = (Test-Path -LiteralPath 'C:\development\opencode\docs\skill-share') -and (Test-Path -LiteralPath 'C:\development\opencode\.conductor\tracks\skillshare-adoption'); $ok
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    git status --short
    ```
  - Error recovery: If the docs directory cannot be created, stop and report the permission/path error. If the track directory is missing, recreate it only if `spec.md` and `plan.md` are available from this plan handoff.

- [ ] 0.2 Read the existing objectives spec for context without changing it.
  - Action: Run:
    ```powershell
    $objectives = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\objectives.md';
    if (-not $objectives.Contains('Skill')) { throw 'Objectives file did not contain expected Skill context.' }
    'Objectives context loaded from docs/skill-share/objectives.md.'
    ```
  - Authoritative acceptance check:
    ```powershell
    $text = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\objectives.md'; $text.Contains('Skill')
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    (Get-Item -LiteralPath 'C:\development\opencode\docs\skill-share\objectives.md').Length
    ```
  - Error recovery: If the file is missing, stop and ask Dave whether to continue using only the request context; do not invent missing objective details.

Exit criteria: Workspace path is correct, `docs/skill-share` exists, the conductor track directory exists, and objectives context has been read.

## Phase 1 Implementation: Evaluation and Decision Documentation

Objective: Create the decision record that captures why SkillShare was chosen and what is intentionally deferred.

- [ ] 1.1 Create `docs/skill-share/evaluation-and-decision.md` with the adoption verdict and pros.
  - Action: Create `C:\development\opencode\docs\skill-share\evaluation-and-decision.md` with this body structure and include these exact body sentences:
    ```markdown
    # SkillShare Evaluation and Decision

    ## Decision

    VERDICT: Adopt SkillShare.

    Dave has decided to move forward with SkillShare as the team's shared skill-distribution mechanism.

    ## Why SkillShare Was Chosen

    SkillShare was chosen because it provides multi-tool auto-injection across Claude Desktop, Claude Cowork, OpenCode, and future AI-client targets.

    SkillShare uses native Windows NTFS junctions without requiring administrator rights, ships as a single Go binary with no Node runtime dependency, includes `skillshare audit`, offers `skillshare ui` for a non-technical dashboard, and supports a single-source private-repo Git-backed model.
    ```
  - Authoritative acceptance check:
    ```powershell
    $text = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\evaluation-and-decision.md'; $text.Contains('VERDICT: Adopt SkillShare.') -and $text.Contains('Dave has decided to move forward with SkillShare as the team''s shared skill-distribution mechanism.') -and $text.Contains('SkillShare was chosen because it provides multi-tool auto-injection across Claude Desktop, Claude Cowork, OpenCode, and future AI-client targets.') -and $text.Contains('single Go binary with no Node runtime dependency')
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath 'C:\development\opencode\docs\skill-share\evaluation-and-decision.md' -SimpleMatch 'VERDICT: Adopt SkillShare.'
    ```
  - Error recovery: If writing fails, verify `docs/skill-share` exists and retry with `Set-Content -Encoding utf8`. Do not use regex replacement on markdown structural characters.

- [ ] 1.2 Add explicit future-work gaps and the easy-install goal to `docs/skill-share/evaluation-and-decision.md`.
  - Action: Append sections to the same file containing these exact body sentences:
    ```markdown
    ## Future Work / Revisit Later

    Future work item 1: Per-user selective profiles are not built in; SkillShare is skill/target-centric opt-out filtering, not machine-centric sparse-checkout manifests.

    Future work item 2: A background daemon is not built in; SkillShare is pull-based and manual through `skillshare sync`.

    Future work item 3: Gotcha hardening is not built in; auth connectivity pre-checks, conflict-to-abort-and-notify behavior, and client cache reload guidance must be designed later.

    ## Easy Install Goal

    The rollout goal is to find an easy install path for non-technical team members who use Claude Desktop, Claude Cowork, or OpenCode, with those AI clients able to help run copy-paste install commands.
    ```
  - Authoritative acceptance check:
    ```powershell
    $text = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\evaluation-and-decision.md'; $text.Contains('Future work item 1: Per-user selective profiles are not built in; SkillShare is skill/target-centric opt-out filtering, not machine-centric sparse-checkout manifests.') -and $text.Contains('Future work item 2: A background daemon is not built in; SkillShare is pull-based and manual through `skillshare sync`.') -and $text.Contains('Future work item 3: Gotcha hardening is not built in; auth connectivity pre-checks, conflict-to-abort-and-notify behavior, and client cache reload guidance must be designed later.') -and $text.Contains('The rollout goal is to find an easy install path for non-technical team members who use Claude Desktop, Claude Cowork, or OpenCode, with those AI clients able to help run copy-paste install commands.')
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath 'C:\development\opencode\docs\skill-share\evaluation-and-decision.md' -SimpleMatch 'Future work item'
    ```
  - Error recovery: If the append duplicates content, keep one complete copy of each section and re-run the authoritative acceptance check.

Exit criteria: The evaluation decision doc contains a complete decision, reasons, gaps, and easy-install goal with deterministic body-content checks passing.

## Phase 2 Implementation: Local SkillShare Prototype and Sync Proof

Objective: Install SkillShare, initialize it, create a minimal sample skill, and prove `skillshare sync` injects that skill into at least one local target directory.

- [ ] 2.1 Install SkillShare on Windows and confirm the binary works.
  - Action: Run:
    ```powershell
    $ErrorActionPreference = 'Stop';
    irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex;
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue;
    if (-not $cmd) { $cmd = Get-Command ss -ErrorAction SilentlyContinue }
    if (-not $cmd) { throw 'SkillShare command not found after install.' }
    & $cmd.Source --version
    ```
  - Authoritative acceptance check:
    ```powershell
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command ss -ErrorAction SilentlyContinue }; if (-not $cmd) { 'MISSING' } else { & $cmd.Source --version }
    ```
    Expected output: a version string from SkillShare, not `MISSING`.
  - Diagnostic checks:
    ```powershell
    Get-Command skillshare,ss -ErrorAction SilentlyContinue | Format-Table -AutoSize
    ```
  - Error recovery: If the install script is blocked, download it with `Invoke-WebRequest -UseBasicParsing` to a temp file, inspect it, then run it only if it is the upstream SkillShare installer. If PATH is stale, open a new shell or invoke the installed executable by full path.

- [ ] 2.2 Initialize SkillShare local configuration.
  - Action: Run:
    ```powershell
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command ss -ErrorAction Stop }
    & $cmd.Source init
    ```
  - Authoritative acceptance check:
    ```powershell
    Test-Path -LiteralPath "$env:APPDATA\skillshare"
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    Get-ChildItem -LiteralPath "$env:APPDATA\skillshare" -Force | Format-Table Name,Mode,Length -AutoSize
    ```
  - Error recovery: If `init` reports already initialized, treat that as acceptable and proceed to the acceptance check. If the directory is elsewhere, run `skillshare init --help` and record the discovered path in the execution log.

- [ ] 2.3 Create a minimal sample skill source under `%AppData%\skillshare\skills\skillshare-sync-proof\SKILL.md`.
  - Action: Create directory `$env:APPDATA\skillshare\skills\skillshare-sync-proof` and create `SKILL.md` with this exact body content:
    ```markdown
    ---
    name: skillshare-sync-proof
    description: Minimal local proof that SkillShare sync injects a skill into a configured target.
    targets:
      - opencode
    ---

    # SkillShare Sync Proof

    This sample skill proves that `skillshare sync` can inject a local skill into at least one AI-client target directory on this Windows machine.
    ```
  - Authoritative acceptance check:
    ```powershell
    $text = Get-Content -Raw -LiteralPath "$env:APPDATA\skillshare\skills\skillshare-sync-proof\SKILL.md"; $text.Contains('name: skillshare-sync-proof') -and $text.Contains('Minimal local proof that SkillShare sync injects a skill into a configured target.') -and $text.Contains('This sample skill proves that `skillshare sync` can inject a local skill into at least one AI-client target directory on this Windows machine.')
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    Get-ChildItem -LiteralPath "$env:APPDATA\skillshare\skills\skillshare-sync-proof" -Force | Format-Table Name,Length -AutoSize
    ```
  - Error recovery: If `$env:APPDATA\skillshare\skills` is missing, create it after confirming `$env:APPDATA\skillshare` exists. If a previous proof skill exists, overwrite only this proof skill and do not modify other skills.

- [ ] 2.4 Configure at least one local target directory for OpenCode or Claude and run `skillshare sync`.
  - Action: Prefer a repo-local safe target so the proof is non-destructive. Run:
    ```powershell
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command ss -ErrorAction Stop }
    $targetRoot = 'C:\development\opencode\.conductor\tracks\skillshare-adoption\local-sync-target\opencode\skill'
    New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
    & $cmd.Source target opencode $targetRoot
    & $cmd.Source sync
    ```
    If `target opencode <path>` is not the correct syntax, run `skillshare target --help`, use the documented syntax to point the `opencode` target at the same `$targetRoot`, record the exact command in the execution log, then run `skillshare sync`.
  - Authoritative acceptance check:
    ```powershell
    $matches = Get-ChildItem -LiteralPath 'C:\development\opencode\.conductor\tracks\skillshare-adoption\local-sync-target' -Recurse -Force -Filter 'SKILL.md' | Where-Object { (Get-Content -Raw -LiteralPath $_.FullName).Contains('This sample skill proves that `skillshare sync` can inject a local skill into at least one AI-client target directory on this Windows machine.') }; @($matches).Count -ge 1
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    Get-ChildItem -LiteralPath 'C:\development\opencode\.conductor\tracks\skillshare-adoption\local-sync-target' -Recurse -Force | Format-Table FullName,Mode,Length -AutoSize
    ```
  - Error recovery: If `target` syntax fails, use `skillshare target --help` and adapt only the target-registration command. If junction creation is blocked, run `skillshare target opencode --mode copy` or the documented copy-mode equivalent, then re-run `skillshare sync`. If the target contains unrelated existing files, stop before overwriting and choose the repo-local target above.

- [ ] 2.5 Run SkillShare audit and record non-blocking results in the execution log.
  - Action: Run:
    ```powershell
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command ss -ErrorAction Stop }
    & $cmd.Source audit
    ```
  - Authoritative acceptance check:
    ```powershell
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command ss -ErrorAction Stop }; $output = & $cmd.Source audit 2>&1 | Out-String; $output.Length -gt 0
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command ss -ErrorAction Stop }; & $cmd.Source audit 2>&1
    ```
  - Error recovery: If audit returns findings, do not fail the track solely for warnings; record the findings in the execution log and continue unless the audit proves the proof skill is unsafe or unsynced.

Exit criteria: SkillShare command exists, initialization completed, a proof skill exists in the SkillShare source directory, and sync produced a proof `SKILL.md` artifact in the repo-local target.

## Phase 3 Implementation: Team Quickstart and Deferred GitHub Notes

Objective: Write a copy-pasteable quickstart for non-technical users and record that GitHub org setup is optional/deferred.

- [ ] 3.1 Create `docs/skill-share/quickstart-for-team.md` with simple install and first-sync instructions.
  - Action: Create `C:\development\opencode\docs\skill-share\quickstart-for-team.md` with this body structure and include these exact body sentences and commands:
    ```markdown
    # SkillShare Quickstart for Team Members

    This guide is for non-technical team members, or for Claude Desktop, Claude Cowork, or OpenCode helping a team member run the commands.

    ## Step 1: Install SkillShare

    Copy and paste this into PowerShell:

    ```powershell
    irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex
    skillshare --version
    ```

    ## Step 2: Connect to the shared skill source

    Dave will provide the final private repository URL from the packaged-agile GitHub organization.

    ```powershell
    skillshare install https://github.com/packaged-agile/TEAM-SKILLS-REPO.git
    ```

    ## Step 3: Run your first sync

    ```powershell
    skillshare sync
    ```

    If `skillshare` is not recognized, try `ss --version` and `ss sync`, or close and reopen PowerShell.
    ```
  - Authoritative acceptance check:
    ```powershell
    $text = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\quickstart-for-team.md'; $text.Contains('This guide is for non-technical team members, or for Claude Desktop, Claude Cowork, or OpenCode helping a team member run the commands.') -and $text.Contains('irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex') -and $text.Contains('skillshare install https://github.com/packaged-agile/TEAM-SKILLS-REPO.git') -and $text.Contains('If `skillshare` is not recognized, try `ss --version` and `ss sync`, or close and reopen PowerShell.')
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath 'C:\development\opencode\docs\skill-share\quickstart-for-team.md' -SimpleMatch 'skillshare sync'
    ```
  - Error recovery: If markdown code fences are malformed, rewrite the file and verify that each fenced block starts and ends with triple backticks.

- [ ] 3.2 Add a clear future-work section to the quickstart for profiles, daemon, and gotcha hardening.
  - Action: Append this exact content to `docs/skill-share/quickstart-for-team.md`:
    ```markdown
    ## Future Work / Not Required for First Sync

    Future work: per-user selective profiles will be designed later.

    Future work: background automatic sync through Task Scheduler or another daemon-style wrapper will be designed later.

    Future work: gotcha hardening for auth checks, conflict handling, and client cache reloads will be designed later.
    ```
  - Authoritative acceptance check:
    ```powershell
    $text = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\quickstart-for-team.md'; $text.Contains('Future work: per-user selective profiles will be designed later.') -and $text.Contains('Future work: background automatic sync through Task Scheduler or another daemon-style wrapper will be designed later.') -and $text.Contains('Future work: gotcha hardening for auth checks, conflict handling, and client cache reloads will be designed later.')
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    Select-String -LiteralPath 'C:\development\opencode\docs\skill-share\quickstart-for-team.md' -SimpleMatch 'Future work:'
    ```
  - Error recovery: If the append duplicates the section, keep one complete future-work section and rerun the acceptance check.

- [ ] 3.3 Optionally check whether `packaged-agile` GitHub repo creation is ready, but do not block completion.
  - Action: Run:
    ```powershell
    gh auth status
    gh repo view packaged-agile/skillshare-skills
    ```
    If `gh auth status` is ready and Dave has owner access, the executor may ask Dave for permission before running `gh repo create packaged-agile/skillshare-skills --private --description 'Shared SkillShare skill source for Packaged Agile'`. If auth or owner rights are not ready, record `GitHub repo creation deferred/manual` in the execution log.
  - Authoritative acceptance check:
    ```powershell
    'GitHub repo creation is optional/deferred and not required for local prototype completion.'
    ```
    Expected output: `GitHub repo creation is optional/deferred and not required for local prototype completion.`
  - Diagnostic checks:
    ```powershell
    gh auth status
    ```
  - Error recovery: If `gh` is missing or unauthenticated, record that repo creation is deferred/manual; do not fail the track.

Exit criteria: The quickstart doc is copy-pasteable, future work is explicit, and GitHub org setup is documented as optional/deferred.

## Final Phase Validation & Handover

Objective: Validate deliverables, update Conductor bookkeeping, and provide a handoff log.

- [ ] 4.1 Run deterministic content validation for both documentation deliverables.
  - Action: Run:
    ```powershell
    $decision = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\evaluation-and-decision.md'
    $quickstart = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\quickstart-for-team.md'
    $ok = $decision.Contains('VERDICT: Adopt SkillShare.') -and $decision.Contains('The rollout goal is to find an easy install path for non-technical team members who use Claude Desktop, Claude Cowork, or OpenCode, with those AI clients able to help run copy-paste install commands.') -and $quickstart.Contains('skillshare install https://github.com/packaged-agile/TEAM-SKILLS-REPO.git') -and $quickstart.Contains('Future work: gotcha hardening for auth checks, conflict handling, and client cache reloads will be designed later.')
    $ok
    ```
  - Authoritative acceptance check:
    ```powershell
    $decision = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\evaluation-and-decision.md'; $quickstart = Get-Content -Raw -LiteralPath 'C:\development\opencode\docs\skill-share\quickstart-for-team.md'; $decision.Contains('VERDICT: Adopt SkillShare.') -and $decision.Contains('The rollout goal is to find an easy install path for non-technical team members who use Claude Desktop, Claude Cowork, or OpenCode, with those AI clients able to help run copy-paste install commands.') -and $quickstart.Contains('skillshare install https://github.com/packaged-agile/TEAM-SKILLS-REPO.git') -and $quickstart.Contains('Future work: gotcha hardening for auth checks, conflict handling, and client cache reloads will be designed later.')
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    git diff -- docs/skill-share/evaluation-and-decision.md docs/skill-share/quickstart-for-team.md
    ```
  - Error recovery: If validation fails, inspect the missing exact substring, fix the body content, and rerun this task before proceeding.

- [ ] 4.2 Run deterministic local prototype validation.
  - Action: Run:
    ```powershell
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command ss -ErrorAction SilentlyContinue }
    $binaryOk = $null -ne $cmd
    $sourceOk = (Get-Content -Raw -LiteralPath "$env:APPDATA\skillshare\skills\skillshare-sync-proof\SKILL.md").Contains('name: skillshare-sync-proof')
    $matches = Get-ChildItem -LiteralPath 'C:\development\opencode\.conductor\tracks\skillshare-adoption\local-sync-target' -Recurse -Force -Filter 'SKILL.md' | Where-Object { (Get-Content -Raw -LiteralPath $_.FullName).Contains('This sample skill proves that `skillshare sync` can inject a local skill into at least one AI-client target directory on this Windows machine.') }
    ($binaryOk -and $sourceOk -and (@($matches).Count -ge 1))
    ```
  - Authoritative acceptance check:
    ```powershell
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command ss -ErrorAction SilentlyContinue }; $binaryOk = $null -ne $cmd; $sourceOk = (Get-Content -Raw -LiteralPath "$env:APPDATA\skillshare\skills\skillshare-sync-proof\SKILL.md").Contains('name: skillshare-sync-proof'); $matches = Get-ChildItem -LiteralPath 'C:\development\opencode\.conductor\tracks\skillshare-adoption\local-sync-target' -Recurse -Force -Filter 'SKILL.md' | Where-Object { (Get-Content -Raw -LiteralPath $_.FullName).Contains('This sample skill proves that `skillshare sync` can inject a local skill into at least one AI-client target directory on this Windows machine.') }; ($binaryOk -and $sourceOk -and (@($matches).Count -ge 1))
    ```
    Expected output: `True`
  - Diagnostic checks:
    ```powershell
    $cmd = Get-Command skillshare -ErrorAction SilentlyContinue; if (-not $cmd) { $cmd = Get-Command ss -ErrorAction SilentlyContinue }; if ($cmd) { & $cmd.Source --version }
    ```
  - Error recovery: If the target artifact is missing, rerun Phase 2.4 with the documented `target --help` fallback, then rerun this validation.

- [ ] 4.3 Create `execution-log-YYYY-MM-DD.md` and update Conductor bookkeeping.
  - Action: Create `C:\development\opencode\.conductor\tracks\skillshare-adoption\execution-log-YYYY-MM-DD.md` using the actual date, then update `plan.md`, `metadata.json`, `.conductor/tracks.md`, and `.conductor/tracks-ledger.md` according to the Conductor executor closeout checklist. The log must include these exact body sentences:
    ```markdown
    Local SkillShare sync proof completed.

    GitHub repo creation under packaged-agile was treated as optional/deferred unless gh auth and owner access were ready.

    Future-work gaps remain: per-user profiles, background daemon sync, and gotcha hardening.
    ```
  - Authoritative acceptance check:
    ```powershell
    $log = Get-ChildItem -LiteralPath 'C:\development\opencode\.conductor\tracks\skillshare-adoption' -Filter 'execution-log-*.md' | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if (-not $log) { $false } else { $text = Get-Content -Raw -LiteralPath $log.FullName; $text.Contains('Local SkillShare sync proof completed.') -and $text.Contains('GitHub repo creation under packaged-agile was treated as optional/deferred unless gh auth and owner access were ready.') -and $text.Contains('Future-work gaps remain: per-user profiles, background daemon sync, and gotcha hardening.') }
    $meta = Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks\skillshare-adoption\metadata.json' -ErrorAction SilentlyContinue
    $metaOk = $false; if ($meta) { $j = $meta | ConvertFrom-Json; $n = $j.PSObject.Properties.Name; $metaOk = (($n -contains 'status') -and ($n -contains 'progress') -and ($n -contains 'task_count') -and ($n -contains 'completed_tasks') -and ($n -contains 'executed_at') -and ($n -contains 'executor_model')) }
    $tracksOk = (Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks.md').Contains('skillshare-adoption')
    $ledgerOk = (Get-Content -Raw -LiteralPath 'C:\development\opencode\.conductor\tracks-ledger.md').Contains('skillshare-adoption')
    ($log -ne $null) -and $log -ne $null -and ($text.Contains('Local SkillShare sync proof completed.') -and $text.Contains('GitHub repo creation under packaged-agile was treated as optional/deferred unless gh auth and owner access were ready.') -and $text.Contains('Future-work gaps remain: per-user profiles, background daemon sync, and gotcha hardening.')) -and $metaOk -and $tracksOk -and $ledgerOk
    ```
    Expected output: `True`
  - Bookkeeping-update sub-actions (in order):
    1. Write `metadata.json` with `track_id="skillshare-adoption"`, `status` matching actual completion (e.g., `executed`), `progress` like `"15/15"`, `task_count=15`, `readiness_check_count=5`, `total_checkbox_count=20`, `completed_tasks=15`, `executed_at` captured once at the start of execution (do NOT recompute at closeout), `executor_model="zai-coding-plan/glm-5.2"`, `updated_at` mirroring `executed_at`. Use `ConvertTo-Json -Depth 5` and a single `[System.IO.File]::WriteAllText()` write.
    2. Append or upsert a single row in `.conductor/tracks.md` for track `skillshare-adoption` with the final status, completed date, and the path `C:\development\opencode\.conductor\tracks\skillshare-adoption`. Do not duplicate existing rows.
    3. Append or upsert a single entry in `.conductor/tracks-ledger.md` for the track, with a one-line spec pointer and the final phase. Do not duplicate existing entries.
  - Diagnostic checks:
    ```powershell
    git status --short
    ```
  - Error recovery: If bookkeeping files do not exist, create only the missing Conductor files needed by local convention and record the deviation in the execution log. Do not mark tasks complete without the deliverable validations in 4.1 and 4.2 passing.

Exit criteria: Documentation and local prototype validations return `True`, an execution log exists, and Conductor bookkeeping is synchronized.

## Execution-Readiness Checklist

- [ ] Executor can run PowerShell commands from `C:\development\opencode` with explicit timeouts.
- [ ] Network access is available for the SkillShare installer.
- [ ] The executor understands that GitHub org repo creation is optional/deferred and not part of the blocking definition of done.
- [ ] The executor will not modify global Claude/OpenCode config unless it intentionally chooses a safe target and records it; the preferred proof target is repo-local.
- [ ] Every task has exactly one `Authoritative acceptance check:` and diagnostic checks are separate.

## Top 3 Risks and Mitigations

1. **SkillShare `target` command syntax differs from the assumed command.** Mitigation: use `skillshare target --help`, adapt only the target-registration command, and record the exact command in the execution log.
2. **Installer or PATH update does not make `skillshare` immediately available.** Mitigation: try `ss`, reopen the shell, or invoke the installed executable by full path after locating it with `Get-Command` or the install output.
3. **Sync could affect a real AI-client config directory unexpectedly.** Mitigation: use the repo-local target `C:\development\opencode\.conductor\tracks\skillshare-adoption\local-sync-target\opencode\skill` for the proof unless Dave explicitly approves a real client directory.

## First Task to Execute

Start with task **0.1 Confirm workspace root and required directories exist**.
