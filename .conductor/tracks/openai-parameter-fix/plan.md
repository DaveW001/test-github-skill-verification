# Plan: openai-parameter-fix

## Phase 1: Evidence Capture (Pre-Change)
- [x] Inspect current `opencode.jsonc` OpenAI provider/model settings.
- [x] Inspect recent OpenCode logs for config/provider errors.
- [x] Confirm error is real: User hit "bad parameter" errors on GPT-5.3, 5.4, 5.5 on Apr 27. Error evidence is in interactive Desktop session DB (not in headless logs).
- [x] Confirm active config precedence: global `opencode.jsonc` is primary. Project-level `.opencode/opencode.jsonc` also loads but global has provider definitions.
- [~] Baseline regression reference: Headless `opencode run` has a pre-existing "Session not found" bug preventing live API testing from CLI. Interactive Desktop is the primary runtime.

## Phase 2: Safety & Rollback Preparation
- [x] Created timestamped backup: `opencode.jsonc.backup-20260428-094622-openai-fix`
- [x] Renamed cache directory: `opencode-cache-backup-20260428-094635`
- [x] Documented rollback commands in `.conductor/tracks/openai-parameter-fix/rollback.md`

## Phase 3: Controlled Change Set 1 (Provider Package)
- [x] Added `"npm": "@ai-sdk/openai"` to `openai` provider at line 140 of `opencode.jsonc`.
- [x] No reasoning/model options modified (single-variable change).
- [x] Cache backed up (renamed) — will refresh on next OpenCode Desktop launch.

## Phase 4: Validation Gates After Change Set 1
- [x] **Gate A (Syntax): PASSED** — Brace/bracket balance verified, all structural elements present.
- [x] **Gate B (Startup): PASSED** — `opencode --version` → 1.14.25, help works, no crashes.
- [x] **Gate C (Provider Resolution): PASSED** — Debug logs show clean config load, no provider errors, all 7 plugins load. Only pre-existing error is `verify.md` frontmatter (unrelated).
- [x] **Gate D (Behavior): PASSED** — User tested in Desktop: medium, high/xhigh, and none reasoning profiles all worked.
- [x] **Gate E (Regression): PASSED** — User confirmed Google proxy and OpenRouter models still work.

## Phase 5: Decision Tree if Failures Persist
- [x] **NOT NEEDED** — All gates passed on first change set. No mitigations required.

## Phase 6: Post-Change Observability
- [ ] Monitor logs for recurrence over next 24h or next 10 OpenAI calls. (Ongoing — user to flag if issues recur.)

## Phase 7: Completion & Handoff
- [x] Update `metadata.json` phase/status.
- [x] Summarize evidence, changes, validations, and rollback state in track notes.
- [ ] Update `.conductor/tracks-ledger.md` when track is complete.
