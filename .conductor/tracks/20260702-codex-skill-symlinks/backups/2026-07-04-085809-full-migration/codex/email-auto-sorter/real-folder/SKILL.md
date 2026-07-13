---
tool_context:
  with_tools: [bash]
name: email-auto-sorter
description: Headless/automated skill to keep the inbox clean. It scans unread emails and routes them into specific folders (INBOX-Urgent, INBOX-Today, INBOX-Later, INBOX-Junk) depending on priority and sender rules without user intervention. Can be run via scheduled job.
triggers:
  intent:
    - automated email routing
    - inbox cleaning
    - background sorting
  user_phrases:
    - sort my emails
    - clean up the inbox
    - run auto sorter
  execution_layer: graph-powershell
  cmdlets: [Get-MgUserMessage, Get-MgUserMailFolder, Move-MgUserMessage, Update-MgUserMessage]
  priority: high
  suggest_only: false
compatibility: OpenCode skills system; optimized for headless execution via Microsoft Graph PowerShell.
---

# Email Auto-Sorter

This skill is an automated inbox cleaner meant to reduce cognitive load and overwhelm. It reads new unread emails from the main Inbox and automatically moves them into priority folders. It can be scheduled (e.g., via `windows-task-scheduler`) to run every few hours without human interaction.

## Graph PowerShell Execution

See [reference.md](reference.md) for PowerShell cmdlets and syntax.

## Core Rules
- Do NOT ask the user for permission for every email. Read the rules below and sort them autonomously.
- Do NOT mark emails as read unless they are being moved to INBOX-Junk.
- NEVER draft or send a response with this skill. Purely parsing and moving.

## Folder Mapping

Expect the presence of standard target folders (or create/move to them if the MCP tool requires it):
- `Inbox Urgent`: Action needed in < 2 hours or same-day critical.
- `Inbox Today`: Action needed today, or this week.
- `Inbox Later`: FYI items, industry newsletters worth reading, non-action items.
- `Inbox Junk`: Newsletters, promotional noise, alerts, auto-notifications no longer needed.

## Classification Source Of Truth

Use these files as the canonical routing inputs:

1. **Routing overrides** (force a specific folder): `C:/development/email-triage/config/routing-overrides.json`
2. **Allowlist** (never junk): `C:/development/email-quarantine/config/do-not-block.json`
3. **Junk indicators** (known junk): `C:/development/email-quarantine/config/junk-indicators.json`
4. **Business context** (relevance keywords for S9/S10): `C:/development/email-triage/config/business-context.json`
5. **Heuristics** (fallback when no config match): `scripts/Get-HeuristicScore.ps1`

### Precedence Rules (Specificity-Aware)

Evaluate these layers **in order** for each email. Higher-specificity matches (exact email) always beat lower-specificity matches (domain-level):

1. **Layer 1 — Exact routing override:** Look up the sender's **exact email address** in `routing-overrides.json`. If found, route to the specified `targetFolder` and stop. Exact email overrides win over all other rules, including domain-level allowlists and junk indicators.
2. **Layer 2 — Exact email allowlist:** If the sender's **exact email address** appears in `do-not-block.json`, do NOT route to `Inbox Junk`. Continue to Layer 4 for heuristic classification.
3. **Layer 3 — Exact email junk indicator:** If the sender's **exact email address** appears in `junk-indicators.json`, route to `Inbox Junk` and stop. **This overrides domain-level allowlists** — a known junk sender at `gmail.com` is junked even though the `gmail.com` domain is in the allowlist.
4. **Layer 4 — Domain-level checks + heuristic scoring:** Check domain-level allowlist, domain-level junk indicators, then fall back to heuristic scoring. Domain-level allowlist prevents junking but does not block heuristic scoring from running. Heuristic scoring runs independently and can route to `Inbox Later` or `Inbox Junk` based on content signals even for allowlisted domains.

## Sorting Logic

1. **Pull unread emails** from the root Inbox.
2. **Resolve destination folder IDs** for `Inbox Urgent`, `Inbox Today`, `Inbox Later`, and `Inbox Junk` using folder lookup tools.
3. **Classify** each email using the precedence rules above. For heuristic classification (step 4), use the deterministic decision tree below instead of relying on subject keywords alone.

### Heuristic Decision Tree

#### 1. 10-Signal Heuristic Scoring (Get-HeuristicScore)

The hourly auto-sorter uses a 10-signal heuristic scorer (`scripts/Get-HeuristicScore.ps1`) that evaluates message headers, sender patterns, body content, and business-context relevance. Signals S1–S8 were added 2026-05-02. Signals S9–S10 were added 2026-05-08.

**Signals:**

| # | Signal | Source | Weight | Trigger |
|---|--------|--------|--------|---------|
| S1 | List-Unsubscribe header | Message headers | +1.0 | Header present AND sender not in do-not-block |
| S2 | Reply-To differs from From | Message headers | +0.5 | Reply-To domain ≠ From domain |
| S3 | Campaign subdomain/sender | Sender domain/email | +1.0 / +0.5 | Domain starts with `campaign.`, `email.`, `news.`, etc. (+1.0); or sender prefix like `campaign@`, `mailer@` (+0.5) |
| S4 | Cold outreach body patterns | Subject + Body | +2.0 | ≥2 of: company/project mention, discovery language ("found you"), guest/interview offer, services pitch (enhanced with "we provide", "verified list", "tele-verified", "pricing details", "expansion or outreach") |
| S5 | Webinar/training urgency | Body content | +1.5 | ≥2 of: "Register Now", webinar+time keywords, duration+speaker, compliance fear-bait |
| S6 | MCA/funding sales language | Body content | +2.0 | ≥2 of: "no credit check", $ amounts, "consolidation"+"advances", prequalification |
| S7 | Duplicate delivery | Graph history | +1.0 | ≥2 copies from same domain within 30 days |
| S8 | Suspicious domain | Sender domain | +1.0 | Long compound domain (≥20 chars), .org for commercial sales, suspicious TLDs, ccsend.com relay |
| S9 | B2B data/list sales | Subject + Body | +2.0 | ≥2 data-broker patterns from `business-context.json` `dataBrokerPatterns` (e.g., "verified email list", "decision-makers", "sample and pricing", "tele-verified") |
| S10 | Topic relevance mismatch | Subject + Body | +1.0 / +1.5 | No positive-relevance keyword from `business-context.json` `positiveRelevanceKeywords` present AND ≥1 irrelevant-topic keyword from `irrelevantTopics` present. +1.5 when combined with S9 data/list-sales match. |

**Business context:** S9 and S10 use `config/business-context.json` (derived from the Packaged Agile knowledge graph) to detect data-broker patterns and zero-relevance cold outreach without external APIs. The file contains positive-relevance keywords (agile, DevSecOps, federal, Army, Jira, etc.), irrelevant-topics (grocery retail, dental, crypto, etc.), and data-broker patterns (verified email list, decision-makers, tele-verified, etc.).

**Score thresholds:**
- `0–1.0`: Continue to Urgent/Today/Later priority tree
- `1.5–2.5`: Route to `Inbox Later` (suspicious but not definite junk)
- `3.0+`: Route to `Inbox Junk`

If Microsoft/Exchange headers are available, treat `BULK`, `SPM`, `HSPM`, `PHSH`, high `SCL`, or high `BCL` as strong junk/bulk evidence unless the sender is explicitly overridden or allowlisted.

#### 2. Urgent is intentionally narrow

Classify as `Inbox Urgent` only when **all** of these are true:

1. Sender is a known human colleague, client, partner, government contact, or user-designated important sender.
2. The person directly asks Dave for help, input, approval, or action.
3. The action is due within 2 hours or is same-day critical.
4. The message is not automated, newsletter, marketing, conference/event promotion, webinar, product update, stock/investment pitch, cold outreach, or system-generated.

Urgency keywords alone never make an email Urgent. Automated senders (`noreply@`, `no-reply@`, `notification@`, `notifications@`, `updates@`, etc.) and cold outreach are never Urgent regardless of subject wording.

#### 3. Today requires a known-human action

Classify as `Inbox Today` only when a known human sender likely needs Dave to respond or act today or this week. Do not classify as Today solely because the subject contains deadline words such as `tomorrow`, `last chance`, `time sensitive`, `action required`, `closing soon`, or `deadline`.

Marketing, webinars, vendor updates, automated notifications, bulk announcements, newsletters, conference/event registration, discount codes, product promotions, and cold outreach go to `Inbox Later` or `Inbox Junk` even when they contain deadline language.

#### 4. Later is the default for non-actionable wanted mail

Classify as `Inbox Later` for wanted but non-actionable mail, including:

- newsletters and Substack-style writing
- product updates and release notes
- GitHub notifications
- webinars, event registration, conference marketing, and matchmaking/event reminders
- government opportunity alerts and market intelligence updates
- vendor FYI notifications
- automated reminders from non-human senders
- receipts, account notices, and platform notifications that do not require same-day action
- any email that does not require a direct response or action from Dave

4. **Move** the email to the specific matching folder using `Move-MgUserMessage -DestinationId $folderId`.

## Execution Pattern

1. Inform user you are starting the auto-sort sweep (if run manually).
2. Fetch unread list.
3. Loop through top emails. Skip those already in categorized sub-folders.
4. Move each to its designated category folder.
5. Provide a summary count:
```text
Sweep complete.
🔴 2 moved to Inbox Urgent
🟡 5 moved to Inbox Today
🟢 4 moved to Inbox Later
   ⚫ 14 moved to Inbox Junk
```

## Related Skills

- **email-routing-config** — Interactive skill for managing routing rules (overrides, allowlists, blocklists). Use when the user asks to route a sender to a specific folder.
- **outlook-inbox-triage** — Interactive triage where you decide what to do with each email. Use when you want to review and discuss emails before acting.
- **email-draft-reply** — Draft replies in Dave's voice. Use after triage when a response is needed.
- **email-to-clickup** — Convert an email into a ClickUp task and archive it. Use for emails that require deeper work.
