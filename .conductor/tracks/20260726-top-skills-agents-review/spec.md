# Spec

## Goal

Identify Dave's 20 most-used/highest-value shared skills and 10 most-used/highest-value agents across Codex and OpenCode, review every selected artifact comprehensively against current local standards, safely correct high-confidence defects, and leave an evidence-backed portfolio report plus validated local artifacts.

## Current Evidence

- Normal shared skills are real folders under `C:\Users\DaveWitkin\.opencode-lazy-vault`; `C:\Users\DaveWitkin\.codex\skills` is a parent junction to that vault and must not be edited as a separate copy.
- Always-on OpenCode skills live under `C:\Users\DaveWitkin\.config\opencode\skill`; this set should remain small.
- OpenCode session history is stored in read-only SQLite at `C:\Users\DaveWitkin\.local\share\opencode\opencode.db`. Archived sessions are valid completed work and must be included.
- OpenCode agent definitions live under `C:\Users\DaveWitkin\.config\opencode\agent`.
- The `skill-creator` checklist is mandatory for all 20 skill reviews, including scope, discovery, frontmatter, progressive disclosure, guardrails, scripts, portability, permissions, structural validation, and representative functional testing.
- Existing user changes and unrelated dirty-worktree content must be preserved.

## Requirements

- [ ] Use structured usage evidence from OpenCode session history and available Codex-local evidence; label evidence confidence and do not infer usage from filenames alone.
- [ ] Select exactly 20 skills and 10 agents using a documented, reproducible ranking method that balances observed frequency, unique-session breadth, recency, and operational importance.
- [ ] Review every selected skill against every applicable item in the `skill-creator` required checklist; record Pass, Fail, Not Applicable, or Unverified with evidence.
- [ ] Review every selected agent for activation/purpose, model and variant validity, permission least privilege, tool/skill access, bounded execution, safety, prompt clarity, output contract, overlap, and Conductor diversity constraints where applicable.
- [ ] Back up every artifact before editing. Treat lazy-vault junction topology and global unversioned agent/skill files conservatively.
- [ ] Apply only high-confidence, in-scope fixes. Do not rename, merge, archive, delete, publish, change provider credentials, change schedules, restart applications, or broaden permissions without explicit approval.
- [ ] Validate every changed skill structurally and functionally. Validate every changed agent structurally plus with a bounded representative dry-run/smoke test when safe.
- [ ] Produce a decision-ready portfolio report separating fixed defects, unresolved defects, optional improvements, unverified items, and artifacts requiring Dave's decision.
- [ ] Keep Conductor artifacts, ledgers, execution logs, validation reports, and pipeline metadata synchronized.

## Non-Requirements

- [ ] Do not review every installed skill or agent beyond the selected 20 and 10 except as needed to detect naming/activation overlap.
- [ ] Do not publish any skill to SkillShare or push/commit changes.
- [ ] Do not alter OpenCode provider keys, account routing, global schedules, plugin installation, or the Codex application runtime.
- [ ] Do not delete or archive lower-ranked skills/agents based only on low usage.
- [ ] Do not expose raw message bodies, secrets, tokens, email content, or other private session content in reports.
- [ ] Do not claim a skill or agent is confirmed from structural checks alone.

## Acceptance Criteria

- [ ] `usage-ranking.json` contains exactly 20 selected skills and 10 selected agents, source counts, scoring fields, confidence labels, and deterministic tie-breaks.
- [ ] `skill-review-matrix.md` contains one row/section per selected skill and an explicit result for every applicable `skill-creator` checklist category.
- [ ] `agent-review-matrix.md` contains one row/section per selected agent and evidence for all required agent-review categories.
- [ ] Every edited artifact has a pre-edit backup, a narrow before/after diff, and a recorded reason.
- [ ] All changed skills pass structural validation, script syntax checks when applicable, and a representative functional smoke test; failures remain explicitly unconfirmed.
- [ ] All changed agents parse correctly and pass a bounded representative dry-run/smoke test when safe; any untestable behavior is labeled unverified.
- [ ] `portfolio-review-report.md` provides the ranked lists, material findings, changes made, residual risks, and recommended next decisions without hiding unresolved Critical/Major findings.
- [ ] Independent validation confirms all non-deferred plan tasks, artifacts, reports, ledgers, and pipeline metadata agree before closeout.

