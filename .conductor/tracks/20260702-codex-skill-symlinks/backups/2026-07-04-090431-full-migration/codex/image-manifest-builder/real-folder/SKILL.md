---
name: image-manifest-builder
description: Analyzes content to identify graphics needs and generates an image-manifest.json with prioritized prompt drafts.
---

# Image Manifest Builder

Plans and tracks image needs for articles or reports, creating a structured manifest that feeds into the image-generator skill.

## Source Of Truth

- If you are working in C:/development/marketing, follow: C:/development/marketing/docs/visual-guidelines-index.md
- Channel standards live in C:/development/2025-pa-website/docs/hero-image-standard.md and C:/development/2025-pa-website/docs/in-article-diagram-prompts.md
- Prefer repo-local skills/agents when available; treat this global skill as a fallback.


## When to Use

- After content analysis to plan all graphics for a document.
- When auditing existing content for visual gaps.
- Before batch image generation sessions.

## Instructions

### 1. Identify Image Needs

Scan content for:
- **Article introduction**: Needs Hero image (3D LEGO style).
- **Comparison content**: Needs Before/After Diagram (hand-drawn whiteboard sketch / digital chalkboard).
- **Lists/Grids (3-8 items)**: Needs Multi-item grid diagram.
- **Process/Protocol**: Needs Flow diagram.
- **Key Statistics**: Needs Data visualization.

### 2. Determine Style & Type

| Content Type | Style | Type |
|--------------|-------|------|
| Intro/Cover | LEGO 3D Isometric | Hero |
| Comparison | Digital Chalkboard (whiteboard-sketch) | Diagram |
| List/Features | Digital Chalkboard (whiteboard-sketch) | Grid |
| Workflow | Digital Chalkboard (whiteboard-sketch) | Process |

### 3. Draft Manifest

Create `image-manifest.json` (or similar tracking structure):

```json
{
  "images_needed": [
    {
      "id": "img-001",
      "type": "hero",
      "style": "lego-3d-isometric",
      "priority": "high",
      "concept": "Core metaphor of the content",
      "suggested_filename": "hero.webp"
    },
    {
      "id": "img-002",
      "type": "diagram",
      "style": "whiteboard-sketch",
      "priority": "medium",
      "concept": "Siloed vs Unified teams",
      "suggested_filename": "silo-vs-unified.webp"
    }
  ]
}
```

### 4. Provide Summary

Output a summary table for the user showing planned images and their priority.

## Integration
- Output is used by the `image-generator` skill or the `/generate-image` command.

## Related Skills

- **image-generator** — Generates individual visual prompts from the manifest entries. Use after `image-manifest-builder` has planned the images.
- **image-to-html-reconstruction** — For converting slide/UI images into high-fidelity, pixel-locked HTML mockups and PPTX, plus full HTML page mockups and interactive demos.
