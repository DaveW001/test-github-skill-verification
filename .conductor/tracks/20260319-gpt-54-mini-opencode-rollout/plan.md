# Plan: Enable GPT-5.4 Mini Across OpenCode CLI and Desktop

**Track ID**: 20260319-gpt-54-mini-opencode-rollout  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-03-19  
**Status**: In Progress

---

## Phase 1: Baseline and Safety

- [ ] Back up `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` with timestamped copy.
- [ ] Record baseline runtime state:
  - `opencode --version`
  - `opencode debug config` (redacted capture)
- [ ] Record current OpenAI path assumptions:
  - OAuth plugin active (`oc-chatgpt-multi-auth@5.4.4`)
  - no OpenAI `baseURL` proxy in active `openai` provider
  - Google proxy remains independent and unchanged

## Phase 2: Path Decision (Hard Gate)

- [ ] Confirm required behavior for `gpt-5.4-mini`:
  - exact API model ID required, or
  - acceptable to use OAuth-normalized equivalent
- [ ] If exact API model required, approve dual-lane architecture (OAuth + API/proxy lane).
- [ ] If OAuth-only lane selected, document limitation that true mini may be remapped.

## Phase 3: Configuration Design

- [ ] Define provider/model naming convention to prevent collisions:
  - retain existing OAuth lane (`openai/...`) for Codex
  - add distinct API lane prefix for exact model IDs
- [ ] Draft config delta for `gpt-5.4-mini` model entry in API lane.
- [ ] Draft optional proxy routing block (OpenAI-compatible `baseURL`) if proxy is used.
- [ ] Keep default model unchanged initially to de-risk rollout.

## Phase 4: Implementation (Build Agent)

- [ ] Apply approved config changes to global OpenCode config.
- [ ] Preserve existing plugin order and existing non-OpenAI providers.
- [ ] Restart OpenCode CLI session.
- [ ] Restart OpenCode Desktop session to force config reload.

## Phase 5: Validation Matrix

- [ ] CLI functional test on new model path.
- [ ] Desktop functional test on new model path.
- [ ] Existing Codex/OAuth regression test (`openai/gpt-5.3-codex`).
- [ ] Verify runtime outbound model identity equals `gpt-5.4-mini` (no silent remap).
- [ ] Verify model appears in picker/list where expected (`/models` and Desktop model selector behavior).

## Phase 6: Rollback and Handover

- [ ] Document one-command rollback to pre-change config backup.
- [ ] Document operator runbook:
  - how to select mini in CLI and Desktop
  - how to distinguish OAuth vs API lane models
  - how to troubleshoot missing model in picker
- [ ] Capture post-change evidence in track artifacts and close track.

---

## Acceptance Checklist

- [ ] `gpt-5.4-mini` reachable from both CLI and Desktop.
- [ ] No disruption to existing Codex OAuth workflow.
- [ ] OpenAI connection mode is explicitly documented (OAuth, direct API, or proxy).
- [ ] Rollback validated.
