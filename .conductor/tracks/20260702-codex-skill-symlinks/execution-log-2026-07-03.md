# Execution Log - 2026-07-03 - Track 20260702-codex-skill-symlinks

Executor model: glm-5.2 (zai-coding-plan/glm-5.2)
Stage: 4 (conductor-track-executor)
Final status: BLOCKED at Phase M (rolled back; no data loss)

## Summary

Execution was HALTED at Phase M because the running OpenCode desktop host
(OpenCode.exe, multiple processes) actively reconciles the .opencode-lazy-vault
and .codex\skills directories and interferes with the manual junction
restructuring that Phase M requires. This is the SAME root cause that the prior
track 20260702-skill-vault-migration already hit and documented ("nlm-skill and
pptx-to-pdf-converter ROLLED BACK to native due to active external interference
destroying their pre-existing vault folders"). Per the executor hard rules
("stop and report if any acceptance check fails"; "if destructive, STOP and
notify; never guess"), I rolled nlm-skill back to its original stable topology
and stopped BEFORE any destructive native deletion (M.9) or the pptx migration
(M.10-M.16).

## Tasks completed this run (2/43)

- [x] M.1 Create the Phase M backup directory marker.
       - Marker: phase-m-backup-dir.txt
         -> backups\phase-m\2026-07-03-130236-pre-edit
         (deviation: plan used backups\<stamp>-pre-edit; I added a phase-m\
         subfolder. Cosmetic; all tasks read the marker file, so resolution is
         unaffected.)
- [x] M.2 Back up native nlm-skill.
       - Backup: nlm-skill-native (SKILL.md present). Intact.

## Tasks attempted then ROLLED BACK (M.3-M.8)

M.3 through M.8 were executed successfully against nlm-skill (vault junction
broken, native copied to vault as a real folder, version: line removed from
vault frontmatter, quick_validate.py returned "Skill is valid!", codex repointed
to vault). They were then REVERTED because the host corrupted the state (see
Root Cause). Their checkboxes have been reset to [ ] in plan.md. The end state
of Phase M was NOT achieved.

## Root cause of the block

While OpenCode desktop is running, it reconciles the vault and codex skill
stores. During my nlm-skill migration it did two things that defeat the plan:

1. After M.5 (vault nlm-skill became a real folder), the host re-created the
   vault entry as a SELF-REFERENTIAL junction (target =
   C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill, i.e. itself), which is
   unresolvable ("The name of the file cannot be resolved by the system").
   Confirmed via fsutil reparsepoint query.
2. It MATERIALIZED then DELETED the codex nlm-skill junction in real time
   (codex\SKILL.md and the codex junction appeared/disappeared between my own
   commands; my commands only touched one path at a time, so the other path was
   changed by an external actor). Multiple OpenCode.exe processes were running
   and DCP context logs show continuous activity.

Evidence: fsutil reparsepoint query showed the self-loop reparse data; process
list showed OpenCode.exe instances (PIDs incl. 58876 + utility/renderer
children) plus Antigravity IDE; the prior track ledger note confirms this is a
recurring environmental issue for these two skills specifically.

After I restored the ORIGINAL topology (codex junction -> native AND vault
junction -> native), both junctions held stable through a 25-second observation
window. Conclusion: the host is stable with junction->native but fights any
deviation (real vault folders), which is exactly what Phase M requires.

## Final filesystem state (verified)

nlm-skill and pptx-to-pdf-converter are BOTH back to the original stable state:
- codex\<skill>      : junction -> native   (resolves, SKILL.md present)
- vault\<skill>      : junction -> native   (resolves, SKILL.md present)
- native skill folder: real folder, intact   (SKILL.md present, version line
                       unchanged on native because the migration was reverted)
All four skills resolve (codex\SKILL.md = True). No data lost.
pptx-to-pdf-converter was never touched by this run.

## Backups retained (under backups\phase-m\2026-07-03-130236-pre-edit)

- nlm-skill-native              (M.2 backup of native)
- nlm-skill-codex-real          (M.8 backup of a codex real folder)
- nlm-skill-codex-real-rollback (rollback-time codex real folder copy)
- nlm-skill-vault-real-rollback (rollback-time vault real folder copy)
Note: vault real folder copies still contain the unsupported version: frontmatter
line because the rollback re-derived them from native before the version edit
could be re-applied. These are rollback insurance only, not the live source.

## Validation performed

- quick_validate.py on vault nlm-skill REAL folder PASSED ("Skill is valid!")
  at M.7, BEFORE the host corrupted it and before rollback.
- After rollback: codex and vault junctions -> native verified IsRp=True with
  correct targets and SKILL.md=True for BOTH nlm-skill and pptx-to-pdf-converter.
- 25-second stability observation of restored junctions: no churn.

## Changed files this run

- plan.md : M.1, M.2 checked; M.3-M.8 reverted to unchecked; BLOCKER note added
            under the Phase M header.
- phase-m-backup-dir.txt : created (Phase M backup root marker).
- phase-m-nlm-vault-state.json : created (now STALE - records the pre-rollback
  vault state; ignore on retry, M.3 regenerates it).
- backups\phase-m\<stamp>-pre-edit\ : created with the four nlm backups above.

## Files NOT created (later phases not reached)

Phases 0, 1, 2, 3, 4, 5, 6, Final were not started:
- No precondition-paths.json, inventory-before.json, canonical-target-map.json.
- No _shared-scripts\codex-skill-junction-reconcile.ps1 (Phase 4).
- No scheduler job JSON (Phase 5).
- No CODEX-SKILL-JUNCTION-RUNBOOK.md, no SKILL-SYNC-SETUP.md annotation (Phase 6).
- No final reconciliation report / dangling-junction check (Final Phase).

## Recommendation / handover (Tier 0 - environmental, requires user action)

1. FULLY QUIT the OpenCode desktop app (all OpenCode.exe processes) before
   retrying Phase M, so nothing concurrently mutates .opencode-lazy-vault or
   .codex\skills. The host's reconciliation is what destroys these two skills'
   vault entries (confirmed recurring across two tracks).
2. Consider a deeper investigation into WHY opencode-skillful specifically
   destroys nlm-skill and pptx-to-pdf-converter vault entries (they are the only
   two affected; the other 71 vault skills are stable). Until that root cause is
   fixed, any retry will likely fail the same way.
3. After the host is quit, re-run Phase M (M.3-M.16) in plan order. The retained
   backups and the M.1-M.2 prep remain valid; M.3 regenerates its state JSON.
4. Do NOT run M.9 / M.16 (native deletions) while the host is running - the plan's
   ordering mitigation assumes no concurrent actor, which is currently violated.

## Issues / deviations classification

- Tier 0 (environmental, user action required): OpenCode desktop host actively
  reconciles skill stores and corrupts/deviates Phase M state. Same root cause as
  prior track 20260702-skill-vault-migration. BLOCKER for this track.
- Minor (cosmetic): Phase M backup root path uses a phase-m\ subfolder vs the
  plan's flat path; marker file resolves it. Documented, no impact.
- No model/provider failures this run.
