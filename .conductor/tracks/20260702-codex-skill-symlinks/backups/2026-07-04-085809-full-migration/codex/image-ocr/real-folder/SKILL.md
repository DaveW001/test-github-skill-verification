---
name: image-ocr
description: >-
  Extract plain text from images (photos of documents, screenshots, scanned pages,
  receipts, whiteboards) and output clean Markdown. Uses GLM-OCR (dedicated OCR model) as primary, with Gemini 2.5 Flash
  secondary and Tesseract offline fallback. Use when user asks to OCR an image,
  extract text from a photo/screenshot/scan, convert image to text/markdown, or
  read text from an image file. Triggers: "OCR", "image to text", "extract text
  from image", "read text from screenshot", "scan to markdown", "image to markdown".
---

## Quick Start

```bash
# Single image
python scripts/ocr_extract.py document.png

# Batch directory
python scripts/ocr_extract.py ./scans/ --batch --output-dir ./output/

# Force Gemini, no fallback
python scripts/ocr_extract.py photo.jpg --engine gemini

# Preserve layout (headings, tables, lists)
python scripts/ocr_extract.py report.png --preserve-layout
```

## Engines

| Engine | Tier | Quality | Speed | Setup | Best For |
|--------|------|---------|-------|-------|----------|
| GLM-OCR (default primary) | 1 | Best | Fast | `ZAI_API_KEY` (Z.AI subscription) | Dedicated OCR: native Markdown, tables, math, handwriting, multi-language |
| Gemini 2.5 Flash (secondary) | 2 | High | Fast | `GEMINI_API_KEY` (free tier) | General fallback; independent failure mode |
| Tesseract (offline last resort) | 3 | Good | Fast | Binary install | Clean printed text, zero network |

Use `--engine auto` (default) to cascade GLM-OCR -> Gemini -> Tesseract.
Force a tier with `--engine glmocr` / `--engine gemini` / `--engine tesseract`.
Use `--no-fallback` with `--engine auto` to stop after primary GLM-OCR and skip Gemini/Tesseract.

## Setup

**Required (always)**:
```bash
pip install httpx pytesseract Pillow
```

**GLM-OCR API key** (for Tier 1 primary):
- Set `ZAI_API_KEY` environment variable. Get a key at https://z.ai/manage-apikey/apikey-list
- On OpenCode, place it in `%USERPROFILE%\.config\opencode\.env` (loads at startup)
- **Billing is separate from the Z.AI Coding Plan subscription.** The Coding Plan (Pro/Max/Lite) covers only 4 text models (GLM-5.x). GLM-OCR uses the standard pay-as-you-go API (`api.z.ai/api/paas/v4`) which requires its own pre-paid balance.
- Recharge at https://z.ai/manage-apikey/billing (min $3; disable 3DS on credit cards)
- Pricing: $0.03/M tokens (input + output). At this rate, $3 covers tens of thousands of OCR operations.
- Balance added: $3.00 on 2026-06-15

**Gemini API key** (for Tier 2 secondary):
- Set `GEMINI_API_KEY` environment variable, OR
- Place key in `%USERPROFILE%\.local\gemini-proxy\api_keys.txt`

**Tesseract binary** (for Tier 2 fallback):
- Windows: `winget install UB-Mannheim.TesseractOCR`
- Or set `TESSERACT_CMD` environment variable to binary path

## Output Format

Each output `.md` file has YAML frontmatter:
```yaml
---
source: "document.png"
engine: gemini-direct
model: gemini-2.5-flash
extracted: 2026-06-14T12:30:00
language: auto
---
```

Batch mode also writes `manifest.json` with `processed`, `failed`, `skipped` arrays.

## Gotchas

- **GLM-OCR key not found**: Check `ZAI_API_KEY` in `%USERPROFILE%\.config\opencode\.env`. Requires OpenCode restart after first setting it.
- **GLM-OCR formats**: Natively accepts PNG/JPG only. GIF/WEBP/BMP/TIFF auto-convert to PNG via Pillow. Images >10MB auto-downscale.
- **GLM-OCR insufficient balance (error 1113)**: GLM-OCR uses the pay-as-you-go API, NOT the Coding Plan subscription. Recharge at https://z.ai/manage-apikey/billing. The Coding Plan covers only GLM-5.x text models.
- **Gemini key not found**: Check `GEMINI_API_KEY` env var or `%USERPROFILE%\.local\gemini-proxy\api_keys.txt`
- **Tesseract not found on Windows**: Default path is `C:\Program Files\Tesseract-OCR\tesseract.exe`. Set `TESSERACT_CMD` if installed elsewhere.
- **Language packs**: Tesseract needs language packs installed. Gemini handles most languages natively.
- **Large images**: Images >20MB are skipped (Gemini API limit).
- **Rate limits**: Gemini free tier has rate limits. Script retries once on 429, then falls back to Tesseract.

## When to Use This vs Other Skills

| Skill | Use When |
|-------|----------|
| `image-ocr` (this) | Extract plain text from images (photos, screenshots, scans, receipts) |
| `visual-ocr` | Extract visual structure (org charts, diagrams, tables with relationships) |
| `doc-to-markdown` | Convert PDF or HTML documents to Markdown |
