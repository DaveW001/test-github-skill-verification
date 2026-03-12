# Phase 4/5 Results (2026-03-12)

## Test Matrix Additions

### A) Stale worker cleanup before launch

- Command: `python scripts/utils/osgrep_debug_wrapper.py --label phase4-small-index --cleanup-stale --cwd C:/development/opencode/tmp/osgrep-small-repro -- -- index`
- Log: `logs/osgrep-debug/20260312-112251-phase4-small-index/result.json`
- Result:
  - stale cleanup path executed
  - no stale `osgrep-nodejs-helper.exe` found on that run
  - indexed successfully with exit code 0

### B) Quoted-path and spaced-path handling

- Command: `python scripts/utils/osgrep_debug_wrapper.py --label phase4-spaced-search --cwd C:/development/opencode/tmp/osgrep path repro -- -- search "folder creation"`
- Log: `logs/osgrep-debug/20260312-112252-phase4-spaced-search/result.json`
- Result:
  - command completed with exit code 0
  - returned matches from repo in path containing spaces

### C) Invalid cwd handling

- Command: `python scripts/utils/osgrep_debug_wrapper.py --label phase4-invalid-cwd --cwd C:/development/opencode/tmp/does-not-exist -- -- --help`
- Log: `logs/osgrep-debug/20260312-112253-phase4-invalid-cwd/result.json`
- Result:
  - wrapper now fails fast with explicit error
  - no subprocess launch attempt against non-existent cwd

### D) Antivirus exclusion check

- Command: `powershell -NoProfile -Command 'try { $p = Get-MpPreference; $p.ExclusionPath | Out-String } catch { Write-Output $_.Exception.Message; exit 1 }'`
- Result:
  - current shell is non-admin
  - Defender exclusion paths could not be enumerated (`Must be an administrator to view exclusions`)
  - test recorded as environment-constrained, not blocked by osgrep behavior

## Root Cause Narrowing (Phase 5)

- Primary failure mode remains MCP/service startup lifecycle on Windows, not direct CLI indexing/search in tested repos.
- Additional Phase 4 runs continue to support CLI-only viability for controlled use.

## Fix Owner / Path Decision

1. **OpenCode local fix path (owner: local repo / Build):**
   - keep osgrep disabled-by-default for routine workflows
   - use CLI-only debug wrapper for controlled reintroduction
   - keep stale-worker cleanup and timeout snapshots available

2. **Upstream osgrep fix path (owner: osgrep maintainers):**
   - investigate MCP/server startup readiness and lifecycle behavior on Windows
   - validate worker shutdown/readiness sequencing in service mode

## Patch / Issue Draft

- Local patch delivered in this session:
  - `scripts/utils/osgrep_debug_wrapper.py`
  - `scripts/utils/osgrep_process_snapshot.ps1`
  - docs updates for active troubleshooting and re-enable checklist
- Upstream issue draft should include:
  - evidence links from `logs/osgrep-debug/*phase4*`
  - contrast between CLI pass results and MCP timeout behavior
  - Windows-specific environment details and process snapshot output
