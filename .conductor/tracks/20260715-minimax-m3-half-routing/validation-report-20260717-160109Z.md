# Stage 7 Validation Report: 20260715-minimax-m3-half-routing (M3 paired cross-check)

**Track:** 20260715-minimax-m3-half-routing
**Validator:** conductor-track-validator-m3 (`opencode-go/minimax-m3`)
**Stage:** 7 (paired cross-check, alternation dispatch; cross-family from Qwen Tier-3 executor)
**Date:** 2026-07-17T16:01:09Z
**Dispatch rationale:** `.conductor\validator-alternation.json` `last_used=tera`, `next=m3` -> under the persisted strict-alternation rule the next Stage 7 validator is the M3 paired validator. Confirmed live before this validation ran.
**Mode:** bookkeeping direct (1 -> 5 -> 7 -> 9; Stage 9 already waived in execution log)
**Tooling:** PowerShell-first via bash (native file tools down with `Bun is not defined`)
**No model invocation:** This validation performed zero model calls. GLM-5.2 and GLM-5.1 were not invoked (per user constraint). Alternation state was not flipped (belongs to the coordinator).

---

## Closeout Verdict

**Close with minor follow-ups (no blockers).** The track is honestly in a `closed` state. All bookkeeping artifacts agree: plan tasks 16/16 `[x]`, metadata `status=closed`/`phase=closed`, exactly one up-to-date row in both `tracks.md` (status=closed, completed=2026-07-17) and `tracks-ledger.md` (Phase=closed 2026-07-17), the runtime validation file records the post-restart Tera Medium smoke test as PASSED (session `ses_08f4a813cffewvxXj3YSlS0UNp`) and the M3 smoke test as DEFERRED with an honest scope statement, the persisted strict-alternation selector is in place (`.conductor\validator-alternation.json` `last_used=tera`, `next=m3`), and no active routing artifact contains a live SHA-256 parity claim (all parity references in current active artifacts explicitly state the design was REJECTED in v2 remediation). The anomaly log's last line parses as JSON and carries the canonical 7-key schema. GLM-5.2 and GLM-5.1 were not invoked. The minor follow-ups (F-1..F-4 below) are not blocking closeout.

---

## Evidence Checked (fully qualified Windows paths)

**Validator alternation state (read-only):**
- `C:\development\opencode\.conductor\validator-alternation.json` - `last_used=tera`, `next=m3`, rule explicit ("Read last_used; invoke the OTHER validator; after dispatch, flip last_used. Never use SHA-256 parity."), `initial_state_reason` set, `state_file` absolute path recorded, `created=2026-07-16`. This validator is the correctly selected M3 paired validator per the rule.

**Track artifacts (all under `C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\`):**

- `metadata.json` - `status=closed`, `phase=closed`, `track_id=20260715-minimax-m3-half-routing`, `track_type=bookkeeping`, `pipeline_mode=bookkeeping`, `pipeline_path=1 -> 5 -> 7 -> 9`, `execution_model=opencode-go/qwen3.7-plus`, `closed_at=2026-07-17`, `completed_tasks=16`, `total_tasks=16`, `runtime_validation=passed-tera-smoke`, `restart_required=false`, `selection_mechanism=persisted-strict-alternation`, `alternation_state_file=C:\development\opencode\.conductor\validator-alternation.json`, `active_agent_count=4`, `tera_ratio=0.5`, `runtime_evidence` object present. No `deterministic_parity_rule` field (correctly removed in v2). `runtime_evidence.scope` honestly says "Does not by itself execute a Stage 7 alternation dispatch".
- `spec.md` - Goal/constraints/DoD/routing decision boundary/acceptance criteria/rollback sections present; pre-existing document, no edits expected.
- `plan.md` - 16 plan tasks across Phase 0..Final Phase + Final Phase all `[x]`. 8 `[ ]` items are confined to the "Execution-readiness checklist" (preconditions, not tasks). Cross-checked the 16 atomic phase tasks (0.1, 0.2, 1.1, 2.1, 2.2, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4) - all `[x]`.
- `runtime-validation.md` - All five required sections present (`## Restart state`, `## MiniMax M3 result`, `## Tera Medium result`, `## Selected model evidence`, `## Verdict`). Tera Medium result PASSED post-restart with session ID `ses_08f4a813cffewvxXj3YSlS0UNp` and output exactly `routing-ready`. M3 result honestly DEFERRED. Scope statement explicit: "does NOT by itself execute a Stage 7 alternation dispatch". Pre-restart verdict (`runtime blocked: Error: Session not found`) is preserved in the backup but is no longer in the active verdict.
- `final-validation.md` - All 10 required sections present + `GLM-5.1` and `Qwen` substrings. SHA-256 parity references are confined to anti-claims documenting that the design was REJECTED in v2 remediation (lines 35, 41, 109, 117, 118, 130). Section "Stale SHA-256 parity assertions: Removed from all current active routing artifacts" is itself an explicit anti-claim. Closeout addendum records the 2026-07-17 reconciliation, including the Tera Medium smoke test resolution and the honest deferral of the M3 side and live alternation dispatch.
- `approved-routing-map.json` - `approval_status=approved`, `approval_required=true`, `approved_at=2026-07-15T23:41:15Z`, `map_hash=1B58BC1E1D3F238FB0CD49AF364E89E8EE8AB3F41E961F039163239AF19E5E88`, 4 assignments, `tera_count=2`, `m3_retained_count=2`, `tera_ratio=0.5`, `deterministic_alternation_rule` (NOT `_parity_rule`) string present, "PERSISTED STRICT-ALTERNATION counter... NOT SHA-256 parity" stated explicitly. No live parity rule.
- `diversity-validation.json` - `status=ok`, `same_family_pair_count=0`, `auditable_selection_count=4` == `assignment_count=4`, `tera_ratio=0.5`, `invocation_rule_proof` references "PERSISTED STRICT-ALTERNATION counter", `rejected_design` explicitly states "SHA-256(track_id) last-hex parity - rejected 2026-07-16".
- `parse-validation.json`, `post-change-inventory.json`, `rollback-validation.json`, `restart-decision.json`, `baseline-manifest.json`, `preflight.json`, `m3-inventory.json`, `routing-decision.md` - present, pre-existing, not modified by closeout reconciliation.
- `metadata.json.bak-20260717-113615` - timestamped backup of the pre-closeout metadata (kept for rollback).
- `runtime-validation.md.bak-20260717-113615` - timestamped backup of the pre-restart runtime validation (kept for rollback).
- `final-validation.md.bak-20260717-113615` - timestamped backup of the pre-closeout final-validation (kept for rollback).

**Pipeline skill and agent files (read-only cross-check):**
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` - line 49: "Validator (Tera primary or M3 paired)... Persisted alternation rule selects between them." Line 53: heading "### Deterministic validator alternation rule". Line 55: explicit anti-claim "NOT a hash-parity rule (an earlier SHA-256 parity design was rejected because it could not guarantee an exact 50/50 split on any pair of consecutive tracks)". Line 57: read `last_used` from `<workspace-root>\.conductor\validator-alternation.json`. Line 65: "**Exact 50/50**: strict alternation guarantees exactly one Tera and one M3 validation across every two consecutive runs - not merely a statistical tendency." Line 74: "Static agent count: 4 active agents (plan-reviewer M3, test-runner Tera, validator Tera, validator-m3 M3). Persisted alternation yields exactly 50/50."
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md` - line 20: `conductor-track-validator-m3: allow` in the permission block (B-1 RESOLVED). Line 59: Stage 7 dispatch implements "Select the Stage 7 validator by the persisted alternation rule... Read `last_used`... invoke the opposite validator identity, then flip `last_used` to the agent just used." Line 82: Stage 5 fallback chain preserved; executor/validator diversity noted as intact because every executor tier (GLM) differs from both validator options (Tera/OpenAI and M3/MiniMax).
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md` - frontmatter `model: openai/gpt-5.6-terra`, `variant: medium` (Tera primary validator).
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator-m3.md` - frontmatter `model: opencode-go/minimax-m3` (M3 paired validator).
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-reviewer.md` - frontmatter `model: opencode-go/minimax-m3` (Stage 2 reviewer).
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md` - frontmatter `model: openai/gpt-5.6-terra`, `variant: medium` (Stage 6 runner).
- Active M3 frontmatter pins: 2 (`conductor-plan-reviewer`, `conductor-track-validator-m3`). Active Tera frontmatter pins: 2 (`conductor-test-runner`, `conductor-track-validator`). Total 4 active agents. Matches `metadata.active_agent_count=4` and `approved-routing-map.json` `tera_count=2` + `m3_retained_count=2`.

**Index files (cross-checked against metadata.json):**
- `C:\development\opencode\.conductor\tracks.md` - exactly 1 row for `20260715-minimax-m3-half-routing`; `Status=closed`, `Completed=2026-07-17`. Matches metadata.json.
- `C:\development\opencode\.conductor\tracks-ledger.md` - exactly 1 entry for `20260715-minimax-m3-half-routing`; entry says "(Phase: closed 2026-07-17; Tera Medium runtime smoke passed; all blockers resolved)". Matches metadata.json.

**Anomaly log (read-only):**
- `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` - last line (the 2026-07-17 closeout-reconciliation audit-correction record) parses as JSON, has exactly 7 keys in the canonical order `detail, stage, severity, type, ts, subagent, track` (i.e. `ts`, `track`, `stage`, `subagent`, `type`, `severity`, `detail`), `track=20260715-minimax-m3-half-routing`, `ts=2026-07-17T11:36:00Z`, `type=audit-correction`, `severity=info`. Historical records (including the 8-key Stage 7 record at `2026-07-16T00:11:40Z`) are preserved unmodified per the v2 audit-correction convention. The labeled 7-key audit-correction record at `2026-07-16T00:40:00Z` documents the historical 8-key schema deviation without rewriting the past.

**Historical artifacts (preserved unmodified as historical records):**
- `validation-report-20260715-235430Z.md` - Stage 7 initial validation (M3, material mismatches M-1..M-4).
- `validation-report-20260716-001140Z.md` - Stage 7 re-validation (M3, "Close with minor follow-ups").
- `validation-blockers-20260716-001519Z.md` - Stage 8 (Tera alt, "Not ready to close"; B-1..B-4).
- `execution-log-2026-07-15.md` - initial 16/16 execution + Stage 5 remediation M-1..M-4.
- These contain SHA-256 parity references in their historical context and are correctly preserved as-is.

**Live deterministic verification (PowerShell via bash, run against the real artifacts during this validation):**

| Check | Result |
|---|---|
| `validator-alternation.json` parses, `last_used=tera`, `next=m3` | PASS |
| `metadata.json` parses, `status=closed`, `phase=closed` | PASS |
| `metadata.json` no `deterministic_parity_rule` field | PASS |
| `metadata.json` `selection_mechanism=persisted-strict-alternation` | PASS |
| `metadata.json` `runtime_evidence` object present | PASS |
| `metadata.json` `runtime_validation=passed-tera-smoke` | PASS |
| `plan.md` 16 plan tasks `[x]`; 8 `[ ]` confined to "Execution-readiness checklist" | PASS |
| `tracks.md` exactly 1 row, `Status=closed`, `Completed=2026-07-17` | PASS |
| `tracks-ledger.md` exactly 1 entry, Phase=closed 2026-07-17 | PASS |
| `runtime-validation.md` all 5 required sections + Tera PASSED + M3 DEFERRED + session ID | PASS |
| `final-validation.md` all 10 required sections + GLM-5.1 + Qwen | PASS |
| `final-validation.md` SHA-256 parity only as anti-claim, not as live rule | PASS |
| `approved-routing-map.json` `approval_status=approved`, ratio=0.5, alternation rule present | PASS |
| `approved-routing-map.json` no `deterministic_parity_rule` field | PASS |
| `diversity-validation.json` `status=ok`, `same_family_pair_count=0`, ratio=0.5 | PASS |
| `diversity-validation.json` no `deterministic_parity_rule` field; alternation present | PASS |
| `SKILL.md` contains "### Deterministic validator alternation rule" heading | PASS |
| `SKILL.md` rejects SHA-256 parity explicitly | PASS |
| `conductor-pipeline-orchestrator.md` permission block contains `conductor-track-validator-m3: allow` | PASS |
| `conductor-pipeline-orchestrator.md` Stage 7 dispatch implements alternation (read last_used, dispatch opposite, flip) | PASS |
| Active M3 frontmatter pins: 2 (`plan-reviewer`, `validator-m3`) | PASS |
| Active Tera frontmatter pins: 2 (`test-runner`, `validator`) | PASS |
| `pipeline-anomalies.jsonl` last line parses as JSON | PASS |
| `pipeline-anomalies.jsonl` last line has exactly 7 keys (`ts, track, stage, subagent, type, severity, detail`) | PASS |
| `pipeline-anomalies.jsonl` last line `track=20260715-minimax-m3-half-routing`, `type=audit-correction` | PASS |
| No GLM-5.2 or GLM-5.1 invocation in this validation (zero model calls) | PASS |
| `validator-alternation.json` unchanged after this validation (read-only; belongs to coordinator) | PASS |

---

## Mismatches Found

No new material mismatches. The track is in a `closed` state and all bookkeeping artifacts agree.

The following minor, non-blocking follow-ups remain (carried forward from the prior validation passes; not introduced by this validation):

### F-1 (bookkeeping-only, minor) - `conductor-test-runner.md` body prose still says "Runs on MiniMax M3"

- Frontmatter correctly pins `model: openai/gpt-5.6-terra`, `variant: medium`. Body prose still says "Runs on MiniMax M3 - an independent model family from the GLM executor."
- Impact: narrative restatement only. Frontmatter is authoritative for model selection. Not blocking closeout. Already noted in prior Stage 7 / Stage 8 reports.

### F-2 (doc-drift, minor) - `conductor-pipeline-orchestrator.md` Stage 5 prose still references stale "validator opencode-go/minimax-m3"

- Line 82: "Diversity remains intact because every executor tier differs from validator `opencode-go/minimax-m3`."
- The Stage 7 validator is no longer M3-only; it is now Tera primary with a paired M3 variant. The SKILL.md already states this correctly.
- Impact: doc-drift only. The orchestrator's actual Stage 7 dispatch (line 59) implements the alternation rule correctly. Not blocking closeout.

### F-3 (bookkeeping-only, minor) - M3 smoke test and live alternation dispatch remain unverified

- `runtime-validation.md` M3 result is DEFERRED. No Stage 7 dispatch has yet exercised the alternation state flip end-to-end against this track.
- Impact: honestly classified as deferred; the user-supplied Tera Medium evidence is sufficient to prove the model-resolution side of the Tera validator. The M3 resolution is a separate smoke test that would require an M3-pinned `opencode run` invocation. Not blocking closeout of this bookkeeping track per the executor's explicit closeout rationale.

### F-4 (audit-trail, minor) - Historical anomaly log contains one 8-key record

- The Stage 7 record at `2026-07-16T00:11:40Z` has 8 keys (`timestamp`, `track_id`, `stage`, `subagent`, `model`, `type`, `severity`, `detail`) rather than the canonical 7-key schema (`ts`, `track`, `stage`, `subagent`, `type`, `severity`, `detail`).
- Per the v2 audit-correction convention, historical JSONL is not rewritten; a labeled audit-correction record was appended at `2026-07-16T00:40:00Z` documenting the schema deviation. This is policy-compliant. Not blocking closeout.

---

## Required Fixes Before Close

**None blocking.** The track is honestly in a `closed` state, all closeout-readiness (Phase A) items pass, and the prior user request constraints (no GLM-5.2 / GLM-5.1 calls) are reflected in the execution log, the metadata (`execution_model=opencode-go/qwen3.7-plus`), and the closeout-reconciliation anomaly record.

Optional non-blocking follow-ups (carried forward, not in scope of this validation):

1. (bookkeeping-only, F-1) Update `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md` body prose to "Runs on OpenAI GPT-5.6 Tera (medium) - an independent family from the GLM executor." Frontmatter is already correct.
2. (doc-drift, F-2) Update `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md` line 82 to reference "conductor-track-validator (Tera Medium) or conductor-track-validator-m3 (M3)" instead of "validator `opencode-go/minimax-m3`". SKILL.md already states this correctly.
3. (M3 smoke, F-3) When convenient, run `opencode run --model opencode-go/minimax-m3 --format json "Reply with exactly: routing-ready"` to verify the M3 resolution side of the alternation pair. This is not blocking and was explicitly classified as deferred in the closeout rationale.
4. (audit-trail, F-4) No action required - the labeled 7-key audit-correction record at `2026-07-16T00:40:00Z` is the policy-compliant disposition.

---

## Final Recommendation

**Close the track.** The M3 paired cross-check independently confirms the closeout-readiness verdict: the bookkeeping track `20260715-minimax-m3-half-routing` is honestly in a `closed` state with all artifacts in agreement, the persisted strict-alternation selector is correctly configured and selects the M3 paired validator as the next Stage 7 dispatch (this validation), no live SHA-256 parity claim remains in any active routing artifact, the post-restart Tera Medium smoke test is honestly recorded as PASSED, the M3 smoke test and live alternation dispatch are honestly classified as deferred and not blocking, the anomaly log's last line parses with the canonical 7-key schema, and no GLM model was invoked. Minor narrative/doc-drift follow-ups (F-1, F-2) are not blocking. The alternation state has NOT been flipped by this validation; that belongs to the coordinator after successful dispatch. The next Stage 7 dispatch should flip `last_used` from `tera` to `m3` and select `conductor-track-validator` (Tera).

---

## Stage 9 Readiness (Phase A pre-check)

- **Stage 9 artifact required?** No. The execution log records a Stage 9 waiver: "This is a bookkeeping track with no public API surface changes. The SKILL.md alternation rule section is a non-contractual sync. Stage 9 documentation is waived."
- **Post-doc validation requirement:** None. The SKILL.md edit is a non-contractual description of the alternation rule; the paired agent file is a pure addition (no prior user-visible contract); the frontmatter pin changes are internal subagent routing only. No README/API doc/CHANGELOG/ADR public contract is affected.
- **Terminal closeout gate (Phase A):** All Phase A items pass. Non-deferred plan tasks all `[x]` (16/16). `metadata.json` status/phase/progress/pipeline_mode/pipeline_path/selection_mechanism reflect the executed path. `.conductor/tracks.md` and `.conductor/tracks-ledger.md` each have exactly one up-to-date row. Execution logs exist and record the model-tier deviation, the M-1..M-4 + v2 Option A remediation, the operational bypass to Qwen Tier 3, the deferred M3 smoke test, and the closeout reconciliation. Every claimed artifact exists with the required acceptance strings. Stage 9 readiness confirmed: waiver is recorded, no Stage 9 artifact required.
- **Phase B (terminal closeout confirmation after Stage 9):** Out of scope of this Stage 7 validation; belongs to the orchestrator. The Stage 9 waiver is already recorded, so the orchestrator's Phase B check is satisfied without a Stage 9 artifact.

---

## Dispatch / alternation handoff

- This validation ran as the M3 paired validator per `validator-alternation.json` (`last_used=tera`, `next=m3`).
- This validation did **not** flip the alternation state. Per the rule, the flip belongs to the coordinator after a successful Stage 7 dispatch. The next coordinator action should:
  1. Confirm this `validation-report-20260717-160109Z.md` is accepted as the closeout M3 paired cross-check.
  2. If the track is being moved to terminal closeout, leave `last_used=tera` (the alternation state tracks which validator was used, and the next dispatch should be Tera per the existing `next=m3` semantic). The state file already correctly indicates that this run was M3 and the next is Tera.
  3. No orchestrator post-doc validation required (Stage 9 waived, recorded).

---

## Author

**Author:** conductor-track-validator-m3 (Stage 7 M3 paired cross-check) - opencode-go/minimax-m3
**Stage:** 7 (paired alternation cross-check)
**Date:** 2026-07-17T16:01:09Z
**Verdict:** Close with minor follow-ups (no blockers)
