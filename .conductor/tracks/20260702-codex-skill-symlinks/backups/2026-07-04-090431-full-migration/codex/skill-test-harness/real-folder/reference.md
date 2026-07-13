# Skill Test Harness - Reference

This reference documents the behavior, output schema, checks, and limitations of the `skill-test-harness` skill and its `scripts\skill-smoke-test.ps1` harness.

A skill is confirmed only when structural checks, script checks when applicable, and at least one representative functional smoke test pass.

## When to run

- After creating or updating a skill, before declaring it confirmed.
- Before closing any Conductor skill-creation track.
- When a skill's instructions change and you want to re-confirm behavior.

## How to run

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1" -SkillPath "<absolute-skill-path>" -PrintFunctionalPrompt
```

- `-SkillPath` is the absolute path to the skill directory (the folder containing `SKILL.md`).
- `-PrintFunctionalPrompt` prints a ready-to-use `FUNCTIONAL PROMPT TEMPLATE` for a Task sub-agent.

## Output Schema

The harness prints a deterministic `SKILL SMOKE TEST SUMMARY` followed by per-category aggregate lines, each beginning with one of these section labels and inline status content on the same line:

- `STRUCTURE:` - SKILL.md existence, frontmatter fences, name/directory-slug match, naming regex, description presence and length.
- `REFERENCES:` - local Markdown link resolution and referenced-file resolution.
- `SCRIPT SYNTAX:` - `.ps1` via `PSParser::Tokenize` and `.py` via Python `ast.parse` when an interpreter is available.

The summary ends with:

- `WARNINGS: <n>   FAILURES: <n>`
- `RESULT: PASS` (zero failures) or `RESULT: FAIL` (one or more failures).

The process exit code is `0` on `RESULT: PASS` and `1` on `RESULT: FAIL`.

A `DETAILS` block lists every individual check result as `[CATEGORY][STATUS] message`. Statuses are `PASS`, `FAIL`, `WARN`, `SKIP`, and `INFO`.

## Checks performed

### Structure
- `SKILL.md` exists in the skill directory.
- File starts with a `--- ... ---` frontmatter fence.
- Frontmatter `name` exactly equals the directory slug.
- `name` matches the recommended regex `^[a-z0-9]+(-[a-z0-9]+)*$` (mismatch is a warning, not a failure).
- Frontmatter `description` exists, is non-empty, and is at most 1024 characters.

### References
- Markdown links of the form `[text](target)` are collected from every `.md` file, with fenced code blocks stripped first.
- External schemes (`http://`, `https://`, `ftp://`, `mailto:`) and pure-anchor (`#...`) links are ignored.
- Remaining targets are resolved relative to the Markdown file. A missing target with a known extension (`.md`, `.ps1`, `.py`, `.json`, `.jsonc`, `.txt`, `.yaml`, `.yml`, etc.) is a hard `FAIL`; an ambiguous/unknown target is a `WARN`.
- Backtick-wrapped relative paths with a known extension are also resolved; a missing one is a `WARN`.

### Script syntax
- Every `.ps1` is tokenized with `[System.Management.Automation.PSParser]::Tokenize`; any parse error is a `FAIL`.
- Every `.py` is parsed with `python -c "import ast; ast.parse(...)"` when an interpreter is found. If Python is not available, the check is a `WARN` (not a failure).
- Skills with no `.ps1`/`.py` files record a single `SKIP`.

## Severity model

- `PASS` - check succeeded.
- `FAIL` - contributes to `RESULT: FAIL`. The run exits `1`.
- `WARN` - advisory only; does NOT fail the run. Used when a reference is ambiguous or a check cannot be performed (e.g., no Python interpreter).
- `SKIP` - nothing to check (e.g., no scripts). Does not fail the run.

Warnings do not fail the run. A failure is recorded only when a check that can be performed on a file that exists (or is clearly required and present) does not pass.

## Sub-Agent Smoke Test

The harness prints a `FUNCTIONAL PROMPT TEMPLATE`; it does NOT launch the sub-agent itself. The orchestrator/author copies that template into a Task sub-agent. The sub-agent must follow the skill's instructions for one representative, offline request and return:

```
## Instructions followed
## Expected output produced
## Forbidden actions avoided
## Verdict
```

with a verdict of either `FUNCTIONAL_SMOKE_TEST_PASSED` or `FUNCTIONAL_SMOKE_TEST_FAILED` (with explicit reasons). The saved report is the closeout artifact that converts a structurally valid skill into a confirmed skill.

## Limitations

- No external API calls. The harness never sends network traffic and never inspects or prints token/credential values.
- The functional confirmation itself requires a human/orchestrator-launched Task sub-agent; the harness only produces the prompt.
- Python syntax checking depends on a local interpreter; when absent it degrades to a warning.
- Frontmatter parsing supports the simple `key: value` form (sufficient for `name` and `description`); complex nested frontmatter is not deeply validated.

## Test-case convention

Every new skill MUST include at least one functional test case in `tests\` or explicitly document that it is structurally valid but functionally unconfirmed. See `templates\test-case.template.md`.
