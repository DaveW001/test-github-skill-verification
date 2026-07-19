# test-manifest-integrity.ps1
# Asserts that the candidate manifest and its validation satisfy integrity criteria.
# All tests FAIL in RED phase because the manifest and validation logic do not exist yet.

function Run-Tests {
    param([string]$TrackRoot, [switch]$Verbose)
    
    $results = @()
    $manifestPath = Join-Path $TrackRoot 'candidate-manifest.json'
    $inventoryScriptPath = Join-Path $TrackRoot 'inventory-session-db.ps1'
    
    # Test 1: Manifest file exists (will not exist until executor creates it)
    $results += [pscustomobject]@{
        Name = 'manifest-file-exists'
        Passed = (Test-Path -LiteralPath $manifestPath)
        Reason = if (-not (Test-Path -LiteralPath $manifestPath)) { 'candidate-manifest.json does not exist yet' } else { $null }
    }
    
    # Test 2: Inventory script generates SHA-256 sidecar
    if (Test-Path -LiteralPath $inventoryScriptPath) {
        $scriptText = Get-Content -Raw -LiteralPath $inventoryScriptPath
        $hasSha256 = ($scriptText | Select-String -SimpleMatch -Pattern 'SHA256' -Quiet) -or
                     ($scriptText | Select-String -SimpleMatch -Pattern 'sha256' -Quiet) -or
                     ($scriptText | Select-String -SimpleMatch -Pattern 'manifestSha256' -Quiet)
        $results += [pscustomobject]@{
            Name = 'manifest-sha256-sidecar-declared'
            Passed = [bool]$hasSha256
            Reason = if (-not $hasSha256) { 'Inventory script does not declare SHA-256 manifest hashing' } else { $null }
        }
    } else {
        $results += [pscustomobject]@{
            Name = 'manifest-sha256-sidecar-declared'
            Passed = $false
            Reason = 'inventory-session-db.ps1 does not exist yet'
        }
    }
    
    # Test 3: Inventory script validates manifest hash before use
    if (Test-Path -LiteralPath $inventoryScriptPath) {
        $scriptText = Get-Content -Raw -LiteralPath $inventoryScriptPath
        $hasHashValidation = ($scriptText | Select-String -SimpleMatch -Pattern 'Get-FileHash' -Quiet) -or
                             ($scriptText | Select-String -SimpleMatch -Pattern 'ComputeHash' -Quiet)
        $results += [pscustomobject]@{
            Name = 'manifest-hash-validation-logic'
            Passed = [bool]$hasHashValidation
            Reason = if (-not $hasHashValidation) { 'Inventory script lacks manifest hash validation logic' } else { $null }
        }
    } else {
        $results += [pscustomobject]@{
            Name = 'manifest-hash-validation-logic'
            Passed = $false
            Reason = 'inventory-session-db.ps1 does not exist yet'
        }
    }
    
    # Test 4: Manifest contains cutoffUtc field (180-day policy)
    if (Test-Path -LiteralPath $manifestPath) {
        try {
            $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
            $hasCutoff = $null -ne $manifest.cutoffUtc
            $results += [pscustomobject]@{
                Name = 'manifest-contains-cutoffUtc'
                Passed = $hasCutoff
                Reason = if (-not $hasCutoff) { 'Manifest missing cutoffUtc field' } else { $null }
            }
        } catch {
            $results += [pscustomobject]@{
                Name = 'manifest-contains-cutoffUtc'
                Passed = $false
                Reason = "Manifest JSON parse error: $($_.Exception.Message)"
            }
        }
    } else {
        $results += [pscustomobject]@{
            Name = 'manifest-contains-cutoffUtc'
            Passed = $false
            Reason = 'candidate-manifest.json does not exist yet'
        }
    }
    
    # Test 5: Manifest contains policyVersion field
    if (Test-Path -LiteralPath $manifestPath) {
        try {
            $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
            $hasPolicyVersion = $null -ne $manifest.policyVersion
            $results += [pscustomobject]@{
                Name = 'manifest-contains-policyVersion'
                Passed = $hasPolicyVersion
                Reason = if (-not $hasPolicyVersion) { 'Manifest missing policyVersion field' } else { $null }
            }
        } catch {
            $results += [pscustomobject]@{
                Name = 'manifest-contains-policyVersion'
                Passed = $false
                Reason = "Manifest JSON parse error: $($_.Exception.Message)"
            }
        }
    } else {
        $results += [pscustomobject]@{
            Name = 'manifest-contains-policyVersion'
            Passed = $false
            Reason = 'candidate-manifest.json does not exist yet'
        }
    }
    
    # Test 6: Manifest summary includes candidateSessions and candidateFamilies counts
    if (Test-Path -LiteralPath $manifestPath) {
        try {
            $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
            $hasSummary = ($null -ne $manifest.summary) -and 
                          ($null -ne $manifest.summary.candidateSessions) -and
                          ($null -ne $manifest.summary.candidateFamilies)
            $results += [pscustomobject]@{
                Name = 'manifest-summary-counts-present'
                Passed = $hasSummary
                Reason = if (-not $hasSummary) { 'Manifest missing summary.candidateSessions or summary.candidateFamilies' } else { $null }
            }
        } catch {
            $results += [pscustomobject]@{
                Name = 'manifest-summary-counts-present'
                Passed = $false
                Reason = "Manifest JSON parse error: $($_.Exception.Message)"
            }
        }
    } else {
        $results += [pscustomobject]@{
            Name = 'manifest-summary-counts-present'
            Passed = $false
            Reason = 'candidate-manifest.json does not exist yet'
        }
    }
    
    # Test 7: Manifest does NOT contain content fields (event.data, message text, credentials)
    if (Test-Path -LiteralPath $manifestPath) {
        $manifestText = Get-Content -Raw -LiteralPath $manifestPath
        $forbiddenPatterns = @('event\.data', 'message\.content', 'api_key', 'apikey', 'token', 'secret', 'credential')
        $leaked = $false
        foreach ($p in $forbiddenPatterns) {
            if ($manifestText | Select-String -Pattern $p -Quiet) {
                $leaked = $true
                break
            }
        }
        $results += [pscustomobject]@{
            Name = 'manifest-no-content-leak'
            Passed = (-not $leaked)
            Reason = if ($leaked) { 'Manifest contains forbidden content fields' } else { $null }
        }
    } else {
        $results += [pscustomobject]@{
            Name = 'manifest-no-content-leak'
            Passed = $false
            Reason = 'candidate-manifest.json does not exist yet'
        }
    }
    
    return $results
}
