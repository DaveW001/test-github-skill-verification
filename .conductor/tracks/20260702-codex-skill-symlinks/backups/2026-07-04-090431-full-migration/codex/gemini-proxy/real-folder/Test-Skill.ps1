# Gemini Proxy Skill Test
# Run this to verify the skill is working correctly

Write-Host "=== Gemini Proxy Skill Validation ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check skill file exists
Write-Host "[1/5] Checking skill file exists..." -NoNewline
$skillPath = "$env:USERPROFILE\.config\opencode\skills\gemini-proxy\SKILL.md"
if (Test-Path $skillPath) {
    Write-Host " ✓ PASS" -ForegroundColor Green
    $content = Get-Content $skillPath -Raw
    
    # Check frontmatter
    if ($content -match "^---") {
        Write-Host "      ✓ Frontmatter present"
    }
    if ($content -match "name:\s*gemini-proxy") {
        Write-Host "      ✓ Name field correct"
    }
} else {
    Write-Host " ✗ FAIL - Skill file not found" -ForegroundColor Red
}

# Test 2: Check reference file
Write-Host ""
Write-Host "[2/5] Checking reference file..." -NoNewline
$refPath = "$env:USERPROFILE\.config\opencode\skills\gemini-proxy\reference.md"
if (Test-Path $refPath) {
    Write-Host " ✓ PASS" -ForegroundColor Green
} else {
    Write-Host " ✗ FAIL - Reference file not found" -ForegroundColor Red
}

# Test 3: Check proxy directory exists
Write-Host ""
Write-Host "[3/5] Checking proxy installation..." -NoNewline
$proxyPath = "$env:USERPROFILE\.local\gemini-proxy"
if (Test-Path $proxyPath) {
    Write-Host " ✓ PASS" -ForegroundColor Green
    
    # Check key files
    $requiredFiles = @(
        "main.py",
        "api_keys.txt",
        "start-proxy-background.ps1",
        "stop-proxy.ps1",
        "proxy-status.ps1"
    )
    
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $proxyPath $file
        if (Test-Path $filePath) {
            Write-Host "      ✓ $file"
        } else {
            Write-Host "      ✗ $file (missing)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host " ✗ FAIL - Proxy directory not found" -ForegroundColor Red
}

# Test 4: Check scheduled tasks
Write-Host ""
Write-Host "[4/5] Checking scheduled tasks..." -NoNewline
try {
    $tasks = Get-ScheduledTask -TaskName "Gemini*" -ErrorAction Stop
    Write-Host " ✓ PASS" -ForegroundColor Green
    foreach ($task in $tasks) {
        $info = Get-ScheduledTaskInfo -TaskName $task.TaskName
        Write-Host "      ✓ $($task.TaskName) - State: $($task.State), Last Run: $($info.LastRunTime)"
    }
} catch {
    Write-Host " ✗ FAIL - Tasks not found or error: $_" -ForegroundColor Red
}

# Test 5: Quick proxy status check
Write-Host ""
Write-Host "[5/5] Checking proxy status..." -NoNewline
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/status" -Method GET -Headers @{"x-proxy-admin"="changeme_local_only"} -TimeoutSec 5
    Write-Host " ✓ PASS" -ForegroundColor Green
    Write-Host "      Keys: $($response.key_count) total, $($response.healthy_keys) healthy"
    Write-Host "      Uptime: $($response.uptime)"
} catch {
    Write-Host " ✗ FAIL - Proxy not responding: $_" -ForegroundColor Red
    Write-Host "      Run .\start-proxy-background.ps1 to start proxy"
}

Write-Host ""
Write-Host "=== Validation Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use the skill, ask OpenCode:"
Write-Host "  - 'check gemini proxy'"
Write-Host "  - 'restart gemini proxy'"  
Write-Host "  - 'is the proxy working?'"
Write-Host ""
Write-Host "Documentation:"
Write-Host "  Skill location: $skillPath"
Write-Host "  Reference:      $refPath"
Write-Host "  Full guide:     C:\development\opencode\docs\reference\gemini-proxy.md"
Write-Host "  Troubleshoot:   C:\development\opencode\docs\troubleshooting\active\gemini-proxy-down.md"
