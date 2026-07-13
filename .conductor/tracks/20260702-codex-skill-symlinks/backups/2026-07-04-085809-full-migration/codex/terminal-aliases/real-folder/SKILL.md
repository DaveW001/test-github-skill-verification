---
name: terminal-aliases
description: Add or update terminal aliases and folder shortcuts across PowerShell 5.x, PowerShell 7.x, and Git Bash.
compatibility: OpenCode skills system; user-level skill for shell profiles on Windows.
---

# Terminal Aliases

Use this skill when the user asks for a new terminal alias, terminal function, PowerShell alias, PowerShell function, or shortcut command for a frequently used folder. It covers PowerShell 5.x, PowerShell 7.x, and Git Bash.

## Activation Examples

Use this skill for prompts like:
- "Add a new terminal alias for a folder"
- "Create a PowerShell function shortcut"
- "Add a new terminal function"
- "Create a new shortcut for AI in the terminal"
- "Add a Git Bash alias for a directory"

## Instructions

1. Identify requested shortcut name and target path.
2. Update PowerShell shared profile at `C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\PowerShell\SharedProfile.ps1` with a `function <name> { Set-Location "<path>" }`.
3. Update Git Bash profile at `C:\Users\DaveWitkin\.bashrc` with `alias <name>="cd /c/..."` using Git Bash path format.
4. Update `Test-OcSetup` in the PowerShell profile and `oc_test` in `.bashrc` to assert the directory exists.
5. If needed, add or update documentation at `C:\development\opencode\docs\guides\terminal-aliases-and-shortcuts.md`.
6. Run tests:
   - PowerShell 5.x: `. "C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\PowerShell\SharedProfile.ps1"; Test-OcSetup`
   - PowerShell 7.x: `. "C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\PowerShell\SharedProfile.ps1"; Test-OcSetup`
   - Git Bash: `source ~/.bashrc && oc_test`

## Guardrails

- Do not remove existing aliases or functions unless explicitly asked.
- Keep shortcut names short and consistent (e.g., `cdev`, `cmark`).
- Ensure paths exist before claiming success.

## Output Expectations

- Confirm the aliases/functions added and the file paths edited.
- Report the test results for each shell.
