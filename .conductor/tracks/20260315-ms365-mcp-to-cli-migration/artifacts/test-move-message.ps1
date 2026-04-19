$ErrorActionPreference = "Stop"
Connect-MgGraph -ClientId $env:DPB_GRAPH_CLIENT_ID -TenantId $env:DPB_GRAPH_TENANT_ID -CertificateThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT -NoWelcome
$userId = "58dba6be-24ef-4a75-b968-c64f75b504b1"
$messageId = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQBGAAAAAAA8K5fYAynyTot_fsDj7yapBwD9YgbCLDoDRqbmmlLG6VOsAAAASHvdAAD9YgbCLDoDRqbmmlLG6VOsAAgksuuiAAA="
$destinationId = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAAAAEKAAA="

Write-Output "Moving message: $messageId to folder: $destinationId"
$result = Move-MgUserMessage -UserId $userId -MessageId $messageId -DestinationId $destinationId
Write-Output "Move successful: $($result.Id)"
