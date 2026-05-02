# Google MCP Server Evaluation

**Date:** 2026-04-29
**Track:** 20260429-email-calendar-mcp-audit
**Phase:** 3 (Research)
**Author:** OpenCode Research Agent

---

## Executive Summary

Evaluated 4 npm packages for Google Gmail + Calendar MCP integration in OpenCode. The ideal candidate must support both Gmail and Calendar, work with `npx -y` (or `bunx`), use OAuth2 (not service account), and be actively maintained.

**Winner: `mcp-google`** — Only npx-compatible package covering Calendar + Gmail + Contacts in a single server. Built on the proven `@cocal` foundation. Trade-off: small community and no recent commits.

**Strong Alternative: `@cocal/google-calendar-mcp`** — Best-in-class calendar-only server (1.1k stars, 16k weekly downloads). Would need a separate Gmail MCP.

---

## Comparison Table

| Metric | `mcp-google` | `google-mcp` | `@cocal/google-calendar-mcp` | `@prmichaelsen/google-calendar-mcp` |
|---|---|---|---|---|
| **Latest Version** | 2.3.0 | 0.0.7 | 2.6.1 | 2.4.1 |
| **Total Versions** | 8 | 7 | 28 | 13 |
| **Weekly Downloads** | 56 | 28 | 16,345 | 13 |
| **Last Published** | 2025-07-01 | 2025-09-13 | 2026-03-02 | 2026-02-14 |
| **GitHub Stars** | 0 | 16 | 1,104 | N/A (repo 404) |
| **GitHub Forks** | 1 | 13 | 311 | N/A |
| **Last Commit** | 2025-07-01 | 2026-03-30 | 2026-03-30 | Unknown |
| **Open Issues** | 0 | 0 | 4 | N/A |
| **Dependencies** | 8 | 4 | ~10 | 3 |
| **License** | MIT | MIT | MIT | MIT |
| **Auth Method** | OAuth2 | OAuth2 or Service Account | OAuth2 | Service Account only |
| **Runtime** | npx (Node) | bunx (Bun) | npx (Node) | npx (Node) |
| **Gmail** | 14 tools | Yes (send, draft, attachments) | **No** | 3 tools (send, list, read) |
| **Calendar** | 8 tools | 5+ tools | 12 tools | 3 tools |
| **Contacts** | 5 tools | No (TODO) | No | No |
| **Drive** | No | Yes | No | No |
| **Tasks** | No | Yes | No | No |
| **Multi-Account** | No | No | Yes | No |

---

## Detailed Candidate Notes

### 1. `mcp-google` (RECOMMENDED)

**npm:** https://www.npmjs.com/package/mcp-google
**GitHub:** https://github.com/199-mcp/mcp-google

**Strengths:**
- Only npx-compatible package with Calendar + Gmail + Contacts in one server
- OAuth2 with direct env vars (GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET) — no JSON file needed
- Built on top of `@cocal/google-calendar-mcp` (nspady's proven codebase)
- Comprehensive Gmail tools: list, get, send, reply, labels, drafts, batch operations
- Comprehensive Calendar tools: CRUD, search, free/busy, recurring events, colors
- Contacts: list, get, create, update, delete
- Automatic token refresh
- Clean MCP config: `npx -y mcp-google`

**Weaknesses:**
- 0 GitHub stars, 1 fork — effectively no community
- No commits since July 1, 2025 (10 months dormant)
- Single maintainer (199-bio / Boris Djordjevic)
- 56 weekly downloads (very low)
- Dependencies include `express` (heavier than needed for stdio MCP)

**Tools (27 total):**
- Calendar: list-calendars, list-events, create-event, update-event, delete-event, search-events, get-freebusy, list-colors
- Contacts: list-contacts, get-contact, create-contact, update-contact, delete-contact
- Gmail: list-emails, get-email, send-email, update-email, delete-email, create-draft, update-draft, send-draft, list-labels, create-label, update-label, delete-label, batch-update-emails

**Auth Setup:**
- OAuth2 browser flow (opens localhost:3000 for callback)
- Env vars: `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`
- OR: `GOOGLE_OAUTH_CREDENTIALS` pointing to credentials JSON
- Token storage: auto-saved with 0600 permissions
- First run triggers browser OAuth flow

---

### 2. `google-mcp`

**npm:** https://www.npmjs.com/package/google-mcp
**GitHub:** https://github.com/vakharwalad23/google-mcp

**Strengths:**
- Broadest coverage: Gmail + Calendar + Drive + Tasks
- Supports both OAuth2 and Service Account auth
- Email attachment support (local files and Google Drive)
- Built-in token management with auto-refresh and re-authentication
- HTTP transport support in addition to stdio
- Recent GitHub activity (last push March 30, 2026)
- 16 stars, 13 forks — small but real community
- Bun is already installed on this machine (v1.3.4)

**Weaknesses:**
- **REQUIRES BUN RUNTIME** — entry point is raw TypeScript (`index.ts`), not compiled JS
- Cannot run with `npx` — must use `bunx`
- Pre-1.0 (v0.0.7) — unstable API
- 28 weekly downloads
- Contacts listed as TODO (not implemented)
- Bun dependency adds operational complexity
- Single maintainer

**Tools:**
- Gmail: send_email, draft_email, download_attachments, list, read, labels
- Calendar: list calendars, create events, list events, update, delete, free slots
- Drive: filter, sort, read, create, update, delete, share
- Tasks: view/create/delete lists, list tasks, create tasks, update, complete, delete

**Auth Setup:**
- OAuth2: `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET` + `GOOGLE_OAUTH_TOKEN_PATH`
- Service Account: `GOOGLE_CLIENT_EMAIL` + `GOOGLE_PRIVATE_KEY` + `GMAIL_USER_TO_IMPERSONATE`
- Browser OAuth flow on first run

---

### 3. `@cocal/google-calendar-mcp` (BEST FOR CALENDAR-ONLY)

**npm:** https://www.npmjs.com/package/@cocal/google-calendar-mcp
**GitHub:** https://github.com/nspady/google-calendar-mcp

**Strengths:**
- By far the most mature and popular Google Calendar MCP
- 1,104 GitHub stars, 311 forks — massive community
- 16,345 weekly downloads — proven production usage
- 28 versions, actively maintained (latest: March 2, 2026)
- Multi-account support (connect work + personal simultaneously)
- Advanced features: recurring events, event responses, image/PDF import
- Tool filtering to reduce context usage
- Docker support, HTTP transport
- Comprehensive documentation (auth guide, advanced usage, architecture)
- 198 commits, 23 releases

**Weaknesses:**
- **CALENDAR ONLY** — no Gmail, no Contacts, no Drive
- Would require a separate MCP server for email
- Requires credentials JSON file (no direct env var support)
- Test mode tokens expire after 7 days (must publish app or re-auth weekly)

**Tools (12 total):**
- list-calendars, list-events, get-event, search-events, create-event, update-event, delete-event
- respond-to-event, get-freebusy, get-current-time, list-colors, manage-accounts

**Auth Setup:**
- OAuth2 with `GOOGLE_OAUTH_CREDENTIALS` env var pointing to JSON file
- Browser OAuth flow on first run
- Multi-account via `manage-accounts` tool or CLI `npm run account auth <nickname>`
- Must publish app to avoid weekly re-auth

---

### 4. `@prmichaelsen/google-calendar-mcp`

**npm:** https://www.npmjs.com/package/@prmichaelsen/google-calendar-mcp
**GitHub:** https://github.com/prmichaelsen/calendar-mcp-server (returns 404 — private or deleted)

**Strengths:**
- Calendar + Gmail in one package
- Service account auth (no browser flow needed)
- 3 dependencies (minimal footprint)
- Factory pattern for multi-tenant use

**Weaknesses:**
- **Service Account only** — requires Google Workspace admin access + domain-wide delegation
- Cannot be used with personal Gmail accounts
- GitHub repo is 404 (private or deleted) — no source code visibility
- 13 weekly downloads — almost no users
- Only 3 Gmail tools (send_email, list_emails, read_email) — very limited
- Only 3 Calendar tools — very limited
- All tools have `google_` prefix (v2.0 breaking change)
- Single maintainer, 13 versions in 2 days (Feb 13-14, 2026), then abandoned
- No Contacts support

**Tools (6 total):**
- Calendar: google_create_calendar_event, google_list_calendar_events, google_update_calendar_event
- Gmail: google_send_email, google_list_emails, google_read_email

**Auth Setup:**
- `GOOGLE_APPLICATION_CREDENTIALS`: path to service account JSON key
- `GOOGLE_CALENDAR_ID`: calendar ID (email or "primary")
- `GOOGLE_CALENDAR_SUBJECT`: email to impersonate
- Requires domain-wide delegation in Google Workspace admin console

---

## Scoring Matrix

| Criterion (Weight) | `mcp-google` | `google-mcp` | `@cocal` | `@prmichaelsen` |
|---|---|---|---|---|
| **Coverage** (25%) | 5 — Cal+Gmail+Contacts | 4 — Cal+Gmail+Drive+Tasks | 2 — Cal only | 3 — Cal+Gmail (limited) |
| **Maintenance** (25%) | 1 — Dormant 10mo | 3 — Recent activity | 5 — Active, 1.1k stars | 1 — Repo gone |
| **Auth Simplicity** (20%) | 5 — OAuth2, env vars | 3 — OAuth2 but needs Bun | 4 — OAuth2, file-based | 2 — Service account only |
| **npx Compat** (15%) | 5 — Full npx support | 1 — Requires bunx | 5 — Full npx support | 3 — npx may work |
| **Stability** (15%) | 2 — 0 stars, single dev | 2 — Pre-1.0 | 5 — 28 versions, massive community | 1 — Repo 404 |
| **Weighted Total** | **3.55** | **2.70** | **3.85** | **2.05** |

---

## Recommendation: `mcp-google`

### Why `mcp-google` wins

1. **Only all-in-one npx package** — Calendar + Gmail + Contacts in a single MCP server that works with `npx -y`. No other package achieves this.

2. **Proven foundation** — Built on top of nspady's `@cocal/google-calendar-mcp` code (the 1.1k-star project), with Gmail and Contacts layers added on top.

3. **Simplest auth** — Direct `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` env vars. No JSON file juggling. Browser OAuth flow on first run.

4. **27 tools** — Most comprehensive tool coverage of any npx-compatible candidate.

5. **Existing Google Cloud project** — You already have project `gws-contacts-audit-20260306` with `dave.witkin@packagedagile.com` configured. Just need to enable Gmail API + People API + Calendar API and create OAuth credentials.

### Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| No community (0 stars) | Medium | Code is fork of proven @cocal; if abandoned, can fork and maintain |
| Dormant since July 2025 | Medium | Package is functional; no breaking changes likely needed |
| Single maintainer | Medium | MIT licensed; can be forked if needed |
| 8 dependencies (including express) | Low | Well-known dependencies; express only used for OAuth callback |

### Fallback Plan

If `mcp-google` proves unreliable:
1. Switch to `@cocal/google-calendar-mcp` for calendar (proven, maintained)
2. Add a separate Gmail-only MCP server (e.g., `google-mcp` via bunx for Gmail only)
3. Or evaluate `@pegasusheavy/google-mcp` (199 weekly downloads, covers everything) as an emerging alternative

---

## Setup Steps for `mcp-google`

### Step 1: Google Cloud Console Configuration

The existing project `gws-contacts-audit-20260306` can be reused.

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → select project `gws-contacts-audit-20260306`
2. **Enable APIs:**
   - Google Calendar API (may already be enabled)
   - Gmail API
   - Google People API (for Contacts)
3. **Configure OAuth Consent Screen:**
   - APIs & Services → OAuth consent screen
   - User type: External
   - Fill in app name (e.g., "OpenCode MCP")
   - Add `dave.witkin@packagedagile.com` as test user
   - Add scopes: `calendar`, `gmail`, `contacts`
4. **Create OAuth 2.0 Credentials:**
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: **Desktop app**
   - Name: "OpenCode MCP Client"
   - Note the **Client ID** and **Client Secret**
5. **Publish to Production** (optional but recommended to avoid weekly re-auth):
   - OAuth consent screen → PUBLISH APP
   - Accept the "unverified app" warning

### Step 2: OpenCode MCP Configuration

Add to OpenCode's MCP server config:

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "npx",
      "args": ["-y", "mcp-google"],
      "env": {
        "GOOGLE_CLIENT_ID": "<CLIENT_ID>.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "<CLIENT_SECRET>"
      }
    }
  }
}
```

### Step 3: First-Run Authentication

1. Start OpenCode / trigger the MCP server
2. Browser window opens at `localhost:3000/oauth2callback`
3. Sign in as `dave.witkin@packagedagile.com`
4. Grant Calendar + Contacts + Gmail permissions
5. Tokens are saved automatically for future use

---

## Existing Google Infrastructure

| Item | Value |
|---|---|
| gcloud CLI | Installed |
| Active Account | `dave.witkin@packagedagile.com` |
| Active Project | `gws-contacts-audit-20260306` |
| Workspace Domain | `packagedagile.com` |
| Credentials DB | `%APPDATA%\gcloud\credentials.db` (exists) |
| Access Tokens DB | `%APPDATA%\gcloud\access_tokens.db` (exists) |
| Bun Runtime | v1.3.4 installed |
| GOOGLE env vars | None set |

---

## Packages Discovered But Not in Original Scope

During research, these additional packages were found:

| Package | Weekly Downloads | Coverage | Notes |
|---|---|---|---|
| `@pegasusheavy/google-mcp` | 199 | Cal+Gmail+Drive+Docs+Sheets+Slides+Meet+Chat+Forms+YouTube+Tasks+Contacts | Most comprehensive, but only 3 versions (Dec 2025), OAuth2 |
| `@chieflatif/google-mcp` | 4 | Gmail+Calendar+Sheets+Docs+Drive | 2 versions, OAuth2 |
| `@bakhshb/google-mcp` | 8 | Gmail+Calendar (10 tools, 2 deps) | Minimal, 1 version |
| `mcp-google-calendar-plus` | 4 | Calendar+Contacts | Same author as `mcp-google` |

If `mcp-google` doesn't work out, `@pegasusheavy/google-mcp` is worth evaluating — it has the broadest Google Workspace coverage of any package found.
