# Spec: Image-OCR GLM-OCR Primary Integration

## Goal / Outcome

Make Z.AI's **GLM-OCR** the **primary** OCR engine in the existing `image-ocr` skill, resolving the recurring Gemini reliability failures documented in track `20260614-image-ocr-skill`. The existing Gemini and Tesseract tiers are **retained** as secondary and offline fallbacks, producing a 3-tier cascade:

- **Tier 1 (Primary): GLM-OCR** -- dedicated OCR model, native Markdown output, direct Z.AI API, backed by the user's monthly Z.AI subscription (independent quota from Gemini's monthly cap).
- **Tier 2 (Secondary): Gemini 2.5 Flash** -- kept as-is; engages when GLM-OCR is unavailable/fails.
- **Tier 3 (Offline): Tesseract** -- zero-network last resort, kept as-is.

This is an **additive inversion of engine priority**, not a rewrite. The CLI contract, output format, and batch/manifest behavior are preserved.

## Motivation

Track `20260614-image-ocr-skill` shipped the Gemini-primary skill, but its execution log documents that the skill is **currently non-functional end-to-end**: every Gemini key in `~/.local/gemini-proxy/` returns `HTTP 429: "Your project has exceeded its monthly spending cap"`, and the Tesseract fallback binary is not installed. The local Gemini proxy (`127.0.0.1:8000`) is a documented fragility point. This recurs monthly.

GLM-OCR directly resolves the root cause via an independent API path on a separately-billed subscription, while offering superior OCR-specific quality (native Markdown, tables to MD, math to LaTeX; #1 on OmniDocBench V1.5 at 94.62) at $0.03/M tokens.

## Constraints / Non-Goals

- **Do NOT rewrite the skill.** Modify the existing `ocr_extract.py` additively.
- **Do NOT remove** Gemini or Tesseract tiers.
- **Do NOT change the output format** (YAML frontmatter + `manifest.json`).
- **Do NOT add the `glmocr` SDK dependency.** Use raw `httpx` to mirror the existing Gemini pattern.
- **Do NOT add PDF input support** in this track. PDFs belong to `doc-to-markdown`; the `image-ocr` skill accepts image formats only. (GLM-OCR native PDF support is noted as a future enhancement.)
- Tesseract binary installation remains **out of scope** (the tier is retained as-is for when the user installs it).
- `--no-fallback` semantics change: in `auto` mode it now stops after the primary (GLM-OCR) rather than only skipping Tesseract. This is the intuitive meaning and will be documented.

## Definition of Done

- [ ] `ocr_extract.py` has a working `extract_glmocr()` + `run_glmocr()` code path (raw httpx, Bearer auth).
- [ ] `--engine` accepts `glmocr` in addition to `auto`/`gemini`/`tesseract`.
- [ ] `--engine auto` (the default) tries **GLM-OCR first**, then Gemini, then Tesseract.
- [ ] Non-PNG/JPG inputs (GIF/WEBP/BMP/TIFF) are auto-converted to PNG via Pillow before GLM-OCR upload.
- [ ] Images exceeding GLM-OCR 10MB limit are downscaled via Pillow (LANCZOS) until under the limit, rather than rejected.
- [ ] `ZAI_API_KEY` is read from env (loaded from `~/.config/opencode/.env` at opencode startup).
- [ ] `SKILL.md` and `reference.md` reflect GLM-OCR as primary, document `ZAI_API_KEY`, and the 3-tier cascade.
- [ ] Existing Gemini and Tesseract paths remain functional (no regression).
- [ ] A request-shape verification passes (payload well-formed, no live API call required).
- [ ] A live GLM-OCR test succeeds on a sample image (requires opencode restart to load `ZAI_API_KEY`), OR is documented as blocked-pending-restart with the exact command to run.
- [ ] All plan.md tasks marked `[x]`; metadata.json + ledgers synchronized.

## Requirements

- [ ] New GLM-OCR constants block (`GLMOCR_MODEL`, `GLMOCR_API_URL`, `GLMOCR_MAX_IMAGE_BYTES`, `GLMOCR_NATIVE_FORMATS`).
- [ ] `resolve_zai_key()` returning `ZAI_API_KEY` from env.
- [ ] `encode_for_glmocr(path)` producing a `data:<mime>;base64,...` data URI, with Pillow conversion for non-native formats and progressive downscale for >10MB.
- [ ] `extract_glmocr()` async function mirroring `extract_gemini()` (httpx POST, Bearer auth, JSON body, parse `md_results` + `usage`).
- [ ] `run_glmocr()` wrapper with 429-retry and graceful error handling, mirroring `run_gemini()`.
- [ ] `process_image()` updated: explicit `glmocr` branch + reordered `auto` cascade (GLM-OCR then Gemini then Tesseract).
- [ ] `parse_args()` `--engine` choices updated to `["auto", "glmocr", "gemini", "tesseract"]`.
- [ ] Module docstring updated to "Three-tier".
- [ ] `SKILL.md` engines table, setup, and gotchas updated.
- [ ] `reference.md` tiers, key setup, and troubleshooting updated.

## Non-Requirements (Deferred)

- [ ] No PDF input support (future enhancement; GLM-OCR supports up to 30-page PDFs natively).
- [ ] No `glmocr` SDK integration (raw httpx is sufficient and matches existing pattern).
- [ ] No local `ollama run glm-ocr` / mlx-vlm integration (cloud-first skill).
- [ ] No Tesseract binary installation (user separate decision).
- [ ] No changes to `visual-ocr` sister skill (separate track if desired).

## Acceptance Criteria

- [ ] `python ocr_extract.py --help` shows `glmocr` in `--engine` choices.
- [ ] `python ocr_extract.py test.png --engine glmocr --dry-run` succeeds (or fails only on missing key with an actionable message).
- [ ] After opencode restart, `python ocr_extract.py test.png` (auto) uses GLM-OCR and produces `.md` with `engine: glm-ocr` in frontmatter.
- [ ] Forcing `--engine gemini` still routes to Gemini (no regression).
- [ ] A GIF/WEBP/BMP/TIFF input converts to PNG and succeeds via GLM-OCR.
- [ ] An image >10MB downscales and succeeds via GLM-OCR.
- [ ] `SKILL.md` and `reference.md` accurately describe the 3-tier cascade and `ZAI_API_KEY`.

## Related Tracks

- `20260614-image-ocr-skill` (completed) -- built the original Gemini-primary skill being modified here. Its execution log documents the Gemini monthly-cap root cause this track resolves.

## API Reference (GLM-OCR)

- **Endpoint:** `POST https://api.z.ai/api/paas/v4/layout_parsing`
- **Auth:** `Authorization: Bearer <ZAI_API_KEY>`
- **Request body:** `{"model": "glm-ocr", "file": "<data-uri-or-url>"}` (required); optional `return_crop_images`, `need_layout_visualization`, `start_page_id`, `end_page_id`, `request_id`, `user_id`.
- **Response:** `md_results` (Markdown string), `layout_details` (array; each element has `label` in {image,text,formula,table}, `bbox_2d`, `content`), `usage` (`prompt_tokens`, `completion_tokens`, `total_tokens`).
- **Limits:** single image <=10MB; supports PDF/JPG/PNG natively (this skill sends PNG/JPG data URIs; other formats converted client-side).
- **Docs:** https://docs.z.ai/llms.txt -- key management at https://z.ai/manage-apikey/apikey-list
