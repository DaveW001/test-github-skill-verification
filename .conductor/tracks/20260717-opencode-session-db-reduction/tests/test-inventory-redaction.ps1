# test-inventory-redaction.ps1
# Asserts that the inventory script (future implementation) satisfies redaction and safety criteria.
# All tests FAIL in RED phase because the script does not exist yet.

function Run-Tests {
    param([string]$TrackRoot, [switch]$Verbose)
    
    $results = @()
    $scriptPath = Join-Path $TrackRoot 'inventory-session-db.ps1'
    
    # Test 1: Inventory script file exists
    $results += [pscustomobject]@{
        Name = 'inventory-script-exists'
        Passed = (Test-Path -LiteralPath $scriptPath)
        Reason = if (-not (Test-Path -LiteralPath $scriptPath)) { 'inventory-session-db.ps1 does not exist yet' } else { $null }
    }
    
    if (-not (Test-Path -LiteralPath $scriptPath)) {
        # All remaining tests fail because script doesn't exist
        $remainingTests = @(
            'inventory-uses-readonly-sqlite',
            'inventory-forbids-mutation-sql',
            'inventory-uses-180day-cutoff',
            'inventory-protects-unarchived',
            'inventory-implements-family-closure',
            'inventory-declares-safety-mechanisms',
            'inventory-no-content-columns-selected',
            'inventory-no-session-ids-in-output'
        )
        foreach ($t in $remainingTests) {
            $results += [pscustomobject]@{
                Name = $t
                Passed = $false
                Reason = 'inventory-session-db.ps1 does not exist yet'
            }
        }
        return $results
    }
    
    $scriptText = Get-Content -Raw -LiteralPath $scriptPath
    
    # Test 2: Uses read-only SQLite
    $hasReadOnly = ($scriptText | Select-String -SimpleMatch -Pattern 'readOnly' -Quiet) -or 
                   ($scriptText | Select-String -SimpleMatch -Pattern 'ReadOnly' -Quiet) -or
                   ($scriptText | Select-String -SimpleMatch -Pattern 'pragmamode=ro' -Quiet) -or
                   ($scriptText | Select-String -SimpleMatch -Pattern 'mode=ro' -Quiet)
    $results += [pscustomobject]@{
        Name = 'inventory-uses-readonly-sqlite'
        Passed = [bool]$hasReadOnly
        Reason = if (-not $hasReadOnly) { 'Script does not declare read-only SQLite access' } else { $null }
    }
    
    # Test 3: Forbids mutation SQL (static analysis - no executable INSERT/UPDATE/DELETE/REPLACE/DROP/ALTER/TRUNCATE)
    $mutationMatches = $scriptText | Select-String -Pattern '(?im)^\s*(?!#|--)\s*(INSERT|UPDATE|DELETE|REPLACE|DROP\s+TABLE|ALTER|TRUNCATE)\b'
    $results += [pscustomobject]@{
        Name = 'inventory-forbids-mutation-sql'
        Passed = ($null -eq $mutationMatches -or @($mutationMatches).Count -eq 0)
        Reason = if ($mutationMatches) { 'Script contains executable SQL mutation statements' } else { $null }
    }
    
    # Test 4: Uses 180-day cutoff (user explicit requirement, overriding plan's 90)
    $has180 = ($scriptText | Select-String -Pattern '180' -Quiet)
    $results += [pscustomobject]@{
        Name = 'inventory-uses-180day-cutoff'
        Passed = [bool]$has180
        Reason = if (-not $has180) { 'Script does not reference 180-day cutoff as required by user' } else { $null }
    }
    
    # Test 5: Protects unarchived sessions
    $hasUnarchivedProtection = ($scriptText | Select-String -SimpleMatch -Pattern 'unarchived' -Quiet) -or
                                ($scriptText | Select-String -SimpleMatch -Pattern 'archived' -Quiet)
    $results += [pscustomobject]@{
        Name = 'inventory-protects-unarchived'
        Passed = [bool]$hasUnarchivedProtection
        Reason = if (-not $hasUnarchivedProtection) { 'Script does not reference unarchived session protection' } else { $null }
    }
    
    # Test 6: Implements family closure (parent/child relationship)
    $hasFamilyClosure = ($scriptText | Select-String -SimpleMatch -Pattern 'family' -Quiet) -or
                        ($scriptText | Select-String -SimpleMatch -Pattern 'parent' -Quiet)
    $results += [pscustomobject]@{
        Name = 'inventory-implements-family-closure'
        Passed = [bool]$hasFamilyClosure
        Reason = if (-not $hasFamilyClosure) { 'Script does not implement family closure for parent/child sessions' } else { $null }
    }
    
    # Test 7: Declares safety mechanisms (cutoffUtc, policyVersion, manifestSha256, denyListColumns, etc.)
    $requiredSubstrings = @('cutoffUtc', 'policyVersion', 'manifestSha256')
    $allPresent = $true
    $missingSubstrings = @()
    foreach ($s in $requiredSubstrings) {
        if (-not ($scriptText | Select-String -SimpleMatch -Pattern $s -Quiet)) {
            $allPresent = $false
            $missingSubstrings += $s
        }
    }
    $results += [pscustomobject]@{
        Name = 'inventory-declares-safety-mechanisms'
        Passed = $allPresent
        Reason = if (-not $allPresent) { "Script missing required safety substrings: $($missingSubstrings -join ', ')" } else { $null }
    }
    
    # Test 8: Does not SELECT forbidden content columns (event.data, message content, etc.)
    # Check that the script does not have executable SELECT statements that include content-bearing columns
    $forbiddenColumnPattern = '(?im)^\s*(?!#|--)\s*SELECT\b[^;]*\b(event\.data|message\.content|message\.text|title|prompt|response|token|credential|secret|api_key|apikey)\b'
    $forbiddenSelects = $scriptText | Select-String -Pattern $forbiddenColumnPattern
    $results += [pscustomobject]@{
        Name = 'inventory-no-content-columns-selected'
        Passed = ($null -eq $forbiddenSelects -or @($forbiddenSelects).Count -eq 0)
        Reason = if ($forbiddenSelects) { 'Script SELECTs forbidden content columns' } else { $null }
    }
    
    # Test 9: Does not output session IDs to console/logs
    # Check that Write-Host/Write-Output do not directly output session ID variables
    $sessionIdOutputPattern = '(?im)(Write-Host|Write-Output|Write-Verbose)\s+.*\$session[Ii]d'
    $sessionIdOutputs = $scriptText | Select-String -Pattern $sessionIdOutputPattern
    $results += [pscustomobject]@{
        Name = 'inventory-no-session-ids-in-output'
        Passed = ($null -eq $sessionIdOutputs -or @($sessionIdOutputs).Count -eq 0)
        Reason = if ($sessionIdOutputs) { 'Script outputs session IDs to console' } else { $null }
    }
    
    return $results
}
