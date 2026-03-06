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

$classifyRun = {
  param($run)

  $detailJson = gh run view $run.databaseId --json jobs 2>$null
  if (-not $detailJson) {
    return [PSCustomObject]@{
      Scope = "CI"
      Result = if ($run.conclusion) { $run.conclusion } else { $run.status }
      Notes = "$($run.url) (details unavailable)"
    }
  }

  $detail = $detailJson | ConvertFrom-Json
  $steps = @($detail.jobs | ForEach-Object { $_.steps } | Where-Object { $_ })
  $visualSteps = @($steps | Where-Object { $_.name -eq "Run visual regression suite" })
  $crossSteps = @($steps | Where-Object { $_.name -eq "Run cross-browser suite" })
  $appChecks = @($steps | Where-Object { $_.name -eq "Check app availability" })

  $visualExecuted = ($visualSteps | Where-Object { $_.conclusion -ne "skipped" }).Count -gt 0
  $crossExecuted = ($crossSteps | Where-Object { $_.conclusion -ne "skipped" }).Count -gt 0
  $appReachabilityUnknown = ($appChecks | Where-Object { $_.conclusion -ne "success" }).Count -gt 0

  if (-not $visualExecuted -and -not $crossExecuted) {
    $reason = if ($appReachabilityUnknown) { "app-check-failed" } else { "app-unreachable-or-not-started" }
    return [PSCustomObject]@{
      Scope = "CI (skipped)"
      Result = "skipped"
      Notes = "$($run.url) [$reason]"
    }
  }

  return [PSCustomObject]@{
    Scope = if ($crossExecuted) { "CI (cross-browser)" } else { "CI (chromium-only)" }
    Result = if ($run.conclusion) { $run.conclusion } else { $run.status }
    Notes = $run.url
  }
}

$rows = foreach ($run in $runs) {
  $date = ([datetime]$run.createdAt).ToString("yyyy-MM-dd")
  $classified = & $classifyRun $run
  "| $date | $($run.headBranch) | non_blocking | $($classified.Scope) | $($classified.Result) | $($classified.Notes) |"
}

Write-Output "Suggested rows for $LogPath"
Write-Output "| Date | Branch | Mode | Scope | Result | Notes |"
Write-Output "| --- | --- | --- | --- | --- | --- |"
$rows
