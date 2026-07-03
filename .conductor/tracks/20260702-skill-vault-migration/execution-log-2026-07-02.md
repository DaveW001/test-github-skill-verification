# Execution Log: Skill Vault Migration

- **Date:** 2026-07-02
- **Track:** `20260702-skill-vault-migration`
- **Executor (Stage 4):** `zai-coding-plan/glm-5.2` (Tier 1 of model fallback chain)
- **Model diversity:** Stage 5 validator will use `opencode-go/minimax-m3`, which differs from this executor (diversity preserved).
- **Overall status:** PARTIAL SUCCESS / BLOCKED on 2 skills by active environmental interference.

## Headline result

| Skill | Final location | Vault validated? | Notes |
|---|---|---|---|
| `knowledge-graph-query` | VAULT only (native deleted) | YES | Migrated + renamed underscore->hyphen + frontmatter added. Stable. |
| `enrich-meeting-notes` | VAULT only (native deleted) | YES | Migrated + renamed underscore->hyphen + frontmatter added. Stable. |
| `retrospective` | VAULT only (native deleted) | YES | Migrated unchanged. Stable. |
| `nlm-skill` | NATIVE (safety net) + VAULT reverted to baseline | NO (vault baseline has `version:`, fails validator) | Vault edit (2.2) was reverted by the external process; skill now at exact pre-track duplicate state (native + vault baseline). |
| `pptx-to-pdf-converter` | NATIVE (safety net) + VAULT reverted to baseline | YES (vault baseline validates) | Skill now at exact pre-track duplicate state (native + vault baseline, good frontmatter). |

- **Native always-on folder:** reduced 11 -> 8 (3 migrated out; the 2 rolled-back skills remain native). Not the target of 6, because 2 migrations are blocked.
- **No skill was permanently lost.** All backups are intact in the repo location (separate from the vault).

## Environment preflight

- Native `Read`/`Edit`/`Write`/`glob`/`grep` tools returned `Bun is not defined`. Per protocol, the ENTIRE session was executed PowerShell-first via the `bash` tool: `Get-Content -Raw` (read), `Set-Content -Encoding utf8` (write), `Select-String -SimpleMatch` (grep), `Get-ChildItem -Recurse` (glob). Literal string edits used `[string]::Replace()` (not regex `-replace`) per `powershell-edit-hazards.md`.
- Every `bash` call carried an explicit `timeout`. No blocking commands were used.

## Tasks completed and held

- Phase 0 (0.1, 0.2, 0.3): all paths/config/folders confirmed.
- Phase 1 (1.1, 1.2): all 5 native folders + 5 vault states backed up to `backups\2026-07-02-pre-edit\`; `backup-dir.txt` written.
- Phase 2.1: frontmatter added to vault `knowledge_graph_query` (then renamed; see deviation).
- Phase 2.4: vault `enrich_meeting_notes` created from native backup + frontmatter (then renamed; see deviation).
- Phase 2.5: vault `retrospective` created from native backup, unchanged.
- Phase 3 (initial run): all 5 vault skills passed `quick_validate.py` and the 2-field frontmatter check (BEFORE the interference destroyed nlm/pptx).
- Phase 4.1: all 5 native target folders deleted (later, 2 were restored to native as a safety net).
- Phase 5.1 (partial): 3 of 5 currently pass the resolvability proxy.

## Documented deviation #1 — underscore -> hyphen rename (Tier 0)

The plan's tasks 2.1 and 2.4 specified underscore `name:` fields matching the underscore folder names. This contradicted the plan's own Definition of Done (`quick_validate.py` must pass for all five) because the validator requires hyphen-case `^[a-z0-9-]+$`, and the skill-creator SKILL.md mandates hyphen-case names AND "Name the skill folder exactly after the skill name." The plan was internally contradictory on this point.

Resolution (Tier-0 documented deviation — low-risk and reversible): renamed the two affected vault folders and their `name:` fields to hyphen-case:
- `knowledge_graph_query` -> `knowledge-graph-query`
- `enrich_meeting_notes` -> `enrich-meeting-notes`

Pre-rename backups were captured: `backups\2026-07-02-pre-edit\vault-knowledge_graph_query.pre-rename.bak`, `vault-enrich_meeting_notes.pre-rename.bak`. A filtered search confirmed ZERO functional (non-log) references to the underscore names (only each skill's own `name:` field, since changed) and no `skill_use`/`skill_find` invocations used the underscore names. After rename, both passed `quick_validate.py`. The native underscore folders were still deleted in Phase 4 by their original names.

## BLOCKER — active interference on pre-existing vault folders (Tier 1 STOP)

After Phase 3 validation passed for all 5, the vault folders `nlm-skill` and `pptx-to-pdf-converter` were found EMPTY (0 files), then on the next check missing entirely, then empty again — an oscillating pattern. A recovery attempt with `Copy-Item` failed mid-copy with errors like:

- `Could not find a part of the path 'C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill\SKILL.md'`
- `Could not find a part of the path 'C:\Users\DaveWitkin\.opencode-lazy-vault\nlm-skill\references'`
- `Could not find a part of the path 'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-to-pdf-converter\scripts'`

These errors occurred WHILE the copy was writing — i.e., the destination folders were being deleted faster than `Copy-Item` could populate them. A 5-second stability re-check confirmed both `SKILL.md` files gone again: `UNSTABLE`.

Key observations:
- The interference is VAULT-SPECIFIC: the native folder (`~/.config/opencode/skill`) is stable — Phase 4 deletions held, and the native restore (below) also held after re-check.
- It targets PRE-EXISTING vault folders: the three skills created this session (`knowledge-graph-query`, `enrich-meeting-notes`, `retrospective`) remained intact across every check, while the two skills that pre-existed in the vault (`nlm-skill`, `pptx-to-pdf-converter`) were repeatedly emptied/removed.
- The `nlm-skill` backup contains a `SKILL.md.backup-20260526-152740` file, indicating an external editing/management process actively touches `nlm-skill`.
- The vault is NOT a reparse point and is NOT under OneDrive (OneDrive exists on the machine but elsewhere). Root cause is not conclusively identified; candidates: an external skill-management/sync process, an opencode-skillful lifecycle action, or AV real-time quarantine.

Per the directive's self-bounding rules, I did NOT retry the failing restore in a tight loop (one recovery + one stability test only), and switched strategy to a safe fallback.

### Final observation (post-closeout snapshot)

After the safety-net restore to native, a final snapshot showed the two vault folders (`nlm-skill`, `pptx-to-pdf-converter`) had repopulated to their PRE-TRACK BASELINE content (the external process reverted them): `nlm-skill` has its original `version:` field back (so it FAILS `quick_validate.py` in the vault), and `pptx-to-pdf-converter` is back to its good baseline (validates). This confirms the external process reverts pre-existing vault folders to a baseline and discards edits made to them. The three skills created fresh this session (`knowledge-graph-query`, `enrich-meeting-notes`, `retrospective`) were NOT affected. Net result for the two blocked skills: they are at their exact pre-track duplicate state (present in both native and vault with baseline content) — no regression, no data loss. Re-attempting their migration requires first diagnosing/stopping the baseline-revert process.

## Safety net — restore the 2 blocked skills to native

Because the native copies of `nlm-skill` and `pptx-to-pdf-converter` were already deleted in Phase 4 and their vault copies were being actively destroyed, those two skills were at risk of becoming unavailable. As a reversible, documented safety net, both were restored to the NATIVE folder from their `native-*.pre-edit.bak` backups:
- `nlm-skill` -> native (original frontmatter, `version:` field present — same as before the track).
- `pptx-to-pdf-converter` -> native (good frontmatter — same as before the track).

Both were verified stable in native after a 4-second re-check. Result: both skills remain usable (always-on), at the cost of those 2 not being moved to the vault. The 3 successfully migrated skills remain vault-only.

## Validation performed and results

- `quick_validate.py` (with `$env:PYTHONUTF8='1'` for nlm): PASS for knowledge-graph-query, nlm-skill (before interference), pptx-to-pdf-converter (before interference), enrich-meeting-notes, retrospective. Currently PASS for the 3 stable vault skills; nlm/pptx vault copies cannot be validated (empty).
- Frontmatter 2-field check (`name` + `description` only, name matches folder): PASS for the 3 stable vault skills.
- `git diff --no-index --numstat` against pre-edit backups: confirmed append-only frontmatter additions (2.1, 2.4), expected frontmatter replacement (2.2), byte-identical copies (2.3, 2.5).
- Native inventory: currently 8 folders (6 intended-keep + nlm-skill + pptx-to-pdf-converter restored).
- Backup integrity: all 5 native backups + 5 vault backups + 2 pre-rename backups are intact with non-empty SKILL.md.

## Restart caveat (handover)

OpenCode builds the `available_skills` list and performs the opencode-skillful vault scan at SESSION START. The deterministic proxy checks above prove the resolvability INPUTS for the 3 migrated skills (folder exists in vault + basePaths config points at vault + valid frontmatter + `quick_validate.py` passes), but the authoritative end-to-end `available_skills` refresh must be confirmed AFTER restarting OpenCode. After restart, verify that `knowledge-graph-query`, `enrich-meeting-notes`, and `retrospective` resolve via `skill_find`/`skill_use`, and that `nlm-skill` and `pptx-to-pdf-converter` are still injected natively.

## Deviations, skipped items, ambiguities

1. Underscore -> hyphen rename of 2 vault skills (Tier 0, documented above) — required to satisfy the plan's Definition of Done and the skill-creator naming standard.
2. nlm-skill and pptx-to-pdf-converter migration ROLLED BACK to native (Tier 1 STOP) — required because active external interference made their vault copies non-restorable. Their Phase 2 edits and Phase 3 validation are therefore NOT durable; the skills are back to their pre-track native state.
3. The plan's Definition of Done (5 skills vault-only, 6 native) is NOT fully met: 3/5 vault-only, 8 native.

## Recommendation / next steps

1. Diagnose the external process emptying pre-existing vault folders (`nlm-skill`, `pptx-to-pdf-converter`) before re-attempting their migration. Likely an external skill-management/sync process, an opencode-skillful lifecycle action, or AV quarantine (note the `SKILL.md.backup-20260526-152740` artifact inside `nlm-skill`).
2. Once the interference is resolved, re-run ONLY the nlm-skill and pptx-to-pdf-converter migration: back up, fix/verify vault copy (nlm: remove `version:`, improve description; pptx: already good), validate with `quick_validate.py`, then delete native. Their backups in this track remain available.
3. After an OpenCode restart, confirm all 5 skills resolve through their intended paths.


