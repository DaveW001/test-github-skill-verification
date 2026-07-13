#!/usr/bin/env python3
"""
Visual OCR Extraction Script
Extracts structured markdown from visual slide images using vision AI.

Primary: Gemini 2.5 Flash (direct API, free tier)
Fallback: gpt-5.4-mini via OpenRouter

Usage:
    extract_visual.py <image_path> [--output-dir DIR] [--batch]
                      [--prompt-type TYPE] [--no-fallback] [--dry-run]

Examples:
    extract_visual.py slide.png --output-dir ./output
    extract_visual.py ./slides/ --batch --output-dir ./output
    extract_visual.py org-chart.png --prompt-type org-chart
"""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    httpx = None

try:
    from openai import OpenAI
except ImportError:
    print("[ERROR] 'openai' package required. Run: pip install openai")
    sys.exit(1)


# --- Configuration ---

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_KEY_FILE = Path.home() / ".local" / "gemini-proxy" / "api_keys.txt"

# Fallback: OpenRouter for gpt-5.4-mini
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "openai/gpt-5.4-mini"

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_IMAGE_SIZE_MB = 20


def _resolve_gemini_key() -> str:
    """Resolve Gemini API key from env or proxy key file."""
    if GEMINI_API_KEY:
        return GEMINI_API_KEY
    # Try key_names.json first (has named keys, try each)
    key_names_file = Path.home() / ".local" / "gemini-proxy" / "key_names.json"
    if key_names_file.exists():
        try:
            keys = json.loads(key_names_file.read_text())
            # Return first key from the dict (ordered in Python 3.7+)
            for key in keys:
                return key
        except Exception:
            pass
    # Fallback to api_keys.txt
    if GEMINI_KEY_FILE.exists():
        for line in GEMINI_KEY_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    return ""

PROMPT_TEMPLATES = {
    "auto": (
        "You are a visual document analyst. Analyze this slide image and extract ALL structured content "
        "into well-organized markdown.\n\n"
        "Identify and extract:\n"
        "1. Any organizational charts → preserve hierarchy with indented lists\n"
        "2. Any timelines or roadmaps → chronological milestone lists\n"
        "3. Any tables or matrices → markdown tables with headers\n"
        "4. Any relationship diagrams → describe connections between entities\n"
        "5. Any process flows → numbered step sequences\n"
        "6. Any text content → capture with proper heading hierarchy\n\n"
        "Output rules:\n"
        "- Use markdown headers (##, ###) for major sections\n"
        "- Use markdown tables for any tabular data\n"
        "- Use indented bullet lists for hierarchies\n"
        "- Preserve all names, dates, acronyms, and technical terms exactly\n"
        "- Note the visual type detected at the top as: <!-- visual-type: [type] -->\n"
        "- If RAG colors (Red/Amber/Green) are present, include them as status indicators [RED], [AMBER], [GREEN]\n"
        "- Include any footnotes, legends, or source attribution\n"
        "- Output ONLY the extracted markdown, no commentary"
    ),
    "org-chart": (
        "You are extracting an organizational chart from a slide image.\n\n"
        "Output format:\n"
        "- Use nested bullet lists to show hierarchy (reporting relationships)\n"
        "- Each person entry: **Name** — Role/Title\n"
        "- Each unit entry: ### Unit Name\n"
        "- Preserve all box connections and grouping lines\n"
        "- Include any annotations (acting, interim, vacant)\n"
        "- If dotted-line vs solid-line relationships exist, note them\n"
        "- Output ONLY the extracted markdown, no commentary"
    ),
    "timeline": (
        "You are extracting a timeline or roadmap from a slide image.\n\n"
        "Output format:\n"
        "- Chronological list of milestones with dates\n"
        "- Use bold for dates, plain text for descriptions\n"
        "- Include status indicators: ✅ complete, 🔄 in-progress, 📋 planned\n"
        "- Preserve any phase/grouping structure\n"
        "- Include dependencies between milestones if shown\n"
        "- Output ONLY the extracted markdown, no commentary"
    ),
    "table": (
        "You are extracting a table or matrix from a slide image.\n\n"
        "Output format:\n"
        "- Use markdown table format with headers\n"
        "- Preserve all column and row structure\n"
        "- Include merged cells noted in parentheses\n"
        "- Preserve status indicators as [RED], [AMBER], [GREEN]\n"
        "- Include totals/summaries if present\n"
        "- Output ONLY the extracted markdown, no commentary"
    ),
    "diagram": (
        "You are extracting a relationship or process diagram from a slide image.\n\n"
        "Output format:\n"
        "1. List all entities (boxes/nodes) with their labels\n"
        "2. List all connections with direction and labels\n"
        "3. Describe any grouping/clustering\n\n"
        "## Entities\n- **Entity A**: [description/role]\n\n"
        "## Relationships\n- Entity A → Entity B: [label]\n\n"
        "## Groups\n- Group 1: Entity A, Entity B\n\n"
        "- Output ONLY the extracted markdown, no commentary"
    ),
}


# --- Image Processing ---

def encode_image(image_path: Path) -> tuple[str, str]:
    """Read and base64-encode an image file. Returns (base64_str, media_type)."""
    suffix = image_path.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_types.get(suffix, "image/png")

    size_mb = image_path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        print(f"  [WARN] {image_path.name} is {size_mb:.1f}MB (exceeds {MAX_IMAGE_SIZE_MB}MB limit), skipping")
        return "", media_type

    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8"), media_type


def collect_images(path: Path) -> list[Path]:
    """Collect image files from a path (file or directory)."""
    if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
        return [path]
    elif path.is_dir():
        images = sorted(
            p for p in path.iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if not images:
            print(f"[WARN] No image files found in {path}")
        return images
    else:
        print(f"[ERROR] {path} is not a valid image file or directory")
        return []


# --- Extraction Engines ---

def extract_gemini(image_path: Path, prompt_type: str, api_key: str = None) -> dict:
    """Extract using Gemini Flash via direct Google API (free tier)."""
    if httpx is None:
        return {"success": False, "error": "httpx not installed (pip install httpx)"}

    key = api_key or _resolve_gemini_key()
    if not key:
        return {"success": False, "error": "No Gemini API key (set GEMINI_API_KEY or populate ~/.local/gemini-proxy/api_keys.txt)"}

    b64, media_type = encode_image(image_path)
    if not b64:
        return {"success": False, "error": "Image too large or unreadable"}

    prompt = PROMPT_TEMPLATES.get(prompt_type, PROMPT_TEMPLATES["auto"])

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": media_type,
                            "data": b64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 8192,
        },
    }

    url = GEMINI_API_URL.format(GEMINI_MODEL) + f"?key={key}"

    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(url, json=payload)

        if resp.status_code != 200:
            return {
                "success": False,
                "error": f"Gemini API returned {resp.status_code}: {resp.text[:300]}",
            }

        data = resp.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        usage_meta = data.get("usageMetadata", {})

        return {
            "success": True,
            "content": content,
            "model": GEMINI_MODEL,
            "engine": "gemini-direct",
            "tokens_in": usage_meta.get("promptTokenCount", 0),
            "tokens_out": usage_meta.get("candidatesTokenCount", 0),
        }
    except Exception as e:
        return {"success": False, "error": f"Gemini API error: {e}"}


def extract_openrouter(image_path: Path, prompt_type: str) -> dict:
    """Extract using gpt-5.4-mini via OpenRouter (fallback)."""
    if not OPENROUTER_API_KEY:
        return {"success": False, "error": "No OPENROUTER_API_KEY set"}

    b64, media_type = encode_image(image_path)
    if not b64:
        return {"success": False, "error": "Image too large or unreadable"}

    prompt = PROMPT_TEMPLATES.get(prompt_type, PROMPT_TEMPLATES["auto"])

    client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)

    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{b64}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
        max_tokens=4096,
    )

    content = response.choices[0].message.content
    usage = response.usage

    return {
        "success": True,
        "content": content,
        "model": OPENROUTER_MODEL,
        "engine": "openrouter",
        "tokens_in": usage.prompt_tokens if usage else 0,
        "tokens_out": usage.completion_tokens if usage else 0,
    }


# --- Output Formatting ---

def format_output(image_path: Path, result: dict) -> str:
    """Format extraction result as a complete markdown file."""
    content = result.get("content", "")
    model = result.get("model", "unknown")
    engine = result.get("engine", "unknown")

    frontmatter = f"""---
source: "{image_path.name}"
model: {model}
engine: {engine}
extracted: {time.strftime('%Y-%m-%dT%H:%M:%S')}
prompt_type: {result.get('prompt_type', 'auto')}
---

"""

    return frontmatter + content


def write_output(image_path: Path, output_dir: Path, result: dict) -> Path:
    """Write extraction result to markdown file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = image_path.stem
    # Clean up date prefix if present (e.g., "2026-05-14-Slide" → "Slide")
    output_file = output_dir / f"{stem}-visual-extraction.md"
    output_file.write_text(format_output(image_path, result), encoding="utf-8")
    return output_file


# --- Main Pipeline ---

def process_image(image_path: Path, args) -> dict:
    """Process a single image through the extraction pipeline."""
    print(f"\nProcessing: {image_path.name}")
    prompt_type = args.prompt_type

    # Primary: Gemini Flash (direct API, free tier)
    result = extract_gemini(image_path, prompt_type)
    result["prompt_type"] = prompt_type

    if not result["success"]:
        print(f"  [WARN] Gemini failed: {result.get('error', 'unknown')[:100]}")
        if not args.no_fallback and OPENROUTER_API_KEY:
            print("  Falling back to OpenRouter gpt-5.4-mini...")
            result = extract_openrouter(image_path, prompt_type)
            result["prompt_type"] = prompt_type

            if not result["success"]:
                print(f"  [ERROR] OpenRouter also failed: {result.get('error', 'unknown')[:100]}")
                return result
        elif not args.no_fallback:
            print("  [WARN] No OPENROUTER_API_KEY for fallback")
            return result
    else:
        tok_in = result.get("tokens_in", 0)
        tok_out = result.get("tokens_out", 0)
        print(f"  OK - {result.get('engine','?')} success ({tok_in} in, {tok_out} out tokens)")

    # Write output
    if not args.dry_run:
        output_path = write_output(image_path, Path(args.output_dir), result)
        print(f"  -> {output_path}")
    else:
        print(f"  [DRY RUN] Would write to {args.output_dir}/{image_path.stem}-visual-extraction.md")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured content from visual slide images using vision AI."
    )
    parser.add_argument("image_path", help="Image file or directory of images")
    parser.add_argument("--output-dir", default="./visual-ocr-output",
                        help="Output directory for extracted markdown (default: ./visual-ocr-output)")
    parser.add_argument("--batch", action="store_true",
                        help="Process all images in directory")
    parser.add_argument("--prompt-type", default="auto",
                        choices=list(PROMPT_TEMPLATES.keys()),
                        help="Type of visual content to optimize extraction for")
    parser.add_argument("--no-fallback", action="store_true",
                        help="Skip OpenRouter fallback if Gemini fails")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run without writing output files")

    args = parser.parse_args()
    path = Path(args.image_path)

    if not path.exists():
        print(f"[ERROR] Path not found: {path}")
        sys.exit(1)

    images = collect_images(path)
    if not images:
        sys.exit(1)

    gemini_key = _resolve_gemini_key()
    print(f"Found {len(images)} image(s) to process")
    print(f"Primary: {GEMINI_MODEL} (direct API)" + (" [key found]" if gemini_key else " [NO KEY]"))
    print(f"Prompt type: {args.prompt_type}")
    if not args.no_fallback and OPENROUTER_API_KEY:
        print(f"Fallback: {OPENROUTER_MODEL} via OpenRouter")

    results = {"success": 0, "failed": 0}
    start_time = time.time()

    for img in images:
        result = process_image(img, args)
        if result["success"]:
            results["success"] += 1
        else:
            results["failed"] += 1
        # Rate limiting: small delay between API calls
        if len(images) > 1:
            time.sleep(0.5)

    elapsed = time.time() - start_time
    print(f"\n{'='*50}")
    print(f"Complete: {results['success']} succeeded, {results['failed']} failed")
    print(f"Time: {elapsed:.1f}s | Output: {args.output_dir}")


if __name__ == "__main__":
    main()
