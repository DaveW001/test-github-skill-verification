# Review Diff Summary: 20260712-pptx-reference-image-rebuild

**Reviewer:** conductor-plan-reviewer (Stage 2)
**Compared:** original plan (16 tasks, 21 883 bytes) vs. revised plan (25 tasks, ~78 000 bytes)
**Date:** 2026-07-12 21:59:43

## Structural changes

- **Task count:** 16 -> 25 (+9 splits)
- **Authoritative acceptance checks:** 16 -> 25 (one per task, with the 3 malformed labels in 0.2a / 0.2b / 1.1b fixed and the F.1 / F.2 missing labels added)
- **Diagnostic checks block:** added or refined for all 25 tasks
- **Error recovery block:** present for all 25 tasks
- **Bash heredocs (`python - <<''PY'' ... PY`):** 16 -> 0 (all replaced with `python -c $py` PowerShell here-strings)
- **`Get-ChildItem` / `Select-String` calls without `-LiteralPath`:** 7 -> 0 (all use `-LiteralPath` with double-quoted paths)
- **Path separator inconsistencies (`C:/...` mixed with `C:\...`):** 4 -> 0 (all Windows paths use backslashes)

## Task-level changes (original -> revised)

| Original | Revised | Reason |
|---|---|---|
| 0.1 (one task) | 0.1 (unchanged) | Backup task was atomic; kept as-is. |
| 0.2 (create source.png + semantic.json + RED test) | 0.2a (semantic.json) + 0.2b (source.png) + 0.2c (RED test) | Multi-file, multi-decision. |
| 1.1 (create 3 schema files) | 1.1a (Python module) + 1.1b (semantic JSON schema) + 1.1c (render-plan JSON schema) | Multi-file. |
| 1.2 (extend validate.py) | 1.2 (unchanged) | Single file, single decision. |
| 1.3 (add CLI flags + builder logic) | 1.3a (CLI flags only) + 1.3b (builder logic) | Multi-decision. |
| 2.1 (add detection + 8 renderer functions) | 2.1 (kept, but command rewritten as numbered spec; check relaxed to `shape_calls >= 4` and `has_rounded` to allow natural function naming) | Single file, but command was prose. |
| 2.2 (PPTX inspection test) | 2.2 (kept, but check upgraded to run pytest + parse log for `PASSED` line + assert test body actually inspects `shape_type`) | Original check only inspected test file body, not PPTX behavior. |
| 3.1 (extend visual_validator.py) | 3.1 (kept, command rewritten as numbered spec + verbatim CLI list) | Original was prose. |
| 3.2 (5+ orchestration actions) | 3.2a (artifact wiring) + 3.2b (bounded repair) | Multi-decision. |
| 3.3 (repair-suggestions; brittle "No OCR/CV/API vision" phrase check) | 3.2b (renumbered; check now uses `max_repair_iterations` substring + post-marker `Image.open(` absence) | Brittle literal replaced. |
| 4.1 (3 doc files) | 4.1a (SKILL.md) + 4.1b (README.md) + 4.1c (CHANGELOG.md) | Multi-file. |
| 4.2 (ADR) | 4.2 (unchanged) | Single file. |
| 4.3 (default-flow regression test) | 4.3 (kept, test rewritten to use `tmp_path` fixture and assert legacy flags in `--help` output) | Original had no fixture isolation. |
| F.1 (run full suite) | F.1 (kept, but authoritative check now parses pytest log for `=+ (\d+) (passed|failed)` summary line and asserts zero FAILED/ERROR) | Original check was identical to the action. |
| F.2 (end-to-end verify) | F.2 (kept, command broken into multi-line PowerShell with backtick continuations; check now allows `code: render_backend_unavailable` as recorded limitation) | Original was one long line; brittle. |
| F.3 (upsert 2 ledgers + create log) | F.3a (tracks.md) + F.3b (tracks-ledger.md) + F.3c (execution log) | Multi-file, multi-decision. |

## metadata.json changes

- `task_count`: `16` -> `25`
- `total_checkbox_count`: `16` -> `25`
- `updated`: unchanged (already `2026-07-12`)
- `status`: unchanged (still `ready-for-plan-review`)
- `track_type`, `classification`, `pipeline_mode`, `pipeline_path`, `test_framework`, `test_command`: all unchanged (already correct)

## spec.md changes

- None. The spec defines the goal, constraints, definition of done, required artifacts, and acceptance criteria. All of these were already clear and well-formed; no executability issues at the spec level.

## Verification rigor improvements (representative)

- **Original 0.1 check:** `print(bool(files and 'Full PPTX generation pipeline' in files[-1].read_text(...)))` - dry-runnable but assumes the backup folder name and last-modified file.
- **Revised 0.1 check:** parses the backup path from CLI, asserts the timestamp format (`len(name) == 15 and name[8] == '-'`), all 7 files present, AND the `Full PPTX generation pipeline` literal in `generate.py`. Dry-runned against a mock backup returned `True`.
- **Original 1.1 check:** required `"roundRect"`, `"connector"`, `"svgIcon"`, `"raster"`, `"validation_report.json"` - 5 literals across 2 files.
- **Revised 1.1b / 1.1c check:** requires all 8 primitive names + `raster` + `validation_report`, AND asserts the parsed JSON enum equals the 8-element set. Catches a missing or mistyped primitive name in the schema enum.
- **Original F.1 check:** identical to the action (`python -m pytest ... -q`).
- **Revised F.1 check:** captures pytest output to a temp log, parses the `=+ (\d+) (passed|failed)` summary line, asserts `n_passed >= 1` AND zero FAILED/ERROR lines. Allows `render_backend_unavailable` to be a recorded limitation in the execution log.

## Untested by reviewer (executor must validate)

- The PowerShell `[string]::Replace` edits inside `scripts/generate.py` (1.3a, 1.3b, 3.2a, 3.2b) and `scripts/validate.py` (1.2). Reviewer dry-ran the check logic against mock source; executor must apply the edit and re-run the check against the real file.
- The python-pptx dispatcher in `scripts/generate_pptx.py` (2.1). Reviewer dry-ran the source-presence check; executor must run `py_compile` and the PPTX inspection test (2.2) against the actually-rendered PPTX.
- The visual-validator function in `scripts/visual_validator.py` (3.1). Reviewer dry-ran the source-presence check; executor must run the end-to-end command and confirm the validation report has the expected `render_backend` field.
- F.2 end-to-end: requires LibreOffice OR PowerPoint COM on the executor host. If neither is available, the validation report will record `status: error, code: render_backend_unavailable` and 3.2b's check accepts that as a recorded limitation.

## Final counts

- Checkboxes: 25 (16 before)
- Authoritative acceptance checks: 25 (one per task)
- Diagnostic check blocks: 26 (one per task; F.3a has zero standalone diagnostic but is still single-action)
- Bash heredoc violations: 0
- `-LiteralPath` violations on native cmdlets: 0
- Path-separator inconsistencies: 0
- Multi-file / multi-decision tasks: 0 (down from 6)
- Brittle prose commands ("edit", "update", "add"): 0 (down from 7)
- Headings-only or phrase-only authoritative checks: 0 (all 25 checks inspect body content or executable behavior)
