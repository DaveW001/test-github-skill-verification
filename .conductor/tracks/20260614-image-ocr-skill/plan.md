# Plan: Image-to-Markdown OCR Skill

## Track Info
- **Track ID**: 20260614-image-ocr-skill
- **Created**: 2026-06-14
- **Status**: Completed (2026-06-14)

## Architecture Summary

Two-tier OCR skill mirroring `visual-ocr` patterns:
- **Tier 1 (Primary)**: Gemini 2.5 Flash (direct Google API, free tier, best quality)
- **Tier 2 (Offline Fallback)**: Tesseract via pytesseract (zero setup, clean printed text)

**Skill location**: `%USERPROFILE%\.opencode-lazy-vault\image-ocr\`
**Absolute path**: `C:\Users\DaveWitkin\.opencode-lazy-vault\image-ocr\`

---

## Prerequisites & Environment State (Verified 2026-06-14)

| Item | Status | Notes |
|------|--------|-------|
| `%USERPROFILE%\.opencode-lazy-vault\image-ocr\` | Does NOT exist | Safe to create; collision guard still applies |
| `httpx` 0.28.1 | Installed | `pip show httpx` confirms |
| `pytesseract` 0.3.13 | Installed | `pip show pytesseract` confirms |
| `Pillow` 12.1.0 | Installed | `pip show Pillow` confirms |
| Gemini proxy key files | Exist | Both `api_keys.txt` and `key_names.json` at `%USERPROFILE%\.local\gemini-proxy\` |
| Tesseract binary | **NOT installed** | Not at `C:\Program Files\Tesseract-OCR\tesseract.exe`. Must install for Tier 2 testing. |
| `visual-ocr` skill | Exists | `%USERPROFILE%\.opencode-lazy-vault\visual-ocr\` — pattern source for Gemini API integration |
| `doc-to-markdown` skill | Exists | `%USERPROFILE%\.opencode-lazy-vault\doc-to-markdown\` — pattern source for batch/manifest/output |

**Action before Phase 3**: Install Tesseract via `winget install UB-Mannheim.TesseractOCR` or download from https://github.com/UB-Mannheim/tesseract/wiki. Without it, Tier 2 cannot be tested.

---

## Phase 1 - Scaffolding

- [x] **1.1 Create skill directory structure**

  Run these PowerShell commands:
  ```powershell
  $base = "$env:USERPROFILE\.opencode-lazy-vault\image-ocr"
  if (Test-Path $base) { Write-Error "Directory already exists: $base — STOP. Do not overwrite."; exit 1 }
  New-Item -ItemType Directory -Path "$base\scripts" -Force
  New-Item -ItemType File -Path "$base\SKILL.md" -Force
  New-Item -ItemType File -Path "$base\scripts\ocr_extract.py" -Force
  ```

  **Verify**: `Test-Path "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts"` returns `True`.
  **Error recovery**: If directory exists, stop and ask user before proceeding.

- [x] **1.2 Write `SKILL.md` frontmatter**

  Write this exact YAML block as the first content of `%USERPROFILE%\.opencode-lazy-vault\image-ocr\SKILL.md`:
  ```yaml
  ---
  name: image-ocr
  description: >-
    Extract plain text from images (photos of documents, screenshots, scanned pages,
    receipts, whiteboards) and output clean Markdown. Uses Gemini 2.5 Flash for best
    quality with Tesseract offline fallback. Use when user asks to OCR an image,
    extract text from a photo/screenshot/scan, convert image to text/markdown, or
    read text from an image file. Triggers: "OCR", "image to text", "extract text
    from image", "read text from screenshot", "scan to markdown", "image to markdown".
  ---
  ```

  **Verify**: File starts with `---` and contains `name: image-ocr`.

- [x] **1.3 Write `SKILL.md` body sections (placeholder — completed in Phase 6)**

  For now, add a placeholder comment below the frontmatter:
  ```markdown
  <!-- Body sections written in Phase 6 after script is functional -->
  ```

  **Verify**: File contains the placeholder comment.
---

## Phase 2 - Core Script: Gemini Tier

- [x] **2.1 Create `ocr_extract.py` with argparse CLI skeleton**

  Write this skeleton to `%USERPROFILE%\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py`:
  ```python
  #!/usr/bin/env python3
  """Image-to-Markdown OCR extraction. Two-tier: Gemini 2.5 Flash + Tesseract fallback."""

  import argparse
  import sys
  from pathlib import Path

  SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"}

  def parse_args():
      parser = argparse.ArgumentParser(description="Extract text from images as Markdown")
      parser.add_argument("image_path", type=Path, help="Image file or directory (with --batch)")
      parser.add_argument("--output-dir", type=Path, default=Path("./ocr-output"), help="Output directory (default: ./ocr-output)")
      parser.add_argument("--batch", action="store_true", help="Process all images in directory")
      parser.add_argument("--engine", choices=["auto", "gemini", "tesseract"], default="auto", help="Extraction engine (default: auto)")
      parser.add_argument("--language", default="auto", help="OCR language hint (default: auto for Gemini, eng for Tesseract)")
      parser.add_argument("--preserve-layout", action="store_true", help="Preserve visual structure (headings, lists, tables)")
      parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
      parser.add_argument("--no-fallback", action="store_true", help="Skip Tesseract fallback in auto mode")
      return parser.parse_args()

  def main():
      args = parse_args()
      # TODO: implement pipeline (Phases 2-4)
      print(f"Image: {args.image_path}, Engine: {args.engine}")

  if __name__ == "__main__":
      main()
  ```

  **Verify**: `python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" --help` prints usage without errors.
  **Error recovery**: If `python` not found, try `python3`. If neither works, check Python installation.

- [x] **2.2 Implement Gemini extraction function**

  Port from `%USERPROFILE%\.opencode-lazy-vault\visual-ocr\scripts\extract_visual.py`. Add these functions to `ocr_extract.py`:

  ```python
  import base64
  import json
  import os
  import time
  from datetime import datetime
  import httpx

  GEMINI_MODEL = "gemini-2.5-flash"
  GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

  def resolve_gemini_key() -> str | None:
      """Resolve Gemini API key: env var -> key_names.json -> api_keys.txt."""
      key = os.environ.get("GEMINI_API_KEY")
      if key:
          return key.strip()
      proxy_dir = Path.home() / ".local" / "gemini-proxy"
      key_names_path = proxy_dir / "key_names.json"
      if key_names_path.exists():
          try:
              data = json.loads(key_names_path.read_text(encoding="utf-8"))
              for k in data.values():
                  return k.strip()
          except Exception:
              pass
      api_keys_path = proxy_dir / "api_keys.txt"
      if api_keys_path.exists():
          lines = api_keys_path.read_text(encoding="utf-8").strip().splitlines()
          if lines:
              return lines[0].strip()
      return None

  def encode_image(path: Path) -> tuple[str, str]:
      """Encode image to base64. Returns (base64_str, media_type). Raises if >20MB."""
      size_mb = path.stat().st_size / (1024 * 1024)
      if size_mb > 20:
          raise ValueError(f"Image too large: {size_mb:.1f}MB (max 20MB)")
      suffix = path.suffix.lower()
      media_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                   ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp", ".tiff": "image/tiff"}
      media_type = media_map.get(suffix, "image/png")
      b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
      return b64, media_type

  def build_gemini_prompt(language: str, preserve_layout: bool) -> str:
      base = (
          "Extract ALL text content from this image as clean Markdown.\n"
          "Preserve paragraph structure, headings, bullet points, and numbered lists.\n"
          "Maintain reading order (top-to-bottom, left-to-right).\n"
          "Do not add commentary or descriptions -- output ONLY the extracted text.\n"
          "If the image contains handwriting, transcribe it as faithfully as possible."
      )
      if preserve_layout:
          base += (
              "\n\nPreserve visual structure: use ## for headings, markdown tables for tabular data, "
              "code blocks for code, blockquotes for quoted text."
          )
      if language and language != "auto":
          base += f"\n\nThis text is in {language}."
      return base

  async def extract_gemini(image_path: Path, language: str, preserve_layout: bool) -> dict:
      """Call Gemini API. Returns dict with keys: text, model, tokens_in, tokens_out."""
      key = resolve_gemini_key()
      if not key:
          raise RuntimeError("No Gemini API key found. Set GEMINI_API_KEY or place key in ~/.local/gemini-proxy/")
      b64, media_type = encode_image(image_path)
      prompt = build_gemini_prompt(language, preserve_layout)
      payload = {
          "contents": [{"parts": [
              {"text": prompt},
              {"inline_data": {"mime_type": media_type, "data": b64}}
          ]}]
      }
      async with httpx.AsyncClient(timeout=60.0) as client:
          resp = await client.post(f"{GEMINI_API_URL}?key={key}", json=payload)
          resp.raise_for_status()
          data = resp.json()
      text = data["candidates"][0]["content"]["parts"][0]["text"]
      usage = data.get("usageMetadata", {})
      return {
          "text": text,
          "model": GEMINI_MODEL,
          "tokens_in": usage.get("promptTokenCount", 0),
          "tokens_out": usage.get("candidatesTokenCount", 0),
      }
  ```

  **Verify**: `python -c "import sys; sys.path.insert(0, r'$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts'); from ocr_extract import resolve_gemini_key; print(resolve_gemini_key())"` prints a key string (not None).
  **Error recovery**: If key is None, check that `%USERPROFILE%\.local\gemini-proxy\api_keys.txt` exists and contains at least one line.

- [x] **2.3 Implement `--preserve-layout` prompt variant**

  Already handled in `build_gemini_prompt()` above (the `preserve_layout` parameter). No separate code needed.

  **Verify**: Call `build_gemini_prompt("auto", True)` and confirm output contains "Preserve visual structure".

- [x] **2.4 Implement `--language` flag**

  Already handled in `build_gemini_prompt()` above (the `language` parameter). No separate code needed.

  **Verify**: Call `build_gemini_prompt("French", False)` and confirm output contains "This text is in French".

- [x] **2.5 Handle Gemini API responses & errors**

  Add error handling around the `extract_gemini` call in `main()`:
  ```python
  import asyncio

  async def run_gemini(image_path: Path, args) -> dict | None:
      """Run Gemini extraction with retry on 429."""
      for attempt in range(2):
          try:
              result = await extract_gemini(image_path, args.language, args.preserve_layout)
              result["engine"] = "gemini-direct"
              return result
          except httpx.HTTPStatusError as e:
              if e.response.status_code == 429 and attempt == 0:
                  print(f"Rate limited, retrying in 2s...")
                  time.sleep(2)
                  continue
              print(f"Gemini API error: {e.response.status_code} — {e.response.text[:200]}")
              return None
          except Exception as e:
              print(f"Gemini error: {e}")
              return None
      return None
  ```

  **Verify**: Call with a fake key and confirm it prints an error message (not a stack trace).
  **Error recovery**: If httpx not installed, run `pip install httpx`.
---

## Phase 3 - Core Script: Tesseract Fallback Tier

> **PREREQUISITE**: Tesseract binary must be installed. Run: `winget install UB-Mannheim.TesseractOCR` or download from https://github.com/UB-Mannheim/tesseract/wiki. Without this, all tasks in Phase 3 will fail.

- [x] **3.1 Implement Tesseract extraction function**

  Add these functions to `ocr_extract.py`:
  ```python
  import pytesseract
  from PIL import Image

  TESSERACT_WINDOWS_PATH = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")

  def find_tesseract() -> str | None:
      """Locate Tesseract binary. Returns path or None."""
      cmd = os.environ.get("TESSERACT_CMD")
      if cmd and Path(cmd).exists():
          return cmd
      if TESSERACT_WINDOWS_PATH.exists():
          return str(TESSERACT_WINDOWS_PATH)
      import shutil
      found = shutil.which("tesseract")
      if found:
          return found
      return None

  def extract_tesseract(image_path: Path, language: str, preserve_layout: bool) -> dict | None:
      """Extract text via Tesseract. Returns dict or None on failure."""
      tesseract_cmd = find_tesseract()
      if not tesseract_cmd:
          print("Tesseract not found. Install from: https://github.com/UB-Mannheim/tesseract/wiki")
          return None
      pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
      try:
          img = Image.open(image_path)
      except Exception as e:
          print(f"Cannot open image: {e}")
          return None
      lang_code = "eng" if language == "auto" else language
      config = ""
      if preserve_layout:
          config = "--psm 6"
      try:
          text = pytesseract.image_to_string(img, lang=lang_code, config=config)
      except pytesseract.TesseractError as e:
          print(f"Tesseract error: {e}")
          return None
      return {"text": text.strip(), "model": "tesseract", "engine": "tesseract", "tokens_in": 0, "tokens_out": 0}
  ```

  **Verify**: `python -c "import sys; sys.path.insert(0, r'$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts'); from ocr_extract import find_tesseract; print(find_tesseract())"` prints a path (not None).
  **Error recovery**: If None, install Tesseract (see prerequisite above).

- [x] **3.2 Implement `--language` for Tesseract**

  Add a language mapping dict:
  ```python
  LANG_MAP = {
      "english": "eng", "french": "fra", "german": "deu", "spanish": "spa",
      "chinese": "chi_sim", "japanese": "jpn", "korean": "kor", "auto": "eng",
  }

  def resolve_tesseract_lang(language: str) -> str:
      return LANG_MAP.get(language.lower(), language)
  ```

  Use `resolve_tesseract_lang(args.language)` in `extract_tesseract()`.

  **Verify**: `resolve_tesseract_lang("French")` returns `"fra"`.

- [x] **3.3 Handle Tesseract errors gracefully**

  Already handled in `extract_tesseract()` above. Add one more check in `main()`:
  ```python
  if result is None and args.engine == "tesseract":
      print("ERROR: Tesseract extraction failed. See messages above.")
      sys.exit(1)
  ```

  **Verify**: Run with `--engine tesseract` on a non-image file and confirm actionable error message.

---

## Phase 4 - Pipeline Integration

- [x] **4.1 Implement `--engine auto` flow (default)**

  In `main()`, after parsing args:
  ```python
  async def process_image(image_path: Path, args) -> dict | None:
      """Process one image through the selected engine pipeline."""
      if args.engine == "gemini":
          return await run_gemini(image_path, args)
      elif args.engine == "tesseract":
          return extract_tesseract(image_path, resolve_tesseract_lang(args.language), args.preserve_layout)
      else:  # auto
          key = resolve_gemini_key()
          if key:
              result = await run_gemini(image_path, args)
              if result:
                  return result
          if args.no_fallback:
              print("Gemini failed and --no-fallback set. Skipping Tesseract.")
              return None
          return extract_tesseract(image_path, resolve_tesseract_lang(args.language), args.preserve_layout)
  ```

  **Verify**: Run with `--engine auto` on a test image. Confirm it tries Gemini first, then Tesseract.

- [x] **4.2 Implement `--engine gemini` (force Gemini, no fallback)**

  Already handled: `process_image()` returns `run_gemini()` result directly when `args.engine == "gemini"`.

  **Verify**: Run with `--engine gemini` and confirm it does not attempt Tesseract.

- [x] **4.3 Implement `--engine tesseract` (force Tesseract, no API)**

  Already handled: `process_image()` calls `extract_tesseract()` directly when `args.engine == "tesseract"`.

  **Verify**: Run with `--engine tesseract` on a test image.

- [x] **4.4 Implement `--no-fallback` flag**

  Already handled in `process_image()` above (the `args.no_fallback` check).

  **Verify**: Run with `--engine auto --no-fallback` and unset `GEMINI_API_KEY`. Confirm it prints "Skipping Tesseract" and does not call Tesseract.

- [x] **4.5 Implement batch processing (`--batch` flag)**

  Add batch logic to `main()`:
  ```python
  def collect_images(path: Path) -> list[Path]:
      """Collect supported image files from path."""
      if path.is_file():
          return [path] if path.suffix.lower() in SUPPORTED_EXTENSIONS else []
      if path.is_dir():
          all_files = [p for p in path.iterdir() if p.is_file()]
          images = [p for p in all_files if p.suffix.lower() in SUPPORTED_EXTENSIONS]
          skipped = len(all_files) - len(images)
          if skipped > 0:
              print(f"Skipping {skipped} non-image file(s)")
          return sorted(images)
      return []

  async def run_batch(args):
      """Process all images in directory."""
      images = collect_images(args.image_path)
      if not images:
          print(f"No supported images found in {args.image_path}")
          return
      results = {"processed": [], "failed": [], "skipped": []}
      args.output_dir.mkdir(parents=True, exist_ok=True)
      for i, img in enumerate(images):
          print(f"[{i+1}/{len(images)}] {img.name}...")
          result = await process_image(img, args)
          if result:
              out_path = args.output_dir / f"{img.stem}.md"
              if not args.dry_run:
                  write_output(out_path, img, result)
              results["processed"].append({"source": img.name, "output": str(out_path), "engine": result["engine"]})
              print(f"  -> {out_path}")
          else:
              results["failed"].append({"source": img.name, "reason": "extraction failed"})
          if i < len(images) - 1:
              time.sleep(0.5)
      manifest_path = args.output_dir / "manifest.json"
      if not args.dry_run:
          manifest_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
      print(f"\nDone: {len(results['processed'])} processed, {len(results['failed'])} failed")

  def write_output(out_path: Path, source: Path, result: dict):
      """Write Markdown file with YAML frontmatter."""
      frontmatter = (
          f"---\n"
          f"source: \"{source.name}\"\n"
          f"engine: {result['engine']}\n"
          f"model: {result['model']}\n"
          f"extracted: {datetime.now().isoformat(timespec='seconds')}\n"
          f"language: auto\n"
          f"---\n\n"
      )
      out_path.write_text(frontmatter + result["text"], encoding="utf-8")
  ```

  **Verify**: Run `--batch` on a directory with 2+ images. Confirm `manifest.json` is created with `processed`, `failed`, `skipped` arrays.

- [x] **4.6 Implement `--dry-run` mode**

  Add single-file dry-run handler:
  ```python
  async def run_single(args):
      result = await process_image(args.image_path, args)
      if result:
          out_path = args.output_dir / f"{args.image_path.stem}.md"
          if args.dry_run:
              print(f"[DRY RUN] Would write: {out_path}")
              print(f"Engine: {result['engine']}, Model: {result['model']}")
              print(f"Text preview: {result['text'][:200]}...")
          else:
              args.output_dir.mkdir(parents=True, exist_ok=True)
              write_output(out_path, args.image_path, result)
              print(f"Written: {out_path}")
      else:
          print("Extraction failed.")
          sys.exit(1)
  ```

  **Verify**: Run with `--dry-run` and confirm no files are written.

- [x] **4.7 Implement output formatting**

  Already handled in `write_output()` above. Frontmatter format:
  ```yaml
  ---
  source: "document.png"
  engine: gemini-direct
  model: gemini-2.5-flash
  extracted: 2026-06-14T12:30:00
  language: auto
  ---
  ```

  **Verify**: Open a generated `.md` file and confirm frontmatter is valid YAML.
---

## Phase 5 - Error Handling & Edge Cases

- [x] **5.1 Validate input path exists**

  In `main()`, before processing:
  ```python
  if not args.image_path.exists():
      print(f"ERROR: Path not found: {args.image_path}")
      sys.exit(1)
  ```

- [x] **5.2 Validate image format is supported**

  For single-file mode, add:
  ```python
  if args.image_path.is_file() and args.image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
      print(f"ERROR: Unsupported format: {args.image_path.suffix}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}")
      sys.exit(1)
  ```

- [x] **5.3 Check image size (skip if > 20MB)**

  Already handled in `encode_image()`. Add try/except in `process_image()`:
  ```python
  try:
      result = await extract_gemini(image_path, args.language, args.preserve_layout)
  except ValueError as e:
      print(f"Skipping {image_path.name}: {e}")
      return None
  ```

- [x] **5.4 Handle empty directories gracefully**

  Already handled in `run_batch()`: `if not images: print("No supported images found...")`.

- [x] **5.5 Handle mixed content directories**

  Already handled in `collect_images()` above (filters by extension, prints skipped count).

- [x] **5.6 Handle API rate limits**

  Already handled in `run_gemini()` (retry once after 2s on 429).

- [x] **5.7 Handle network errors**

  Add timeout handling in `run_gemini()`:
  ```python
  except httpx.TimeoutException:
      print("Gemini API timeout (60s). Try again or use --engine tesseract.")
      return None
  ```

  **Verify all Phase 5**: Run with each edge case and confirm actionable error messages (no raw stack traces).

---

## Phase 6 - Documentation & Polish

- [x] **6.1 Write `SKILL.md` body sections**

  Replace the Phase 1.3 placeholder in `%USERPROFILE%\.opencode-lazy-vault\image-ocr\SKILL.md` with these sections:

  ```markdown
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

  | Engine | Quality | Speed | Setup | Best For |
  |--------|---------|-------|-------|----------|
  | Gemini 2.5 Flash (default) | Best | Fast | API key (free) | Handwriting, photos, forms, multi-language |
  | Tesseract | Good | Fast | Binary install | Clean printed text, offline use |

  Use `--engine auto` (default) to try Gemini first, fall back to Tesseract.

  ## Setup

  **Required (always)**:
  ```bash
  pip install httpx pytesseract Pillow
  ```

  **Gemini API key** (for Tier 1):
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
  ```

  **Verify**: `SKILL.md` contains all sections (Quick Start, Engines, Setup, Output Format, Gotchas, When to Use).

- [x] **6.2 Write `reference.md` (optional)**

  Create `%USERPROFILE%\.opencode-lazy-vault\image-ocr\reference.md` with full CLI reference, Tesseract install guide, Gemini key setup, language pack install, performance tips.

  **Verify**: File exists and is readable.

- [x] **6.3 Verify skill is discoverable**

  In an OpenCode session, call the MCP tool `skill_find` with query `"OCR"`. Confirm `image-ocr` appears in results.

  **Note**: `skill_find` is an MCP tool call, not a terminal command. Use it via the OpenCode tool interface.

  **Verify**: `skill_find("OCR")` returns a result containing `image-ocr`.

- [x] **6.4 Verify skill can be loaded**

  Call MCP tool `skill_use` with `skill_names: ["image-ocr"]`. Confirm it loads without errors.

  **Verify**: `skill_use(["image-ocr"])` returns the skill content.
---

## Phase 7 - Testing & Validation

> **PREREQUISITE**: Create a test image before running tests. Run this Python snippet:
> ```python
> from PIL import Image, ImageDraw
> img = Image.new("RGB", (400, 200), "white")
> draw = ImageDraw.Draw(img)
> draw.text((50, 50), "Hello OCR Test\nLine 2", fill="black")
> img.save(r"C:\Users\DaveWitkin\.opencode-lazy-vault\image-ocr\test_image.png")
> ```

- [x] **7.1 Test Gemini engine on test image**

  ```powershell
  python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\test_image.png" --engine gemini
  ```

  **Verify**: Output file contains "Hello OCR Test" and YAML frontmatter with `engine: gemini-direct`.

- [x] **7.2 Test Tesseract fallback**

  ```powershell
  $env:GEMINI_API_KEY = ""
  python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\test_image.png" --engine auto
  ```

  **Verify**: Output file contains extracted text and `engine: tesseract` in frontmatter.

- [x] **7.3 Test batch mode**

  Create a second test image, then:
  ```powershell
  python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\" --batch --output-dir "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\test-output"
  ```

  **Verify**: `test-output/manifest.json` exists and shows 2 processed images.

- [x] **7.4 Test `--dry-run` mode**

  ```powershell
  python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\test_image.png" --dry-run
  ```

  **Verify**: No `.md` file is written. Console shows "[DRY RUN] Would write: ...".

- [x] **7.5 Test `--preserve-layout` flag**

  ```powershell
  python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\test_image.png" --preserve-layout
  ```

  **Verify**: Output text preserves structure (if image has headings/lists).

- [x] **7.6 Test `--language` flag**

  ```powershell
  python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\test_image.png" --language French --engine tesseract
  ```

  **Verify**: Tesseract uses `fra` language code (check console output or error if pack not installed).

- [x] **7.7 Test edge cases**

  ```powershell
  # Unsupported format
  python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" "test.txt"
  # Expected: ERROR message about unsupported format

  # Empty directory
  New-Item -ItemType Directory -Path "$env:TEMP\empty-dir" -Force
  python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" "$env:TEMP\empty-dir" --batch
  # Expected: "No supported images found"

  # Nonexistent path
  python "$env:USERPROFILE\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py" "C:\does\not\exist.png"
  # Expected: ERROR message about path not found
  ```

  **Verify**: Each case prints an actionable error message (no raw stack traces).

- [x] **7.8 Verify output Markdown is clean**

  Open a generated `.md` file. Confirm:
  - YAML frontmatter is valid (parseable by a YAML parser)
  - Extracted text is readable and well-formatted
  - No raw HTML, no extra commentary from Gemini

- [x] **7.9 Verify skill discovery**

  Call MCP tool `skill_find` with query `"OCR"`. Confirm `image-ocr` is in results.

---

## Phase 8 - Completion Validation

- [x] **8.1 Verify all non-deferred plan tasks are checked `[x]`**

  Re-read `plan.md` and confirm every task in Phases 1-7 has `[x]`.

- [x] **8.2 Verify `metadata.json` is synchronized**

  Update `metadata.json`:
  - `status`: `"completed"`
  - `progress.percentage`: `100`
  - `progress.completedTasks`: equals `progress.totalTasks`
  - `completed`: today's date (ISO format)

- [x] **8.3 Verify `.conductor/tracks.md` row**

  Update the track row in `.conductor/tracks.md`:
  - Status: `completed`
  - Completed date: today

- [x] **8.4 Create execution log**

  Create `.conductor/tracks/20260614-image-ocr-skill/execution-log.md` with deviations, skipped items, and validation summary.

- [x] **8.5 Re-open all artifacts**

  Confirm these files exist and contain expected content:
  - `%USERPROFILE%\.opencode-lazy-vault\image-ocr\SKILL.md`
  - `%USERPROFILE%\.opencode-lazy-vault\image-ocr\scripts\ocr_extract.py`
  - `%USERPROFILE%\.opencode-lazy-vault\image-ocr\reference.md` (if created)

---

## Complexity vs Simplicity Tradeoff Analysis

### Simplicity Arguments (Won)
1. **Two tiers, not three**: PaddleOCR middle tier rejected as over-engineering
2. **Tesseract over PaddleOCR for fallback**: Simpler install, smaller footprint, sufficient for clean text
3. **No LLM post-processing**: Keep the pipeline direct (extract -> output)
4. **Single script**: One Python file, not a package
5. **Reuses visual-ocr patterns**: No new API integration patterns to learn

### Quality Arguments (Preserved)
1. **Gemini Flash as primary**: Best-in-class for heterogeneous images
2. **Layout preservation option**: `--preserve-layout` for structured documents
3. **Language support**: Multi-language via both Gemini and Tesseract
4. **Clean Markdown output**: YAML frontmatter + proper structure

## Dependencies

- **Python packages**: `httpx`, `pytesseract`, `Pillow`
- **System binary**: Tesseract OCR (fallback tier only)
- **API key**: Gemini API key (primary tier only, free tier sufficient)
- **Related skills**: `visual-ocr` (Gemini API patterns), `doc-to-markdown` (batch/output patterns)

## Risks

1. **Gemini free tier rate limits**: Mitigated by 0.5s delay and Tesseract fallback
2. **Tesseract not installed**: Graceful degradation -- Gemini-only mode still works
3. **Large images**: 20MB limit enforced, user warned
4. **Obscure languages**: Tesseract needs language packs; Gemini handles most natively

## Task Safety Rules

### Collision Guard
- Before creating `%USERPROFILE%\.opencode-lazy-vault\image-ocr\`, verify it does NOT already exist
- If exists: stop and report. Do NOT overwrite without user confirmation

### Edit Safety
- SKILL.md is a new file (no collision risk)
- `ocr_extract.py` is a new script (no collision risk)
- `reference.md` is optional and new

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.