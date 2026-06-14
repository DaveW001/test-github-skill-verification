# Plan: ClickUp Skill Windows UTF-8 Encoding Fix

## Phase 0: Setup & Preconditions

**Objective:** Verify the environment, locate all relevant files, and confirm the encoding issue is reproducible.

- [x] 0.1 Confirm the ClickUp skill scripts directory and common.py exist at the expected path
  - Command: `Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\scripts\common.py"`
  - Expected: `True`
  - Fallback: If `False`, check these alternative paths in order:
    1. `Test-Path "C:\Users\DaveWitkin\.config\opencode\skill\clickup\scripts\common.py"`
    2. `Test-Path "C:\Users\DaveWitkin\.codex\skills\clickup\scripts\common.py"`
    3. If still not found, run: `Get-ChildItem -Path "C:\Users\DaveWitkin" -Depth 5 -Filter "common.py" -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'clickup' } | Select-Object -First 1 FullName`
  - Once found, update the variable `$SKILL_ROOT` to the actual path for all subsequent tasks.

- [x] 0.2 Confirm the external repo exists at `C:\development\cursor-clickup-mcp\`
  - Command: `Test-Path "C:\development\cursor-clickup-mcp\scripts\clickup_client.py"`
  - Expected: `True`
  - Fallback: If not found, check `C:\development\cursor-clickup-mcp\` exists at all: `Test-Path "C:\development\cursor-clickup-mcp"`. If it does not exist, the preflight in Phase 2 will fail — stop and report the missing repo.

- [x] 0.3 List all Python scripts that import common.py (for awareness only)
  - Command: `Select-String -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\scripts\*.py" -Pattern "from common import" | Select-Object Filename`
  - Expected: Multiple filenames listed (create_task.py, update_task.py, preflight.py, create_meeting_notes.py, prioritize.py, etc.)
  - Note: This list is for information only. No action needed — all these scripts will automatically benefit from the common.py fix.
  - Verification: Count the results — expect at least 5 scripts.

- [x] 0.4 Confirm Python version supports `sys.stdout.reconfigure()` (Python 3.7+)
  - Command: `python --version`
  - Expected: Output contains `Python 3.7` or higher (e.g., `Python 3.11.2`)
  - Fallback: If Python < 3.7, STOP and report: "Python 3.7+ required for sys.stdout.reconfigure()". Do not proceed.

**Exit criteria:** `common.py` found at a known path, external repo exists, Python 3.7+ confirmed.

---

## Phase 1: Implement UTF-8 Encoding Fix in common.py

**Objective:** Add a Windows-specific UTF-8 encoding configuration to `common.py` so all scripts that import it get correct Unicode output.

- [x] 1.1 Read the current `common.py` file to confirm its structure
  - File to read: `C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\scripts\common.py`
  - Command: `Get-Content "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\scripts\common.py" -TotalCount 10`
  - Expected: The first 10 lines contain the docstring, then `import sys`, then `import os`, then `from pathlib import Path`.
  - Verification: Confirm the output contains `import sys` and `import os` on consecutive lines near the top.

- [x] 1.2 Add the UTF-8 encoding block to `common.py`
  - File to modify: `C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\scripts\common.py`
  - **Exact edit:** Replace this existing text (oldString):

```python
"""
Common utilities for ClickUp skill scripts.
Handles path resolution and external repo discovery.
"""

import sys
import os
from pathlib import Path
```

  - With this new text (newString):

```python
"""
Common utilities for ClickUp skill scripts.
Handles path resolution and external repo discovery.
"""

import sys
import os

# Ensure UTF-8 output on Windows (default console encoding is cp1252)
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass

from pathlib import Path
```

  - How to perform the edit: Read the full file first, then use `Set-Content` to write the modified content back. Do NOT use partial string replacement that could corrupt the file.
  - The block must be placed after `import sys` and `import os` and before `from pathlib import Path`.

- [x] 1.3 Verify the edit was applied correctly
  - Command: `Select-String -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\scripts\common.py" -Pattern "reconfigure" -Context 2`
  - Expected: Output shows both `sys.stdout.reconfigure(encoding='utf-8')` and `sys.stderr.reconfigure(encoding='utf-8')` near the top of the file.
  - Also verify syntax is valid: `python -m py_compile "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\scripts\common.py"`
  - Expected: No output (success). If errors appear, the edit corrupted the file — restore from backup and retry 1.2.

**Exit criteria:** `common.py` contains the UTF-8 encoding block, `py_compile` passes with no errors.

---

## Phase 2: Smoke Test the Fix

**Objective:** Verify the fix works by running scripts with Unicode input, then clean up test artifacts.

- [x] 2.1 Run preflight to confirm scripts still load correctly
  - Working directory: `C:\Users\DaveWitkin\.opencode-lazy-vault\clickup`
  - Command: `cd "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup"; python scripts/preflight.py`
  - Expected: `[OK] Skill root`, `[OK] Host mount`, `[OK] External repo found`, `[OK] ClickUp client initialized` — all with no errors.
  - Fallback: If preflight fails with import errors or syntax errors, check that the edit in Phase 1 did not break Python syntax. Run `python -m py_compile scripts/common.py` to check for syntax errors. If syntax errors exist, restore `common.py` from the original content and retry Phase 1.

- [x] 2.2 Create a baseline test task (no emoji, to confirm the script still works normally)
  - Working directory: `C:\Users\DaveWitkin\.opencode-lazy-vault\clickup`
  - Command: `cd "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup"; python scripts/create_task.py --name "Baseline UTF-8 Test" --description "Smoke test for basic task creation" --priority 4`
  - Expected: `Task created successfully!` with a task ID and URL. No errors.
  - Important: This creates a real task in Dave's ClickUp Inbox. Capture the task ID from the output (it appears after `ID: `).
  - Verification: The output contains `ID:` followed by an alphanumeric string (e.g., `868abc123`). Save this ID as `$BASELINE_TASK_ID`.

- [x] 2.3 Create a test task with Unicode characters in the description (the actual fix verification)
  - Working directory: `C:\Users\DaveWitkin\.opencode-lazy-vault\clickup`
  - Command: `cd "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup"; python scripts/create_task.py --name "UTF-8 Test Task" --description "Testing Unicode: test-value" --priority 4`
  - Expected: `Task created successfully!` with a task ID and URL. No `UnicodeEncodeError`.
  - Important: Capture the task ID from the output (after `ID: `). Save as `$UNICODE_TASK_ID`.
  - Fallback: If this fails with `UnicodeEncodeError`, the fix in `common.py` is not working. Check:
    1. Did `common.py` get imported? (Is the script using the updated version?)
    2. Is the Python version 3.7+?
    3. Try setting the env var first: `$env:PYTHONIOENCODING='utf-8'; python scripts/create_task.py ...`
- [x] 2.4 Clean up both test tasks created in steps 2.2 and 2.3
  - For `$BASELINE_TASK_ID`: `cd "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup"; python scripts/update_task.py $BASELINE_TASK_ID --status done`
  - For `$UNICODE_TASK_ID`: `cd "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup"; python scripts/update_task.py $UNICODE_TASK_ID --status done`
  - Expected for each: `Task updated successfully!`
  - Fallback: If a task ID was not captured (e.g., the create command failed before printing the ID), skip cleanup for that task and note it in the report. Do not let a missing task ID block the rest of the plan.

**Exit criteria:** Preflight passes, at least one task creation succeeds without UnicodeEncodeError, test tasks are cleaned up.

---

## Phase 3: Update Troubleshooting Documentation

**Objective:** Document this issue and its fix so future users and agents can self-diagnose.

- [x] 3.1 Read the current troubleshooting reference to confirm it exists and find the insertion point
  - File to read: `C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\references\08-troubleshooting.md`
  - Command: `Get-Content "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\references\08-troubleshooting.md" -TotalCount 15`
  - Expected: File exists and starts with `# Troubleshooting: Create/Update Failures (Targeted)`.
  - Verification: Confirm the output contains `## Problem Pattern We Hit` on a line by itself.

- [x] 3.2 Add the encoding troubleshooting section to `08-troubleshooting.md`
  - File to modify: `C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\references\08-troubleshooting.md`
  - **Exact edit:** Replace this existing text (oldString):

```markdown
Use this only when ClickUp task create/update fails. Keep this flow short and deterministic.

## Problem Pattern We Hit
```

  - With this new text (newString):

```markdown
Use this only when ClickUp task create/update fails. Keep this flow short and deterministic.

## UnicodeEncodeError on Windows (Emoji/Special Characters)

**Symptom:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f3a4' in position 15: character maps to <undefined>
```

**Cause:**
Windows default console encoding is `cp1252`, which cannot represent emojis or many Unicode characters. Python's `sys.stdout` inherits this encoding.

**Fix:**
The skill's `common.py` module now configures UTF-8 encoding for stdout/stderr on Windows. This fix is applied automatically when any skill script runs.

**If the error persists:**
1. Verify `common.py` contains the `sys.stdout.reconfigure(encoding='utf-8')` block near the top.
2. Check that the script imports `common.py` before any `click.echo()` or `print()` calls.
3. As a workaround, set the environment variable before running: `$env:PYTHONIOENCODING='utf-8'`
4. Avoid emojis in task names as a last resort.

## Problem Pattern We Hit
```

  - How to perform the edit: Read the full file, then use `Set-Content` to write the modified content back. Do NOT use partial string replacement that could corrupt the file.

- [x] 3.3 Verify the documentation was added correctly
  - Command: `Select-String -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\references\08-troubleshooting.md" -Pattern "UnicodeEncodeError"`
  - Expected: Output shows at least one match, confirming the section was added.
  - Also verify the section structure: `Select-String -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\references\08-troubleshooting.md" -Pattern "## Problem Pattern We Hit"`
  - Expected: Match found — confirming the new section was inserted before the existing content, not replacing it.

**Exit criteria:** Troubleshooting doc contains the encoding issue section, and the original `## Problem Pattern We Hit` section still exists below it.

---

## Final Phase: Validation & Handover

**Objective:** Confirm all changes are correct and the track is complete.

- [x] F.1 Run the full preflight check one final time
  - Working directory: `C:\Users\DaveWitkin\.opencode-lazy-vault\clickup`
  - Command: `cd "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup"; python scripts/preflight.py`
  - Expected: All lines start with `[OK]`. No `[WARN]` or `[ERROR]`.

- [x] F.2 Verify `common.py` has the encoding fix
  - Command: `Select-String -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\scripts\common.py" -Pattern "reconfigure" | Measure-Object`
  - Expected: `Count` is at least 2 (one for stdout, one for stderr).

- [x] F.3 Verify troubleshooting doc is updated
  - Command: `Select-String -Path "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\references\08-troubleshooting.md" -Pattern "UnicodeEncodeError" | Measure-Object`
  - Expected: `Count` is at least 1.

- [x] F.4 Update the conductor track metadata to mark completion
  - File to modify: `C:\development\opencode\.conductor\tracks\20260511-clickup-windows-encoding-fix\metadata.json`
  - Read the current file: `Get-Content "C:\development\opencode\.conductor\tracks\20260511-clickup-windows-encoding-fix\metadata.json" -Raw`
  - Make these exact changes:
    1. Change `"status": "ready"` to `"status": "completed"`
    2. Change `"completed": null` to `"completed": "2026-05-11"`
    3. Change `"completedTasks": 0` to `"completedTasks": 14`
    4. Change `"percentage": 0` to `"percentage": 100`
    5. In the `phases` array, change every `"status": "pending"` to `"status": "completed"` and every `"completion": 0` to `"completion": 100`
  - Write the modified content back to the file.
  - Verification: `Select-String -Path "C:\development\opencode\.conductor\tracks\20260511-clickup-windows-encoding-fix\metadata.json" -Pattern '"status": "completed"' | Measure-Object`
  - Expected: `Count` is at least 1.

**Exit criteria:** Preflight passes, common.py has 2+ reconfigure references, troubleshooting doc has UnicodeEncodeError section, metadata shows completed status.

---

## Execution Readiness Checklist

| # | Standard | Status |
|---|----------|--------|
| 1 | Atomic tasks - one clear action per checkbox | Ready |
| 2 | Exact file paths - full paths specified | Ready |
| 3 | Explicit commands - verbatim terminal commands | Ready |
| 4 | Clear ordering - prerequisites first | Ready |
| 5 | Verification per step - concrete validation | Ready |
| 6 | No assumed context - self-contained instructions | Ready |
| 7 | Concrete examples - inline code snippets | Ready |
| 8 | Error recovery - fallback for common failures | Ready |

## Top 3 Implementation Risks + Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `sys.stdout.reconfigure()` fails on redirected/piped output | Medium | Wrapped in `try/except`; fallback env var documented in troubleshooting |
| Edit to `common.py` introduces syntax error breaking all scripts | High | `py_compile` check in 1.3 before any smoke test; preflight in 2.1 as gate |
| Skill root path differs between host apps | Low | Phase 0.1 checks 3 known paths before falling back to search |

## First Task to Execute

**Task 0.1:** Confirm the ClickUp skill scripts directory and `common.py` exist.

```powershell
Test-Path "C:\Users\DaveWitkin\.opencode-lazy-vault\clickup\scripts\common.py"
```

If `True`, proceed to 0.2. If `False`, run the fallback checks in 0.1 in order and update all subsequent file paths to use the discovered location.

