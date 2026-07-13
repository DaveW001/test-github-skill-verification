# Due Dates

Prefer human-friendly due date options.

## Rules

- If user says "due tomorrow" -> use `--due-tomorrow`
- If user says "due tomorrow morning" -> use `--due-tomorrow-morning`
- If user gives relative time -> use `--due-relative "..."`
- Avoid `--due-date` unless the user provides an explicit Unix timestamp (ms) or you are instructed to compute it.

## Examples

Due tomorrow:

```bash
python scripts/create_task.py --name "Task" --due-tomorrow
```

Due in 2 hours:

```bash
python scripts/create_task.py --name "Task" --due-relative "2 hours"
```
