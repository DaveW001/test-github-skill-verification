# Plan: OpenAI Multi-Auth Doc Fixup

## Approach

1. Research the actual plugin architecture (source code, README, operator runbook)
2. Verify current auth state (global auth.json, per-project plugin storage, diagnostic output)
3. Rewrite the existing troubleshooting note with corrected architecture
4. Create a comprehensive guide covering setup, operation, and troubleshooting
5. Add a dedicated step-by-step runbook with clear "who does what where" delineation
6. Verify cross-references and formatting
7. Mark complete

## Tasks

- [x] Research plugin architecture (accounts/state.js, storage/state.js, README)
- [x] Verify current auth state (auth.json, per-project accounts file, codex-* diagnostic output)
- [x] Rewrite `codex-multi-auth-refresh-token-reused.md` (7594 → 15270 bytes)
  - Corrected per-project-required language
  - Added global fallback explanation
  - Added "Fix: Burned Refresh Token" section
  - Added multi-account setup instructions
  - Added Revision Notes
- [x] Create `openai-codex-multi-auth-guide.md` (NEW, 16944 bytes)
  - Section 1: Architecture (three layers)
  - Section 2: Initial Setup
  - Section 3: Daily Operation Commands
  - Section 4: Per-Project vs Global Storage
  - Section 5: Troubleshooting Decision Tree
  - Section 6: Common Errors & Fixes
  - Section 7: Step-by-Step Fix Runbook (THE KEY DELIVERABLE)
  - Section 8: Best Practices
- [x] Add "Where Commands Run" reference table (user terminal vs agent internal)
- [x] Add Quick Reference fix sequence (compact 3-phase summary)
- [x] Verify cross-references between docs
- [x] Final visual check (code block balance, anchors, formatting)

## Dependencies

None — documentation only.

## Risks

1. File operations could corrupt content (mitigated by using Set-Content for full rewrites)
2. Unicode arrow characters (→) corrupted in PowerShell here-strings (mitigated by using ASCII `->` in Quick Reference)

## Validation

- Verified file structure (521 lines, 8 sections)
- Confirmed exactly 3 PHASE blocks (no duplicates from earlier failed edit)
- Confirmed 2 "Quick Reference" entries are in different sections (not duplicates)
- Spot-checked critical content reads correctly
- Verified cross-references between docs resolve