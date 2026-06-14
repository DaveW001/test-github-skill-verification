# Plan

## Phase 1 - Setup
- [x] Initialize project
- [x] Install dependencies

## Phase 2 - Implementation
- [ ] Build feature A
- [ ] Build feature B

## Phase 3 - Verification
- [ ] Test feature A
- [ ] Update documentation

## Phase 4 - Completion Validation
- [ ] Verify all non-deferred plan tasks are checked `[x]`
- [ ] Verify `metadata.json` status/progress values are synchronized with plan completion
- [ ] Verify `.conductor/tracks.md` row status and completed date match metadata
- [ ] Create or update execution/change log with deviations, skipped items, and validation summary
- [ ] Re-open all modified/created artifacts and confirm required acceptance strings exist

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.

## Task Safety Rules

### Collision Guard (Required for Any Rename/Move Task)

When a task involves renaming or moving files, include a pre-execution check in the task instructions:

```markdown
#### Pre-execution check
- Before executing, verify the target path does NOT already exist.
- If target exists: stop and report the collision. Do NOT overwrite.
- Resolve by either: (a) asking user to choose, (b) merging content, or
  (c) deleting the duplicate if confirmed redundant.
```

### Edit Safety for Structured Files (Required for Bulk Edits)

When editing files with 3+ items sharing identical structural patterns (review queues,
ledgers, audit reports), prefer rewriting the entire file over individual `oldString`
edits. See `knowledge-graph-maintainer` skill reference:
`references/edit-safety-for-structured-files.md`.
