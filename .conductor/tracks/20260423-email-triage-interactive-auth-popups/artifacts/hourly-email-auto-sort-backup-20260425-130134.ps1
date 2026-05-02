<#
.SYNOPSIS
    Hourly email auto-sorter using Microsoft Graph API directly.
.DESCRIPTION
    Scans unread emails in the Inbox and routes them to priority folders
    (Inbox Urgent, Inbox Today, Inbox Later, Inbox Junk) based on sender
    classification config files. Bypasses opencode run entirely for reliability.
.NOTES
    Requires Microsoft.Graph.Authentication and Microsoft.Graph.Mail modules.
    Auth token is cached via MSAL (Windows Credential Manager) after first
    interactive Connect-MgGraph login.
#>

$ErrorActionPreference = 'Continue'

# ── Config ──────────────────────────────────────────────────────────────────
$UserId          = 'dave.witkin@packagedagile.com'
$ClientId        = '14d82eec-204b-4c2f-b7e8-296a70dab67e'
$TenantId        = '520005c9-0db3-4780-9c20-50fca961f83a'
$RepoRoot        = 'C:\development\email-triage'
$DoNotBlockPath  = 'C:\development\email-quarantine\config\do-not-block.json'
$JunkIndicatorsPath = 'C:\development\email-quarantine\config\junk-indicators.json'

# Folder IDs (Inbox child folders)
$InboxFolderId   = 'AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAAAAEMAAA='
$UrgentFolderId  = 'AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAg9NfggAAA='
$TodayFolderId   = 'AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAg9NfghAAA='
$LaterFolderId   = 'AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAg9NfgiAAA='
$JunkFolderId    = 'AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAg9NfgjAAA='

# ── Logging Setup ───────────────────────────────────────────────────────────
$start     = Get-Date
$timestamp = $start.ToString('yyyy-MM-dd_HH-mm')
$logsDir   = Join-Path $RepoRoot 'logs'
$logPath   = Join-Path $logsDir ("{0}_run.md" -f $timestamp)
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

$logLines = [System.Collections.Generic.List[string]]::new()

function Write-Log {
    param([string]$Text)
    $script:logLines.Add($Text)
}

# ── Counters ────────────────────────────────────────────────────────────────
$counts = @{
    'Inbox Urgent' = 0
    'Inbox Today'  = 0
    'Inbox Later'  = 0
    'Inbox Junk'   = 0
    'Skipped'      = 0
    'Error'        = 0
}

$exitCode = 0

try {
    # ── 1) Load Classification Config ───────────────────────────────────────
    Write-Log '# Hourly Email Auto Sort Run'
    Write-Log ''
    Write-Log "- Start: $($start.ToString('yyyy-MM-dd HH:mm:ss'))"

    $doNotBlock = @{ Emails = @(); Domains = @() }
    $junkIndicators = @{ Emails = @(); Domains = @() }

    if (Test-Path $DoNotBlockPath) {
        $dnb = Get-Content $DoNotBlockPath -Raw | ConvertFrom-Json
        $doNotBlock.Emails = @($dnb.emails | ForEach-Object { $_.ToLowerInvariant() })
        $doNotBlock.Domains = @($dnb.domains | ForEach-Object { $_.ToLowerInvariant() })
        Write-Log "- Do-not-block loaded: $($doNotBlock.Emails.Count) emails, $($doNotBlock.Domains.Count) domains"
    } else {
        Write-Log "- WARNING: do-not-block.json not found at $DoNotBlockPath"
    }

    if (Test-Path $JunkIndicatorsPath) {
        $ji = Get-Content $JunkIndicatorsPath -Raw | ConvertFrom-Json
        $junkIndicators.Emails = @($ji.emails | ForEach-Object { $_.ToLowerInvariant() })
        $junkIndicators.Domains = @($ji.domains | ForEach-Object { $_.ToLowerInvariant() })
        Write-Log "- Junk indicators loaded: $($junkIndicators.Emails.Count) emails, $($junkIndicators.Domains.Count) domains"
    } else {
        Write-Log "- WARNING: junk-indicators.json not found at $JunkIndicatorsPath"
    }

    # ── 2) Connect to Graph ─────────────────────────────────────────────────
    Write-Log ''
    Write-Log '## Authentication'

    Import-Module Microsoft.Graph.Authentication -ErrorAction Stop
    Import-Module Microsoft.Graph.Mail -ErrorAction Stop

    try {
        Connect-MgGraph -ClientId $ClientId -TenantId $TenantId `
            -Scopes 'Mail.ReadWrite','Mail.Read' -NoWelcome -ErrorAction Stop 2>&1 | Out-Null
        $ctx = Get-MgContext
        Write-Log "- Connected as: $($ctx.Account) ($($ctx.AuthType))"
    } catch {
        throw "Graph auth failed: $($_.Exception.Message)"
    }

    # ── 3) Fetch Unread Messages ────────────────────────────────────────────
    Write-Log ''
    Write-Log '## Inbox Scan'

    $messages = Get-MgUserMailFolderMessage -UserId $UserId -MailFolderId $InboxFolderId `
        -All -Filter "IsRead eq false" -Property 'Subject,Sender,BodyPreview,ReceivedDateTime,IsRead' `
        -ErrorAction Stop

    $totalUnread = @($messages).Count
    Write-Log "- Unread messages found: $totalUnread"

    if ($totalUnread -eq 0) {
        Write-Log "- No unread emails to process. Exiting cleanly."
        $exitCode = 0
    } else {
        # ── 4) Classify and Move ────────────────────────────────────────────
        Write-Log ''
        Write-Log '## Classification & Moves'

        $msgIndex = 0
        foreach ($msg in $messages) {
            $msgIndex++
            $senderEmail = ''
            $senderDomain = ''
            $senderName = ''

            if ($msg.Sender -and $msg.Sender.EmailAddress) {
                $senderEmail = $msg.Sender.EmailAddress.Address.ToLowerInvariant()
                $senderName = $msg.Sender.EmailAddress.Name
                $parts = $senderEmail.Split('@')
                if ($parts.Length -eq 2) { $senderDomain = $parts[1] }
            }

            $subject = if ($msg.Subject) { $msg.Subject } else { '(no subject)' }
            $subject = $subject.Substring(0, [Math]::Min(80, $subject.Length))

            # Determine classification
            $destination = 'Inbox Later'  # default
            $destFolderId = $LaterFolderId
            $isDoNotBlock = $doNotBlock.Emails -contains $senderEmail -or $doNotBlock.Domains -contains $senderDomain
            $isJunkSender = $junkIndicators.Emails -contains $senderEmail -or $junkIndicators.Domains -contains $senderDomain

            if ($isDoNotBlock) {
                # Safe sender — never junk, default to Today
                $destination = 'Inbox Today'
                $destFolderId = $TodayFolderId

                # Check for urgency signals in subject
                if ($subject -match 'urgent|asap|critical|immediate|emergency|action required|time.sensitive') {
                    $destination = 'Inbox Urgent'
                    $destFolderId = $UrgentFolderId
                }
                # FYI / newsletter patterns from safe senders go to Later
                elseif ($subject -match 'fyi|newsletter|digest|weekly|monthly|update' -and $subject -notmatch 'action|reply|respond') {
                    $destination = 'Inbox Later'
                    $destFolderId = $LaterFolderId
                }
            } elseif ($isJunkSender) {
                $destination = 'Inbox Junk'
                $destFolderId = $JunkFolderId
            } else {
                # Unknown sender — heuristic classification
                # Check for junk patterns
                if ($subject -match 'unsubscribe|promo|sale|discount|deal|offer|free trial|webinar invite|cold outreach') {
                    $destination = 'Inbox Junk'
                    $destFolderId = $JunkFolderId
                }
                # Check for urgency
                elseif ($subject -match 'urgent|asap|critical|immediate|emergency|action required|time.sensitive') {
                    $destination = 'Inbox Urgent'
                    $destFolderId = $UrgentFolderId
                }
                # Check for today-level items
                elseif ($subject -match 'review|approve|feedback|response|reply|meeting|calendar|invite|schedule') {
                    $destination = 'Inbox Today'
                    $destFolderId = $TodayFolderId
                }
                # Default: Later
                else {
                    $destination = 'Inbox Later'
                    $destFolderId = $LaterFolderId
                }
            }

            # Move the message
            try {
                Move-MgUserMailFolderMessage -UserId $UserId -MailFolderId $InboxFolderId `
                    -MessageId $msg.Id -BodyParameter @{ destinationId = $destFolderId } `
                    -ErrorAction Stop | Out-Null

                $counts[$destination]++
                Write-Log "- [$msgIndex/$totalUnread] $destination <- `"$subject`" (from $senderEmail)"
            } catch {
                $counts['Error']++
                Write-Log "- [$msgIndex/$totalUnread] ERROR moving `"$subject`": $($_.Exception.Message)"
            }
        }
    }

    # ── 5) Disconnect ───────────────────────────────────────────────────────
    Disconnect-MgGraph 2>&1 | Out-Null

} catch {
    $exitCode = 1
    Write-Log ''
    Write-Log "## FATAL ERROR"
    Write-Log $_.Exception.Message
}

# ── 6) Write Log ────────────────────────────────────────────────────────────
$end = Get-Date
$status = if ($exitCode -eq 0) { 'success' } else { 'failed' }

Write-Log ''
Write-Log "- End: $($end.ToString('yyyy-MM-dd HH:mm:ss'))"
Write-Log "- Status: $status"
Write-Log "- Exit code: $exitCode"
Write-Log ''
Write-Log '## Summary'
Write-Log ''
Write-Log "| Destination | Count |"
Write-Log "|---|---|"
Write-Log "| Inbox Urgent | $($counts['Inbox Urgent']) |"
Write-Log "| Inbox Today | $($counts['Inbox Today']) |"
Write-Log "| Inbox Later | $($counts['Inbox Later']) |"
Write-Log "| Inbox Junk | $($counts['Inbox Junk']) |"
Write-Log "| Skipped | $($counts['Skipped']) |"
Write-Log "| Errors | $($counts['Error']) |"

Set-Content -Path $logPath -Value $logLines -Encoding UTF8

# Write latest-status.md index
$latestPath = Join-Path $logsDir 'latest-status.md'
$statusLine = "- $($start.ToString('yyyy-MM-dd HH:mm')) | $status | Urgent=$($counts['Inbox Urgent']) Today=$($counts['Inbox Today']) Later=$($counts['Inbox Later']) Junk=$($counts['Inbox Junk']) Errors=$($counts['Error'])"
Set-Content -Path $latestPath -Value $statusLine -Encoding UTF8

exit $exitCode
