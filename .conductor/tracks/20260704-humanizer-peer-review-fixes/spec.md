# Spec: Humanizer Peer Review Fixes

Track id: `20260704-humanizer-peer-review-fixes`
Created: 2026-07-04
Workspace root: `C:\development\opencode`

## Goal / outcome
Fix the eight concrete peer-review findings for the expanded Packaged Agile `humanizer` skill, re-run and ground the measurement suite in the new checks, document the out-of-band improvement in the existing test track log, and commit/push the humanizer skill changes from the temp skill repo.

## Constraints / non-goals
- File tools are shell-first for downstream agents: use PowerShell 7+ through shell commands; do not rely on native Read/Edit/Write/glob/grep if they return `Bun is not defined`.
- Keep every shell/network command bounded and non-interactive; no `Read-Host`, `Wait-Process`/`-Wait`, `tail -f`, `Start-Process -Wait`, uncapped servers, or force push.
- Use exact Windows paths with `-LiteralPath` and double quotes.
- Active working set is under `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\`; do not relocate it.
- Do not re-expand beyond the existing 22 pattern categories.
- Do not touch the PDF deliverable or unrelated skills.
- Preserve Packaged Agile voice and meaning in `after.md`.
- Measurement edits must remain PowerShell 7+ compatible.

## Definition of done
- All eight review issues are fixed across the four humanizer skill files, `after.md`, and `measure-humanizer.ps1`.
- `measure-humanizer.ps1` includes at least five new pattern checks: short sentence stacks, hook formula opener, Kobak excess word count, resolution closer, and rhetorical contrast.
- Running the updated suite against fixed `after.md` reports zero short sentence stacks and `AllPass: True`.
- `summary.md` and `metrics-report.md` contain accurate claims grounded in the new checks.
- A dated section is appended to `C:\development\opencode\.conductor\tracks\test-skillshare-skills\execution-log-2026-07-04.md`.
- Humanizer skill changes are committed and pushed to `origin` from `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\` without amend or force-push.

## Source-of-truth files
Skill source repo:
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\SKILL.md`
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\ai-patterns-to-fix.md`
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\brand-voice.md`
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-skills\skills\humanizer\references\humanization-checklist.md`

Test artifacts:
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\after.md`
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\measure-humanizer.ps1`
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\metrics-report.md`
- `C:\Users\DAVEWI~1\AppData\Local\Temp\opencode\skillshare-tests\humanizer\summary.md`

## Required downstream anomaly handling
If a downstream executor/validator observes a permission prompt, tool error, model fallback, destructive ask, deviation, retry, push failure, or other anomaly, append exactly one JSONL line to `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` using the seven-key schema documented in `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\references\anomaly-logging.md`.
