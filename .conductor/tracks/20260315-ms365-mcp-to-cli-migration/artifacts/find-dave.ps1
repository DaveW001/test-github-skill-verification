$ErrorActionPreference = "Stop"
Connect-MgGraph -ClientId $env:DPB_GRAPH_CLIENT_ID -TenantId $env:DPB_GRAPH_TENANT_ID -CertificateThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT -NoWelcome
Get-MgUser -Filter "startsWith(DisplayName, 'Dave')" | Select-Object DisplayName, UserPrincipalName, Id | ConvertTo-Json
