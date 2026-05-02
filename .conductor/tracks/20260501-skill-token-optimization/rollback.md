# Rollback Procedure

Use this procedure if `@zenobius/opencode-skillful` causes startup errors, tool errors, missing skills, or unacceptable workflow regressions.

## Restore OpenCode Config

```powershell
Copy-Item "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.bak-20260501-skillful-poc" "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc" -Force
```

Verify:

```powershell
Test-Path "C:\Users\DaveWitkin\.config\opencode\opencode.jsonc"
```

Expected result: `True`.

## Restore Skill Directories From Backup

Only run these commands if the backup files exist in `C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501`.

```powershell
Remove-Item "C:\Users\DaveWitkin\.config\opencode\skill" -Recurse -Force
Remove-Item "C:\Users\DaveWitkin\.config\opencode\skills" -Recurse -Force
Remove-Item "C:\Users\DaveWitkin\.agents\skills" -Recurse -Force

Expand-Archive "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501\skill.zip" "C:\Users\DaveWitkin\.config\opencode" -Force
Expand-Archive "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501\skills.zip" "C:\Users\DaveWitkin\.config\opencode" -Force
Expand-Archive "C:\Users\DaveWitkin\.config\opencode\backups\skill-token-optimization-20260501\agents-skills.zip" "C:\Users\DaveWitkin\.agents" -Force
```

Verify restored native skills:

```powershell
Test-Path "C:\Users\DaveWitkin\.config\opencode\skill\calendar-today\SKILL.md"
Test-Path "C:\Users\DaveWitkin\.config\opencode\skill\conductor\SKILL.md"
```

Expected result: both commands return `True`.

## Remove Skillful Config

```powershell
Remove-Item "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json" -Force
```

Verify:

```powershell
Test-Path "C:\Users\DaveWitkin\.config\opencode\.opencode-skillful.json"
```

Expected result: `False`.

## Restart OpenCode

Manual action: close all OpenCode sessions, then start a fresh session from `C:\development\opencode`.

Expected result: native `<available_skills>` returns to the pre-migration skill list.
