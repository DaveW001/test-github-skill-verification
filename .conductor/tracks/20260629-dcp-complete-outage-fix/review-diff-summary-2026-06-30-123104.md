# Review Diff Summary - 20260629-dcp-complete-outage-fix

- **Reviewer:** `opencode-go/minimax-m3` (Stage 2)
- **Timestamp:** 2026-06-30-123104
- **Plan under review:** `C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\plan.md`
- **Net effect:** 2 in-place edits applied, 0 structural changes (21 tasks, 6 phases, 5 ACs all preserved).

## Edits Applied to plan.md (High Confidence)

### Edit 1 - Task 2.1 April-backup fallback path correction

**Why it was wrong:** the original error-recovery snippet pointed at the plugin directory, not the tokenizer. The April backup at `C:\Users\DaveWitkin\.cache\opencode-cache-backup-20260428-094635\node_modules\@tarquinen\opencode-dcp` is a directory, not a tokenizer. Direct filesystem inspection during this review (PowerShell `Test-Path` and `Get-Content` against the real April-backup directory) confirmed the tokenizer is at `C:\Users\DaveWitkin\.cache\opencode-cache-backup-20260428-094635\node_modules\@anthropic-ai\tokenizer` (top-level node_modules), with `version: 0.0.4` and the same `dist/cjs/index.js` main that the DCP plugin imports. If the offline fallback had been triggered, the original path would have silently failed (or copied a wrong tree), defeating the entire fallback.

**Before:**
```powershell
# Error recovery: as a last resort (offline), copy `@anthropic-ai/tokenizer` from the April backup if present:
$alt = "C:\Users\DaveWitkin\.cache\opencode-cache-backup-20260428-094635\node_modules\@tarquinen\opencode-dcp"; Test-Path $alt
# if True, inspect whether it contains a usable tokenizer and copy it into $dir\node_modules\@anthropic-ai\tokenizer.
```

**After:**
```powershell
# Error recovery: as a last resort (offline), copy `@anthropic-ai/tokenizer` from the April backup if present:
$alt = "C:\Users\DaveWitkin\.cache\opencode-cache-backup-20260428-094635\node_modules\@anthropic-ai\tokenizer"; Test-Path $alt
# if True, `Copy-Item -LiteralPath $alt -Destination "$dir\node_modules\@anthropic-ai\tokenizer" -Recurse -Force` and re-run the Test-Path check.
```

**Verification (PowerShell dry-run against the real April backup):**
- `Test-Path ...\node_modules\@anthropic-ai\tokenizer` -> `True`
- `Test-Path ...\node_modules\@tarquinen\opencode-dcp\node_modules\@anthropic-ai\tokenizer` -> `False` (would have been the wrong path)
- `Get-Content ...\package.json -Raw` -> `{"name":"@anthropic-ai/tokenizer","version":"0.0.4",...,"main":"dist/cjs/index.js"}` (matches DCP's import)

### Edit 2 - Task 3.1 opencode launcher path correction

**Why it was wrong:** the original primary command was `& opencode run ...`. `Get-Command opencode` on this machine returns only `C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.ps1` (an ExternalScript) - `opencode` is NOT on `PATH` directly. Running `& opencode run` from a fresh PowerShell would error with "the term 'opencode' is not recognized" and Phase 3 would fail before any verification could occur. The error-recovery text mentioned the full path but only as a fallback. The primary command needed the full path.

**Before:**
```powershell
$logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
& opencode run --title 'dcp-verify-0629' --agent general 'Reply with the single word PING and stop. Do not call any tools.' 2>&1 | Out-Null
"run_exit=$LASTEXITCODE"
...
# Error recovery: if `opencode run` is not on PATH, use `& "C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.ps1" run ...`.
```

**After:**
```powershell
$logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
& "C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.ps1" run --title 'dcp-verify-0629' --agent general 'Reply with the single word PING and stop. Do not call any tools.' 2>&1 | Out-Null
"run_exit=$LASTEXITCODE"
...
# Error recovery: if `opencode.ps1` is not at that path, locate with `(Get-Command opencode -ErrorAction SilentlyContinue).Source` and use the full path returned.
```

**Verification (PowerShell dry-run):**
- `Get-Command opencode` -> `Name=opencode.ps1 Source=C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.ps1`
- `& "C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.ps1" run --help` -> lists `--title`, `--agent`, `--format` etc.
- `opencode.jsonc` -> `agent.general` is defined with `model: zai-coding-plan/glm-5.2` (so `--agent general` is valid).

## Edits NOT Applied (Surfaced to User)

These are not applied because they are cosmetic / convention choices. None block execution.

1. **Task 0.1 / 3.2 pattern strictness.** The pattern `service=plugin path=@tarquinen/opencode-dcp` matches both INFO `loading plugin` and ERROR `failed to load plugin` lines. The plan's failure-check is separate, so this is correct. A stricter version (e.g. matching `loaded` or `service=dcp`) would be more rigorous but is not emitted by opencode 1.15.10 in practice.

2. **Task 0.2 missing-dir abort.** The plan does not explicitly abort if `$dir` itself is missing (only if backup is empty). Phase 0.4's byte-count check catches the same root cause implicitly. Adding a one-line "if `Test-Path $dir` is False, STOP - DCP not installed" would be a small clarity win.

## Structural Change Audit

| Item | Before | After | Delta |
|------|--------|-------|-------|
| Acceptance criteria count | 5 | 5 | 0 |
| Phase count | 6 (0,1,2,3,4,Final) | 6 | 0 |
| Checkbox task count | 21 | 21 | 0 |
| Task renames | 0 | 0 | 0 |
| Phase renames | 0 | 0 | 0 |
| New tasks introduced | 0 | 0 | 0 |
| Tasks removed | 0 | 0 | 0 |

**No structural changes.** The two in-place edits are within-task wording corrections, not plan restructuring. The Stage 3 threshold-policy triggers (AC count >=2, phase count change, task count >=20%) are NOT hit.

## Readiness Score

**92%** (post-edit). Breakdown:
- 19 of 21 tasks rated Ready with no caveats.
- 2 of 21 tasks originally rated Needs work, both fixed in-place, now Ready.
- 0 tasks rated Blocking.
- Deductions: the two within-task defects cost 3 percentage points each (-6 total) - these are now reversed, but the score reflects the original state and the verifier diligence required to catch them. A 2-point deduction is retained for "a less capable build agent running the pre-edit plan would have hit silent failures" - the executor still needs to know what to look for, which the report now documents.

## Diversity Gate (per threshold-policy.md)

- Stage 1 creator: `openai/gpt-5.5` (gpt-5.5).
- Stage 2 reviewer: `opencode-go/minimax-m3` (MiniMax M3).
- **PASS** - distinct model families.

## Files Touched

| File | Action |
|------|--------|
| `C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\plan.md` | 2 in-place edits (Task 2.1 fallback path; Task 3.1 launcher path) |
| `C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\review-report-2026-06-30-123104.md` | created |
| `C:\development\opencode\.conductor\tracks\20260629-dcp-complete-outage-fix\review-diff-summary-2026-06-30-123104.md` | created (this file) |

No other track files were modified. The `spec.md`, `metadata.json`, `execution-log.md`, and the unrelated `20260628-opencode-session-message-seq-fatal` track artifacts are untouched (Task 5.5's cross-link is an executor action, not a reviewer action).
