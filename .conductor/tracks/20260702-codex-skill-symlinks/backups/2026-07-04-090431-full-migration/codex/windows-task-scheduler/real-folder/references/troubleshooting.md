# Troubleshooting

## Common Errors

### Access Denied

- Likely cause: requires elevated privileges or different Run As user.
- Fix: run PowerShell as Administrator; confirm task RunLevel/user choice.

### Command Not Found

- Likely cause: executable path is wrong or not in PATH.
- Fix: use a fully qualified path (or run via `powershell.exe -File ...`).

### Trigger Not Found / Invalid Trigger

- Likely cause: trigger parameters are incompatible (time format, repetition settings).
- Fix: create the trigger with `New-ScheduledTaskTrigger` first, inspect it, then register.

### Invalid Task Name

- Likely cause: unsupported characters.
- Fix: use letters/numbers/spaces/hyphens and keep it stable over time.
