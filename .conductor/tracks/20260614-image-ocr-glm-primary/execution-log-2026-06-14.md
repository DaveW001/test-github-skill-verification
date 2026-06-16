# Execution Log: 20260614-image-ocr-glm-primary

**Date:** 2026-06-14 (build), 2026-06-15 (live validation)
**Agent:** Build Agent (opencode, glm-5.1 model)
**Track:** Image-OCR GLM-OCR Primary Integration
**Final Status:** COMPLETED (32/32 tasks, 100%)

## Summary

GLM-OCR is now the primary OCR engine in the image-ocr skill. All build tasks (Phase
0-3) and all validation tasks (Phase 4) completed successfully. The integration was
live-validated on 2026-06-15 after resolving a Z.AI account billing issue: GLM-OCR uses
the standard pay-as-you-go API (`/api/paas/v4`), which is SEPARATE from the Coding Plan
subscription and requires its own pre-paid balance. $3.00 was added on 2026-06-15.

Both `--engine glmocr` (explicit) and `--engine auto` (cascade) successfully OCR'd a
4-line test image, producing perfect Markdown output with `engine: glm-ocr` in the
YAML frontmatter.

## Tasks Completed (32/32)

### Phase 0 - Setup & Preconditions (4/4)
All target files verified, deps confirmed (httpx 0.28.1, Pillow 12.1.0), ZAI_API_KEY in .env,
timestamped backups created.

### Phase 1 - GLM-OCR Engine Implementation (4/4)
Added GLMOCR_* constants, resolve_zai_key(), _downscale_to_png() + encode_for_glmocr(),
and extract_glmocr()/run_glmocr() async pair. All imports + ast.parse verified.

### Phase 2 - Pipeline Integration (6/6)
--engine accepts glmocr; CLI help updated; docstring updated; process_image() has glmocr
branch; auto cascade reordered to GLM-OCR -> Gemini -> Tesseract; --help smoke test passes.

### Phase 3 - Documentation (8/8)
SKILL.md and reference.md updated with 3-tier cascade, ZAI_API_KEY setup, separate billing
documentation (pay-as-you-go vs Coding Plan), format conversion notes, --no-fallback semantics.

### Phase 4 - Validation & Handover (11/11)
- 4.1 Request-shape smoke test -- PASS
- 4.2 Test images generated -- PASS
- 4.3 encode_for_glmocr: PNG native + GIF->PNG convert -- PASS
- **4.4 Live GLM-OCR test (--engine glmocr)** -- **PASS** (2026-06-15)
  - 4-line test image (600x300) OCR'd perfectly
  - Output: `engine: glm-ocr`, `model: glm-ocr` in frontmatter
  - All 4 text lines extracted correctly
- **4.5 Verify --engine auto cascades to GLM-OCR** -- **PASS** (2026-06-15)
  - `--engine auto` selected GLM-OCR first (no Gemini/Tesseract fallback triggered)
  - Output frontmatter: `engine: glm-ocr`
- 4.6 Regression: Gemini (429 monthly cap) + Tesseract (not installed) both ran without traceback -- PASS
- 4.7 Test artifacts cleaned -- PASS
- 4.8 metadata.json: status=completed, 32/32=100% -- PASS
- 4.9 tracks-ledger.md: moved to Completed Tracks -- PASS
- 4.10 This execution log -- PASS

## Issues Encountered & Resolved

1. **Tool-layer `Bun is not defined`** (all File tools). Switched to PowerShell-first mode
   with a Python `_apply_edits.py` helper for literal string replacements. All 18+ edits applied
   cleanly with CRLF preservation.

2. **ZAI_API_KEY not in child-process env**: opencode loads `.env` at startup but bash-tool
   children don't inherit. Worked around by sourcing the key from `.env` inline via PowerShell.

3. **Z.AI error 1113 "Insufficient balance"**: Root cause was a two-billing-path issue.
   The Coding Plan subscription (Pro/Max/Lite) covers ONLY 4 text models (GLM-5.2, GLM-5-Turbo,
   GLM-4.7, GLM-4.5-Air) at the `/api/coding/paas/v4` endpoint. GLM-OCR uses the standard
   pay-as-you-go API at `/api/paas/v4`, which requires its own pre-paid cash balance.
   - Fix: Added $3.00 at https://z.ai/manage-apikey/billing (minimum recharge; 3DS disabled)
   - Documented in SKILL.md and reference.md with recharge link and pricing details
   - This billing separation is now documented in the skill docs for future reference

4. **Ledger cleanup**: Required multiple approaches to remove the old Active Tracks entry
   due to CRLF matching. Resolved with direct string replacement.

## Billing Reference (documented in skill docs)

- GLM-OCR: $0.03/M tokens (input + output, uniform)
- Uses pay-as-you-go API at `api.z.ai/api/paas/v4` (NOT the Coding Plan endpoint)
- Recharge: https://z.ai/manage-apikey/billing (min $3, no 3DS)
- Current balance: $3.00 (added 2026-06-15)
- At $0.03/M tokens, $3 covers tens of thousands of OCR operations

## Validation Summary

| Validation | Result |
|------------|--------|
| Phase 1 imports + syntax | PASS |
| Phase 2 --help smoke test | PASS |
| Phase 3 content checks (8 tasks) | PASS |
| Phase 4.1 request-shape | PASS |
| Phase 4.3 PNG native + GIF convert | PASS |
| Phase 4.4 live GLM-OCR extraction | **PASS** (perfect output) |
| Phase 4.5 auto cascade selects GLM-OCR | **PASS** (engine: glm-ocr) |
| Phase 4.6 Gemini/Tesseract regression | PASS (no traceback) |

**Track COMPLETE. No remaining items.**


