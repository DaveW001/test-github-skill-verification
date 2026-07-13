# PPTX Quality Pipeline — Category B Improvements Handoff

**Created:** 2026-07-12 (updated 2026-07-13)
**Author:** OpenCode Build Agent
**Status:** Category A COMPLETE; Category B (gap items B1–B10) NOT STARTED — this handoff drives that work
**Working code location:** `C:\development\pptx-pipeline\benchmarks\army-c2-pptx-model-comparison\quality_pipeline\`

---

## Purpose

This handoff enables a new OpenCode session to implement **Category B** — 10 quality-check gap items identified from research that layer on top of the completed core pipeline. These are improvements the core pipeline does NOT yet cover: WCAG contrast, brand palette adherence (design.md-driven), spacing/grid/alignment, placeholder compliance, cross-slide typography consistency, structural checks, connector styling, visual-balance metrics, and an annotated HTML QA report.

**No GitHub repos from the research note will be implemented directly.** All work is our own implementation.

---

## What's Done (Category A — Complete)

The core quality pipeline is fully built, tested, and baselined. All 12 production modules are implemented and the test suite passes:

| Module | File | Bytes |
|--------|------|-------|
| Content linting | `pptx_quality/content_lint.py` | 2,672 |
| Claim grounding | `pptx_quality/claims.py` | 2,483 |
| Geometry/collision | `pptx_quality/geometry.py` | 4,606 |
| Text-fit/overflow | `pptx_quality/text_fit.py` | 2,858 |
| Typography floors | `pptx_quality/typography.py` | 1,607 |
| PowerPoint rendering | `pptx_quality/rendering.py` | 3,442 |
| Visual review | `pptx_quality/visual_review.py` | 1,456 |
| Diagram checks | `pptx_quality/diagram_checks.py` | 2,984 |
| Scoring/verdicts | `pptx_quality/scoring.py` | 2,479 |
| Evaluator calibration | `pptx_quality/calibration.py` | 4,877 |
| Repair loop | `pptx_quality/repair_loop.py` | 3,602 |
| CLI orchestration | `pptx_quality/cli.py` | 8,361 |
| Shared models | `pptx_quality/_models.py` | 578 |

**Infrastructure:** `config/quality-policy.json`, `config/layout-capacities.json`, `schema/evaluation-report.schema.json`, `schema/visual-review.schema.json`, `requirements.txt` — all present.

**CLI:** `run_quality_pipeline.py` — works end-to-end (`--pptx`, `--source`, `--output`, `--visual-review`).

**Test suite:** 63 passed, 5 skipped (integration tests needing real decks).

**Baselines (3 models):** GPT-5.6 (109 hard failures), GLM-5.2 (60), MiniMax M2.5 (184) — all provisional. Correct severity ordering.

**Benchmark docs:** `benchmark-prompt.md`, `evaluation-rubric.md`, `final-eval-process.md`, `README.md`, `HANDOVER.md` — all present at benchmark root.

**Track status:** Conductor track `20260712-pptx-quality-pipeline` completed; track artifacts moved to `C:\development\pptx-pipeline\.conductor\tracks\20260712-pptx-quality-pipeline\`. A separate track `20260712-pptx-reference-image-rebuild` (reference-image reconstruction for the pptx-from-layouts skill) is also complete.

**Path bug fixed (2026-07-13):** `conftest.py` and `test_cli.py` had hardcoded paths to the old `opencode/benchmarks/` location; updated to relative path resolution after the code move.

---

## Current Directory Structure

```
C:\development\pptx-pipeline\benchmarks\army-c2-pptx-model-comparison\quality_pipeline\
├── __init__.py
├── run_quality_pipeline.py          # CLI entry point (1,851 bytes)
├── execution-log.md
├── red-gate-results.txt
├── HANDOVER.md
├── requirements.txt
├── config/
│   ├── quality-policy.json          # thresholds (286 bytes)
│   └── layout-capacities.json       # 7 archetypes (701 bytes)
├── schema/
│   ├── evaluation-report.schema.json (904 bytes)
│   └── visual-review.schema.json     (865 bytes)
├── pptx_quality/
│   ├── __init__.py
│   ├── _models.py                   # shared Result/finding models (578 bytes)
│   ├── content_lint.py
│   ├── claims.py
│   ├── geometry.py
│   ├── text_fit.py
│   ├── typography.py
│   ├── rendering.py
│   ├── visual_review.py
│   ├── diagram_checks.py
│   ├── scoring.py
│   ├── calibration.py
│   ├── repair_loop.py
│   └── cli.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # relative path resolution (fixed)
│   ├── test_smoke.py
│   ├── test_content_lint.py
│   ├── test_claims.py
│   ├── test_geometry.py
│   ├── test_text_fit.py
│   ├── test_typography.py
│   ├── test_rendering.py
│   ├── test_visual_review.py
│   ├── test_diagram_checks.py
│   ├── test_scoring.py
│   ├── test_calibration.py
│   ├── test_repair_loop.py
│   ├── test_cli.py                  # relative path resolution (fixed)
│   ├── derive_visual_review_fixtures.py
│   ├── run_baseline_matrix.py
│   └── validate_baselines.py
├── fixtures/
│   ├── glm-5-2/
│   ├── gpt-5-6/
│   └── minimax-m2-5/
└── baselines/
    ├── baseline-matrix-summary.json
    ├── glm-5-2/ (quality-report.json, visual-review.json)
    ├── gpt-5-6/ (quality-report.json, visual-review.json)
    └── minimax-m2-5/ (quality-report.json, visual-review.json)
```

---

## Existing Test Contracts (Reference for Category B)

The existing modules follow consistent patterns. Category B developers should match these conventions.

### Result/finding pattern
All check functions return a `Result` object (defined in `_models.py`) with `.findings` (list), plus domain-specific attributes. Findings have severity levels (`hard_failure`, `warning`) and finding codes (strings like `off_canvas`, `below_body_floor`).

### Module conventions
- Each module exports one primary function (e.g., `check_geometry`, `lint_content`, `check_typography`)
- Functions take typed inputs (shape dicts, text strings, config dicts)
- Shape dicts use EMU coordinates (914400/inch) with keys: `left, top, width, height, text, role`
- Policy thresholds come from `config/quality-policy.json`
- Findings are deterministic — same input always produces same output
- Modules never edit PPTX files directly; they emit findings/instructions

### quality-policy.json thresholds (existing)
- target_words_per_slide=80, hard_word_ceiling=90
- body_min_pt=18, label_min_pt=14, content_title_min_pt=32
- max_repair_iterations=3
- overflow_warning_ratio=1.05, overflow_hard_failure_ratio=1.25
- client_ready_requires_raster_review=true

### layout-capacities.json archetypes (existing)
7 archetypes: matrix, dashboard, roadmap, loop, escalation, comparison, risk_safeguard. Each has: max_primary_elements, max_words, min_body_pt, min_label_pt.

---

## The design.md Concept (Key Design Decision)

**User decision:** Brand palette checking should be driven by a `design.md` file used for each generation. This is the central organizing concept for gap items B2 (palette), B6 (typography consistency), and partially B1 (contrast).

### What design.md is
A per-deck (or per-brand) design specification file that accompanies each PPTX generation. It declares the brand palette, typography rules, spacing rules, and structural expectations. The quality pipeline reads it to know what "correct" means for that specific deck.

### Strongest existing template
`C:\development\marketing\docs\design-system\DESIGN.md` — rich YAML frontmatter (version, name, description, colors, typography with fontFamily/fontSize/fontWeight/lineHeight per role, rounded, spacing, components) + markdown body (overview, source-of-truth precedence, design principles, colors with semantic roles, typography, layout, elevation, shapes, animation, components, do's and don'ts).

### Existing Pydantic schema to REUSE
`C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\brand_config.py` defines `BrandConfigSchema` with:
- `ColorPalette` (primary, secondary, accent, background_light, background_dark; hex validation, no # prefix)
- `FontFamilies` (header, body, mono — each a list of allowed fonts)
- `FontSizeRanges` (header_bar 7-9pt, title 28-44pt, subtitle 18-24pt, body 12-20pt, footnote 8-11pt)
- `LogoPlacement` (position, min/max width/height pct, tolerance)
- `LogoConfig`
- `BrandConfigSchema` (name, colors, allowed_colors list, fonts, allowed_fonts list, font_size_ranges, logo)
- `to_checker_format()` and `from_checker_format()` methods
- Default brand = "Inner Chapter" (primary=0196FF, secondary=000000, accent=595959, fonts=Aptos)

This schema is RICH and already exists but is NOT currently wired into the quality pipeline. Category B should reuse it.

**NOTE:** `brand_checker.py` is referenced in `brand_config.py` docstrings but was NOT found. Do NOT depend on it — implement brand checking logic fresh in the quality pipeline.

### What design.md covers vs. what falls outside it

**Covered by design.md:**
- Brand color palette (allowed RGB values, semantic roles: primary/secondary/accent/background)
- Font families (header, body, mono — allowed lists)
- Font size ranges per role (title, subtitle, body, footnote, header_bar)
- Logo placement rules (position, size constraints, required slides)
- Spacing rules (margins, gutters, gaps — if declared)
- Layout grid expectations (if declared)
- Structural expectations (required slides: title, section dividers, summary/closing — if declared)

**Outside design.md (already handled by existing pipeline):**
- Content density limits (words per slide — quality-policy.json)
- Claim grounding (source text matching — claims.py)
- Bounding-box collision detection (geometry.py)
- Text-fit/overflow estimation (text_fit.py)
- Rendering and raster review (rendering.py, visual_review.py)
- Scoring rubrics and verdicts (scoring.py)
- Evaluator calibration (calibration.py)
- Repair strategy ordering (repair_loop.py)
- Diagram authenticity (diagram_checks.py)

### Fallback when design.md is missing or incomplete

**Strategy: graceful degradation with warnings, not hard failures.**

1. **No design.md at all:** Fall back to a default brand config (the Inner Chapter default from `create_default_brand_config()` in `brand_config.py`). Emit a `design_md_missing` warning finding. Brand checks run against the default. May produce false positives if the deck uses a different brand — the warning makes this visible.

2. **design.md present but missing fields:**
   - Missing `colors` block → fall back to default `ColorPalette`, emit `colors_missing` warning
   - Missing `fonts` block → fall back to default `FontFamilies`, emit `fonts_missing` warning
   - Missing `font_size_ranges` block → fall back to defaults, emit `font_size_ranges_missing` warning
   - Missing `logo` block → skip logo validation, emit `logo_config_missing` warning
   - Missing `spacing` block → skip spacing checks (B3), emit `spacing_config_missing` warning
   - Missing `layout` block → skip grid/alignment checks (B4), emit `layout_config_missing` warning

3. **design.md present but malformed (invalid YAML/JSON):** Emit `design_md_parse_error` hard_failure. Do NOT silently fall back — a broken design.md means the generation was broken.

4. **design.md present but invalid values (e.g., bad hex color):** The `BrandConfigSchema` Pydantic validation will raise. Catch it, emit `design_md_validation_error` hard_failure with the validation message.

**Principle:** Missing design.md → degrade gracefully with warnings. Broken design.md → hard failure.

---

## Category B: Gap Items (B1–B10) — The Work To Do

Each item includes: what it checks, why it matters, design.md dependency, finding codes, severity, and implementation notes.

---

#### B1. WCAG Text/Background Contrast Checking
- **What:** Compute contrast ratio between text color and its actual background color. Flag text below WCAG thresholds.
- **Why:** Low-contrast text is a common failure mode in AI-generated decks.
- **Thresholds:** 4.5:1 for normal text, 3:1 for large text (≥18pt or ≥14pt bold). WCAG 2.1 contrast formula.
- **design.md dependency:** Reads `colors` block to know intended text/background pairs. Falls back to checking every text run against its detected background.
- **Finding codes:** `contrast_below_normal` (hard_failure), `contrast_below_large` (warning), `contrast_unverifiable` (warning when background can't be determined).
- **Implementation notes:** Use python-pptx to read run colors and shape fill colors. For text on slide background, use the slide background color. For text inside shapes, use the shape's fill color. Handle theme colors (resolve via theme XML). Handle inherited colors.
- **Target module:** `pptx_quality/brand_checks.py`
- **Priority:** HIGH

#### B2. Brand Palette and Theme Adherence
- **What:** Check that every color used in the deck (text, fills, lines, backgrounds) is in the allowed palette. Flag arbitrary/off-palette colors.
- **Why:** AI generators frequently invent colors not in the brand palette.
- **design.md dependency:** Reads `colors` and `allowed_colors` from design.md (via `BrandConfigSchema`). This is the PRIMARY consumer of design.md.
- **Finding codes:** `off_palette_color` (warning), `off_palette_primary_role` (hard_failure — primary color used for a non-primary role), `missing_brand_color` (warning — brand color not used anywhere).
- **Implementation notes:** Reuse `BrandConfigSchema` from `pptx-from-layouts/schemas/brand_config.py`. Parse design.md YAML frontmatter into `BrandConfigSchema`. Iterate all shapes, runs, fills, lines. Compare each color (normalized to uppercase hex, no #) against `allowed_colors`.
- **Target module:** `pptx_quality/brand_checks.py`
- **Priority:** HIGH

#### B3. Minimum Whitespace and Element-Spacing Checks
- **What:** Check minimum gaps between elements, slide-edge margins, consistent gutters. Flag cramped cards, inconsistent spacing, edge-kissing.
- **Why:** Cramped layouts are a visual quality failure.
- **design.md dependency:** Reads `spacing` block (if declared) for expected margins, gutters, gaps. Falls back to sensible defaults (min 0.25" margin, min 0.1" gap between elements).
- **Finding codes:** `edge_margin_violation` (warning), `element_spacing_violation` (warning), `inconsistent_gutters` (warning), `cramped_layout` (warning).
- **Implementation notes:** Use bounding boxes from geometry check. Compute pairwise distances. Default thresholds: min edge margin = 0.25" (228600 EMU), min inter-element gap = 0.1" (91440 EMU).
- **Target module:** `pptx_quality/layout_checks.py`
- **Priority:** MEDIUM

#### B4. Grid and Alignment Consistency
- **What:** Check near-aligned edges, repeated object widths/heights, consistent distribution.
- **Why:** Misalignment is a subtle but pervasive AI-generation failure.
- **design.md dependency:** Reads `layout` block (if declared) for expected grid columns/rows. Falls back to detecting implicit grids from shape positions.
- **Finding codes:** `misaligned_edge` (warning), `inconsistent_width` (warning), `inconsistent_height` (warning), `uneven_distribution` (warning).
- **Implementation notes:** Cluster shapes by approximate left/top/width/height (within tolerance ~0.05" = 45720 EMU). Flag near-but-not-at alignment lines. Detect repeated element widths/heights. Check distribution.
- **Target module:** `pptx_quality/layout_checks.py`
- **Priority:** MEDIUM

#### B5. Template and Placeholder Compliance
- **What:** Check that shapes use native PowerPoint placeholders vs. free-floating text boxes. Flag unexpected layouts or placeholder misuse.
- **Why:** AI generators often create free-floating text boxes instead of using template placeholders, breaking editability.
- **design.md dependency:** None directly. Reads from pptx-from-layouts `template_config.json` if available.
- **Finding codes:** `freefloating_textbox` (warning), `placeholder_misuse` (warning), `unexpected_layout` (warning).
- **Implementation notes:** Use python-pptx `shape.is_placeholder`. Check `placeholder_format.type` and `idx` against expected layout. Flag text boxes that should be placeholders (heuristic: large text boxes in title/content positions).
- **Target module:** `pptx_quality/structure_checks.py`
- **Priority:** MEDIUM

#### B6. Cross-Slide Typography Consistency
- **What:** Check font-family consistency, consistent sizing per role, weight, capitalization, theme-font usage, and font substitution ACROSS slides.
- **Why:** AI generators often mix fonts or sizes inconsistently across slides. Distinct from existing typography.py (which checks minimum font sizes) — this checks CONSISTENCY across the deck.
- **design.md dependency:** Reads `fonts` and `font_size_ranges` blocks. SECONDARY consumer of design.md.
- **Finding codes:** `inconsistent_font_family` (warning), `inconsistent_title_size` (warning), `inconsistent_body_size` (warning), `font_substitution` (warning — font not in allowed_fonts), `weight_inconsistency` (warning), `capitalization_inconsistency` (warning). Font substitution → hard_failure if design.md declares allowed_fonts.
- **Implementation notes:** Group runs by role. Within each role, check font family consistency across slides. Check size consistency (within tolerance). Check against `allowed_fonts` from design.md. Detect theme-font usage (`+mj-lt` / `+mn-lt` in run XML).
- **Target module:** `pptx_quality/brand_checks.py`
- **Priority:** HIGH

#### B7. Required-Title and Structural Checks
- **What:** Check for titles on every slide, duplicate titles, hierarchy, section transitions, summary/closing slides. Configurable by deck type.
- **Why:** Missing titles and broken hierarchy are structural failures.
- **design.md dependency:** Reads `structure` block (if declared) for required slides, expected deck type.
- **Finding codes:** `missing_title` (hard_failure), `duplicate_title` (warning), `missing_section_divider` (warning), `missing_summary_slide` (warning), `missing_closing_slide` (warning), `hierarchy_violation` (warning).
- **Implementation notes:** Iterate slides, check for title placeholder or title-sized text. Track titles for duplicates. Check last slide for summary/closing content.
- **Target module:** `pptx_quality/structure_checks.py`
- **Priority:** MEDIUM

#### B8. Line and Connector Styling
- **What:** Check minimum line thickness, arrowheads, consistent styles, connector contrast.
- **Why:** Thin lines and missing arrowheads make diagrams hard to read.
- **design.md dependency:** Reads `lines` block (if declared) for min thickness, expected arrowhead style. Defaults: min 1pt, arrowheads required for process flows.
- **Finding codes:** `line_too_thin` (warning), `missing_arrowhead` (warning), `inconsistent_line_style` (warning), `connector_low_contrast` (warning).
- **Implementation notes:** Use python-pptx `shape.line.width`, `shape.line.dash_style`, arrowhead properties. Min thickness default: 1pt (12700 EMU).
- **Target module:** `pptx_quality/visual_metrics.py`
- **Priority:** LOW

#### B9. Visual-Balance Metrics
- **What:** Check left/right or top/bottom imbalance, isolated objects, overloaded regions. WARNING-level only.
- **Why:** Visual balance affects perceived quality but is subjective. Surface as warnings for human review.
- **design.md dependency:** None.
- **Finding codes:** `visual_imbalance` (warning), `isolated_object` (warning), `overloaded_region` (warning).
- **Implementation notes:** Compute center-of-mass of shapes per slide. Compare left/right and top/bottom weight. Flag imbalance >70%. Detect isolated/overloaded regions.
- **Target module:** `pptx_quality/visual_metrics.py`
- **Priority:** LOW

#### B10. HTML QA Report
- **What:** Generate an annotated HTML report with slide thumbnails, findings by severity, highlighted bounding boxes, per-slide scores, and recommended repairs.
- **Why:** JSON is machine-readable but not human-friendly. PPTChecker produces HTML reports. Makes findings actionable for the person repairing the deck.
- **design.md dependency:** None (consumes JSON report + rendered slide images).
- **Implementation notes:** Consume `quality-report.json` + rendered slide PNGs. Generate HTML with: summary header, per-slide section (thumbnail + findings + highlighted bounding boxes via EMU→px conversion), findings table sortable by severity, recommended repairs from repair_loop output. Output to `quality-report.html`.
- **Target module:** `pptx_quality/html_report.py`
- **Priority:** MEDIUM (after core pipeline works end-to-end — it does now)

---

## Recommended Implementation Order

Category A is done. Start at Wave 2.

### Wave 2: design.md Integration + Brand/Palette (B1, B2, B6)
The primary design.md consumers. Implement design.md parsing (YAML frontmatter → `BrandConfigSchema`), then:
1. **B2 (Brand Palette)** — check all colors against `allowed_colors`
2. **B1 (Contrast)** — WCAG contrast ratios for text/background pairs
3. **B6 (Cross-Slide Typography Consistency)** — font family/size consistency + allowed_fonts enforcement

**Deliverable:** `pptx_quality/brand_checks.py` + tests + design.md loader

### Wave 3: Spacing, Grid, Alignment (B3, B4)
1. **B3 (Whitespace/Spacing)** — gaps, margins, gutters
2. **B4 (Grid/Alignment)** — near-aligned edges, repeated dimensions, distribution

**Deliverable:** `pptx_quality/layout_checks.py` + tests

### Wave 4: Template/Placeholder + Structural (B5, B7)
1. **B5 (Placeholder Compliance)** — native placeholders vs free-floating text boxes
2. **B7 (Structural Checks)** — titles, hierarchy, required slides

**Deliverable:** `pptx_quality/structure_checks.py` + tests

### Wave 5: Connector Styling + Visual Balance (B8, B9)
1. **B8 (Line/Connector Styling)** — thickness, arrowheads, consistency
2. **B9 (Visual-Balance Metrics)** — center-of-mass, imbalance, isolation

**Deliverable:** `pptx_quality/visual_metrics.py` + tests

### Wave 6: HTML QA Report (B10)
**Deliverable:** `pptx_quality/html_report.py` + tests

### Wave 7: Integrate Into Existing Pipeline
- Add new check categories to `run_quality_pipeline.py` check order
- Add new categories to `scoring.py` (brand, layout, structure, visual_metrics)
- Update `schema/evaluation-report.schema.json` to include new check categories
- Update `config/quality-policy.json` with thresholds for new checks
- Re-baseline against the 3 model decks

---

## Key File References

### Quality Pipeline (working code)
- **Root:** `C:\development\pptx-pipeline\benchmarks\army-c2-pptx-model-comparison\quality_pipeline\`
- **Production modules:** `pptx_quality\*.py` (13 files, all implemented)
- **Tests:** `tests\test_*.py` (63 passed, 5 skipped)
- **CLI:** `run_quality_pipeline.py`
- **Config:** `config\quality-policy.json`, `config\layout-capacities.json`
- **Schema:** `schema\evaluation-report.schema.json`, `schema\visual-review.schema.json`

### Existing Brand Schema (REUSE for B2, B6)
- **Pydantic schema:** `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\brand_config.py`
  - Defines `BrandConfigSchema`, `ColorPalette`, `FontFamilies`, `FontSizeRanges`, `LogoPlacement`, `LogoConfig`
  - Has `to_checker_format()` / `from_checker_format()` methods
  - Default brand = "Inner Chapter"
  - **This schema exists but is NOT wired into the quality pipeline.** Category B must wire it in.
- **Simpler template config:** `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\template_config.py`

### design.md Templates (reference)
- **Strongest template:** `C:\development\marketing\docs\design-system\DESIGN.md`
- **Per-deck example:** `C:\development\marketing\content\topics\digitalai\jira-eol-webinar-2026-05\design.md`

### pptx-from-layouts Skill (delivered, closed)
- **Location:** `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\`
- **Template config:** `templates\inner-chapter-config.json` (brand block: primary=0196FF, secondary=000000, accent=595959, header_font=Aptos, body_font=Aptos)
- **Rules:** `rules\` (7 files)
- **NOTE:** `brand_checker.py` is referenced in `brand_config.py` docstrings but was NOT found. Do NOT depend on it.

### Conductor Tracks (completed)
- **Quality pipeline track:** `C:\development\pptx-pipeline\.conductor\tracks\20260712-pptx-quality-pipeline\` (moved from opencode repo)
- **Reference-image rebuild track:** `C:\development\opencode\.conductor\tracks\20260712-pptx-reference-image-rebuild\` (different effort, complete)

### Research Note (reference only)
- `C:\development\pptx-pipeline\Identify GitHub repos designed to create expert lo.md`
- Surveys: PPTChecker, powerpoint-toolkit, pptx-from-layouts, deckforge, etc.
- **Decision: NONE of these repos will be implemented directly.**

---

## Dependencies

### Python
- Python 3.13 (fallback: `py -3.13`)
- python-pptx==1.0.2, Pillow==12.1.0, jsonschema>=4.23<5, pytest>=8.3<9
- **Add for Category B:** PyYAML (design.md parsing), pydantic (BrandConfigSchema)

### System
- Microsoft PowerPoint 16.0 (production rendering; tests mock COM)
- win32com / comtypes / pythoncom (COM automation)
- Windows PowerShell 7+
- **Avoid requiring Bun** (environment hazard: Read/Write/glob/grep tools fail with `Bun is not defined`; use `bash` tool with PowerShell cmdlets)

---

## Next Steps for the New Session

1. **Load the Conductor pipeline skill** and create a NEW Conductor track for Category B.
2. **Use the full pipeline** (TDD): `1 -> 2 -> 4 -> 4b -> 5 -> 6 -> 7 -> 9` — write RED tests first, then implement.
3. **Start with Wave 2** (design.md integration + B1/B2/B6 in `brand_checks.py`).
4. **Follow the wave order** through Wave 7 (integration into existing pipeline).
5. **Run `python -m pytest tests\ -q` from the quality_pipeline directory** after each module to confirm tests pass.
6. **Re-baseline** against the 3 model decks after Wave 7 integration.

### Environment Reminder
The `Read`/`Write`/`glob`/`grep` tools fail with `Bun is not defined`. Use the `bash` tool with PowerShell cmdlets: `Get-Content -Raw`, `Set-Content`, `Get-ChildItem -Recurse`, `Select-String`.

---

**End of handoff document.**
