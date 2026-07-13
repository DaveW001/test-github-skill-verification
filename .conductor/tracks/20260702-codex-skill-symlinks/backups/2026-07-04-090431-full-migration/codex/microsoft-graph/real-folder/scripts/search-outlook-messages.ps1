<#
.SYNOPSIS
    Search Outlook messages by subject keywords and export as Markdown.
.DESCRIPTION
    Uses Microsoft Graph API (app-only cert auth) to search Dave Witkin's mailbox
    for messages matching subject keywords within a date range. Deduplicates and
    exports as a structured Markdown file suitable for knowledge graph ingestion.
.NOTES
    REQUIRES: Active Graph session from connect-graph-no-wam.ps1.
    Run Connect-GraphNoWam BEFORE calling this script, in the SAME command.
    Do not use Connect-MgGraph -CertificateThumbprint directly; it can trigger
    Microsoft WAM account-picker popups even when AuthType is AppOnly.

    Example:
      . "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
      Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
      & search-outlook-messages.ps1 -Topics @("OIP","Trilogy") -StartDate "2026-01-29" -EndDate "2026-04-29" -OutputPath "outlook_export.md"

    Auth constants (copy into your script):
      $ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"
      $TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
      $CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
      $UserId         = "dave.witkin@packagedagile.com"
#>
param(
    [Parameter(Mandatory)]
    [string[]]$Topics,

    [Parameter(Mandatory)]
    [string]$StartDate,

    [Parameter(Mandatory)]
    [string]$EndDate,

    [Parameter(Mandatory)]
    [string]$OutputPath,

    [string]$UserId = "dave.witkin@packagedagile.com",

    [int]$TopPerTopic = 50,

    [int]$MaxBodyLength = 2000
)

$ErrorActionPreference = "Continue"

# Verify auth
$ctx = Get-MgContext
if (-not $ctx) {
    Write-Error "No active MgGraph session. Run connect-graph-no-wam.ps1 / Connect-GraphNoWam BEFORE this script, in the SAME command."
    exit 10
}
Write-Output "Authenticated as: $($ctx.AppName)"

# Collect and deduplicate
$allMsgs = [ordered]@{}

foreach ($topic in $Topics) {
    $filter = [System.Uri]::EscapeDataString(
        "receivedDateTime ge ${StartDate}T00:00:00Z and receivedDateTime le ${EndDate}T23:59:59Z and contains(subject, '$topic')"
    )
    $uri = "https://graph.microsoft.com/v1.0/users/$UserId/messages?`$filter=$filter&`$top=$TopPerTopic&`$select=subject,receivedDateTime,from,toRecipients,ccRecipients,body,conversationId"

    try {
        $r = Invoke-MgGraphRequest -Method GET -Uri $uri -ErrorAction Stop
        $newCount = 0
        foreach ($m in $r.value) {
            if (-not $allMsgs.Contains($m.id)) {
                $allMsgs[$m.id] = $m
                $newCount++
            }
        }
        Write-Output "  '$topic' -> $($r.value.Count) results, $newCount new"
    } catch {
        Write-Warning "  '$topic' -> FAILED: $($_.Exception.Message)"
    }
}

$msgs = @($allMsgs.Values) | Sort-Object receivedDateTime -Descending
Write-Output "`nTotal unique messages: $($msgs.Count)"

# Build Markdown
$sb = [System.Text.StringBuilder]::new()
$sb.AppendLine("# Outlook Export ($StartDate to $EndDate)") | Out-Null
$sb.AppendLine("Exported: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')") | Out-Null
$sb.AppendLine("Messages: $($msgs.Count)") | Out-Null
$sb.AppendLine("") | Out-Null

$i = 0
foreach ($msg in $msgs) {
    $i++
    $sb.AppendLine("## $i. $($msg.subject)") | Out-Null
    $dt = [DateTime]$msg.receivedDateTime
    $sb.AppendLine("- **Date:** $($dt.ToString('yyyy-MM-dd HH:mm'))") | Out-Null

    $fromDomain = if ($msg.from.emailAddress.address) {
        $msg.from.emailAddress.address -replace '.*@','@'
    } else { "" }
    $sb.AppendLine("- **From:** $($msg.from.emailAddress.name) ($fromDomain)") | Out-Null

    if ($msg.toRecipients) {
        $toStr = ($msg.toRecipients | ForEach-Object { $_.emailAddress.name }) -join ", "
        $sb.AppendLine("- **To:** $toStr") | Out-Null
    }
    if ($msg.ccRecipients -and $msg.ccRecipients.Count -gt 0) {
        $ccStr = ($msg.ccRecipients | ForEach-Object { $_.emailAddress.name }) -join ", "
        $sb.AppendLine("- **Cc:** $ccStr") | Out-Null
    }
    $sb.AppendLine("- **ConversationId:** $($msg.conversationId)") | Out-Null
    $sb.AppendLine("") | Out-Null

    # Strip HTML, truncate
    $bodyText = $msg.body.content `
        -replace '<[^>]+>','' `
        -replace '&nbsp;',' ' `
        -replace '&amp;','&' `
        -replace '&lt;','<' `
        -replace '&gt;','>' `
        -replace '\s+',' '
    $bodyText = $bodyText.Trim()
    if ($bodyText.Length -gt $MaxBodyLength) {
        $bodyText = $bodyText.Substring(0, $MaxBodyLength) + "...(truncated)"
    }
    $sb.AppendLine($bodyText) | Out-Null
    $sb.AppendLine("") | Out-Null
    $sb.AppendLine("---") | Out-Null
    $sb.AppendLine("") | Out-Null
}

$sb.ToString() | Out-File -FilePath $OutputPath -Encoding UTF8
Write-Output "Exported $i messages to $OutputPath"
