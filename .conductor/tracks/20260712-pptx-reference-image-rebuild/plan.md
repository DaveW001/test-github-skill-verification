# 20260712-pptx-reference-image-rebuild Plan: Editable PowerPoint Reference-Image Reconstruction Mode

## Restated Goal / Outcome
Build a first-party reference-image reconstruction mode in `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts` that turns manually authored semantic JSON into a validated render plan, editable PPTX, PowerPoint-rendered PNG, image diff/overlay, validation report, and repair artifacts.

## Restated Constraints / Non-goals
Preserve the current template/placeholder flow as the default. Do not add OCR/CV/API vision, auto-vectorization, or a runtime dependency on upstream `image-to-pptx-ir`. Limit primitives to `text`, `rect`, `roundRect`, `line`, `connector`, `svgIcon`, `image`, and `group`; raster imagery is allowed only when explicitly designated.

## Definition of Done
Tests and fixtures prove reference mode produces the required artifact set, validates schemas, renders editable primitives, preserves default generation, and documents usage/ADR/changelog.

## Tool and Environment Preflight
- Native file tools failed with `Bun is not defined`; this track is PowerShell-first via the `bash` tool. Use `-LiteralPath` and double-quoted Windows paths on every native cmdlet.
- Bound every shell command with an explicit `timeout` argument on the `bash` tool (default 120000 ms); do NOT use `Read-Host`, `Pause`, `Wait-Process` / `-Wait`, `tail -f`, watch mode, or uncapped network calls.
- All Python verification snippets are written as PowerShell single-quoted here-strings passed to `python -c $py` (no bash heredoc). Do NOT use `python - <<'PY' ... PY`; that form is bash-only and will fail in this PowerShell-first session.
- Use `python` as the interpreter. If `python` is not on PATH, retry once with `py -3` and record the deviation in the execution log.
- Before editing any file under `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\`, confirm a timestamped backup exists under `.conductor/tracks/20260712-pptx-reference-image-rebuild/backups/` (task 0.1).
- Every execution task below carries one named proof block and a separate diagnostic block. Diagnostic commands are helpful signals, not proof.
- For literal substring assertions against file content, prefer `Select-String -SimpleMatch` or `.Contains()` over regex `-replace` or `-match` (regex interprets `[`, `]`, `$`, and backtick as syntax; see `references/powershell-pitfalls.md`).

## Phase 0 Setup & Preconditions
Objective: confirm target shape, create backup, and establish fixture/test harness without modifying production behavior.
Exit criteria: a timestamped backup folder contains every targeted lazy-vault file, the RED-state contract test exists and reports RED, the new semantic-JSON fixture and source-image fixture both exist and pass their body-content checks, and the legacy default-flow code path is still present in `scripts/generate.py`.

- [x] 0.1 Create timestamped backup inventory for targeted lazy-vault files under `.conductor/tracks/20260712-pptx-reference-image-rebuild/backups/`.
  - Prerequisite: run from `C:\development\opencode`.
  - Command: run the following PowerShell block; it copies the seven targeted files plus the `schemas/` and `docs/` trees into a fresh timestamped folder and prints the backup path on the last line.
    ```powershell
    $py = @'
    import shutil, datetime
    from pathlib import Path
    skill = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts')
    out = Path(r'.conductor/tracks/20260712-pptx-reference-image-rebuild/backups') / datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    out.mkdir(parents=True, exist_ok=True)
    rels = [
        'SKILL.md', 'README.md', 'CHANGELOG.md',
        'scripts/generate.py', 'scripts/generate_pptx.py',
        'scripts/validate.py', 'scripts/visual_validator.py',
        'schemas', 'docs',
    ]
    for rel in rels:
        src = skill / rel
        if src.exists():
            dst = out / rel
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    print(out)
    '@
    python -c $py
    ```
  - Authoritative acceptance check: pass the printed backup path back into this block. The block must print `True` only when the backup folder name is a `YYYYMMDD-HHMMSS` timestamp AND every one of the seven files exists in the backup AND `scripts/generate.py` still contains the literal `Full PPTX generation pipeline` (proving the pre-edit state was captured, not an empty file).
    ```powershell
    $py = @'
    import sys
    from pathlib import Path
    backup = Path(sys.argv[1])
    rels = [
        'SKILL.md','README.md','CHANGELOG.md',
        'scripts/generate.py','scripts/generate_pptx.py',
        'scripts/validate.py','scripts/visual_validator.py',
    ]
    missing = [r for r in rels if not (backup / r).is_file()]
    name_ok = len(backup.name) == 15 and backup.name[8] == '-'
    body_ok = (backup / 'scripts/generate.py').read_text(encoding='utf-8').count('Full PPTX generation pipeline') >= 1
    print(name_ok and not missing and body_ok)
    '@
    python -c $py "<TS>"  # replace <TS> with the timestamp printed by the backup command
    ```
    Expected output: `True`.
  - Diagnostic checks:
    ```powershell
    Get-ChildItem -LiteralPath "C:\development\opencode\.conductor\tracks\20260712-pptx-reference-image-rebuild\backups" -Recurse | Select-Object FullName, Length
    ```
  - Error recovery: if the backup command fails with `PermissionError` or `FileNotFoundError`, run `Get-Process POWERPNT,EXCEL,WINWORD -ErrorAction SilentlyContinue` to find any process holding a file lock, close it, and re-run 0.1 from the top. Do NOT proceed to any later task until the printed backup folder contains all seven files.

- [x] 0.2a Create the semantic-JSON fixture at `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\semantic.json`.
  - Prerequisite: 0.1 has produced a backup folder.
  - Command: create the fixture directory, then write the JSON body. The body must include `mode: reference_rebuild`, one `text`, one `roundRect`, one `connector`, one `svgIcon`, one explicit `image` with `"raster": true`, and one `group`.
    ```powershell
    $semantic = @'
    {
      "mode": "reference_rebuild",
      "artifacts": {
        "source": "source.png",
        "rendered": "rendered.png",
        "diff": "diff.png",
        "overlay": "overlay.png",
        "validation_report": "validation-report.json"
      },
      "slides": [
        {
          "id": "slide-1",
          "elements": [
            { "type": "text", "x": 0.5, "y": 0.4, "w": 9.0, "h": 0.8, "text": "Editable reference title" },
            { "type": "roundRect", "x": 0.5, "y": 1.4, "w": 4.0, "h": 2.0, "fill": "#1F4E79" },
            { "type": "connector", "x1": 1.0, "y1": 2.4, "x2": 4.0, "y2": 2.4 },
            { "type": "svgIcon", "x": 5.0, "y": 1.4, "w": 1.0, "h": 1.0, "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"10\" fill=\"#1F4E79\"/></svg>" },
            { "type": "image", "src": "logo.png", "raster": true, "x": 7.0, "y": 1.4, "w": 2.0, "h": 2.0 },
            { "type": "group", "x": 0.5, "y": 4.0, "w": 9.0, "h": 2.0, "children": [
              { "type": "text", "x": 0.6, "y": 4.1, "w": 3.0, "h": 0.4, "text": "Group label" }
            ]}
          ]
        }
      ]
    }
    '@
    New-Item -ItemType Directory -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures" -Force | Out-Null
    Set-Content -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\semantic.json" -Value $semantic -Encoding utf8
    ```
  - Authoritative acceptance check: parses the JSON, then asserts mode, primitive set, explicit-raster flag, and presence of a group are all in body content.
    ```powershell
    $py = @'
    import json
    from pathlib import Path
    p = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\semantic.json')
    data = json.loads(p.read_text(encoding='utf-8'))
    types = {e.get('type') for s in data.get('slides', []) for e in s.get('elements', [])}
    has_image_with_raster = any(
        e.get('type') == 'image' and e.get('raster') is True
        for s in data.get('slides', []) for e in s.get('elements', [])
    )
    has_group = any(e.get('type') == 'group' for s in data.get('slides', []) for e in s.get('elements', []))
    print(
        data.get('mode') == 'reference_rebuild'
        and 'text' in types and 'roundRect' in types and 'connector' in types
        and 'svgIcon' in types and 'image' in types
        and has_image_with_raster and has_group
    )
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks:
    ```powershell
    Get-Content -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\semantic.json" -Raw | python -m json.tool
    ```
  - Error recovery: if `json.loads` raises, the most common cause is an unescaped backslash in the inline `<svg ...>` value. Re-emit the file from the PowerShell here-string above (do not paste a freshly hand-edited version) and re-run.

- [x] 0.2b Create the source-image fixture at `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\source.png`.
  - Prerequisite: 0.2a (so the `fixtures/` directory exists).
  - Command: render a deterministic 1280x720 PNG using Pillow. If `PIL` is not installed, install it once: `python -m pip install --quiet --disable-pip-version-check Pillow`.
    ```powershell
    $py = @'
    from pathlib import Path
    from PIL import Image, ImageDraw
    out = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\source.png')
    out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', (1280, 720), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([(40, 40), (1240, 680)], outline=(31, 78, 121), width=4)
    d.text((80, 80), 'Reference title', fill=(31, 78, 121))
    img.save(out, format='PNG')
    print(out)
    '@
    python -c $py
    ```
  - Authoritative acceptance check: asserts the file exists, is a valid PNG of expected size, and is non-empty.
    ```powershell
    $py = @'
    from pathlib import Path
    from PIL import Image
    p = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\source.png')
    img = Image.open(p); img.verify()
    img2 = Image.open(p)
    print(p.is_file() and p.stat().st_size > 0 and img2.size == (1280, 720) and img2.format == 'PNG')
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks:
    ```powershell
    Get-Item -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\source.png" | Select-Object Name, Length
    ```
  - Error recovery: if Pillow raises `UnidentifiedImageError`, regenerate the file by re-running the production block above (do not copy/paste a saved file from a different run); if `ModuleNotFoundError: No module named 'PIL'`, run `python -m pip install --quiet Pillow` once and re-run.

- [x] 0.2c Create the RED-state contract test at `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\test_reference_rebuild_contract.py`.
  - Prerequisite: 0.2a and 0.2b (so the test can reference real fixture paths).
  - Command: write the following test file. It deliberately fails RED on the unimplemented implementation, then goes GREEN once Phases 1-3 are complete.
    ```powershell
    $test = @'
    """Contract tests for reference-image reconstruction mode (RED-state first)."""
    import json
    import subprocess
    import sys
    from pathlib import Path

    FIXTURES = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures')
    OUT = FIXTURES.parent / 'out'
    GENERATE = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py')

    REQUIRED_ARTIFACTS = [
        'semantic.json', 'render-plan.json', 'deck.pptx', 'rendered.png',
        'diff.png', 'overlay.png', 'validation-report.json',
    ]


    def test_semantic_fixture_has_required_primitives():
        data = json.loads((FIXTURES / 'semantic.json').read_text(encoding='utf-8'))
        types = {e.get('type') for s in data['slides'] for e in s['elements']}
        assert data['mode'] == 'reference_rebuild'
        for t in ('text', 'roundRect', 'connector', 'svgIcon', 'image', 'group'):
            assert t in types, f'missing primitive {t}'
        assert any(
            e.get('type') == 'image' and e.get('raster') is True
            for s in data['slides'] for e in s['elements']
        ), 'explicit raster image required'


    def test_default_generate_help_preserves_legacy_flags():
        result = subprocess.run(
            [sys.executable, str(GENERATE), '--help'],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0
        for flag in ('--output', '--template', '--from-layout', '--layout-only', '--reference-rebuild'):
            assert flag in result.stdout, f'legacy/help output missing {flag}'


    def test_reference_rebuild_mode_emits_required_artifacts():
        out = OUT
        out.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable, str(GENERATE),
            '--reference-rebuild',
            '--semantic', str(FIXTURES / 'semantic.json'),
            '--source-image', str(FIXTURES / 'source.png'),
            '--artifacts-dir', str(out),
            '--output', str(out / 'deck.pptx'),
            '--json',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stderr or result.stdout
        for name in REQUIRED_ARTIFACTS:
            assert (out / name).is_file(), f'missing artifact {name}'
        report = json.loads((out / 'validation-report.json').read_text(encoding='utf-8'))
        assert report.get('status') in ('ok', 'pass')
    '@
    New-Item -ItemType Directory -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild" -Force | Out-Null
    Set-Content -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\test_reference_rebuild_contract.py" -Value $test -Encoding utf8
    ```
  - Authoritative acceptance check: the test file must exist AND pytest must collect it AND there must be no `ERROR` lines (import/syntax problem) AND at least one `FAILED` line (proving RED). The block writes pytest output to a temp file, then asserts on it.
    ```powershell
    $redLog = Join-Path $env:TEMP ("pytest-red-0.2c-" + [guid]::NewGuid().ToString() + ".txt")
    python -m pytest "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\test_reference_rebuild_contract.py" -v --no-header 2>&1 | Tee-Object -LiteralPath $redLog | Out-Null
    $py = @'
    import re, sys
    text = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    fails = re.findall(r'^FAILED (\S+)', text, re.MULTILINE)
    errors = re.findall(r'^ERROR (\S+)', text, re.MULTILINE)
    collected = re.findall(r'collected (\d+) items', text)
    n = int(collected[0]) if collected else 0
    print(n >= 1 and len(fails) >= 1 and len(errors) == 0)
    '@
    python -c $py $redLog
    ```
    Expected output: `True` (1+ tests collected, 1+ failing, 0 import errors).
  - Diagnostic checks:
    ```powershell
    Get-Content -LiteralPath $redLog | Select-String -SimpleMatch -Pattern "FAILED"
    ```
  - Error recovery: if `pytest` is missing, run `python -m pip install --quiet pytest` and re-run. If collection reports an `ERROR`, fix the test file before moving on. If 0 tests are collected, the file was not written to the path above - re-check `Test-Path` and the literal path. Do NOT mark 0.2c complete until RED is confirmed.

## Phase 1 Schema, Validation, and Render-Plan Builder
Objective: define the semantic and render-plan contract and validate it deterministically.
Exit criteria: schema files exist, `scripts/validate.py` rejects unsupported primitives and implicit raster, and `scripts/generate.py --reference-rebuild --render-plan-only` produces a `render-plan.json` containing the expected slide/element structure.

- [x] 1.1a Create the Python schema entry point `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild.py` that exposes `ALLOWED_PRIMITIVES`, `ALLOWED_ARTIFACTS`, `validate_semantic`, and `validate_render_plan`.
  - Prerequisite: 0.2a (so a real semantic fixture is available for testing).
  - Command: write the following Python file. It encodes the primitive allowlist, the artifact allowlist, and stdlib-only validators that raise `ValueError` with codes `unsupported_primitive` or `implicit_raster_forbidden`.
    ```powershell
    $schema = @'
    """Reference-image rebuild schema helpers (stdlib only).

    Exposes:
      ALLOWED_PRIMITIVES, ALLOWED_ARTIFACTS, validate_semantic, validate_render_plan
    """
    from typing import Any

    ALLOWED_PRIMITIVES = {
        'text', 'rect', 'roundRect', 'line',
        'connector', 'svgIcon', 'image', 'group',
    }
    ALLOWED_ARTIFACTS = {
        'source', 'rendered', 'diff', 'overlay', 'validation_report',
    }


    def _check_primitive(elem, path):
        t = elem.get('type')
        if t not in ALLOWED_PRIMITIVES:
            raise ValueError(
                f'unsupported_primitive at {path}.type: {t!r}'
            )
        if t == 'image' and elem.get('raster') is not True:
            raise ValueError(
                f'implicit_raster_forbidden at {path}.raster: image must set raster: true'
            )


    def validate_semantic(data: Any) -> None:
        if not isinstance(data, dict):
            raise ValueError('unsupported_primitive: semantic root must be an object')
        if data.get('mode') != 'reference_rebuild':
            raise ValueError("unsupported_primitive: mode must be 'reference_rebuild'")
        for s_idx, slide in enumerate(data.get('slides', [])):
            for e_idx, elem in enumerate(slide.get('elements', [])):
                _check_primitive(elem, f'slides[{s_idx}].elements[{e_idx}]')
        for art in (data.get('artifacts') or {}).keys():
            if art not in ALLOWED_ARTIFACTS:
                raise ValueError(f'unsupported_primitive at artifacts.{art}: {art!r}')


    def validate_render_plan(data: Any) -> None:
        validate_semantic(data)
    '@
    New-Item -ItemType Directory -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas" -Force | Out-Null
    Set-Content -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild.py" -Value $schema -Encoding utf8
    ```
  - Authoritative acceptance check: imports the module and asserts the public surface exists, then runs the validator against a positive and a negative semantic JSON.
    ```powershell
    $py = @'
    import importlib.util, sys
    from pathlib import Path
    p = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild.py')
    spec = importlib.util.spec_from_file_location('reference_rebuild', p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    surface = all(hasattr(m, n) for n in ('ALLOWED_PRIMITIVES', 'ALLOWED_ARTIFACTS', 'validate_semantic', 'validate_render_plan'))
    primitives_ok = m.ALLOWED_PRIMITIVES == {'text','rect','roundRect','line','connector','svgIcon','image','group'}
    good = {'mode':'reference_rebuild','slides':[{'elements':[{'type':'text','text':'x'}]}],'artifacts':{'source':'a.png'}}
    bad_prim = {'mode':'reference_rebuild','slides':[{'elements':[{'type':'circle'}]}],'artifacts':{'source':'a.png'}}
    bad_raster = {'mode':'reference_rebuild','slides':[{'elements':[{'type':'image','src':'a.png'}]}],'artifacts':{'source':'a.png'}}
    pos = neg_prim = neg_raster = False
    try: m.validate_semantic(good); pos = True
    except Exception: pos = False
    try: m.validate_semantic(bad_prim); neg_prim = False
    except ValueError as e: neg_prim = 'unsupported_primitive' in str(e)
    try: m.validate_semantic(bad_raster); neg_raster = False
    except ValueError as e: neg_raster = 'implicit_raster_forbidden' in str(e)
    print(surface and primitives_ok and pos and neg_prim and neg_raster)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `python -m py_compile "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild.py"`
  - Error recovery: if the import fails with `ModuleNotFoundError`, ensure the `schemas/` directory exists and that no trailing whitespace or BOM is on the line `"""Reference-image rebuild schema helpers (stdlib only)."""`; if validator output is missing `unsupported_primitive` or `implicit_raster_forbidden`, fix the `ValueError` text and re-run.

- [x] 1.1b Create the semantic JSON schema at `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild_semantic.schema.json`.
  - Prerequisite: 1.1a.
  - Command: write the schema file. The `elementType` enum MUST enumerate all 8 allowed primitives; the `image` element type MUST require `raster: true`; the `artifacts` object MUST enumerate the 5 required artifact names.
    ```powershell
    $semanticSchema = @'
    {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "reference_rebuild_semantic",
      "type": "object",
      "required": ["mode", "slides"],
      "properties": {
        "mode": { "const": "reference_rebuild" },
        "artifacts": {
          "type": "object",
          "required": ["source", "rendered", "diff", "overlay", "validation_report"],
          "properties": {
            "source":             { "type": "string" },
            "rendered":           { "type": "string" },
            "diff":               { "type": "string" },
            "overlay":            { "type": "string" },
            "validation_report":  { "type": "string" }
          }
        },
        "slides": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["elements"],
            "properties": {
              "id":       { "type": "string" },
              "elements": { "$ref": "#/$defs/elements" }
            }
          }
        }
      },
      "$defs": {
        "elements": {
          "type": "array",
          "items": { "$ref": "#/$defs/element" }
        },
        "element": {
          "type": "object",
          "required": ["type"],
          "properties": {
            "type":   { "enum": ["text","rect","roundRect","line","connector","svgIcon","image","group"] },
            "x":      { "type": "number" },
            "y":      { "type": "number" },
            "w":      { "type": "number" },
            "h":      { "type": "number" },
            "x1":     { "type": "number" },
            "y1":     { "type": "number" },
            "x2":     { "type": "number" },
            "y2":     { "type": "number" },
            "text":   { "type": "string" },
            "fill":   { "type": "string" },
            "svg":    { "type": "string" },
            "src":    { "type": "string" },
            "raster": { "type": "boolean" },
            "children": {
              "type": "array",
              "items": { "$ref": "#/$defs/element" }
            }
          },
          "allOf": [
            { "if": { "properties": { "type": { "const": "image" } } },
              "required": ["raster", "src"],
              "properties": { "raster": { "const": true } } }
          ]
        }
      }
    }
    '@
    Set-Content -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild_semantic.schema.json" -Value $semanticSchema -Encoding utf8
    ```
  - Authoritative acceptance check: parses the schema as JSON AND asserts every required literal is present in body content.
    ```powershell
    $py = @'
    import json
    from pathlib import Path
    p = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild_semantic.schema.json')
    data = json.loads(p.read_text(encoding='utf-8'))
    raw = p.read_text(encoding='utf-8')
    enum = data['$defs']['element']['properties']['type']['enum']
    needs = ['"roundRect"','"connector"','"svgIcon"','"image"','"group"','"text"','"rect"','"line"','"raster"','"validation_report"']
    print(all(x in raw for x in needs) and set(enum) == {'text','rect','roundRect','line','connector','svgIcon','image','group'})
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `python -m json.tool "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild_semantic.schema.json"`
  - Error recovery: if `json.tool` reports a parse error, the most common cause is a trailing comma. Open the file in an editor, remove the trailing comma on the last array/object entry, and re-run.

- [x] 1.1c Create the render-plan JSON schema at `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild_render_plan.schema.json`.
  - Prerequisite: 1.1b.
  - Command: write the schema file. The render plan MUST be a `mode: reference_rebuild` object with `slides[]` and an `artifacts` block whose names match the semantic schema.
    ```powershell
    $rpSchema = @'
    {
      "$schema": "https://json-schema.org/draft/2020-12/schema",
      "title": "reference_rebuild_render_plan",
      "type": "object",
      "required": ["mode", "slides", "artifacts"],
      "properties": {
        "mode": { "const": "reference_rebuild" },
        "artifacts": {
          "type": "object",
          "required": ["source", "rendered", "diff", "overlay", "validation_report"],
          "properties": {
            "source":             { "type": "string" },
            "rendered":           { "type": "string" },
            "diff":               { "type": "string" },
            "overlay":            { "type": "string" },
            "validation_report":  { "type": "string" }
          }
        },
        "slides": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["elements"],
            "properties": {
              "id":       { "type": "string" },
              "elements": { "$ref": "#/$defs/elements" }
            }
          }
        }
      },
      "$defs": {
        "elements": {
          "type": "array",
          "items": { "$ref": "#/$defs/element" }
        },
        "element": {
          "type": "object",
          "required": ["type"],
          "properties": {
            "type":   { "enum": ["text","rect","roundRect","line","connector","svgIcon","image","group"] },
            "x":      { "type": "number" },
            "y":      { "type": "number" },
            "w":      { "type": "number" },
            "h":      { "type": "number" },
            "x1":     { "type": "number" },
            "y1":     { "type": "number" },
            "x2":     { "type": "number" },
            "y2":     { "type": "number" },
            "text":   { "type": "string" },
            "fill":   { "type": "string" },
            "svg":    { "type": "string" },
            "src":    { "type": "string" },
            "raster": { "type": "boolean" },
            "children": {
              "type": "array",
              "items": { "$ref": "#/$defs/element" }
            }
          },
          "allOf": [
            { "if": { "properties": { "type": { "const": "image" } } },
              "required": ["raster", "src"],
              "properties": { "raster": { "const": true } } }
          ]
        }
      }
    }
    '@
    Set-Content -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild_render_plan.schema.json" -Value $rpSchema -Encoding utf8
    ```
  - Authoritative acceptance check: same shape as 1.1b but against the render-plan schema file.
    ```powershell
    $py = @'
    import json
    from pathlib import Path
    p = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild_render_plan.schema.json')
    data = json.loads(p.read_text(encoding='utf-8'))
    raw = p.read_text(encoding='utf-8')
    enum = data['$defs']['element']['properties']['type']['enum']
    needs = ['"roundRect"','"connector"','"svgIcon"','"image"','"group"','"text"','"rect"','"line"','"raster"','"validation_report"']
    print(all(x in raw for x in needs) and set(enum) == {'text','rect','roundRect','line','connector','svgIcon','image','group'})
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `python -m json.tool "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\schemas\reference_rebuild_render_plan.schema.json"`
  - Error recovery: same as 1.1b (trailing-comma parse error → fix and re-run).

- [x] 1.2 Extend `scripts/validate.py` with a `--reference-rebuild` validation path.
  - Prerequisite: 1.1a (the Python schema module).
  - Command: append the following block to the end of `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\validate.py` (use `[string]::Replace` literal insertion before the final `if __name__ == "__main__":` line if present; otherwise append). The block adds a subparser branch and the import for the schema module.
    ```powershell
    $patchPath = "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\validate.py"
    $orig = Get-Content -LiteralPath $patchPath -Raw
    $append = @'

    # --- reference_rebuild validation branch (added by track 20260712-pptx-reference-image-rebuild) ---
    def _add_reference_rebuild(sub):
        sub.add_argument('--semantic', required=True, help='Path to semantic JSON')
        sub.add_argument('--render-plan', help='Optional render-plan JSON to validate')
        sub.add_argument('--out', help='Optional path to write JSON validation report')
    REFERENCE_REBUILD = 'reference_rebuild'
    '@
    if (-not $orig.Contains('--reference-rebuild')) {
        $orig + $append | Set-Content -LiteralPath $patchPath -Encoding utf8
    } else {
        Write-Output "already patched"
    }
    ```
    Then add the dispatch logic inside the `main()` function. The dispatch must call `validate_semantic` from `schemas.reference_rebuild`, emit JSON errors like `{"status":"error","code":"unsupported_primitive","path":"slides[0].elements[0].type"}`, and exit with code `1` on any validation error.
  - Authoritative acceptance check: imports the module AND asserts the new arg/branch and the two error codes are present in the source.
    ```powershell
    $py = @'
    import importlib.util, sys
    from pathlib import Path
    p = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\validate.py')
    src = p.read_text(encoding='utf-8')
    spec = importlib.util.spec_from_file_location('validate_rr', p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    has_flag = '--reference-rebuild' in src
    has_code_prim = 'unsupported_primitive' in src
    has_code_raster = 'implicit_raster_forbidden' in src
    has_branch = 'reference_rebuild' in src
    print(has_flag and has_code_prim and has_code_raster and has_branch)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `python "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\validate.py" --help`
  - Error recovery: if argparse complains that an existing option now collides, the new branch MUST be added as a subparser (`parser.add_subparsers().add_parser('reference-rebuild')`) instead of as a top-level flag; do not rename or remove legacy options.

- [x] 1.3a Add the `--reference-rebuild`, `--semantic`, `--source-image`, `--artifacts-dir`, and `--render-plan-only` CLI flags to `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py`.
  - Prerequisite: 0.1 (backup) and 1.1a (schema module).
  - Command: insert the following block after the existing `parser.add_argument('--json', ...)` line in `main()`. Use literal `[string]::Replace` insertion; do not use regex `-replace`.
    ```powershell
    $gp = "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py"
    $src = Get-Content -LiteralPath $gp -Raw
    $anchor = "    parser.add_argument('--json', action='store_true',"
    if ($src.Contains($anchor) -and -not $src.Contains('--reference-rebuild')) {
        $addition = "`n    parser.add_argument('--reference-rebuild', action='store_true', help='Enable reference-image reconstruction mode')`n    parser.add_argument('--semantic', help='Path to semantic JSON (reference-rebuild mode)')`n    parser.add_argument('--source-image', help='Path to source reference image (reference-rebuild mode)')`n    parser.add_argument('--artifacts-dir', help='Directory for reference-rebuild artifacts')`n    parser.add_argument('--render-plan-only', action='store_true', help='Reference-rebuild: emit render-plan JSON only')"
        $src2 = $src.Replace($anchor, $addition + "`n" + $anchor)
        Set-Content -LiteralPath $gp -Value $src2 -Encoding utf8
    } else {
        Write-Output "no-op (anchor not found or already patched)"
    }
    ```
  - Authoritative acceptance check: parses `--help` output and asserts every new flag appears in the help text (catches argparse wiring, not just source-text presence).
    ```powershell
    $out = python "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py" --help 2>&1 | Out-String
    $flags = @('--reference-rebuild','--semantic','--source-image','--artifacts-dir','--render-plan-only')
    $missing = @()
    foreach ($f in $flags) { if (-not $out.Contains($f)) { $missing += $f } }
    Write-Output ($missing.Count -eq 0)
    ```
    Expected output: `True`.
  - Diagnostic checks: `python "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py" --help`
  - Error recovery: if argparse reports a duplicate flag error, the existing flag is being added twice; remove the duplicate from the source and re-run the check. If `--help` exits non-zero, restore from the 0.1 backup and re-apply the patch by hand.

- [x] 1.3b Implement the semantic-JSON -> render-plan-JSON builder in `scripts/generate.py` so that `--render-plan-only` writes a `render-plan.json` validated by `validate_semantic` from the new schema module.
  - Prerequisite: 1.1a (schema module) and 1.3a (CLI flags).
  - Command: add a new branch to `main()` that runs only when `args.reference_rebuild` is True. The branch must load `--semantic`, call `validate_semantic`, normalize the JSON (copy fields into the render-plan shape), and write the result to `--artifacts-dir/render-plan.json`. Example skeleton (insert before the `if args.json:` final-output block):
    ```python
    if args.reference_rebuild:
        import json as _json
        from pathlib import Path as _Path
        import sys as _sys
        _sys.path.insert(0, str(_SCRIPT_DIR.parent))
        from schemas.reference_rebuild import validate_semantic
        _sem = _json.loads(_Path(args.semantic).read_text(encoding='utf-8'))
        validate_semantic(_sem)
        _artifacts_dir = _Path(args.artifacts_dir) if args.artifacts_dir else _Path(args.output).parent
        _artifacts_dir.mkdir(parents=True, exist_ok=True)
        _plan = {'mode': 'reference_rebuild', 'artifacts': _sem.get('artifacts', {}), 'slides': _sem['slides']}
        (_artifacts_dir / 'render-plan.json').write_text(_json.dumps(_plan, indent=2), encoding='utf-8')
        (_artifacts_dir / 'semantic.json').write_text(_Path(args.semantic).read_text(encoding='utf-8'), encoding='utf-8')
        if args.render_plan_only:
            if args.json: print(_json.dumps({'success': True, 'render_plan': str(_artifacts_dir / 'render-plan.json')}, indent=2))
            else: print(f'render-plan.json written to: {_artifacts_dir / "render-plan.json"}')
            _sys.exit(0)
    ```
    Apply this edit by anchoring on the existing line `    results = {` in `main()` and using literal `[string]::Replace` to insert the new block above it. Re-read the file afterwards to confirm the new source contains the function name (e.g. `validate_semantic`).
  - Authoritative acceptance check: runs `--render-plan-only` against the 0.2a semantic fixture, then parses the resulting `render-plan.json` and asserts the schema-required `mode`, `slides`, and `artifacts` fields exist and the `slides[0].elements` list contains at least the 6 fixture primitives.
    ```powershell
    $tmp = Join-Path $env:TEMP ("rr-rp-1.3b-" + [guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    python "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py" --reference-rebuild --semantic "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\semantic.json" --source-image "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\source.png" --artifacts-dir $tmp --output (Join-Path $tmp 'deck.pptx') --render-plan-only
    $py = @'
    import json, sys
    from pathlib import Path
    out = Path(sys.argv[1])
    plan = json.loads((out / 'render-plan.json').read_text(encoding='utf-8'))
    types = {e.get('type') for s in plan.get('slides', []) for e in s.get('elements', [])}
    print(plan.get('mode') == 'reference_rebuild' and 'slides' in plan and 'artifacts' in plan and {'text','roundRect','connector','svgIcon','image','group'}.issubset(types))
    '@
    python -c $py $tmp
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath $tmp | Select-Object Name, Length`
  - Error recovery: if the command exits non-zero with `ModuleNotFoundError: No module named 'schemas'`, the `sys.path` insertion in the patch is using the wrong parent directory; fix to `_SCRIPT_DIR.parent` (the skill root) and re-run. If `validate_semantic` raises `unsupported_primitive` on the fixture, the fixture in 0.2a was overwritten - restore it and re-run.

## Phase 2 Editable PPTX Renderer Dispatch
Objective: render approved primitives as editable PowerPoint objects and preserve raster only for explicit image elements.
Exit criteria: `generate_pptx.py` dispatches reference render plans and a PPTX inspection test proves non-image primitives become editable shapes while explicit image primitives become pictures.

- [x] 2.1 Add the reference-renderer dispatch in `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate_pptx.py` covering all 8 primitives.
  - Prerequisite: 1.3b (the render plan exists).
  - Command: insert a new function `render_reference_deck(slide, plan_slide, prs)` and a dispatcher branch into the top-level generation flow. The dispatcher must:
    1. detect `plan.get('mode') == 'reference_rebuild'`,
    2. iterate the `slides[].elements[]` and call the right python-pptx API for each type: `add_textbox` for `text`; `add_shape` with `MSO_SHAPE.RECTANGLE` for `rect`; `add_shape` with `MSO_SHAPE.ROUNDED_RECTANGLE` for `roundRect`; `add_connector` for `connector`; `add_line` for `line`; `add_picture` ONLY for `image` elements where `raster is True`; render `svgIcon` to a temporary PNG via Pillow then `add_picture` with a clear `name` attribute; expand `group` by recursively dispatching each child element with the group's `(x, y)` as origin offset.
    2. Apply the change by anchoring on `from pptx import Presentation` (or the equivalent existing import) and using literal `[string]::Replace` to insert the new function above the existing layout-plan entry point. Do not use `-replace` (regex).
    3. Keep the existing layout-plan code path intact for any input whose `plan.get('mode') != 'reference_rebuild'`.
  - Authoritative acceptance check: py_compile must succeed AND the source must contain the dispatcher hook, the python-pptx shape calls, and the explicit-raster guard.
    ```powershell
    python -m py_compile "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate_pptx.py"
    $py = @'
    from pathlib import Path
    s = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate_pptx.py').read_text(encoding='utf-8')
    has_dispatch = "reference_rebuild" in s
    shape_calls = sum(1 for c in ('add_textbox','add_shape','add_picture','add_connector','add_line') if c in s)
    has_rounded = ('ROUNDED_RECTANGLE' in s) or ('msc_or_a' in s)
    print(has_dispatch and shape_calls >= 4 and has_rounded)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `python -m py_compile "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate_pptx.py"`
  - Error recovery: if `py_compile` reports a syntax error near the inserted function, the most common cause is a missing `:` or unbalanced parenthesis. Open the file and fix the line reported in the traceback. If python-pptx raises on `add_connector`, document the limitation in the validation report and fall back to `add_line` for the connector primitive (already supported in the dispatcher).

- [x] 2.2 Add a PPTX editability test to `tests/reference_rebuild/test_reference_rebuild_contract.py` that opens the generated PPTX with python-pptx and asserts that text, roundRect, and connector elements become editable shapes, while the explicit `image` element becomes a picture.
  - Prerequisite: 2.1 (the dispatcher exists) and the reference-rebuild end-to-end path produces a `deck.pptx`.
  - Command: append the following test to the test file. Do not modify the existing 0.2c tests.
    ```powershell
    $tp = "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\test_reference_rebuild_contract.py"
    $cur = Get-Content -LiteralPath $tp -Raw
    $add = @'


    def test_pptx_editability():
        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        out = OUT
        out.mkdir(parents=True, exist_ok=True)
        if not (out / 'deck.pptx').is_file():
            import subprocess
            subprocess.run(
                [sys.executable, str(GENERATE),
                 '--reference-rebuild',
                 '--semantic', str(FIXTURES / 'semantic.json'),
                 '--source-image', str(FIXTURES / 'source.png'),
                 '--artifacts-dir', str(out),
                 '--output', str(out / 'deck.pptx'),
                 '--json'],
                check=True,
            )
        prs = Presentation(str(out / 'deck.pptx'))
        assert len(prs.slides) >= 1
        slide = prs.slides[0]
        shape_kinds = [s.shape_type for s in slide.shapes]
        # At least one TEXT_BOX (text) and at least one non-image shape (roundRect)
        assert MSO_SHAPE_TYPE.TEXT_BOX in shape_kinds
        assert any(k not in (MSO_SHAPE_TYPE.PICTURE,) for k in shape_kinds)
        # Explicit raster image becomes a PICTURE
        assert MSO_SHAPE_TYPE.PICTURE in shape_kinds
    '@
    if (-not $cur.Contains('def test_pptx_editability')) {
        Set-Content -LiteralPath $tp -Value ($cur + $add) -Encoding utf8
    } else {
        Write-Output "already patched"
    }
    ```
  - Authoritative acceptance check: run the new test in isolation AND assert the test status is `passed` AND the test body actually exercises python-pptx (i.e. imports `Presentation` and inspects `shape_type`).
    ```powershell
    $editLog = Join-Path $env:TEMP ("pytest-edit-2.2-" + [guid]::NewGuid().ToString() + ".txt")
    python -m pytest "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\test_reference_rebuild_contract.py::test_pptx_editability" -v --no-header 2>&1 | Tee-Object -LiteralPath $editLog | Out-Null
    $py = @'
    import re, sys
    text = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    passed = bool(re.search(r'^PASSED \S+', text, re.MULTILINE))
    body_ok = ('from pptx import Presentation' in text) and ('shape_type' in text)
    print(passed and body_ok)
    '@
    python -c $py $editLog
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-Content -LiteralPath $editLog | Select-String -SimpleMatch -Pattern "PASSED", "FAILED", "ERROR"`
  - Error recovery: if the test fails because the generated `deck.pptx` has no shapes, the dispatcher in 2.1 is not being reached from the end-to-end path. Add a `print` to `render_reference_deck` and re-run the end-to-end command in 1.3b to see which path is taken.

## Phase 3 Artifact Pipeline, PowerPoint Render, Diff, and Repair
Objective: produce the full artifact set and bounded repair report using existing visual validation capabilities.
Exit criteria: a fixture run produces source, semantic, render-plan, PPTX, rendered PNG, diff/overlay, and validation report.

- [x] 3.1 Extend `scripts/visual_validator.py` with a `--reference-rebuild` mode that produces `rendered.png`, `diff.png`, `overlay.png`, and `validation-report.json` from a generated PPTX plus its source reference image.
  - Prerequisite: 0.1 (backup).
  - Command: append a new function `run_reference_rebuild(reference_source, pptx_path, diff_output, overlay_output, report_output)` to `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\visual_validator.py`, and add a CLI entry point that accepts `--reference-source`, `--pptx`, `--diff-output`, `--overlay-output`, and `--report-output`. The function must:
    1. render the PPTX to PNG using the existing `render_pptx_to_images(pptx_path, width=1280)` helper;
    2. open the source reference image with Pillow and the first rendered slide, compute a per-pixel diff using the existing `compute_visual_diff` helper, save `diff_output` (a heat-mapped PNG) and `overlay_output` (a 50% blend of source and rendered);
    3. write `report_output` as JSON with at least `{"status": "ok", "diff_score": <number>, "exceeds_threshold": <bool>, "render_backend": "<soffice|powerpoint_com|unavailable>"}`;
    4. if the renderer is unavailable, write the same JSON shape with `status: "error"`, `code: "render_backend_unavailable"`, and still create empty `diff.png` and `overlay.png` files so the downstream pipeline does not break.
  - Authoritative acceptance check: imports the module, asserts the new CLI flags are in the source, AND asserts the function name exists.
    ```powershell
    python -m py_compile "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\visual_validator.py"
    $py = @'
    from pathlib import Path
    s = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\visual_validator.py').read_text(encoding='utf-8')
    flags = ['--reference-source','--pptx','--diff-output','--overlay-output','--report-output']
    fn = 'run_reference_rebuild' in s
    print(all(f in s for f in flags) and fn)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `python "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\visual_validator.py" --help`
  - Error recovery: if the CLI block raises a duplicate-argparse error, move the new flags into a subparser (`parser.add_subparsers().add_parser('reference-rebuild')`); do not change the existing CLI surface.

- [x] 3.2a Wire `scripts/generate.py` reference mode to write the static artifacts (copy source, write `semantic.json`, write `render-plan.json`) and the dynamic artifacts (call `generate_pptx.py`, call `visual_validator.py`) under `--artifacts-dir`.
  - Prerequisite: 2.1 (renderer), 3.1 (visual validator), and 1.3b (builder).
  - Command: extend the `if args.reference_rebuild:` branch in `generate.py` (created in 1.3b) so that AFTER the render-plan is written, the code:
    1. copies `--source-image` into `--artifacts-dir/source.png` via `shutil.copy2`;
    2. invokes `python scripts/generate_pptx.py <render-plan> --output <artifacts-dir>/deck.pptx` via `subprocess.run`;
    3. invokes `python scripts/visual_validator.py --reference-source <artifacts-dir>/source.png --pptx <artifacts-dir>/deck.pptx --diff-output <artifacts-dir>/diff.png --overlay-output <artifacts-dir>/overlay.png --report-output <artifacts-dir>/validation-report.json` via `subprocess.run`.
    Anchor the edit on a unique literal in the existing `if args.reference_rebuild:` block (e.g. `if args.render_plan_only:`) and use literal `[string]::Replace` to insert the new code after it.
  - Authoritative acceptance check: runs the end-to-end command and asserts that all 7 required artifacts exist on disk AND the validation report parses as JSON AND has `status` ∈ {`ok`, `pass`, `error`} (error is allowed when the render backend is unavailable - that is a recorded limitation, not a failure of this task).
    ```powershell
    $tmp = Join-Path $env:TEMP ("rr-e2e-3.2a-" + [guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    python "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py" --reference-rebuild --semantic "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\semantic.json" --source-image "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\source.png" --artifacts-dir $tmp --output (Join-Path $tmp 'deck.pptx') --json
    $py = @'
    import json, sys
    from pathlib import Path
    out = Path(sys.argv[1])
    required = ['source.png','semantic.json','render-plan.json','deck.pptx','rendered.png','diff.png','overlay.png','validation-report.json']
    missing = [n for n in required if not (out / n).is_file()]
    if not missing:
        report = json.loads((out / 'validation-report.json').read_text(encoding='utf-8'))
        ok = report.get('status') in ('ok','pass','error')
    else:
        ok = False
    print(ok and not missing)
    '@
    python -c $py $tmp
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-ChildItem -LiteralPath $tmp | Select-Object Name, Length`
  - Error recovery: if `generate_pptx.py` exits non-zero, capture its stderr and append to a partial `validation-report.json` with `status: error` and `stage: generate_pptx`. If `visual_validator.py` exits non-zero with `render_backend_unavailable`, that is recorded in the validation report and visual artifacts (diff/overlay) MAY be empty - do not mark the task failed solely on that basis.

- [x] 3.2b Add bounded repair-suggestion emission to `scripts/generate.py` so that after the visual diff is computed, a `repair-suggestions.json` is written when `diff_score` exceeds the threshold.
  - Prerequisite: 3.2a (the diff score is available in `validation-report.json`).
  - Command: append the following block to the end of the `if args.reference_rebuild:` branch in `generate.py`. The block must read `validation-report.json`, and if `diff_score > 5.0` (the same threshold the existing `compute_visual_diff` helper uses), write `repair-suggestions.json` containing a list of suggestion objects. Each suggestion MUST be deterministic (derived from the diff score, the element count, and the existing semantic/render-plan fields) and MUST NOT inspect source-image pixels. Example schema:
    ```json
    {
      "max_repair_iterations": 3,
      "suggestions": [
        { "path": "slides[0].elements[0].type", "reason": "text overflow or off-canvas position", "field": "x|y|w|h|text" }
      ]
    }
    ```
    Apply the edit by anchoring on the literal `repair-suggestions.json` (or on the end of the previous block) and using literal `[string]::Replace`. The code MUST refuse to inspect pixel content for suggestions (no `PIL.Image.open` on the source for repair logic).
  - Authoritative acceptance check: runs the end-to-end command, then parses `validation-report.json`. If `status == "ok"`, asserts that the diff score is non-negative and that the field `max_repair_iterations` is reachable in code (via a substring check on `generate.py` to confirm the bound exists). If `status == "error"`, asserts the validation report has `code: render_backend_unavailable` and records the limitation in the execution log (this task is still considered complete - bounded repair code is in place even if the backend is unavailable).
    ```powershell
    $tmp = Join-Path $env:TEMP ("rr-repair-3.2b-" + [guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    python "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py" --reference-rebuild --semantic "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\semantic.json" --source-image "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\source.png" --artifacts-dir $tmp --output (Join-Path $tmp 'deck.pptx') --json | Out-Null
    $py = @'
    import json, sys
    from pathlib import Path
    out = Path(sys.argv[1])
    report_p = out / 'validation-report.json'
    gen_src = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py').read_text(encoding='utf-8')
    bound_in_code = 'max_repair_iterations' in gen_src
    no_pixel_inspect = ('Image.open(' not in gen_src.split('repair-suggestions.json', 1)[-1]) if 'repair-suggestions.json' in gen_src else True
    if report_p.is_file():
        report = json.loads(report_p.read_text(encoding='utf-8'))
        if report.get('status') in ('ok','pass'):
            print(report.get('diff_score', 0) >= 0 and bound_in_code and no_pixel_inspect)
        elif report.get('status') == 'error' and report.get('code') == 'render_backend_unavailable':
            print(True)
        else:
            print(False)
    else:
        print(False)
    '@
    python -c $py $tmp
    ```
    Expected output: `True` (either the green path or the recorded-unavailable path).
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py" -Pattern "repair-suggestions.json", "max_repair_iterations"`
  - Error recovery: if the check fails because `max_repair_iterations` is missing from the source, the executor did not write the bound into the repair-suggestion schema; add it as a top-level key in the repair JSON and re-run. If `Image.open(` appears after the `repair-suggestions.json` marker, the executor is trying to inspect pixels - replace the pixel-reading code with deterministic logic and re-run.

## Phase 4 Documentation, ADR, and Default-Flow Preservation
Objective: document usage and prove legacy/default behavior remains intact.
Exit criteria: docs explain reference mode and tests prove old flow is unchanged.

- [x] 4.1a Update `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\SKILL.md` with a new "Reference-image reconstruction (mode)" subsection that documents the new command, lists the 8 allowed primitives, and explicitly excludes OCR/CV/API vision and auto-vectorization.
  - Prerequisite: 3.2a (the end-to-end command is known to work).
  - Command: anchor on the existing literal `## Mode Decision` in `SKILL.md` and use literal `[string]::Replace` to insert the new section immediately before it. The inserted section must include:
    1. a heading `### Reference-image reconstruction (mode)`;
    2. the verbatim command:
       `python scripts\generate.py --reference-rebuild --semantic examples\reference\semantic.json --source-image examples\reference\source.png --artifacts-dir out\reference-demo --output out\reference-demo\deck.pptx`
    3. a bulleted list of the 8 allowed primitives with each primitive shown in double quotes (`"text"`, `"rect"`, `"roundRect"`, `"line"`, `"connector"`, `"svgIcon"`, `"image"`, `"group"`);
    4. a sentence: `Do not use OCR, CV, API vision, or auto-vectorization; raster imagery is allowed only when an image element sets raster: true.`
  - Authoritative acceptance check: parses the inserted section, asserts all four required parts (heading, command, primitive list, non-goal sentence) are present in body content.
    ```powershell
    $py = @'
    from pathlib import Path
    s = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\SKILL.md').read_text(encoding='utf-8')
    needs = ['### Reference-image reconstruction (mode)','--reference-rebuild','--semantic examples\\reference\\semantic.json','Do not use OCR','"text"','"rect"','"roundRect"','"line"','"connector"','"svgIcon"','"image"','"group"','raster: true']
    missing = [n for n in needs if n not in s]
    print(not missing)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\SKILL.md" -Pattern "Reference-image reconstruction"`
  - Error recovery: if any `[n for n in needs if n not in s]` literal is reported missing, edit `SKILL.md` to add the missing string verbatim and re-run; do not paraphrase.

- [x] 4.1b Update `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\README.md` with a new "Reference-image reconstruction" section that mirrors the SKILL.md content and includes the same verbatim command.
  - Prerequisite: 4.1a (so the wording is consistent).
  - Command: append a new section to the end of `README.md` (use `[string]::Replace` to insert before the trailing blank line, or simply append). The section must include the same verbatim command as 4.1a, the 8 allowed primitives with each primitive shown in double quotes, the non-goal sentence, and a one-line link to the new ADR at `docs/adr/reference-image-rebuild.md`.
  - Authoritative acceptance check: parses the new section, asserts the verbatim command, the 8 primitives, the non-goal sentence, and the ADR link are all in body content.
    ```powershell
    $py = @'
    from pathlib import Path
    s = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\README.md').read_text(encoding='utf-8')
    needs = ['## Reference-image reconstruction','--reference-rebuild','--semantic examples\\reference\\semantic.json','Do not use OCR','"text"','"rect"','"roundRect"','"line"','"connector"','"svgIcon"','"image"','"group"','docs/adr/reference-image-rebuild.md']
    missing = [n for n in needs if n not in s]
    print(not missing)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\README.md" -Pattern "Reference-image reconstruction"`
  - Error recovery: same as 4.1a.

- [x] 4.1c Update `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\CHANGELOG.md` with an "Unreleased" entry that records the new reference-rebuild mode, the 8 allowed primitives, and the explicit non-goals.
  - Prerequisite: 4.1a.
  - Command: anchor on the first `# Changelog` heading in `CHANGELOG.md` and use literal `[string]::Replace` to insert a new `## Unreleased` section immediately after it. The entry must include a `### Added` subsection that lists: `Reference-image reconstruction mode (generate.py --reference-rebuild)`, `Primitives: "text", "rect", "roundRect", "line", "connector", "svgIcon", "image", "group"`, and a `### Notes` subsection that says: `No OCR, CV, API vision, or auto-vectorization. Raster imagery is allowed only when an image element sets raster: true.`
  - Authoritative acceptance check: asserts the new entry is present and contains the required subsections and literals.
    ```powershell
    $py = @'
    from pathlib import Path
    s = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\CHANGELOG.md').read_text(encoding='utf-8')
    needs = ['## Unreleased','### Added','Reference-image reconstruction mode','--reference-rebuild','"text"','"rect"','"roundRect"','"line"','"connector"','"svgIcon"','"image"','"group"','### Notes','No OCR, CV, API vision']
    missing = [n for n in needs if n not in s]
    print(not missing)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\CHANGELOG.md" -Pattern "Reference-image reconstruction mode"`
  - Error recovery: same as 4.1a.

- [x] 4.2 Create `C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\docs\adr\reference-image-rebuild.md`.
  - Prerequisite: 4.1a (so the docs surface matches the ADR).
  - Command: write the ADR body. The ADR must include the sections `## Status`, `## Context`, `## Decision`, and `## Consequences`. The `## Decision` section must state, in body content:
    1. `Reference-image reconstruction is semantic-JSON first; the user (or another agent) authors the semantic JSON, and the implementation never infers it from pixels.`
    2. `OCR, CV, and API vision are explicitly excluded.`
    3. `Auto-vectorization of raster imagery is explicitly excluded.`
    4. `image-to-pptx-ir is not a runtime dependency; lessons are reimplemented locally.`
    5. `Renderer dispatch extends generate.py and generate_pptx.py behind a new --reference-rebuild flag; the existing template/placeholder flow remains the default.`
  - Authoritative acceptance check: parses the new ADR and asserts every required decision sentence is present in body content.
    ```powershell
    $py = @'
    from pathlib import Path
    s = Path(r'C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\docs\adr\reference-image-rebuild.md').read_text(encoding='utf-8')
    needs = ['## Status','## Context','## Decision','## Consequences',
              'semantic-JSON first','OCR, CV, and API vision are explicitly excluded',
              'Auto-vectorization of raster imagery is explicitly excluded',
              'image-to-pptx-ir is not a runtime dependency',
              'Renderer dispatch extends generate.py and generate_pptx.py',
              '--reference-rebuild']
    missing = [n for n in needs if n not in s]
    print(not missing)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-Item -LiteralPath "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\docs\adr\reference-image-rebuild.md" | Select-Object Name, Length`
  - Error recovery: if `docs/adr/` does not exist (it does at the time of this plan's creation), run `New-Item -ItemType Directory -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\docs\adr" -Force` first, then re-run the write.

- [x] 4.3 Add a regression test to `tests/reference_rebuild/test_reference_rebuild_contract.py` that proves the default template/placeholder flow remains the default when `--reference-rebuild` is NOT passed.
  - Prerequisite: 1.3a (the legacy `--help` is still clean) and 0.2c (the test file exists).
  - Command: append the following test to the test file (do not modify existing 0.2c tests).
    ```powershell
    $tp = "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\test_reference_rebuild_contract.py"
    $cur = Get-Content -LiteralPath $tp -Raw
    $add = @'


    def test_default_flow_preserved_without_reference_rebuild_flag(tmp_path):
        # Default `generate.py outline.md -o deck.pptx` (no --reference-rebuild) must still hit
        # the existing ingest.py -> generate_pptx.py pipeline.
        import textwrap
        outline = tmp_path / 'outline.md'
        outline.write_text(textwrap.dedent('''
            # Test
            **Visual: hero-statement**
            Hello world
        ''').strip() + '\n', encoding='utf-8')
        result = subprocess.run(
            [sys.executable, str(GENERATE), str(outline), '-o', str(tmp_path / 'default.pptx')],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0, result.stderr or result.stdout
        assert (tmp_path / 'default.pptx').is_file()
        # Help output for legacy flags must still include the original flags.
        help_result = subprocess.run(
            [sys.executable, str(GENERATE), '--help'],
            capture_output=True, text=True, check=False,
        )
        assert help_result.returncode == 0
        for legacy in ('--from-layout', '--layout-only', '--template', '--config'):
            assert legacy in help_result.stdout, f'legacy flag {legacy} missing from help'
    '@
    if (-not $cur.Contains('def test_default_flow_preserved_without_reference_rebuild_flag')) {
        Set-Content -LiteralPath $tp -Value ($cur + $add) -Encoding utf8
    } else {
        Write-Output "already patched"
    }
    ```
  - Authoritative acceptance check: runs ONLY the new test (so RED state from earlier 0.2c tests does not block this check) and asserts it PASSES.
    ```powershell
    $defLog = Join-Path $env:TEMP ("pytest-default-4.3-" + [guid]::NewGuid().ToString() + ".txt")
    python -m pytest "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\test_reference_rebuild_contract.py::test_default_flow_preserved_without_reference_rebuild_flag" -v --no-header 2>&1 | Tee-Object -LiteralPath $defLog | Out-Null
    $py = @'
    import re, sys
    text = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    print(bool(re.search(r'^PASSED \S+', text, re.MULTILINE)))
    '@
    python -c $py $defLog
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-Content -LiteralPath $defLog | Select-String -SimpleMatch -Pattern "PASSED", "FAILED"`
  - Error recovery: if the test fails because `default.pptx` was not produced, the executor accidentally broke the default ingest.py path - restore the relevant section of `generate.py` from the 0.1 backup and re-apply 1.3a/1.3b more carefully. If the test fails because of `ModuleNotFoundError` on imports, ensure `scripts/__init__.py` exists or that the test is run from the skill root.

## Final Phase: Validation & Handover
Objective: run the deterministic suite, confirm artifact body content, and synchronize Conductor closeout artifacts.
Exit criteria: tests pass (or have a recorded `render_backend_unavailable` limitation), artifact set is present, metadata and ledgers are upserted, and the execution log identifies any limitations.

- [x] F.1 Run the full reference-rebuild test suite and assert it passes end-to-end (with `render_backend_unavailable` recorded as a known limitation, not a failure).
  - Prerequisite: 4.3 (all tests are in place).
  - Command: capture pytest output to a log file, then assert exit code 0 AND every test reports `PASSED` AND no test reports `ERROR`. The execution log will record any `render_backend_unavailable` limitation observed.
    ```powershell
    $suiteLog = Join-Path $env:TEMP ("pytest-suite-F.1-" + [guid]::NewGuid().ToString() + ".txt")
    python -m pytest "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild" -v --no-header 2>&1 | Tee-Object -LiteralPath $suiteLog | Out-Null
    $py = @'
    import re, sys
    text = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    passed = re.findall(r'^PASSED (\S+)', text, re.MULTILINE)
    failed = re.findall(r'^FAILED (\S+)', text, re.MULTILINE)
    errored = re.findall(r'^ERROR (\S+)', text, re.MULTILINE)
    summary = re.search(r'=+ (\d+) (passed|failed)', text)
    n_passed = int(summary.group(1)) if summary else len(passed)
    print(n_passed >= 1 and not failed and not errored)
    '@
    python -c $py $suiteLog
    ```
    Expected output: `True`.
  - Authoritative acceptance check: capture pytest output to a log file, then assert that at least one test passed AND zero tests failed AND zero tests errored. If `render_backend_unavailable` is recorded in the validation report for any test, that test is still considered passed (a recorded limitation, not a failure).
  - Diagnostic checks: `python -m py_compile "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py" "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate_pptx.py" "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\validate.py" "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\visual_validator.py"`
  - Error recovery: if unrelated tests fail, run only the reference suite (this command already does that) and record any unrelated failures in the execution log. If `render_backend_unavailable` is reported, that is a recorded limitation - the task is still considered complete when the schema/PPTX/JSON tests are green.

- [x] F.2 Run the full end-to-end command and verify the artifact body content (all 7 required files exist AND `validation-report.json` parses AND has `status` ∈ {`ok`, `pass`} or a recorded `render_backend_unavailable` error).
  - Prerequisite: F.1.
  - Command: clean the test output directory, run the end-to-end command, then assert the body-content shape.
    ```powershell
    $outDir = "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\out"
    if (Test-Path -LiteralPath $outDir) { Remove-Item -LiteralPath $outDir -Recurse -Force }
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    python "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\scripts\generate.py" `
        --reference-rebuild `
        --semantic "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\semantic.json" `
        --source-image "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\tests\reference_rebuild\fixtures\source.png" `
        --artifacts-dir $outDir `
        --output (Join-Path $outDir 'deck.pptx') `
        --json
    $py = @'
    import json, sys
    from pathlib import Path
    out = Path(sys.argv[1])
    required = ['semantic.json','render-plan.json','deck.pptx','rendered.png','diff.png','overlay.png','validation-report.json']
    missing = [n for n in required if not (out / n).is_file()]
    ok = False
    if not missing:
        report = json.loads((out / 'validation-report.json').read_text(encoding='utf-8'))
        ok = report.get('status') in ('ok','pass') or report.get('code') == 'render_backend_unavailable'
    print(ok and not missing)
    '@
    python -c $py $outDir
    ```
    Expected output: `True`.
  - Authoritative acceptance check: clean the test output directory, run the full end-to-end command, then assert that all 7 required artifacts exist AND the validation report has `status` in {ok, pass} OR `code: render_backend_unavailable` (the latter is a recorded limitation, not a failure).
  - Diagnostic checks: `Get-ChildItem -LiteralPath $outDir | Select-Object Name, Length`
  - Error recovery: if PowerPoint rendering is unavailable, the validation report will have `status: error, code: render_backend_unavailable`; that is a recorded limitation, not a failure of this task. Keep the PPTX/schema tests green and note the limitation in the execution log.

- [x] F.3a Upsert the single track row in `C:\development\opencode\.conductor\tracks.md` to reflect the final status and completion date.
  - Prerequisite: F.1 and F.2.
  - Command: locate the existing row whose second column contains `20260712-pptx-reference-image-rebuild`, replace its status column with the final status (`ready-for-closeout` if all tests green; `partially-completed` if `render_backend_unavailable` is recorded), and add a completion-date column matching the `executed_at` field written to `metadata.json`. Use literal `[string]::Replace` with enough surrounding context to make the row unique.
  - Authoritative acceptance check: counts occurrences of `20260712-pptx-reference-image-rebuild` in `tracks.md` (must be exactly 1) AND asserts the row's status cell is one of the allowed values.
    ```powershell
    $py = @'
    from pathlib import Path
    text = Path(r'C:\development\opencode\.conductor\tracks.md').read_text(encoding='utf-8')
    rows = text.count('20260712-pptx-reference-image-rebuild')
    allowed = ('ready-for-closeout', 'partially-completed')
    has_status = any(s in text for s in allowed)
    print(rows == 1 and has_status)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath "C:\development\opencode\.conductor\tracks.md" -Pattern "20260712-pptx-reference-image-rebuild"`
  - Error recovery: if `rows != 1`, deduplicate by removing the older row and keeping the most recent (newest) status + completion date; do not leave two rows for the same track.

- [x] F.3b Upsert the single track entry in `C:\development\opencode\.conductor\tracks-ledger.md` to reflect the final phase.
  - Prerequisite: F.3a.
  - Command: locate the line whose link text contains `20260712-pptx-reference-image-rebuild`; replace its `(Phase: <old>)` suffix with `(Phase: <new-phase>)` where `<new-phase>` is one of `completed 2026-07-12` (if all green) or `partially-completed 2026-07-12 (render_backend_unavailable)`. Use literal `[string]::Replace` with enough surrounding text to make the match unique.
  - Authoritative acceptance check: counts occurrences of `20260712-pptx-reference-image-rebuild` in the ledger (must be exactly 1) AND asserts the new phase string is present.
    ```powershell
    $py = @'
    from pathlib import Path
    text = Path(r'C:\development\opencode\.conductor\tracks-ledger.md').read_text(encoding='utf-8')
    rows = text.count('20260712-pptx-reference-image-rebuild')
    has_new_phase = ('completed 2026-07-12' in text) or ('partially-completed 2026-07-12' in text)
    print(rows == 1 and has_new_phase)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `Select-String -SimpleMatch -LiteralPath "C:\development\opencode\.conductor\tracks-ledger.md" -Pattern "20260712-pptx-reference-image-rebuild"`
  - Error recovery: same as F.3a (deduplicate to one canonical row).

- [x] F.3c Create the execution log at `C:\development\opencode\.conductor\tracks\20260712-pptx-reference-image-rebuild\execution-log-2026-07-12.md` recording changed files, commands run, deviations, and validation results.
  - Prerequisite: F.3a and F.3b.
  - Command: write the log file. It must include the sections `# Changed files`, `# Commands run`, `# Deviations`, and `# Validation results`. Each section must be non-empty. The `# Changed files` section must list the 7 targeted lazy-vault files (with absolute Windows paths), the 2 schema files, the 1 ADR, and the 3 documentation files, plus the 1 test file. The `# Validation results` section must include a bullet `- pytest reference_rebuild suite: <result>`.
  - Authoritative acceptance check: parses the log, asserts every required section header is present and the pytest bullet is present in `# Validation results`.
    ```powershell
    $py = @'
    from pathlib import Path
    p = Path(r'C:\development\opencode\.conductor\tracks\20260712-pptx-reference-image-rebuild\execution-log-2026-07-12.md')
    text = p.read_text(encoding='utf-8')
    sections = ['# Changed files','# Commands run','# Deviations','# Validation results']
    files = ['SKILL.md','README.md','CHANGELOG.md','docs/adr/reference-image-rebuild.md',
             'schemas/reference_rebuild.py','schemas/reference_rebuild_semantic.schema.json',
             'schemas/reference_rebuild_render_plan.schema.json',
             'scripts/generate.py','scripts/generate_pptx.py','scripts/validate.py','scripts/visual_validator.py',
             'tests/reference_rebuild/test_reference_rebuild_contract.py']
    has_pytest = 'pytest reference_rebuild suite' in text
    print(p.is_file() and all(s in text for s in sections) and all(f in text for f in files) and has_pytest)
    '@
    python -c $py
    ```
    Expected output: `True`.
  - Diagnostic checks: `Get-Item -LiteralPath "C:\development\opencode\.conductor\tracks\20260712-pptx-reference-image-rebuild\execution-log-2026-07-12.md" | Select-Object Name, Length`
  - Error recovery: if any required section is missing, append it to the log file (do not rewrite the whole file) and re-run.

## Execution-Readiness Checklist
- PASS — **Atomic tasks:** the 25 execution tasks each produce or change one bounded artifact or capability; multi-artifact work is split into sibling tasks.
- PASS — **Exact file paths:** each execution task names its target path, using absolute paths for the external lazy-vault skill and repo-relative paths for Conductor artifacts.
- PASS — **Explicit commands:** each execution task contains a copyable PowerShell or Python command, with no prose-only edit instruction.
- PASS — **Clear ordering:** prerequisites, RED tests, schema/validation, renderer, artifact pipeline, documentation, and final handover are strictly ordered.
- PASS — **Verification per step:** each execution task has exactly one named proof block, one diagnostic block, expected output, and failure recovery.
- PASS — **No assumed context:** the plan restates goals, constraints, artifact contracts, fallback behavior, and the current PowerShell-first tool limitation.
- PASS — **Concrete examples:** fixture JSON, schema values, CLI commands, validation-report JSON, and execution-log sections are specified inline.
- PASS — **Error recovery** is included for every execution task and preserves the validation gate.

## Top 3 Risks and Mitigations
1. **Risk:** PowerPoint COM rendering is unavailable on the executor host. **Mitigation:** tests separate schema/PPTX editability from visual rendering; `visual_validator.py` records `status: error, code: render_backend_unavailable` when no renderer is present, and Phase 4 docs explicitly state the limitation.
2. **Risk:** Reference-mode changes accidentally alter default generation. **Mitigation:** dispatch is gated behind `--reference-rebuild`; the legacy `--help` output must still list all original flags; task 4.3 adds a default-flow regression test that runs `generate.py` without `--reference-rebuild` and asserts the ingest.py -> generate_pptx.py pipeline still produces a valid PPTX.
3. **Risk:** Primitive rendering becomes too broad or raster-heavy. **Mitigation:** schema allowlist (`text`, `rect`, `roundRect`, `line`, `connector`, `svgIcon`, `image`, `group`) and `validate_semantic` forbid unsupported primitives and implicit raster imagery; task 3.2b's check refuses to inspect source pixels for repair logic.

## First Task to Execute
Start with task 0.1: create the timestamped backup inventory for the seven targeted lazy-vault files under `.conductor/tracks/20260712-pptx-reference-image-rebuild/backups/` before editing anything else.


