# Script to list Windows Scheduled Tasks
# Usage: ./list_tasks.ps1 [optional-filter]

param (
    [string]$Filter = "*"
)

if ($Filter -eq "*") {
    Get-ScheduledTask | 
        Where-Object { $_.TaskPath -notmatch "^\Microsoft\Windows" } |
        Select-Object TaskName, State, Description, TaskPath |
        Format-Table -AutoSize
} else {
    Get-ScheduledTask | 
        Where-Object { $_.TaskName -like "*$Filter*" } |
        Select-Object TaskName, State, Description, TaskPath |
        Format-Table -AutoSize
}
