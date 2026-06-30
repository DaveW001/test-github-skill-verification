# Spec: Smoke-Test Hello World Section

Track ID: `20260629-smoke-test-hello-world`
Title: Append Hello World smoke-test section
Status: planning
Created: 2026-06-29
Target file: `C:\development\opencode\.conductor\smoke-test\hello-world.md`
Workspace root: `C:\development\opencode`

## Goal / Outcome
Append one new Markdown section to `C:\development\opencode\.conductor\smoke-test\hello-world.md`: a single heading `## Hello World` followed by exactly one prose paragraph of 3-6 sentences stating that the section is a toy / sanity-check documentation example created by the Conductor pipeline as a smoke test.

## Constraints / Non-goals
- Modify only `C:\development\opencode\.conductor\smoke-test\hello-world.md`.
- Do not modify, remove, or reorder existing target content.
- Do not touch unrelated tracked or untracked working-tree files.
- Use PowerShell 7+ commands on Windows with absolute paths.
- Use native `git diff --no-index` between the pre-edit backup and the post-edit target. The target file is currently UNTRACKED in the working tree (`git status` shows `?? .conductor/smoke-test/hello-world.md`), so path-scoped `git diff -- <path>` returns empty for it; `git diff --no-index <backup> <target>` is the literal interpretation of "git diff against a pre-edit backup" and works for any two files on disk (tracked or not).
- Isolate this task from unrelated pre-existing dirty paths by using the pre-edit backup as the diff reference and a byte-exact prefix check; do not assume a clean working tree.
- If `## Hello World` already exists before appending, stop and report instead of appending a duplicate.

## Definition of Done
- The target file begins byte-for-byte with the entire pre-edit backup content.
- Exactly one new `## Hello World` section is appended after existing content.
- The appended section contains one heading line and one prose paragraph of 3-6 sentences.
- `git diff --no-index` between the pre-edit backup and the post-edit target shows only added lines for the new section; numstat's deletion column is `0`.
- Verification confirms this track's intended footprint is only the target file plus the pre-edit sidecar backup, despite unrelated pre-existing repo dirtiness.

## Acceptance Criteria
1. `C:\development\opencode\.conductor\smoke-test\hello-world.md` exists before modification.
2. A byte-exact sidecar backup exists at `C:\development\opencode\.conductor\smoke-test\hello-world.pre-edit.bak.md` before modification, and is the SHA256-identical pre-edit content.
3. The backup content is an unchanged byte-level prefix of the current target file after modification.
4. The appended snippet is exactly:

```markdown

## Hello World
This section is a toy documentation example created by the Conductor pipeline as a smoke test. It is a sanity-check addition that proves the pipeline can append a small, well-scoped Markdown section without disturbing existing content. The example is intentionally simple so reviewers can verify the change quickly and confidently.
```

5. No duplicate `## Hello World` heading is created (count of `^## Hello World$` lines in the file is exactly `1` after execution).
6. `git diff --no-index --numstat` between the pre-edit backup and the post-edit target shows `0` in the deletion column and a positive value in the addition column, with the only file mentioned in the diff being the target file.
7. No file other than `C:\development\opencode\.conductor\smoke-test\hello-world.md` is modified by execution, except the temporary sidecar backup used for verification/recovery.