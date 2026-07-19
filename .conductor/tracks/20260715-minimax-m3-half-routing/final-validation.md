# Final Validation Report (Post-Remediation, Closeout 2026-07-17)

## Changed files

**Active agent edited (2):**
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md` - model changed from `opencode-go/minimax-m3` to `openai/gpt-5.6-terra`, variant `medium` added (initial Stage 5 execution).
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md` - model changed from `opencode-go/minimax-m3` to `openai/gpt-5.6-terra`, variant `medium` added (remediation M-1).

**Active agent created (1):**
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator-m3.md` - new paired M3 validator for persisted strict-alternation (remediation M-1, v2 Option A).

**Pipeline documentation updated (1):**
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` - added deterministic validator alternation rule section; updated model assignment table and diversity log; preserved GLM-5.2 quota operational note and canonical fallback chain.

**Backups created (4):**
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-test-runner.md.bak-20260715-194208`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md.bak-20260715-194257`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-validator.md.bak-20260715-195909`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md.bak-20260715-195912`

## Inventory reconciliation

- Active M3 pins before remediation: 3 (plan-reviewer, test-runner, validator)
- Active M3 pins after remediation: 2 (plan-reviewer, validator-m3)
- Active Tera pins after remediation: 2 (test-runner, validator)
- Total active agents: 4 (plan-reviewer M3, test-runner Tera, validator Tera, validator-m3 M3)
- Historical M3 references: 220+ (all in .conductor artifacts, unchanged)
- Unexplained active M3 references: 0

## Tera usage ratio

- **Static agent count:** 2 Tera / 2 M3 = 50% Tera (of 4 active agents)
- **Cyclic invocation distribution:** plan-reviewer always M3, test-runner always Tera, validator alternates Tera/M3 by persisted strict-alternation counter
- **Over two consecutive Stage-7 runs:** exactly one Tera + one M3 validation (hard guarantee via `.conductor/validator-alternation.json`)
- **Method:** persisted strict alternation (NOT SHA-256 parity; SHA-256 parity was rejected as non-exact and replaced in v2 remediation)

## Routing decision

Native 50/50 weighted routing: Unsupported by verified evidence (OpenCode 1.18.1). Selected mechanism: fixed pins with paired agents and **persisted strict-alternation** invocation rule. The alternation state is stored in `C:\development\opencode\.conductor\validator-alternation.json` (last_used=tera, next=m3). Before each Stage 7 dispatch, the orchestrator reads last_used, invokes the opposite validator, then flips last_used. This guarantees exactly one Tera and one M3 validation per two consecutive Stage-7 runs.

**Note:** SHA-256(track_id) last-hex-digit parity was the initial design but was rejected in v2 remediation (2026-07-16) because it cannot guarantee an exact split on consecutive tracks. All current active routing artifacts use persisted strict alternation. Historical reports that reference SHA-256 parity are preserved unmodified as historical records.

## Independent-review diversity

- Stage 1 (OpenAI SOL) vs Stage 2 (MiniMax M3): different families. OK.
- Stage 5 (GLM) vs Stage 6 (OpenAI Tera): different families. OK.
- Stage 5 (GLM) vs Stage 7 Tera primary (OpenAI Tera): different families. OK.
- Stage 5 (GLM) vs Stage 7 M3 paired (MiniMax M3): different families. OK.
- Same-family pair count: 0.

## GLM-5.2 quota workaround

- Canonical chain preserved: `zai-coding-plan/glm-5.2` -> `zai-coding-plan/glm-5.1` -> `opencode-go/qwen3.7-plus`
- Operational note in SKILL.md: while GLM-5.2 is exhausted, Stage 5 starts with GLM-5.1, then Qwen.
- This run (Stage 5 remediation): opencode-go/qwen3.7-plus (Tier 3) directly.
- Both GLM-5.2 and GLM-5.1 tiers recorded as model-unavailable (user-reported quota exhaustion).

## Deterministic validation

| Check | Result |
|---|---|
| Parse validation (frontmatter) | PASS (4 files) |
| Post-change inventory reconciliation | PASS (0 unexplained) |
| Diversity validation | PASS (0 same-family pairs, 50% Tera) |
| Rollback validation | PASS (backups exist, hashes match) |
| Routing decision evidence | PASS |
| Persisted strict-alternation rule | PASS (alternation state file valid, 50/50 guarantee) |
| Bookkeeping sync (tracks.md, tracks-ledger.md, metadata.json) | PASS |
| Tera Medium smoke test | PASS (user-supplied evidence 2026-07-17, session ses_08f4a813cffewvxXj3YSlS0UNp) |
| MiniMax M3 smoke test | PASS (2026-07-17, session ses_08f324508ffeVw5cvmUdCr5375, cost $0.00423204 metered) |
| Stage 7 M3 alternation dispatch | PASS (2026-07-17, report validation-report-20260717-160109Z.md, alternation flipped to last_used=m3 next=tera) |

## Restart and runtime validation

- Restart required: WAS YES; restart completed 2026-07-17.
- Live Tera Medium smoke test: **PASSED** (user-supplied evidence 2026-07-17).
  - Command: `opencode run --model openai/gpt-5.6-terra --variant medium --format json "Reply with exactly: routing-ready"`
  - Output: exactly `routing-ready`, finish reason `stop`, exit success.
  - Session: `ses_08f4a813cffewvxXj3YSlS0UNp`.
  - Scope: proves explicit Tera Medium model-resolution works post-restart; does not by itself execute a Stage 7 alternation dispatch.
- Live M3 smoke test: **PASSED** (2026-07-17, session `ses_08f324508ffeVw5cvmUdCr5375`).
  - Command: `opencode run --model opencode-go/minimax-m3 --format json "Reply with exactly: routing-ready"`
  - Output: exactly `routing-ready`, finish reason `stop`, exit success.
  - Model used: `opencode-go/minimax-m3`. Cost: $0.00423204 (metered; not mixed with subscription totals).
- Live alternation dispatch: **EXECUTED** (2026-07-17). Stage 7 task dispatch using `conductor-track-validator-m3` completed successfully. Report: `validation-report-20260717-160109Z.md`. Verdict: Close with minor follow-ups (no blockers). Alternation state flipped from `last_used=tera, next=m3` to `last_used=m3, next=tera`. No GLM models were invoked.
- Deterministic validation: ALL PASSED.
- Pre-existing `Session not found` block: RESOLVED.

## Rollback readiness

- Backup exists for every changed file
- Pre-edit SHA-256 hashes recorded in baseline-manifest.json and rollback-validation.json
- Per-file restore commands generated in rollback-validation.json
- New file (conductor-track-validator-m3.md) has delete-only rollback (no prior state)
- No bulk restore used; file-scoped only

## Anomalies and deferrals

1. model-fallback (warn): Tier 1 (GLM-5.2) and Tier 2 (GLM-5.1) skipped due to user-reported Z.AI quota exhaustion. Run starts at Tier 3 (Qwen). Canonical chain unchanged.
2. 50%-target material mismatch (remediated): Initial execution achieved 33% Tera (1/3). Remediation M-1 converted validator to Tera primary with paired M3 validator and persisted strict-alternation rule, achieving exactly 50% Tera over two consecutive runs.
3. Runtime smoke test (fully resolved 2026-07-17): Both Tera Medium (session `ses_08f4a813cffewvxXj3YSlS0UNp`) and MiniMax M3 (session `ses_08f324508ffeVw5cvmUdCr5375`) sides passed. Live alternation dispatch via `conductor-track-validator-m3` executed successfully (report `validation-report-20260717-160109Z.md`). Alternation state flipped to `last_used=m3, next=tera`.

## Stage 9 documentation waiver

This is a bookkeeping track with no public API surface changes. The SKILL.md alternation rule section is a non-contractual sync. Stage 9 documentation is waived (no public documentation change required).

---

## V2 remediation addendum (operator-authorized, 2026-07-16, Option A)

Resolves Stage 8 blockers B-1, B-2, and B-4:

- **B-1 RESOLVED:** Orchestrator now permits conductor-track-validator-m3 in its task allowlist and its Stage 7 catalog line implements the persisted-alternation selection (read last_used -> dispatch opposite -> flip).
- **B-2 RESOLVED (Option A):** Probabilistic SHA-256 parity replaced by persisted strict-alternation counter .conductor/validator-alternation.json. Guarantees EXACT 50/50 (one Tera + one M3 per two consecutive validation runs).
- **B-4 RESOLVED:** Labeled 7-key audit-correction anomaly appended; no historical JSONL rewritten. approved-routing-map.json map_hash re-frozen = 1B58BC1E1D3F238FB0CD49AF364E89E8EE8AB3F41E961F039163239AF19E5E88.
- Doc drift fixed in conductor-test-runner.md.

### Deterministic verification (all pass)
- Orchestrator allowlist contains conductor-track-validator-m3: allow - PASS
- Orchestrator Stage 7 line implements alternation dispatch - PASS
- Alternation state file valid (last_used=tera, next=m3) - PASS
- Zero SHA-256(track_id) residue across orchestrator, SKILL.md, both validators - PASS
- SKILL.md alternation heading present, parity heading removed - PASS
- Validator frontmatter: validator=Tera medium, validator-m3=M3 - PASS
- All track artifacts valid JSON - PASS
- Active agent reconciliation: plan-reviewer M3, test-runner Tera, validator Tera, validator-m3 M3 - PASS

---

## Closeout addendum (2026-07-17, Qwen bookkeeping executor)

- **B-3 RESOLVED (Tera side):** User-supplied post-restart evidence confirms `openai/gpt-5.6-terra` with `--variant medium` resolves and completes normally. Session `ses_08f4a813cffewvxXj3YSlS0UNp`. Output exactly `routing-ready`, finish reason `stop`, exit success. Pre-existing `Session not found` block is resolved.
- **M3 smoke + Stage 7 dispatch (2026-07-17):** Live M3 smoke test passed (session `ses_08f324508ffeVw5cvmUdCr5375`, output exactly `routing-ready`, finish reason `stop`, model `opencode-go/minimax-m3`, cost $0.00423204 metered). Live Stage 7 dispatch using `conductor-track-validator-m3` executed successfully (report `validation-report-20260717-160109Z.md`, verdict: Close with minor follow-ups / no blockers). No GLM models were invoked. Alternation state flipped from `last_used=tera, next=m3` to `last_used=m3, next=tera`.
- **Track status:** Moved to `closed`. All closeout conditions met for a bookkeeping track.
- **Stale SHA-256 parity assertions:** Removed from all current active routing artifacts (metadata.json, final-validation.md, tracks.md, tracks-ledger.md). Historical reports (execution-log-2026-07-15.md, validation-report-20260716-001140Z.md, validation-blockers-20260716-001519Z.md) preserved unmodified as historical records.

