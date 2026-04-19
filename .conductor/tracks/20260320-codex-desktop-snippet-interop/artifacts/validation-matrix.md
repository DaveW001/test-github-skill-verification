# Validation Matrix: OpenCode Snippet Interop for Codex Desktop

**Track ID**: 20260320-codex-desktop-snippet-interop  
**Created**: 2026-03-20  
**Purpose**: Define the validation burden so the agent performs the majority of testing work.

---

## Validation Principles

1. Prefer deterministic, agent-run proof over manual observation.
2. Use the real snippet corpus as fixtures instead of synthetic-only tests.
3. Separate parser/runtime validation from UI-surface validation so desktop automation gaps do not block confidence.
4. Keep final operator validation to a minimal smoke check only if agent-run UI proof cannot reach the live Codex Desktop input surface.

---

## Test Layers

## Layer 1: Corpus Audit

- Objective: Prove what features exist in the real snippet set.
- Agent-run: Yes
- Evidence:
  - snippet inventory
  - alias map
  - feature map for shell commands, append blocks, inject blocks, and recursive references

## Layer 2: Parser and Resolver Tests

- Objective: Prove that frontmatter, body parsing, file-name lookup, alias lookup, and precedence rules are correct.
- Agent-run: Yes
- Evidence:
  - automated unit tests
  - pass/fail summary

## Layer 3: Expansion Semantics Tests

- Objective: Prove recursive expansion, append handling, inject handling, cycle detection, and missing-snippet behavior.
- Agent-run: Yes
- Evidence:
  - fixture outputs
  - failure-case assertions

## Layer 4: Shell Interpolation Policy Tests

- Objective: Prove exactly how ``!`command` `` behaves in Codex Desktop compatibility mode.
- Agent-run: Yes
- Evidence:
  - supported-command test results
  - blocked-command test results
  - documented policy decision

## Layer 5: Real-Snippet Fixture Proof

- Objective: Prove representative snippets from the live corpus expand as expected.
- Agent-run: Yes
- Candidate fixtures:
  - `#context`
  - `#conductor-spec`
  - `#code-review`
  - one snippet with aliases
  - one snippet with recursive includes if present

## Layer 6: Desktop Invocation Proof

- Objective: Prove that a Codex Desktop user can invoke `#name` and obtain the expected expanded prompt.
- Agent-run: Preferred
- Fallback: Minimal operator smoke check
- Evidence:
  - automation trace or screenshot/log if agent-driven
  - one-line operator confirmation only if direct automation is blocked

## Layer 7: Regression and Rollback Proof

- Objective: Prove OpenCode snippets remain unchanged and the Codex Desktop integration can be disabled cleanly.
- Agent-run: Yes
- Evidence:
  - unchanged snippet source files
  - rollback execution notes
  - post-rollback sanity check

---

## Exit Criteria

- Parser/resolver tests pass on the chosen implementation.
- Real-snippet fixtures pass on the chosen implementation.
- Shell interpolation policy is explicit and tested.
- Desktop invocation is proven by automation or, if impossible, by one short operator smoke check.
- Rollback is documented and validated.
