# run-tests.ps1 - RED-phase safety harness for session-db reduction track
# Runs all test-*.ps1 files in this directory and reports pass/fail.
# Exit code: 0 if all pass, 1 if any fail.

param(
    [string]$TestDirectory = (Split-Path -Parent $MyInvocation.MyCommand.Path),
    [switch]$Verbose
)

$ErrorActionPreference = 'Stop'
$testsDir = $TestDirectory
$trackRoot = Split-Path -Parent $testsDir

# Discover test files
$testFiles = Get-ChildItem -LiteralPath $testsDir -Filter 'test-*.ps1' -File | Sort-Object Name

if ($testFiles.Count -eq 0) {
    Write-Error "No test-*.ps1 files found in $testsDir"
    exit 1
}

$totalTests = 0
$passedTests = 0
$failedTests = 0
$failedNames = @()

foreach ($tf in $testFiles) {
    Write-Host "`n=== Running $($tf.Name) ===" -ForegroundColor Cyan
    try {
        # Each test file must define a function Run-Tests and return an array of result objects
        . $tf.FullName
        $results = Run-Tests -TrackRoot $trackRoot -Verbose:$Verbose
        foreach ($r in $results) {
            $totalTests++
            if ($r.Passed) {
                $passedTests++
                Write-Host "  PASS: $($r.Name)" -ForegroundColor Green
            } else {
                $failedTests++
                $failedNames += "$($tf.Name)::$($r.Name)"
                Write-Host "  FAIL: $($r.Name) - $($r.Reason)" -ForegroundColor Red
            }
        }
    } catch {
        $totalTests++
        $failedTests++
        $failedNames += "$($tf.Name)::SCRIPT_ERROR"
        Write-Host "  FAIL: SCRIPT_ERROR - $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Yellow
Write-Host "Total: $totalTests | Passed: $passedTests | Failed: $failedTests" -ForegroundColor $(if ($failedTests -eq 0) { 'Green' } else { 'Red' })
if ($failedNames.Count -gt 0) {
    Write-Host "Failed tests:" -ForegroundColor Red
    $failedNames | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}
Write-Host "========================================" -ForegroundColor Yellow

exit $(if ($failedTests -eq 0) { 0 } else { 1 })
