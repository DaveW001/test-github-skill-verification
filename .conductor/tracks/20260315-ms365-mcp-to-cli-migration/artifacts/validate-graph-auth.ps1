$ErrorActionPreference = "Stop"
$null = Connect-MgGraph -ClientId $env:DPB_GRAPH_CLIENT_ID -TenantId $env:DPB_GRAPH_TENANT_ID -CertificateThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT -NoWelcome
$ctx = Get-MgContext
Write-Output "AppName: $($ctx.AppName)"
Write-Output "Account: $($ctx.Account)"
Write-Output "AuthMode: $($ctx.AuthMode)"
Write-Output "VALIDATION: Graph cert auth successful"
