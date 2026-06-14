# Handover: System Prompt Token Audit & Reduction — Track 20260526-system-prompt-token-audit

**Created:** 2026-05-26  
**Track Directory:** `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\`  
**Plan File:** `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\plan.md`  
**Spec File:** `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\spec.md`  
**Metadata:** `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\metadata.json`

---

## Goal

Reduce the OpenCode system prompt from approximately **29,001 tokens** to **<=15,000 tokens** through safe, locally configurable changes (AGENTS.md, skill metadata, subagent descriptions, MCP config) without modifying OpenCode application source code. If the target is proven unattainable locally, the final report must clearly distinguish achieved savings from non-local overhead.

---

## Current Status

**Phase 0 (Setup):** Complete  
**Phase 1 (Measurement):** Complete  
**Phase 2 (Reduction Strategy):** Complete  
**Phase 3 (Implementation):** Partially complete — 2 tasks blocked, 1 skipped  
**Phase 4 (Validation):** Not started — requires fresh OpenCode session  
**Phase 5 (Handover/Finalize):** Not started

**Track status in metadata.json:** `active` (correct — work is incomplete)  
**Track status in tracks-ledger.md:** Incorrectly says "not started" — needs updating.

---

## What Was Done

### Phase 0 — Setup & Baseline
- Artifacts directory created at `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\`
- Baseline tokenscope captured: **system tokens = 27,280**
- Baseline file: `artifacts\baseline-tokenscope.txt`
- Baseline notes: `artifacts\baseline-notes.md`

### Phase 1 — Token Breakdown
- `artifacts\token-breakdown.md` — component-by-component breakdown
- `artifacts\native-tool-inventory.md` — 15 native tools inventoried
- `artifacts\mcp-tool-inventory.md` — Codex, Chrome DevTools, Slack MCP families
- Summary: Remainder bucket ~11,142 tokens (40.8%), Skill metadata ~5,712, MCP ~4,300, AGENTS.md ~2,875, Native tools ~2,350, Subagents ~901

### Phase 2 — Reduction Proposals
- `artifacts\reduction-proposals.md` — quantified before/after proposals
- AGENTS.md: ~1,480 tokens proposed savings
- Skill descriptions: ~610 tokens proposed savings
- MCP (Codex only): ~2,750 tokens proposed (later skipped)
- Subagents: ~200 tokens proposed (blocked — config path unknown)
- Consolidated projection: ~22,240 tokens post-reduction (still above 15,000)

### Phase 3 — Implementation (Partial)

**Completed:**
- **Task 3.1:** AGENTS.md backed up to `C:\Users\DaveWitkin\.config\opencode\AGENTS.md.backup-20260526-152545`
- **Task 3.2:** AGENTS.md compressed from ~11,497 chars to ~3,797 chars. Estimated savings ~1,925 tokens. Edit summary: `artifacts\agents-edit-summary.md`
- **Task 3.3:** 14 of 15 skill files backed up. `customize-opencode` SKILL.md was not found at the proposed path (it is built-in).
- **Task 3.4:** Descriptions shortened in 14 SKILL.md files.
- **Task 3.7:** MCP config backed up: `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.backup-20260526-155200`

**Blocked:**
- **Task 3.5 / 3.6:** Subagent config location not found. Subagent definitions appear compiled into the OpenCode binary, not in local config.

**Skipped:**
- **Task 3.8:** MCP reduction skipped. Codex MCP is actively used for OAuth management; target was already proven unattainable locally even with full MCP removal.

---

## Critical Issues Found by Review (Must Fix First)

### 1. INVALID YAML FRONTMATTER IN 4 SKILL FILES

A deterministic YAML parse check (Python/PyYAML) found that these edited skill files now have **invalid frontmatter** due to unquoted colons in description values. This can break skill discovery/loading:

| File | Problem |
|---|---|
| `C:\Users\DaveWitkin\.agents\skills\gemini-proxy\SKILL.md` | `description: Manage local Gemini API Key Rotator Proxy: status, restart, key rotation, monitoring.` — unquoted `: ` |
| `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md` | `description: Ingest source material into the local markdown knowledge graph: extract entities, deduplicate, validate.` — unquoted `: ` |
| `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md` | `description: Audit and maintain the local markdown knowledge graph: health, gaps, review queues.` — unquoted `: ` |
| `C:\Users\DaveWitkin\.agents\skills\notebooklm-cli\SKILL.md` | `description: Interact with Google NotebookLM programmatically: create notebooks, add sources, generate content.` — unquoted `: ` |

**Fix:** Quote the description values in YAML frontmatter, e.g.:
```yaml
description: "Manage local Gemini API Key Rotator Proxy: status, restart, key rotation, monitoring."
```

### 2. CONTROL-CHARACTER CORRUPTION IN ARTIFACTS

PowerShell backtick escaping caused control characters in several markdown artifacts. Affected files:
- `artifacts\reduction-proposals.md` — `escalate upstream` rendered as ESC char + `scalate upstream`
- `artifacts\final-report.md` — `bash` rendered as backspace + `ash`, `read` as control char + `ead`, `<=` as replacement char
- `execution-log.md` — `tokenscope` and artifact paths corrupted
- `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` — `osgrep -> grep/glob -> targeted Read` has replacement chars instead of arrows

**Fix:** Replace corrupted characters with clean ASCII equivalents.

### 3. METADATA INCONSISTENCY

`metadata.json` has:
```json
"totalTasks": 20,
"completedTasks": 27,
"percentage": 67
```
Completed tasks cannot exceed total tasks. This needs correction.

### 4. PLAN CHECKBOX INCONSISTENCY

Task 2.4 in `plan.md` is marked `[x]` (complete), but it did NOT identify exact subagent config file paths as required by the plan verification step. It should be marked as blocked or incomplete.

### 5. TRACKS-LEDGER STALE

`C:\development\opencode\.conductor\tracks-ledger.md` still lists the track as "Phase: not started". This is false and must be updated.

### 6. MISSING CHANGELOG

`C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\change-log.md` does not exist.

### 7. POTENTIAL TRIGGER METADATA REMOVAL

In `knowledge-graph-builder` and `knowledge-graph-maintainer` SKILL.md files, the frontmatter regex may have consumed trigger blocks along with multiline descriptions. Verify whether `triggers:` sections are still present; if not, skill discoverability may be reduced.

---

## Files Modified (With Backups)

| File | Backup | Status |
|---|---|---|
| `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` | `AGENTS.md.backup-20260526-152545` | Edited, compressed |
| `C:\Users\DaveWitkin\.agents\skills\clickup-cli\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.agents\skills\google-drive\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.agents\skills\first-principles-mastery\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.agents\skills\gemini-proxy\SKILL.md` | `.backup-20260526-153500` | **Edited, YAML BROKEN** |
| `C:\Users\DaveWitkin\.agents\skills\gmail-workspace\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.agents\skills\image-to-html-reconstruction\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.agents\skills\frontend-design\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.agents\skills\find-info\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md` | `.backup-20260526-153500` | **Edited, YAML BROKEN** |
| `C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md` | `.backup-20260526-153500` | **Edited, YAML BROKEN** |
| `C:\Users\DaveWitkin\.agents\skills\notebooklm-cli\SKILL.md` | `.backup-20260526-153500` | **Edited, YAML BROKEN** |
| `C:\Users\DaveWitkin\.agents\skills\notebooklm-meta-prompt\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.config\opencode\skill\nlm-skill\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.agents\skills\slack-messaging\SKILL.md` | `.backup-20260526-153500` | Edited, YAML OK |
| `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` | `opencode.jsonc.backup-20260526-155200` | Backed up, not edited |

---

## Existing Artifacts

All in `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\artifacts\`:

| File | Status |
|---|---|
| `baseline-tokenscope.txt` | Exists, valid |
| `baseline-notes.md` | Exists, valid |
| `token-breakdown.md` | Exists, valid |
| `native-tool-inventory.md` | Exists, valid |
| `mcp-tool-inventory.md` | Exists, valid |
| `reduction-proposals.md` | Exists, has control-char corruption |
| `agents-edit-summary.md` | Exists, valid |
| `final-report.md` | Exists, validation incomplete, has corruption |

**Missing (required by spec):**
- `post-reduction-tokenscope.txt` — Phase 4 not yet executed

---

## Key Finding: <=15,000 Token Target

**Assessment:** The target of <=15,000 tokens is **likely not achievable through safe local configuration alone**, but this has NOT been rigorously proven.

**Reasoning:**
- Baseline: ~27,280 system tokens
- Actual applied savings: ~2,535 tokens (AGENTS.md ~1,925 + skill descriptions ~610)
- Estimated post-reduction: ~24,745 tokens
- Gap to target: ~9,745 tokens
- Non-local components (base prompt ~11,142, native tool schemas ~2,350, skill tool boilerplate ~3,561) total ~17,053 tokens alone — already exceeding the target before any configurable content is added.

**Caveats:**
- MCP/tool schema contributions were estimated, not directly measured (tokenscope export failed due to missing bun index.js)
- The remainder bucket is calculated by subtraction, not independently decomposed
- Some MCP reductions were skipped that could have saved ~2,750 more tokens
- Post-reduction tokenscope has not been run to validate actual savings

**Recommended conclusion wording:** "Current evidence suggests the <=15,000 target is unlikely to be achievable through safe local configuration alone, but this has not been fully proven because several prompt components were estimated and post-reduction tokenscope validation is still missing."

---

## Next Steps (In Order)

### Step 1: Fix Broken Skill Frontmatter (URGENT)
Fix the 4 SKILL.md files with invalid YAML by quoting description values containing colons. Use the backups if needed:
```
C:\Users\DaveWitkin\.agents\skills\gemini-proxy\SKILL.md
C:\Users\DaveWitkin\.agents\skills\knowledge-graph-builder\SKILL.md
C:\Users\DaveWitkin\.agents\skills\knowledge-graph-maintainer\SKILL.md
C:\Users\DaveWitkin\.agents\skills\notebooklm-cli\SKILL.md
```

### Step 2: Verify All 14 Skill Frontmatters Parse as Valid YAML
Run a YAML validation script to confirm all edited skills parse cleanly.

### Step 3: Fix Control-Character Corruption
Clean up corrupted text in:
- `artifacts\reduction-proposals.md`
- `artifacts\final-report.md`
- `execution-log.md`
- `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` (fix arrow characters)

### Step 4: Verify Trigger Metadata
Check whether `knowledge-graph-builder`, `knowledge-graph-maintainer`, and `slack-messaging` still have `triggers:` blocks in their frontmatter. If missing, restore from backups or re-add minimal triggers.

### Step 5: Run Phase 4 Validation (Fresh OpenCode Session)
This MUST be done in a new OpenCode session:

1. **Task 4.1:** Run `tokenscope`, copy output to `artifacts\post-reduction-tokenscope.txt`
2. **Task 4.2:** Update `final-report.md` with baseline vs post-reduction token comparison table
3. **Task 4.3:** Run `skill_find "calendar"` — expect at least one calendar skill
4. **Task 4.4:** Run `skill_use "calendar_today"` — expect successful load
5. **Task 4.5:** Run `skill_find "email"` — expect at least one email skill
6. **Task 4.6:** Run tool validation:
   - `bash` with `Write-Output "hello"`
   - `glob` against `C:\development\opencode` with pattern `**/*.md`
   - `grep` for `"Conductor Tracks"` in `C:\development\opencode\.conductor`
   - `read` on `C:\development\opencode\.conductor\tracks.md`
7. **Task 4.7:** Validate AGENTS.md behavior rules (skill_find preference, absolute paths, osgrep-first)
8. **Task 4.8:** Finalize `final-report.md` with all 6 required sections and conclusion

### Step 6: Fix Metadata and Ledger
- Correct `metadata.json` totalTasks/completedTasks consistency
- Update `C:\development\opencode\.conductor\tracks-ledger.md` to reflect actual phase
- Update `C:\development\opencode\.conductor\tracks.md` with completion date if track is done

### Step 7: Complete Phase 5
- Mark all completed tasks in `plan.md`
- Update `tracks.md` and `tracks-ledger.md`
- Create or update `change-log.md`
- Append final handoff section to `execution-log.md`

---

## Constraints & Guardrails

- Do NOT modify OpenCode application source code
- Do NOT disable MCP servers without explicit user confirmation
- Preserve backups before any further edits
- All skill edits must preserve valid YAML frontmatter
- Use approximate token counting (char count / 4) where model-specific tokenization is unavailable

---

## Reference Files

- **Plan:** `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\plan.md`
- **Spec:** `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\spec.md`
- **Metadata:** `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\metadata.json`
- **Execution Log:** `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log.md`
- **Issue Log:** `C:\development\opencode\.conductor\tracks\20260526-system-prompt-token-audit\execution-log-2026-05-26.md`
- **Tracks Index:** `C:\development\opencode\.conductor\tracks.md`
- **Tracks Ledger:** `C:\development\opencode\.conductor\tracks-ledger.md`
- **AGENTS.md (current):** `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
- **AGENTS.md (backup):** `C:\Users\DaveWitkin\.config\opencode\AGENTS.md.backup-20260526-152545`