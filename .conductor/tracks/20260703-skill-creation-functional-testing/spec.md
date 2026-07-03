# Spec: Skill Creation Functional Testing Harness

## Goal / Outcome
Create a sustainable, reusable, first-class `skill-test-harness` OpenCode skill and Conductor guidance so newly created skills are not merely structurally valid, but **confirmed** by structural checks, script checks, and at least one recorded functional smoke test.

## Problem Statement
The Slack skill creation workflow proved that our current validation can declare a skill complete after checking frontmatter, file existence, links, and documentation cross-references, without proving the skill works when its instructions are followed. That is not sufficient for user trust. The skill-writer workflow also became a single point of risk: earlier edits damaged its Markdown formatting, and the base Conductor track template does not contain the same task-authoring quality standards as the Conductor pipeline Stage 1 prompt.

## Architecture Decision
Create a **first-class lazy-vault skill** instead of a hidden utility directory:

`C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\`

This location is discoverable, reusable, and maintainable. The skill owns:
- `SKILL.md` - when/how to run confirmed-skill validation.
- `scripts\skill-smoke-test.ps1` - reusable structural/script checker and functional-prompt generator.
- `reference.md` - detailed output schema, limitations, and integration details.
- `templates\test-case.template.md` - canonical functional test case template.

## Requirements
- The harness must validate structure: `SKILL.md` exists, frontmatter fences exist, `name` matches the directory slug, `description` exists and is under 1024 characters, local Markdown links resolve, and local referenced files with known extensions resolve.
- The harness must syntax-check included `.ps1` scripts with `PSParser` and `.py` scripts with Python `ast.parse` when Python is available.
- The harness must emit deterministic `PASS`/`FAIL` output and a machine-readable summary line.
- The harness must print a `FUNCTIONAL PROMPT TEMPLATE` for Task-tool sub-agent validation when requested.
- The Conductor plan must require an actual sub-agent functional smoke test report, not just a printed prompt.
- Every new skill must include at least one functional test case under `tests\`, or explicitly document that it is structurally valid but functionally unconfirmed.
- `skill-writer\reference.md` must be repaired and updated to point to the first-class `skill-test-harness` skill.
- `conductor-pipeline\references\skill-creation-testing.md` must document how skill-creation tracks add the harness plus sub-agent smoke-test gate.
- `conductor\references\templates\track-plan.template.md` must gain task-authoring standards: atomic tasks, exact paths, explicit commands, authoritative acceptance checks, diagnostic checks, error recovery, body-content verification, and idempotency.

## Non-Requirements
- Do not call real external APIs, Slack, ClickUp, Microsoft Graph, browser automation, or any production system from the harness.
- Do not store, print, or inspect token values.
- Do not fully automate Task-tool invocation from PowerShell; the orchestrator is responsible for launching the sub-agent with the printed prompt.
- Do not modify OpenCode runtime code or Conductor pipeline subagent code in this track; document the integration and update references/templates only.

## Definition of Done
- `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\SKILL.md` exists with valid frontmatter and clear activation guidance.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1` exists, parses, and implements structural checks, script syntax checks, deterministic summary output, and functional-prompt generation.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\reference.md` and `templates\test-case.template.md` document the confirmed-skill standard and test-case convention.
- `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-writer\reference.md` is repaired and references the harness as canonical Step 10 validation.
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\skill-creation-testing.md` documents optional Conductor pipeline integration.
- `C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md` includes the missing task-authoring standards.
- The harness is run against `C:\Users\DaveWitkin\.opencode-lazy-vault\slack-send-message`.
- A Task sub-agent functional smoke-test report is created under this track and contains either `FUNCTIONAL_SMOKE_TEST_PASSED` or `FUNCTIONAL_SMOKE_TEST_FAILED` with explicit reasons.
- Execution log, validation report, metadata, `tracks.md`, and `tracks-ledger.md` are synchronized.

## Target Files
- Create: `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\SKILL.md`
- Create: `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1`
- Create: `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\reference.md`
- Create: `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\templates\test-case.template.md`
- Modify: `C:\Users\DaveWitkin\.opencode-lazy-vault\skill-writer\reference.md`
- Create/update: `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\skill-creation-testing.md`
- Modify: `C:\Users\DaveWitkin\.config\opencode\skill\conductor\references\templates\track-plan.template.md`
- Create during execution: `C:\development\opencode\.conductor\tracks\20260703-skill-creation-functional-testing\functional-test-report-2026-07-03.md`

## Acceptance Summary
The final validation must prove: (1) structural harness checks pass or fail with explicit reasons, (2) script syntax checks are actually run, (3) at least one representative sub-agent functional smoke test report exists, and (4) the base Conductor templates now expose the same task-authoring quality bar as the Conductor pipeline Stage 1 prompt.