# Changelog

All notable changes to the **pptx-from-layouts** skill are documented here.
This project adapts the `tristan-mcinnis/pptx-from-layouts-skill` Claude Code
skill into a consolidated, Windows-native OpenCode lazy-vault skill.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased] - Adapted for OpenCode (Windows)

Date: 2026-07-10
Track: `20260709-pptx-skill-adapt`

Consolidates the three Claude sibling skills (`pptx-from-layouts`,
`pptx-profile`, `pptx-author`) into one self-contained OpenCode skill at
`C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\`, with all
documented Windows portability bugs fixed and three registered OpenCode
subagents wired to the Task tool. Validated 6/6 on the Windows validation
matrix.

### Added

- **Consolidated OpenCode install.** The skill is a single self-contained
  package in the OpenCode lazy vault (`~/.opencode-lazy-vault/pptx-from-layouts`),
  discoverable via `skill_find` / `skill_use` (after a session restart).
- **Registered OpenCode subagents.** Three global subagents registered at
  `~/.config/opencode/agent/` for programmatic Task-tool delegation:
  - `pptx-outline-architect` - turn raw material into a generation-ready outline.
  - `pptx-template-onboarder` - one-time onboarding of a custom brand template.
  - `pptx-deck-qa` - validate a deck and apply a surgical fix or recommend
    regeneration.
  Each uses `mode: subagent`, `hidden: true`, and
  `permission: { edit: allow, bash: allow, task: { "*": deny } }`.
- **Bundled templates inside the skill.** The Inner Chapter template
  (`templates\inner-chapter.pptx`) and its render config
  (`templates\inner-chapter-config.json`) are bundled inside the skill dir, so
  the default works with no external repo-relative path. SHA-256 unchanged:
  `D9800CAA98BB5926595B55195BF47592B8DA50CEAE1896A32684B1706EA82B01`.
- **Folded-in sibling skills.** `pptx-profile` (`catalog.py`) and
  `pptx-author` (`lint_hints.py` + author guidance) are merged into this one
  skill, removing sibling-directory assumptions.
- **README.md** documenting the 3-step pipeline, the three public entry-point
  commands with Windows invocation, the bundled template, the registered
  subagents (including the session-restart caveat), Windows requirements, and
  known limitations.

### Changed

- **Paths are self-relative to the skill directory.** Entry-point scripts
  (`generate.py`, `profile.py`, `edit.py`, `validate.py`) now default the
  template/config to `_SKILL_DIR / "templates" / ...` instead of a repo-root or
  sibling-directory assumption, so they resolve correctly from any working
  directory.
- **Working directory is set to the skill dir.** The `cwd=` for the rendering
  subprocess was changed from a repo-root `_PROJECT_ROOT` to `_SKILL_DIR`, so
  template/config resolution is anchored on the skill itself.
- **Subagent invocation moved to the OpenCode Task tool.** The Claude
  `tools:` / `model:` blocks and `~/.claude/agents/` install guidance were
  replaced with OpenCode Task-tool delegation (`subagent_type:` matching the
  agent name). `SKILL.md` documents the delegation patterns.
- **`SKILL.md` rewritten** with OpenCode frontmatter (`compatibility: opencode`),
  consolidated workflow commands, and the Task-tool delegation table. All
  `~/.claude/` and sibling-skill references were scrubbed from executable
  guidance and the bundled `agents\`, `references\`, and `rules\` markdown.

### Fixed

- **PYTHONPATH separator (Windows).** Entry-point scripts built `PYTHONPATH`
  with a colon (`":"`) separator, which is invalid on Windows. Replaced with
  `os.pathsep.join(...)` so the module search path is correct on Windows (and
  any platform).
- **Hardcoded `/tmp` path (Issue B).** `visual_validator.py` hardcoded
  `/tmp/lo-profile-{pid}` for the LibreOffice profile dir, which does not exist
  on Windows. Replaced with `tempfile.gettempdir()` so a Windows-friendly
  absolute temp path is used. (End-to-end visual validation remains
  dependency-skipped where LibreOffice is not installed.)
- **`generate_config.py` module path (self-contained sys.path).**
  `generate_config.py` derived its base directory from a fixed parent depth
  that assumed a sibling-skill layout. Replaced with a self-contained
  `sys.path` insertion rooted on `_SCRIPT_DIR` / `_SKILL_DIR` / `_LIB_DIR` /
  `_SCHEMAS_DIR`.
- **Singular `template/` default (Issue C).** `generate_pptx.py` defaulted the
  template to `template/inner-chapter.pptx` (singular, repo-root relative).
  Replaced with `default=str(_SKILL_DIR / "templates" / "inner-chapter.pptx")`
  so the bundled default resolves correctly.
- **`quality_check.py` cp1252 `UnicodeEncodeError` (Windows stdout).** The
  validation report printer crashed on a default Windows console (cp1252)
  because box-drawing/checkmark glyphs are not encodable. Added a UTF-8 stdout
  reconfigure guard at the start of `main()` (`hasattr(sys.stdout, "reconfigure")`
  for 3.7+ safety, `errors="replace"`), which fixed both user-facing validation
  entry points (`generate.py ... --validate` and `validate.py`) on a default
  Windows setup without relying on `PYTHONUTF8=1`.

### Validation

- Windows validation matrix: **6/6 PASS** (generate, profile, generate-config,
  edit inventory, validate, template-hash-unchanged).
- Supplemental static checks: all 21 scripts compile (`py_compile`), bad-path
  literals absent, positive-fix assertions present; `validate.py` runs without
  `--template` (self-relative default resolves); template hash unchanged after
  generation.
- Visual validation: **dependency-skipped** (LibreOffice not installed on the
  validation host).

### Known caveats

- Subagent invocation via the Task tool and skill discovery via `skill_find`
  require an **OpenCode session restart** after first registration (agent types
  and the skillful vault index are cached at startup).
- Visual (pixel-diff) validation requires **LibreOffice**; without it, only
  structural validation runs.

---

### Links

- Source skill: `tristan-mcinnis/pptx-from-layouts-skill`
- Adaptation track: `20260709-pptx-skill-adapt`
- Architectural decision: `docs\ADR-001-registered-opencode-subagents.md`
