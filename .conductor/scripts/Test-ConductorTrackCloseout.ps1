<#
.SYNOPSIS
  Validates that a Conductor track is fully closed out and synchronized across all
  bookkeeping artifacts: metadata.json, plan.md, execution log, tracks.md, and
  tracks-ledger.md.

.PARAMETER RepoRoot
  Absolute path to the repository root (the folder that contains .conductor).

.PARAMETER TrackId
  The track id, e.g. 20260629-smoke-test-hello-world.

.PARAMETER ExpectedStatus
  The expected final status string, e.g. "executed".

.PARAMETER ExpectedDate
  The expected completion date in YYYY-MM-DD form, e.g. "2026-06-29".

.EXAMPLE
  .\Test-ConductorTrackCloseout.ps1 -RepoRoot C:\development\opencode `
    -TrackId 20260629-smoke-test-hello-world -ExpectedStatus executed -ExpectedDate 2026-06-29
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$RepoRoot,
  [Parameter(Mandatory = $true)][string]$TrackId,
  [Parameter(Mandatory = $true)][string]$ExpectedStatus,
  [Parameter(Mandatory = $true)][string]$ExpectedDate
)

$trackDir   = Join-Path $RepoRoot ".conductor\tracks\$TrackId"
$metaPath   = Join-Path $trackDir 'metadata.json'
$planPath   = Join-Path $trackDir 'plan.md'
$logPath    = Join-Path $trackDir "execution-log-$ExpectedDate.md"
$tracksPath = Join-Path $RepoRoot '.conductor\tracks.md'
$ledgerPath = Join-Path $RepoRoot '.conductor\tracks-ledger.md'

# 1. metadata.json: status and executed_at must match.
if (-not (Test-Path -LiteralPath $metaPath)) {
  Write-Host "FAIL: metadata.json not found: $metaPath"; exit 1
}
$meta = Get-Content -Raw -LiteralPath $metaPath | ConvertFrom-Json
if ($meta.status -ne $ExpectedStatus) {
  Write-Host "FAIL: metadata.json status='$($meta.status)' (expected '$ExpectedStatus')"; exit 1
}
if ($meta.executed_at -ne $ExpectedDate) {
  Write-Host "FAIL: metadata.json executed_at='$($meta.executed_at)' (expected '$ExpectedDate')"; exit 1
}

# 2. plan.md: all task checkboxes complete (no unchecked markdown task boxes).
if (-not (Test-Path -LiteralPath $planPath)) {
  Write-Host "FAIL: plan.md not found: $planPath"; exit 1
}
$planLines = Get-Content -LiteralPath $planPath
$unchecked = @($planLines | Where-Object { $_ -match '^\s*-\s*\[\s\]' })
if ($unchecked.Count -ne 0) {
  Write-Host "FAIL: plan.md has $($unchecked.Count) unchecked task checkbox(es)"; exit 1
}

# 3. execution log for the expected date must exist.
if (-not (Test-Path -LiteralPath $logPath)) {
  Write-Host "FAIL: execution log not found: $logPath"; exit 1
}

# 4. tracks.md: exactly one row for this track with the expected status and date.
if (-not (Test-Path -LiteralPath $tracksPath)) {
  Write-Host "FAIL: tracks.md not found: $tracksPath"; exit 1
}
$tracksLines = Get-Content -LiteralPath $tracksPath
$rowPattern = [regex]::Escape("| $TrackId ")
$rowMatches = @($tracksLines | Where-Object { $_ -match $rowPattern })
if ($rowMatches.Count -lt 1) {
  Write-Host "FAIL: tracks.md has no row for track '$TrackId'"; exit 1
}
$statusOk = $false
$dateOk = $false
foreach ($r in $rowMatches) {
  if ($r -match ([regex]::Escape("| $ExpectedStatus |"))) { $statusOk = $true }
  if ($r -match ([regex]::Escape("| $ExpectedDate |"))) { $dateOk = $true }
}
if (-not $statusOk) {
  Write-Host "FAIL: tracks.md row for '$TrackId' missing status '$ExpectedStatus'"; exit 1
}
if (-not $dateOk) {
  Write-Host "FAIL: tracks.md row for '$TrackId' missing date '$ExpectedDate'"; exit 1
}

# 5. tracks-ledger.md: an entry for this track with the expected phase.
if (-not (Test-Path -LiteralPath $ledgerPath)) {
  Write-Host "FAIL: tracks-ledger.md not found: $ledgerPath"; exit 1
}
$ledgerLines = Get-Content -LiteralPath $ledgerPath
$entryPattern = [regex]::Escape("[$TrackId]")
$entryMatches = @($ledgerLines | Where-Object { $_ -match $entryPattern })
if ($entryMatches.Count -lt 1) {
  Write-Host "FAIL: tracks-ledger.md has no entry for track '$TrackId'"; exit 1
}
$phaseOk = $false
$phaseNeedle = [regex]::Escape("Phase: $ExpectedStatus $ExpectedDate")
foreach ($e in $entryMatches) {
  if ($e -match $phaseNeedle) { $phaseOk = $true }
}
if (-not $phaseOk) {
  Write-Host "FAIL: tracks-ledger.md entry for '$TrackId' missing phase 'Phase: $ExpectedStatus $ExpectedDate'"; exit 1
}

Write-Host "PASS: conductor track closeout synchronized"
exit 0