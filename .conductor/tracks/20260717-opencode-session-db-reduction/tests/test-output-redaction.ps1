# test-output-redaction.ps1
# Asserts that no script outputs content, credentials, tokens, raw JSON, or session IDs
# to console or log files. All tests FAIL in RED phase because scripts do not exist yet.

function Run-Tests {
    param([string]$TrackRoot, [switch]$Verbose)
    
    $results = @()
    $scriptNames = @('inventory-session-db.ps1', 'delete-approved-sessions.ps1', 'backup-session-db.ps1', 'validate-session-db.ps1', 'compact-session-db.ps1')
    
    foreach ($scriptName in $scriptNames) {
        $scriptPath = Join-Path $TrackRoot $scriptName
        
        if (-not (Test-Path -LiteralPath $scriptPath)) {
            $results += [pscustomobject]@{
                Name = "$scriptName-no-content-output"
                Passed = $false
                Reason = "$scriptName does not exist yet"
            }
            continue
        }
        
        $scriptText = Get-Content -Raw -LiteralPath $scriptPath
        
        # Check that the script does not Write-Host/Write-Output session IDs directly
        # Pattern: Write-Host ... $sessionId or Write-Output ... $sessionId
        $sessionIdOutputPattern = '(?im)(Write-Host|Write-Output)\s+[^#]*\$session[Ii]d'
        $sessionIdOutputs = $scriptText | Select-String -Pattern $sessionIdOutputPattern
        $results += [pscustomobject]@{
            Name = "$scriptName-no-session-ids-in-console"
            Passed = ($null -eq $sessionIdOutputs -or @($sessionIdOutputs).Count -eq 0)
            Reason = if ($sessionIdOutputs) { "$scriptName outputs session IDs to console" } else { $null }
        }
        
        # Check that the script does not output raw JSON to console
        # Pattern: Write-Host ... ConvertTo-Json or Write-Output ... | ConvertTo-Json
        $rawJsonOutput = $scriptText | Select-String -Pattern '(?im)(Write-Host|Write-Output)\s+[^#]*ConvertTo-Json'
        $results += [pscustomobject]@{
            Name = "$scriptName-no-raw-json-in-console"
            Passed = ($null -eq $rawJsonOutput -or @($rawJsonOutput).Count -eq 0)
            Reason = if ($rawJsonOutput) { "$scriptName outputs raw JSON to console" } else { $null }
        }
        
        # Check that the script does not SELECT or output content-bearing columns
        $forbiddenColumnPattern = '(?im)^\s*(?!#|--)\s*SELECT\b[^;]*\b(event\.data|message\.content|message\.text|title|prompt|response|token|credential|secret|api_key|apikey)\b'
        $forbiddenSelects = $scriptText | Select-String -Pattern $forbiddenColumnPattern
        $results += [pscustomobject]@{
            Name = "$scriptName-no-content-columns"
            Passed = ($null -eq $forbiddenSelects -or @($forbiddenSelects).Count -eq 0)
            Reason = if ($forbiddenSelects) { "$scriptName SELECTs forbidden content columns" } else { $null }
        }
    }
    
    # Additional test: deletion log must not contain content fields
    $deletionLogPath = Join-Path $TrackRoot 'deletion-log.jsonl'
    if (Test-Path -LiteralPath $deletionLogPath) {
        $logText = Get-Content -Raw -LiteralPath $deletionLogPath
        $forbiddenInLog = @('event\.data', 'message\.content', 'api_key', 'apikey', 'token', 'secret', 'credential')
        $leaked = $false
        foreach ($p in $forbiddenInLog) {
            if ($logText | Select-String -Pattern $p -Quiet) {
                $leaked = $true
                break
            }
        }
        $results += [pscustomobject]@{
            Name = 'deletion-log-no-content-leak'
            Passed = (-not $leaked)
            Reason = if ($leaked) { 'deletion-log.jsonl contains forbidden content fields' } else { $null }
        }
    } else {
        $results += [pscustomobject]@{
            Name = 'deletion-log-no-content-leak'
            Passed = $false
            Reason = 'deletion-log.jsonl does not exist yet'
        }
    }
    
    # Test: inventory output files must not contain content
    $inventoryOutputFiles = @('inventory.json', 'candidate-manifest.json', 'baseline.json')
    foreach ($f in $inventoryOutputFiles) {
        $fPath = Join-Path $TrackRoot $f
        if (Test-Path -LiteralPath $fPath) {
            $fText = Get-Content -Raw -LiteralPath $fPath
            $forbiddenPatterns = @('event\.data', 'message\.content', 'api_key', 'apikey', 'token', 'secret', 'credential')
            $leaked = $false
            foreach ($p in $forbiddenPatterns) {
                if ($fText | Select-String -Pattern $p -Quiet) {
                    $leaked = $true
                    break
                }
            }
            $results += [pscustomobject]@{
                Name = "$f-no-content-leak"
                Passed = (-not $leaked)
                Reason = if ($leaked) { "$f contains forbidden content fields" } else { $null }
            }
        } else {
            $results += [pscustomobject]@{
                Name = "$f-no-content-leak"
                Passed = $false
                Reason = "$f does not exist yet"
            }
        }
    }
    
    return $results
}
