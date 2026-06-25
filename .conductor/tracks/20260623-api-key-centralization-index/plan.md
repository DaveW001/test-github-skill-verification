# API Key Centralization Index Plan

## Brief Restatement

**Goal/outcome:** create a metadata-only API key discovery index and agent lookup rule so future agents can find required keys and canonical locations quickly without exposing values.

**Constraints/non-goals:** do not move, delete, rotate, print, or store secret values; do not edit production source code; do not introduce OS keychain/cloud secret manager/symlink automation; do not touch Firebase env layout beyond documenting it; prioritize convenience and discoverability.

**Definition of done:** `secrets-index.jsonc` exists with audited key metadata only, `AGENTS.md` points agents to it, `conductor-reporter\.gitignore` ignores `.env`, handover encoding artifacts are cleaned, and deterministic PowerShell validation passes.

## Phase 0: Setup & Preconditions

Objective: verify required paths exist and establish a no-secret-values working mode before editing files.

- [x] **Task 0.1: Verify the global OpenCode config directory exists.**  
  File path: `C:\Users\DaveWitkin\.config\opencode`  
  Command:
  ```powershell
  Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode"
  ```
  Expected output: `True`  
  Error recovery: if output is `False`, stop and ask the user for the correct OpenCode config path.

- [x] **Task 0.2: Verify the handover document exists.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\docs\handovers\api-key-centralization-handover-20260623.md`  
  Command:
  ```powershell
  Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\docs\handovers\api-key-centralization-handover-20260623.md"
  ```
  Expected output: `True`  
  Error recovery: if output is `False`, stop; do not recreate audit findings from memory.

- [x] **Task 0.3: Verify the conductor-reporter repo directory exists.**  
  File path: `C:\development\conductor-reporter`  
  Command:
  ```powershell
  Test-Path -LiteralPath "C:\development\conductor-reporter"
  ```
  Expected output: `True`  
  Error recovery: if output is `False`, skip Phase 2 and document the skipped gitignore fix in the Final Phase handover.

- [x] **Task 0.4: Verify this Conductor track files exist before execution.**  
  File paths: `C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\spec.md`, `C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\plan.md`  
  Command:
  ```powershell
  Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\spec.md"; Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\plan.md"
  ```
  Expected output: two `True` lines.  
  Error recovery: if either is `False`, stop and ask the user to reopen the planning handoff.

Phase-level exit criteria: all required setup checks return `True`, or the only skipped item is the conductor-reporter path with a documented skip.

## Phase 1: Create Metadata-Only Secrets Index

Objective: create `secrets-index.jsonc` with audited key names, canonical locations, consumers, scopes, duplicate locations, and status metadata only.

- [x] **Task 1.1: Create `secrets-index.jsonc` with metadata-only content.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc`  
  Command:
  ```powershell
  @'
  {
    "version": 1,
    "last_audited": "2026-06-23",
    "policy": {
      "store_values": false,
      "preferred_lookup_order": [
        "C:\\Users\\DaveWitkin\\.config\\opencode\\secrets-index.jsonc",
        "documented canonical_location paths",
        "documented consumer repo .env files",
        "skill-scoped .env files"
      ],
      "never_print_secret_values": true,
      "notes": "This file stores key names and locations only. It must never contain API key values."
    },
    "secrets": {
      "openrouter.api_key": { "env": "OPENROUTER_API_KEY", "service": "OpenRouter", "scope": "opencode-runtime", "canonical_location": "C:\\Users\\DaveWitkin\\.config\\opencode\\.env", "consumers": ["OpenCode global config and agents"], "duplicate_locations": [], "status": "active", "rotation_impact": "single-location", "notes": "Existing global OpenCode runtime key.", "last_verified": "2026-06-23" },
      "opencode_go.dave_api_key": { "env": "OPENCODE_GO_DAVE_API_KEY", "service": "OpenCode Go / Codex Dave account", "scope": "opencode-runtime", "canonical_location": "C:\\Users\\DaveWitkin\\.config\\opencode\\.env", "consumers": ["OpenCode global config and agents"], "duplicate_locations": [], "status": "active", "rotation_impact": "single-location", "notes": "Existing global OpenCode runtime key.", "last_verified": "2026-06-23" },
      "opencode_go.tiberius_api_key": { "env": "OPENCODE_GO_TIBERIUS_API_KEY", "service": "OpenCode Go / Codex Tiberius account", "scope": "opencode-runtime", "canonical_location": "C:\\Users\\DaveWitkin\\.config\\opencode\\.env", "consumers": ["OpenCode global config and agents"], "duplicate_locations": [], "status": "active", "rotation_impact": "single-location", "notes": "Existing global OpenCode runtime key.", "last_verified": "2026-06-23" },
      "zai.api_key": { "env": "ZAI_API_KEY", "service": "Z.AI / GLM", "scope": "opencode-runtime", "canonical_location": "C:\\Users\\DaveWitkin\\.config\\opencode\\.env", "consumers": ["OpenCode global config and agents"], "duplicate_locations": [], "status": "active", "rotation_impact": "single-location", "notes": "Existing global OpenCode runtime key.", "last_verified": "2026-06-23" },
      "perplexity.api_key": { "env": "PERPLEXITYAI_API_KEY", "service": "Perplexity AI", "scope": "skill", "canonical_location": "C:\\Users\\DaveWitkin\\.config\\opencode\\skill\\perplexity-search\\.env", "consumers": ["C:\\Users\\DaveWitkin\\.config\\opencode\\skill\\perplexity-search"], "duplicate_locations": [], "status": "active", "rotation_impact": "single-location", "notes": "Skill-scoped key; candidate for future global env move only if user wants it.", "last_verified": "2026-06-23" },
      "clickup.api_token": { "env": "CLICKUP_API_TOKEN", "service": "ClickUp", "scope": "shared", "canonical_location": "C:\\development\\cursor-clickup-mcp\\.env", "consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\govpulse"], "duplicate_locations": ["C:\\development\\govpulse\\.env"], "status": "active", "rotation_impact": "multi-repo", "notes": "Candidate for future shared central env after repo loading behavior is confirmed.", "last_verified": "2026-06-23" },
      "slack.bot_token": { "env": "SLACK_BOT_TOKEN", "service": "Slack", "scope": "shared", "canonical_location": "C:\\development\\cursor-clickup-mcp\\.env", "consumers": ["C:\\development\\cursor-clickup-mcp", "C:\\development\\conductor-reporter"], "duplicate_locations": ["C:\\development\\conductor-reporter\\.env"], "status": "active", "rotation_impact": "multi-repo", "notes": "Fix conductor-reporter .gitignore before any git add operations.", "last_verified": "2026-06-23" },
      "exa.api_key": { "env": "EXA_API_KEY", "service": "Exa", "scope": "shared", "canonical_location": "C:\\development\\marketing\\.env", "consumers": ["C:\\development\\marketing", "C:\\development\\INACTIVE-content-marketing"], "duplicate_locations": ["C:\\development\\INACTIVE-content-marketing\\.env.search"], "status": "active", "rotation_impact": "multi-repo", "notes": "Inactive repo duplicate should be reviewed before rotation/deletion.", "last_verified": "2026-06-23" },
      "google.api_key": { "env": "GOOGLE_API_KEY", "service": "Google Custom Search/API", "scope": "shared", "canonical_location": "C:\\development\\marketing\\.env", "consumers": ["C:\\development\\marketing", "C:\\development\\INACTIVE-content-marketing"], "duplicate_locations": ["C:\\development\\INACTIVE-content-marketing\\.env.search"], "status": "active", "rotation_impact": "multi-repo", "notes": "Pairs with GOOGLE_CSE_ID for search workflows.", "last_verified": "2026-06-23" },
      "google.cse_id": { "env": "GOOGLE_CSE_ID", "service": "Google Custom Search Engine", "scope": "shared", "canonical_location": "C:\\development\\marketing\\.env", "consumers": ["C:\\development\\marketing", "C:\\development\\INACTIVE-content-marketing"], "duplicate_locations": ["C:\\development\\INACTIVE-content-marketing\\.env.search"], "status": "active", "rotation_impact": "multi-repo", "notes": "Identifier/config value paired with GOOGLE_API_KEY.", "last_verified": "2026-06-23" },
      "serpapi.api_key": { "env": "SERPAPI_API_KEY", "service": "SerpAPI", "scope": "shared", "canonical_location": "C:\\development\\marketing\\.env", "consumers": ["C:\\development\\marketing", "C:\\development\\INACTIVE-content-marketing"], "duplicate_locations": ["C:\\development\\INACTIVE-content-marketing\\.env.search"], "status": "active", "rotation_impact": "multi-repo", "notes": "Inactive repo duplicate should be reviewed before rotation/deletion.", "last_verified": "2026-06-23" },
      "inactive_content_marketing.openai_api_key": { "env": "OPENAI_API_KEY", "service": "OpenAI", "scope": "orphan", "canonical_location": "C:\\development\\INACTIVE-content-marketing\\.env.search", "consumers": ["C:\\development\\INACTIVE-content-marketing"], "duplicate_locations": [], "status": "orphan", "rotation_impact": "unknown", "notes": "Possibly retired/orphaned; do not delete or rotate without explicit user approval.", "last_verified": "2026-06-23" },
      "inactive_content_marketing.gemini_api_key": { "env": "GEMINI_API_KEY", "service": "Google Gemini", "scope": "orphan", "canonical_location": "C:\\development\\INACTIVE-content-marketing\\.env.search", "consumers": ["C:\\development\\INACTIVE-content-marketing"], "duplicate_locations": [], "status": "orphan", "rotation_impact": "unknown", "notes": "Possibly retired/orphaned; do not delete or rotate without explicit user approval.", "last_verified": "2026-06-23" },
      "repo_project_configs": { "env": ["KV_REST_API_READ_ONLY_TOKEN", "KV_REST_API_TOKEN", "KV_REST_API_URL", "KV_URL", "NEXT_PUBLIC_GA_ID", "REDIS_URL", "RESEND_API_KEY", "VERCEL_OIDC_TOKEN", "NEXT_PUBLIC_FIREBASE_*", "GLM_API_BASE_URL", "GLM_API_KEY", "GLM_MODEL_ID", "GLM_TRIVIAL_MODEL_ID", "SAM_GOV_API_KEY", "GITHUB_USER", "GITHUB_TOKEN", "ACOUSTID_CLIENT_KEY", "ACOUSTID_CLIENT_NAME", "ACOUSTID_CLIENT_VERSION"], "service": "Repo/project-specific configs", "scope": "repo", "canonical_location": "See handover document section 4b per-repo .env table.", "consumers": ["C:\\development\\2025-pa-website", "C:\\development\\command-center", "C:\\development\\margin-calc-firebase", "C:\\development\\govpulse", "C:\\development\\create-new-github-repository", "C:\\development\\music_duplicates"], "duplicate_locations": ["C:\\development\\2025-pa-website\\.env.local and .env.development.local", "C:\\development\\command-center\\.env.local and .firebase\\command-ctr-pa\\functions\\.env.local"], "status": "active", "rotation_impact": "project-specific", "notes": "Keep repo-local unless a future track confirms each toolchain can load shared env safely. Treat NEXT_PUBLIC_FIREBASE_* as public/project config.", "last_verified": "2026-06-23" }
    }
  }
  '@ | Set-Content -Encoding utf8 -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc"
  ```
  Expected output: no error output.  
  Error recovery: if PowerShell reports access denied, retry from an elevated shell only after confirming with the user; do not write the file elsewhere.

- [x] **Task 1.2: Verify `secrets-index.jsonc` exists.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc`  
  Command:
  ```powershell
  Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc"
  ```
  Expected output: `True`  
  Error recovery: if `False`, rerun Task 1.1 and check for path typos.

- [x] **Task 1.3: Verify the index includes expected key names.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc`  
  Command:
  ```powershell
  $text = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc"; @("OPENROUTER_API_KEY","PERPLEXITYAI_API_KEY","CLICKUP_API_TOKEN","SLACK_BOT_TOKEN","EXA_API_KEY","GOOGLE_API_KEY","SERPAPI_API_KEY","OPENAI_API_KEY") | ForEach-Object { if ($text -notmatch [regex]::Escape($_)) { "MISSING $_" } else { "FOUND $_" } }
  ```
  Expected output: eight `FOUND ...` lines and zero `MISSING ...` lines.  
  Error recovery: if any key is missing, edit only `secrets-index.jsonc` to add the missing metadata entry; do not inspect secret values.

- [x] **Task 1.4: Verify the index contains no obvious secret values or raw env assignments.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc`  
  Command:
  ```powershell
  $text = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc"; $patterns = @('sk-[A-Za-z0-9_-]{20,}','xox[baprs]-[A-Za-z0-9-]{20,}','gh[pousr]_[A-Za-z0-9_]{20,}','(?m)^\s*[A-Z0-9_]+\s*=\s*[^\s#]'); $hits = foreach ($p in $patterns) { [regex]::Matches($text, $p) }; if (($hits | Measure-Object).Count -eq 0) { "PASS no obvious secret values" } else { "FAIL possible secret value pattern found" }
  ```
  Expected output: `PASS no obvious secret values`  
  Error recovery: if output starts with `FAIL`, remove any value-like content from the index and rerun this command before continuing.

Phase-level exit criteria: index exists, expected key names are present, and the no-obvious-secret-values check passes.

## Phase 2: Add Agent Lookup Rule

Objective: make future agents consult the secrets index before searching repos for API keys.

- [x] **Task 2.1: Create a timestamped backup of `AGENTS.md`.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`  
  Command:
  ```powershell
  $src = "C:\Users\DaveWitkin\.config\opencode\AGENTS.md"; $bak = "C:\Users\DaveWitkin\.config\opencode\AGENTS.md.api-key-index-backup-20260623"; Copy-Item -LiteralPath $src -Destination $bak -Force; Test-Path -LiteralPath $bak
  ```
  Expected output: `True`  
  Error recovery: if source path is missing, stop and ask the user before creating a new AGENTS.md.

- [x] **Task 2.2: Insert the API key lookup rule after the Knowledge Graph Entity Lookup section.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`  
  Command:
  ```powershell
  $path = "C:\Users\DaveWitkin\.config\opencode\AGENTS.md"; $text = Get-Content -Raw -LiteralPath $path; $rule = @'

### API Keys / Secrets Lookup
Before searching repos for API keys or service credentials, consult `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc`. This metadata-only index contains key names, services, canonical locations, consuming repos, duplicate locations, and status notes. Never print, copy, or commit secret values.
'@; if ($text -notmatch '### API Keys / Secrets Lookup') { $marker = '### ClickUp Quick References'; $text = $text.Replace($marker, $rule + "`r`n" + $marker); Set-Content -Encoding utf8 -LiteralPath $path -Value $text }; Select-String -LiteralPath $path -Pattern 'API Keys / Secrets Lookup','secrets-index.jsonc'
  ```
  Expected output: matching lines containing `API Keys / Secrets Lookup` and `secrets-index.jsonc`.  
  Error recovery: if `### ClickUp Quick References` is not found, append the rule immediately after the `Knowledge Graph Entity Lookup` paragraph manually, then rerun the `Select-String` part.

- [x] **Task 2.3: Verify the lookup rule is present exactly once.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`  
  Command:
  ```powershell
  ((Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\AGENTS.md" -Pattern '### API Keys / Secrets Lookup').Count)
  ```
  Expected output: `1`  
  Error recovery: if output is greater than `1`, remove duplicate inserted sections and rerun this task.

Phase-level exit criteria: AGENTS.md contains exactly one API key lookup rule and a backup file exists.

## Phase 3: Fix conductor-reporter Gitignore Gap

Objective: prevent accidental commits of `C:\development\conductor-reporter\.env`.

- [x] **Task 3.1: Verify or create `C:\development\conductor-reporter\.gitignore`.**  
  File path: `C:\development\conductor-reporter\.gitignore`  
  Command:
  ```powershell
  $path = "C:\development\conductor-reporter\.gitignore"; if (-not (Test-Path -LiteralPath $path)) { New-Item -ItemType File -Path $path | Out-Null }; Test-Path -LiteralPath $path
  ```
  Expected output: `True`  
  Error recovery: if parent directory is missing, skip Phase 3 and document the skip in Final Phase.

- [x] **Task 3.2: Add `.env` to `conductor-reporter\.gitignore` if absent.**  
  File path: `C:\development\conductor-reporter\.gitignore`  
  Command:
  ```powershell
  $path = "C:\development\conductor-reporter\.gitignore"; $text = Get-Content -Raw -LiteralPath $path; if ($text -notmatch '(?m)^\.env$') { Add-Content -Encoding utf8 -LiteralPath $path -Value "`n.env" }; Select-String -LiteralPath $path -Pattern '^\.env$'
  ```
  Expected output: one matching `.env` line.  
  Error recovery: if duplicate `.env` entries are created, leave one exact `.env` line and rerun this task.

- [x] **Task 3.3: Verify Git ignores `conductor-reporter\.env`.**  
  File path: `C:\development\conductor-reporter\.env`  
  Command:
  ```powershell
  git -C "C:\development\conductor-reporter" check-ignore -v -- ".env"
  ```
  Expected output: a line referencing `.gitignore` and `.env`.  
  Error recovery: if output is empty and exit code is nonzero, verify the repo is a Git repo with `git -C "C:\development\conductor-reporter" rev-parse --is-inside-work-tree`; if that returns `true`, fix `.gitignore` syntax and rerun.

Phase-level exit criteria: `.gitignore` contains `.env` and `git check-ignore` confirms it applies.

## Phase 4: Clean Handover Encoding Artifacts

Objective: make the existing handover readable for future agents without changing audit meaning.

- [x] **Task 4.1: Replace known control-character artifacts in the handover document.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\docs\handovers\api-key-centralization-handover-20260623.md`  
  Command:
  ```powershell
  $path = "C:\Users\DaveWitkin\.config\opencode\docs\handovers\api-key-centralization-handover-20260623.md"; $text = Get-Content -Raw -LiteralPath $path; $text = $text.Replace([char]0x15, 'section ').Replace([char]0x1A, '->'); Set-Content -Encoding utf8 -LiteralPath $path -Value $text; "updated"
  ```
  Expected output: `updated`  
  Error recovery: if the file is missing, skip this phase and document the skip in Final Phase.

- [x] **Task 4.2: Verify known control characters are gone.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\docs\handovers\api-key-centralization-handover-20260623.md`  
  Command:
  ```powershell
  $text = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\docs\handovers\api-key-centralization-handover-20260623.md"; if ($text.Contains([char]0x15) -or $text.Contains([char]0x1A)) { "FAIL control characters remain" } else { "PASS no known control characters" }
  ```
  Expected output: `PASS no known control characters`  
  Error recovery: if `FAIL`, inspect only surrounding text and replace the bad characters with ASCII equivalents; do not alter key findings or values.

Phase-level exit criteria: handover no longer contains the known control characters, or the phase is explicitly skipped because the file is absent.

## Final Phase: Validation & Handover

Objective: run deterministic validation, update Conductor status, and leave a concise execution handover.

- [x] **Task 5.1: Run consolidated validation for all expected artifacts.**  
  File paths: `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc`, `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`, `C:\development\conductor-reporter\.gitignore`  
  Command:
  ```powershell
  $checks = [ordered]@{}; $checks.indexExists = Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc"; $checks.agentsRule = [bool](Select-String -LiteralPath "C:\Users\DaveWitkin\.config\opencode\AGENTS.md" -Pattern 'secrets-index.jsonc' -Quiet); $checks.gitignoreEnv = [bool](Select-String -LiteralPath "C:\development\conductor-reporter\.gitignore" -Pattern '^\.env$' -Quiet); $checks | ConvertTo-Json
  ```
  Expected output: JSON with `indexExists`, `agentsRule`, and `gitignoreEnv` all `true`.  
  Error recovery: if any value is `false`, return to the phase responsible for that artifact and rerun its verification task.

- [x] **Task 5.2: Run final no-secret-pattern check on the index.**  
  File path: `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc`  
  Command:
  ```powershell
  $text = Get-Content -Raw -LiteralPath "C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc"; $patterns = @('sk-[A-Za-z0-9_-]{20,}','xox[baprs]-[A-Za-z0-9-]{20,}','gh[pousr]_[A-Za-z0-9_]{20,}','(?m)^\s*[A-Z0-9_]+\s*=\s*[^\s#]'); $hits = foreach ($p in $patterns) { [regex]::Matches($text, $p) }; if (($hits | Measure-Object).Count -eq 0) { "PASS no obvious secret values" } else { "FAIL possible secret value pattern found" }
  ```
  Expected output: `PASS no obvious secret values`  
  Error recovery: if `FAIL`, remove value-like content and repeat Phase 1 validation.

- [x] **Task 5.3: Review working tree changes before reporting completion.**  
  File path: `C:\development\opencode` and external config files listed above  
  Command:
  ```powershell
  git -C "C:\development\opencode" status --short; git -C "C:\development\conductor-reporter" status --short
  ```
  Expected output: changed Conductor files in `C:\development\opencode` only if the build agent updated track checkboxes/metadata, and `.gitignore` changed in `conductor-reporter`. External `C:\Users\DaveWitkin\.config\opencode` files may not appear because that folder is not a Git repo.  
  Error recovery: if unexpected application source files appear, stop and ask user before proceeding.

- [x] **Task 5.4: Update this Conductor `plan.md` checkboxes and `metadata.json` phase/status.**  
  File paths: `C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\plan.md`, `C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\metadata.json`  
  Command:
  ```powershell
  Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\metadata.json"; Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\plan.md"
  ```
  Expected output: two `True` lines.  
  Error recovery: if metadata is missing, recreate it using the template in this track's initial metadata and set status to `validation-complete` only after all prior tasks pass.

Phase-level exit criteria: validation passes, no unexpected source-code changes exist, and Conductor artifacts reflect actual execution status.

## Execution Readiness Checklist

- [x] Atomic tasks: each checkbox contains one clear action.
- [x] Exact file paths: every task names precise full Windows paths.
- [x] Explicit commands: every task includes verbatim PowerShell or Git commands.
- [x] Clear ordering: phases and tasks are ordered by prerequisites.
- [x] Verification per step: every task includes deterministic expected output.
- [x] No assumed context: all audited paths and required content are embedded here.
- [x] Concrete examples: index schema and complete initial content are provided.
- [x] Error recovery: each task includes fallback instructions.

## Top 3 Implementation Risks + Mitigations

1. **Risk:** accidental secret values copied into `secrets-index.jsonc`.  
   **Mitigation:** only use key names from the handover; run the no-secret-pattern checks in Tasks 1.4 and 5.2.

2. **Risk:** AGENTS.md insertion duplicates or lands in the wrong section.  
   **Mitigation:** Task 2.2 inserts only if the heading is absent; Task 2.3 requires exactly one heading.

3. **Risk:** Firebase or repo-specific env files are modified beyond documentation.  
   **Mitigation:** this plan has no task that edits `.env` values or Firebase env files; any such change is out of scope and must be rejected.

## First Task the Build Agent Should Execute Immediately

Run Task 0.1 exactly:

```powershell
Test-Path -LiteralPath "C:\Users\DaveWitkin\.config\opencode"
```

