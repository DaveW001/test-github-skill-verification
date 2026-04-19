$ErrorActionPreference = "Stop"
Connect-MgGraph -ClientId $env:DPB_GRAPH_CLIENT_ID -TenantId $env:DPB_GRAPH_TENANT_ID -CertificateThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT -NoWelcome
$userId = "58dba6be-24ef-4a75-b968-c64f75b504b1"
Get-MgUserMailFolder -UserId $userId -Filter "DisplayName eq 'Junk Email'" | Select-Object DisplayName, Id | ConvertTo-Json
