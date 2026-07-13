# Output Reference

Reference for all supported output contracts:
- Legacy Markdown report
- Legacy JSON schema
- Google-style `DESIGN.md` draft output

---

## Spec Version & Compatibility

- External spec observed: `https://raw.githubusercontent.com/google-labs-code/design.md/main/docs/spec.md`
- Observed spec version: `alpha` (from spec header/content at planning time)
- Compatibility stance: **best-effort draft alignment**, not a strict conformance guarantee.

When spec changes, update this section first, then examples and workflows.

---

## Canonical Internal Model (Source-Agnostic)

Normalize extraction results before rendering:

```json
{
  "metadata": {
    "source": "string",
    "method": "url|file|hybrid",
    "extracted": "ISO8601",
    "confidence": "high|medium|low"
  },
  "tokens": {
    "colors": {},
    "typography": {},
    "rounded": {},
    "spacing": {},
    "components": {}
  },
  "layoutSignals": {},
  "elevationSignals": {},
  "notes": [],
  "provenance": {
    "<path.to.token>": "exact|perceived|inferred"
  }
}
```

Provenance meanings:
- `exact`: directly observed from CSS/style declarations.
- `perceived`: vision-estimated value.
- `inferred`: reasoned from incomplete evidence.

---

## Gap-to-Mapping Table

| Existing Extraction Shape | DESIGN.md Target | Mapping Rule |
| --- | --- | --- |
| `borders.radii` | `rounded` | Convert to named rounded scale (`sm/md/lg/full`) where possible |
| `borders.widths/colors` | no dedicated YAML group | Keep in prose (Shapes / Components) when relevant |
| `shadows` | `## Elevation & Depth` | Render as prose guidance rather than YAML tokens |
| `layout.grid/breakpoints` | `## Layout` + optional `spacing` | Render layout strategy in prose; keep spacing values in `spacing` |
| typography core fields | `typography` object | Preserve known fields; emit `letterSpacing`, `fontFeature`, `fontVariation` when observed in source |
| freeform components | `components` map | Prefer token references (`{colors.primary}` etc.) |

---

## DESIGN.md Rendering Contract

### 1) Front Matter

When enough structured tokens exist, emit YAML front matter:

```yaml
---
version: alpha
name: <Design System Name>
description: <Optional short description>
colors:
  primary: "#1A1C1E"
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  label-caps:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.1em
rounded:
  sm: 4px
spacing:
  md: 16px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: 12px
---
```

**Typography object properties** (7 supported):

| Property | Required | Format | Example |
|----------|----------|--------|---------|
| `fontFamily` | Yes | string | `Inter` |
| `fontSize` | Yes | Dimension | `16px` |
| `fontWeight` | Yes | number | `400`, `700` |
| `lineHeight` | Yes | Dimension or unitless number | `1.6`, `24px` |
| `letterSpacing` | No | Dimension | `-0.02em`, `0.1em` |
| `fontFeature` | No | string | `"cv02"` |
| `fontVariation` | No | string | `"wght 400"` |

Emit all observed properties. Omit unobserved optional fields rather than inventing values.

**`version` field guidance:**
- `version` is optional. When present, use `"alpha"` to match the current Google draft spec version.
- If the Google spec introduces a new version identifier, update `reference.md` first, then examples.
- The field does not affect token semantics; it signals which spec revision the output targets.

Policy:
- Emit partial front matter if useful tokens are available.
- Omit unsupported groups entirely.
- Never fabricate values for completeness.

### 2) Body Section Order

Use `##` headings. Include only relevant sections, but preserve order of included sections:

1. Overview (alternate: "Brand & Style")
2. Colors
3. Typography
4. Layout (alternate: "Layout & Spacing")
5. Elevation & Depth (alternate: "Elevation")
6. Shapes
7. Components
8. Do's and Don'ts

Alternate names are recognized by consumers as equivalent. Generation should use primary names only; recognition should accept alternates.

### 3) Prose Rules

- Be conservative when evidence is weak.
- Prefer "likely", "appears", "inferred" language for non-exact claims.
- If evidence is insufficient for a section, omit section or include explicit caveat.
- Duplicate section headings are **invalid** and must not be generated (per Google spec: "Error; reject the file").

---

## Token Reference Syntax

Use Google-style references in component values:

```yaml
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
    typography: "{typography.body-md}"
```

**Primitive vs. composite constraint:**
- **Outside `components`:** References must point to a primitive value (e.g., `colors.primary`), not a group (e.g., `colors`).
- **Inside `components`:** References to composite values are permitted (e.g., `{typography.body-md}` referencing a full typography object). This is the only context where composite references are valid.

Guidance:
- Reference defined token paths.
- Use literal values only when no stable token exists.

---

## Legacy Markdown Contract (Backward Compatible)

Keep current shape intact:
- Metadata block (`Extraction Method`, `Source`, `Extracted`, `Confidence`)
- Sections/tables for colors, typography, spacing, borders, shadows, components, layout
- Perceived/inferred caveats for non-exact values

---

## Legacy JSON Contract (Backward Compatible)

Keep legacy schema structure unchanged for existing consumers.

**Complete baseline schema:**

```json
{
  "metadata": {
    "source": "string",
    "method": "url | file | hybrid",
    "extracted": "ISO8601 timestamp",
    "confidence": "high | medium | low",
    "note": "string (optional)"
  },
  "colors": {
    "primary": [{ "name": "string", "value": "hex", "usage": "string" }],
    "secondary": [{ "name": "string", "value": "hex", "usage": "string" }],
    "semantic": { "success": "hex", "warning": "hex", "error": "hex", "info": "hex" },
    "neutral": { "background": "hex", "surface": "hex", "text": "hex", "muted": "hex", "border": "hex" }
  },
  "typography": {
    "families": [{ "category": "string", "font": "string", "fallbacks": "string" }],
    "scale": [{ "name": "string", "size": "string", "weight": "number", "lineHeight": "number", "usage": "string" }]
  },
  "spacing": [{ "token": "string", "value": "string", "usage": "string" }],
  "borders": {
    "radii": [{ "token": "string", "value": "string", "usage": "string" }],
    "widths": [{ "token": "string", "value": "string" }],
    "colors": [{ "token": "string", "value": "hex" }]
  },
  "shadows": [{ "token": "string", "value": "string", "usage": "string" }],
  "components": [
    {
      "name": "string",
      "properties": { "height": "string", "padding": "string", "borderRadius": "string", "fontWeight": "number" },
      "states": ["string"],
      "perceived": true
    }
  ],
  "layout": {
    "grid": { "columns": "number", "gutter": "string", "containerMax": "string" },
    "breakpoints": [{ "name": "string", "value": "string" }]
  }
}
```

All top-level groups are optional. Groups not extracted from a source should be omitted entirely rather than included with empty values. This schema is the authoritative backward-compatibility baseline.

Provenance notes may be represented in existing optional item-level annotations where already used in examples (e.g., `perceived: true`).

---

## Standard Component Properties

The Google spec defines 8 standard component properties:

| Property | Type | Example |
|----------|------|---------|
| `backgroundColor` | Color or token reference | `"{colors.primary}"` |
| `textColor` | Color or token reference | `"{colors.on-primary}"` |
| `typography` | Composite token reference or inline object | `"{typography.body-md}"` |
| `rounded` | Dimension or token reference | `"{rounded.md}"` |
| `padding` | Dimension | `12px` |
| `size` | Dimension | `40px` |
| `height` | Dimension | `48px` |
| `width` | Dimension | `120px` |

Additional domain-specific properties may be defined but should be documented when used. Component variants (e.g., `button-primary-hover`, `button-primary-active`) define states under related keys.

---

## Recommended Token Names (Non-Normative)

The Google spec provides naming conventions for cross-tool consistency. Prefer these names when extracting:

**Colors:** `primary`, `secondary`, `tertiary`, `neutral`, `surface`, `on-surface`, `error`

**Typography:** `headline-display`, `headline-lg`, `headline-md`, `body-lg`, `body-md`, `body-sm`, `label-lg`, `label-md`, `label-sm`

**Rounded:** `none`, `sm`, `md`, `lg`, `xl`, `full`

When source uses different naming, map to recommended names where the semantic match is clear. Preserve source names when no clear mapping exists.

---

## Confidence & Provenance Conventions

Document-level confidence:
- `high` - mostly exact values
- `medium` - mixed exact + inferred/perceived
- `low` - mostly perceived/inferred

Token-level notation:
- Markdown: annotate value labels (`(perceived)`, `(inferred)`)
- JSON: optional flags on token entries
- DESIGN.md: caveated prose and selective token inclusion; for YAML front matter, use inline comments for non-exact values:
  ```yaml
  colors:
    primary: "#3B82F6"  # perceived
    neutral: "#F8FAFC"  # perceived
  typography:
    body-md:
      fontFamily: Sans-serif  # inferred
  ```

---

## Minimal Compliance Checklist (for DESIGN.md outputs)

- Front matter delimiters are valid (`---` ... `---`) when front matter is present.
- Token groups use supported names (`colors`, `typography`, `rounded`, `spacing`, `components`).
- Component token references use `{path.to.token}` syntax.
- Included sections follow required order.
- No duplicate `##` section headings (invalid per spec — reject).
