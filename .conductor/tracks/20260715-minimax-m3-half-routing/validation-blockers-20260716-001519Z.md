# Stage 8 Conditional Re-Validation Blockers: 20260715-minimax-m3-half-routing

**Stage:** 8 (sole permitted conditional re-validation pass)
**Validator:** conductor-track-validator-alt (`openai/gpt-5.6-sol`, low)
**Scope:** Phase A closeout readiness only

## Closeout Verdict

**Not ready to close.** The post-fix artifacts describe a parity selector, but the active global orchestrator cannot dispatch the M3 paired validator, and the claimed mathematically exact two-track 50/50 cycle does not follow from SHA-256 parity. This sole Stage 8 pass is exhausted; remaining material defects are blockers rather than another route-back.

## Evidence Checked

- `C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\spec.md`
- `C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\plan.md`
- `C:\development\opencode\.conductor\tracks\20260715-minimax-m3-half-routing\metadata.json`
- Both prior validation reports and `execution-log-2026-07-15.md`
- `approved-routing-map.json`, `diversity-validation.json`, `parse-validation.json`, `post-change-inventory.json`, `rollback-validation.json`, `restart-decision.json`, `runtime-validation.md`, and `final-validation.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-plan-reviewer.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator-m3.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`
- `C:\development\opencode\.conductor\tracks.md`, `tracks-ledger.md`, and `logs\pipeline-anomalies.jsonl`
- Independent frontmatter-name scan: no duplicate active `name:` value was found among 15 active user agents.
- Independent SHA-256 verification for this track ID confirmed the documented digest ending in `4`, so this individual track selects Tera. That verifies the example only, not an exact alternating cycle.

## Mismatches Found

### B-1 — Material routing defect: the paired M3 validator is not dispatchable

**Artifact:** `C:\Users\DaveWitkin\.config\opencode\agent\conductor-pipeline-orchestrator.md`

**Expected:** The active orchestrator must be permitted to invoke both identities named by the deterministic Stage 7 selector and must actually select between them.

**Actual:** The permission allowlist includes `conductor-track-validator` but does **not** include `conductor-track-validator-m3`. Its Stage 7 catalog unconditionally says to invoke `conductor-track-validator`; it contains no SHA-256 selection procedure. It also retains stale prose that diversity is preserved because the validator is `opencode-go/minimax-m3`. Therefore the skill's statement that “the orchestrator computes the parity before dispatching” is not implemented in the active orchestrator agent. Odd-parity tracks cannot follow the claimed route under current permissions.

**Impact:** The runtime mechanism is incomplete. Static frontmatter counts do not prove invocation distribution, and the principal remediation is not operational.

### B-2 — Material mathematical defect: SHA-256 parity does not guarantee an exact two-track cycle

**Artifacts:** `approved-routing-map.json`, `diversity-validation.json`, `final-validation.md`, and `SKILL.md`.

**Expected:** Exact deterministic SHA-256 last-hex parity selection and a mathematically correct 50/50 usage statement, including Stage 2 plan-reviewer, Stage 6 test-runner, and Stage 7 validator.

**Actual:** Hash parity is deterministic per track and balanced over the complete input space (and approximately balanced for a sufficiently broad, unbiased population), but it does not force consecutive or arbitrarily paired track IDs to have opposite parity. Two tracks may both hash even or both hash odd. In those cases the three checkpoints per track produce respectively 4 Tera/2 M3 or 2 Tera/4 M3, not 3/3. The artifacts qualify the claim in one location as “with one even-parity and one odd-parity track,” but repeatedly promote that conditional example to “over each/any two-track cycle exactly 50%.” That conclusion is mathematically unsupported without a persisted pairing/cycle state that guarantees one track from each bucket.

**Impact:** The reported exact 50/50 two-track acceptance result is false as written. The mechanism can support an expected/asymptotic 50/50 validator split, but not an exact every-two-track split.

### B-3 — Material compatibility/effectiveness gap: no post-restart routing smoke test

**Artifacts:** `restart-decision.json` and `runtime-validation.md`.

**Expected:** Runtime effectiveness is tested only after restart, or explicitly remains pending without claiming the routing mechanism is “genuinely operational.”

**Actual:** Restart is correctly marked required and `safe_to_test_now=false`; the smoke test is deferred. This deferral is correct. However, the post-fix Stage 7 report and final recommendation call the mechanism genuinely operational despite no post-restart resolution test and despite B-1. Metadata correctly remains `executed-deterministic-complete-runtime-pending`.

**Impact:** Deferral itself is not a defect, but closeout cannot rely on an operational-success claim. Runtime completion remains a required external follow-up after restart.

### B-4 — Audit/bookkeeping defects

- The Stage 7 anomaly appended at `2026-07-16T00:11:40Z` has eight properties (`timestamp`, `track_id`, `stage`, `subagent`, `model`, `type`, `severity`, `detail`), not the required seven-key schema used by this pipeline (`ts`, `track`, `stage`, `subagent`, `type`, `severity`, `detail`). Historical JSONL must not be rewritten, so this requires a labeled audit correction, not silent mutation.
- `approved-routing-map.json.map_hash` was not re-frozen after material remediation. The prior report correctly identified this, but it remains unresolved.
- `conductor-test-runner.md` has correct Tera Medium frontmatter but still describes itself as MiniMax M3. This is non-authoritative prose drift.

### Checks that passed

- Active agent names are unique; the new paired agent has distinct `name: conductor-track-validator-m3`.
- Tera frontmatter uses exactly `model: openai/gpt-5.6-terra` and `variant: medium`.
- No unsupported weighted/random/fallback model field was found in the inspected active agent frontmatter or routing map; the design uses fixed pins plus prose-defined selection.
- Current active M3 frontmatter pins reconcile to plan-reviewer and validator-m3; current Tera pins reconcile to test-runner and primary validator. Historical records remain classified separately in the inventory artifacts.
- Creator/reviewer and executor/test-runner/validator family pairings remain diverse for the documented GLM/Qwen executor choices.
- File-scoped rollback evidence exists for the edited runner, validator, and skill; the newly created paired validator has delete-only rollback. Recorded backup hashes reconcile in `rollback-validation.json`.
- The canonical documented Stage 5 chain remains GLM-5.2 -> GLM-5.1 -> Qwen, with an operational quota bypass note. The execution artifacts record direct authorized Qwen use. No command, report, provider result, or model-operation evidence inspected shows invocation of either GLM-5.2 or GLM-5.1 during this track; both are recorded as skipped/unavailable. This is evidence-based confirmation, not an external provider-billing audit.
- Plan tasks are 16/16 `[x]`; metadata and both indexes are synchronized to `executed-deterministic-complete-runtime-pending`; Stage 9 waiver is explicitly recorded in the execution log and is not required as a separate Phase A artifact.

## Required Fixes Before Close

1. **Deliverable/config — blocking:** Add `conductor-track-validator-m3: allow` to the active orchestrator task permission map and implement the exact SHA-256(track_id) last-hex selection in its Stage 7 dispatch instructions. Verify both even and odd fixture track IDs resolve to the intended agent identity without invoking either model.
2. **Plan/spec flaw — blocking:** Choose and document one mathematically valid contract:
   - expected/asymptotic 50/50 over SHA-256 parity, removing every claim of exact per-two-track balance; or
   - exact two-track cycles, which requires persisted cycle/pair state guaranteeing one Tera and one M3 validator selection per cycle. A bare hash parity rule cannot guarantee this.
3. **Deliverable/config — blocking before effectiveness completion:** Restart OpenCode, then run bounded smoke tests for both permitted validator identities or the narrowest supported resolution probe. Keep `runtime-pending` if restart cannot be performed; do not call GLM-5.2 or GLM-5.1.
4. **Bookkeeping-only — required:** Emit a labeled audit correction for the malformed eight-key Stage 7 anomaly and stale `map_hash`; do not rewrite historical JSONL records.
5. **Bookkeeping/doc drift — minor:** Correct the stale MiniMax narrative in `conductor-test-runner.md` and the stale validator prose in the orchestrator after the routing contract is fixed.

Because Stage 8 is capped at one extra pass, these fixes cannot be routed through another automatic re-validation in this run. They require operator/orchestrator follow-up and a new explicitly authorized validation context.

## Final Recommendation

Do not close the track: preserve its current runtime-pending status, correct the undispatchable paired route and false exact-cycle claim, then perform the deferred post-restart resolution smoke test without invoking either exhausted GLM model.

## Stage 9 Readiness

**Not ready for terminal closeout.** The existing Stage 9 waiver is valid for public documentation scope and no separate Stage 9 artifact is required in Phase A. Nevertheless, Phase A fails on execution correctness (B-1/B-2) and unresolved runtime effectiveness (B-3). The waiver does not cure those blockers.
