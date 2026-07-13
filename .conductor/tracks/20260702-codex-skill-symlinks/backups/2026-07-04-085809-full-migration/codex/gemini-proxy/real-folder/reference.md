> **Note:** This reference still mentions legacy scheduled task names (`GeminiAPIKeyRotator`, `GeminiProxyMonitor`). These tasks have been removed. Scheduled operations are now managed by the OpenCode scheduler. See `gemini-proxy-source-of-truth.md` for current task names.
# Gemini Proxy - Detailed Reference

Advanced commands, procedures, and troubleshooting details for the Gemini API Key Rotator Proxy.

## Complete Command Reference

### Process Management

```powershell
# Get detailed process information
$pid = Get-Content C:/Users/DaveWitkin/.local/gemini-proxy/proxy.pid
Get-Process -Id $pid | Select-Object Name, Id, StartTime, CPU, WorkingSet, PagedMemorySize

# Check if specific port is listening
Test-NetConnection -ComputerName 127.0.0.1 -Port 8000

# Find what's using port 8000
netstat -ano | findstr :8000
Get-Process -Id (netstat -ano | findstr :8000 | ForEach-Object { $_.Split()[-1] } | Select-Object -First 1)
```

### Windows Task Scheduler Deep Dive

```powershell
# Get all Gemini-related tasks
Get-ScheduledTask -TaskName "Gemini*" | Format-Table TaskName, State, Author, Date -AutoSize

# Get detailed task info
Get-ScheduledTask -TaskName "GeminiAPIKeyRotator" | 
    Select-Object -ExpandProperty Triggers | 
    Format-List *

# View task history (requires elevated PowerShell)
Get-ScheduledTaskInfo -TaskName "GeminiAPIKeyRotator"
Get-ScheduledTaskInfo -TaskName "GeminiProxyMonitor"

# Disable a task temporarily
Disable-ScheduledTask -TaskName "GeminiProxyMonitor"

# Re-enable a task
Enable-ScheduledTask -TaskName "GeminiProxyMonitor"

# Run task immediately (for testing)
Start-ScheduledTask -TaskName "GeminiAPIKeyRotator"

# Stop a running task
Stop-ScheduledTask -TaskName "GeminiAPIKeyRotator"

# Export task configuration (backup)
Export-ScheduledTask -TaskName "GeminiAPIKeyRotator" | Out-File C:/temp/gemini-proxy-task-backup.xml
```

### Log Analysis

```powershell
# Search for errors in proxy logs
Select-String -Path C:/Users/DaveWitkin/.local/gemini-proxy/logs/proxy.log -Pattern "ERROR|Exception|Failed"

# Count requests by key (basic log parsing)
Select-String -Path C:/Users/DaveWitkin/.local/gemini-proxy/logs/proxy.log -Pattern "Routing to key" | 
    Group-Object { ($_ -split "key ")[1] } | 
    Select-Object Name, Count | 
    Sort-Object Count -Descending

# Find last restart time
Select-String -Path C:/Users/DaveWitkin/.local/gemini-proxy/logs/proxy.log -Pattern "Proxy started|Starting Gemini" | Select-Object -Last 5

# Monitor log in real-time with filtering
Get-Content C:/Users/DaveWitkin/.local/gemini-proxy/logs/proxy.log -Wait | Where-Object { $_ -match "ERROR|WARN" }
```

### API Key Management Procedures

#### Adding New Keys

1. **Obtain new API key from Google AI Studio**: https://aistudio.google.com/app/apikey
2. **Edit the keys file**:
   ```powershell
   notepad C:/Users/DaveWitkin/.local/gemini-proxy/api_keys.txt
   ```
3. **Add key on new line** (one key per line):
   ```
   AIzaSyExistingKey1
   AIzaSyExistingKey2
   AIzaSyNewKey3      # <-- Add here
   ```
4. **Save and reload** (no restart needed):
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/reload-keys" -Method POST -Headers @{"x-proxy-admin"="changeme_local_only"}
   ```
5. **Verify key count increased**:
   ```powershell
   (Invoke-RestMethod "http://127.0.0.1:8000/status").key_count
   ```

#### Removing Keys

1. **Edit the keys file**:
   ```powershell
   notepad C:/Users/DaveWitkin/.local/gemini-proxy/api_keys.txt
   ```
2. **Remove the line** with the key to delete
3. **Save and reload**:
   ```powershell
   Invoke-RestMethod -Uri "http://127.0.0.1:8000/reload-keys" -Method POST -Headers @{"x-proxy-admin"="changeme_local_only"}
   ```

#### Testing Key Health

```powershell
# Check all keys at once
Invoke-RestMethod -Uri "http://127.0.0.1:8000/status" -Method GET | Select-Object -ExpandProperty keys | Format-Table

# Test individual key against Google API directly
$testKey = "AIzaSyYourKeyHere"
Invoke-RestMethod -Uri "https://generativelanguage.googleapis.com/v1beta/models?key=$testKey" -Method GET
```

### Configuration Management

#### View Current OpenCode Configuration

```powershell
# Check if proxy is configured
Get-Content C:/Users/DaveWitkin/.config/opencode/opencode.jsonc | Select-String -Pattern "baseURL|gemini|8000" -Context 2

# Verify baseURL points to proxy
$config = Get-Content C:/Users/DaveWitkin/.config/opencode/opencode.jsonc | ConvertFrom-Json
$config.providers.google.baseURL
```

#### Update Admin Token (Advanced)

⚠️ **Warning**: Requires editing main.py and restarting proxy.

1. **Edit main.py**:
   ```powershell
   code C:/Users/DaveWitkin/.local/gemini-proxy/main.py
   ```
2. **Find line**: `ADMIN_TOKEN = "changeme_local_only"`
3. **Change to new token**
4. **Restart proxy**:
   ```powershell
   cd C:/Users/DaveWitkin/.local/gemini-proxy; ./stop-proxy.ps1; Start-Sleep 2; ./start-proxy-background.ps1
   ```

### Health Check Automation

```powershell
# Comprehensive health check function
function Test-GeminiProxy {
    $results = @{}
    
    # Check process
    try {
        $pid = Get-Content C:/Users/DaveWitkin/.local/gemini-proxy/proxy.pid -ErrorAction Stop
        $proc = Get-Process -Id $pid -ErrorAction Stop
        $results.Process = "Running (PID: $pid, $($proc.WorkingSet/1MB) MB RAM)"
    } catch {
        $results.Process = "NOT RUNNING or PID file missing"
    }
    
    # Check port
    try {
        $connection = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue
        $results.Port = if ($connection.TcpTestSucceeded) { "Listening" } else { "NOT RESPONDING" }
    } catch {
        $results.Port = "ERROR: $_"
    }
    
    # Check admin endpoint
    try {
        $status = Invoke-RestMethod -Uri "http://127.0.0.1:8000/status" -Method GET -Headers @{"x-proxy-admin"="changeme_local_only"} -TimeoutSec 5
        $results.Keys = "$($status.key_count) total, $($status.healthy_keys) healthy"
        $results.Uptime = $status.uptime
    } catch {
        $results.AdminEndpoint = "ERROR: $_"
    }
    
    # Check tasks
    try {
        $mainTask = Get-ScheduledTask -TaskName "GeminiAPIKeyRotator" -ErrorAction Stop
        $monitorTask = Get-ScheduledTask -TaskName "GeminiProxyMonitor" -ErrorAction Stop
        $results.ScheduledTasks = "Main: $($mainTask.State), Monitor: $($monitorTask.State)"
    } catch {
        $results.ScheduledTasks = "ERROR: $_"
    }
    
    return $results | Format-Table -AutoSize
}

# Run health check
Test-GeminiProxy
```

## Troubleshooting Scenarios

### Scenario 1: Proxy Starts But Returns 500 Errors

**Symptoms**: Proxy process running, but requests fail with 500 errors.

**Diagnosis**:
```powershell
# Check logs for key errors
Get-Content C:/Users/DaveWitkin/.local/gemini-proxy/logs/proxy.log -Tail 20 | Select-String "500|Error|Exception"

# Verify keys are valid
Invoke-RestMethod "http://127.0.0.1:8000/status" | Select-Object -ExpandProperty keys
```

**Solutions**:
1. Check if keys are valid (not expired/revoked): Test directly with Google API
2. Verify key format (should start with `AIzaSy`)
3. Check for empty lines in api_keys.txt
4. Reload keys: `Invoke-RestMethod -Uri "http://127.0.0.1:8000/reload-keys" ...`

### Scenario 2: High Memory Usage

**Symptoms**: Proxy using excessive RAM over time.

**Diagnosis**:
```powershell
# Check current memory
Get-Process -Id (Get-Content C:/Users/DaveWitkin/.local/gemini-proxy/proxy.pid) | Select-Object WorkingSet, PagedMemorySize

# Check for memory leaks in logs
Get-Content C:/Users/DaveWitkin/.local/gemini-proxy/logs/proxy.log | Select-String "memory|leak|cleanup"
```

**Solutions**:
1. Restart proxy: `./stop-proxy.ps1; ./start-proxy-background.ps1`
2. Check log rotation is working
3. Monitor with: `while($true) { Get-Process -Id (Get-Content proxy.pid) | Select-Object WorkingSet; Start-Sleep 60 }`

### Scenario 3: Task Scheduler Shows "Running" But Proxy Not Responding

**Symptoms**: Task status is Running, but proxy doesn't respond on port 8000.

**Diagnosis**:
```powershell
# Check if process actually exists
Get-Process -Id (Get-Content C:/Users/DaveWitkin/.local/gemini-proxy/proxy.pid) -ErrorAction SilentlyContinue

# Check if port is actually listening
netstat -ano | findstr :8000
```

**Solutions**:
1. Stop orphaned task: `Stop-ScheduledTask -TaskName "GeminiAPIKeyRotator"`
2. Kill any hanging Python processes: `Get-Process python | Where-Object { $_.Path -like "*gemini-proxy*" } | Stop-Process`
3. Clear PID file: `Remove-Item C:/Users/DaveWitkin/.local/gemini-proxy/proxy.pid`
4. Restart manually: `./start-proxy-background.ps1`

### Scenario 4: Monitoring Task Not Sending Notifications

**Symptoms**: No toast notifications when proxy is down.

**Diagnosis**:
```powershell
# Check if BurntToast module is installed
Get-Module -ListAvailable BurntToast

# Check monitor logs
Get-Content C:/Users/DaveWitkin/.local/gemini-proxy/logs/alerts.log -Tail 10

# Test notification manually
Import-Module BurntToast
New-BurntToastNotification -Text "Test", "Notification is working"
```

**Solutions**:
1. Install BurntToast: `Install-Module -Name BurntToast -Scope CurrentUser`
2. Check Windows notification settings
3. Review monitor script: `Get-Content C:/Users/DaveWitkin/.local/gemini-proxy/monitor-proxy.ps1 -Tail 50`

## Performance Tuning

### Adjusting Rate Limits

Edit main.py to adjust rate limiting per key:

```python
# In main.py, find rate limiter configuration
# Default is conservative to avoid Google rate limits
# Increase if you have higher quota:

# For 60 requests/minute per key (standard):
# (Already default in main.py)

# For 120 requests/minute per key (if you have higher quota):
# Modify: @limiter.limit("120 per minute") 
```

⚠️ **Warning**: Don't exceed your actual Google API quota or keys will be rate-limited by Google.

### Log Rotation

Logs rotate automatically at 10MB, but you can manually archive:

```powershell
# Archive old logs
$date = Get-Date -Format "yyyy-MM-dd"
Compress-Archive -Path C:/Users/DaveWitkin/.local/gemini-proxy/logs/proxy.log -DestinationPath C:/temp/proxy-log-$date.zip
Clear-Content C:/Users/DaveWitkin/.local/gemini-proxy/logs/proxy.log
```

## Backup and Recovery

### Full Backup

```powershell
$backupPath = "C:/temp/gemini-proxy-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $backupPath -Force

# Copy configuration
copy C:/Users/DaveWitkin/.local/gemini-proxy/api_keys.txt $backupPath/
copy C:/Users/DaveWitkin/.local/gemini-proxy/main.py $backupPath/

# Export scheduled tasks
Export-ScheduledTask -TaskName "GeminiAPIKeyRotator" | Out-File $backupPath/GeminiAPIKeyRotator.xml
Export-ScheduledTask -TaskName "GeminiProxyMonitor" | Out-File $backupPath/GeminiProxyMonitor.xml

# Copy logs (optional - can be large)
copy C:/Users/DaveWitkin/.local/gemini-proxy/logs/alerts.log $backupPath/

Write-Host "Backup complete at $backupPath"
```

### Restore from Backup

```powershell
$backupPath = "C:/temp/gemini-proxy-backup-20240115-120000"  # Change to your backup

# Restore configuration
copy $backupPath/api_keys.txt C:/Users/DaveWitkin/.local/gemini-proxy/
copy $backupPath/main.py C:/Users/DaveWitkin/.local/gemini-proxy/

# Import scheduled tasks
Register-ScheduledTask -Xml (Get-Content $backupPath/GeminiAPIKeyRotator.xml | Out-String) -TaskName "GeminiAPIKeyRotator"
Register-ScheduledTask -Xml (Get-Content $backupPath/GeminiProxyMonitor.xml | Out-String) -TaskName "GeminiProxyMonitor"

# Restart proxy
cd C:/Users/DaveWitkin/.local/gemini-proxy; ./stop-proxy.ps1; Start-Sleep 2; ./start-proxy-background.ps1
```

## Monitoring Customization

### Change Monitor Interval

1. **Open Task Scheduler**: `taskschd.msc`
2. **Navigate to**: `\GeminiProxyMonitor`
3. **Edit trigger**: Change from "Every 30 minutes" to desired interval
4. **Or via PowerShell**:
   ```powershell
   $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 9999)
   Set-ScheduledTask -TaskName "GeminiProxyMonitor" -Trigger $trigger
   ```

### Add Custom Health Checks

Edit `monitor-proxy.ps1` to add additional checks:

```powershell
# Add to monitor-proxy.ps1 after existing checks

# Check OpenCode is using proxy
$openCodeConfig = Get-Content C:/Users/DaveWitkin/.config/opencode/opencode.jsonc | ConvertFrom-Json
if ($openCodeConfig.providers.google.baseURL -ne "http://127.0.0.1:8000/v1beta") {
    Send-Alert -Type "WARNING" -Message "OpenCode not configured to use proxy!"
}

# Check disk space for logs
$logDrive = (Get-Item C:/Users/DaveWitkin/.local/gemini-proxy/logs).PSDrive
if ($logDrive.Free -lt 1GB) {
    Send-Alert -Type "WARNING" -Message "Low disk space for proxy logs!"
}
```

## OpenCode Integration

### Verify Proxy is Being Used

```powershell
# Check OpenCode configuration file
$config = Get-Content C:/Users/DaveWitkin/.config/opencode/opencode.jsonc | ConvertFrom-Json

# Should show:
# providers.google.baseURL = "http://127.0.0.1:8000/v1beta"
# providers.google.apiKey = null (or not set, since proxy handles keys)
```

### Fallback Configuration

If you need OpenCode to use direct Google API instead of proxy temporarily:

```powershell
# Edit opencode.jsonc and change:
# "baseURL": "http://127.0.0.1:8000/v1beta"  ->  "baseURL": "https://generativelanguage.googleapis.com/v1beta"
# "apiKey": "YOUR_DIRECT_API_KEY"

# To revert to proxy:
# "baseURL": "http://127.0.0.1:8000/v1beta"
# "apiKey": null (or remove the line)
```

⚠️ **Warning**: Direct API key in config bypasses rotation and rate limiting.

## Best Practices

1. **Keep 3-4 API keys minimum** for good rotation and redundancy
2. **Monitor alerts.log weekly** for early warning signs
3. **Test restart procedure monthly** to ensure auto-restart works
4. **Backup configuration** before making changes
5. **Update keys** before they expire (Google keys don't expire but can be revoked)
6. **Keep logs** for at least 7 days for debugging
7. **Document any custom changes** to main.py or scripts

## Quick Reference Card

```powershell
# STATUS
./proxy-status.ps1

# RESTART
./stop-proxy.ps1; Start-Sleep 2; ./start-proxy-background.ps1

# RELOAD KEYS (no restart)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/reload-keys" -Method POST -Headers @{"x-proxy-admin"="changeme_local_only"}

# VIEW LOGS
Get-Content logs/proxy.log -Tail 30

# CHECK TASKS
Get-ScheduledTask -TaskName "Gemini*" | Get-ScheduledTaskInfo

# BACKUP
$date = Get-Date -Format "yyyyMMdd"; Compress-Archive -Path . -DestinationPath C:/temp/gemini-backup-$date.zip
```
