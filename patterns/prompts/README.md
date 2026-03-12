# Prompt Pattern Library

This directory stores reusable prompt patterns for recurring task shapes.

## How to add a pattern

1. Copy `TEMPLATE.md` to a new markdown file.
2. Name the file using a slug derived from the title.
3. Fill all required sections.

## Validation

Run:

```bash
python scripts/validate-prompt-patterns.py
```

The validator checks:

- title/filename slug consistency
- required sections
- at least one `{{variable}}` in `Prompt Template`
- at least one bullet in `Variables`
- non-empty `Example Input` and `Example Output Shape`
