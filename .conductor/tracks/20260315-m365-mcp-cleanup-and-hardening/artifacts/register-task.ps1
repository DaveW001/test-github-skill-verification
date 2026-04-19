$taskName = 'OpenCode-M365-MCP-Removal-Check'
$scriptPath = 'C:\development\opencode\.conductor\tracks\20260315-m365-mcp-cleanup-and-hardening\artifacts\restart-reminder.ps1'
$userId = "$env:USERDOMAIN\$env:USERNAME"

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -AtLogon
$principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Description 'Creates a reminder file in the opencode workspace to verify M365 MCP removal after restart.' -Force
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName, State
