param(
    [string]$ArtifactRoot = "C:\development\opencode\.conductor\tracks\20260526-skillful-local-patch\artifacts",
    [switch]$RotateDatabase = $true
)

$ErrorActionPreference = "Stop"

function Assert-NotRunning {
    $running = Get-Process -Name opencode, "OpenCode*", "ai.opencode*" -ErrorAction SilentlyContinue
    if ($running) {
        throw "OpenCode process is running. Quit Desktop before recovery."
    }
}

function Move-IfExists {
    param(
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$DestinationPath
    )
    if (Test-Path -LiteralPath $SourcePath) {
        Move-Item -LiteralPath $SourcePath -Destination $DestinationPath -Force
        return $true
    }
    return $false
}

Assert-NotRunning

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $ArtifactRoot "desktop-recovery-$timestamp"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

$desktopRoaming = "C:\Users\DaveWitkin\AppData\Roaming\ai.opencode.desktop"
$openCodeData = "C:\Users\DaveWitkin\.local\share\opencode"

# 1) Patch Skillful Desktop cache first.
powershell -ExecutionPolicy Bypass -File "C:\development\opencode\scripts\Repair-SkillfulDesktopCache.ps1"

# 2) Move window/workspace state files.
$stateNames = @("window-state.json", ".window-state.json")
foreach ($name in $stateNames) {
    $src = Join-Path $desktopRoaming $name
    $dst = Join-Path $backupDir $name
    [void](Move-IfExists -SourcePath $src -DestinationPath $dst)
}

$workspaceState = Get-ChildItem -LiteralPath $desktopRoaming -Filter "opencode.workspace*.dat" -File -ErrorAction SilentlyContinue
foreach ($file in $workspaceState) {
    $dst = Join-Path $backupDir $file.Name
    Move-Item -LiteralPath $file.FullName -Destination $dst -Force
}

# 3) Move Local/Session storage folders.
$localStorage = Join-Path $desktopRoaming "Local Storage"
$sessionStorage = Join-Path $desktopRoaming "Session Storage"
[void](Move-IfExists -SourcePath $localStorage -DestinationPath (Join-Path $backupDir "Local Storage"))
[void](Move-IfExists -SourcePath $sessionStorage -DestinationPath (Join-Path $backupDir "Session Storage"))
New-Item -ItemType Directory -Path $localStorage -Force | Out-Null
New-Item -ItemType Directory -Path $sessionStorage -Force | Out-Null

# 4) Optionally rotate OpenCode DB if previous steps were insufficient.
if ($RotateDatabase) {
    $db = Join-Path $openCodeData "opencode.db"
    $dbWal = "$db-wal"
    $dbShm = "$db-shm"
    [void](Move-IfExists -SourcePath $db -DestinationPath (Join-Path $backupDir "opencode.db"))
    [void](Move-IfExists -SourcePath $dbWal -DestinationPath (Join-Path $backupDir "opencode.db-wal"))
    [void](Move-IfExists -SourcePath $dbShm -DestinationPath (Join-Path $backupDir "opencode.db-shm"))
}

$report = [pscustomobject]@{
    backup_dir = $backupDir
    rotated_database = [bool]$RotateDatabase
    new_local_storage = Test-Path -LiteralPath $localStorage
    new_session_storage = Test-Path -LiteralPath $sessionStorage
    remaining_workspace_state = @(Get-ChildItem -LiteralPath $desktopRoaming -Filter "opencode.workspace*.dat" -File -ErrorAction SilentlyContinue).Count
}

$reportPath = Join-Path $backupDir "recovery-report.json"
$report | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $reportPath -NoNewline

Write-Output "backup_dir=$backupDir"
Write-Output "report=$reportPath"
Write-Output "remaining_workspace_state=$($report.remaining_workspace_state)"

