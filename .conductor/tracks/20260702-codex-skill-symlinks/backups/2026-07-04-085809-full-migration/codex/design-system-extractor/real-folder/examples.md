# Example Outputs

Sample outputs for each supported output contract.

---

## Example 1: URL Extraction (`DESIGN.md`, high confidence)

```markdown
---
version: alpha
name: Tailwind Reference
description: Utility-first web UI with high-contrast neutrals and cyan accents
colors:
  primary: "#06B6D4"
  secondary: "#0EA5E9"
  neutral: "#0F172A"
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.75
  heading-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: -0.02em
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.08em
rounded:
  md: 8px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: 12px
    height: 40px
---

## Overview

The interface style is clean, utility-driven, and optimized for readability and implementation consistency.

## Colors

Primary cyan drives interactive emphasis; dark neutrals anchor text and structural contrast.

## Typography

A modern sans-serif system supports both dense utility UIs and long-form documentation.

## Layout

Spacing follows a compact, scale-based rhythm that supports rapid composition.

## Elevation & Depth

Depth is subtle and primarily communicated through restrained shadows and contrast.

## Shapes

Rounded corners are moderate and consistent across primary interactive elements.

## Components

Primary buttons use token references to keep color and shape decisions centralized.

## Do's and Don'ts

- Do keep spacing on token scale increments.
- Don't introduce ad-hoc accent colors for core actions.
```

---

## Example 2: Hybrid Extraction (`DESIGN.md`, mixed confidence)

```markdown
---
version: alpha
name: Dashboard Mockup (Hybrid)
colors:
  primary: "#3B82F6"  # perceived
  neutral: "#F8FAFC"  # perceived
  on-surface: "#1E293B"  # perceived
typography:
  body-md:
    fontFamily: Sans-serif  # inferred
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  label-caps:
    fontFamily: Sans-serif  # inferred
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.05em  # inferred
rounded:
  md: 8px
spacing:
  md: 16px
  gutter: 24px  # perceived
components:
  card-primary:
    backgroundColor: "{colors.neutral}"
    rounded: "{rounded.md}"
    padding: 16px
  card-primary-elevated:
    backgroundColor: "#FFFFFF"  # perceived
    rounded: "{rounded.md}"
    padding: 16px
    height: auto
---

## Overview

The design appears to emphasize clarity and card-based organization; typography and spacing values are partially inferred from screenshot evidence.

## Colors

Primary blue appears to drive interactive emphasis. Neutral backgrounds are light and low-noise.

## Typography

Typography likely uses a modern sans-serif family. Exact family is not confirmed. Labels appear to use uppercase with letter-spacing.

## Layout

The layout appears grid-like with moderate gutters; exact breakpoint behavior is not confirmed.

## Elevation & Depth

Depth appears to use tonal layering — off-white background with white card surfaces — rather than heavy shadows. Card shadows, where present, are subtle and low-spread.

## Shapes

Cards and buttons appear moderately rounded (inferred from visual analysis).

## Components

Cards use token-referenced rounding and neutral background fills. Elevated card variant adds a white surface with explicit height. Component coverage is partial due to limited exact source styles.

## Do's and Don'ts

- Do maintain the neutral-off-white tonal layering for depth.
- Don't introduce strong shadows without matching the source's subtle elevation approach.
```

---

## Example 3: Backward Compatibility (Markdown)

```markdown
# Design System: Example Site

**Extraction Method:** URL
**Source:** https://example.com
**Extracted:** 2026-04-25T12:00:00Z
**Confidence:** High

## Colors

| Name | Value | Usage |
|---|---|---|
| Primary | #0086CA | Buttons, links |

## Typography

| Name | Size | Weight | Line Height | Usage |
|---|---|---|---|---|
| Body | 16px | 400 | 1.6 | Paragraph text |
```

---

## Example 4: Backward Compatibility (JSON)

```json
{
  "metadata": {
    "source": "https://example.com",
    "method": "url",
    "extracted": "2026-04-25T12:00:00Z",
    "confidence": "high"
  },
  "colors": {
    "primary": [
      { "name": "Primary", "value": "#0086CA", "usage": "Buttons" }
    ]
  },
  "typography": {
    "scale": [
      { "name": "body", "size": "16px", "weight": 400, "lineHeight": 1.6, "usage": "Paragraphs" }
    ]
  }
}
```
