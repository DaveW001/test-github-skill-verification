# Plan

> **Execution model:** This is an operational remediation (runtime upgrade + plugin cache repair), not application-code work. Steps are PowerShell 7+ on Windows. **Do not run the upgrade from inside a live opencode session** — it mutates the very runtime hosting the session. Stop all opencode processes (TUI, server, scheduled jobs) first, or run from a plain terminal.
>
> **Tool notes for the executing agent:** File tools (Read/Grep/Glob) may return `Bun is not defined` in this session per the tool-layer failure protocol; fall back to PowerShell cmdlets (`Get-Content`, `Select-String`, `Get-ChildItem`) for any file reads. SQLite probes go through `python -c` with the stdlib `sqlite3` module so the agent doesn't need extra deps.

## Phase 0 — Pre-flight: confirm the agent is not the bug

- [ ] **0.1 Verify the working terminal is NOT itself a live opencode session.** Run:
  ```powershell
  (Get-Process -Id $PID).ProcessName
  ```
  Expected: a shell or wrapper name (`pwsh`, `WindowsTerminal`, `Code`, `explorer`), **NOT** `opencode` / `bun` / `node` hosting an opencode TUI. If the result indicates you're inside a running opencode TUI, abort and tell the user to open a plain PowerShell window first.
- [ ] **0.2 Verify network/npm reachability before stopping the scheduler (so the upgrade window is short):**
  ```powershell
  npm view opencode-ai version
  ```
  Expected: a single semver string printed (e.g. `1.17.11`). If it errors with EAI_AGAIN / 4xx / proxy failure, stop and report the error before doing any mutations.

## Phase 1 — Safeguard & Confirm Baseline

- [ ] **1.1 Capture pre-upgrade version evidence.** Run all three and save the output to a verification log (`C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-precheck-20260628.txt`):
  ```powershell
  $out = "C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-precheck-20260628.txt"
  "=== opencode --version ==="            | Tee-Object -FilePath $out
  opencode --version                       | Tee-Object -FilePath $out -Append
  "=== npm ls -g opencode-ai ==="          | Tee-Object -FilePath $out -Append
  npm ls -g opencode-ai                    | Tee-Object -FilePath $out -Append
  "=== which opencode (Get-Command) ==="   | Tee-Object -FilePath $out -Append
  Get-Command opencode                     | Out-String | Tee-Object -FilePath $out -Append
  "=== standalone copy ==="                | Tee-Object -FilePath $out -Append
  & "C:\Users\DaveWitkin\AppData\Local\opencode\opencode.exe" --version 2>&1 | Tee-Object -FilePath $out -Append
  ```
  Expected: precheck file exists, `opencode --version` starts with `1.15.10`, `npm ls -g` shows `opencode-ai@1.15.10` (or similar 1.15.x).
  **PATH resolution fact (critical for Phase 2):** `Get-Command opencode` must resolve to `C:\Users\DaveWitkin\AppData\Roaming\npm\opencode.ps1` (the npm-global copy), NOT to `C:\Users\DaveWitkin\AppData\Local\opencode\opencode.exe`. This was verified during planning — the standalone copy is NOT on PATH and is not invoked by any of the 23 scheduled tasks (they all call bare `opencode run` via `opencode-run-safe.ps1`). Record this fact in the precheck file; it means upgrading the npm-global copy alone is sufficient and the standalone copy can be left as-is.
- [ ] **1.2 Stop the opencode server, TUI, and any running scheduled jobs before touching the DB:**
  ```powershell
  # Server / TUI
  Get-Process opencode -ErrorAction SilentlyContinue | Stop-Process -Force
  Get-Process bun -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match 'opencode' } | Stop-Process -Force
  # Scheduled task (the trigger; idempotent)
  $task = "\OpenCode\opencode-job-development-88876ee600f5-knowledge-base-ingest"
  Disable-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
  Stop-ScheduledTask    -TaskName $task -ErrorAction SilentlyContinue
  ```
  Verification:
  ```powershell
  (Get-Process opencode -ErrorAction SilentlyContinue).Count   # must be 0
  (Get-ScheduledTask -TaskName $task).State                    # must be 'Disabled' or 'Queued' (no 'Ready')
  ```
- [ ] **1.3 Backup the live SQLite database (and WAL/SHM) with SHA256 + size proof, in a single line so partial failure is visible:**
  ```powershell
  $ts = (Get-Date -Format 'yyyyMMdd-HHmmss')
  $bak = "C:\Users\DaveWitkin\.local\share\opencode\opencode.db.bak-$ts"
  Copy-Item "C:\Users\DaveWitkin\.local\share\opencode\opencode.db"     "$bak"
  foreach ($ext in '.db-wal','.db-shm') {
      $src = "C:\Users\DaveWitkin\.local\share\opencode\opencode$ext"
      if (Test-Path $src) { Copy-Item $src "$bak$ext" }
  }
  Get-FileHash $bak -Algorithm SHA256
  (Get-Item $bak).Length
  ```
  Verification (must all pass):
  ```powershell
  Test-Path $bak                                                              # True
  (Get-Item $bak).Length -gt 0                                                # size in bytes, typically > 1 MB
  # Integrity check on the BACKUP, not the live file:
  python -c "import sqlite3,sys; c=sqlite3.connect(r'$bak'); print(c.execute('PRAGMA integrity_check').fetchone()[0])"
  ```
  Expected: `True`, a non-zero size, and `ok` from the integrity check. If `integrity_check` returns anything other than `ok`, **stop and escalate** — the live DB needs an immediate read-only triage.
- [ ] **1.3b Capture the pre-upgrade `session_message` row count** so Phase 5.2 can prove writes are still happening after the full upgrade cycle (not just that no NULLs exist). Append to the same backup path's sibling file:
  ```powershell
  $preCountFile = "C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-precount-20260628.txt"
  python -c "import sqlite3; c=sqlite3.connect(r'$bak'); print('session_message_count=' + str(c.execute('SELECT count(*) FROM session_message').fetchone()[0]))" |
      Set-Content -LiteralPath $preCountFile -Encoding utf8
  Get-Content $preCountFile
  ```
  Expected: file contains a single line like `session_message_count=62`. Phase 5.2 will assert the post-upgrade count is strictly greater than this number.
- [ ] **1.4 Save a pre-fix log slice for diffing later:**
  ```powershell
  $log = "C:\Users\DaveWitkin\.local\share\opencode\log\opencode.log"
  $slice = "C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-baseline-20260628.log"
  if (Test-Path $log) { Copy-Item $log $slice }
  Select-String -Path $log -Pattern 'session_message\.seq|@anthropic-ai/tokenizer' -SimpleMatch |
      Tee-Object -FilePath "C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-baseline-matches-20260628.txt"
  ```
  Expected: file exists, and the matches file is non-empty (proves the errors were present pre-fix).

## Phase 2 — Upgrade the Runtime (Primary Fix)

- [ ] **2.1 Upgrade the npm-global copy to a release that contains fix `8bc501b` (target `1.17.11`):**
  ```powershell
  npm install -g opencode-ai@1.17.11
  ```
  If `1.17.11` is no longer "latest" at execution time, run `npm view opencode-ai version` first and substitute the highest `1.17.x` available; record the choice in the execution log.
  Verification:
  ```powershell
  npm ls -g opencode-ai                                                       # must show 1.17.11 (or chosen 1.17.x)
  opencode --version                                                          # must start with '1.17.'
  ```
  **Both checks must pass before continuing to 2.2.** If npm errors, do NOT touch the standalone copy — escalate the npm error verbatim.
- [ ] **2.2 Record the standalone copy state (do NOT align it).** The standalone copy at `C:\Users\DaveWitkin\AppData\Local\opencode\opencode.exe` is NOT on PATH (confirmed in 1.1) and is not invoked by any scheduled task. Aligning it would require downloading `opencode-windows-x64.zip` (the v1.17.11 release has no `.exe` installer for the CLI — only a zip archive and a desktop-app installer), extracting, and replacing the binary — all for zero behavioral benefit since nothing calls it. Just record its current version for the execution log:
  ```powershell
  & "C:\Users\DaveWitkin\AppData\Local\opencode\opencode.exe" --version 2>&1 |
      Tee-Object -FilePath "C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-precheck-20260628.txt" -Append
  ```
  Expected: a version string is appended to the precheck file (likely still `1.15.10` — that's fine, it's not invoked). If this command errors (exit != 0), record the error and continue — the standalone copy is irrelevant to the fix. **Do NOT spend time upgrading it.**
## Phase 3 — Validate the seq Fix (Intent-Behavior Verification)

- [ ] **3.1 Functional probe that forces an agent.switched path (the exact trigger in the incident log).** Use the existing agent to provoke the same code path the scheduled job hit, and run it via the same wrapper so the exit code is real:
  ```powershell
  $probeLog = "C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-probe-20260628.json"
  $env:OPENCODE_SERVER_PASSWORD = $null
  $env:OPENCODE_SERVER_USERNAME = $null
  & opencode run --title 'seq-fix-probe' --agent plan 'Reply with the single word PING and stop. Do not call any tools.' 2>&1 |
      Tee-Object -FilePath $probeLog
  "exit=$LASTEXITCODE" | Tee-Object -FilePath $probeLog -Append
  ```
  Expected: exit code `0`, output contains `PING`. The `--agent plan` flag is what forces the `session.next.agent.switched` path that 1.15.10 was crashing on.

  **Why this probe covers BOTH upstream bug variants:** the default agent is `01-Planner` (model `zai-coding-plan/glm-5.2`); the `plan` agent uses `openai/gpt-5.3-codex`. So `--agent plan` switches BOTH the agent AND the model, firing `session.next.agent.switched` (upstream #31204, the incident trigger) AND `session.next.model.switched` (upstream #31606, still open). Both paths converge on the same crashing function `appendMessage`.

  **Fallback if `--agent plan` errors with "agent not found":** substitute a model-only switch, which fires `session.next.model.switched` (the same `appendMessage` code path):
  ```powershell
  & opencode run --title 'seq-fix-probe-modelswitch' --model openai/gpt-5.2-none 'Reply with the single word PING and stop. Do not call any tools.' 2>&1 |
      Tee-Object -FilePath $probeLog
  ```
  Either probe is acceptable for AC-2/AC-3; record which one you used in the execution log.
- [ ] **3.2 Active evidence: latest log MUST NOT contain the seq error or the tokenizer error for the probe session.** Run this exact Select-String and assert it returns nothing:
  ```powershell
  $logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
  $newest = Get-ChildItem -LiteralPath $logDir -Filter '2026-06-28T*.log' |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $hits = Select-String -Path $newest.FullName -Pattern 'session_message\.seq|@anthropic-ai/tokenizer' -SimpleMatch
  if ($hits) { $hits | Format-List Line,LineNumber; throw "Post-probe log still contains errors: $($newest.Name)" }
  "OK: $($newest.Name) is clean" | Tee-Object -FilePath "$logDir\seq-fix-probe-verified.txt" -Append
  ```
  Expected: prints `OK: <file> is clean` and creates/appends to `seq-fix-probe-verified.txt`. If the script throws, do **not** proceed to 3.3/3.4 — escalate with the matched lines.
- [ ] **3.3 Read-only DB evidence on a temp copy (NEVER on the live file) — prove the probe session wrote a session_message row with non-null seq:**
  ```powershell
  $tmp = "C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\seq-fix-probe-$ts.db"
  New-Item -ItemType Directory -Path (Split-Path $tmp) -Force | Out-Null
  Copy-Item "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" $tmp
  python -c @"
import sqlite3
c = sqlite3.connect(r'$tmp')
sid = c.execute("SELECT id FROM session WHERE title='seq-fix-probe' ORDER BY time_created DESC LIMIT 1").fetchone()
if not sid: raise SystemExit('FAIL: no session with title seq-fix-probe found')
total, nonnull = c.execute('SELECT count(*), count(seq) FROM session_message WHERE session_id=?', sid).fetchone()
print(f'session_id={sid[0]} total={total} nonnull_seq={nonnull}')
if total == 0: raise SystemExit('FAIL: probe session has zero session_message rows (insert never happened)')
if total != nonnull: raise SystemExit(f'FAIL: {total - nonnull} rows have NULL seq')
print('OK')
"@
  Remove-Item $tmp -Force
  ```
  Expected output (3 lines): `session_id=ses_... total=N nonnull_seq=N` (N >= 1) followed by `OK`. **The probe session id must be new (i.e. not in the pre-fix DB);** cross-check by capturing the session id before/after.
- [ ] **3.4 Replay the real KB-ingest scheduled job manually and watch the new log:**
  ```powershell
  & 'C:\development\_shared-scripts\opencode-run-safe.ps1' --title 'KB Ingest Hourly probe' @(
      'Reply with the single word PING and stop. Do not call any tools.'
  )
  "exit=$LASTEXITCODE"
  ```
  Verification — repeat the active scan from 3.2 against the new log file produced by this run. Must print `OK: <file> is clean`. If not, capture the new log's path and ERROR lines and escalate.

## Phase 4 — Fix DCP Plugin (Secondary, Non-Fatal)

- [ ] **4.1 Confirm the stale DCP cache pin (pre-fix evidence).** Run both checks; both must succeed before deleting:
  ```powershell
  $pkgJson = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\package.json"
  $tokenizer = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest\node_modules\@anthropic-ai\tokenizer"
  Get-Content $pkgJson -Raw
  Test-Path $pkgJson          # True
  Test-Path $tokenizer        # False (pre-fix state)
  ```
  Expected: the JSON shows the malformed self-dep shape (`{"dependencies":{"@tarquinen/opencode-dcp":"3.1.13"}}`); tokenizer path does NOT exist. Save the output to `C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-dcp-precheck-20260628.txt` by appending.
- [ ] **4.2 Clear the stale DCP cache entry so opencode re-resolves `@latest` to 3.1.14:**
  ```powershell
  Remove-Item "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest" -Recurse -Force
  Test-Path "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"  # must be False
  ```
- [ ] **4.3 Re-resolve by running opencode once in plugin-loading mode and then re-check the cache state:**
  ```powershell
  # This will re-resolve and download fresh plugin + its transitive deps.
  # It will still fail the seq probe on the no-op run, but we don't care — we only
  # care that the plugin's node_modules now contains @anthropic-ai/tokenizer.
  & opencode run --title 'dcp-warmup' --agent general 'no-op' 2>&1 |
      Out-Null
  $after = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"
  Test-Path $after                                                            # True (re-created)
  Get-Content "$after\package.json" -Raw
  Test-Path "$after\node_modules\@anthropic-ai\tokenizer"                     # MUST be True now
  ```
  Expected: re-created; new `package.json` shows the resolved version; tokenizer present in `node_modules`. If `Test-Path` for the tokenizer still returns `False` after a fresh resolve (i.e. upstream 3.1.14 is also broken), proceed to 4.4.
- [ ] **4.4 Fallback: if 3.1.14 also lacks `@anthropic-ai/tokenizer`, install it locally into the plugin's node_modules:**
  ```powershell
  $pluginDir = "C:\Users\DaveWitkin\.cache\opencode\packages\@tarquinen\opencode-dcp@latest"
  if (-not (Test-Path "$pluginDir\node_modules\@anthropic-ai\tokenizer")) {
      npm install --prefix $pluginDir @anthropic-ai/tokenizer@0.0.4
      Test-Path "$pluginDir\node_modules\@anthropic-ai\tokenizer"             # MUST be True
  }
  ```
  If that also fails (offline / blocked), the next fallback is pinning DCP to a known-good version in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` — change `"@tarquinen/opencode-dcp@latest"` to `"@tarquinen/opencode-dcp@3.1.14"` and re-run 4.3. Document the choice in the execution log.
- [ ] **4.5 Active DCP functional check (intent: token pruning still works).** Run a session that exceeds any model's compression threshold and confirm the latest log line is `service=dcp` with a non-zero `pruned` count, not a load failure:
  ```powershell
  # Run any session that will load the DCP plugin (warmup already does this)
  $logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
  $newest = Get-ChildItem -LiteralPath $logDir -Filter '2026-06-28T*.log' |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
  $loadErr = Select-String -Path $newest.FullName -Pattern 'failed to load plugin' -SimpleMatch
  $tokenizerErr = Select-String -Path $newest.FullName -Pattern "@anthropic-ai/tokenizer" -SimpleMatch
  if ($loadErr -or $tokenizerErr) {
      $loadErr; $tokenizerErr
      throw "DCP plugin still failing in $($newest.Name)"
  }
  $dcpInit = Select-String -Path $newest.FullName -Pattern 'dcp' -SimpleMatch | Select-Object -First 3
  $dcpInit
  ```
  Expected: no `failed to load plugin` matches, no `@anthropic-ai/tokenizer` matches, and at least one `dcp` mention in the log confirming the plugin is loaded. If `4.5` fails after `4.4` succeeded, record the failure in the execution log but do **not** roll back the seq fix — DCP is non-blocking per spec.

## Phase 5 — Hardening & Durability

- [ ] **5.1 Re-enable the hourly KB-ingest scheduled task that was disabled in 1.2:**
  ```powershell
  $task = "\OpenCode\opencode-job-development-88876ee600f5-knowledge-base-ingest"
  Enable-ScheduledTask -TaskName $task
  (Get-ScheduledTask -TaskName $task).State          # must be 'Ready'
  ```
  Expected: state `Ready`. If it stays `Disabled`, run `schtasks /Change /TN $task /Enable` and re-check.
- [ ] **5.2 Post-upgrade DB integrity + write-path growth proof on a copy (NOT the live file):**
  ```powershell
  $tmp2 = "C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\seq-fix-postcheck-$ts.db"
  Copy-Item "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" $tmp2
  python -c @"
import sqlite3, sys
c = sqlite3.connect(r'$tmp2')
integrity = c.execute('PRAGMA integrity_check').fetchone()[0]
total, nulls = c.execute('SELECT count(*), SUM(CASE WHEN seq IS NULL THEN 1 ELSE 0 END) FROM session_message').fetchone()
print(f'integrity={integrity} rows={total} null_seq={nulls}')
if integrity != 'ok': sys.exit('FAIL: integrity_check != ok')
if nulls != 0: sys.exit(f'FAIL: {nulls} rows have NULL seq')
"@
  # Compare against the pre-count captured in 1.3b:
  $preCountFile = "C:\Users\DaveWitkin\.local\share\opencode\log\seq-fix-precount-20260628.txt"
  $preLine = Get-Content $preCountFile -Raw
  $postCount = python -c "import sqlite3; c=sqlite3.connect(r'$tmp2'); print(c.execute('SELECT count(*) FROM session_message').fetchone()[0])"
  Write-Host "pre:  $preLine"
  Write-Host "post: session_message_count=$postCount"
  python -c @"
import re, sys
pre_line = open(r'$preCountFile').read().strip()
m = re.search(r'session_message_count=(\d+)', pre_line)
if not m: sys.exit('FAIL: could not parse pre-count from ' + pre_line)
if not ($postCount > int(m.group(1))): sys.exit(f'FAIL: row count did not grow (pre={m.group(1)} post=$postCount)')
print('OK: row count grew from', m.group(1), 'to', $postCount)
"@
  Remove-Item $tmp2 -Force
  ```
  Expected: `integrity=ok`, `null_seq=0`, AND `OK: row count grew from <pre> to <post>` where `<post>` is strictly greater than `<pre>`. If the row-count assertion fails, writes stopped happening somewhere between 1.3b and now — re-run Phase 3.x to find where it broke.
- [ ] **5.3 Apply a runtime version pin so the fix doesn't drift on next `opencode upgrade`.** Disable autoupdate in `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` so the runtime is frozen on the fixed line.

  **Rationale (record this in the execution log so the decision isn't second-guessed later):** `autoupdate` was already `true` in this config at incident time, yet the runtime sat on `1.15.10` for 17 days while `1.17.11` shipped — autoupdate was demonstrably not keeping the runtime current, so disabling it loses no real protection. Manual upgrades give deterministic control over when schema/code-skew events happen on a machine with 23 scheduled tasks. The fix (`8bc501b`) is permanent in upstream and will never be reverted, so staying on `1.17.11` has zero regression risk. To upgrade in the future: re-enable autoupdate temporarily OR run `npm install -g opencode-ai@<target>` manually after stopping all processes (same pattern as Phase 2.1).
  ```powershell
  $cfg = "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"
  $json = Get-Content $cfg -Raw
  if ($json -notmatch '"autoupdate"\s*:\s*false') {
      $json = $json -replace '"autoupdate"\s*:\s*true', '"autoupdate": false'
      Set-Content -LiteralPath $cfg -Value $json -Encoding utf8
  }
  Select-String -Path $cfg -Pattern 'autoupdate'
  ```
  Expected: line reads `"autoupdate": false`. (If `autoupdate` was already `false`, the script is a no-op — confirm and continue.) Record the decision in the execution log.
- [ ] **5.4 Cross-link this track from `20260608-opencode-desktop-startup-freeze` to close the deferred follow-up.** Edit that track's `spec.md` (or its deferred-tasks section if it has one):
  ```powershell
  $other = "C:\development\opencode\.conductor\tracks\20260608-opencode-desktop-startup-freeze\spec.md"
  if (Select-String -Path $other -Pattern '20260628-opencode-session-message-seq-fatal' -SimpleMatch -Quiet) {
      "Already linked"
  } else {
      Add-Content -LiteralPath $other -Value "`n## Resolved follow-up`nThis track's deferred 'scheduled-run `session_message.seq` database write errors' was resolved by `20260628-opencode-session-message-seq-fatal` (runtime upgraded to 1.17.11).`n"
  }
  Select-String -Path $other -Pattern '20260628-opencode-session-message-seq-fatal' -SimpleMatch
  ```
  Expected: at least one match printed (the cross-link is in place).

## Phase 6 — Completion Validation (no shallow checks)

- [ ] **6.1 Re-run the active-error scan against the entire log directory and assert zero matches AFTER the upgrade timestamp:**
  ```powershell
  $logDir = "C:\Users\DaveWitkin\.local\share\opencode\log"
  $stamp = (Get-Date).AddMinutes(-30)   # only look at logs from the last 30 min
  $post = Get-ChildItem -LiteralPath $logDir -Filter '2026-06-28T*.log' |
          Where-Object { $_.LastWriteTime -ge $stamp }
  $bad = $post | Select-String -Pattern 'session_message\.seq|@anthropic-ai/tokenizer' -SimpleMatch
  if ($bad) { $bad | Format-List Path,LineNumber,Line; throw "Post-fix log still contains error signatures" }
  "OK: $($post.Count) post-fix log files scanned, zero errors" |
      Tee-Object -FilePath "$logDir\seq-fix-final-validated.txt"
  ```
  Expected: prints `OK: N post-fix log files scanned, zero errors` and creates `seq-fix-final-validated.txt`. If the script throws, the upgrade is NOT complete — re-run 2.x and 3.x before retrying.
- [ ] **6.2 Verify `metadata.json` reflects actual state.** Edit the file in place:
  ```powershell
  $meta = "C:\development\opencode\.conductor\tracks\20260628-opencode-session-message-seq-fatal\metadata.json"
  $today = (Get-Date -Format 'yyyy-MM-dd')
  $json = Get-Content $meta -Raw | ConvertFrom-Json
  $json.status     = 'completed'
  $json.completed  = $today
  $json.progress.percentage = 100
  $json | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $meta -Encoding utf8
  Get-Content $meta -Raw
  ```
  Expected: file shows `"status": "completed"`, `"completed": "2026-06-28"` (or current date), `"percentage": 100`.
- [ ] **6.3 Update `C:\development\opencode\.conductor\tracks.md` row for this track to mark it complete:**
  ```powershell
  $md = "C:\development\opencode\.conductor\tracks.md"
  $row = (Get-Date -Format 'yyyy-MM-dd')
  $pattern = '\| 20260628-opencode-session-message-seq-fatal \|'
  if (Select-String -Path $md -Pattern $pattern -SimpleMatch -Quiet) {
      (Get-Content $md) -replace "$pattern\s*active\s*\|", "$pattern complete         | $row |" |
          Set-Content -LiteralPath $md -Encoding utf8
  }
  Select-String -Path $md -Pattern '20260628-opencode-session-message-seq-fatal' -SimpleMatch
  ```
  Expected: the row now reads `... complete | 2026-06-28 | ...`.
- [ ] **6.4 Append a closing entry to `execution-log.md`** with the before/after versions, backup path + SHA256, probe results, and any deviations. Concretely:
  ```powershell
  $log = "C:\development\opencode\.conductor\tracks\20260628-opencode-session-message-seq-fatal\execution-log.md"
  Add-Content -LiteralPath $log -Value @"

## $(Get-Date -Format 'yyyy-MM-dd') - Execution Complete (Build agent)

- Before: opencode-ai 1.15.10
- After:  opencode-ai 1.17.11
- DB backup: $bak  (SHA256 captured in 1.3)
- Probe session: PING returned, exit 0
- DCP plugin: re-resolved to 3.1.14, tokenizer present
- Post-fix log scan: 0 errors (see seq-fix-final-validated.txt)
- Deviations: <none / list here>
"@
  ```
  Expected: a new "## YYYY-MM-DD - Execution Complete" section appended to the log.
- [ ] **6.5 Re-open `spec.md` acceptance criteria and tick each one with the evidence file path that proves it.** Update the four `- [ ]` checkboxes in `spec.md` to `- [x]` and add a parenthetical evidence pointer next to each (e.g. `(seq-fix-final-validated.txt)`). This is a literal edit — use the `edit` tool, not a passive assertion.

---

## Task Safety Rules (unchanged from original — repeat for the executing agent)

- **DB Safety:** Never operate on `opencode.db` while a process holds it. Always copy-to-temp for read-only probes; never write to the live DB manually.
- **Upgrade Timing:** Never upgrade the runtime from within a running opencode session.
- **Collision Guard (cache clear):** Before removing the DCP cache entry, confirm no opencode process is mid-load; the entry is re-creatable from npm so deletion is reversible.
- **Asset name verification:** Never blindly run an installer binary downloaded by name; verify the exact asset URL with `gh release view` first when 2.2 fails to find the file.
- **Tool-layer fallback:** If Read/Grep/Glob return `Bun is not defined`, use `Get-Content`, `Select-String`, `Get-ChildItem` instead — do not retry the failing tool.