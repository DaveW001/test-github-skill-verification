# Retrospective: Conductor Pipeline `write`-Permission Gap

**Date:** 2026-07-03
**Scope (approved):** B - Medium. The `write`-tool permission gap across the entire conductor-pipeline agent fleet + global config, and a durable permission model so no future pipeline run pauses on file creation.
**Triggering session:** `2026-07-02` Conductor pipeline run, track `20260702-slack-skill-validation` (orchestrator `ses_0e1c3a3f1ffeChLaO12f5RlWZD`, executor `glm-5.2`).
**Evidence base:**
- `C:\development\opencode\.conductor\tracks\20260702-slack-skill-validation\` (spec.md, plan.md, execution-log, validation-report, metadata.json)
- `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` (permission block)
- `C:\Users\DaveWitkin\.config\opencode\agent\conductor-*.md` (subagent frontmatter)
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\SKILL.md` + `references\threshold-policy.md`
- Prior retro: `C:\development\opencode\.conductor\docs\conductor-pipeline-run-retro-2026-06-30.md`

---

## Executive Summary

A mid-run permission prompt disrupted the `2026-07-02` slack-skill-validation pipeline. Root cause: **the `write` tool (create/overwrite a file) is authorized *nowhere*** - not in the global `opencode.jsonc` permission block and not in any conductor subagent frontmatter. Every conductor agent authorizes `edit` (modify existing) but none authorize `write` (create new). Because the config sets no `mode`/`yolo` override, unlisted tools fall to the opencode default = **ASK**.

Pipeline stages routinely create new files (spec.md, plan.md, execution-log, validation-report, skill files, backups). Each creation invokes `write` and triggers a human prompt. The defect was *hidden* during this run because the executor's file tools were broken (`Bun is not defined`), forcing it onto the allowed `bash` tool (PowerShell `Set-Content`) - which accidentally bypassed the `write` gate. Stages using native file tools (Stage 1 plan-creator, Stage 5 validator) were not so lucky.

**Key realization:** the `write` gate provides negligible real safety because `bash: allow` already lets any agent write files via PowerShell. The genuine guardrail is the destructive-bash `ask` rules (`rm *`, `git reset*`, `git clean*`, `del *`). The missing `write: allow` is pure friction.

---

## What Went Well

1. **The deliverable succeeded.** The `20260702-slack-skill-validation` track completed 15/15 tasks, validated PASS, no secrets exposed, no deviations logged. The permission prompt was friction, not failure.
2. **The pipeline's diversity model and stage isolation held.** Plan creation (gpt-5.5), review (minimax-m3), execution (glm-5.2), and validation (minimax-m3) ran on distinct models with intact diversity gates.
3. **Forensic trail was complete enough.** Track artifacts (spec/plan/execution-log/validation-report/metadata) plus the agent frontmatter made the root cause determinable from *structure* even though session-log archaeology was inconclusive.
4. **The shell-first fallback (codified in the 2026-06-30 retro) kept the executor moving** when native file tools broke - proving that prior mitigation works as intended.
5. **The config's destructive-bash `ask` rules are correctly scoped** (`rm *`, `git reset*`, `git clean*`, `del *`) - the real safety boundary is intact.

## What Could Be Improved

1. **`write` is authorized nowhere** - the core defect. Every file-creating stage is one `write` call away from a prompt.
2. **`edit` and `write` are conflated in the permission model.** All conductor agents grant `edit` (modify existing file) but not `write` (create new file). The two are distinct opencode tools, and "I can edit" does not imply "I can create." This asymmetry is easy to overlook.
3. **No `mode`/`yolo` baseline in `opencode.jsonc`.** Without a top-level permission mode, every unlisted tool defaults to ASK, so any future tool addition silently becomes a prompt source.
4. **A prior mitigation masked the bug.** The 2026-06-30 retro codified the shell-first workaround for `Bun is not defined`, which accidentally routed agents around the `write` gate (bash is allowed). The permission gap survived undetected because the workaround hid it.
5. **Log archaeology cannot attribute permission prompts.** Every DCP context snapshot embeds the full system prompt + all agent definitions, so keyword searches for "permission/write/edit" match ~all 417 session logs (noise). There is no dedicated permission-event log to identify *which* subagent actually prompted.
6. **Read-only agents must still create files.** The Stage 5 validator is `edit: deny` (read-only by design) yet must emit `validation-report-<ts>.md` - an inherent contradiction unless it writes via `bash` or is granted `write`.

## What To Do Differently Next Time

1. **Add `write: allow` globally** to `opencode.jsonc` `permission`. Rationale: marginal security cost is ~zero because `bash: allow` already grants equivalent file-write power (`Set-Content`, redirection, `Out-File`). Friction goes to zero; the real safety net (destructive-bash `ask`) is untouched.
2. **Alternatively/additionally, grant `write: allow` per conductor agent** that creates files (plan-creator, executor tiers, orchestrator, validator). This is more surgical but higher-maintenance.
3. **Keep `edit: deny` on the validator** to preserve its read-only *modification* posture, but grant `write: allow` so it can emit its report - the write/edit split makes this expressible.
4. **Add a top-level permission note** documenting that the meaningful guardrail is the destructive-bash rules, not the write/edit distinction.
5. **When a workaround is codified, audit for the *independent* defect it masks.** The shell-first fallback should have triggered a "what else does routing around file-tools hide?" question.

## Systemic Issues

1. **Latent config defects survive when mitigations mask them.** The 2026-06-30 retro solved the symptom (`Bun is not defined`) without checking whether the *permission model itself* was sound for the native path. Retros should include a "what does this workaround conceal?" checklist item.
2. **No dedicated permission/authorization event log.** OpenCode prompts are not recorded in a queryable, prompt-attributing store. This makes incident attribution depend on structural inference rather than evidence. (Cross-references the broader "no per-agent execution timeout / no orchestrator watchdog" gap already noted in `threshold-policy.md`.)
3. **Tool-list asymmetry is error-prone.** Granting `edit` but not `write` is a subtle, repeatable mistake. A config linter or a documented permission *baseline set* (read+write+edit+bash together) would prevent it.
4. **Two failure layers compound.** When the file-tool layer (Bun) is down AND the permission layer is misconfigured, behavior is inconsistent across stages (some use bash, some use native tools) - so a single pipeline run can both dodge and hit the same prompt.

## Lessons Learned

1. **`edit` != `write` in opencode.** `write` creates/overwrites; `edit` modifies existing via string replacement. Permission rules must list both independently.
2. **`bash: allow` is a file-write superpermission.** Any agent that can run bash can write files. Therefore a missing `write: allow` is not a security boundary - it is friction. The destructive-command `ask` rules are where real safety lives.
3. **The shell-first fallback is a *resilience* tool, not a *correctness* tool.** It kept the run alive but it also hid the permission gap. Don't let a workaround substitute for fixing the native path.
4. **Structural analysis beat log archaeology.** The root cause was provable from the permission config + agent frontmatter; the session logs were uninformative for this class of incident.
5. **Retros must ask "what else is broken in the same neighborhood."** The prior retro fixed Bun-resilience; a one-line "does the native write path have permission?" check would have caught this months earlier.

## Codify / Reuse

**Knowledge artifacts (this retro):**
- This document: `.conductor\docs\conductor-pipeline-write-permission-retro-2026-07-02.md`

**Recommended codified changes (scaffolded as Conductor track `20260703-write-permission-fix`):**
1. **Config fix (primary):** Add `"write": "allow"` to the global `opencode.jsonc` permission block. Marginal risk ~0 given existing `bash: allow`.
2. **Agent hardening (defense in depth):** Add `write: allow` to conductor-plan-creator, conductor-track-executor (+glm51/qwen tiers), conductor-track-validator, conductor-pipeline-orchestrator frontmatter. Keep validator `edit: deny`.
3. **Skill doc update:** Add a "Permission model" subsection to `conductor-pipeline\SKILL.md` (or `references\threshold-policy.md`) stating: native file-creating stages require `write`; the meaningful guardrail is destructive-bash `ask` rules; `edit` and `write` are distinct and both must be granted.
4. **AGENTS.md / agent-development-standards note:** Add a permission-baseline checklist: "When defining an agent that creates files, grant both `write` and `edit`; verify `write` is in the global permission block or the agent frontmatter."
5. **Retro-process update:** Add "what does this workaround conceal?" to the standard retro question set so future mitigations don't mask independent defects.

**Reuse for future AI/human users:**
- Future agent authors: copy the permission baseline (`read`+`write`+`edit`+`bash` allowed, destructive-bash `ask`) instead of hand-listing tools.
- Future retro conductors: include the "workaround-masking" check (lesson 3 + systemic issue 1).
- Incident responders: for permission-prompt class issues, start from config+frontmatter structure, not session logs.
