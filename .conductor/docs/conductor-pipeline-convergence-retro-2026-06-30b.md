# Conductor Pipeline Convergence Retrospective - 2026-06-30 (Round 2)

## Summary

This retrospective evaluates the Conductor pipeline by comparing two consecutive pipeline-on-pipeline improvement runs. **Round 1** (`20260629-conductor-pipeline-retro-improvements`) made the first wave of improvements. **Round 2** (`20260630-conductor-skill-hardening`) implemented the remaining items identified by a retro on round 1. The central question: **did the round-1 improvements actually make the pipeline more effective, or are we cycling through the same issues in different forms?**

The answer is **converging, with one structural limitation**. Round-1 improvements in body-content verification, dry-run enforcement, and metadata clarity all demonstrably helped in round 2. However, Stage 1 (plan creation) still produces the same *class* of PowerShell verification bugs — because Stage 1 cannot benefit from references it is itself creating (a bootstrapping paradox). The self-improvement loop shows diminishing returns and should shift from "run the pipeline on itself" to "feed new references into the Stage 1 prompt so future plans avoid the pitfalls from the start."

## Scope

**Scope B — Convergence comparison.** Compare round 2 (`20260630-conductor-skill-hardening`) against round 1 (`20260629-conductor-pipeline-retro-improvements`) to measure whether round-1 improvements moved the needle and whether the self-improvement loop is converging or cycling.

### Evidence base
- Round 1: spec, plan, 2x review reports, execution log, validation report under `...\tracks\20260629-conductor-pipeline-retro-improvements\`
- Round 2: spec, plan, review report, execution log, validation report under `...\tracks\20260630-conductor-skill-hardening\`
- Prior retro: `...\docs\conductor-pipeline-run-retro-2026-06-30.md`

### Round-by-round metrics at a glance

| Metric | Round 1 | Round 2 | Trend |
|---|---|---|---|
| Tasks in plan | 29 | 11 | Smaller scope (remaining items only) |
| Phases | 6 | 5 | Simpler structure |
| Stage 1 readiness before review | 68% | 73% | Slight improvement |
| Blocking bugs found by Stage 2 | 1 | 3 | More found (but plan was smaller; density higher) |
| Blocking bug class | `-like` bracket wildcard | `-notlike` bracket wildcard + backtick parser error | **Same class, different instance** |
| Stage 2 readiness after fixes | 92% | 100% | Improvement |
| Stage 3 triggered? | YES (structural change: +5 ACs) | NO (no structural change) | Correct gating both times |
| Stage 3 found new regression? | YES (Task 5.3 invalid regex) | N/A (skipped) | — |
| Stage 4 deviations | 2 (PowerShell method adaptations) | 4 (tool fallback, code-span, placement, metadata creation) | More documented but less severe |
| Stage 4 blocking failures | 0 | 0 | Clean both times |
| Stage 5 verdict | Ready to close | Ready to close | Clean both times |
| Stage 6 triggered? | NO | NO | Correct gating both times |
| Body-content verification from start? | NO (8+ shallow checks fixed in review) | YES (all tasks had multi-substring checks) | **Converging** |
| Authoritative/diagnostic separation? | NO (added in review) | YES (labeled in plan from creation) | **Converging** |
| Metadata count confusion? | YES (29 tasks vs 37 checkboxes) | NO (task_count=11, readiness=6, total=17) | **Converging** |

---

## 1. What Went Well

### Round-1 improvements demonstrably helped
The six improvements codified in round 1 were put to the test in round 2. Five of six showed measurable benefit:

1. **Body-content verification** — Round 2's plan author (gpt-5.5) produced body-content checks from the start. Every task named multiple required substrings, not just headings. Round 1 had 8+ shallow heading-only checks that the reviewer had to strengthen. The improvement took hold at the authoring stage, not just the review stage.
2. **Authoritative/diagnostic check separation** — Round 2's plan explicitly labeled `Authoritative acceptance check:` and `Diagnostic checks:` on every task. This was a round-1 recommendation that the plan author internalized.
3. **Reviewer dry-run enforcement** — Round 2's reviewer (minimax-m3) dry-ran every verification command it added or modified, catching 3 Blocking PowerShell bugs before execution. Round 1's reviewer also dry-ran but the enforcement was newly codified; by round 2 it was standard practice.
4. **Metadata schema clarity** — Round 2's metadata.json immediately used the new `task_count`/`readiness_check_count`/`total_checkbox_count` fields. No more 29-vs-37 confusion. The validator reported all counts separately and they were consistent.
5. **Literal matching preference** — Round 2's reviewer fixed bugs by switching to single-quoted `.Contains()` (literal substring matching), exactly the pattern the round-1 retro recommended. Round 1's fix used `-match` regex, which itself introduced a regression caught by Stage 3.

### Threshold gating worked perfectly across both rounds
- Round 1 Stage 3 triggered correctly (structural change: +5 acceptance criteria forced a second review pass) and caught a Stage 2 regression.
- Round 2 Stage 3 skipped correctly (no structural change, 100% readiness, no unresolved Blockings).
- Both rounds' Stage 6 skipped correctly (clean validations).

### Model diversity provided genuine independent verification
- minimax-m3 (reviewer/validator) caught PowerShell bugs that gpt-5.5 (creator) produced in both rounds. Different model families have different blind spots, and the diversity gate exploited this effectively.
- glm-5.2 (executor) executed cleanly in both rounds without introducing new defects.

### The pipeline caught its own defects before closeout
The multi-stage design prevented defective verification commands from reaching execution in both rounds. No run has ever closed with a blocking defect undetected.

---

## 2. What Could Be Improved

### The bootstrapping paradox: Stage 1 cannot benefit from references it creates
Round 2's plan was to create a `powershell-pitfalls.md` reference. But the plan's own verification commands contained the exact PowerShell pitfalls the reference documents — `-notlike` with bracket wildcards, backtick parser errors. Stage 1 (gpt-5.5) had no access to the reference because it didn't exist yet. **The self-improvement loop has a structural delay: improvements take effect one cycle later, never in the cycle that creates them.**

### Stage 1 still produces PowerShell verification bugs (same class, different instance)
| Round | Bug | Root cause |
|---|---|---|
| 1 | `Where-Object { $_ -like '*[track-id]*' }` throws WildcardPatternException | `[`/`]` are wildcard char classes in `-like` |
| 2 | `-notlike "*[regex]::Escape()*"` silently reports false-negative | Same: `[`/`]` are wildcard char classes in `-notlike` |
| 2 | `` "`completed_tasks`..." `` parser error (unterminated string) | Backtick before `"` escapes the closing quote |
| 2 | `` `t `` in double-quoted strings becomes tab | Backtick escape interpretation |

The class is consistent: **PowerShell wildcard and backtick interpretation in verification commands.** Round 1's fix was `-match` regex (which itself broke in Stage 3). Round 2's fix was single-quoted `.Contains()` (which worked cleanly). The knowledge of which fix works is now codified in the pitfalls reference — but only after the fact.

### Plan body vs. acceptance check inconsistency
Round 2 Task 3.1 specified a body block with `` `$text.Replace($old, $new)` `` (2 backticks, space after comma) but its acceptance check required `` `$text.Replace(`$old,`$new) `` (3 backticks, no space, escaped dollars). The executor had to reconcile this discrepancy by writing the body to match the check. This is a plan-authoring quality issue: **the body specification and the verification check should agree on exact literals before the plan leaves Stage 1.**

### Orchestrator token cost is high
Each subagent handoff required a self-contained prompt with full context (artifact paths, stage prompt text, tool preflight, target file details, prior state). These prompts ranged from ~800 to ~2000 words each. For a simple 11-task documentation plan, the total orchestrator overhead was substantial. This is inherent to the self-contained-handoff design but worth noting as a scaling concern.

### The `Bun is not defined` issue persists as infrastructure debt
Identified in round 1. "Fixed" by propagation in stage prompts. Still occurred in every stage of round 2. The propagation reduces rediscovery cost (subagents switch to PowerShell-first immediately) but does not fix the root cause. Every stage still pays the adaptation tax.

---

## 3. What To Do Differently Next Time

### Stop running the pipeline on itself — feed references forward instead
The self-improvement loop has reached diminishing returns. Round 1 found systemic issues and codified fixes. Round 2 implemented the remaining items but found no NEW systemic issues — only the same PowerShell verification bug class in a new instance. **The next improvement should not be another pipeline-on-pipeline run.** Instead:
- Add a reference to `powershell-pitfalls.md` in the Stage 1 prompt so plan authors read it before writing verification commands.
- Add a reference to `global-skill-versioning.md` in the Stage 4 prompt so executors follow backup practices from the start.
- This shifts from reactive (Stage 2 catches bugs) to preventive (Stage 1 avoids bugs).

### Require plan body and acceptance check to be cross-validated in Stage 1
Before a plan leaves Stage 1, every acceptance check should be dry-run against the body text it claims to verify. If the body says `` `$text.Replace($old, $new)` `` and the check looks for `` `$text.Replace(`$old,`$new) ``, the mismatch should be caught at creation, not execution. This can be a Stage 1 self-check requirement.

### Consider a Stage 1 "PowerShell safety lint" for verification commands
A simple check: if a verification command uses `-notlike` or `-like` with patterns containing `[`, `]`, or backticks, flag it for review. This would have caught all 3 Blocking bugs in round 2 and the 1 Blocking bug in round 1 before they reached Stage 2.

### Accept that some improvements are infrastructure, not process
The `Bun is not defined` issue is not a pipeline process problem — it is an OpenCode runtime/sandbox problem. The pipeline correctly propagates the workaround, but the fix belongs in the runtime layer, not in more pipeline documentation.

---

## 4. Systemic Issues

### The self-improvement loop has a one-cycle delay
Improvements created in cycle N take effect in cycle N+1, never in cycle N. This is inherent to the bootstrapping pattern. The mitigation is to make the delay explicit and plan for it: when creating a new reference, immediately add a forward-reference in the relevant stage prompt so the NEXT plan-creator session reads it.

### Verification commands are code, and code has bugs
Both rounds confirmed that PowerShell verification snippets in plans are executable code that can have syntax errors, wildcard interpretation bugs, and escape-sequence issues. The pipeline treats plan tasks as specifications, but verification commands are really small programs. They need the same dry-run discipline as any code — which is exactly what the round-1 dry-run enforcement codified. The system is working as designed; the remaining gap is at the authoring stage.

### Orchestrator context-gathering is manual and token-expensive
The orchestrator (this session) had to read retro docs, prior track artifacts, skill files, stage prompts, and threshold policies before each stage to write a self-contained handoff prompt. There is no mechanism for the orchestrator to delegate context-gathering — it must do it inline. This limits the pipeline's scalability to larger, more complex tracks.

### Global skill files remain unversioned outside git
Round 2 created the `global-skill-versioning.md` reference documenting the backup pattern, but the underlying issue persists: files under `C:\Users\DaveWitkin\.config\opencode\skill\` have no git history. Every edit relies on manual `.pre-edit.bak` copies. A structural fix (symlinking global skills into the repo, or a dedicated git repo for skills) would eliminate this entire class of risk.

---

## 5. Lessons Learned

1. **Convergence is real but slow.** Round 2 was measurably better than round 1 in plan structure (body-content checks from creation, authoritative/diagnostic separation, metadata clarity). But the improvement cost two full pipeline runs plus two retrospectives. The cost-benefit ratio is declining.

2. **The highest-value improvements are now preventive, not reactive.** The pipeline's reactive defenses (Stage 2 dry-run, Stage 5 independent validation) are working well. The remaining gap is at Stage 1 — plan authors still produce verification bugs. Feeding the new references into the Stage 1 prompt is the next high-value move.

3. **PowerShell wildcard/backtick pitfalls are the dominant bug class in this pipeline.** Across both rounds, every Blocking bug in Stage 1 plans was a PowerShell `-like`/`-notlike`/backtick issue. This is now documented in `powershell-pitfalls.md`, but the reference needs to reach the plan author before it writes verification commands.

4. **Threshold gating is well-calibrated.** Across four gating decisions (two Stage 3, two Stage 6), every decision was correct. The B+C and A+C hybrid triggers neither over-triggered nor under-triggered.

5. **Model diversity provides genuine value, not just compliance.** minimax-m3 consistently caught bugs that gpt-5.5 produced. This is not a formality — it is the pipeline's primary defect-detection mechanism for plan-authoring bugs.

6. **A successful closeout can still reveal systemic improvements.** Both runs validated cleanly. The retro still found actionable improvements. This validates the practice of conducting retros even on clean runs.

7. **The self-referential paradox is instructive, not problematic.** The plan to create a PowerShell pitfalls reference contained PowerShell pitfalls. This is not a failure — it is evidence that the pitfalls are common enough to warrant a reference, and that the reference will be useful once it reaches the authoring stage.

---

## 6. Codify / Reuse

### High priority (do next, without another pipeline run)
1. **Forward-reference `powershell-pitfalls.md` in the Stage 1 prompt.** Add a line in `stage-prompts.md` Stage 1 section: "Before writing PowerShell verification commands, consult `references/powershell-pitfalls.md` for common wildcard and backtick traps." This is a one-line edit that prevents the dominant bug class at the source.
2. **Forward-reference `global-skill-versioning.md` in the Stage 4 prompt.** Add a line in `stage-prompts.md` Stage 4 section pointing executors to the versioning reference before editing global files.
3. **Add a Stage 1 self-check requirement: body and acceptance check must agree on exact literals.** One sentence in the Stage 1 prompt: "Before finalizing a task, verify that every literal substring in the authoritative acceptance check appears verbatim in the body text the task produces."

### Medium priority (next pipeline run on a real task)
4. **Add a "PowerShell safety lint" note to the Stage 2 reviewer prompt.** Tell the reviewer to specifically flag `-notlike`/`-like` patterns containing `[`, `]`, or backticks as high-risk verification commands requiring dry-run.
5. **Consider an orchestrator context-budget metric.** Track total tokens consumed by orchestrator handoff prompts vs. subagent execution. If the ratio exceeds a threshold, flag the track as "orchestrator-heavy" and consider simplification.

### Low priority (structural, not urgent)
6. **Evaluate symlinking global skills into the repo** so they get git history. This would eliminate the unversioned-files risk class entirely and make the `global-skill-versioning.md` backup pattern unnecessary.
7. **Consider a dedicated Conductor issue log for non-blocking process observations** across pipeline runs, so patterns are aggregated over time rather than rediscovered per retro.

### Explicitly NOT recommended
- **Do not run a third pipeline-on-pipeline improvement round.** Round 2 found no new systemic issues beyond what round 1 already identified. The remaining improvements (items 1-3 above) are simple edits that do not need the full 6-stage pipeline. The self-improvement loop has converged for now; the next pipeline run should be on a real task to validate that the forward-references actually help.

---

## Recommended Priority Order

1. Forward-reference `powershell-pitfalls.md` in Stage 1 prompt (prevents dominant bug class).
2. Forward-reference `global-skill-versioning.md` in Stage 4 prompt (prevents unversioned-edit risk).
3. Add Stage 1 body/check literal-agreement self-check (prevents code-span reconciliation issues).
4. Add Stage 2 PowerShell safety lint note (catches residual bugs that slip past item 1).
5. Run the pipeline on a real task to validate that forward-references help.
6. Evaluate structural fixes (git-tracked skills, orchestrator budget metric).

---

## Validation

- Confirmed round 1 validation report: `Ready to close`, no mismatches, all 29 tasks + 8 readiness items checked.
- Confirmed round 2 validation report: `Ready to close`, no mismatches, all 11 tasks + 6 readiness items checked.
- Confirmed round 1 Stage 2 found 1 Blocking + 12 needs-work; Stage 3 found 1 regression.
- Confirmed round 2 Stage 2 found 3 Blocking; Stage 3 correctly skipped.
- Confirmed threshold gating: 4/4 correct decisions across both rounds.
- Confirmed `Bun is not defined` affected every stage of both rounds despite propagation.
- Confirmed metadata schema improvement (`task_count`/`readiness_check_count`/`total_checkbox_count`) was immediately applied in round 2's metadata.json.
