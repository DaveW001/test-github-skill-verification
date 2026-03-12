param(
  [Parameter(Mandatory = $true)][string]$Label,
  [Parameter(Mandatory = $true)][string]$OutputDir,
  [Parameter(Mandatory = $false)][string]$TargetCwd = ""
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$procOut = Join-Path $OutputDir ("processes-" + $stamp + ".txt")
$treeOut = Join-Path $OutputDir ("process-tree-" + $stamp + ".txt")
$dbOut = Join-Path $OutputDir ("db-paths-" + $stamp + ".txt")

"Label: $Label" | Out-File -FilePath $procOut -Encoding UTF8
"Timestamp: $(Get-Date -Format o)" | Out-File -FilePath $procOut -Append -Encoding UTF8
"" | Out-File -FilePath $procOut -Append -Encoding UTF8

Get-Process | Where-Object { $_.ProcessName -match "osgrep|node" } |
  Sort-Object ProcessName, StartTime |
  Select-Object ProcessName, Id, StartTime, CPU |
  Format-Table -AutoSize |
  Out-String | Out-File -FilePath $procOut -Append -Encoding UTF8

"Timestamp: $(Get-Date -Format o)" | Out-File -FilePath $treeOut -Encoding UTF8
if (Get-Command wmic -ErrorAction SilentlyContinue) {
  cmd /c "wmic process where \"name='osgrep-nodejs-helper.exe' or name='node.exe'\" get ProcessId,ParentProcessId,Name,CommandLine /format:table" |
    Out-File -FilePath $treeOut -Append -Encoding UTF8
} else {
  Get-CimInstance Win32_Process |
    Where-Object { $_.Name -in @("osgrep-nodejs-helper.exe", "node.exe") } |
    Select-Object Name, ProcessId, ParentProcessId, CommandLine |
    Format-Table -AutoSize |
    Out-String | Out-File -FilePath $treeOut -Append -Encoding UTF8
}

"Timestamp: $(Get-Date -Format o)" | Out-File -FilePath $dbOut -Encoding UTF8
if ($TargetCwd -and (Test-Path $TargetCwd)) {
  $osgrepPath = Join-Path $TargetCwd ".osgrep"
  "Target cwd: $TargetCwd" | Out-File -FilePath $dbOut -Append -Encoding UTF8
  "Path exists: $(Test-Path $osgrepPath)" | Out-File -FilePath $dbOut -Append -Encoding UTF8
  if (Test-Path $osgrepPath) {
    Get-ChildItem -Recurse -File -Path $osgrepPath -ErrorAction SilentlyContinue |
      Select-Object FullName, Length, LastWriteTime |
      Format-Table -AutoSize |
      Out-String | Out-File -FilePath $dbOut -Append -Encoding UTF8
  }
}

Write-Output "Snapshot files created in $OutputDir"
