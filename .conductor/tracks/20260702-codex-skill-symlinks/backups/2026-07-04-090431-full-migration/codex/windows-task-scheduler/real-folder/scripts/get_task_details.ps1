# Script to get detailed info about a task
# Usage: ./get_task_details.ps1 "TaskName"

param (
    [Parameter(Mandatory=$true)]
    [string]$TaskName
)

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if (-not $task) {
    Write-Error "Task '$TaskName' not found."
    exit 1
}

Write-Output "--- Task Details ---"
Write-Output "Name:        $($task.TaskName)"
Write-Output "State:       $($task.State)"
Write-Output "Description: $($task.Description)"
Write-Output "Author:      $($task.Author)"
Write-Output "Path:        $($task.TaskPath)"

Write-Output "`n--- Triggers ---"
foreach ($trig in $task.Triggers) {
    $type = $trig.GetType().Name
    $start = $trig.StartBoundary
    Write-Output "- Type: $type"
    Write-Output "  Start: $start"
    if ($trig.DaysOfWeek) { Write-Output "  Days: $($trig.DaysOfWeek)" }
    if ($trig.DaysInterval) { Write-Output "  Interval: Every $($trig.DaysInterval) day(s)" }
}

Write-Output "`n--- Actions ---"
foreach ($act in $task.Actions) {
    Write-Output "- Execute: $($act.Execute)"
    Write-Output "  Arguments: $($act.Arguments)"
    Write-Output "  WorkingDir: $($act.WorkingDirectory)"
}

Write-Output "`n--- Run Info ---"
Write-Output "User: $($task.Principal.UserId)"
Write-Output "RunLevel: $($task.Principal.RunLevel)"
Write-Output "LogonType: $($task.Principal.LogonType)"
