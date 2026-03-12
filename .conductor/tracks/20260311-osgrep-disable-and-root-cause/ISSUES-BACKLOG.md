# Issues Backlog (Current)

Source: post-build evaluation findings on 2026-03-11.

## High

### 1) Osgrep policy conflict across active guidance

Problem:
- Some instructions still imply or prioritize osgrep usage even though disablement is active.

Why it matters:
- Creates contradictory agent behavior and operator confusion.

Required fix:
- Keep disablement direction for now.
- Remove any remaining osgrep-first language from active prompts/policies.
- Ensure troubleshooting docs and active standards agree on disabled-by-default behavior.

Status:
- Completed on 2026-03-12.
- Updated active guidance wording in `AGENTS-STREAMLINING-SUMMARY.md` and `docs/reference/osgrep-configuration.md` to align with disabled-by-default policy.

## Medium

### 2) Hardcoded local repo paths in global standards

Problem:
- Global docs reference `C:/development/opencode/patterns/prompts/...` directly.

Why it matters:
- Not portable across machines and alternate workspace locations.

Required fix:
- Replace absolute local paths with repo-relative paths (for example `patterns/prompts/...`).
- Add one short note describing expected repository context when needed.

Status:
- Completed on 2026-03-12.
- Updated global standards and skill docs to repo-relative prompt-pattern references with explicit repository-context notes.

### 3) Prompt pattern validator too shallow

Problem:
- `scripts/validate-prompt-patterns.py` checks section presence but not enough content quality.

Why it matters:
- Weak patterns can pass validation and reduce long-term library quality.

Required fix:
- Add checks for:
  - at least one `{{variable}}` in `Prompt Template`
  - at least one bullet under `Variables`
  - non-empty `Example Input` and `Example Output Shape`
  - title/filename quality checks (title case and expected slug consistency)

Status:
- Completed on 2026-03-12.
- Added `scripts/validate-prompt-patterns.py` with all required content-quality checks.

## Low

### 4) Minor trigger ambiguity (`osgrep` vs `perplexity-search`)

Problem:
- Phrase overlap remains (`find code for` vs `find sources`).

Why it matters:
- Low-level ranking ambiguity in edge cases.

Required fix:
- Tighten phrase specificity (for example `find code path for` and `find web sources for`).

Status:
- Completed on 2026-03-12.
- Updated trigger phrasing in `C:/Users/DaveWitkin/.config/opencode/skill/osgrep/SKILL.md` and `C:/Users/DaveWitkin/.config/opencode/skill/perplexity-search/SKILL.md`.
