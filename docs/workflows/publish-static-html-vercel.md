# Workflow: Publish a Static HTML Page to a Public URL (Vercel CLI)

**Purpose:** Publish any self-contained HTML file to a neutral, shareable public URL in under 60 seconds.
**Created:** 2026-06-22
**Last updated:** 2026-06-22
**Related:** `docs/decisions/quick-public-static-hosting-2026-06-14.md` (why Vercel was chosen over 7 alternatives)

---

## When to use this

You have a single, self-contained HTML file (inline CSS, no server, no build step) and you need a public link to share with others. Common cases:

- Status dashboards / project overviews
- One-off analysis reports
- Data visualizations
- Presentation handouts

This pattern is **not** for full web apps, multi-file sites, or anything that needs a build step.

## Prerequisites

- **Vercel CLI** installed: `npm i -g vercel` (check with `vercel --version`)
- **Logged in:** `vercel login` (one-time; reuses existing account `davew001` / team `pa-projects-0025`)
- **Self-contained HTML:** all CSS inline, no external script/CDN dependencies, no local file references

## The recipe (3 steps)

```powershell
# --- 1. STAGE: copy your HTML as index.html into a temp folder named after your slug ---

$slug = "<neutral-slug>"                          # e.g. "govpulse-status-2026"
$src  = "<path-to-your-file>.html"                # e.g. "C:\development\govpulse\GOVPULSE-STATUS.html"
$dir  = "$env:TEMP\opencode\$slug"

New-Item -ItemType Directory -Force -Path $dir | Out-Null
Copy-Item -LiteralPath $src -Destination "$dir\index.html"

# --- 2. DEPLOY: from inside that folder (folder name = project slug = URL alias) ---

Set-Location $dir
vercel deploy --prod --yes
#   -> Output includes: "Aliased: https://<neutral-slug>.vercel.app"

# --- 3. VERIFY: confirm it is live ---

Invoke-WebRequest "https://$slug.vercel.app" -UseBasicParsing | Select-Object StatusCode
#   Expected: 200
```

**Total time:** ~10-15 seconds.

## CRITICAL RULES

### 1. Share ONLY the clean alias URL

Vercel produces two URLs per deploy:

| URL type | Format | Contains team slug? | Share? |
|---|---|---|---|
| **Alias (clean)** | `https://<slug>.vercel.app` | NO | YES |
| **Deployment-specific** | `https://<slug>-<hash>-<team-slug>.vercel.app` | YES (`pa-projects-0025`) | **NEVER** |
| **Inspect link** | `https://vercel.com/<team-slug>/<slug>/...` | YES | **NEVER** |

Always share `https://<slug>.vercel.app`. Never paste the deployment URL or the dashboard inspect link in any external communication.

### 2. Pick a neutral slug

The folder name becomes the project slug and the public alias. Rules:
- **Neutral:** no "pa", "packaged", "packaged-agile", client names, or anything that identifies the org
- **Globally unique:** Vercel slugs are unique across ALL users; if taken, Vercel appends a random suffix (check the output)
- **Descriptive but generic:** `govpulse-status-2026`, `dcp-savings-2026`, `q3-margin-analysis`

### 3. The HTML must be truly self-contained

- All CSS in `<style>` tags (inline)
- All SVG inline
- No `<script src="...">`, no CDN links, no local file references
- If you need charts, use inline SVG (not Chart.js / D3 from a CDN)

## How to UPDATE an existing page (redeploy after editing)

When the source HTML changes and you want the same URL to show the new version:

```powershell
# The project already exists on Vercel; just re-stage and redeploy to the same slug.

$slug = "govpulse-status-2026"
$src  = "C:\development\govpulse\GOVPULSE-STATUS.html"   # updated file
$dir  = "$env:TEMP\opencode\$slug"

# If the temp folder still exists from the last deploy, just overwrite:
Copy-Item -LiteralPath $src -Destination "$dir\index.html" -Force
Set-Location $dir
vercel deploy --prod --yes

# The alias URL stays the same: https://govpulse-status-2026.vercel.app
# The new deployment goes live under that alias within seconds.
```

If the temp folder was cleaned up, repeat the full 3-step recipe above (it relinks to the existing project).

**Note:** Each redeploy creates a new deployment under the same project. Old deployments remain accessible via their unique URLs but the alias always points to the latest `--prod` deploy.

## How to TEAR DOWN (remove a page)

```powershell
vercel remove <project-slug> --yes
#   e.g. vercel remove govpulse-status-2026 --yes
```

This deletes the project and all its URLs (alias + deployments). Irreversible.

## Deployment log

Append a new row each time a page is published or updated.

| Date | Slug | Purpose | Source file | Public link | Deployed by | Status |
|---|---|---|---|---|---|---|
| 2026-06-14 | `dcp-savings-2026` | DCP token-savings analysis report (100 sessions) | `.conductor/tracks/20260613-dcp-token-savings-analysis/artifacts/dcp-savings-report.html` | https://dcp-savings-2026.vercel.app | Build agent | Live |
| 2026-06-22 | `govpulse-status-2026` | GovPulse project status overview (Phase 1 gate passed) | `C:\development\govpulse\GOVPULSE-STATUS.html` | https://govpulse-status-2026.vercel.app | Build agent | Live |

## Known deployments (detailed)

### govpulse-status-2026

| Field | Value |
|---|---|
| **Purpose** | GovPulse signal intelligence pipeline status overview |
| **First deployed** | 2026-06-22 |
| **Source file** | `C:\development\govpulse\GOVPULSE-STATUS.html` (23.7 KB) |
| **Content** | Single self-contained HTML: pipeline SVG diagram, phase roadmap, metrics dashboard, 2 live leads, decision gate status |
| **Public link** | https://govpulse-status-2026.vercel.app |
| **Vercel team** | `pa-projects-0025` (internal only - never share) |
| **Teardown** | `vercel remove govpulse-status-2026 --yes` |
| **Update cadence** | As needed (after each phase completion, major milestone, or weekly digest) |
| **Notes** | Phase 1 Decision Gate passed (2 leads, $0.75/run, 15/15 tests). Next update expected after Phase 2 or AC-7 review. |

### dcp-savings-2026

| Field | Value |
|---|---|
| **Purpose** | DCP (Dynamic Context Pruning) token-savings analysis report |
| **First deployed** | 2026-06-14 |
| **Source file** | `.conductor/tracks/20260613-dcp-token-savings-analysis/artifacts/dcp-savings-report.html` |
| **Public link** | https://dcp-savings-2026.vercel.app |
| **Teardown** | `vercel remove dcp-savings-2026 --yes` |
| **Related workflow** | `docs/workflows/re-run-dcp-report.md` (how to regenerate the report) |