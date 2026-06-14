# Plan: System Prompt Token Audit Remediation & Final Validation

## Goal / Outcome

Repair the partially completed system-prompt-token audit, validate that prior local reductions are safe, measure the post-reduction system prompt in a fresh session, and close the conductor track with a defensible final report.

## Constraints / Non-Goals

- Do not modify OpenCode application source code.
- Do not disable MCP servers or make new prompt-reduction changes beyond the specific repairs in this plan.
- Preserve backups before any additional edit.
- Keep all YAML frontmatter valid.
- Use ASCII-safe markdown in conductor artifacts.
- Do not execute this plan from the planning session that created it; a build agent should execute it in a new session.

## Definition of Done

- Broken skill YAML is repaired and all edited skill frontmatter validates.
- Control-character corruption is removed from the specified files.
- Trigger metadata is verified or restored.
- Fresh-session token telemetry is captured and compared against the baseline.
- Final report and conductor bookkeeping files agree on the outcome and track status.

---

## Phase 0: Setup & Preconditions

**Objective:** Confirm the active track, preserve the current state, and prepare deterministic validation commands before editing any files.

1. - [x] **Task 0.1: Confirm the active track directory exists**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/`
     - Command: `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit"`
     - Verification: Expected output is `True`.
     - Error recovery: If output is `False`, stop and report `Track directory missing: C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit`.

2. - [x] **Task 0.2: Create a remediation backup directory**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/remediation-backups/`
     - Command: `New-Item -ItemType Directory -Path "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\remediation-backups" -Force`
     - Verification: Run `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\remediation-backups"` and confirm `True`.
     - Error recovery: If access is denied, stop; do not edit any external config or skill files.

3. - [x] **Task 0.3: Append a remediation start entry to the execution log**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/execution-log.md`
     - Command: `Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log.md" -Value "`n## $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Remediation start`n- Action: Begin remediation and final validation pass.`n- Result: started"`
     - Verification: Run `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log.md" -Pattern "Remediation start"` and confirm at least one match.
     - Error recovery: If `execution-log.md` is missing, create it with `New-Item -ItemType File -Path "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log.md" -Force`, then rerun the append command.

4. - [x] **Task 0.4: Back up the four known broken skill files**
     - File/path targets:
       - `C:\Users\DaveWitkin\.agents\skills\gemini-proxy\SKILL.md`
       - `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md`
       - `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md`
       - `C:\Users\DaveWitkin\.agents\skills\notebooklm-cli\SKILL.md`
     - Command: `$ts=Get-Date -Format 'yyyyMMdd-HHmmss'; $dest="C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\remediation-backups"; @("C:\Users\DaveWitkin\.agents\skills\gemini-proxy\SKILL.md","C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md","C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md","C:\Users\DaveWitkin\.agents\skills\notebooklm-cli\SKILL.md") | ForEach-Object { Copy-Item -LiteralPath $_ -Destination (Join-Path $dest ((Split-Path $_ -Parent | Split-Path -Leaf) + "-SKILL.md.backup-$ts")) -Force }`
     - Verification: Run `Get-ChildItem -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\remediation-backups" -Filter "*-SKILL.md.backup-*"` and confirm at least 4 files exist.
     - Error recovery: If any source path is missing, stop and record the missing path in `execution-log.md`.

**Phase 0 Exit Criteria:** Track directory exists, remediation backup directory exists, execution log has a remediation start entry, and the four broken skill files have backups.

---

## Phase 1: Repair Skill Frontmatter

**Objective:** Fix invalid YAML frontmatter caused by unquoted description values and prove all previously edited skill frontmatter parses.

1. - [x] **Task 1.1: Quote the `gemini-proxy` description value**
     - File/path: `C:\Users\DaveWitkin\.agents\skills\gemini-proxy\SKILL.md`
     - Edit: In YAML frontmatter only, change `description: Manage local Gemini API Key Rotator Proxy: status, restart, key rotation, monitoring.` to `description: "Manage local Gemini API Key Rotator Proxy: status, restart, key rotation, monitoring."`.
     - Verification command: `python -c "import pathlib,yaml; p=pathlib.Path(r'C:\Users\DaveWitkin\.agents\skills\gemini-proxy\SKILL.md'); s=p.read_text(encoding='utf-8'); fm=s.split('---',2)[1]; yaml.safe_load(fm); print('YAML OK')"`
     - Expected output: `YAML OK`.
     - Error recovery: If parsing fails, restore the file from the newest `gemini-proxy-SKILL.md.backup-*` in `artifacts/remediation-backups/` and stop.

2. - [x] **Task 1.2: Quote the `knowledge-graph-builder` description value**
     - File/path: `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md`
     - Edit: In YAML frontmatter only, change `description: Ingest source material into the local markdown knowledge graph: extract entities, deduplicate, validate.` to `description: "Ingest source material into the local markdown knowledge graph: extract entities, deduplicate, validate."`.
     - Verification command: `python -c "import pathlib,yaml; p=pathlib.Path(r'C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md'); s=p.read_text(encoding='utf-8'); fm=s.split('---',2)[1]; yaml.safe_load(fm); print('YAML OK')"`
     - Expected output: `YAML OK`.
     - Error recovery: If parsing fails, restore the newest `knowledge-graph-builder-SKILL.md.backup-*` and stop.

3. - [x] **Task 1.3: Quote the `knowledge-graph-maintainer` description value**
     - File/path: `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md`
     - Edit: In YAML frontmatter only, change `description: Audit and maintain the local markdown knowledge graph: health, gaps, review queues.` to `description: "Audit and maintain the local markdown knowledge graph: health, gaps, review queues."`.
     - Verification command: `python -c "import pathlib,yaml; p=pathlib.Path(r'C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md'); s=p.read_text(encoding='utf-8'); fm=s.split('---',2)[1]; yaml.safe_load(fm); print('YAML OK')"`
     - Expected output: `YAML OK`.
     - Error recovery: If parsing fails, restore the newest `knowledge-graph-maintainer-SKILL.md.backup-*` and stop.

4. - [x] **Task 1.4: Quote the `notebooklm-cli` description value**
     - File/path: `C:\Users\DaveWitkin\.agents\skills\notebooklm-cli\SKILL.md`
     - Edit: In YAML frontmatter only, change `description: Interact with Google NotebookLM programmatically: create notebooks, add sources, generate content.` to `description: "Interact with Google NotebookLM programmatically: create notebooks, add sources, generate content."`.
     - Verification command: `python -c "import pathlib,yaml; p=pathlib.Path(r'C:\Users\DaveWitkin\.agents\skills\notebooklm-cli\SKILL.md'); s=p.read_text(encoding='utf-8'); fm=s.split('---',2)[1]; yaml.safe_load(fm); print('YAML OK')"`
     - Expected output: `YAML OK`.
     - Error recovery: If parsing fails, restore the newest `notebooklm-cli-SKILL.md.backup-*` and stop.

5. - [x] **Task 1.5: Validate all 14 previously edited skill frontmatter blocks**
     - File/path output: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/skill-yaml-validation.txt`
     - Command: `python -c "import pathlib,yaml,sys; paths=[r'C:\Users\DaveWitkin\.agents\skills\clickup-cli\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\google-drive\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\first-principles-mastery\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\gemini-proxy\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\gmail-workspace\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\image-to-html-reconstruction\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\frontend-design\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\find-info\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\notebooklm-cli\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\notebooklm-meta-prompt\SKILL.md',r'C:\Users\DaveWitkin\.config\opencode\skill\nlm-skill\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\slack-messaging\SKILL.md']; out=[]; bad=[];\nfor x in paths:\n p=pathlib.Path(x); s=p.read_text(encoding='utf-8'); fm=s.split('---',2)[1]; yaml.safe_load(fm); out.append('OK '+x)\npathlib.Path(r'C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\skill-yaml-validation.txt').write_text('\\n'.join(out)+'\\n',encoding='utf-8'); print('validated',len(out),'files')"`
     - Verification: Expected output is `validated 14 files`, and `artifacts/skill-yaml-validation.txt` contains 14 lines beginning with `OK `.
     - Error recovery: If `ModuleNotFoundError: No module named 'yaml'` appears, run `python -m pip install PyYAML` once, then rerun the validation command. If any file still fails, restore that file from its newest backup and rerun.

**Phase 1 Exit Criteria:** The four known broken files are fixed, and `artifacts/skill-yaml-validation.txt` proves all 14 edited skill files parse as YAML.

---

## Phase 2: Repair Artifact Corruption and Trigger Metadata

**Objective:** Remove known control-character corruption and verify discovery-critical trigger metadata was not accidentally removed.

1. - [x] **Task 2.1: Back up files that will be scanned or repaired for control characters**
     - File/path targets:
       - `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/reduction-proposals.md`
       - `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
       - `.conductor/tracks/20260526-system-prompt-token-audit/execution-log.md`
       - `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
     - Command: `$ts=Get-Date -Format 'yyyyMMdd-HHmmss'; $dest="C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\remediation-backups"; @("C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\reduction-proposals.md","C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\final-report.md","C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log.md","C:\Users\DaveWitkin\.config\opencode\AGENTS.md") | ForEach-Object { if (Test-Path -LiteralPath $_) { Copy-Item -LiteralPath $_ -Destination (Join-Path $dest ((Split-Path $_ -Leaf) + ".backup-$ts")) -Force } else { "MISSING $_" | Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log.md" } }`
     - Verification: Backup files exist in `artifacts/remediation-backups/` for each existing target.
     - Error recovery: If `final-report.md` does not exist, create an empty file at `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md` and continue.

2. - [x] **Task 2.2: Replace known corrupted strings with ASCII-safe text**
     - File/path targets: same as Task 2.1.
     - Required replacements:
       - Replace corrupted `escalate upstream` text in `artifacts/reduction-proposals.md` with `escalate upstream`.
       - Replace corrupted `bash` text in `artifacts/final-report.md` with `bash`.
       - Replace corrupted `read` text in `artifacts/final-report.md` with `read`.
       - Replace corrupted `<=` text in `artifacts/final-report.md` with `<=`.
       - Replace corrupted `tokenscope` text in `execution-log.md` with `tokenscope`.
       - Replace corrupted arrow text in `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` with `osgrep -> grep/glob -> targeted Read`.
     - Verification command: `python -c "import pathlib; paths=[r'C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\reduction-proposals.md',r'C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\final-report.md',r'C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log.md',r'C:\Users\DaveWitkin\.config\opencode\AGENTS.md']; bad=[];\nfor x in paths:\n s=pathlib.Path(x).read_text(encoding='utf-8',errors='replace');\n for i,ch in enumerate(s):\n  if (ord(ch)<32 and ch not in '\\n\\r\\t') or ch=='\ufffd': bad.append((x,i,ord(ch)))\nprint('BAD',len(bad)); [print(b) for b in bad[:20]]"`
     - Expected output: `BAD 0`.
     - Error recovery: If output is not `BAD 0`, inspect the printed file and position, replace the character with ASCII text, and rerun once.

3. - [x] **Task 2.3: Verify trigger metadata presence in three skills**
     - File/path targets:
       - `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md`
       - `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md`
       - `C:\Users\DaveWitkin\.agents\skills\slack-messaging\SKILL.md`
     - Command: `python -c "import pathlib,re; paths=[r'C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md',r'C:\Users\DaveWitkin\.agents\skills\slack-messaging\SKILL.md'];\nfor x in paths:\n s=pathlib.Path(x).read_text(encoding='utf-8'); fm=s.split('---',2)[1]; print(('HAS_TRIGGERS ' if re.search(r'(?m)^triggers:',fm) else 'MISSING_TRIGGERS ')+x)"`
     - Verification: Expected output includes `HAS_TRIGGERS` for all three files.
     - Error recovery: If a file prints `MISSING_TRIGGERS`, restore the `triggers:` block from the file's `.backup-20260526-153500` backup, then rerun Task 1.5 and Task 2.3.

4. - [x] **Task 2.4: Create or update the track change log**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/change-log.md`
     - Command: `Add-Content -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\change-log.md" -Value "# Change Log`n`n## $(Get-Date -Format 'yyyy-MM-dd')`n- Repaired invalid skill YAML frontmatter.`n- Removed control-character corruption from track artifacts and AGENTS.md.`n- Verified trigger metadata for knowledge graph and Slack skills."`
     - Verification: Run `Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\change-log.md"` and confirm `True`; then confirm the file contains `Repaired invalid skill YAML frontmatter`.
     - Error recovery: If `Add-Content` duplicates the `# Change Log` heading, keep the duplicate harmlessly or clean it during final handover; do not block validation.

**Phase 2 Exit Criteria:** Control-character scan returns `BAD 0`, trigger metadata is present or restored, and `change-log.md` exists.

---

## Phase 3: Fresh-Session Measurement and Capability Validation

**Objective:** Validate the repaired prompt environment in a new OpenCode session and capture the post-reduction system-token count.

1. - [x] **Task 3.1: Start a brand-new OpenCode session before measuring**
     - Required action: Close the current OpenCode session and open a new one in `C:\development\opencode`.
     - Command to run in the new session after it opens: `Get-Location`
     - Verification: Expected path output is `C:\development\opencode`.
     - Error recovery: If the path is different, reopen the session with working directory `C:\development\opencode` before continuing.

2. - [x] **Task 3.2: Capture post-reduction tokenscope output**
     - File/path output: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/post-reduction-tokenscope.txt`
     - Action: Run the `tokenscope` tool in the fresh session.
     - Command after tokenscope completes: `Copy-Item -LiteralPath "C:\Users\DaveWitkin\token-usage-output.txt" -Destination "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\post-reduction-tokenscope.txt" -Force`
     - Verification: Run `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\post-reduction-tokenscope.txt" -Pattern "System \(inferred from API telemetry\)"` and confirm at least one match.
     - Error recovery: If `token-usage-output.txt` is missing, run `tokenscope` once more. If it is still missing, record `tokenscope output missing` in `final-report.md` and continue with validation marked incomplete.

3. - [x] **Task 3.3: Validate skill discovery for calendar skills**
     - Action: In the fresh session, run skill discovery for calendar skills using the available skill discovery mechanism.
     - Expected query: `calendar`
     - Expected result example: at least one result such as `calendar-today`, `calendar-schedule`, `google-calendar-today`, or `unified-calendar-today`.
     - File/path to record result: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Verification: `final-report.md` contains `Calendar skill discovery: PASS` plus the returned skill name.
     - Error recovery: If no calendar skill appears, record `Calendar skill discovery: FAIL` and do not mark the track complete.

4. - [x] **Task 3.4: Validate skill loading for one calendar skill**
     - Action: Load one discovered calendar skill, preferably `calendar-today` if present.
     - Expected result: Skill content loads without YAML/frontmatter errors.
     - File/path to record result: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Verification: `final-report.md` contains `Calendar skill load: PASS`.
     - Error recovery: If loading fails, record the exact skill name and error, then inspect only that skill's frontmatter; do not edit unrelated skills.

5. - [x] **Task 3.5: Validate email skill discovery**
     - Action: In the fresh session, run skill discovery for email skills using query `email`.
     - Expected result example: at least one result such as `email-draft-reply`, `outlook-inbox-triage`, or `gmail-draft-reply`.
     - File/path to record result: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Verification: `final-report.md` contains `Email skill discovery: PASS` plus the returned skill name.
     - Error recovery: If no email skill appears, record `Email skill discovery: FAIL` and do not mark the track complete.

6. - [x] **Task 3.6: Validate core terminal tool behavior**
     - Command: `Write-Output "hello"`
     - Expected output: `hello`
     - File/path to record result: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Verification: `final-report.md` contains `bash terminal check: PASS`.
     - Error recovery: If the command fails, record the exact error in `final-report.md` and stop finalization.

7. - [x] **Task 3.7: Validate markdown file discovery behavior**
     - Action: Run a file glob for markdown files in `C:\development\opencode` using pattern `**/*.md`.
     - Expected result: At least one markdown path is returned, such as `.conductor/tracks.md`.
     - File/path to record result: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Verification: `final-report.md` contains `glob markdown check: PASS`.
     - Error recovery: If glob tooling fails with `Bun is not defined`, record that exact error and use PowerShell fallback `Get-ChildItem -LiteralPath "C:\development\opencode" -Recurse -Filter "*.md"` only for evidence gathering; keep the tool validation marked failed.

8. - [x] **Task 3.8: Validate text search behavior**
     - Action: Search for `Conductor Tracks` under `.conductor/`.
     - Expected result: A match in `.conductor/tracks.md` or another conductor markdown file.
     - File/path to record result: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Verification: `final-report.md` contains `grep conductor check: PASS`.
     - Error recovery: If grep tooling fails, record the exact error and use PowerShell fallback `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks.md" -Pattern "Conductor Tracks"` only for evidence gathering; keep the tool validation marked failed.

9. - [x] **Task 3.9: Validate file read behavior**
     - Action: Read `.conductor/tracks.md`.
     - Expected result: File content is returned and includes conductor track index content.
     - File/path to record result: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Verification: `final-report.md` contains `read tracks.md check: PASS`.
     - Error recovery: If the read tool fails, record the exact error and use PowerShell fallback `Get-Content -LiteralPath "C:\development\opencode\.conductor\tracks.md" -TotalCount 20` only for evidence gathering; keep the tool validation marked failed.

**Phase 3 Exit Criteria:** Post-reduction tokenscope exists or is explicitly marked unavailable, skill discovery/loading results are recorded, and tool validation results are recorded.

---

## Phase 4: Final Report and Conductor Bookkeeping

**Objective:** Convert validation evidence into the final conclusion and synchronize all conductor status files.

1. - [x] **Task 4.1: Write the final report section skeleton**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Required structure:
       ```md
       # Final Report

       ## Token Comparison

       ## Component Changes

       ## Skill Validation

       ## Tool Validation

       ## AGENTS.md Rule Validation

       ## Conclusion
       ```
     - Verification: Run `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\final-report.md" -Pattern "## Token Comparison","## Component Changes","## Skill Validation","## Tool Validation","## AGENTS.md Rule Validation","## Conclusion"` and confirm all six headings appear.
     - Error recovery: If existing content would be lost, append missing headings instead of overwriting the file.

2. - [x] **Task 4.2: Add the token comparison table**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Required table template:
       ```md
       | Measure | Baseline | Post-Reduction | Delta |
       |---|---:|---:|---:|
       | System tokens | 27280 | <post-reduction-system-tokens> | <baseline-minus-post> |
       ```
     - Verification: The table contains numeric values for baseline, post-reduction, and delta, or the post-reduction value is explicitly `unavailable` with a blocker note.
     - Error recovery: If post-reduction tokens cannot be parsed, write `Post-reduction system tokens unavailable; tokenscope capture failed` and set conclusion to `Validation incomplete; target status cannot be concluded.`

3. - [x] **Task 4.3: Add the final conclusion**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md`
     - Required conclusion values: Use exactly one of these lines:
       - `Target achieved locally.`
       - `Target not achieved locally; remaining overhead appears non-local.`
       - `Validation incomplete; target status cannot be concluded.`
     - Verification: `final-report.md` contains exactly one of the three conclusion lines.
     - Error recovery: If validation failed but tokens were captured, choose the validation-incomplete conclusion and list failed checks.

4. - [x] **Task 4.4: Correct metadata progress values**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/metadata.json`
     - Edit requirements:
       - Ensure `progress.completedTasks` is not greater than `progress.totalTasks`.
       - Set `status` to `completed` only if all non-deferred tasks in this plan are complete and final validation passed.
       - Otherwise set `status` to `active` or `blocked` and explain the blocker in `execution-log.md`.
     - Verification command: `python -m json.tool "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\metadata.json" > $null; if ($LASTEXITCODE -eq 0) { "JSON OK" }`
     - Expected output: `JSON OK`.
     - Error recovery: If JSON validation fails, restore from the latest metadata backup if one exists; otherwise fix commas/quotes until `python -m json.tool` passes.

5. - [x] **Task 4.5: Update `.conductor/tracks-ledger.md`**
     - File/path: `.conductor/tracks-ledger.md`
     - Edit requirement: Update the `20260526-system-prompt-token-audit` entry so its phase/status matches `metadata.json` and no longer says `not started`.
     - Verification: Search `.conductor/tracks-ledger.md` for `20260526-system-prompt-token-audit`; it appears exactly once and the line includes the current status.
     - Error recovery: If duplicate entries exist, keep the most current one and remove stale duplicates.

6. - [x] **Task 4.6: Update `.conductor/tracks.md`**
     - File/path: `.conductor/tracks.md`
     - Edit requirement: Update the `20260526-system-prompt-token-audit` row with the current status and completion date if completed.
     - Verification: Search `.conductor/tracks.md` for `20260526-system-prompt-token-audit`; it appears exactly once and agrees with `metadata.json`.
     - Error recovery: If the track row is missing, add one row using the existing table format in `.conductor/tracks.md`.

7. - [x] **Task 4.7: Append the final handoff entry**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/execution-log.md`
     - Required template:
       ```md
       ## Handoff
       - Current status: <completed|active|blocked>
       - Final report: .conductor/tracks/20260526-system-prompt-token-audit/artifacts/final-report.md
       - Plan: .conductor/tracks/20260526-system-prompt-token-audit/plan.md
       - Remaining blockers: <none|list>
       - Recommended next action: <action>
       ```
     - Verification: `execution-log.md` contains `## Handoff` and a `Current status:` line.
     - Error recovery: If the log has control-character corruption after appending, rerun the control-character scan from Task 2.2.

8. - [x] **Task 4.8: Mark completed tasks in this plan**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/plan.md`
     - Edit requirement: Change each completed task checkbox from `[ ]` to `[x]`; leave failed, skipped, or blocked tasks unchecked and note the reason in `execution-log.md`.
     - Verification: Every task marked `[x]` has corresponding validation evidence in an artifact, command output, or `execution-log.md`.
     - Error recovery: If evidence is missing, leave the task unchecked and document the gap.

**Phase 4 Exit Criteria:** `final-report.md`, `metadata.json`, `.conductor/tracks-ledger.md`, `.conductor/tracks.md`, `execution-log.md`, and `plan.md` agree on the final status.

---

## Final Phase: Validation & Handover

**Objective:** Perform a final consistency check and leave a clear handoff for the user or next build agent.

1. - [x] **Task 5.1: Run final artifact existence checks**
     - Command: `@("C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\spec.md","C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\plan.md","C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\metadata.json","C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log.md","C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\change-log.md","C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\final-report.md") | ForEach-Object { if (Test-Path -LiteralPath $_) { "OK $_" } else { "MISSING $_" } }`
     - Verification: Output contains only `OK` lines and no `MISSING` lines.
     - Error recovery: If an artifact is missing, create or restore it before handover.

2. - [x] **Task 5.2: Run final control-character scan**
     - Command: `python -c "import pathlib; paths=[r'C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\spec.md',r'C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\plan.md',r'C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log.md',r'C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\change-log.md',r'C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\final-report.md',r'C:\Users\DaveWitkin\.config\opencode\AGENTS.md']; bad=[];\nfor x in paths:\n s=pathlib.Path(x).read_text(encoding='utf-8',errors='replace');\n for i,ch in enumerate(s):\n  if (ord(ch)<32 and ch not in '\\n\\r\\t') or ch=='\ufffd': bad.append((x,i,ord(ch)))\nprint('BAD',len(bad))"`
     - Verification: Expected output is `BAD 0`.
     - Error recovery: If not `BAD 0`, repair the printed file before reporting completion.

3. - [x] **Task 5.3: Record final user-facing handover summary in `execution-log.md`**
     - File/path: `.conductor/tracks/20260526-system-prompt-token-audit/execution-log.md`
     - Required content:
       ```md
       ## User Handover Summary
       - Track updated: yes
       - Final status: <completed|active|blocked>
       - Total plan tasks: <number>
       - Completed plan tasks: <number>
       - Final report path: C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\final-report.md
       ```
     - Verification: The section exists and includes absolute Windows paths.
     - Error recovery: If task counts are uncertain, count checklist lines in `plan.md` with `Select-String -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\plan.md" -Pattern "- \[[ x]\]"`.

**Final Phase Exit Criteria:** All required artifacts exist, scans pass, and the handover summary gives the next operator a complete starting point.

---

## Execution Readiness Checklist

| # | Standard | Pass/Fail | Evidence |
|---|---|---|---|
| 1 | Atomic tasks | PASS | Each checkbox has one primary action. |
| 2 | Exact file paths | PASS | Every task names exact repo-relative or absolute paths. |
| 3 | Explicit commands | PASS | Terminal commands are written verbatim where commands are required. |
| 4 | Clear ordering | PASS | Backups precede edits; repairs precede validation; validation precedes closure. |
| 5 | Verification per step | PASS | Each task includes expected output or file/content validation. |
| 6 | No assumed context | PASS | Starting state, target files, and expected outputs are included inline. |
| 7 | Concrete examples | PASS | YAML replacement examples, report templates, and handoff templates are included. |
| 8 | Error recovery | PASS | Every task includes a fallback, restore, or stop condition. |

## Top 3 Implementation Risks + Mitigations

1. **YAML validation command may fail because PyYAML is unavailable.**
   - Mitigation: The plan permits exactly one `python -m pip install PyYAML` retry before rerunning validation.

2. **Fresh-session tokenscope may fail or not emit `token-usage-output.txt`.**
   - Mitigation: Retry once in a fresh session; if still unavailable, mark validation incomplete rather than inventing a post-reduction number.

3. **Tool validation may reveal environment-level failures unrelated to the prompt edits, such as `Bun is not defined`.**
   - Mitigation: Record exact tool failure, use PowerShell fallback only for evidence gathering, and keep the relevant validation check failed until the tool issue is resolved.

## First Task the Build Agent Should Execute Immediately

Execute **Task 0.1: Confirm the active track directory exists** with:

```powershell
Test-Path -LiteralPath "C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit"
```

Continue to Task 0.2 only if the command returns `True`.
