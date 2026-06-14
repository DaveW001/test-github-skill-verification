---
name: git-push
description: Standardized, low-token git stage+commit+push workflow for Windows.
triggers:
  intent:
    - git push workflow
    - branch publishing
    - commit and publish
  user_phrases:
    - push to github
    - push changes
    - commit and push
  file_context:
    extensions: [md, ts, js, py]
    paths: [.git/**]
  tool_context:
    before_tools: [bash]
    with_tools: [bash]
  error_context:
    - branch not pushed
    - commit workflow needed
  priority: high
  suggest_only: true
compatibility: Windows; requires python on PATH and C:/development/01-knowledge-base/07_scripts_and_utilities/git-push-universal.py
---

# Git Push

Use this skill any time the user asks to push changes / a branch to GitHub.

## Default Behavior

- Unless the user explicitly says otherwise, do the full sequence: stage -> commit -> push.
- Exclude anything in folders whose name contains `tmp` (e.g., `.opencode/tmp/`, `tmp/`, `foo/tmp/bar`).
- Be diff-summary-first to keep token usage low.

## Token/IO Efficiency Rules (Always)

1. Prefer summaries over full diffs:
   - `git status -sb`
   - `git diff --stat`
   - `git diff --name-status`
   - `git diff --name-status --cached`

2. Do not dump full `git diff` output into the chat.
   - Only inspect full diffs for the 1-3 files that actually drive the commit message.

3. Do not delegate commit message drafting to another agent by default.
   - Use file paths + stats to draft a Conventional Commits message.

## Preflight Checks

1. Confirm we are in a git repo: `git rev-parse --is-inside-work-tree`
2. Confirm Python is available: `python --version`
3. Confirm the universal push script exists:
   - `C:/development/01-knowledge-base/07_scripts_and_utilities/git-push-universal.py`

## Standard Process

1. Review changes (summary-first)
2. Draft a Conventional Commits message (1 line; use scope when helpful)
3. Run:

```bash
python "C:/development/01-knowledge-base/07_scripts_and_utilities/git-push-universal.py" "<message>"
```

4. Report success or the exact error output.

## Guardrails

- Do not commit secrets (`.env`, credentials, tokens).
- If there are no changes, report "nothing to push".
