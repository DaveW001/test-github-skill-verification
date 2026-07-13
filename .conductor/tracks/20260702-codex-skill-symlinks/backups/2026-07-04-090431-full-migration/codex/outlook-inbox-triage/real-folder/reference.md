# Outlook Inbox Triage Reference

This file contains supporting guidance for the `outlook-inbox-triage` skill.

## Recommended Review Order

When the inbox is busy, review in this order:

1. direct human messages,
2. active threads with open loops,
3. calendar or scheduling changes,
4. operational alerts that may need acknowledgement,
5. financial alerts or statements,
6. newsletters, promos, and cold outreach.

## Suggested Summary Template

Use this structure when summarizing a message:

- `Sender:` who it is from
- `What it is:` one plain-English sentence
- `Why it matters:` action, if any
- `My take:` recommended next move

Example:

- `Sender:` Thomas
- `What it is:` He is fine with rescheduling and says weekends before May 17, 2026 still work.
- `Why it matters:` You may want to confirm a new date if you still want to meet sooner.
- `My take:` likely reply if you want to keep momentum; otherwise no urgent action.

## Suggested Interview Shortcuts

For common situations:

### Scheduling email

- `Do you want to lock a date now or leave it open?`

### Idea or suggestion email

- `Do you want to encourage this, politely defer it, or say no?`

### Cold outreach

- `Ignore, polite no, or keep for later?`

### Operational alert

- `Is this expected, or do you want to investigate before replying?`

### Relationship maintenance

- `Do you want to keep this warm with a quick acknowledgement?`

## Drafting Handoff Notes

When triage is complete, the next drafting skill or workflow should know:

- the target message,
- the intended outcome,
- the user's preferred tone,
- any facts to include,
- any boundaries to preserve.

## Minimal Response Planning Template

Before drafting, capture:

- `Goal:`
- `Tone:`
- `Include:`
- `Avoid:`
- `CTA or next step:`

If any of these are missing, ask one short follow-up question instead of guessing too much.


## Graph PowerShell Execution

All Outlook operations use **Microsoft Graph PowerShell** cmdlets via `bash`. Key patterns:

### Connect (required every invocation — no-WAM app-only auth, no browser prompt)
```powershell
$ClientId       = "23040dc9-20db-4645-99f7-71ba5e79b35e"
$TenantId       = "520005c9-0db3-4780-9c20-50fca961f83a"
$CertThumbprint = "764A4240264B0F302BE55247A9BC4AB1FBD5C357"
$UserId         = "dave.witkin@packagedagile.com"

. "C:\Users\DaveWitkin\.opencode-lazy-vault\microsoft-graph\scripts\connect-graph-no-wam.ps1"
Connect-GraphNoWam -ClientId $ClientId -TenantId $TenantId -CertThumbprint $CertThumbprint
```

### List recent inbox messages
```powershell
Get-MgUserMessage -UserId $userId -Top 10 -Sort "receivedDateTime desc" -Property "id,subject,from,receivedDateTime,isRead"
```

### Search by sender/subject
```powershell
Get-MgUserMessage -UserId $userId -Top 20 -Filter "contains(subject, 'search term')"
Get-MgUserMessage -UserId $userId -Top 20 -Filter "from/emailAddress/address eq 'sender@example.com'"
```

### Get full message by ID
```powershell
Get-MgUserMessage -UserId $userId -MessageId $messageId
```

### Critical Gotchas
- **Never use `-UserId me`** — always use full UPN `dave.witkin@packagedagile.com`
- **Session doesn't persist** — `Connect-MgGraph` required at start of every script
- **Use `-Top 2` not `-Top 1`** — single results can fail to enumerate
- Full reference: `C:\development\opencode\.conductor\tracks\20260429-email-calendar-mcp-audit\artifacts\graph-powershell-reference.md`
