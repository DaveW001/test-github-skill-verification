---
name: image-generator
description: Generates on-brand visual prompts for hero images and in-article diagrams using Packaged Agile's visual standards. Supports LEGO 3D Isometric and Hand-Drawn Whiteboard Sketch (Digital Chalkboard) styles.
---

# Image Generator

Creates prompts for AI image generation (Gemini, DALL-E, Midjourney) following documented visual standards. Supports two distinct style modes.

## Source Of Truth

- If you are working in C:/development/marketing, use: C:/development/marketing/docs/visual-guidelines-index.md
- Website channel standards: C:/development/2025-pa-website/docs/hero-image-standard.md and C:/development/2025-pa-website/docs/in-article-diagram-prompts.md
- Prefer repo-local skills/agents when available; treat this global skill as a fallback.


## When to Use

- After `image-manifest-builder` has identified needed images.
- When creating hero images for new articles or social media.
- When generating in-article diagrams (before/after, grids, infographics).

## Style Modes

### Mode 1: Hero Image (3D Isometric LEGO)

**Visual Characteristics:**
- 3D isometric LEGO style.
- Professional toy photography look with correct brick proportions.
- Clean white background.
- Brand colors: Blue (#0086CA) and Gold (#FDBA31).
- Government themes: pillars, shields, networks, dashboards.

**Technical Requirements:**
- Format: WebP or JPEG.
- Aspect ratio: 16:9 (Default) or 1:1.
- Tool: Use `generate_image(prompt="...", file_name="hero")`.

**Base Prompt Template:**
```
3D isometric LEGO style illustration on a clean white background. 
[SCENE DESCRIPTION]
Professional toy photography aesthetic with correct LEGO brick proportions.
Brand accent colors: government blue (#0086CA) and gold (#FDBA31).
No clutter, minimal distractions. Sharp shadows, studio lighting.
16:9 aspect ratio.
```

---

### Mode 2: In-Article Diagram (Hand-Drawn Whiteboard Sketch / Digital Chalkboard)

**Visual Characteristics:**
- Hand-drawn, slightly imperfect lines (whiteboard marker aesthetic).
- Dark navy blue gradient background.
- Chalk-like or marker texture.
- White and light blue sketch lines.
- Simple stick figures or cartoon icons.
- Ribbon/banner labels for section headers.
- Red X marks for anti-patterns, green checkmarks for solutions.

**Technical Requirements:**
- Format: WebP or JPEG.
- Aspect ratio: 16:9 (Default).
- Tool: Use `generate_image(prompt="...", file_name="diagram")`.

**Base Prompt Template:**
```
Hand-drawn whiteboard sketch style infographic on a dark navy blue gradient background.
Title at top in slightly imperfect handwritten font: "[TITLE]" with subtitle "[SUBTITLE]".

[CONTENT LAYOUT]

Style: Hand-drawn whiteboard sketch aesthetic. Imperfect lines, slightly uneven text 
like marker on whiteboard. Warm chalk-like or marker texture. White and light blue 
sketch lines on dark background. Think "executive explaining on a whiteboard" look. 
Organic, approachable, not corporate-polished. Simple stick figures or cartoon people.
16:9 aspect ratio (1600x900).
```

---

## Diagram Layout Templates

### Before/After Comparison

```
Split into two side-by-side panels:

LEFT SIDE (labeled "[LEFT_LABEL]" as a banner/ribbon):
- [DESCRIBE LEFT SIDE - the problem/anti-pattern]
- Red X mark
- Handwritten note below: "[LEFT_CAPTION]"

RIGHT SIDE (labeled "[RIGHT_LABEL]" as a banner/ribbon):
- [DESCRIBE RIGHT SIDE - the solution/best practice]
- Green checkmark
- Handwritten note below: "[RIGHT_CAPTION]"

IMPORTANT: Do NOT include any text that says "LEFT PANEL" or "RIGHT PANEL" anywhere in the image.
```

### Multi-Item Grid

```
Grid layout with [N] items arranged in [ROWS x COLS] format:

Item 1: [ICON] "[LABEL]" - [BRIEF DESCRIPTION]
Item 2: [ICON] "[LABEL]" - [BRIEF DESCRIPTION]
...

Each item in a rounded card with subtle shadow.
Consistent icon style throughout.
Clear visual hierarchy with labels prominent.
```

---

## Instructions

1. **Determine Mode**: Hero (LEGO) for covers, Diagram (Whiteboard) for content.
2. **Select Layout Template**: For diagrams (Comparison, Grid, Workflow).
3. **Generate Prompt**: Combine base template, layout, and content.
4. **Tool Execution**: Use `/generate-image` command or `generate_image` tool.

### Output Format for Agent

```markdown
## [Image Name]

**Type:** Hero | Diagram
**Style:** LEGO 3D | Hand-Drawn Whiteboard Sketch
**Filename:** [suggested-filename].webp

### Prompt
[Complete prompt ready for generation]

### Alt Text
[SEO-optimized alt text]
```

## Related Skills

- **image-manifest-builder** — Plan images for an entire article or document. Use this first to generate an `image-manifest.json` with prioritized concepts, then use `image-generator` for each one.
- **image-to-html-reconstruction** — For converting slide/UI images into high-fidelity, pixel-locked HTML mockups and PPTX, plus full HTML page mockups and interactive demos.
