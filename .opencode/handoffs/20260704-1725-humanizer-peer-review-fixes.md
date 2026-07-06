# Session Handoff: Fix humanizer skill peer review issues

## Original Session

- Title: 2026-07-04 Review SkillShare Skills for Quality
- Session ID: ses_0d1dfb63affeuabFNBvYMv18Tm
- Repo: C:\development\opencode
- Watermark: 2026-07-04T17:01:24 (peer review completed)

## Recovered Goal

Fix the 8 issues identified in the peer review of the humanizer skill improvement work. The peer review returned "Accept with minor fixes" and recommended 7 concrete fixes to the humanizer skill files and the re-humanized test artifact.

## Work Already Done

### Completed (in original session, before peer review)
- Fixed PDF deliverable (logo path, font paths, running() CSS) - skillshare-test-v2.pdf at `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\markdown-pdf\publication\dist\`
- Researched AI writing tells (Bloomberry AI Sentence DNA, Vollmer's Field Guide, Kobak et al. 2025, EyeSift 2026)
- Expanded humanizer skill from 9 to 22 pattern categories in ai-patterns-to-fix.md
- Expanded humanization-checklist.md to 25+ verification items
- Expanded brand-voice.md with 15 voice rules and Kobak excess word list
- Updated SKILL.md with signal stacking principle and 8-step workflow
- Re-humanized after.md (but this introduced new issues - see below)

### Peer Review Completed (Accept with minor fixes)
The peer review verified all expanded skill files exist and contain real content. It independently verified the humanizer metrics (burstiness, markers, em-dashes). But it found 8 issues requiring fixes.

## Successor Sessions Reviewed

| Session Title | Session ID | Relevant? | Finding |
|---|---|---|---|
| Pipeline skillshare-rollout-improvements | ses_0d19350c5ffekO9a6QBKKu4NrV | Partially | Addressed SkillShare ROLLOUT/documentation/portability gaps, NOT the humanizer skill quality issues. Performed a portability audit of humanizer (checking for hardcoded paths, Dave refs) but did NOT touch the 8 peer-review issues below. |
| Peer Review Skill migration handoff | ses_0d5dc5f6dffe9JJBeutG1SekuY | No | About Codex skill symlinks migration. |
| Verify peer-review file read | ses_0d1099f4effeQfRYHARCuJ8ABv | No | About peer-review agent file-read capability. |
| Pipeline Restore opencode-scheduler plugin | ses_0d1b723eeffeLJq5lUf94sk5Q0 | No | About opencode-scheduler plugin restoration. [ARCHIVED] |
| Peer Review Agent Fix | ses_0d1e84ab8ffef9x5gnMxmOB2Kq | No | About fixing peer-review agent Bun-is-not-defined issue. |
| Pipeline Fix Scheduled Email Triage Tasks | ses_0d0fde053ffeXHI5sdfm9ENqOS | No | About scheduled email triage tasks. |

## Current Status: Issues STILL UNFIXED

Verified on 2026-07-04 by checking file contents and modification times. No humanizer files were modified after the peer review (~5:00 PM). The 8 issues remain:

### MAJOR ISSUES (must fix)

**1. after.md fails its own checklist on short sentence stacks.**
- File: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md`
- Current state: 3 short sentence stacks (4 consecutive <12 word sentences each)
- Stack locations: (a) "Six weeks, every time..." / "Nothing moved." / "The fix is boring." block; (b) "Then do it again." / "If the numbers move, keep going." / "Go find the real one." block; (c) "Choose a value stream..." / "Map it end to end..." / "The bottleneck will introduce itself." block
- Checklist requirement: 0 short sentence stacks
- Fix: Rewrite these sections to break up the short-sentence runs by combining sentences or adding longer connective tissue

**2. measure-humanizer.ps1 has zero coverage of the 22 new pattern categories.**
- File: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1`
- Current state: Only checks 3 original metrics (burstiness, coherence markers, em-dashes)
- Fix: Add at least 5 programmatic pattern checks: short sentence stack detection, hook formula opener detection, Kobak excess word count, resolution closer detection, rhetorical contrast detection

**3. Triple contradiction on "Here's the thing."**
- brand-voice.md Rule 7: lists "Here's the thing" as a natural transition (endorsement)
- brand-voice.md banned phrases: says "vary your opener"
- ai-patterns-to-fix.md Pattern 10: lists "Here's the thing" as Observer Opener AI tell (prohibition)
- Fix: Pick ONE recommendation. Recommended: remove from brand-voice.md Rule 7 (endorse it as banned per ai-patterns-to-fix.md Pattern 10)

**4. Em-dash contradiction in brand-voice.md Rule 3 (Line 16).**
- Says "Avoid em dashes" then immediately "If you use an em dash, make it a sharp interruption"
- Fix: Reword to a single clear position. Recommended: "Use em dashes sparingly, only for sharp interruptions. Never for explanatory clauses."

### MINOR ISSUES (should fix)

**5. Kobak excess word list desync.**
- humanization-checklist.md has 26 Kobak words; brand-voice.md only lists a partial subset
- Fix: Synchronize to the full 26-word list in both files

**6. summary.md and metrics-report.md claim "AllPass: True" without checking 22 new patterns.**
- File: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\summary.md` and `metrics-report.md`
- Fix: Update claims after issues 1 and 2 are fixed; re-run the full measurement suite

**7. No programmatic signal density counter.**
- Previous agent claimed a "signal density counter" but the script only checks 3 metrics
- Fix: Issue 2 addresses this

**8. Checklist has no prioritization.**
- humanization-checklist.md has 25+ items with no quick high-signal subset
- Fix: Add a "top 5 high-signal checks" callout at the top

## Next Steps

1. **Fix after.md** - Rewrite the 3 short-sentence-stack sections to break up the runs while preserving PA voice and meaning
2. **Update measure-humanizer.ps1** - Add at least 5 programmatic checks for the new pattern categories (short sentence stacks, hook openers, Kobak words, resolution closers, rhetorical contrast)
3. **Resolve the 3 contradictions** in brand-voice.md and ai-patterns-to-fix.md ("Here's the thing", em-dash rule, Kobak word list)
4. **Add prioritization** to humanization-checklist.md (top 5 high-signal checks)
5. **Re-run the measurement suite** on the fixed after.md and verify all checks pass
6. **Update summary.md and metrics-report.md** with accurate AllPass claims
7. **Document the out-of-band skill improvement** in the test-skillshare-skills execution log
8. **Push the humanizer skill changes to GitHub** (currently only in temp clone at `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\`)

## Key Artifact Paths

### Humanizer skill files (in temp clone, NOT pushed to GitHub)
- SKILL.md: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\SKILL.md`
- ai-patterns-to-fix.md: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\ai-patterns-to-fix.md`
- brand-voice.md: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md`
- humanization-checklist.md: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\humanization-checklist.md`

### Humanizer test artifacts (need fixes)
- after.md: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md`
- measure-humanizer.ps1: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1`
- metrics-report.md: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\metrics-report.md`
- summary.md: `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\summary.md`

### Peer review report
- `C:\Users\DaveWitkin\.local\share\opencode\tool-output\` (search for the peer-review output from ses_0d1dfb63affeuabFNBvYMv18Tm around 17:00-17:01)

### Conductor track (original test pipeline)
- Track dir: `C:\development\opencode\.conductor\tracks\test-skillshare-skills\`
- Execution log: `C:\development\opencode\.conductor\tracks\test-skillshare-skills\execution-log-2026-07-04.md`

## Suggested Fresh-Session Prompt

Continue this work using the handoff doc at C:\development\opencode\.opencode\handoffs\20260704-1725-humanizer-peer-review-fixes.md.
