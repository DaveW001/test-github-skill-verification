# Stage 7 Validator Dispatch Deviation

- Timestamp: `2026-07-27T12:24:37Z`
- Validator: `conductor-track-validator-m3`
- Outcome: the OpenCode process exceeded the 480-second contract and remained
  live after the interrupted parent turn.
- Containment: only the exact owned process tree was terminated.
- Alternation: unchanged at `last_used=luna`; the failed M3 attempt was not
  counted as a successful dispatch.
- Resume route: independent read-only closeout validation through a bounded
  Codex subagent, followed by the normal Stage 7 evidence and verifier checks.
