# Runtime Validation

## Restart state

Restart required: WAS YES (pre-2026-07-17). OpenCode caches agent definitions at startup, so the model/variant pin changes in conductor-test-runner.md and conductor-track-validator.md required a restart to take effect.

**Post-restart state (2026-07-17):** Restart completed. OpenCode successfully resolves the Tera Medium pin.

## Tera Medium result (post-restart, user-supplied evidence)

**Command:**
```
opencode run --model openai/gpt-5.6-terra --variant medium --format json "Reply with exactly: routing-ready"
```

**Result:**
- JSON event stream emitted text exactly `routing-ready`
- Finish reason: `stop`
- Exit: success
- Session ID: `ses_08f4a813cffewvxXj3YSlS0UNp`
- No model/variant resolution error

**Verdict:** PASS. The explicit `openai/gpt-5.6-terra` model with `--variant medium` resolves correctly and runs to normal completion post-restart. The pre-existing `Session not found` runtime block is resolved.

## Scope statement (updated 2026-07-17 after M3 smoke + Stage 7 dispatch)

Both smoke tests now prove explicit model-resolution works for both Tera Medium and MiniMax M3 after restart. A real Stage 7 task dispatch using `conductor-track-validator-m3` was executed on 2026-07-17, confirming the alternation state file is read and the M3 validator dispatches successfully. The alternation state has been flipped from `last_used=tera, next=m3` to `last_used=m3, next=tera` by the coordinator after the successful dispatch.

What this evidence establishes:
- The OpenAI GPT-5.6 Tera medium variant is reachable and completes normally (session `ses_08f4a813cffewvxXj3YSlS0UNp`).
- The MiniMax M3 model is reachable and completes normally (session `ses_08f324508ffeVw5cvmUdCr5375`).
- The post-restart runtime is healthy (no `Session not found`).
- The Tera Medium pin in `conductor-track-validator.md` and `conductor-test-runner.md` is operationally valid.
- The M3 pin in `conductor-track-validator-m3.md` and `conductor-plan-reviewer.md` is operationally valid.
- A live Stage 7 dispatch using `conductor-track-validator-m3` succeeded (report: `validation-report-20260717-160109Z.md`).
- The alternation state file was correctly flipped after the M3 dispatch.

## MiniMax M3 result (2026-07-17, post-restart)

**Command:**
```
opencode run --model opencode-go/minimax-m3 --format json "Reply with exactly: routing-ready"
```

**Result:**
- JSON event stream emitted text exactly `routing-ready`
- Finish reason: `stop`
- Exit: success
- Session ID: `ses_08f324508ffeVw5cvmUdCr5375`
- Model used: `opencode-go/minimax-m3`
- Cost: $0.00423204 (metered; not mixed with subscription totals)
- No model resolution error

**Verdict:** PASS. The explicit `opencode-go/minimax-m3` model resolves correctly and runs to normal completion. The M3 pin in `conductor-track-validator-m3.md` and `conductor-plan-reviewer.md` is operationally valid.

## Selected model evidence

Post-restart Tera Medium smoke test passed (session `ses_08f4a813cffewvxXj3YSlS0UNp`). Post-restart MiniMax M3 smoke test passed (session `ses_08f324508ffeVw5cvmUdCr5375`). Live Stage 7 dispatch via `conductor-track-validator-m3` succeeded (report `validation-report-20260717-160109Z.md`). Alternation state flipped to `last_used=m3, next=tera`. Deterministic validation (parse, inventory, diversity, rollback, alternation state file, bookkeeping sync) all passed.

## Verdict (updated 2026-07-17 after M3 smoke + Stage 7 dispatch)

runtime validation: PASSED for both explicit Tera Medium resolution (session `ses_08f4a813cffewvxXj3YSlS0UNp`) and explicit MiniMax M3 resolution (session `ses_08f324508ffeVw5cvmUdCr5375`). Pre-existing `Session not found` block resolved. Stage 8 blocker B-3 is fully resolved for both Tera and M3 sides. Live alternation dispatch via `conductor-track-validator-m3` succeeded (report `validation-report-20260717-160109Z.md`). Alternation state flipped to `last_used=m3, next=tera`.

## Post-restart test commands (for future reference)

1. `opencode run --model openai/gpt-5.6-terra --variant medium --format json "Reply with exactly: routing-ready"` - PASSED 2026-07-17 (session `ses_08f4a813cffewvxXj3YSlS0UNp`)
2. `opencode run --model opencode-go/minimax-m3 --format json "Reply with exactly: routing-ready"` - PASSED 2026-07-17 (session `ses_08f324508ffeVw5cvmUdCr5375`, cost $0.00423204 metered)
3. Stage 7 dispatch via `conductor-track-validator-m3` - PASSED 2026-07-17 (report `validation-report-20260717-160109Z.md`); alternation state flipped to `last_used=m3, next=tera`

