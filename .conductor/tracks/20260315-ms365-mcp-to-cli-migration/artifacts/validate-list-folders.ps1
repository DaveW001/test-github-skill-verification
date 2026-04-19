$ErrorActionPreference = "Stop"

# Auth
$null = Connect-MgGraph -ClientId $env:DPB_GRAPH_CLIENT_ID -TenantId $env:DPB_GRAPH_TENANT_ID -CertificateThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT -NoWelcome

# Get current user via WhoAmI or similar
$ctx = Get-MgContext
Write-Output "Context: $($ctx | ConvertTo-Json -Depth 2)"

# For app-only, need to query users to find a valid user
Write-Output ""
Write-Output "=== Finding Users ==="
$users = Get-MgUser -Top 1
if ($users) {
    $userId = $users[0].Id
    Write-Output "Using User ID: $userId"
    
    # Test: List mail folders
    Write-Output ""
    Write-Output "=== Mail Folders Test ==="
    $folders = Get-MgUserMailFolder -UserId $userId -Top 10 | Select-Object DisplayName, Id
    $folders | Format-Table -AutoSize
    
    Write-Output ""
    Write-Output "VALIDATION: List mail folders successful"
} else {
    Write-Output "No users found - check app permissions"
}
