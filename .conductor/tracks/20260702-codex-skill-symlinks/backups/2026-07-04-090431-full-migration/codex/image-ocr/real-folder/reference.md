# Reference: Image-to-Markdown OCR Skill

Full reference for the `image-ocr` skill.

## CLI Reference

```
python scripts/ocr_extract.py IMAGE_PATH [OPTIONS]
```

### Positional Arguments

| Argument | Description |
|----------|-------------|
| `image_path` | Image file, or directory (with `--batch`) |

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--output-dir PATH` | `./ocr-output` | Output directory for `.md` files |
| `--batch` | off | Process all images in a directory |
| `--engine {auto,glmocr,gemini,tesseract}` | `auto` | Extraction engine (auto cascades GLM-OCR -> Gemini -> Tesseract) |
| `--language LANG` | `auto` | Language hint (auto=eng for Tesseract) |
| `--preserve-layout` | off | Preserve headings, lists, tables |
| `--dry-run` | off | Preview without writing files |
| `--no-fallback` | off | In `auto` mode, stop after primary GLM-OCR and skip Gemini/Tesseract fallbacks |

### Supported Formats

PNG, JPG, JPEG, GIF, WEBP, BMP, TIFF. GLM-OCR (Tier 1) limit is 10MB and accepts PNG/JPG natively; other formats auto-convert to PNG via Pillow, and oversized images auto-downscale. Gemini (Tier 2) limit is 20MB.

## Engines

### Tier 1: GLM-OCR (primary, default auto)

- Z.AI layout_parsing API: `POST https://api.z.ai/api/paas/v4/layout_parsing`
- Model: `glm-ocr` (dedicated OCR; #1 on OmniDocBench V1.5)
- Native Markdown output (tables to MD tables, math to LaTeX, headings/lists preserved)
- $0.03/M tokens (input + output, uniform rate) — extraordinarily cheap ($3 covers tens of thousands of images)
- **Billing is SEPARATE from the Z.AI Coding Plan subscription.** The Coding Plan (Pro/Max/Lite, $18+/month) covers only 4 text models (GLM-5.2, GLM-5-Turbo, GLM-4.7, GLM-4.5-Air) at the `/api/coding/paas/v4` endpoint. GLM-OCR uses the standard pay-as-you-go API at `/api/paas/v4`, which requires its own pre-paid cash balance.
- Recharge balance at: https://z.ai/manage-apikey/billing (minimum $3; credit cards must have 3DS disabled)
- Current balance: $3.00 (added 2026-06-15)
- API key: `ZAI_API_KEY` env var, loaded from `~/.config/opencode/.env` at startup
- Formats: PNG/JPG native; GIF/WEBP/BMP/TIFF auto-convert to PNG; >10MB auto-downscale
- Retry once on HTTP 429 (2s delay), then cascades to Gemini in `auto` mode

### Tier 2: Gemini 2.5 Flash (secondary)

- Direct Google Generative Language API (`v1beta`)
- Model: `gemini-2.5-flash`
- Free tier, multimodal, handles handwriting / photos / multi-language
- API key auto-discovery order:
  1. `GEMINI_API_KEY` environment variable
  2. `%USERPROFILE%\.local\gemini-proxy\key_names.json` (keys are API keys; values are labels)
  3. `%USERPROFILE%\.local\gemini-proxy\api_keys.txt` (first non-empty line)
- Retry once on HTTP 429 (2 s delay), then falls back to Tesseract in `auto` mode

### Tier 3: Tesseract (offline fallback)

- Via `pytesseract` + `Pillow`
- Binary detection order:
  1. `TESSERACT_CMD` environment variable
  2. `C:\Program Files\Tesseract-OCR\tesseract.exe` (Windows default)
  3. `shutil.which("tesseract")` (PATH lookup)
- `--preserve-layout` maps to `--psm 6` (uniform block of text)

## Setup

### Python packages

```bash
pip install httpx pytesseract Pillow
```

### Tesseract binary (Windows)

```powershell
winget install UB-Mannheim.TesseractOCR
```

Or download from https://github.com/UB-Mannheim/tesseract/wiki.

Default install path: `C:\Program Files\Tesseract-OCR\tesseract.exe`. If installed elsewhere, set `TESSERACT_CMD`.

### Tesseract language packs

On Windows, the UB-Mannheim installer lets you select additional languages. To add languages after install, re-run the installer and check the desired language boxes. Common codes:

| Language | Code |
|----------|------|
| English | `eng` |
| French | `fra` |
| German | `deu` |
| Spanish | `spa` |
| Chinese (Simplified) | `chi_sim` |
| Japanese | `jpn` |
| Korean | `kor` |

### Gemini API key

1. Get a free key at https://aistudio.google.com/app/apikey
2. Set `GEMINI_API_KEY` env var, OR
3. Add a line to `%USERPROFILE%\.local\gemini-proxy\api_keys.txt`

## Output Format

### Single-file `.md`

```markdown
---
source: "document.png"
engine: gemini-direct
model: gemini-2.5-flash
extracted: 2026-06-14T12:30:00
language: auto
---

<extracted text>
```

### Batch `manifest.json`

```json
{
  "processed": [{"source": "a.png", "output": "ocr-output/a.md", "engine": "gemini-direct"}],
  "failed":    [{"source": "b.png", "reason": "extraction failed"}],
  "skipped":   []
}
```

## Performance Tips

- **Batch delay**: 0.5 s between images to respect Gemini free-tier rate limits.
- **Large batches**: Consider `--engine tesseract` for clean printed text to avoid rate limits.
- **Image size**: Resize images >20 MB before OCR (Gemini limit).
- `--dry-run` to preview extraction before committing files.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `No Gemini API key found` | Set `GEMINI_API_KEY` or populate `api_keys.txt` |
| `Tesseract not found` | Install binary or set `TESSERACT_CMD` |
| `Image too large` | Resize/compress to <20 MB |
| Gemini 429 rate limit | Wait, or use `--engine tesseract` |
| `Gemini API timeout (60s)` | Retry, or use `--engine tesseract` |
| Wrong language output | Pass `--language <lang>` |