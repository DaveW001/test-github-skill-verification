# Decision: Quick Public Hosting for a Single Static Web Page

**Date:** 2026-06-14
**Status:** Decided / In use
**Impact:** Reusable pattern for publishing low-volume, temporary, anonymous static pages (e.g., one-off HTML reports)

---

## Context and problem statement

We needed to publish a single, self-contained HTML file (the DCP Token Savings Report - ~29 KB, one inline `<style>` block, zero external scripts/refs) so a small number of people could view it via a public link.

**Constraints:**

- **Low volume:** ~10-20 views/day for ~1 week, then effectively dead. (~140 views total, ~4 MB egress - trivially under any free tier.)
- **Free.**
- **Easy and fast to publish.**
- **Anonymous re: Packaged Agile:** the host and URL must not reveal that Packaged Agile is serving it. Better if viewers cannot tell.
- **Separate from the main website** (`packagedagile.com`) - do not host it there.
- **Temporary** - should be easy to tear down afterward.

**Existing footprint we can reuse:** Vercel (2025-pa-website, clickup-contact-entry, command-center, marketing-materials) and Firebase Hosting (command-center, margin-calc-firebase).

## Options evaluated

| Option | Free? | Reveal PA? | Setup | Persistence | Verdict |
|---|---|---|---|---|---|
| **Vercel CLI** (existing account) | Yes - static HTML is not counted as a build | No, via clean alias | Low - reuse auth, one command | Stable alias | CHOSEN |
| Netlify Drop | Yes (100 GB/mo) | No | Lowest - drag file, no account | Unclaimed sites may be cleaned up; claim to keep | Runner-up |
| Surge.sh | Yes (unlimited projects) | No | Low - CLI, one-time email/pw | Persistent | Good CLI alternative |
| Cloudflare Pages | Yes (unlimited bandwidth) | No | Medium - account + direct upload | Persistent | Overkill (unlimited BW unneeded) |
| Firebase Hosting (existing) | Yes | No (`*.web.app`) | Medium - `firebase init` + `public/` + project | Persistent | Heavier friction than warranted for one file |
| GitHub Pages | Yes | Yes - GitHub account appears in URL | Medium - repo + branch config | Permanent | Rejected (account exposure + Git steps) |
| Tiiny.host | Free tier | No | Lowest | Free links expire 24h-7d | Rejected - too short for a week |
| Paste-host newcomers (HTMLPub, host-html, HTMLPUT) | Free tier | No | Lowest | Short/unclear expirations; less established | Rejected - trust + longevity |
| packagedagile.com (Vercel site) | Yes | Yes | n/a | Permanent | Rejected by requirement |

**Key clarifications from the 2026 research:**

- **Vercel is not the same as packagedagile.com.** A standalone Vercel project gets its own neutral `*.vercel.app` subdomain. Viewers see "Vercel," not Packaged Agile. Hosting static files (an `index.html`) on Vercel is explicitly **not** classed as a build, so it consumes no build minutes and is free.
- All of Vercel / Netlify / Surge / Cloudflare expose only their own neutral subdomains to a viewer - none reveal PA.
- Free-tier bandwidth (Vercel 100 GB/mo, Netlify 100 GB/mo, Cloudflare unlimited) is a non-issue at ~4 MB total.

## Decision

**Use the Vercel CLI** to deploy the single HTML file as a new standalone project under the existing account.

Rationale:

1. Auth and tooling already in place (Vercel CLI installed; `vercel login`).
2. Free; static HTML is not a build.
3. The clean production alias (`<project>.vercel.app`) is neutral - no PA in the URL or the served HTML.
4. Trivial publish and teardown.

**Fallback** if an absolute-zero PA footprint is ever required (not even in a buried deployment URL): use **Netlify Drop** (no account/team at all) or a throwaway Vercel account.

## How to publish (reusable)

```powershell
# 1. Stage the file as index.html in a throwaway folder named after the slug you want
$src  = "<path-to-your-file>.html"
$dir  = "$env:TEMP\opencode\<neutral-slug>"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
Copy-Item -LiteralPath $src -Destination "$dir\index.html"

# 2. Deploy to production (reuses the existing Vercel login)
vercel deploy --prod --yes
#   project slug = folder name  ->  public URL: https://<neutral-slug>.vercel.app

# 3. Verify it is live
Invoke-WebRequest https://<neutral-slug>.vercel.app -UseBasicParsing | Select-Object StatusCode
```

**Slug naming:** the folder name becomes the project slug and the public alias. Pick something neutral and globally unique (Vercel slugs are unique across ALL users; if taken, Vercel appends a random suffix). Avoid names containing "pa", "packaged", etc.

## CRITICAL: share ONLY the alias

Vercel creates two URLs per deploy:

- **Alias (share this):** `https://<project>.vercel.app` - clean, stable, neutral.
- **Deployment-specific URL:** `https://<project>-<hash>-<team-slug>.vercel.app` - contains the **team slug** (e.g., `pa-projects-0025`), which reveals PA. Never share this or the dashboard/inspect link.

The alias does not redirect and does not expose the team slug to viewers.

## How to tear down (after the temp window)

```powershell
vercel remove <project-slug> --yes
```

Deletes the project and its URLs entirely. Optionally also delete it from the Vercel dashboard.

## Instance record

| Field | Value |
|---|---|
| Date deployed | 2026-06-14 |
| Project / slug | `dcp-savings-2026` |
| Account | `davew001` |
| Vercel team | `pa-projects-0025` |
| Source file | `.conductor/tracks/20260613-dcp-token-savings-analysis/artifacts/dcp-savings-report.html` |
| Public link (alias) | https://dcp-savings-2026.vercel.app |
| Verified | HTTP 200; title "DCP Token Savings Report"; served HTML neutral (no PA references) |
| Teardown | `vercel remove dcp-savings-2026 --yes` |
