# PowerShell Recipes (ScheduledTasks)

These recipes assume PowerShell's `ScheduledTasks` module is available.

## Create a Task (Daily)

```powershell
$taskName = "TaskName"
$description = "What it does. Why it exists. Runs daily at 7:30 AM. See C:/docs/task-notes.md"

$action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File C:/scripts/do-work.ps1" `
  -WorkingDirectory "C:/scripts"

$trigger = New-ScheduledTaskTrigger -Daily -At "7:30AM"

Register-ScheduledTask `
  -TaskName $taskName `
  -Action $action `
  -Trigger $trigger `
  -Description $description `
  -RunLevel Highest
```

## Modify a Task (Update Trigger + Description)

```powershell
$task = Get-ScheduledTask -TaskName "TaskName"

$task.Triggers = New-ScheduledTaskTrigger -Daily -At "8:00AM"
$task.Description = "Updated purpose. Runs daily at 8:00 AM. See C:/docs/task-notes.md"

Set-ScheduledTask -InputObject $task
```

## Trigger Patterns

### Weekdays Only

```powershell
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At "9:00AM"
```

### Every X Days

```powershell
$trigger = New-ScheduledTaskTrigger -Daily -DaysInterval 7 -At "2:00AM"
```

### Every 8 Hours (Repeating)

```powershell
$trigger = New-ScheduledTaskTrigger -Once -At "09:00AM" `
  -RepetitionInterval (New-TimeSpan -Hours 8) `
  -RepetitionDuration ([TimeSpan]::MaxValue)
```

### At Startup

```powershell
$trigger = New-ScheduledTaskTrigger -AtStartup
```

### At Logon

```powershell
$trigger = New-ScheduledTaskTrigger -AtLogOn
```

## Useful Commands

### List Tasks (Name, State, Description)

```powershell
Get-ScheduledTask | Select-Object TaskName, State, Description | Format-Table -AutoSize
```

### Get Task Details

```powershell
Get-ScheduledTask -TaskName "TaskName" | Select-Object TaskName, Description, Actions, Triggers
```

### Run Task Manually

```powershell
Start-ScheduledTask -TaskName "TaskName"
```

### Disable / Enable

```powershell
Disable-ScheduledTask -TaskName "TaskName"
Enable-ScheduledTask -TaskName "TaskName"
```

### Delete

```powershell
Unregister-ScheduledTask -TaskName "TaskName" -Confirm:$false
```

### History / Last Result

```powershell
Get-ScheduledTaskInfo -TaskName "TaskName" | Select-Object LastRunTime, NextRunTime, LastTaskResult
```
