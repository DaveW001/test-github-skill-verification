# Spec: Image-to-Markdown OCR Skill

## Goal

Create a new OpenCode skill (`image-ocr`) that extracts plain text from images (photos of documents, screenshots, scanned pages, receipts, whiteboards) and outputs clean, structured Markdown. This fills the gap between `doc-to-markdown` (PDF/HTML sources) and `visual-ocr` (visual structures like org charts/diagrams in slide images).

## Motivation

Current skill coverage:

| Input Type | Existing Skill | Gap |
|---|---|---|
| PDF/HTML to Markdown | `doc-to-markdown` | Covers document files only |
| Slide images to structured Markdown (diagrams, org charts) | `visual-ocr` | Specialized for visual relationships, not plain text |
| **Image to plain text Markdown** | **None** | **This skill** |

User needs: photos of documents, screenshots, scanned pages, receipts, handwritten notes, whiteboard photos -- all converted to clean Markdown text.

## Architecture Decision: Two-Tier Hybrid

### Tier 1 (Primary): Gemini 2.5 Flash via Direct Google API
- **Why**: Best all-rounder quality across heterogeneous image types (handwriting, photos, complex layouts, forms, receipts). Mirrors `visual-ocr` infrastructure. Free tier (Google AI Studio) keeps costs zero for typical usage. Handles multi-language, rotated text, low-quality photos.
- **API key**: Auto-loaded from `~/.local/gemini-proxy/api_keys.txt` or `GEMINI_API_KEY` env var (same pattern as `visual-ocr`)
- **Model**: `gemini-2.5-flash` (fast, multimodal, generous free tier)

### Tier 2 (Offline Fallback): Tesseract via pytesseract
- **Why**: Zero API dependency, works fully offline, no setup beyond `pip install pytesseract` + Tesseract binary. Good on clean printed text (99.3% baseline accuracy). Falls back automatically when Gemini key is unavailable or API fails.
- **Limitations**: No handwriting, no table structure, no complex layouts. Clean printed text only.
- **Tradeoff accepted**: Simplicity over PaddleOCR's marginally better accuracy. PaddleOCR's ~500MB PaddlePaddle framework dependency and slower cold start are not justified for a fallback tier.

### Why Not Other Options

| Option | Rejected Because |
|---|---|
| **PaddleOCR as primary** | Heavy dependency (~500MB PaddlePaddle), slower cold start, table extraction only via PP-StructureV3 (complex). Gemini provides better quality on diverse image types. |
| **Surya as primary** | GPL 3.0 license (restrictive for skill distribution), GPU required for practical speed, complex setup. |
| **Marker** | OpenRAIL license concerns, uses Surya under the hood (same GPU/GPL issues), PDF-oriented not image-oriented. |
| **EasyOCR** | Fallen behind in 2026 benchmarks (75.8% accuracy), no compelling advantage over Tesseract+Gemini. |
| **GPT-4o/Claude as primary** | Paid APIs, higher cost per image (~$0.01+), no free tier. Gemini Flash matches quality at zero cost. |
| **Three-tier (Tesseract -> PaddleOCR -> Gemini)** | Over-engineered. Two tiers cover the simplicity/quality tradeoff cleanly. Adding a middle tier adds dependency complexity without meaningful benefit. |

## Requirements

- [ ] Skill directory at `~/.opencode-lazy-vault/image-ocr/` with `SKILL.md`
- [ ] Python script `scripts/ocr_extract.py` with argparse CLI
- [ ] **Tier 1**: Gemini 2.5 Flash extraction via direct Google API (reusing `visual-ocr` patterns)
- [ ] **Tier 2**: Tesseract fallback via pytesseract (auto-triggered on Gemini failure or missing key)
- [ ] `--engine gemini|tesseract|auto` flag to force engine selection (default: `auto`)
- [ ] Input: single image file or directory (batch mode with `--batch`)
- [ ] Supported formats: PNG, JPG, JPEG, GIF, WEBP, BMP, TIFF
- [ ] Output: clean Markdown files with YAML frontmatter (source, engine, model, timestamp, language)
- [ ] `--output-dir` flag for output location (default: `./ocr-output`)
- [ ] `--dry-run` flag for preview without writing files
- [ ] `--language` flag for OCR language hint (default: `auto` for Gemini, `eng` for Tesseract)
- [ ] `--preserve-layout` flag to attempt structural preservation (headings, lists, paragraphs)
- [ ] Batch processing with manifest output (processed/skipped/failed)
- [ ] Rate limiting between API calls (0.5s delay)
- [ ] API key auto-discovery: `GEMINI_API_KEY` env var -> `~/.local/gemini-proxy/key_names.json` -> `~/.local/gemini-proxy/api_keys.txt`
- [ ] Graceful error handling with actionable messages (missing key, missing Tesseract binary, image too large)
- [ ] YAML frontmatter follows `visual-ocr` convention for consistency
- [ ] Tesseract binary path detection (Windows default: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- [ ] `SKILL.md` frontmatter: `name: image-ocr`, description with triggers ("OCR", "image to text", "extract text from image", "read text from screenshot", "scan to markdown")
- [ ] Script uses only stdlib + `httpx` (for Gemini) + `pytesseract` (for Tesseract) + `Pillow` (image loading)

## Non-Requirements

- [ ] No table structure extraction (that is `visual-ocr` domain with `--prompt-type table`)
- [ ] No diagram/org-chart/relationship extraction (that is `visual-ocr` domain)
- [ ] No PDF input (that is `doc-to-markdown` domain)
- [ ] No LLM-based post-processing or refinement (keep simple)
- [ ] No GPU dependency
- [ ] No PaddleOCR/Surya/Marker integration (deferred -- can add as `--engine paddle` later if needed)
- [ ] No batch queueing/scheduling (single-run CLI only)
- [ ] No web UI or GUI

## Acceptance Criteria

- [ ] `SKILL.md` passes frontmatter validation (valid `name`, `description` fields)
- [ ] `skill_find "OCR"` and `skill_find "image to text"` both discover the skill
- [ ] `ocr_extract.py` runs successfully with Gemini on a test image (requires API key)
- [ ] `ocr_extract.py` falls back to Tesseract when Gemini key is absent
- [ ] `--dry-run` produces preview without writing files
- [ ] Batch mode processes a directory and produces manifest
- [ ] Output Markdown is clean, readable, and includes YAML frontmatter
- [ ] Error messages are actionable (tell user what to install/set)
- [ ] Script handles edge cases: empty directory, unsupported format, oversized image, missing Tesseract binary
- [ ] All tasks in plan.md marked `[x]`
