# Spec: Install Thinking Partner Skill with Multi-App Symlinks

## Goal
Install the [thinking-partner](https://github.com/mattnowdev/thinking-partner) skill (150+ mental models, orientation detection, cognitive operations) into OpenCode and make it available to Codex and Anti-Gravity-adjacent agent surfaces via the established symlink/junction pattern.

## Background
- **Source repo**: `https://github.com/mattnowdev/thinking-partner` (MIT license)
- **Observed upstream tree**: `skills/thinking-partner/` contains one `SKILL.md` and two one-level reference files.
- **Skill files**:
  - `skills/thinking-partner/SKILL.md` (~17.5 KB — main skill definition)
  - `skills/thinking-partner/references/model-catalog.md` (~46 KB — 150+ models across 17 disciplines)
  - `skills/thinking-partner/references/thinking-diagnostics.md` (~12 KB — orientation capture, cognitive operations)
- **OpenCode path note**: `C:\Users\DaveWitkin\.config\opencode\skills` is a junction to `C:\Users\DaveWitkin\.config\opencode\skill`. Either path resolves to the same canonical skill store.

## Requirements
- [ ] Use the `skill-writer` skill/checklist to validate the upstream skill before installing.
- [ ] Clone the repo to a temp directory and record the exact upstream commit SHA used.
- [ ] Check whether `thinking-partner` already exists in the canonical OpenCode skill store and back it up or stop before overwrite.
- [ ] Copy `skills/thinking-partner/` (SKILL.md + references/) to the OpenCode skills directory.
- [ ] Validate OpenCode skill compliance:
  - [ ] folder slug is `thinking-partner`
  - [ ] `SKILL.md` exists exactly at the skill root
  - [ ] frontmatter YAML parses
  - [ ] frontmatter `name: thinking-partner` exactly matches directory
  - [ ] `name` matches `^[a-z0-9]+(-[a-z0-9]+)*$`
  - [ ] `description` is non-empty, within 1-1024 chars, and includes what/when triggers
  - [ ] reference paths are one level deep and readable
- [ ] Create directory symlink: Codex skills → OpenCode skills.
- [ ] Create directory symlink: `.agents/skills` → OpenCode skills.
- [ ] Verify symlinks resolve correctly from Codex and `.agents`.
- [ ] Verify activation/discovery expectations; note that a new OpenCode session may be required before the installed skill appears in the runtime `available_skills` list.

## Non-Requirements
- [ ] Refactoring or rewriting the upstream skill unless validation finds a load-blocking issue.
- [ ] Creating an npm-based `npx skills add` installation (manual install is preferred for control, traceability, and symlink setup).
- [ ] Creating a native Anti-Gravity integration unless a skills directory is discovered. Current observed Anti-Gravity directory only has VS Code-style extension storage; `.agents/skills` is the relevant cross-agent surface found on this machine.

## Symlink Pattern (established)
Existing Codex skills use **directory symlinks** (`New-Item -ItemType SymbolicLink`) pointing from the app's skill dir to the canonical OpenCode skills dir. If symlink creation fails due Windows permissions, fall back to a junction (`New-Item -ItemType Junction`) or give the user an elevated `gsudo` command.

| App / Surface | Skill Dir | Pattern |
|-----|-----------|---------|
| OpenCode | `C:\Users\DaveWitkin\.config\opencode\skill\thinking-partner\` | Primary canonical store |
| OpenCode compatibility path | `C:\Users\DaveWitkin\.config\opencode\skills\thinking-partner\` | Via existing `skills` junction |
| Codex | `C:\Users\DaveWitkin\.codex\skills\thinking-partner` → OpenCode | Symlink or junction |
| .agents | `C:\Users\DaveWitkin\.agents\skills\thinking-partner` → OpenCode | Symlink or junction |
| Anti-Gravity | `C:\Users\DaveWitkin\.antigravity\` | No skills dir found; skip native install unless later discovered |

## Acceptance Criteria
- [ ] `C:\Users\DaveWitkin\.config\opencode\skill\thinking-partner\SKILL.md` exists with valid frontmatter.
- [ ] `C:\Users\DaveWitkin\.config\opencode\skill\thinking-partner\references\model-catalog.md` exists and is readable.
- [ ] `C:\Users\DaveWitkin\.config\opencode\skill\thinking-partner\references\thinking-diagnostics.md` exists and is readable.
- [ ] Skill Writer validation checklist passes or any deviations are documented.
- [ ] Source commit SHA is recorded in install notes or metadata.
- [ ] `C:\Users\DaveWitkin\.codex\skills\thinking-partner` resolves to the OpenCode location.
- [ ] `C:\Users\DaveWitkin\.agents\skills\thinking-partner` resolves to the OpenCode location.
- [ ] Anti-Gravity handling is documented: no native skill directory found; `.agents/skills` link provides the available shared agent surface.
- [ ] Skill triggers are documented for phrases like "help me think through X", "challenge my thinking", and "play devil's advocate".
