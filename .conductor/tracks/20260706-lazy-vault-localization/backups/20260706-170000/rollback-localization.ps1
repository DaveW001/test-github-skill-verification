# rollback-localization.ps1
# Restores OneDrive-backed lazy-vault junctions to their original junction state.
# Usage:  pwsh -File rollback-localization.ps1 [-Names name1,name2] [-DryRun]
# Reads junction-inventory.json sitting next to this script.
[CmdletBinding()]
param(
    [string[]]$Names,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$here  = Split-Path -Parent $MyInvocation.MyCommand.Path
$json  = Join-Path $here 'junction-inventory.json'
$data  = Get-Content -LiteralPath $json -Raw | ConvertFrom-Json
$cands = $data.Entries | Where-Object { $_.Kind -eq 'junction' -and $_.OneDriveBacked -and $_.TargetExists }
if ($Names) { $cands = $cands | Where-Object { $Names -contains $_.Name } }
$stageDir = Join-Path $here ('rollback-staging-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (-not $DryRun) { New-Item -ItemType Directory -Path $stageDir -Force | Out-Null }
$restored = 0; $skipped = 0; $failed = @()
foreach ($c in $cands) {
    $p = $c.Path; $t = $c.Target
    if (-not (Test-Path -LiteralPath $p)) {
        # Path missing entirely -> recreate junction directly
        if ($DryRun) { Write-Output "[DRY] recreate-junction (missing): $($c.Name) -> $t"; continue }
        cmd /c mklink /J "$p" "$t" | Out-Null
        $restored++; continue
    }
    $cur = Get-Item -LiteralPath $p -Force
    $isJunction = ($cur.LinkType -eq 'Junction') -or ($cur.Attributes.ToString() -match 'ReparsePoint')
    if ($isJunction) { $skipped++; continue }
    # It's a real folder (was converted) -> stage it, remove, recreate junction
    if ($DryRun) { Write-Output "[DRY] would-stage+restore: $($c.Name) -> $t"; continue }
    $dest = Join-Path $stageDir $c.Name
    Copy-Item -LiteralPath $p -Destination $dest -Recurse -Force
    # Remove real folder then recreate junction. cmd /c rmdir on a real non-empty dir will fail; use Remove-Item -Recurse.
    Remove-Item -LiteralPath $p -Recurse -Force
    cmd /c mklink /J "$p" "$t" | Out-Null
    if (Test-Path -LiteralPath $p) { $restored++ } else { $failed += $c.Name }
}
Write-Output "Restored: $restored"
Write-Output "Skipped (already junction): $skipped"
if ($failed.Count -gt 0) { Write-Output "FAILED: $($failed -join ', ')" }
if (-not $DryRun) { Write-Output "Staged converted folders under: $stageDir" }
