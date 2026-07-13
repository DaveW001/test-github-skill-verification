# Skill Functional Test Case

Use this template to record at least one representative functional test case for every new skill. Fill in the sections below and save the result under the skill's `tests\` directory (for example `tests\<scenario>.md`).

Every new skill MUST include at least one functional test case in tests/ or explicitly document that it is structurally valid but functionally unconfirmed.

## Skill Under Test

- Skill name: `<skill-name>`
- Skill path: `<absolute path to the skill directory>`
- Skill version / commit: `<optional>`
- Harness run (structural + script): `RESULT: PASS | FAIL` (attach or reference the `SKILL SMOKE TEST SUMMARY`)

## Representative User Request

State a single, realistic user request that should activate and exercise this skill.

> Example request: <one sentence a user would actually say>

Context / inputs available to the sub-agent (offline and safe): <list any sample files, fixtures, or simulated data>

## Expected Behavior

Describe what a correct skill-following run produces. Be specific about output type, format, and any decision points.

- Expected output type / format: <e.g., a JSON payload, a plan, a file path>
- Expected steps the skill instructs: <ordered list>
- Acceptable variations: <what is OK to differ>

## Forbidden Actions

List actions the sub-agent MUST NOT take during this test (enforced offline).

- No real external API calls, webhooks, or production systems.
- No sending of real messages, emails, tickets, or other side effects.
- No reading, printing, exposing, or transmitting tokens, keys, or credentials.
- No mutating production data or shared state.
- <add skill-specific forbidden actions>

## Acceptance Checks

Deterministic checks that prove the skill worked for this request.

1. The skill instructions were followed without requiring context not present in the skill.
2. The produced output matches the expected type/format above.
3. No forbidden action occurred.
4. <add skill-specific acceptance checks>

## Sub-Agent Prompt

The exact prompt to hand to a Task sub-agent (derived from the harness `FUNCTIONAL PROMPT TEMPLATE`). The sub-agent returns a report with:

```
## Instructions followed
## Expected output produced
## Forbidden actions avoided
## Verdict
```

The Verdict line must be exactly `FUNCTIONAL_SMOKE_TEST_PASSED` or `FUNCTIONAL_SMOKE_TEST_FAILED` (with explicit reasons on failure).

Paste the sub-agent report below this line and link or save it as the closeout artifact.

---
<sub-agent report goes here>
