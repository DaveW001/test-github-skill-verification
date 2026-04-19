Connect-MgGraph -ClientId $env:DPB_GRAPH_CLIENT_ID -TenantId $env:DPB_GRAPH_TENANT_ID -CertificateThumbprint $env:DPB_GRAPH_CERT_THUMBPRINT -NoWelcome
$userId = "58dba6be-24ef-4a75-b968-c64f75b504b1"
$junkId = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAASHvdAAA="
$deletedItemsId = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAAAAEKAAA="
$msgs = Get-MgUserMailFolderMessage -UserId $userId -MailFolderId $junkId -Top 1
Write-Output "Messages found: $($msgs.Count)"
foreach ($m in $msgs) {
    Write-Output "Moving: $($m.Subject)"
    Move-MgUserMessage -UserId $userId -MessageId $m.Id -DestinationId $deletedItemsId
    Write-Output "SUCCESS"
}
