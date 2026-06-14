# Plan

## Phase 0: Setup & Preconditions
Objective: preserve current evidence and make all later recovery steps reversible.

- [x] 0.1 Confirm no OpenCode Desktop or sidecar processes are running before state changes.
  Command: `Get-Process | Where-Object { $_.ProcessName -match 'OpenCode|opencode' } | Select-Object Id,ProcessName,Path`
  Verification: output is empty, or the operator intentionally closes only OpenCode-related processes.
  Recovery: if unrelated processes appear, stop and ask Dave before terminating anything.

- [x] 0.2 Create a timestamped backup folder for Desktop state and OpenCode DB.
  Command: `$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'; $backup = "C:\Users\DaveWitkin\Downloads\opencode-recovery-$stamp"; New-Item -ItemType Directory -Path $backup -Force; $backup`
  Verification: command prints an existing folder path under `C:\Users\DaveWitkin\Downloads`.
  Recovery: if Downloads is unavailable, create the backup under `C:\development\opencode\.conductor\tracks\20260608-opencode-desktop-startup-freeze\backups`.

- [x] 0.3 Back up Desktop global state, workspace state files, and the OpenCode database.
  Command: `Copy-Item -LiteralPath 'C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\opencode.global.dat' -Destination $backup; Copy-Item -LiteralPath 'C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\opencode.workspace.*.dat' -Destination $backup -ErrorAction SilentlyContinue; Copy-Item -LiteralPath 'C:\Users\DaveWitkin\.local\share\opencode\opencode.db' -Destination $backup`
  Verification: `Get-ChildItem -LiteralPath $backup | Select-Object Name,Length` shows `opencode.global.dat` and `opencode.db`.
  Recovery: if `opencode.db` is locked, ensure OpenCode processes are stopped and rerun only this task.

- [x] 0.4 Record current database integrity and key counts before mutation.
  Command: `@' <python sqlite read-only script from this plan's Appendix A> '@ | python -`
  Verification: output includes `integrity ok`, table counts, and top large session IDs.
  Recovery: if Python is unavailable, install nothing; use this as a blocker and proceed only with Desktop state backup tests.

Phase exit criteria: current state is backed up and baseline evidence is recorded.

## Phase 0.5: Upstream GitHub Research
Objective: check the OpenCode upstream repository for known Desktop renderer freezes, oversized session/message timeline failures, SQLite migration issues, and documented workarounds before applying heavier local recovery.

- [x] 0.5 Identify the canonical upstream GitHub repository and current Desktop release context.
  Command: `gh repo view opencode-ai/opencode --json nameWithOwner,url,defaultBranchRef,latestRelease`
  Verification: output identifies the repo, default branch, and latest release; record whether Desktop 1.16.0 or 1.16.2 is mentioned.
  Recovery: if `gh` is not authenticated or the repo name differs, run `gh auth status` and then use the GitHub skill/connector to resolve the correct OpenCode Desktop repository before continuing.

- [x] 0.6 Search upstream issues and discussions for matching renderer/session-load symptoms.
  Command: `gh issue list --repo opencode-ai/opencode --state all --search "renderer unresponsive constructMessageRows loadMessages Desktop SQLite session message timeline" --limit 30 --json number,title,state,url,createdAt,updatedAt,labels`
  Verification: record any issue URLs that mention renderer freeze, message timeline, large diffs, session history, Desktop startup, or SQLite migration/state problems.
  Recovery: if GitHub search is too narrow, run separate searches for `renderer unresponsive`, `constructMessageRows`, `loadMessages`, `session_message.seq`, `large diff`, and `opencode.db`.

- [x] 0.7 Search recent release notes and commits for fixes related to startup, Desktop state, message rendering, or SQLite schema changes.
  Command: `gh release list --repo opencode-ai/opencode --limit 10; gh search commits "repo:opencode-ai/opencode constructMessageRows OR loadMessages OR session_message.seq OR renderer unresponsive OR opencode.db" --limit 20`
  Verification: determine whether upgrading to Desktop 1.16.2 is likely to fix the freeze or whether the local state workaround is still required.
  Recovery: if `gh search commits` is unavailable in the installed GH CLI, use `gh api search/commits -f q='repo:opencode-ai/opencode constructMessageRows OR loadMessages OR session_message.seq'`.

- [x] 0.8 Update this track with upstream findings before local mutation.
  Command: create or update `C:\development\opencode\.conductor\tracks\20260608-opencode-desktop-startup-freeze\upstream-github-findings.md`.
  Verification: the findings file lists search commands run, issue/release/commit URLs reviewed, whether a known workaround exists, and the recommended next local action.
  Recovery: if no upstream matches are found, write `No upstream match found as of 2026-06-08` and proceed to Phase 1.

Phase exit criteria: upstream issue/release research is documented, and the plan either incorporates a known workaround or explicitly records that no matching upstream workaround was found.

## Phase 1: Reversible Desktop State Isolation
Objective: prove whether startup freeze is caused by reopening the last project/session.

- [x] 1.1 Temporarily move only `opencode.global.dat` out of the active Desktop state path.
  Command: `Move-Item -LiteralPath 'C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\opencode.global.dat' -Destination (Join-Path $backup 'opencode.global.dat.moved')`
  Verification: `Test-Path 'C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\opencode.global.dat'` returns `False`.
  Recovery: restore with `Copy-Item -LiteralPath (Join-Path $backup 'opencode.global.dat') -Destination 'C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\opencode.global.dat'`.

- [x] 1.2 Start OpenCode Desktop and wait 60 seconds.
  Command: start from the normal Desktop shortcut or Start Menu.
  Verification: Desktop opens without `renderer unresponsive` in `C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\logs\<new-run>\window.log`.
  Recovery: if Desktop still freezes, close it and proceed to Phase 2.

- [ ] 1.3 Open a safe small project, preferably `C:\development\opencode`, and create a new session.
  Command: use Desktop UI project open flow.
  Verification: the UI remains responsive and a new session can be created.
  Recovery: if only `C:\development\02-Kx-to-process` freezes, treat `ses_158d41ed8ffeZTg8Fa0jZwqAJG` as the primary culprit.

Phase exit criteria: Desktop either starts with reset global state or the failure persists with last-project state removed.

## Phase 2: Problem Session Isolation
Objective: avoid or archive the oversized session while preserving database history.

- [ ] 2.1 Query the problematic session and confirm its ID, title, directory, message count, and largest payloads.
  Command: `@' <python sqlite read-only script from Appendix B> '@ | python -`
  Verification: output includes `ses_158d41ed8ffeZTg8Fa0jZwqAJG`, 49 messages, 206 parts, and the 25 MB message.
  Recovery: if the session ID is absent, re-read `opencode.global.dat` and update this plan with the new last session ID.

- [ ] 2.2 Prefer UI-level recovery: with Desktop opened on a safe project, avoid opening the problematic session and create a fresh session for `C:\development\02-Kx-to-process`.
  Command: use Desktop UI; do not select `2026-06-08 Run kg-review-queue-phase2-bulk-approval`.
  Verification: `C:\development\02-Kx-to-process` opens to a new session without freezing.
  Recovery: if the project automatically reopens the bad session, continue to task 2.3.

- [x] 2.3 If UI-level recovery fails, mark only the problematic session archived in the database after backup.
  Command: `@' <python sqlite write script from Appendix C> '@ | python -`
  Verification: the script reports one updated session row and the session has non-null `time_archived`.
  Recovery: restore `opencode.db` from `$backup` if Desktop behavior worsens.

- [ ] 2.4 Restart Desktop and open `C:\development\02-Kx-to-process`.
  Command: start from normal Desktop shortcut or Start Menu.
  Verification: project opens without loading the archived oversized session, and `window.log` has no renderer unresponsive entry.
  Recovery: restore database backup and escalate to Phase 3.

Phase exit criteria: the project opens without the oversized session freezing the renderer.

## Phase 3: Scheduled Job and Write-Path Follow-Up
Objective: address the separate `session_message.seq` write error seen in scheduled OpenCode runs.

- [ ] 3.1 Identify scheduled OpenCode jobs active around 06:00-12:00 UTC on 2026-06-08.
  Command: use OpenCodeScheduler inventory first; if unavailable, run `Get-ScheduledTask | Where-Object { $_.TaskName -match 'OpenCode|KB|Skill' } | Select-Object TaskName,TaskPath,State`
  Verification: identify the jobs titled `KB Ingest Hourly` and `Skill Health Validator` or document if names differ.
  Recovery: do not disable jobs without Dave's explicit approval.

- [ ] 3.2 Reproduce or inspect the scheduled job logs for `NOT NULL constraint failed: session_message.seq`.
  Command: `rg -n "NOT NULL constraint failed: session_message.seq|SessionHttpApi.prompt|KB Ingest Hourly|Skill Health Validator" 'C:\Users\DaveWitkin\.local\share\opencode\log'`
  Verification: collect exact log paths and timestamps.
  Recovery: if `rg` is unavailable, use `Select-String -Path 'C:\Users\DaveWitkin\.local\share\opencode\log\*.log' -Pattern 'session_message.seq'`.

- [ ] 3.3 Check whether scheduled jobs still run OpenCode 1.15.10 while Desktop is 1.16.0 or pending 1.16.2.
  Command: inspect job actions through OpenCodeScheduler and compare `opencode --version` from the invoked binary path.
  Verification: record exact binary path and version for each job.
  Recovery: if versions differ, plan a scheduler runtime alignment change before further DB mutation.

- [ ] 3.4 Create a separate follow-up track if the scheduled job error persists after Desktop recovery.
  Command: create `.conductor/tracks/<new-track>/spec.md`, `plan.md`, and `metadata.json`.
  Verification: `tracks.md` and `tracks-ledger.md` point to the follow-up track.
  Recovery: if the error disappears after updating Desktop/OpenCode runtime, document closure in this track instead.

Phase exit criteria: the scheduled-job error is either fixed, disproven as current, or captured in a dedicated follow-up track.

## Final Phase: Validation & Handover
Objective: prove recovery, document rollback, and close the incident track only after evidence is clean.

- [ ] 4.1 Export a fresh debug log after successful startup.
  Command: use Desktop's `Export logs` command.
  Verification: a new `opencode-debug-*.zip` exists in `C:\Users\DaveWitkin\Downloads`.
  Recovery: if export is unavailable, copy the latest logs folder manually into this track's artifacts folder.

- [ ] 4.2 Verify no renderer freeze in the fresh run.
  Command: `rg -n "renderer unresponsive|constructMessageRows|loadMessages" 'C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop\logs\<new-run>'`
  Verification: no matches.
  Recovery: if matches remain, return to Phase 2 or Phase 3 depending on the stack.

- [ ] 4.3 Update this plan, metadata, and ledgers with final status.
  Command: edit `plan.md`, `metadata.json`, `.conductor\tracks.md`, and `.conductor\tracks-ledger.md`.
  Verification: task checkboxes and metadata counts agree.
  Recovery: if validation is partial, leave status active and list blockers.

Final exit criteria: Desktop opens reliably, the specific root cause and mitigation are recorded, and rollback artifacts are available.

## Top 3 Implementation Risks
- Database edit risk: mitigate with full `opencode.db` backup before any write.
- Product bug risk: if resetting state fixes startup but the same session always freezes, escalate with the debug bundle and offending session payload sizes.
- Scheduled job recurrence risk: pause or align scheduled jobs only after explicit approval, because they may continue writing incompatible records.

## First Task To Execute
Run Phase 0 task 0.1, then create the backup folder in task 0.2. Do not mutate Desktop state or the database until the backups in task 0.3 are verified and the upstream GitHub research in Phase 0.5 is documented.

## Appendix A: Baseline Read-Only SQLite Script

```python
import sqlite3, os
p = r'C:\Users\DaveWitkin\.local\share\opencode\opencode.db'
con = sqlite3.connect('file:' + p + '?mode=ro', uri=True)
cur = con.cursor()
print('db_size', os.path.getsize(p))
print('integrity', cur.execute('pragma integrity_check').fetchone()[0])
for (name,) in cur.execute("select name from sqlite_master where type='table' order by name"):
    print(name, cur.execute(f'select count(*) from "{name}"').fetchone()[0])
```

## Appendix B: Problem Session Read-Only SQLite Script

```python
import sqlite3
p = r'C:\Users\DaveWitkin\.local\share\opencode\opencode.db'
sid = 'ses_158d41ed8ffeZTg8Fa0jZwqAJG'
con = sqlite3.connect('file:' + p + '?mode=ro', uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()
print(dict(cur.execute('select id,title,directory,time_created,time_updated,time_archived from session where id=?', (sid,)).fetchone()))
print('messages', cur.execute('select count(*) from message where session_id=?', (sid,)).fetchone()[0])
print('parts', cur.execute('select count(*) from part where session_id=?', (sid,)).fetchone()[0])
for row in cur.execute('select id,length(data) bytes,substr(data,1,180) sample from message where session_id=? order by length(data) desc limit 5', (sid,)):
    print(dict(row))
for row in cur.execute('select id,message_id,length(data) bytes,substr(data,1,180) sample from part where session_id=? order by length(data) desc limit 5', (sid,)):
    print(dict(row))
```

## Appendix C: Archive One Problem Session SQLite Script

```python
import sqlite3, time
p = r'C:\Users\DaveWitkin\.local\share\opencode\opencode.db'
sid = 'ses_158d41ed8ffeZTg8Fa0jZwqAJG'
con = sqlite3.connect(p)
cur = con.cursor()
now = int(time.time() * 1000)
cur.execute('update session set time_archived=? where id=? and time_archived is null', (now, sid))
con.commit()
print('updated_rows', cur.rowcount)
```
