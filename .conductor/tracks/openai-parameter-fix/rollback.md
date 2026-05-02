# Rollback Commands: openai-parameter-fix

## Config Restore
```powershell
Copy-Item 'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc.backup-20260428-094622-openai-fix' 'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc' -Force
```

## Cache Restore
```powershell
Rename-Item 'C:\Users\DaveWitkin\.cache\opencode-cache-backup-20260428-094635' 'opencode'
```

## Verify Rollback
```powershell
# Confirm config file date
Get-Item 'C:\Users\DaveWitkin\.config\opencode\opencode.jsonc' | Select-Object Name,LastWriteTime,Length

# Confirm cache restored
Test-Path 'C:\Users\DaveWitkin\.cache\opencode'
```
