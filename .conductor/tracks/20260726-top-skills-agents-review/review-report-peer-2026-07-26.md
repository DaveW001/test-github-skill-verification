# Stage 2 Peer Review — Top Skills and Agents Portfolio

**Verdict: Needs Work — not execution-ready.**  The plan has a sound phase order, good safety intent, one labelled acceptance check per executable task, and recovery language.  It is not yet safe for a less-capable executor because nearly every task states outcomes rather than executable actions, and most acceptance checks accept self-reported booleans, headings, or a mere file count instead of the required evidence body.

## Review scope and test evidence

- Reviewed `spec.md`, `plan.md`, and `metadata.json` against the Stage 2 prompt and the full required `skill-creator` checklist.
- Parsed all 20 embedded acceptance snippets. The 19 `python -c` snippets are syntactically valid; Task 1.1 invokes a script intentionally not yet created, so it cannot be compiled or run at review time.
- Only the three planning artifacts currently exist in the track. Future-output checks cannot be run against real output without executing the plan; therefore none has demonstrated its claimed success output. This is why syntax validation is not treated as acceptance validation.
- Counted **20** executable tasks and **8** execution-readiness checkboxes (28 plan checkboxes total). `metadata.json` currently claims 19 and 27.

## Blocking structural findings

1. **Pipeline contract mismatch.** `metadata.json` calls the track `standard` but declares `1 -> 2 -> 5 -> 7 -> 9` and skips Stage 6. The defined standard path is `1 -> 2 -> 5 -> 6 -> 7 -> 9`; this is a bookkeeping track whose appropriate mode is `bookkeeping`, with Stage 2 deliberately added for broad unversioned global-agent/skill risk. Stage 3/8 trigger sources are also not named.
2. **No executable review engine or evidence schema.** Tasks 2.1 and 3.1 can set `rubric_complete: true` without proving any checklist category, evidence, severity, source path, or test result. This fails the requirement to apply the entire checklist to each of 20 skills and a rigorous rubric to each of 10 agents.
3. **Backup safety is incomplete.** Copying complete global skill/agent folders into a repository-local `.conductor` directory without first classifying the destination as tracked/ignored and scanning/redacting reportable evidence can leak credentials or private prompt material and may contaminate the worktree. The plan also does not state a reversible, verified restore command.

## Task-by-task ratings

| Task | Rating | Exact reason |
|---|---|---|
| 0.1 Baseline | Needs Work | One checkbox combines five inventories. It supplies no capture command/schema; acceptance only asserts five keys and one Boolean, not canonical junction target, inventory body, redaction, or unchanged-target baseline. |
| 0.2 Rubrics | **Blocking** | It says “applicable” and “agent checklist from the spec,” so the executor can omit checklist items. The heading-only check is expressly disallowed by Stage 2 standards. |
| 0.3 Scaffold | Needs Work | Paths are relative and creation is prose, not commands. It does not prove the directory is safe for sensitive backups or that the marker contains the canonical path. |
| 1.1 Ranking | **Blocking** | Schema discovery, script implementation, ranking policy, and data extraction are one task. No command/schema proves read-only SQLite, archived coverage, deterministic ties, source counts, confidence, or no raw bodies. |
| 1.2 Selection | Needs Work | Count/path checks can select inactive or noncanonical artifacts and omit scores, confidence, evidence, tie-breaks, aliases, and exclusions. |
| 2.1 Static skills | **Blocking** | `rubric_complete` is self-attested. The task does not explicitly require several required checklist checks: decision tree where applicable; trigger schema and two phrase tests; gotcha/default/alternative quality; script error/magic-number/dependency review; forward slash/compatibility; permission rules and per-agent overrides; test-case convention. |
| 2.2 Functional skills | Needs Work | “bounded subagent/test path” is not a concrete command or safety protocol. The check permits 20 arbitrary verdicts and never proves a fixture/dry-run, command, redacted output, or an Unverified reason. |
| 2.3 Skill matrix | Needs Work | Name substring and a filtered queue do not prove all categories/findings/functional verdicts are consolidated, or that all high-confidence material findings were included. |
| 3.1 Static agents | **Blocking** | No frozen agent rubric/schema or per-category status/evidence is required. `rubric_complete` can conceal missing activation, model route, permission, tool/skill, prompt-body, output-contract, overlap, and diversity checks. |
| 3.2 Agent smoke/matrix | Needs Work | No per-agent fixture, exact dry-run command, expected safe result, or command/session/exit-code body verification. The matrix check only looks for names. |
| 4.1 Backups | **Blocking** | The manifest check permits empty queues/entries and trusts `backup_verified`; it does not prove every copied path/hash/marker exists, destination safety, or a reversible restore mapping. |
| 4.2 Skill corrections | Needs Work | `all([])` passes; the manifest can be empty or omit approved targets. No machine-check compares every change to the queue and backup or prevents a capability/authority expansion. |
| 4.3 Agent corrections | Needs Work | Same empty-list defect. `permission_broadened: false` is an assertion, not a before/after permission comparison. |
| 5.1 Revalidate skills | Needs Work | `all([])` permits no validation. It conflicts with its recovery text by allowing a failed changed skill to remain while the authoritative check requires every changed skill to pass. |
| 5.2 Revalidate agents | Needs Work | `all([])` and a self-reported diversity flag are insufficient; no link to the actual changed-agent set, smoke evidence, model inventory, or applicability/N/A treatment. |
| 5.3 Portfolio report | Needs Work | Required headings and one table header are phrase-only checks; neither 20 skill rows, 10 agent rows, nor decision-ready body content is proved. |
| F.1 Sync | **Blocking** | Metadata is presently wrong (19/27 versus 20/28). The check ignores `percentage`, pipeline fields, execution-log body, and `status/stage`; it would accept an empty log. |
| F.2 Ledgers | Needs Work | Loose substring counts do not prove an upserted canonical row or matching status/date/progress. It also does not use a structural table/ledger parser. |
| F.3 Stage 7 | Needs Work | `glob()` ordering is not latest-report ordering and `Ready to close` is phrase-only. It does not prove the validator identity, no blockers, all task evidence, or closeout readiness body. |
| F.4 Terminal closeout | Needs Work | File existence plus a waiver phrase and `status=complete` does not prove a Stage 9 log, post-doc validation/waiver body, one permitted Stage 9 retry, or that docs made no semantic change. |

## Exact proposed rewrites

Use the following task text replacements. `C:\development\opencode\.conductor\tracks\20260726-top-skills-agents-review` is abbreviated as **TRACK** only inside this review; the plan itself must write the full absolute path in every command.

### 0.1 — replace with

> **0.1 Capture the immutable baseline.** Run the exact read-only inventory command in `TRACK\scripts\capture_baseline.ps1` (created from the inline JSON schema below) with `-RepoRoot "C:\development\opencode" -VaultRoot "C:\Users\DaveWitkin\.opencode-lazy-vault" -SkillRoot "C:\Users\DaveWitkin\.config\opencode\skill" -AgentRoot "C:\Users\DaveWitkin\.config\opencode\agent" -CodexSkillRoot "C:\Users\DaveWitkin\.codex\skills" -OutFile "TRACK\baseline-inventory.json"`. The JSON must contain UTC `captured_at`, canonical resolved paths, junction `link_path` and `target_path`, per-root file lists/counts with SHA-256, redacted `git_status`, and `redaction_applied: true`; do not record file bodies, tokens, or secrets. Stop before edits if the resolved Codex skills target is not exactly the resolved vault root. **Authoritative acceptance check:** run `python "TRACK\scripts\verify_portfolio_review.py" --check baseline --track "TRACK"`; it must print JSON `{"check":"baseline","status":"PASS"}` and exit 0. **Diagnostic checks:** compare the pre-edit inventory hashes after each correction cohort. **Recovery:** write `baseline-topology-blocker.md`, leave all targets unchanged, and stop.

### 0.2 — replace with

> **0.2 Freeze the complete, machine-readable review contract.** Create `TRACK\review-rubric.md`, `TRACK\schemas\skill-packet.schema.json`, `TRACK\schemas\agent-packet.schema.json`, and `TRACK\scripts\verify_portfolio_review.py`. The skill schema must require one result (`Pass|Fail|Not Applicable|Unverified`), severity, confidence, source path, and nonempty evidence for every named checklist item: scope/intent/decision tree; naming/placement; all-caps SKILL.md; frontmatter/name/description/triggers; progressive disclosure/one-level links; gotchas/default/alternatives; scripts/error handling/magic numbers/dependencies; forward-slash portability/compatibility; permissions/agent overrides; structural checks; functional smoke/trigger phrases/scripts/test case; troubleshooting. The agent schema must require the same result/evidence fields for activation/purpose, frontmatter/body, mode, model/variant availability, permissions/least privilege, tools/skills, Windows/path/shell/bounded-command guidance, safety stops, output contract, overlap, smoke outcome, and Conductor diversity/applicability. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check rubric --track "TRACK"` prints `{"check":"rubric","status":"PASS"}` and exits 0. **Recovery:** if a checklist item cannot be operationalized, record it in `rubric-open-question.md` and stop before selection.

### 0.3 — replace with

> **0.3 Create a safe evidence/backup scaffold.** First run `git -C "C:\development\opencode" check-ignore -v -- ".conductor/tracks/20260726-top-skills-agents-review/backups"` and record whether the destination is ignored; if it is tracked or not ignored, stop and write `backup-destination-blocker.md` before any backup is copied. Then create `TRACK\backups\2026-07-26-pre-edit`, `TRACK\evidence`, `TRACK\review-batches\skills`, and `TRACK\review-batches\agents`; write `backup-dir.json` containing the full canonical backup path and `copy_targets_started: false`. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check scaffold --track "TRACK"` prints `{"check":"scaffold","status":"PASS"}`. **Recovery:** never reuse a nonempty backup directory without matching `trackId` and a hash-equal `backup-dir.json`.

### 1.1 — replace with two atomic tasks

> **1.1a Inspect and record the read-only database contract.** Run `python "TRACK\scripts\rank_portfolio.py" --inspect-schema --db "C:\Users\DaveWitkin\.local\share\opencode\opencode.db" --output "TRACK\evidence\database-schema-summary.json" --read-only --timeout-seconds 60`. The script must open `file:...opencode.db?mode=ro`, include archived sessions, emit only table/column names and aggregate counts, state the verified millisecond-to-UTC conversion, and never select or write raw message-body columns. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check database-schema --track "TRACK"` prints `{"check":"database-schema","status":"PASS"}`. **Recovery:** if required structured records are absent, record the precise missing tables/columns and proceed only through the documented fallback path.
>
> **1.1b Rank the portfolio reproducibly.** Implement the documented scoring formula and deterministic final sort `(score desc, unique_sessions desc, recency desc, canonical_name casefold asc)` in `TRACK\scripts\rank_portfolio.py`; run it with the same read-only database, `--codex-evidence-root "C:\Users\DaveWitkin\.codex"`, and output `TRACK\usage-ranking.json`. Each candidate must include canonical path, artifact type, source signal(s), counts, recency, score components, confidence, and exclusion/tie-break rationale; mark fallback signals as inferred. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check ranking --track "TRACK"` prints `{"check":"ranking","status":"PASS"}`. **Recovery:** do not invent zero/raw-body evidence; downgrade confidence and preserve the fallback rationale.

### 1.2 — replace with

> **1.2 Resolve active canonical artifacts and freeze the 20/10 selection.** Resolve every ranked candidate with `Resolve-Path -LiteralPath`, classify active/archived/alias/package-managed/missing, and write the canonical classification plus the next eligible replacement and reason into `TRACK\usage-ranking.json`. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check selection --track "TRACK"` prints `{"check":"selection","status":"PASS"}` only when exactly 20 active unique skills and 10 active unique agents have canonical existing paths, scores, confidence, source evidence, and deterministic tie-break/exclusion records. **Recovery:** replace only with the next-ranked active candidate and append the substitution reason; never reactivate an archive.

### 2.1 — replace with

> **2.1 Generate and validate 20 complete static skill packets.** For each `selected_skills` record, run the named structural checks from the frozen rubric against the entire canonical folder and write `TRACK\review-batches\skills\<canonical-name>.json` conforming to `skill-packet.schema.json`. Parse frontmatter with the declared parser; enumerate all internal links and scripts; record the exact command/output for every syntax, link, frontmatter, uniqueness, length, portability, permission, guardrail, test-case, and trigger result. A `Pass` requires evidence; inaccessible or inapplicable checks require a precise `Unverified`/`Not Applicable` reason. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check skill-static --track "TRACK"` prints `{"check":"skill-static","status":"PASS","skills":20}` only after validating each packet against the schema, matching the selected canonical names exactly, and finding every frozen checklist item recorded with evidence/reason. **Recovery:** do not substitute `rubric_complete`; retain a malformed/inaccessible packet as `Unverified` with the failed command and continue only if the selection identity is intact.

### 2.2 — replace with

> **2.2 Perform one authority-safe functional assessment for every selected skill.** For each static packet, run `pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1" -SkillPath "<canonical-skill-path>" -PrintFunctionalPrompt`, select a read-only fixture or built-in dry-run, and record the exact safe command, expected behavior, exit code, redacted output excerpt, and verdict in that skill packet. Never dispatch a test that sends a message, changes a calendar, publishes, uses credentials, mutates production, or creates a destructive operation. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check skill-functional --track "TRACK"` prints `{"check":"skill-functional","status":"PASS","skills":20}` only when every packet has exactly one allowed verdict and either complete safe-test evidence or an explicit safety/credential reason for `FUNCTIONAL_SMOKE_TEST_UNVERIFIED`. **Recovery:** prefer a fixture/dry-run; if none is safe, mark Unverified and do not execute a live action.

### 2.3 — replace with

> **2.3 Consolidate exact skill findings.** Generate `TRACK\skill-review-matrix.md` from the validated packets and `TRACK\fix-queue.json` from only high-confidence Critical/Major/Minor findings. Each matrix row must contain the canonical name, every rubric-item result, evidence reference, functional verdict, confidence, and exact proposed fix; the queue item must contain a stable id, canonical path, evidence reference, before/after intent, safety classification, and no change authority expansion. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check skill-matrix --track "TRACK"` prints `{"check":"skill-matrix","status":"PASS","skills":20}` only when the matrix is generated from all packets and every queue item maps one-to-one to a high-confidence packet finding. **Recovery:** keep subjective/conflicting findings in the matrix as Optional/Unverified; do not queue them.

### 3.1 — replace with

> **3.1 Generate and validate 10 complete static agent packets.** For each `selected_agents` record, inspect frontmatter and complete prompt body, active-definition resolution, configured model/variant against `opencode models`, permission/tool/skill constraints, Windows-safe bounded-command instructions, safety stops, output contract, role overlap, and applicable Conductor creator/reviewer/executor/validator diversity. Write schema-valid `TRACK\review-batches\agents\<canonical-name>.json` with a result, severity, confidence, evidence, and source line range for every frozen agent-rubric item. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check agent-static --track "TRACK"` prints `{"check":"agent-static","status":"PASS","agents":10}` only when all selected canonical agents have exactly one schema-valid packet and every rubric item has evidence/reason. **Recovery:** record unavailable routes or unparseable definitions as Unverified; do not silently substitute models or alter permissions.

### 3.2 — replace with

> **3.2 Perform safe agent smoke assessments and consolidate the matrix.** For each agent packet, define a read-only/disposable-fixture prompt that exercises its stated role and prohibit external messages, publication, schedule changes, credential use, and destructive mutation. Record the exact prompt, selected configured model, session identifier, bounded command, exit code, redacted outcome, and Pass/Fail/Unverified reason; then generate `TRACK\agent-review-matrix.md` and append only evidence-backed queue entries. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check agent-matrix --track "TRACK"` prints `{"check":"agent-matrix","status":"PASS","agents":10}` only when each selected agent has a rubric-complete packet, safe smoke evidence or reason, and every queued agent fix maps to a high-confidence finding. **Recovery:** unavailable/unsafe paths remain Unverified and no different model is used to validate the definition.

### 4.1 — replace with

> **4.1 Back up each approved target with a verified restore map.** For every unique queued canonical path, copy the complete file/folder to the safe scaffold using a deterministic encoded destination name, write `TRACK\backup-manifest.json` containing source path, backup path, source/backup SHA-256 tree hashes, target type, queue ids, preexistence marker, and restore command. Do not copy a target until the backup destination safety gate in 0.3 passed. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check backups --track "TRACK"` prints `{"check":"backups","status":"PASS","targets":N}` only when N equals the distinct queued target count and every manifest entry has existing hash-equal source/backup material or an explicit absent-before-edit marker. **Recovery:** remove that target from the execution cohort and leave its queue item unresolved if any backup/hash fails.

### 4.2 — replace with

> **4.2 Apply only backed-up, approved skill fixes.** Process disjoint cohorts whose every target has a `backup-manifest` entry and a queue item. For each change, write `change-manifest.json` evidence with queue id, target, before/after hashes, diff path, intended correction, and `authority_delta: none`; compare tracked targets with `git diff -- <path>` and untracked targets with `git diff --no-index <backup> <target>`. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check skill-changes --track "TRACK"` prints `{"check":"skill-changes","status":"PASS","changes":N}` only when every changed skill is queued, backed up, diffed, and has no unapproved file or authority expansion. **Recovery:** restore exactly from the manifest backup and move the queue item to Dave-decision if scope/authority expands.

### 4.3 — replace with

> **4.3 Apply only backed-up, approved agent fixes.** Apply disjoint cohorts with the same manifest/diff requirements as 4.2. Parse before/after permission, tool, skill, model, and variant fields and record the comparison; a permission/tool/skill expansion is a blocker, not a self-reported Boolean. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check agent-changes --track "TRACK"` prints `{"check":"agent-changes","status":"PASS","changes":N}` only when every changed agent maps to a backup and queue item and the parsed comparison shows no permission/tool/skill broadening or silent model substitution. **Recovery:** restore the named target from its manifest backup and retain the finding for decision.

### 5.1 — replace with

> **5.1 Revalidate the exact changed-skill set.** Derive the changed-skill set from `change-manifest.json`; run every structural, script-syntax, safe script-functional, trigger, and representative harness smoke check required by its packet, then write evidence-linked `TRACK\validation-results.json`. A zero-change set must be represented as `changed_skills: []` and `status: NOT_APPLICABLE`, not vacuous PASS. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check changed-skills --track "TRACK"` prints `{"check":"changed-skills","status":"PASS|NOT_APPLICABLE"}` only when the validated set exactly equals the manifest set and each changed skill passes all applicable checks; a failed changed skill must be restored before this task is complete. **Recovery:** restore the failed skill; if a proven pre-existing failure prevents restoration, leave this task unchecked and create a blocker.

### 5.2 — replace with

> **5.2 Revalidate the exact changed-agent set and applicable diversity.** Derive changed agents from `change-manifest.json`; parse each definition, confirm its configured route is available, run its bounded safe smoke case, and evaluate diversity only for changed agents in applicable Conductor roles. Record `PASS`, `NOT_APPLICABLE`, or `FAIL` with source evidence in `validation-results.json`. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check changed-agents --track "TRACK"` prints `{"check":"changed-agents","status":"PASS|NOT_APPLICABLE"}` only when the validated set equals the manifest set and no applicable model/permission/diversity defect remains. **Recovery:** restore a failed agent and leave the related finding unresolved; never weaken the check or silently swap a model.

### 5.3 — replace with

> **5.3 Generate the decision-ready portfolio report from source artifacts.** Generate `TRACK\portfolio-review-report.md` from ranking, packet, queue, manifest, and validation JSON. It must contain 20 structured skill entries and 10 structured agent entries, methodology/confidence, fixes applied, validation results, unresolved Critical/Major/Minor findings, Optional improvements, explicit Unverified items, and Dave-decision items. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check portfolio-report --track "TRACK"` prints `{"check":"portfolio-report","status":"PASS","skills":20,"agents":10}` only when report entries and all finding/change/decision counts reconcile to the source JSON. **Recovery:** surface any conflict and lower confidence; never choose a favorable number.

### F.1 — replace with

> **F.1 Synchronize execution history and metadata.** Write `TRACK\execution-log-2026-07-26.md` with a dated command/result/deviation/skipped-item/model-session table and synchronize `metadata.json` from the actual plan states. Set `totalTasks` to 20, `completedTasks` to the count of `[x]` executable tasks, `percentage` to the derived integer, `readiness_check_count` to 8, and `total_checkbox_count` to 28; preserve pipeline fields and record any skipped-stage decision. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check execution-sync --track "TRACK"` prints `{"check":"execution-sync","status":"PASS","tasks":20,"checkboxes":28}` only when all counts, percentage, pipeline fields, and nonempty execution-log rows reconcile. **Recovery:** append an audit correction; never rewrite historical evidence.

### F.2 — replace with

> **F.2 Upsert one structurally valid row in each ledger.** Find the existing track row in `C:\development\opencode\.conductor\tracks.md` and `C:\development\opencode\.conductor\tracks-ledger.md`; update it in place, or insert one canonical row only if absent, using the exact metadata status/date/progress. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check ledgers --track "TRACK"` prints `{"check":"ledgers","status":"PASS"}` only when each ledger contains exactly one parsed record for the track and its status/date/progress equal metadata. **Recovery:** correct the existing record rather than appending a duplicate.

### F.3 — replace with

> **F.3 Obtain independent Phase-A closeout-readiness validation.** Select and atomically update the validator alternation state, pass the validator all absolute artifact paths and the Stage 7 prompt, and write a timestamped validation report with validator identity, task reconciliation, artifact evidence, blockers, Stage 9 readiness, and `verdict`. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check stage7 --track "TRACK"` prints `{"check":"stage7","status":"PASS","verdict":"ready_to_close"}` only when the newest report selected by parsed timestamp has the expected validator identity, zero unresolved blockers, and evidence for every nondeferred task. **Recovery:** route only concrete measurable blockers through the correction-cycle policy and stop on a repeated signature or authority-sensitive work.

### F.4 — replace with

> **F.4 Complete Stage 9 and Phase-B terminal confirmation.** Write `TRACK\doc-update-log-<UTC timestamp>.md` that lists each documentation file, before/after contract assessment, and whether a post-doc validation is required. If required, write `post-doc-validation-<UTC timestamp>.md`; otherwise record a dated reasoned waiver in both the doc log and execution log. Set `metadata.status` to `complete` only after the terminal checker passes; Stage 9 may be retried once for missing evidence. **Authoritative acceptance check:** `python "TRACK\scripts\verify_portfolio_review.py" --check terminal-closeout --track "TRACK"` prints `{"check":"terminal-closeout","status":"PASS"}` only when the newest parsed doc log has a valid Phase-B companion/waiver, no unpermitted semantic documentation change, and final metadata is complete. **Recovery:** retry Stage 9 once for absent evidence, then stop with a terminal blocker.

## Required metadata rewrite

Replace metadata pipeline/count fields with:

```json
"track_type": "bookkeeping",
"classification": "certain",
"pipeline_mode": "bookkeeping",
"pipeline_path": "1 -> 2 -> 5 -> 7 -> 9",
"pipeline_rationale": "This is a bookkeeping track with no production-code test framework. Stage 2 is deliberately added because the scope includes broad, unversioned global skill and agent artifacts; Stage 7 independently validates corrections.",
"progress": { "totalTasks": 20, "completedTasks": 0, "percentage": 0 },
"readiness_check_count": 8,
"total_checkbox_count": 28
```

Keep Stage 3 and Stage 8 conditional, but name `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md` as the controlling B+C/A+C decision source and record the actual decision in the execution log/metadata.

## Dry-run results and readiness score

| Check class | Result |
|---|---|
| Python syntax for 19 embedded `python -c` checks | Passed |
| Task 1.1 executable script | Cannot run/compile: it is a planned output, not present |
| Real-output acceptance simulation | Cannot pass yet: no task outputs exist; only `plan.md`, `spec.md`, and `metadata.json` are present |
| Metadata count reconciliation | Failed: 19/27 recorded; 20/28 in the plan |
| New replacement verifier commands | Untested: the proposed verifier is a required first-phase artifact, so it must be dry-run on a synthetic fixture before plan execution |

**Readiness score: 22/100.** This includes a 5-point deduction for the untestable planned ranking command and a further 5-point deduction for proposed verifier commands that cannot truthfully be dry-run before their planned verifier exists. No current task is Ready because every task lacks at least one required explicit action, evidence-body verification, or bounded command.

## Structural change count

- 20 task rewrites (Task 1.1 split into two atomic tasks; plan task total becomes **21** if adopted).
- 20 current acceptance checks replaced with evidence-body/schema checks (21 checks after the split).
- 1 frozen skill rubric + 1 frozen agent rubric/schema contract added.
- 1 canonical verifier added, which removes duplicated shallow one-liners.
- 1 pipeline-mode/path correction and 3 metadata count corrections.

If 1.1 is split, update the final metadata counts again to **21 executable tasks** and **29 total plan checkboxes**. The 20/28 metadata correction above applies only if the executor keeps 1.1 as one task; splitting is the recommended structural correction.

## Top three priorities

1. Freeze the machine-readable skill and agent rubrics plus evidence schema before selection or review; otherwise “complete” is self-attested and the required 20/10 coverage is not auditable.
2. Correct the pipeline metadata/count contract and split the ranking work into schema inspection and reproducible ranking before an executor is dispatched.
3. Gate backups on a tracked/ignored/sensitive-destination check, then replace all heading/count/self-assertion acceptance checks with schema and evidence-body validation.

## Final conclusion

Do not execute this plan in its current form. Apply the structural corrections above, dry-run the frozen verifier against a synthetic fixture and the real baseline, then submit the revised plan for one bounded Stage 2 re-review.
