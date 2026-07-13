---
name: skill-test-harness
description: Validate and confirm skills structurally and functionally. Use when creating or updating a skill, running a confirmed skill smoke test, checking frontmatter/structure/Markdown links/referenced files, syntax-checking included PowerShell or Python scripts, or generating a functional test prompt for a Task sub-agent.
---

# Skill Test Harness

This skill is the canonical validation layer for OpenCode skills. A skill is confirmed only when structural checks, script checks when applicable, and at least one representative functional smoke test pass.

## When to use

Use this skill when:

- You are creating or updating a skill and need to confirm it.
- You need to verify a skill's structure, frontmatter, links, and referenced files.
- You need to syntax-check included PowerShell (`.ps1`) or Python (`.py`) scripts.
- You need a deterministic `RESULT: PASS` / `RESULT: FAIL` smoke-test report.
- You need a FUNCTIONAL PROMPT TEMPLATE to hand to a Task sub-agent for functional confirmation.

## Instructions

### 1. Run the structural and script harness

Run the smoke-test harness against the absolute skill path:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1" -SkillPath "<absolute-skill-path>" -PrintFunctionalPrompt
```

The harness prints a `SKILL SMOKE TEST SUMMARY` with `STRUCTURE:`, `REFERENCES:`, and `SCRIPT SYNTAX:` sections plus a `FUNCTIONAL PROMPT TEMPLATE`. It exits `0` when there are no failures (`RESULT: PASS`) and `1` otherwise (`RESULT: FAIL`).

### 2. Functional confirmation (required for a confirmed skill)

A confirmed skill requires more than structural validation. Copy the printed `FUNCTIONAL PROMPT TEMPLATE` into a Task sub-agent and have it execute one representative, offline skill test case using only the skill instructions. The sub-agent must return either `FUNCTIONAL_SMOKE_TEST_PASSED` or `FUNCTIONAL_SMOKE_TEST_FAILED` with explicit reasons, and must never call real APIs or expose tokens.

Save the sub-agent report alongside the skill or in the owning track. A skill that passes structure but not function is structurally valid but functionally unconfirmed.

### 3. Test-case convention

Every new skill MUST include at least one functional test case in `tests\` or explicitly document that it is structurally valid but functionally unconfirmed. Use the canonical template at `templates\test-case.template.md`.

## References

- Detailed behavior, output schema, and limitations: [reference.md](reference.md)
- Functional test-case template: [templates/test-case.template.md](templates/test-case.template.md)

## Limitations

- The harness makes no external API calls and never prints, stores, or inspects token values.
- The harness prints the functional prompt; launching the Task sub-agent is the orchestrator's responsibility.
