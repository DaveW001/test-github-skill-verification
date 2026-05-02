import re

file_path = r"C:\development\email-triage\scripts\hourly-email-auto-sort.ps1"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace auth section
old_auth = r"""Connect-MgGraph -ClientId \$ClientId -TenantId \$TenantId `
            -CertificateThumbprint \$CertThumbprint -NoWelcome -ErrorAction Stop 2>&1 \| Out-Null
        \$ctx = Get-MgContext
        if \(\$ctx\.AuthType -ne 'AppOnly'\) \{
            \$exitCode = 10
            throw "Expected AppOnly auth but got \$\(\$ctx\.AuthType\)\. Aborting to prevent interactive prompts\."
        \}
        Write-Log "- Connected as: \$\(\$ctx\.AppName\) \(\$\(\$ctx\.AuthType\)\)""""

new_auth = """Connect-MgGraph -Scopes "Mail.ReadWrite" -NoWelcome -ErrorAction Stop 2>&1 | Out-Null
        $ctx = Get-MgContext
        Write-Log "- Connected as: $($ctx.AppName) ($($ctx.AuthType))\""""

content = re.sub(old_auth, new_auth, content)

# Replace fetch section
old_fetch = r"""\$messages = Get-MgUserMailFolderMessage -UserId \$UserId -MailFolderId \$InboxFolderId `
            -All -Filter "IsRead eq false" -Property 'Subject,Sender,BodyPreview,ReceivedDateTime,IsRead' `
            -ErrorAction Stop"""

new_fetch = """$messages = Get-MgUserMessage -UserId "dave.witkin@packagedagile.com" -Filter "isRead eq false" -Top 50 -Property 'Id,Subject,Sender,BodyPreview,ReceivedDateTime,IsRead' -ErrorAction Stop"""

content = re.sub(old_fetch, new_fetch, content)

# Replace move section
old_move = r"""Move-MgUserMailFolderMessage -UserId \$UserId -MailFolderId \$InboxFolderId `
                    -MessageId \$msg\.Id -BodyParameter @\{ destinationId = \$destFolderId \} `
                    -ErrorAction Stop \| Out-Null"""

new_move = """Move-MgUserMessage -UserId "dave.witkin@packagedagile.com" -MessageId $msg.Id -DestinationId $destFolderId -ErrorAction Stop | Out-Null"""

content = re.sub(old_move, new_move, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated hourly-email-auto-sort.ps1")