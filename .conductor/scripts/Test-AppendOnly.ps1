<#
.SYNOPSIS
  Verifies that <TargetPath> is a byte-for-byte append-only extension of <BackupPath>,
  with the expected heading present exactly once and the following paragraph within
  an expected sentence-count range.

.EXAMPLE
  .\Test-AppendOnly.ps1 -BackupPath C:\b\hello.bak.md -TargetPath C:\b\hello.md `
    -ExpectedHeadingRegex '^##\s+Hello World\s*$' -MinSentences 3 -MaxSentences 6
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$BackupPath,
  [Parameter(Mandatory = $true)][string]$TargetPath,
  [Parameter(Mandatory = $true)][string]$ExpectedHeadingRegex,
  [Parameter(Mandatory = $true)][int]$MinSentences,
  [Parameter(Mandatory = $true)][int]$MaxSentences
)

function Test-FilePresent {
  param([string]$Path, [string]$Label)
  if (-not (Test-Path -LiteralPath $Path)) {
    Write-Host "FAIL: $Label not found: $Path"
    exit 1
  }
}

# Required behavior: Fail if backup or target does not exist.
Test-FilePresent -Path $BackupPath -Label 'BackupPath'
Test-FilePresent -Path $TargetPath -Label 'TargetPath'

# Required behavior: Fail if target is shorter than backup.
$backupBytes = [System.IO.File]::ReadAllBytes($BackupPath)
$targetBytes = [System.IO.File]::ReadAllBytes($TargetPath)
if ($targetBytes.Length -lt $backupBytes.Length) {
  Write-Host "FAIL: target ($($targetBytes.Length) bytes) is shorter than backup ($($backupBytes.Length) bytes)"
  exit 1
}

# Required behavior: Fail if any backup byte differs from target prefix.
for ($i = 0; $i -lt $backupBytes.Length; $i++) {
  if ($targetBytes[$i] -ne $backupBytes[$i]) {
    Write-Host "FAIL: byte mismatch at index $i (backup=$($backupBytes[$i]) target=$($targetBytes[$i])) - existing content was rewritten"
    exit 1
  }
}

# Required behavior: Run git diff --no-index --numstat and fail if deletions are not 0.
# Note: git diff --no-index exits non-zero when files differ; we rely on the numstat
# columns, not the exit code.
$numstat = & git diff --no-index --numstat -- $BackupPath $TargetPath 2>&1
$deletionsOk = $true
foreach ($line in $numstat) {
  if ($null -eq $line) { continue }
  $text = $line.ToString()
  if ($text.Trim() -eq '') { continue }
  $cols = $text -split "`t"
  if ($cols.Length -ge 2 -and $cols[1] -ne '0') {
    $deletionsOk = $false
    Write-Host "FAIL: git diff --no-index --numstat reports deletions=$($cols[1]) in: $text"
  }
}
if (-not $deletionsOk) { exit 1 }

# Required behavior: Fail if heading regex count is not exactly 1.
$lines = Get-Content -LiteralPath $TargetPath
$headingIndexes = New-Object System.Collections.Generic.List[int]
for ($i = 0; $i -lt $lines.Count; $i++) {
  if ($lines[$i] -match $ExpectedHeadingRegex) { $headingIndexes.Add($i) | Out-Null }
}
if ($headingIndexes.Count -ne 1) {
  Write-Host "FAIL: ExpectedHeadingRegex match count=$($headingIndexes.Count) (expected exactly 1)"
  exit 1
}

# Required behavior: Find the paragraph immediately after the heading and fail if
# sentence count is outside [MinSentences, MaxSentences].
$hi = $headingIndexes[0]
$para = New-Object System.Collections.Generic.List[string]
for ($j = $hi + 1; $j -lt $lines.Count; $j++) {
  $l = $lines[$j]
  if ($l.Trim() -eq '') { break }
  if ($l -match '^\s*#{1,6}\s') { break }
  $para.Add($l) | Out-Null
}
$paraText = ($para -join ' ').Trim()
if ($paraText -eq '') {
  Write-Host "FAIL: no non-empty paragraph found immediately after the heading"
  exit 1
}
$sentences = [regex]::Split($paraText, '(?<=[.!?])\s+') | Where-Object { $_.Trim().Length -gt 0 }
$scount = @($sentences).Count
if ($scount -lt $MinSentences -or $scount -gt $MaxSentences) {
  Write-Host "FAIL: paragraph sentence count=$scount outside [$MinSentences, $MaxSentences]"
  exit 1
}

# Required behavior: Print PASS on success.
Write-Host "PASS: append-only verification succeeded"
exit 0