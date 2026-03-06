param(
  [string]$Workflow = "Visual Regression",
  [int]$Limit = 20,
  [string]$LogPath = ".conductor/tracks/webapp-visual-regression/artifacts/cross-browser-stability-log.md"
)

$runsJson = gh run list --workflow $Workflow --limit $Limit --json databaseId,status,conclusion,createdAt,headBranch,event,url 2>$null
if (-not $runsJson) {
  Write-Output "No runs returned. Ensure workflow '$Workflow' exists on default branch and has executed at least once."
  exit 0
}

$runs = $runsJson | ConvertFrom-Json
if (-not $runs -or $runs.Count -eq 0) {
  Write-Output "No runs found for workflow '$Workflow'."
  exit 0
}

$rows = foreach ($run in $runs) {
  $date = ([datetime]$run.createdAt).ToString("yyyy-MM-dd")
  $result = if ($run.conclusion) { $run.conclusion } else { $run.status }
  "| $date | $($run.headBranch) | non_blocking | CI | $result | $($run.url) |"
}

Write-Output "Suggested rows for $LogPath"
Write-Output "| Date | Branch | Mode | Scope | Result | Notes |"
Write-Output "| --- | --- | --- | --- | --- | --- |"
$rows
