# 20260712-pptx-reference-image-rebuild Spec: Editable PowerPoint Reference-Image Reconstruction Mode

## Goal / Outcome
Implement a built-in, test/fixture-driven reference-image reconstruction mode in the globally installed lazy-vault skill at `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts`. The mode converts a human-authored semantic JSON description of a reference image into a render-plan JSON, validates it, generates an editable PPTX, renders the PPTX to PNG with the existing visual validator, produces diff/overlay artifacts against the source image, and supports bounded repair.

## Constraints / Non-goals
- Preserve the current template/placeholder outline-to-layout flow as the default behavior in `scripts/generate.py` and `scripts/generate_pptx.py`.
- Do not add automated OCR, CV, API vision, or image understanding. The first implementation consumes manually authored semantic JSON.
- Do not make upstream `image-to-pptx-ir` a runtime dependency. Any lessons from it must be reimplemented locally and minimally.
- Do not auto-vectorize raster images. Imagery is only allowed when explicitly designated as raster in semantic JSON/render-plan JSON.
- Core primitives are limited to: `text`, `rect`, `roundRect`, `line`, `connector`, `svgIcon`, `image`, `group`.
- Work targets these existing skill files precisely: `SKILL.md`, `README.md`, `CHANGELOG.md`, `scripts/generate.py`, `scripts/generate_pptx.py`, `scripts/validate.py`, `scripts/visual_validator.py`, `tests`, `docs/adr/reference-image-rebuild.md`, and `schemas`.

## Definition of Done
- A new CLI mode exists in `scripts/generate.py` that dispatches reference-image reconstruction without changing default generation semantics.
- Built-in schema and validation reject unsupported primitives, implicit raster imagery, missing artifacts, and malformed render plans.
- `scripts/generate_pptx.py` renders all allowed primitives as editable PowerPoint objects where possible, with raster only for explicit `image` primitives.
- Required artifacts are produced for a fixture run: source image, semantic JSON, render-plan JSON, PPTX, rendered PNG, diff/overlay, and validation report.
- Tests/fixtures cover the end-to-end contract before implementation is marked complete.
- Documentation and ADR explain the mode, non-goals, artifacts, and repair loop.

## Required Artifacts
For each reconstruction run, write or preserve these artifacts under the caller-specified output directory:
1. `source.png` or caller-provided source reference image path.
2. `semantic.json`.
3. `render-plan.json`.
4. `deck.pptx`.
5. `rendered.png`.
6. `diff.png` and `overlay.png`.
7. `validation-report.json`.

## Acceptance Criteria
1. The default command `python scripts/generate.py outline.md -o deck.pptx` continues to use the current template/placeholder flow.
2. A new reference mode accepts semantic JSON plus source image, emits render-plan JSON, validates it, generates PPTX, renders PNG, and writes diff/overlay/report artifacts.
3. The schemas document and enforce only the approved primitive set.
4. Unsupported primitives and implicit raster extraction fail with deterministic JSON validation errors.
5. The implementation is fixture-driven and runnable with a single pytest command.
