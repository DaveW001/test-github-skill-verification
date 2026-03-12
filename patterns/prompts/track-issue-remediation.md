# Track Issue Remediation

## Prompt Template

```text
Remediate the open issues in {{track_path}} using {{priority_order}}.
Update conductor artifacts and include validation results from {{test_commands}}.
```

## Variables

- `track_path`: Conductor track directory that owns the backlog.
- `priority_order`: Expected execution order for backlog items.
- `test_commands`: Commands used to verify changes.

## Example Input

Track path: .conductor/tracks/20260311-osgrep-disable-and-root-cause
Priority order: high to low
Test commands: python scripts/validate-prompt-patterns.py

## Example Output Shape

- Completed item: <item name>
- Updated files:
  - <file path>
- Validation:
  - <command> -> <result>
- Remaining risks: <risk summary>
