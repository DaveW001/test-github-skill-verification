# Spec: Cross-Harness AGENTS.md and Instruction Architecture Remediation

## Goal

Implement the approved AGENTS.md, progressive-disclosure, agent-authoring, project-file, and cross-harness storage improvements while preserving the user-level OpenCode environment file as the central documented source of truth for credentials and runtime variables.

## Requirements

- [ ] Preserve `C:\Users\DaveWitkin\.config\opencode\.env` as the central, commented reference for shared runtime variables; do not rotate credentials in this track.
- [ ] Repair the agent-writer templates and references to match current OpenCode permission syntax and existing canonical files.
- [ ] Extract shared instruction modules under `C:\Users\DaveWitkin\.config\opencode\agent-rules\` and reduce always-loaded global files.
- [ ] Move specialized OpenCode guidance behind trigger-based references or skills.
- [ ] Consolidate duplicated OpenCode agent/command standards without losing normative rules.
- [ ] Refine selected project AGENTS.md files so they contain project-local constraints rather than duplicated workflow catalogs.
- [ ] Add an ownership/loading manifest and deterministic validation checks for the new structure.
- [ ] Preserve unrelated dirty-worktree changes and do not commit, push, rotate credentials, publish, or send external communications.

## Non-Requirements

- [ ] Do not rotate any credential.
- [ ] Do not delete backups or historical Conductor artifacts.
- [ ] Do not change application source code, provider routing behavior, or external integrations.
- [ ] Do not make Codex and OpenCode share one identical global AGENTS.md; retain thin harness-specific adapters.

## Acceptance Criteria

- [ ] The documented shared-rule tree exists and the two global bootstrap files are reduced without losing harness-specific safety rules.
- [ ] Agent templates use canonical `permission:` syntax and no active template uses deprecated `tools:` syntax.
- [ ] Every reference in the active agent-writer skill resolves to an existing canonical file, or is explicitly removed/replaced.
- [ ] OpenCode configuration references environment variables rather than embedding the affected credential value; `.env` remains documented and unchanged in value.
- [ ] Selected project AGENTS.md files retain required commands and constraints while moving detailed workflow material to canonical references.
- [ ] Deterministic structural/config validation passes, Conductor artifacts are synchronized, and a rollback map exists.

