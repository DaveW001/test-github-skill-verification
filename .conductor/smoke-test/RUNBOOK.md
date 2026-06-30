# Conductor Pipeline — Clean Smoke-Test Runbook

Purpose: run the six-stage `/conductor-pipeline` command **end-to-end with zero human interaction** to prove the pipeline, its model-diversity gates, and its saved permissions all work after a restart.

---

## Why the previous run (track `readme-hello-world-section`) was NOT clean

The test targeted an **out-of-repo, ambiguous** path. The request `skill\conductor-pipeline\README.md` resolved to two candidate locations:

1. `C:\development\opencode\skill\conductor-pipeline\README.md` — did NOT exist
2. `C:\Users\DaveWitkin\.config\opencode\skill\conductor-pipeline\README.md` — existed

Stage 2 (plan-reviewer) correctly hit the **"do not guess" stop rule** and paused to ask which copy to edit. That single human decision is the ONLY thing that broke full-auto. The pipeline itself behaved correctly — the test input was the problem.

## What makes this rerun clean

- **Fully-qualified, unambiguous target** — a brand-new file at a path with no sibling of the same name anywhere on disk.
- **Inside the workspace git repo** (`C:\development\opencode`) — so scope verification uses native `git diff` against a pre-edit backup (the designed happy path), not an out-of-repo workaround.
- **Trivial, reversible change** — append one documentation section.
- **Permissions already saved** — `edit: allow` + `bash: allow` on all four writer agents (plan-creator, plan-reviewer, plan-reviewer-alt, executor); validators are read-only by design. These load fresh after a restart, so **no approval prompts** should appear.

## What was set up (ready now)

| Artifact | Path |
|---|---|
| Smoke-test fixture (baseline, NO Hello World) | `C:\development\opencode\.conductor\smoke-test\hello-world.md` |
| Pristine baseline backup (for reset) | `C:\development\opencode\.conductor\smoke-test\hello-world.baseline.md` |
| This runbook | `C:\development\opencode\.conductor\smoke-test\RUNBOOK.md` |

The fixture currently contains 0 `## Hello World` headings.

---

## The exact command to run (Step 6)

After restart, paste this single request. It is deliberately unambiguous and scoped:

```
/conductor-pipeline Append one new Markdown section to the file C:\development\opencode\.conductor\smoke-test\hello-world.md (fully-qualified absolute path; this is the only file by that name anywhere on disk). Add a single heading `## Hello World` followed by exactly one prose paragraph of 3-6 sentences stating that the section is a toy / sanity-check documentation example created by the Conductor pipeline as a smoke test. Do not modify, remove, or reorder any existing content in that file, and do not touch any other file. The target lives inside the workspace git repo C:\development\opencode, so scope verification should use native git diff against a pre-edit backup.
```

---

## Numbered step-by-step

### 1. Confirm the fixture is at baseline
Run this in the CURRENT session (or any session). It must print `0` and show the baseline text:
```powershell
(Select-String -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" -Pattern '^## Hello World$').Count
```
If it prints `1`, the fixture was already modified — go to Step 2 to reset first.

### 2. Reset the fixture to baseline (only if Step 1 showed 1, or to guarantee reproducibility)
```powershell
Copy-Item -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.baseline.md" -Destination "C:\development\opencode\.conductor\smoke-test\hello-world.md" -Force
```

### 3. Quit OpenCode completely
OpenCode does **not** hot-reload agent/command/permission config. The saved permission fixes (`bash: allow`, `edit: allow`) only take effect after a full restart. Quit the current session now.

### 4. Restart OpenCode in the workspace
Reopen OpenCode rooted at `C:\development\opencode`. The `/conductor-pipeline` command, the orchestrator + 6 stage agents, and the `conductor-pipeline` skill must all load from the saved config.

### 5. Optional pre-flight: confirm the command + agents are registered
- The command file is `C:\Users\DaveWitkin\.config\opencode\commands\conductor-pipeline.md`.
- The 7 agents are in `C:\Users\DaveWitkin\.config\opencode\agent\` (orchestrator + 6 stages).
- You can sanity-check with `opencode` agent listing if available, or simply proceed — Stage 1 will fail loudly if an agent is missing.

### 6. Run the pipeline
Paste the exact command from **"The exact command to run"** above. Do NOT intervene unless a genuine stop condition fires (model unavailable, iteration cap, destructive/blocked task).

### 7. Watch for the CLEANLINESS success criteria (all must hold)
- [ ] **No approval prompts** for `bash` or `edit` on any of the 6 stages (Fix 5 verified).
- [ ] **No "which file do you mean?" ambiguity pause** in Stage 2 — the path is unambiguous, so the reviewer must NOT stop.
- [ ] **Diversity gates logged**: creator (gpt-5.5) != reviewer (minimax-m3); executor (glm-5.2) != validator (minimax-m3).
- [ ] **Stage 3 (re-review) and Stage 6 (re-validation) correctly SKIP** unless a real threshold fires.
- [ ] **Stage 4 execution** appends exactly one `## Hello World` section with one 3-6 sentence paragraph.
- [ ] **Stage 5 validation** independently re-runs the checks and returns a closeout verdict (ideally "Ready to close" with zero blockers).
- [ ] **Scope verified**: a pre-edit backup + `git diff`/`Compare-Object` shows ONLY additions to the fixture; no other repo file changed.

### 8. Inspect the outputs (all fully qualified Windows paths)
Expected under `C:\development\opencode\.conductor\tracks\<new-track-id>\`:
- `spec.md`, `plan.md`, `metadata.json`
- `review-report-<ts>.md`, `review-diff-summary-<ts>.md`
- `execution-log-<date>.md`
- `validation-report-<ts>.md`
- A pre-edit backup of the fixture (e.g. `hello-world.pre-edit.bak.md`)
- The modified target: `C:\development\opencode\.conductor\smoke-test\hello-world.md` (now has the section)

### 9. Verify the change manually
```powershell
# Exactly one heading
(Select-String -LiteralPath "C:\development\opencode\.conductor\smoke-test\hello-world.md" -Pattern '^## Hello World$').Count   # expect 1
# Scope: only the fixture changed in the repo
git -C "C:\development\opencode" status --porcelain
```

### 10. Optional teardown / re-arm for the next run
To run again, return to Step 2 (reset the fixture) and Step 3 (restart). The track folder from this run stays as a completed artifact.

---

## Troubleshooting

- **An approval prompt appears during a stage** → the permission fix did not load; confirm OpenCode was fully quit and restarted (Step 3-4), and re-check the agent files in `C:\Users\DaveWitkin\.config\opencode\agent\`.
- **Stage 2 still stops on ambiguity** → the request text was altered; use the exact string from "The exact command to run" verbatim.
- **"Bun is not defined" errors in a stage agent** → known runtime sandbox-init issue (Bun 1.3.4 is installed but sandbox init can fail). The executor should auto-switch to PowerShell-first via the `bash` tool. This is NOT an approval prompt and does not count as an unclean interaction; it is handled automatically per the AGENTS.md tool-failure protocol.
- **Validator returns "not-ready"** → do not re-run blindly; read `validation-report-<ts>.md`, then route back to execution once per the skill's failure rule.

---

## Clean-run summary card

| # | Check | Pass when |
|---|---|---|
| A | No human interaction | Pipeline reaches the final summary without asking you anything |
| B | No approval prompts | No `bash`/`edit` permission dialogs on any stage |
| C | Diversity preserved | 3 model families used; reviewer!=creator, validator!=executor |
| D | Correct stage skips | Stages 3 & 6 skip unless a real threshold triggers |
| E | Scope clean | Only the fixture file changed; additions-only vs. backup |
| F | Validation verdict | "Ready to close" or "Close with minor follow-ups", 0 blockers |

If A-F all pass, the pipeline is verified end-to-end and the 6 remaining runtime items from the build track are satisfied.
