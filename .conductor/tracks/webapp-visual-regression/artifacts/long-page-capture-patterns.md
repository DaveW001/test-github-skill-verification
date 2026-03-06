# Long-Page Capture Patterns

## Goal
Reduce false positives on long pages where lazy sections, logo strips, and delayed assets can shift layout during capture.

## Pattern 1: Prime Before Lower Probe
- Use `primeLongContent()` to scroll to the bottom in short passes.
- Return to top, then run the lower probe capture.
- This warms lazy content before final screenshots.

## Pattern 2: Probe-Specific Stabilization
- For `lower` probes, apply an extra settle wait after scroll.
- Keep deterministic CSS animation suppression enabled.

## Pattern 3: Keep Evidence Lightweight
- Attach finding annotations and targeted evidence screenshot only when guards detect issues.
- Avoid full-page evidence attachments for every test.

## Usage
- Helper: `tests/visual/helpers/long-content.ts`
- Integrated in: `tests/visual/p0.visual.spec.ts` (`lower` probes)
