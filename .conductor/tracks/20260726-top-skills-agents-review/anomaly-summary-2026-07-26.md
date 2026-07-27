# Anomaly Summary — Top Skills and Agents Portfolio

- **Track:** `20260726-top-skills-agents-review`
- **Source of truth:** `C:\development\opencode\.conductor\logs\pipeline-anomalies.jsonl` (append-only JSONL)
- **Anomalies for this track:** 6

| ts | stage | type | severity | detail |
|---|---|---|---|---|
| 2026-07-26T21:40:50Z | stage-2 | deviation | warn | First review scored 22/100; plan and evidence-contract corrections applied before execution. |
| 2026-07-26T21:52:41Z | stage-3 | deviation | warn | Conditional re-review scored 63/100; manual correction closed RR-B1..RR-B5 before Stage 5. |
| 2026-07-26T23:10:00Z | stage-5 | tool-error | warn | `opencode models` hung; live route/smoke evidence was honestly recorded Unverified. |
| 2026-07-26T00:00:00Z | stage-7 | tool-error | info | Initial bounded backup check used a nonexistent helper name; corrected to `_tree_hash`; no mutation or conclusion was affected. |
| 2026-07-26T00:00:01Z | stage-7 | tool-error | info | PowerShell 5.1 rejected `Get-Date -AsUTC`; report generation used a compatible UTC fallback. |
| 2026-07-26T22:57:02Z | stage-7 | deviation | warn | Current clickup tree contains two unclaimed generated pyc files and differs from `change-manifest.json`; narrow-diff evidence is stale. |

No raw message bodies, secrets, or external-action results are included.