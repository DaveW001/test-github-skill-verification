# Skill Health Report — 2026-05-05

**Date**: 2026-05-05
**Total skills checked**: 5
**Issues found**: 36

## Auto-Fixes Applied

- `JUNCTION_CREATED` | `pptx-to-pdf-converter` | agents — missing junction created → `C:\Users\DaveWitkin\.config\opencode\skill\pptx-to-pdf-converter`

## Flags (Manual Review Needed)

The following 35 skills are listed in the global skills index but have no matching canonical directory at `C:\Users\DaveWitkin\.config\opencode\skill\`. All exist as lazy-loaded skills in `C:\Users\DaveWitkin\.codex\skills\`.

| # | Flag | Skill | Reason |
|---|------|-------|--------|
| 1 | INDEX_STALE | `content-trend-researcher` | No canonical directory |
| 2 | INDEX_STALE | `image-generator` | No canonical directory |
| 3 | INDEX_STALE | `image-manifest-builder` | No canonical directory |
| 4 | INDEX_STALE | `youtube-shorts` | No canonical directory |
| 5 | INDEX_STALE | `design-system-extractor` | No canonical directory |
| 6 | INDEX_STALE | `frontend-design` | No canonical directory |
| 7 | INDEX_STALE | `html-demo-design` | No canonical directory |
| 8 | INDEX_STALE | `pa-ui-design` | No canonical directory |
| 9 | INDEX_STALE | `notebooklm-cli` | No canonical directory |
| 10 | INDEX_STALE | `notebooklm-meta-prompt` | No canonical directory (duplicate index entry — lines 32 and 92) |
| 11 | INDEX_STALE | `firebase-deployment-specialist` | No canonical directory |
| 12 | INDEX_STALE | `github-create-repo` | No canonical directory |
| 13 | INDEX_STALE | `github-management` | No canonical directory |
| 14 | INDEX_STALE | `powershell-master` | No canonical directory |
| 15 | INDEX_STALE | `webapp-testing` | No canonical directory |
| 16 | INDEX_STALE | `doc-to-markdown` | No canonical directory |
| 17 | INDEX_STALE | `markdown-pdf-publisher` | No canonical directory |
| 18 | INDEX_STALE | `markdown-render` | No canonical directory |
| 19 | INDEX_STALE | `clickup` | No canonical directory |
| 20 | INDEX_STALE | `clickup-cli` | No canonical directory |
| 21 | INDEX_STALE | `session-retro` | No canonical directory |
| 22 | INDEX_STALE | `scheduled-job-best-practices` | No canonical directory |
| 23 | INDEX_STALE | `terminal-aliases` | No canonical directory |
| 24 | INDEX_STALE | `windows-task-scheduler` | No canonical directory |
| 25 | INDEX_STALE | `email-auto-sorter` | No canonical directory |
| 26 | INDEX_STALE | `email-draft-reply` | No canonical directory |
| 27 | INDEX_STALE | `email-to-clickup` | No canonical directory |
| 28 | INDEX_STALE | `outlook-inbox-triage` | No canonical directory |
| 29 | INDEX_STALE | `first-principles-mastery` | No canonical directory |
| 30 | INDEX_STALE | `thinking-partner` | No canonical directory |
| 31 | INDEX_STALE | `agent-writer` | No canonical directory |
| 32 | INDEX_STALE | `command-writer` | No canonical directory |
| 33 | INDEX_STALE | `skill-writer` | No canonical directory |
| 34 | INDEX_STALE | `snippet-writer` | No canonical directory |
| 35 | INDEX_STALE | `gemini-proxy` | No canonical directory |

## Observations

- **Duplicate index entry**: `notebooklm-meta-prompt` appears in both "NotebookLM & Research" (line 32) and "AI & Agent Tooling" (line 92). Consider deduplicating.
- **Architecture note**: The canonical directory (`opencode\skill\`) contains only 5 always-on native skills. The global index lists 40 skills, with 35 served as lazy-loaded skills from `codex\skills\`. Consider updating the index description to document this multi-location architecture and avoid false INDEX_STALE signals in future runs.

## Summary

5 canonical skills checked. 1 auto-fix applied (junction for pptx-to-pdf-converter in agents). 35 flags for manual review — all INDEX_STALE entries exist as lazy-loaded skills in codex-skills/ and may reflect an outdated index scope rather than genuine staleness.
