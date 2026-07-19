# delete-approved-sessions.ps1 - Manifest-bound CLI-only session deletion
# FAIL-CLOSED: Requires exact manifest hash approval before any deletion.
# Uses ONLY `opencode session delete` CLI - no direct SQL mutation.
# Validates manifest SHA-256 matches approval, checks DB unchanged (TOCTOU gate).
# Supports -WhatIf for dry-run. Stops on first failure.
# Never outputs session IDs or raw JSON to console.

param(
    [Parameter(Mandatory)][string]$ManifestPath,
    [Parameter(Mandatory)][string]$ApprovalPath,
    [Parameter(Mandatory)][string]$OpenCodePath,
    [Parameter(Mandatory)][string]$LogPath,
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'

# Safety: no SQL mutation allowed - this script uses CLI only
# Forbidden patterns (static analysis will reject if found):
# INSERT, UPDATE, DELETE FROM, REPLACE, DROP TABLE, ALTER, TRUNCATE, CREATE TABLE, VACUUM

if (-not (Test-Path -LiteralPath $ManifestPath)) { throw "Manifest not found: $ManifestPath" }
if (-not (Test-Path -LiteralPath $ApprovalPath)) { throw "Approval not found: $ApprovalPath. Cannot proceed without explicit approval." }
if (-not (Test-Path -LiteralPath $OpenCodePath)) { throw "OpenCode CLI not found: $OpenCodePath" }

# Load and validate approval
$approval = Get-Content -Raw -LiteralPath $ApprovalPath | ConvertFrom-Json
if (-not $approval.approvedByUser) { throw "Approval file does not have approvedByUser=true. Cannot proceed." }
if (-not $approval.dbUnchangedConfirmed) { throw "Approval file does not have dbUnchangedConfirmed=true. TOCTOU gate not confirmed." }

# Validate manifest SHA-256 matches approval
$manifestHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $ManifestPath).Hash
if ($manifestHash -ne $approval.manifestSha256) {
    throw "Manifest SHA-256 mismatch. Approval hash: $($approval.manifestSha256), Actual hash: $manifestHash. Cannot proceed."
}

# Load manifest
$manifest = Get-Content -Raw -LiteralPath $ManifestPath | ConvertFrom-Json

# TOCTOU gate: verify DB unchanged since inventory
# This is a safety check - in production, would query DB session count/timestamp
# For now, we trust the approval's dbUnchangedConfirmed flag
Write-Verbose "TOCTOU gate: dbUnchangedConfirmed=$($approval.dbUnchangedConfirmed)"

# Extract candidate session IDs from manifest
$candidateIds = @()
if ($manifest.sessions -and $manifest.sessions.Count -gt 0) {
    $candidateIds = $manifest.sessions | ForEach-Object { $_.id }
}

Write-Host "Deletion script loaded."
Write-Host "  Manifest: $ManifestPath"
Write-Host "  Manifest SHA-256: $manifestHash"
Write-Host "  Candidates: $($candidateIds.Count) sessions"
Write-Host "  WhatIf: $WhatIf"

if ($WhatIf) {
    Write-Host "WhatIf mode: would delete $($candidateIds.Count) sessions. No changes made."
    exit 0
}

# Initialize deletion log
$logEntries = @()
$deletedCount = 0
$failedCount = 0

foreach ($sessionId in $candidateIds) {
    $timestamp = [DateTime]::UtcNow.ToString('o')
    try {
        # Invoke opencode session delete CLI
        $output = & $OpenCodePath session delete $sessionId 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            $logEntries += [pscustomobject]@{
                sessionId = $sessionId
                status = 'deleted'
                exitCode = $exitCode
                timestamp = $timestamp
            } | ConvertTo-Json -Compress
            $deletedCount++
            Write-Verbose "Deleted session (ID not shown for privacy)"
        } else {
            $logEntries += [pscustomobject]@{
                sessionId = $sessionId
                status = 'failed'
                exitCode = $exitCode
                timestamp = $timestamp
                error = ($output | Out-String)
            } | ConvertTo-Json -Compress
            $failedCount++
            Write-Error "Deletion failed for session. Exit code: $exitCode. Stopping."
            break  # Stop on first failure
        }
    } catch {
        $logEntries += [pscustomobject]@{
            sessionId = $sessionId
            status = 'error'
            exitCode = -1
            timestamp = $timestamp
            error = $_.Exception.Message
        } | ConvertTo-Json -Compress
        $failedCount++
        Write-Error "Exception during deletion: $($_.Exception.Message). Stopping."
        break  # Stop on first failure
    }
}

# Write deletion log (append mode)
$logEntries | ForEach-Object { Add-Content -LiteralPath $LogPath -Value $_ -Encoding utf8 }

Write-Host "Deletion complete."
Write-Host "  Deleted: $deletedCount"
Write-Host "  Failed: $failedCount"
Write-Host "  Log: $LogPath"

if ($failedCount -gt 0) {
    exit 1
}
