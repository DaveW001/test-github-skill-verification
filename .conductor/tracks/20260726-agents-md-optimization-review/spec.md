# Spec: AGENTS.md Optimization and Review

## Goal

Comprehensively review and safely optimize Dave's global Codex and OpenCode
`AGENTS.md` files first, then every active `AGENTS.md` under qualifying
`C:\development` folders or repositories modified during the 120-day window
ending 2026-07-26. Produce evidence-backed changes, preserve client-specific
instruction behavior, and close with independent validation.

## Frozen Scope

### Global files (review and validate first)

1. `C:\Users\DaveWitkin\.codex\AGENTS.md`
2. `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`

### Qualifying local roots

Cutoff: `2026-03-28T00:00:00-04:00`.

| Root | Qualification | Active AGENTS.md count |
|---|---|---:|
| `C:\development\02-Kx-to-process` | Recent commits and working-tree changes | 1 |
| `C:\development\command-center` | Commit on 2026-04-19 | 1 |
| `C:\development\INACTIVE-content-marketing` | Commit on 2026-07-18 | 2 |
| `C:\development\marketing` | Commit on 2026-07-18 | 3 |
| `C:\development\marketing\marketingskills` | Independent nested Git repository; commits since cutoff | 1 |
| `C:\development\opencode-core-dcp-fix` | Commit on 2026-07-20 | 15 |
| `C:\development\opencode-upstream` | Commit on 2026-07-18 | 15 |
| `C:\development\opencodex` | Commit on 2026-07-25 and recent working-tree changes | 2 |
| `C:\development\chief-of-staff` | Non-Git folder with files modified through 2026-07-26 | 1 |

Local total: 41 active files. Portfolio total: 43 files.

### Explicit exclusions

- `AGENTS.md` files below `.conductor\...\backup*`, `.git`, `node_modules`,
  vendored dependencies, generated output, or other archival paths.
- Repositories or folders with no active `AGENTS.md`.
- `CLAUDE.md`, Cursor rules, Copilot rules, and configured instruction files
  are precedence/reference evidence only; they are not edit targets.
- Creating AGENTS.md files in currently uncovered repositories is an optional
  follow-up, not an automatic action in this track.

## Requirements

- [ ] Review the global Codex file against the current official Codex manual.
- [ ] Review the global OpenCode file against the current OpenCode rules documentation and live machine configuration.
- [ ] Complete the frozen rubric for all 43 active files and record Pass, Finding, Not Applicable, or Unverified with evidence.
- [ ] Analyze effective instruction chains, nested scope, duplicate rules, stale paths/commands, client leakage, authority expansion, and token/byte cost.
- [ ] Verify build/lint/test commands and referenced paths using bounded, read-only checks where safe.
- [ ] Finish global review, fixes, and validation before starting local repository review.
- [ ] Back up every potential edit target and verify byte-identical recovery copies before editing.
- [ ] Preserve all pre-existing user changes and stop on overlapping dirty AGENTS.md files that cannot be separated safely.
- [ ] Apply only high-confidence, behavior-preserving improvements with no unrequested authority expansion.
- [ ] Validate changed files structurally, semantically, by backup diff, and through representative client instruction-discovery probes.
- [ ] Produce a decision-ready portfolio report, change manifest, unresolved-decision list, execution log, and Conductor closeout evidence.

## Frozen Review Rubric

Every file receives all applicable checks:

1. `SCOPE-01` correct global/repo/subtree scope.
2. `SCOPE-02` no broader rule where a narrower file is appropriate.
3. `LOAD-01` correct client discovery and precedence behavior.
4. `LOAD-02` no hidden override/fallback conflict.
5. `PURPOSE-01` concise repository or personal-context orientation.
6. `STRUCT-01` scannable headings and actionable bullets.
7. `STRUCT-02` critical rules appear before optional references.
8. `TOKEN-01` no avoidable duplication, narrative, or low-value context cost.
9. `TOKEN-02` large files use valid client-specific modularization.
10. `CMD-01` build, lint, test, and focused-check commands exist and match the repo.
11. `CMD-02` Windows/path/shell guidance is accurate for the target client.
12. `REF-01` every local reference resolves or is explicitly marked optional/ghost.
13. `REF-02` external-reference loading semantics match Codex or OpenCode behavior.
14. `ARCH-01` architecture and important-directory guidance is current and non-obvious.
15. `CONV-01` engineering conventions are project-specific rather than generic.
16. `VERIFY-01` definition of done names proportional verification.
17. `SAFETY-01` destructive/external/high-authority actions retain human gates.
18. `SAFETY-02` secrets and sensitive data guidance is least-privilege and non-disclosing.
19. `GIT-01` repository ownership, fork, dirty-tree, and commit/push rules are accurate.
20. `NEST-01` nested files add or override local rules without restating the parent.
21. `CLIENT-01` Codex-only and OpenCode-only tool names are not leaked across clients.
22. `DRIFT-01` instructions agree with current manifests, CI, docs, and live paths.
23. `REVIEW-01` code-review guidance flags behavior and safe alternatives, leaving mechanical lint to CI.
24. `HANDOFF-01` changes, unresolved items, and verification limitations are explicit.

Each item records: file identity, applicable scope, result, severity, confidence,
evidence path/command, finding ID, and disposition.

## Non-Requirements

- [ ] Do not modify application source code, tests, CI, deployment, secrets, schedules, or external systems.
- [ ] Do not restart Codex or OpenCode.
- [ ] Do not publish, commit, push, open a PR, send a message, or mutate calendars/tasks.
- [ ] Do not normalize the two OpenCode clones blindly; identical content may be reviewed once, but each live file and repository must be validated independently before any ported change.
- [ ] Do not remove an instruction solely to reduce tokens when it encodes an active safety or workflow requirement.
- [ ] Do not claim client-load or command validation passed when a bounded probe is unavailable or times out; record Unverified.

## Acceptance Criteria

- [ ] Scope inventory proves exactly 2 global and 41 active local AGENTS.md files across the nine qualifying local roots.
- [ ] The 24-item rubric is complete for every applicable file with no missing evidence fields.
- [ ] Global files are reviewed, corrected if warranted, and validated before local review begins.
- [ ] Every changed file has a verified pre-edit backup, narrow diff, rationale, and no unapproved authority expansion.
- [ ] All active nested chains and mirror relationships are reconciled without editing excluded backup/vendor files.
- [ ] Deterministic structural/reference/command checks pass, with unsafe or unavailable functional probes labeled Unverified.
- [ ] Independent Stage 7 validation returns Ready to close or an explicit bounded blocker report.
- [ ] Plan, metadata, execution log, both ledgers, Stage 9 evidence, and terminal closeout state agree.

