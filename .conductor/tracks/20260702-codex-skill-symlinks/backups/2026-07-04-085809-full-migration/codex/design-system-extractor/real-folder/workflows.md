# Extraction & Rendering Workflows

Step-by-step workflows for URL, file, and hybrid extraction with multi-format rendering support.

---

## Universal Pipeline (All Modes)

1. **Extract signals** from source(s).
2. **Normalize** into canonical internal model.
3. **Assign provenance** (`exact|perceived|inferred`) per token/signal.
4. **Render** requested format(s): Markdown, JSON, and/or `DESIGN.md`.
5. **Apply safety checks** (no fabricated certainty, section ordering, duplicate heading prevention).

---

## URL Extraction Workflow

### Step 1: Validate URL

- Ensure URL is reachable and parseable.

### Step 2: Fetch and parse style sources

- Retrieve HTML and available style sources.
- Extract:
  - CSS custom properties
  - inline style values
  - common class/style patterns

### Step 3: Build canonical token set

- Prioritize exact style values.
- Map values into canonical groups: colors, typography, rounded, spacing, components.
- Record layout/elevation as signals for prose rendering.

### Step 4: Render output contract(s)

- **Markdown/JSON:** preserve legacy output structure.
- **DESIGN.md:** emit front matter + ordered prose sections.

### Step 5: Validate confidence and claims

- URL-derived values are usually `exact` unless inferred.
- Any inferred design-intent prose must be clearly caveated.

---

## File Extraction Workflow

### Step 1: Validate file

- Confirm image path and supported format (`.png`, `.jpg`, `.jpeg`, `.svg`, `.webp`).

### Step 2: Vision analysis

- Estimate palette, typography cues, spacing patterns, component shapes.

### Step 3: Normalize with provenance

- Mark most values `perceived`.
- Use `inferred` only when extrapolating patterns from partial visual evidence.

### Step 4: Render output contract(s)

- **Markdown/JSON:** include explicit approximation notes.
- **DESIGN.md:**
  - Emit partial front matter only where token confidence is useful.
  - Use conservative prose.
  - Omit sections lacking evidence.

### Step 5: Confidence guardrail

- Never present perceived values as exact.

---

## Hybrid Validation Workflow

### Step 1: Process URL and file independently

- Run URL extraction and file extraction in sequence.

### Step 2: Reconcile

- Prefer URL exact values when conflicts exist.
- Keep file-derived values as validation/context.
- Mark disagreements explicitly.

### Step 3: Stable token naming

- Assign stable token names (`colors.primary`, `rounded.md`, etc.) from reconciled set.
- Ensure component rendering can reference tokens using `{path.to.token}` syntax.

### Step 4: Render output contract(s)

- Markdown/JSON remain backward compatible.
- `DESIGN.md` reflects reconciled token model and caveated rationale prose.

---

## DESIGN.md Generation Workflow

### Step A: Front matter decision

- If at least one meaningful token group is available, emit front matter.
- Omit missing groups; do not add placeholders.

### Step B: Section rendering

Render included sections in this order only:
1. Overview
2. Colors
3. Typography
4. Layout
5. Elevation & Depth
6. Shapes
7. Components
8. Do's and Don'ts

### Step C: Prose safety

- Exact evidence → direct language
- Perceived/inferred evidence → caveated language
- Duplicate section headings are **invalid** and must not be generated (per Google spec: "Error; reject the file").
- Insufficient evidence → omit section or add explicit limitation note.

### Step D: Component token references

- Prefer token references in component definitions:
  - `backgroundColor: "{colors.primary}"`
  - `rounded: "{rounded.md}"`

---

## Verification Checklist

> **Note:** This is a runtime template for agents executing the skill. For planning verification status, see the Conductor track `checklists.md`.

### DESIGN.md Compliance Checks

- [ ] Valid YAML delimiters (`---` start/end) when front matter present.
- [ ] Supported token group names only.
- [ ] Component references follow `{path.to.token}` syntax (primitives only outside `components`; composites allowed inside `components`).
- [ ] Included `##` sections are in required order.
- [ ] No duplicate section headings (invalid per spec — reject).

### Backward-Compatibility Checks

- [ ] Legacy Markdown output still follows prior section/table style.
- [ ] Legacy JSON top-level shape remains unchanged.
- [ ] Existing workflows (URL/file/hybrid) still callable without requesting `DESIGN.md`.

---

## Troubleshooting

| Problem | Action |
|---|---|
| Weak or sparse source evidence | Reduce output certainty; omit unsupported sections/tokens |
| Conflicting URL vs screenshot values | Prefer URL exact values; document discrepancy |
| Component values cannot reference tokens | Use literal value with note; improve token naming pass |
| Draft spec ambiguity | Follow `reference.md` compatibility notes and document assumptions |
