# Execution & Change Log

## Track: 20260411-notebooklm-cli-install

### Deviations from Plan

| # | Deviation | Impact | Resolution |
|---|-----------|--------|------------|
| 1 | Package version upgraded from v0.5.22 to v0.6.5 during validation | `metadata.json` version field stale | Updated metadata.json to reflect actual installed version 0.6.5 |
| 2 | Executable installed to global Python Scripts dir, not `--user` location | Paths in metadata.json incorrect | Updated paths to `AppData\Local\Programs\Python\Python313\Scripts\` |
| 3 | Official skill install succeeded initially but was lost (likely during 20260425-cleanup operation) | Skill directory missing, `nlm skill list` showed opencode: `-` | Re-ran `nlm skill install opencode` successfully |
| 4 | Legacy custom skill was already archived in `skill-backups/20260425-cleanup/notebooklm-legacy` rather than renamed in-place | Original plan assumed in-place rename | Documented actual archive location in metadata.json |
| 5 | `nlm doctor` hit Windows Unicode bug (Rich library `→` char on cp1252 console) | Cosmetic only, not a functional failure | Noted as known issue; requires `$env:PYTHONIOENCODING="utf-8"` |

### Skipped Items

None. All planned tasks completed.

### Ambiguities Resolved

| # | Ambiguity | Resolution |
|---|-----------|------------|
| 1 | `skill/` vs `skills/` directory | Confirmed: `skills/` is a junction to `skill/` — both paths resolve to same location |
| 2 | Legacy skill location | Found in `skill-backups/20260425-cleanup/notebooklm-legacy` from a prior cleanup operation |
| 3 | Skill install path | `nlm skill install opencode` installs to `~/.config/opencode/skills/nlm-skill/` (user level) |

### Validation Performed

| Check | Command | Result |
|-------|---------|--------|
| CLI version | `nlm --version` | `nlm version 0.6.5` ✅ |
| MCP server | `notebooklm-mcp --help` | Available ✅ |
| Skill install | `nlm skill list` | opencode: ✓ (user level) ✅ |
| Skill files | `Get-ChildItem ...nlm-skill\` | 4 files present (SKILL.md + 3 references) ✅ |
| Executable location | `where.exe nlm` | `AppData\Local\Programs\Python\Python313\Scripts\nlm.exe` ✅ |
| Package info | `pip show notebooklm-mcp-cli` | v0.6.5, correct location ✅ |
| Auth status | `nlm login --check` | Not authenticated (expected) ✅ |
| AI reference | `nlm --ai` | Captured to `nlm-ai-reference.md` (39KB) ✅ |

### Timeline

| Time | Event |
|------|-------|
| 2026-04-11 | Initial track creation, research phase, plan/spec/metadata written |
| 2026-04-11 | Phase 1-3 execution: CLI installed, verified, skill installed, legacy archived |
| 2026-04-11 | Phase 4: nlm --ai captured, auth status checked |
| 2026-04-11 | Phase 5: User handoff documentation delivered |
| 2026-05-08 | Validation run discovered 9 mismatches between claimed and actual state |
| 2026-05-08 | Fix 1: Re-ran `nlm skill install opencode` — success |
| 2026-05-08 | Fix 2: Verified legacy skill state — already archived in skill-backups |
| 2026-05-08 | Fix 3: Updated metadata.json with correct version (0.6.5), paths, progress (100%) |
| 2026-05-08 | Fix 4: Updated plan.md — all 18 tasks marked [x] |
| 2026-05-08 | Fix 5: Added track entry to tracks-ledger.md |
| 2026-05-08 | Fix 6: Created this execution/change log |
