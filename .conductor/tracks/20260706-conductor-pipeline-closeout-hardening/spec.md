# Spec: Conductor Pipeline Closeout Hardening

**Track ID**: `20260706-conductor-pipeline-closeout-hardening`  
**Created**: 2026-07-06  
**Author**: 01-Planner  
**Status**: planning-ready  
**Track type**: bookkeeping  

---

## 1. Goal / Outcome

Turn the still-valid recommendations from the email-triage pipeline peer review into durable Conductor/OpenCode process improvements, without changing application production code in this track.

The intended outcome is a hardened Conductor pipeline that:

1. Refuses terminal success unless Stage 9 and closeout bookkeeping are synchronized.
2. Uses correct Stage 5 terminology in all fallback executor agents.
3. Has an explicit audit-correction convention for validation-discovered reporting mismatches.
4. Requires post-documentation validation or an explicit waiver when Stage 9 documents semantic/runtime behavior.
5. Treats `Bun is not defined` as a known platform/runtime issue with a first-class diagnostic/fallback path rather than a vague “fix Bun” task.
6. Captures the residual email-triage PSParser/mojibake cleanup as a separate, auditable follow-up track if parser cleanliness matters.

## 2. Background / Evidence

The peer-review checklist at `C:\development\opencode\.conductor\reviews\20260706-email-triage-pipeline-peer-review-checklist.md` concluded that the email-triage deliverable and first full nine-stage run are acceptable, but left process follow-ups.

Current evidence already gathered:

- The full email-triage track eventually completed Stage 9 and synchronized `metadata.json` / `.conductor\tracks.md`.
- Fallback executor agents still contain stale Stage 4 wording:
  - `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md`
  - `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md`
- Canonical stage prompts already use Stage 4 for test writing and Stage 5 for execution:
  - `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`
- GitHub issue evidence for the Bun-family runtime problem exists at `https://github.com/anomalyco/opencode/issues/25880` (`Desktop v1.14.39: Bun-target plugins fail to load (Node.js sidecar lacks Bun APIs)`). Exact `gh issue list --repo opencode-ai/opencode --search '"Bun is not defined"'` returned no matches, but `gh issue view 25880 --repo anomalyco/opencode` and web search found the upstream Desktop sidecar Bun/Node regression issue.
- Local environment evidence: native file tools in this session returned `Bun is not defined`; the global AGENTS.md already contains a PowerShell-first fallback protocol.

## 3. Requirements

- [ ] Add a terminal closeout gate to the Conductor pipeline instructions/checklists that machine-checks Stage 9 artifact presence or documented skip, metadata stage/status, track index row, ledger row where present, and required follow-ups before final success.
- [ ] Correct stale Stage 4/Stage 5 wording in fallback executor agent configs so fallback execution is consistently Stage 5.
- [ ] Add an audit-correction artifact convention for validation-discovered reporting mismatches, such as `audit-correction-<timestamp>.md`, with required fields and routing rules.
- [ ] Add a post-documentation validation rule for Stage 9 semantic/runtime docs: rerun the relevant validation/test command and emit `post-doc-validation-<timestamp>.md`, or write a waiver with rationale.
- [ ] First-class the `Bun is not defined` failure mode as a diagnostic and fallback recommendation, not as an assumed local fix.
- [ ] Create or explicitly defer a separate email-triage Conductor track for the residual PSParser/mojibake cleanup.
- [ ] Keep this track as bookkeeping/config/documentation scope; no application production-code edits belong here.

## 4. Non-Requirements / Out of Scope

- [ ] Do not edit email-triage production scripts in this track.
- [ ] Do not attempt to patch OpenCode core runtime or Desktop sidecar internals in this track.
- [ ] Do not add a new automated binary/tool to replace native file tools unless a later implementation track proves it is safe.
- [ ] Do not force ADR/API-reference conventions on repositories that do not use ADR/API docs.
- [ ] Do not rerun the full email-triage analysis; use existing artifacts unless a specific plan task requires a targeted check.

## 5. Files Likely Affected

### Global OpenCode / Conductor config and docs

- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-glm51.md`
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-track-executor-qwen.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\stage-prompts.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\threshold-policy.md`
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\artifact-output-format.md` (if the audit-correction artifact convention belongs there after inspection)
- `C:\Users\DaveWitkin\.config\opencode\docs\troubleshooting\tool-failure-bun-undefined.md` or the existing equivalent path if present
- `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` only if the fallback protocol needs a short cross-reference update

### Repo-local Conductor artifacts

- `C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\spec.md`
- `C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\plan.md`
- `C:\development\opencode\.conductor\tracks\20260706-conductor-pipeline-closeout-hardening\metadata.json`
- `C:\development\opencode\.conductor\tracks.md`
- `C:\development\opencode\.conductor\tracks-ledger.md`

### Possible cross-repo planning-only artifact

- `C:\development\email-triage\.conductor\tracks\<new-psparser-track>\spec.md`
- `C:\development\email-triage\.conductor\tracks\<new-psparser-track>\plan.md`
- `C:\development\email-triage\.conductor\tracks\<new-psparser-track>\metadata.json`

## 6. Acceptance Criteria

- [ ] Closeout gate text exists and states terminal success is blocked unless Stage 9 docs/skips, metadata, track index, ledger behavior, and required follow-ups are synchronized.
- [ ] Fallback executor agents no longer say execution is Stage 4 or instruct agents to load a Stage 4 execution prompt; they reference Stage 5 execution.
- [ ] Audit-correction convention is documented with required artifact name, when to create it, required body fields, and how it interacts with anomaly logs.
- [ ] Stage 9 instructions require post-doc validation artifact or waiver whenever docs describe semantic/runtime behavior.
- [ ] Bun issue documentation links to `https://github.com/anomalyco/opencode/issues/25880`, states local workaround limits, and preserves the current PowerShell-first fallback protocol.
- [ ] The PSParser/mojibake residual is either represented by a new email-triage Conductor track or explicitly deferred in this track’s execution log with rationale.
- [ ] The final validation/handover confirms all modified artifacts exist and that OpenCode restart is required for changed global agents/skills to take effect.

## 7. Risks and Mitigations

1. **Over-fitting pipeline rules to one email-triage run.** Mitigation: phrase closeout gates generically and use artifact presence/status checks that apply to any code or bookkeeping track.
2. **Creating impossible Bun “fix” expectations.** Mitigation: distinguish upstream Desktop/runtime issue from local fallback documentation; treat code patches as out of scope unless a later technical track proves them.
3. **Mixing OpenCode pipeline hardening with email-triage production cleanup.** Mitigation: keep this track bookkeeping-only and create a separate email-triage track for parser/mojibake cleanup if needed.

## 8. Definition of Done

- This Conductor track has synchronized `spec.md`, `plan.md`, `metadata.json`, `tracks.md`, and `tracks-ledger.md` entries.
- All implementation tasks in `plan.md` are written with exact paths, commands, recovery guidance, and one authoritative acceptance check each.
- The track is ready for a simplified bookkeeping pipeline: Stage 1 plan already completed manually, then plan review -> execution -> validation -> documentation.
