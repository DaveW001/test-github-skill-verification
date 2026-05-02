# Spec: Skill Health Validator — Scheduled Job

## Goal
Create a daily automated job that validates the OpenCode skill taxonomy is healthy: frontmatter valid, global index fresh, cross-surface junctions intact. Auto-fixes safe issues (junctions, renames) and flags complex issues (missing index categories, bad frontmatter) in a rolling report.

## Background
Skills live in a canonical directory with junctions to Codex and `.agents`. After manual skill work (installs, renames, archives), the following can drift:
- **Index staleness** — `docs/reference/global-skills-index.md` references old names or misses new skills.
- **Missing junctions** — A skill exists in OpenCode but has no `.codex/skills` or `.agents/skills` link.
- **Broken frontmatter** — Directory name doesn't match frontmatter `name`, or description is invalid.
- **Orphaned archive links** — An archived skill still has active junctions pointing to it.

## Scheduling Decision
Use the OpenCode built-in scheduler in the `development` scope to run an AI agent daily. 

## Scheduler Schema (observed from existing jobs)
```json
{
  "scopeId": "development-88876ee600f5",
  "slug": "skill-health-validator",
  "name": "skill-health-validator",
  "schedule": "0 6 * * *",
  "run": {
    "command": "Read and execute the exact instructions in C:\\Users\\DaveWitkin\\.config\\opencode\\scripts\\skill-health-validator.md",
    "title": "Skill Health Validator",
    "runFormat": "default"
  },
  "source": "development",
  "workdir": "C:\\development",
  "timeoutSeconds": 300,
  "invocation": {
    "command": "opencode",
    "args": [
      "run",
      "Read and execute the exact instructions in C:\\Users\\DaveWitkin\\.config\\opencode\\scripts\\skill-health-validator.md"
    ]
  }
}
```

## Requirements

### The Validator Prompt (skill-health-validator.md)
The prompt must instruct the agent to perform these checks, in order:

#### Check 1: Frontmatter Validity
For every directory in `C:\Users\DaveWitkin\.config\opencode\skill\` containing `SKILL.md` (skip `_*` dirs):
- `name:` exactly matches directory, matches regex `^[a-z0-9]+(-[a-z0-9]+)*$`
- `description:` 1-1024 chars, non-empty
- **Action**: Flag only (FRONTMATTER_ISSUE).

#### Check 2: Global Skills Index Freshness
Read `C:\development\opencode\docs\reference\global-skills-index.md`:
- **Stale names** (entry exists but name is old): **Auto-fix** via safe string replacement.
- **Missing skills** (not in index at all): **Flag only** (INDEX_MISSING) because the agent should not guess which Markdown table category to inject it into.

#### Check 3: Junction Consistency
For every skill directory in the canonical path:
- **Action**: **Auto-fix** missing junctions in `.codex\skills` and `.agents\skills` using `New-Item -ItemType Junction`.

#### Check 4: Archive Hygiene
For every item in `C:\Users\DaveWitkin\.config\opencode\_archived_skills\`:
- **Action**: **Auto-fix** orphaned junctions by removing them from `.codex\skills` and `.agents\skills`.

#### Check 5: Report Generation (Anti-Bloat Strategy)
- Overwrite `C:\development\opencode\docs\reports\skill-health-latest.md` with full details.
- Append a 1-line summary to `C:\development\opencode\docs\reports\skill-health-log.csv` (Date, Status, Auto-fixes count, Flags count).

#### Check 6: Output Contract
Must follow `scheduled-job-best-practices` and end the console output with:
- Status: success | skipped | failed
- Reason: (1 line)
- Outputs written: (paths)

### The Cross-Surface Map
- Canonical skill store: `C:\Users\DaveWitkin\.config\opencode\skill\`
- Codex skills: `C:\Users\DaveWitkin\.codex\skills\`
- `.agents` skills: `C:\Users\DaveWitkin\.agents\skills\`
- Archived skills: `C:\Users\DaveWitkin\.config\opencode\_archived_skills\`
- Global index: `C:\development\opencode\docs\reference\global-skills-index.md`

### Exclusions
- Package-managed skills (e.g., `snippets` from npm cache) — validate only index presence, no junctions.
- Project-local skills — out of scope.

## Acceptance Criteria
- Validator prompt file exists, is self-contained, includes `@scheduled-job-best-practices`, and enforces the output contract.
- Scheduled job JSON uses a simple bootstrap prompt to load the file, avoiding JSON escaping issues.
- Manual test run overwrites `latest` report and appends to `log.csv`.
- Index missing skills are flagged, not auto-fixed. Index renames are auto-fixed.
