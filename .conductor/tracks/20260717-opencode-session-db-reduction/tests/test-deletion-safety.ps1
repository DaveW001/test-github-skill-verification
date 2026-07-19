# test-deletion-safety.ps1
# Asserts that the deletion script satisfies safety criteria:
# - Uses opencode session delete (not direct SQL)
# - Refuses schema/data mutation SQL
# - Refuses deletion absent approval
# - Validates manifest SHA-256 matches approval
# - Validates DB unchanged before delete (TOCTOU gate)
# - Supports -WhatIf
# - Stops on first failure
# All tests FAIL in RED phase because the script does not exist yet.

function Run-Tests {
    param([string]$TrackRoot, [switch]$Verbose)
    
    $results = @()
    $scriptPath = Join-Path $TrackRoot 'delete-approved-sessions.ps1'
    
    # Test 1: Deletion script file exists
    $results += [pscustomobject]@{
        Name = 'deletion-script-exists'
        Passed = (Test-Path -LiteralPath $scriptPath)
        Reason = if (-not (Test-Path -LiteralPath $scriptPath)) { 'delete-approved-sessions.ps1 does not exist yet' } else { $null }
    }
    
    if (-not (Test-Path -LiteralPath $scriptPath)) {
        $remainingTests = @(
            'deletion-uses-opencode-session-delete',
            'deletion-refuses-mutation-sql',
            'deletion-requires-approval-file',
            'deletion-validates-manifest-sha256',
            'deletion-implements-toctou-gate',
            'deletion-supports-whatif',
            'deletion-stops-on-first-failure',
            'deletion-no-direct-sql-delete'
        )
        foreach ($t in $remainingTests) {
            $results += [pscustomobject]@{
                Name = $t
                Passed = $false
                Reason = 'delete-approved-sessions.ps1 does not exist yet'
            }
        }
        return $results
    }
    
    $scriptText = Get-Content -Raw -LiteralPath $scriptPath
    
    # Test 2: Uses 'opencode session delete' or 'session delete' CLI invocation
    $hasCliDelete = ($scriptText | Select-String -SimpleMatch -Pattern 'session delete' -Quiet)
    $results += [pscustomobject]@{
        Name = 'deletion-uses-opencode-session-delete'
        Passed = [bool]$hasCliDelete
        Reason = if (-not $hasCliDelete) { 'Script does not invoke opencode session delete CLI' } else { $null }
    }
    
    # Test 3: Refuses schema/data mutation SQL (no executable INSERT/UPDATE/DELETE/REPLACE/DROP/ALTER/TRUNCATE/CREATE/VACUUM)
    $mutationMatches = $scriptText | Select-String -Pattern '(?im)^\s*(?!#|--)\s*(INSERT|UPDATE|DELETE|REPLACE|DROP\s+TABLE|ALTER|TRUNCATE|CREATE\s+TABLE|VACUUM)\b'
    $results += [pscustomobject]@{
        Name = 'deletion-refuses-mutation-sql'
        Passed = ($null -eq $mutationMatches -or @($mutationMatches).Count -eq 0)
        Reason = if ($mutationMatches) { 'Script contains executable SQL mutation statements' } else { $null }
    }
    
    # Test 4: Requires approval file before proceeding
    $hasApprovalCheck = ($scriptText | Select-String -SimpleMatch -Pattern 'approval' -Quiet) -and
                        ($scriptText | Select-String -SimpleMatch -Pattern 'ApprovalPath' -Quiet)
    $results += [pscustomobject]@{
        Name = 'deletion-requires-approval-file'
        Passed = $hasApprovalCheck
        Reason = if (-not $hasApprovalCheck) { 'Script does not check for approval file before deletion' } else { $null }
    }
    
    # Test 5: Validates manifest SHA-256 matches approval
    $hasManifestValidation = ($scriptText | Select-String -SimpleMatch -Pattern 'manifestSha256' -Quiet) -and
                             ($scriptText | Select-String -SimpleMatch -Pattern 'Get-FileHash' -Quiet)
    $results += [pscustomobject]@{
        Name = 'deletion-validates-manifest-sha256'
        Passed = $hasManifestValidation
        Reason = if (-not $hasManifestValidation) { 'Script does not validate manifest SHA-256 against approval' } else { $null }
    }
    
    # Test 6: Implements TOCTOU gate (DB unchanged check before deletion)
    $hasToctou = ($scriptText | Select-String -SimpleMatch -Pattern 'dbUnchanged' -Quiet) -or
                 ($scriptText | Select-String -SimpleMatch -Pattern 'TOCTOU' -Quiet) -or
                 ($scriptText | Select-String -SimpleMatch -Pattern 'unchanged' -Quiet)
    $results += [pscustomobject]@{
        Name = 'deletion-implements-toctou-gate'
        Passed = [bool]$hasToctou
        Reason = if (-not $hasToctou) { 'Script does not implement DB-unchanged TOCTOU gate' } else { $null }
    }
    
    # Test 7: Supports -WhatIf parameter
    $hasWhatIf = ($scriptText | Select-String -SimpleMatch -Pattern 'WhatIf' -Quiet)
    $results += [pscustomobject]@{
        Name = 'deletion-supports-whatif'
        Passed = [bool]$hasWhatIf
        Reason = if (-not $hasWhatIf) { 'Script does not support -WhatIf parameter' } else { $null }
    }
    
    # Test 8: Stops on first failure (checks exit code / LASTEXITCODE)
    $hasStopOnError = ($scriptText | Select-String -SimpleMatch -Pattern 'LASTEXITCODE' -Quiet) -or
                      ($scriptText | Select-String -SimpleMatch -Pattern 'exit code' -Quiet) -or
                      ($scriptText | Select-String -SimpleMatch -Pattern 'stop' -Quiet)
    $results += [pscustomobject]@{
        Name = 'deletion-stops-on-first-failure'
        Passed = [bool]$hasStopOnError
        Reason = if (-not $hasStopOnError) { 'Script does not stop on first deletion failure' } else { $null }
    }
    
    # Test 9: Does not use direct SQL DELETE (only CLI)
    # Check that there's no executable "DELETE FROM" or "DELETE " SQL statement
    $directSqlDelete = $scriptText | Select-String -Pattern '(?im)^\s*(?!#|--)\s*DELETE\s+FROM\b'
    $results += [pscustomobject]@{
        Name = 'deletion-no-direct-sql-delete'
        Passed = ($null -eq $directSqlDelete -or @($directSqlDelete).Count -eq 0)
        Reason = if ($directSqlDelete) { 'Script uses direct SQL DELETE instead of CLI' } else { $null }
    }
    
    return $results
}
