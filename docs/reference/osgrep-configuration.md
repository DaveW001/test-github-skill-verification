# Osgrep Configuration Reference

## Current Policy

- Osgrep is disabled-by-default for normal OpenCode workflows while reliability work remains active.
- Prefer `grep`, `glob`, and targeted `Read` for routine navigation.
- Use osgrep only for controlled debugging and reproduction work.

## CLI Health Commands

```bash
osgrep --help
osgrep doctor
```

## Debug Wrapper

Use the local wrapper when capturing reproducible logs:

```bash
python scripts/utils/osgrep_debug_wrapper.py --label help-check -- -- --help
python scripts/utils/osgrep_debug_wrapper.py --cleanup-stale --label index-check -- -- index
```

## Snapshot Utility (Windows)

The wrapper calls `scripts/utils/osgrep_process_snapshot.ps1` on timeout.
You can also run it directly:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/utils/osgrep_process_snapshot.ps1 -Label manual -OutputDir logs/osgrep-debug/manual -TargetCwd C:/development/opencode
```

## Re-enable Prerequisite

Before considering re-enable, complete the checklist in:

- `docs/troubleshooting/active/osgrep-cli-only-re-enable-checklist.md`
