# inventory-session-db.ps1 - Metadata-only inventory of the OpenCode session database
# Produces baseline.json, inventory.json, and candidate-manifest.json.
# NEVER selects, prints, or logs content-bearing columns.
# Uses node:sqlite in read-only mode. pragmamode=ro enforced at open.
# attributionSql uses only length() and octet_length() on data columns.
# denyListColumns: data, title, prompt, response, secret, value, access_token, refresh_token, metadata, slug, directory, path, share_url
# Family closure: complete parent/child families are retained or candidates together.
# Unarchived sessions (time_archived IS NULL) are always protected, plus their complete family.
# Cutoff: 180 days default (user policy overrides plan 90-day default).
# node --version must be >= 24 or >= 22.5 for node:sqlite support.

param(
    [Parameter(Mandatory)][string]$DbPath,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [int]$CutoffDays = 180,
    [string]$KeepListPath,
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
$policyVersion = 'metadata-only-v1'

Write-Verbose "DbPath=$DbPath"
Write-Verbose "OutputDirectory=$OutputDirectory"
Write-Verbose "CutoffDays=$CutoffDays"
Write-Verbose "KeepListPath=$KeepListPath"
Write-Verbose "WhatIf=$WhatIf"
Write-Verbose "policyVersion=$policyVersion"

if (-not (Test-Path -LiteralPath $DbPath)) { throw "Database not found: $DbPath" }
if (-not (Test-Path -LiteralPath $OutputDirectory)) { throw "Output directory not found: $OutputDirectory" }

$keepIds = @()
if ($KeepListPath -and (Test-Path -LiteralPath $KeepListPath)) {
    $keepIds = @(Get-Content -LiteralPath $KeepListPath | Where-Object { $_.Trim() -ne '' } | ForEach-Object { $_.Trim() })
}
Write-Verbose "Keep list count: $($keepIds.Count)"

$cutoffUtc = [long]([DateTimeOffset]::UtcNow.AddDays(-$CutoffDays).ToUnixTimeMilliseconds())
Write-Verbose "cutoffUtc=$cutoffUtc"

if ($WhatIf) {
    Write-Verbose "WhatIf mode: validating parameters only, no output files will be written."
    Write-Verbose "DbPath=$DbPath OutputDirectory=$OutputDirectory CutoffDays=$CutoffDays KeepListPath=$KeepListPath"
    Write-Host "WhatIf: parameters validated. No files written."
    exit 0
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$nodeHelperPath = Join-Path $scriptDir 'inventory-helper.mjs'
if (-not (Test-Path -LiteralPath $nodeHelperPath)) { throw "Node helper not found: $nodeHelperPath" }

# Build keep list JSON before any console output
$keepListJson = if ($keepIds.Count -gt 0) { ($keepIds | ConvertTo-Json -Compress) } else { '[]' }

$nodeOutput = & node --no-warnings $nodeHelperPath $DbPath $OutputDirectory $cutoffUtc $keepListJson 2>$null
if ($LASTEXITCODE -ne 0) { throw "Node.js helper failed with exit code $LASTEXITCODE" }

$allData = $nodeOutput | ConvertFrom-Json

# Write all JSON files BEFORE any console output to avoid raw JSON in console
$baselinePath = Join-Path $OutputDirectory 'baseline.json'
$allData.baseline | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 -LiteralPath $baselinePath

$inventoryPath = Join-Path $OutputDirectory 'inventory.json'
$allData.inventory | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 -LiteralPath $inventoryPath

$manifestPath = Join-Path $OutputDirectory 'candidate-manifest.json'
$allData.manifest | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 -LiteralPath $manifestPath

$manifestHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $manifestPath).Hash
Write-Verbose "manifestSha256=$manifestHash"

$sidecarPath = Join-Path $OutputDirectory 'candidate-manifest.json.sha256'
"$manifestHash  candidate-manifest.json" | Set-Content -Encoding utf8 -LiteralPath $sidecarPath

# Update baseline with actual file sizes (DB, WAL, SHM)
$dbFile = Get-Item -LiteralPath $DbPath
$walFile = Get-Item -LiteralPath "$DbPath-wal" -ErrorAction SilentlyContinue
$shmFile = Get-Item -LiteralPath "$DbPath-shm" -ErrorAction SilentlyContinue
$allData.baseline.dbBytes = $dbFile.Length
$allData.baseline.walBytes = if ($walFile) { $walFile.Length } else { 0 }
$allData.baseline.shmBytes = if ($shmFile) { $shmFile.Length } else { 0 }

# Re-write baseline with actual sizes
$baselinePath = Join-Path $OutputDirectory 'baseline.json'
$allData.baseline | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 -LiteralPath $baselinePath

# NOW output summary to console (all JSON I/O is complete)
$summary = $allData.manifest.summary
Write-Host "Inventory complete."
Write-Host "  Total sessions: $($summary.totalSessions)"
Write-Host "  Protected: $($summary.protectedSessions)"
Write-Host "  Candidates: $($summary.candidateSessions) sessions in $($summary.candidateFamilies) families"
Write-Host "  Estimated reclaimable bytes: $($summary.estimatedBytes)"
Write-Host "  Manifest SHA-256: $manifestHash"
Write-Host "  Manifest path: $manifestPath"
