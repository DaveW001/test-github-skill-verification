# Plan: Skill Health Validator — Scheduled Job

## Phase 1 - Create the Validator Prompt
- [x] Created `C:\Users\DaveWitkin\.config\opencode\scripts\skill-health-validator.md`
- [x] Includes `@scheduled-job-best-practices` directive
- [x] All 5 checks + output contract + idempotency rules
- [x] Safety rules: auto-fix renames, flag-only for missing index + bad frontmatter

## Phase 2 - Create the Scheduled Job
- [x] Created `development-skill-health-validator.json` in development scope
- [x] Schedule: `0 6 * * *` (daily at 6 AM)
- [x] Timeout: 300 seconds
- [x] Uses bootstrap prompt to load the validator markdown file

## Phase 3 - Manual Test Run
- [x] Check 1 (Frontmatter): 1 flag — `clickup-cli` has frontmatter name `clickup` (mismatch)
- [x] Check 2 (Index): 0 missing entries — all skills indexed correctly
- [x] Check 3 (Junctions): 47 auto-fixed — massive gap in .agents surface (most skills had no link)
- [x] Check 4 (Archive): 0 orphaned links
- [x] Check 5 (Reports): `skill-health-latest.md` written, `skill-health-log.csv` appended

## Phase 4 - Verify Scheduled Job Registration
- [x] JSON validates, matches schema, schedule confirmed `0 6 * * *`

## Phase 5 - Conductor Sync
- [x] Plan updated
- [x] Metadata updated

Checkbox states:
- [ ] Pending
- [~] In Progress
- [x] Completed
