# Plan: Install Thinking Partner Skill

**Upstream commit:** `ce95b6280660652d67bfc3fc36f8d7f941538f7f`
**Installed:** 2026-04-25

## Phase 0 - Preflight & Validation Design
- [x] Load/use `skill-writer` guidance before installing or modifying the skill.
- [x] Confirm canonical OpenCode skill path: `C:\Users\DaveWitkin\.config\opencode\skill` (`skills` is a junction to this path).
- [x] Check for existing `thinking-partner` installs in OpenCode, Codex, and `.agents`; back up or stop if conflicts exist. → None found.
- [x] Identify upstream commit SHA to install and record it. → `ce95b628`
- [x] Validate upstream `SKILL.md` against Skill Writer/OpenCode rules before copy:
  - [x] file is named exactly `SKILL.md` ✓
  - [x] frontmatter YAML parses ✓
  - [x] `name: thinking-partner` exactly matches directory ✓
  - [x] `name` matches `^[a-z0-9]+(-[a-z0-9]+)*$` ✓
  - [x] `description` is 1-1024 chars (837 chars) and contains what/when trigger language ✓
  - [x] references are one level deep and referenced files exist/read correctly ✓

## Phase 1 - Download & Install to OpenCode
- [x] Clone `mattnowdev/thinking-partner` to a temp directory.
- [x] Create target directory: `C:\Users\DaveWitkin\.config\opencode\skill\thinking-partner\references\`.
- [x] Copy `skills/thinking-partner/SKILL.md` to `C:\Users\DaveWitkin\.config\opencode\skill\thinking-partner\SKILL.md`.
- [x] Copy `skills/thinking-partner/references/model-catalog.md` to the references subdirectory.
- [x] Copy `skills/thinking-partner/references/thinking-diagnostics.md` to the references subdirectory.
- [x] Verify copied files landed correctly (existence, approximate sizes, frontmatter).

## Phase 2 - Create Symlinks for Multi-App Access
- [x] Create junction: `C:\Users\DaveWitkin\.codex\skills\thinking-partner` → `C:\Users\DaveWitkin\.config\opencode\skill\thinking-partner`. (Symlink failed due permissions; junction used as fallback.)
- [x] Create junction: `C:\Users\DaveWitkin\.agents\skills\thinking-partner` → `C:\Users\DaveWitkin\.config\opencode\skill\thinking-partner`.
- [x] Verify junctions resolve and reference files are readable through each linked path.

## Phase 3 - Discovery & Runtime Verification
- [x] Confirm OpenCode skill path can be enumerated from canonical and compatibility locations.
- [x] Confirm SKILL.md frontmatter has `name: thinking-partner` and rich `description`.
- [x] Confirm reference files are readable through OpenCode, Codex, and `.agents` paths.
- [x] Anti-Gravity result: no native skills dir found under `C:\Users\DaveWitkin\.antigravity`; `.agents/skills` junction provides the shared agent-surface link.

## Phase 4 - Cleanup & Conductor Sync
- [x] Remove temp clone directory.
- [x] Record installed commit SHA and validation outcome in this track.
- [x] Update `metadata.json` progress/status and mark plan tasks completed.

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.
