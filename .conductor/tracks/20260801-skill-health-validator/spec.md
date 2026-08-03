# Spec

## Goal

Implement a safe, idempotent, non-interactive Skill Health Validator job for the seven always-on canonical OpenCode skills. It must audit frontmatter, reconcile the historical global index only for evidence-backed renames, respect the Codex parent-junction architecture, remove only archived-surface orphans safely, and produce a current Markdown report plus one-per-day CSV log row.

## Requirements

- [ ] Validate every eligible canonical skill's `SKILL.md` frontmatter, flagging—not rewriting—invalid name or description fields.
- [ ] Reconcile the global index deterministically: auto-fix only a precise, evidence-backed stale-name table-row replacement; flag missing canonical entries and index names without canonical directories; do not add new index entries.
- [ ] Detect whether `C:\Users\DaveWitkin\.codex\skills` is a reparse-point parent junction targeting `C:\Users\DaveWitkin\.opencode-lazy-vault`; when true, skip all Codex child-junction creation and emit no creation rows.
- [ ] In expected Codex parent-junction mode, suppress **all** Codex child operations: inspection, creation, reconciliation, and archive cleanup. Never invoke `rmdir` beneath the Codex root in that mode.
- [ ] Preserve the independent Agents-surface logic, while treating the absent/archived `.agents\skills` path as non-authoritative per the architecture runbook and never recreating it.
- [ ] Inspect archived skill names on Codex and Agents surfaces and auto-remove only confirmed orphan reparse-point links, using `cmd /c rmdir`; flag all real directories without removing them. Absence of `.agents\skills` is healthy and must not recreate the root.
- [ ] Derive archived names only from immediate child directories of `C:\Users\DaveWitkin\.config\opencode\_archived_skills`; a confirmed Agents orphan is an existing reparse-point child with the same name and a target outside the archive, while a real directory is never auto-removed.
- [ ] Treat the evidence-backed index rename map as empty unless a separately documented mapping is supplied; ambiguous or inferred renames are flags, never edits.
- [ ] Overwrite `C:\development\opencode\docs\reports\skill-health-latest.md` with the required report sections, date, counts, auto-fixes, flags, and one-sentence summary using UTF-8.
- [ ] Append exactly one CSV row for the run date to `skill-health-log.csv`, creating the specified header when absent and avoiding duplicate-date rows.
- [ ] End every run with exactly these five ordered console lines and no extra summary lines: `Status: success | issues`, `Reason: <1-line summary>`, `Auto-fixes: <N>`, `Flags: <N>`, `Outputs: skill-health-latest.md, skill-health-log.csv`.
- [ ] Keep all operations non-interactive, bounded, and idempotent; stop with one concise preflight reason if a required preflight path is missing or unreadable.

## Non-Requirements

- [ ] Do not edit frontmatter automatically.
- [ ] Do not add missing skills to the global index or categorize skills.
- [ ] Do not create child junctions under the Codex parent junction.
- [ ] If the live Codex root is missing, not a directory, or is a real directory rather than the expected parent junction, flag and stop the live junction phase; legacy child creation is fixture-only.
- [ ] Agents handling is cleanup-only: never create, reconcile, or repair a non-orphan Agents child. A missing Agents root is healthy.
- [ ] Do not validate package-managed or project-local skills.
- [ ] Do not recreate `.agents\skills`, localize skills, publish results, schedule external tasks, or delete real archived skill content without a separately authorized migration decision.

## Acceptance Criteria

- [ ] A clean run against the current surfaces completes without modifying the Codex parent junction and produces the required report/log artifacts.
- [ ] Tests/checks cover malformed frontmatter, stale/missing index rows, parent-junction detection, legacy Codex child creation, safe reparse-point removal, preflight stop, and same-day log idempotency.
- [ ] Running the validator twice on an unchanged fixture produces no duplicate junctions, no duplicate CSV date row, and no additional index/report drift.
- [ ] The report exactly uses the required headings/template, the CSV header is exactly `Date,Status,AutoFixes,Flags`, and counts agree with emitted events.

### Exact report template

The report must use this exact section order and field spelling (values are substituted, list items are one per event, and an empty list is the literal `None`):

```markdown
# Skill Health Report — <TODAY>

**Date**: <TODAY>
**Total skills checked**: <N>
**Issues found**: <M>

## Auto-Fixes Applied
<auto-fix event lines or None>

## Flags (Manual Review Needed)
<flag event lines or None>

## Summary
<one sentence summary>
```

The CSV must be UTF-8 with header `Date,Status,AutoFixes,Flags`; an existing same-date row is retained only when its values match the current run, otherwise it is replaced in place (never duplicated). Runtime stdout is exactly five lines: `Status: success` or `Status: issues`; `Reason: <1-line summary>`; `Auto-fixes: <N>`; `Flags: <N>`; `Outputs: skill-health-latest.md, skill-health-log.csv`.

Preflight failure uses the same five-line stdout contract with `Status: issues`, `Reason: preflight failed: <one line>`, zero auto-fixes/flags, and the two required output names; it must not overwrite existing report/log artifacts.
- [ ] The implementation documents exact paths, safety guardrails, expected flags, and rollback behavior.
