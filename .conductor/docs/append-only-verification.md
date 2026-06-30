# Append-Only Verification Runbook

A reusable pattern for verifying that an edit to an existing file is strictly append-only: every original byte is preserved exactly, and all changes are pure additions at the end (or a clearly bounded insertion that does not rewrite existing bytes). Use this whenever a plan claims an "append-only" or "preserve existing content" edit.

## When to Use

Use this runbook when:

- A task must append a section to an existing Markdown/doc file and must not alter any existing line.
- The target file may be untracked by git, so path-scoped `git diff` cannot be trusted.
- You need deterministic, re-runnable proof (not a visual skim) that existing content is byte-for-byte intact.

Do not use this for full rewrites, formatting passes, or in-place edits where existing bytes are intended to change.

## Step 1: Classify Target File State

Before diffing, classify the target:

- Tracked by git? Run `git ls-files --error-unmatch <path>`; exit 0 means tracked.
- If tracked, `git diff -- <path>` is a valid comparator against the index/HEAD baseline.
- If untracked (newly created, gitignored, or never staged), `git diff -- <path>` is insufficient - it has no tracked baseline. Fall back to the backup comparator in the next steps.

Living inside a git repo does not prove a file is tracked by git.

## Step 2: Capture Pre-Edit Backup

Before editing, copy the exact current bytes to a timestamped backup:

```
Copy-Item -LiteralPath <target> -Destination <target>.pre-edit.bak -Force
```

This backup is the source of truth for the no-index diff. Keep it until verification passes.

## Step 3: Use Semantic Idempotency Guards

When asserting a structure exists "exactly once", match structure, not loose substrings. Use line-anchored full-line patterns. For example, to prove a `## Hello World` heading exists as its own line, use `^##\s+Hello World\s*$`, not a bare `## Hello World` substring (which would also match inside backticks or a longer line).

## Step 4: Append Without Rewriting Existing Bytes

Perform the edit so existing bytes are never rewritten. Preferred approaches:

- Read the file as a single string, append new content, write once with no trailing-newline injection in the middle.
- Or open in append mode and write only the new block.

Avoid editors/commands that normalize line endings, reflow whitespace, or re-encode the file, because those silently rewrite existing bytes and break byte-prefix preservation.

## Step 5: Verify Byte-Prefix Preservation

Confirm the backup is an exact byte-prefix of the target:

```
$backup = [System.IO.File]::ReadAllBytes(<backup>)
$target = [System.IO.File]::ReadAllBytes(<target>)
if ($target.Length -lt $backup.Length) { "FAIL: target shorter than backup"; exit 1 }
for ($i = 0; $i -lt $backup.Length; $i++) { if ($target[$i] -ne $backup[$i]) { "FAIL: byte mismatch at $i"; exit 1 } }
"PASS: byte-prefix preserved"
```

If this fails, the edit rewrote existing bytes; revert and redo Step 4.

## Step 6: Verify Native Git Diff Against Backup

Use `git diff --no-index` to get a line-level additions-only diff against the backup. This works for tracked and untracked files alike. Use `--numstat` to assert that deletions are zero:

```
git diff --no-index --numstat -- <backup> <target>
```

Expected output: a single line where the deletions column (the second number) is `0`, e.g. `1	0	path/to/target`. Any non-zero deletion column means existing content was changed, not appended. Note: `git diff --no-index` exits non-zero when files differ, which is expected here; rely on the numstat columns, not the exit code.

## Step 7: Verify Content Shape

Finally, verify the appended block itself has the expected shape:

- The new heading appears exactly once (line-anchored regex, count must equal 1).
- The paragraph immediately after the heading has a sentence count within the expected range.
- No duplicate of the heading exists elsewhere in the file.

## Dirty Working Tree Guidance

This runbook does NOT require a clean git working tree. Unrelated dirty files may stay dirty. The backup-vs-target comparator (Steps 5 and 6) is independent of git working-tree state, which is exactly why `git diff --no-index <backup> <target>` is authoritative for untracked targets where `git diff -- <path>` is insufficient.

## Recovery

If any step fails:

1. Byte-prefix failed (Step 5): existing bytes were rewritten. Restore the target from the Step 2 backup and redo the append without a normalizing editor.
2. Numstat shows deletions (Step 6): existing lines were modified. Restore from backup and redo.
3. Heading count is not 1 (Step 7): either the heading already existed (dedupe) or the append was skipped (re-append).
4. Never weaken the acceptance criteria to make a failing check pass; fix the edit or restore and redo.