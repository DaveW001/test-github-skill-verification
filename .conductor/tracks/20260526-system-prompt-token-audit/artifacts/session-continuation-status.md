# System Prompt Token Audit - Session Continuation Status

**Date:** May 31, 2026
**Track:** `20260526-system-prompt-token-audit`
**Original Session:** May 26, 2026
**Status:** Track marked COMPLETED (33/33 tasks), but fresh validation reveals open items.

---

## 1. What We're Trying to Achieve

**Goal:** Reduce the OpenCode system prompt from ~27,280 tokens to <=15,000 tokens through safe, locally configurable changes -- without modifying OpenCode source code.

**Why it matters:** System prompt tokens are charged on every single API call. A bloated system prompt wastes context window space, increases costs (or burns through subscription limits faster), and reduces the amount of useful conversation context available.

**Root problem:** The system prompt is assembled from many components (base prompt, AGENTS.md, skill metadata, MCP tool schemas, native tool schemas, subagent definitions). Most of the heaviest components are not locally editable.

---

## 2. What Was Done (May 26, 2026)

### Phase 0 - Setup (4 tasks)
- Baseline measurement: **27,280 system tokens** (captured in first API call of fresh session)
- Artifacts directory created, execution log started

### Phase 1 - Measurement (5 tasks)
- Complete component breakdown produced:

| Component | Tokens | % of Total |
|-----------|--------|------------|
| Remainder (base prompt + env) | 11,142 | 40.8% |
| Skill tool metadata (32 skills) | 5,712 | 20.9% |
| MCP tools (Codex) | ~4,300 | 15.8% |
| AGENTS.md | 2,875 | 10.5% |
| Native tool schemas | 2,350 | 8.6% |
| Subagent definitions | 901 | 3.3% |
| **Total** | **27,280** | **100%** |

### Phase 2 - Reduction Proposals (4 tasks)
- AGENTS.md: Proposed ~1,480 token savings
- Skill descriptions: Proposed ~610 token savings
- MCP: Proposed ~2,750 (later SKIPPED)
- Subagents: Proposed ~200 (later BLOCKED)

### Phase 3 - Implementation (9 tasks)
- **AGENTS.md compressed:** 2,875 -> ~950 tokens (**-1,925 tokens saved**)
  - Backup at `AGENTS.md.backup-20260526-152545`
- **14 skill descriptions shortened:** ~610 tokens saved
- **4 skill YAML frontmatter repaired:** Quoted descriptions containing colons
- **5 control-character corruptions fixed** in SKILL.md files
- **3 skills had triggers metadata added**
- **BLOCKED:** Subagent config compiled into binary (not locally editable)
- **SKIPPED:** MCP reduction (Codex actively used; target unattainable regardless)

### Phase 4 - Remediation and Validation (8 tasks)
- All repair tasks completed
- Skill validation: calendar PASS, email PASS
- Tool validation: bash PASS, glob/grep/read FAIL (Bun runtime issue)
- Final report written with conclusion: "Target not achieved locally"

### Phase 5 - Final Checks (3 tasks)
- Artifact existence verified
- Control-char scan performed
- User handover summary created

---

## 3. Key Findings

### What we achieved
- **~2,535 tokens saved locally** (AGENTS.md -1,925 + skills -610)
- Estimated post-reduction: **~24,745 tokens**

### Why the target was not met
The <=15,000 target is **NOT achievable locally**. Non-local components total ~17,053 tokens:
- Base prompt (compiled into binary): ~11,142
- Native tool schemas (built-in): ~2,350
- Skill boilerplate (framework overhead): ~3,561

The remaining gap of ~9,745 tokens would require upstream OpenCode source code changes.

### Important: The tokenscope "system" measurement is unreliable for comparing sessions
The tokenscope SYSTEM category is an **inferred estimate from API telemetry**, not a direct measurement. It includes accumulated conversation overhead that gets larger as the session progresses. This is why the post-reduction measurement showed 35,801 "system" tokens despite the actual system prompt being smaller -- the session had 30 API calls worth of accumulated context being counted as "system."

---

## 4. Fresh Validation (May 31, 2026 - This Session)

### Current session tokenscope data
- **Most recent API call:** 35,788 total input tokens (but this is the full conversation, not just system prompt)
- This session uses the **01-Planner agent** which has a different (likely leaner) base prompt than the original 00-Agent

### Skills loaded comparison
| Metric | Baseline (May 26) | Current Session (May 31) |
|--------|-------------------|--------------------------|
| Skills in always-on context | 32 | 8 |
| Skill metadata tokens | ~2,151 | ~430 |
| **Savings from lazy-loading** | -- | **~1,721 tokens** |

The lazy-vault skill migration (done separately, not part of this track) has saved an additional ~1,721 tokens by moving skills from always-on to lazy-loaded.

### Combined estimated savings
| Source | Tokens Saved |
|--------|-------------|
| AGENTS.md compression | -1,925 |
| Skill description shortening | -610 |
| Lazy-vault skill migration (separate) | -1,721 |
| **Total estimated savings** | **-4,256** |

**Estimated current system prompt:** ~23,024 tokens (27,280 - 4,256) -- but this is a rough estimate. A truly fresh session with minimal tools loaded would be needed for an accurate measurement.

---

## 5. What's Left To Do

### Open Items (Track QA)

#### A. AGENTS.md Arrow Characters (LOW)
- Line 27 contains Unicode right arrows (U+2192) instead of ASCII ->
- Hex verified: E2 86 92 (valid UTF-8 for right arrow)
- **Not corruption** -- these are valid Unicode arrows from the original compression
- Consider replacing with ASCII -> for maximum compatibility

#### B. Tokenscope Bun Dependency (MEDIUM)
- Tokenscope output has corrupted control characters in PowerShell
- Root cause: Missing `bun` package in tokenscope node_modules
- Error: Cannot find package 'bun'
- This prevents accurate system-prompt-only measurements
- The SYSTEM token count from tokenscope is an unreliable heuristic

#### C. Fresh Session Measurement Not Done (HIGH)
- The original plan called for a "fresh session" measurement to validate reductions
- The post-reduction tokenscope (35,801 system tokens) was taken in the SAME session as the edits, making it unreliable
- A truly fresh session (new session, minimal tools) would give an accurate system-only count
- This was the most valuable validation step and was never properly executed

#### D. Upstream Reduction Path (FUTURE)
- To reach <=15,000 tokens, OpenCode source changes would be needed:
  - Reduce base prompt (~11,142 tokens)
  - Reduce native tool schemas (~2,350 tokens)
  - Reduce skill framework boilerplate (~3,561 tokens)
- This is an upstream contribution opportunity, not a local fix

### Recommended Next Steps

1. **Quick win:** Fix AGENTS.md arrow characters (replace Unicode arrows with ASCII ->) -- trivial
2. **Validation:** Open a fresh session with 01-Planner agent, run tokenscope on first API call, capture true system-only token count
3. **Documentation:** Update final-report.md with the fresh measurement
4. **Future planning:** If <=15,000 target is still desired, create an upstream issue/PR for OpenCode to reduce base prompt and tool schema sizes

---

## 6. Files Modified (Complete List)

### Configuration
| File | Change | Backup |
|------|--------|--------|
| `~/.config/opencode/AGENTS.md` | Compressed 2,875->950 tokens | `AGENTS.md.backup-20260526-152545` |

### Skills (14 files modified)
All in `~/.agents/skills/` and `~/.config/opencode/skill/`:
- Descriptions shortened in YAML frontmatter
- 4 descriptions re-quoted (colons)
- 5 control-character corruptions removed
- 3 trigger metadata entries added

### Artifacts (in `.conductor/tracks/20260526-system-prompt-token-audit/artifacts/`)
- `baseline-tokenscope.txt` -- original 27,280 system tokens
- `post-reduction-tokenscope.txt` -- same-session 35,801 (unreliable)
- `token-breakdown.md` -- component analysis
- `reduction-proposals.md` -- quantified proposals
- `final-report.md` -- complete 6-section report
- `skill-yaml-validation.txt` -- 14/14 pass
- `baseline-notes.md`, `agents-edit-summary.md`, `native-tool-inventory.md`, `mcp-tool-inventory.md`
- `remediation-backups/` -- backup subdirectory
- `session-continuation-status.md` -- THIS FILE

---

## 7. Summary Metrics

| Metric | Value |
|--------|-------|
| Baseline system tokens (May 26) | 27,280 |
| Tokens saved locally (this track) | -2,535 |
| Tokens saved (lazy-vault, separate) | -1,721 |
| **Total estimated savings** | **-4,256** |
| Estimated current system prompt | ~23,024 |
| Target | <=15,000 |
| Gap to target | ~8,024+ |
| Gap requires | Upstream OpenCode changes |
| Track tasks completed | 33/33 (100%) |
| Track conclusion | Target not achievable locally |
