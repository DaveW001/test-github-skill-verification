# backup-session-db.ps1 - Create a consistent SQLite backup using the backup API
# Requires all writers to be stopped for a clean checkpoint.
# Uses node:sqlite backup API. Never modifies the source database.

param(
    [Parameter(Mandatory)][string]$DbPath,
    [Parameter(Mandatory)][string]$BackupDirectory,
    [Parameter(Mandatory)][string]$ReportPath
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $DbPath)) { throw "Source database not found: $DbPath" }
if (-not (Test-Path -LiteralPath $BackupDirectory)) {
    New-Item -ItemType Directory -Path $BackupDirectory -Force | Out-Null
}

$timestamp = [DateTime]::UtcNow.ToString('yyyyMMdd-HHmmss')
$backupPath = Join-Path $BackupDirectory "opencode-pre-cleanup-$timestamp.db"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$nodeHelperPath = Join-Path $scriptDir 'backup-helper.mjs'
if (-not (Test-Path -LiteralPath $nodeHelperPath)) { throw "Backup helper not found: $nodeHelperPath" }

$nodeOutput = & node --no-warnings $nodeHelperPath $DbPath $backupPath 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) { throw "Backup failed: $nodeOutput" }

$validation = $nodeOutput | ConvertFrom-Json
$backupFile = Get-Item -LiteralPath $backupPath
$backupHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $backupPath).Hash

$report = [pscustomobject]@{
    backupPath = $backupPath
    backupBytes = $backupFile.Length
    backupSha256 = $backupHash
    sourceQuickCheck = $validation.sourceQuickCheck
    backupQuickCheck = $validation.backupQuickCheck
    sourceSchemaSha256 = $validation.sourceSchemaSha256
    backupSchemaSha256 = $validation.backupSchemaSha256
    sourceUserVersion = $validation.sourceUserVersion
    backupUserVersion = $validation.backupUserVersion
    createdAt = [DateTime]::UtcNow.ToString('o')
}

$report | ConvertTo-Json -Depth 5 | Set-Content -Encoding utf8 -LiteralPath $ReportPath

Write-Host "Backup created: $backupPath"
Write-Host "Backup size: $($backupFile.Length) bytes"
Write-Host "Quick check: source=$($validation.sourceQuickCheck), backup=$($validation.backupQuickCheck)"
Write-Host "Schema match: $($validation.sourceSchemaSha256 -eq $validation.backupSchemaSha256)"
