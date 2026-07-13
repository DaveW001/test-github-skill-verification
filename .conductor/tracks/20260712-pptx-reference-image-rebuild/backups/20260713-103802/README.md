# pptx-from-layouts (OpenCode skill)

Generate consultant-grade PowerPoint decks from markdown outlines by filling a
template's **real slide-master layouts** - never overlaying text boxes on slides.

This is the OpenCode adaptation of the `pptx-from-layouts` Claude Code skill,
consolidated into **one self-contained, Windows-native skill**. The original
three-step pipeline (profile -> author -> render) and its two sibling skills
(`pptx-profile`, `pptx-author`) are all folded into this single skill.

---

## What this skill does

A three-step pipeline. Each step is a script under `scripts\`:

| Step | Purpose | Script |
|------|---------|--------|
| **1 - Profile** | Turn a `.pptx` into a layout catalog + render `config.json` (one-time per template) | `catalog.py` / `profile.py` |
| **2 - Author** | Write `slides.md` with a `[HINT: layout_name]` / `**Visual:**` per slide; lint hints against the catalog | `lint_hints.py` |
| **3 - Render** | Fill the named layouts and validate the deck | `generate.py` (+ `validate.py`) |

You can also start directly at **Step 3** with the bundled **Inner Chapter**
template (no profiling needed) - it is the default and the running example
throughout this doc.

---

## Installation location

The skill lives in the OpenCode lazy vault (global, available across sessions):

```
C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts\
```

All entry-point scripts are under `scripts\` relative to that root, and the
bundled default template is under `templates\`. The scripts resolve their own
paths relative to the skill directory, so they work from any working directory.

> **Note:** If this skill was just installed during the current session, a
> **session restart is required** before `skill_find` / `skill_use` can discover
> it (the opencode-skillful plugin caches its vault index at startup). The
> scripts themselves work immediately via a direct `python` call.

---

## Windows requirements

| Requirement | Needed for |
|-------------|-----------|
| **Python 3.7+** | All scripts. The source skill recommends 3.10+; the bundled code explicitly guards for 3.7+ (e.g. `hasattr(sys.stdout, "reconfigure")`). |
| **python-pptx** | Rendering and validation (`generate.py`, `validate.py`, `edit.py`) |
| **pydantic** | Schema validation throughout the pipeline |
| **LibreOffice** *(optional)* | Visual (pixel-diff) validation only. If absent, visual validation is dependency-skipped and structural validation still runs. |

Install the Python deps:

```powershell
pip install python-pptx pydantic
```

The entry-point scripts set their own `PYTHONPATH` (using `os.pathsep`, so it
is correct on Windows), so run them directly with `python` - no manual
`PYTHONPATH` or `cwd` setup is required.

---

## The three public entry-point commands

The canonical set of user-facing commands. Invoke them with absolute skill paths
so they work from any directory. Below, `<SKILL>` is
`C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts`.

### `generate.py` - render a deck

```powershell
python "<SKILL>\scripts\generate.py" outline.md -o deck.pptx --validate
```

Renders `outline.md` into `deck.pptx` using the bundled Inner Chapter template,
then runs validation. Options:

| Flag | Description |
|------|-------------|
| `input` *(positional)* | Input markdown outline (or layout JSON with `--from-layout`) |
| `-o`, `--output` *(required)* | Output `.pptx` path |
| `-t`, `--template` | Custom template `.pptx` (default: bundled Inner Chapter) |
| `-c`, `--config` | Custom template config `.json` (default: bundled Inner Chapter config) |
| `--validate` | Run validation after generating |
| `--layout-only` | Emit a layout plan JSON instead of a `.pptx` |
| `--from-layout` | Read a layout JSON instead of markdown |
| `--strict` | Treat warnings as errors |
| `--json` | Emit machine-readable JSON instead of a human report |
| `-v`, `--verbose` | Verbose logging |

Use your own template:

```powershell
python "<SKILL>\scripts\generate.py" outline.md -o deck.pptx `
    --template your-template.pptx --config your-template-config.json --validate
```

### `profile.py` - profile a custom template (one-time)

```powershell
python "<SKILL>\scripts\profile.py" your-template.pptx `
    --name your-template --generate-config --output-dir templates\
```

Profiles a `.pptx`, emits a layout catalog, and (with `--generate-config`)
generates the render config. Options:

| Flag | Description |
|------|-------------|
| `template` *(positional, optional)* | Path to the `.pptx` to profile |
| `-n`, `--name` | Template name slug |
| `-o`, `--output-dir` | Where to write artifacts (default: `.`) |
| `--generate-config` | Also generate the render config (`config.json`) |
| `--full` | Full detail catalog |
| `--use-cache` | Reuse a cached profile |
| `--clear-cache` | Clear the profile cache |
| `-v`, `--verbose` | Verbose logging |

For step-1 cataloging only (no config), you can also use `catalog.py`:

```powershell
python "<SKILL>\scripts\catalog.py" your-template.pptx --output-dir .
```

### `validate.py` - quality-check a deck

```powershell
python "<SKILL>\scripts\validate.py" deck.pptx
```

Runs structural validation (overflow, layout coverage, visual-type fit). With no
`--template`, it resolves the bundled Inner Chapter template by default.
Options:

| Flag | Description |
|------|-------------|
| `presentation` *(positional)* | The `.pptx` to validate |
| `-t`, `--template` | Template to validate against (default: bundled Inner Chapter) |
| `-r`, `--reference` | Reference deck for diffing |
| `-l`, `--layout-plan` | Layout plan to compare against |
| `--diff` | Produce a diff against a reference |
| `-o`, `--output` | Write the report to a file |
| `--json` | Machine-readable JSON report |
| `--strict` | Treat warnings as errors |
| `--no-parallel` | Disable parallel validation checks |
| `-v`, `--verbose` | Verbose logging |

A deck is **not done** until `validate.py` reports zero errors and no text
overflow.

### Companion commands (also bundled)

| Command | Use |
|---------|-----|
| `lint_hints.py slides.md --config <config.json>` | Step 2: lint `[HINT:]` markers against a catalog/config |
| `edit.py deck.pptx --inventory -o inv.json` then `--replace inv.json` | Small text fixes / reorders on an existing deck (< 30% of slides) |
| `generate_config.py --generate-ic-defaults --output config.json` | Regenerate the Inner Chapter default config |

---

## The bundled default template

```
<SKILL>\templates\inner-chapter.pptx        # the template
<SKILL>\templates\inner-chapter-config.json # its render config
```

The Inner Chapter template is bundled inside the skill and is the default for
both `generate.py` and `validate.py`. SHA-256 of the bundled template:

```
D9800CAA98BB5926595B55195BF47592B8DA50CEAE1896A32684B1706EA82B01
```

To use your own brand template instead, profile it once with `profile.py`
(above) or delegate to the **template-onboarder** subagent, then pass
`--template` / `--config` to `generate.py`. Full guide: `rules\bring-your-own-template.md`.

---

## Registered subagents (OpenCode Task-tool delegation)

This skill ships **three registered OpenCode subagents** at the global agent
path (`C:\Users\DaveWitkin\.config\opencode\agent\`). Invoke them
programmatically from a primary agent via the Task tool:

| Subagent | Invoke with | Use it to |
|----------|-------------|-----------|
| `pptx-outline-architect` | `Task(subagent_type: "pptx-outline-architect", prompt: "...")` | Turn raw material into a generation-ready `outline.md` with correct visual types |
| `pptx-template-onboarder` | `Task(subagent_type: "pptx-template-onboarder", prompt: "...")` | Onboard a user `.pptx` as a reusable, on-brand template (one-time) |
| `pptx-deck-qa` | `Task(subagent_type: "pptx-deck-qa", prompt: "...")` | Validate a deck and apply a surgical fix or recommend regeneration |

They chain as **architect -> `generate.py` -> QA**; for your own template, the
**onboarder** runs once up front.

Each registered agent uses `mode: subagent`, `hidden: true`, with
`permission: { edit: allow, bash: allow, task: { "*": deny } }` (the `task: deny`
prevents subagent recursion). Their `description:` fields are the activation
triggers the Task tool matches on.

### Session-restart caveat (important)

Newly registered subagents require an **OpenCode session restart** before the
Task tool can invoke them. OpenCode caches agent types at startup, so agents
registered during a running session are not yet Task-invokable in that session.

After a restart, test each subagent via the Task tool, e.g.:

```
Task(subagent_type: "pptx-outline-architect",
     prompt: "Make a 5-slide deck outline about Q1 strategy")
```

> The `opencode run --agent <name>` CLI subcommand returns "Session not found"
> for **all** agents (including pre-existing ones) in some CLI contexts - this
> is an environmental runtime quirk, not a frontmatter problem. No YAML/frontmatter
> parse errors occurred for any of the three agents. The Task-tool path (after a
> restart) is the supported invocation route.

The same restart caveat applies to **skill discovery**: `skill_find "powerpoint"`
will not surface `pptx-from-layouts` until the opencode-skillful plugin
re-indexes the vault, which happens at session startup.

---

## Known limitations

- **Visual (pixel-diff) validation requires LibreOffice.** If LibreOffice is not
  installed, visual validation is dependency-skipped; structural validation
  still runs and is sufficient for most checks.
- **Subagent invocation and skill discovery require a session restart** after
  first install/registration (see the caveat above). The scripts themselves are
  unaffected and work immediately via a direct `python` call.
- **Editing is limited to < 30% of slides.** For layout changes, added/removed
  slides, or larger churn, regenerate via `generate.py` rather than using
  `edit.py`.

---

## Quick start (copy-paste)

```powershell
$SKILL = "C:\Users\DaveWitkin\.opencode-lazy-vault\pptx-from-layouts"

# Render a deck from an outline (bundled template, validated)
python "$SKILL\scripts\generate.py" outline.md -o deck.pptx --validate

# Validate an existing deck
python "$SKILL\scripts\validate.py" deck.pptx

# Profile a custom template (one-time onboarding)
python "$SKILL\scripts\profile.py" your-template.pptx --name your-template --generate-config
```

---

## See also

- **`SKILL.md`** - the full author-facing skill instructions (visual types,
  typography markers, anti-patterns, the mandatory generation workflow).
- **`rules\`** - author-facing rules: `outline-format.md`, `visual-types.md`,
  `typography.md`, `columns.md`, `tables.md`, `editing.md`,
  `bring-your-own-template.md`, `decisions.md`.
- **`references\layouts.md`** - Inner Chapter layout indices.
- **`agents\`** - scrubbed reference copies of the source Claude agents (the
  authoritative OpenCode agents live at the global agent path).
- **`docs\ADR-001-registered-opencode-subagents.md`** - architectural decision
  record for the registered-subagent wiring.
- **`CHANGELOG.md`** - what changed in the OpenCode adaptation.
