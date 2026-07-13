<#
.SYNOPSIS
    Send a Slack message from PowerShell using a bot token.

.DESCRIPTION
    Based on email-triage/scripts/hourly-email-auto-sort.ps1 patterns.
    Uses Invoke-RestMethod with chat.postMessage. No extra packages needed.

.PARAMETER Text
    Message text to send (Slack mrkdwn supported).

.PARAMETER Channel
    Channel ID or user ID (default: $env:SLACK_USER_ID for DM).

.PARAMETER UnfurlLinks
    Show link previews (default: $false to keep messages clean).

.EXAMPLE
    .\Send-SlackMessage.ps1 -Text "Deploy complete!"
    .\Send-SlackMessage.ps1 -Text "Error: checkout-api down" -Channel "#alerts"
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Text,

    [string]$Channel = $env:SLACK_USER_ID,

    [bool]$UnfurlLinks = $false
)

# --- Configuration ---
$BotToken = $env:SLACK_BOT_TOKEN
$ApiUrl   = "https://slack.com/api/chat.postMessage"

if ([string]::IsNullOrWhiteSpace($BotToken)) {
    Write-Error "SLACK_BOT_TOKEN not set. Configure in .env or environment."
    exit 1
}

# --- Build payload ---
# Use ConvertTo-Json with -Depth to handle nested structures properly
$payload = @{
    channel      = $Channel
    text         = $Text
    unfurl_links = $UnfurlLinks
    link_names   = $true
} | ConvertTo-Json -Depth 10

$headers = @{
    Authorization = "Bearer $BotToken"
    "Content-Type" = "application/json"
}

# --- Send ---
try {
    $response = Invoke-RestMethod -Uri $ApiUrl -Method Post -Headers $headers -Body $payload -TimeoutSec 30

    # Slack always returns HTTP 200 - check the ok field
    if ($response.ok) {
        Write-Output "[OK] Message sent (ts: $($response.ts))"
    } else {
        Write-Error "[FAIL] Slack API error: $($response.error)"
        exit 1
    }
} catch {
    # Check for rate limiting (429)
    if ($_.Exception.Response.StatusCode -eq 429) {
        $retryAfter = $_.Exception.Response.Headers["Retry-After"]
        Write-Warning "Rate limited. Waiting $retryAfter seconds..."
        Start-Sleep -Seconds ([int]$retryAfter)
        # Retry once
        $response = Invoke-RestMethod -Uri $ApiUrl -Method Post -Headers $headers -Body $payload -TimeoutSec 30
        if ($response.ok) {
            Write-Output "[OK] Message sent after retry (ts: $($response.ts))"
        } else {
            Write-Error "[FAIL] Still failing: $($response.error)"
            exit 1
        }
    } else {
        Write-Error "[ERROR] Request failed: $_"
        exit 1
    }
}


<#
.NOTES
    Slack mrkdwn formatting (NOT standard Markdown):
      *bold*       (not **bold**)
      _italic_     (not *italic*)
      ~strike~     (not ~~strike~~)
      `code`
      > blockquote
      - bullet item

    For Block Kit messages with buttons/dividers/images, add a "blocks" key
    to the payload hashtable before ConvertTo-Json.

    For file uploads from PowerShell, use the 3-step API:
      1. files.getUploadURLExternal (POST, returns upload_url + file_id)
      2. POST file bytes to upload_url
      3. files.completeUploadExternal (POST, with file_id + channel_id)

    See reference.md for the full file upload flow.
#>