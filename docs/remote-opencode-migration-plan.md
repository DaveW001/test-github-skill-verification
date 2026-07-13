# Remote OpenCode Migration Plan

**Date:** July 8, 2026  
**Status:** Research complete, ready for implementation  
**Goal:** Run OpenCode on existing VPS and access from phone, iPad, and laptop while preserving current local workflows

---

## Executive Summary

OpenCode already ships remote-access as a first-class feature. The TUI is just a client; all the real work (repo access, tool execution, model calls) happens in the server. Your VPS is the correct host for always-on scheduled jobs.

**Recommendation:** Tailscale + `opencode web` as primary access, with layered solutions for specific needs (native mobile apps, SSH/tmux fallback, VPS browser environment for Chrome DevTools).

**Total additional cost:** $0 (VPS already paid; Tailscale free for personal use)

---

## Part 1: OpenCode's Built-in Remote Capabilities

### Three native commands

1. **`opencode serve`** — headless HTTP API server (OpenAPI 3.1 spec at `/doc`). No UI. For custom clients, automation, or mobile apps.
2. **`opencode web`** — API server **plus** web UI in one. Best for opening a browser tab on phone/iPad/laptop.
3. **`opencode attach <url>`** — connect a local TUI (on your laptop) to a server running elsewhere.

### Key flags

- `--hostname 0.0.0.0` — bind to all interfaces (needed for remote access)
- `--port 4096` — default port
- `--mdns` — LAN service discovery
- `--cors` — cross-origin resource sharing

### Authentication

Set `OPENCODE_SERVER_PASSWORD` to enable HTTP basic auth:
```bash
OPENCODE_SERVER_PASSWORD=your-strong-password opencode web --hostname 0.0.0.0 --port 4096
```

Optional: `OPENCODE_SERVER_USERNAME` (defaults to `opencode`)

**Note:** Current OpenCode versions support `opencode attach --password` and `--username` flags. Older versions had bugs — upgrade before relying on remote attach.

---

## Part 2: The Five Options

All use your existing VPS. They differ in exposure model, setup complexity, and mobile UX.

### Option 1: VPS + `opencode web` + Tailscale ⭐ **RECOMMENDED DEFAULT**

**Cost:** $0  
**Exposure:** Private mesh only  
**Mobile UX:** Excellent (browser)  
**Setup:** Low

Free personal mesh VPN (100 devices). Install on VPS + phone + iPad + laptop; each gets stable `100.x.y.z` IP. Browse to `http://100.x.y.z:4096`.

**Security:**
- No public exposure, no port forwarding
- WireGuard-encrypted end-to-end
- Tailscale *is* your auth layer (only your devices can reach it)
- Bind to `0.0.0.0` but lock port with firewall rule:
  ```bash
  sudo ufw allow in on tailscale0 to any port 4096
  ```

**Community consensus:** Overwhelming recommendation across Reddit, blogs, and GitHub discussions.

### Option 2: VPS + `opencode web` + Cloudflare Tunnel + Access

**Cost:** $0 (Cloudflare Tunnel free, Access free ≤50 users)  
**Exposure:** Public HTTPS URL  
**Mobile UX:** Excellent (browser)  
**Setup:** Medium

Free tunnel gives public `https://opencode.yourdomain.com` with automatic TLS, no port forwarding, behind Cloudflare's edge. Add **Cloudflare Access** for email-OAuth/GitHub/Google auth.

**Best for:**
- Shareable link (teammates, contractors)
- Access from devices you don't fully control
- Fine-grained auth policies

**Trade-offs:**
- More moving parts than Tailscale
- Quick-tunnel URLs rotate on restart
- Named tunnel requires domain on Cloudflare DNS

**Community tools:**
- `octunnel` — one-command Cloudflare Tunnel wrapper
- `opencode-remote` — Cloudflare Container sharding (needs Workers Paid ~$5/mo)

### Option 3: VPS + `opencode serve` + Native Mobile Client

**Cost:** $0 (apps free/open-source)  
**Exposure:** Private or tunnel  
**Mobile UX:** Best (native)  
**Setup:** Medium

Pair headless API with purpose-built mobile apps:

**Android:**
- **OpenCode Mobile** (`dzianisv/opencode-mobile`) — open-source, F-Droid
- Streaming chat, side-by-side diff viewer, **tool-call approval UI**, biometric unlock, secure credential storage, multi-connection

**iOS:**
- **WhisperCode** — connects to your `opencode serve`

**Connection methods:** LAN / Tailscale / Cloudflare Tunnel / ngrok

**Caveats:**
- iPad/tablet layout is *planned, not shipped* (use browser web UI on iPad for now)
- Some fork connection quirks with Tailnet-only endpoints (GitHub issue #16)

### Option 4: VPS + SSH + tmux/zellij + Terminal App

**Cost:** $0  
**Exposure:** Private (SSH)  
**Mobile UX:** Doable, awkward  
**Setup:** Low

Power-user fallback. Run opencode inside `tmux new -s oc`; detach/reattach from anywhere — session, history, context all preserved.

**Mobile apps:**
- Termius (iOS/Android)
- Blink Shell (iOS)
- a-Shell (iOS)
- Moshi (purpose-built for coding agents)
- Termux (Android)

**Best for:**
- Running scripts, checking logs
- Shell ops the web UI can't do
- Full TUI access

**Reddit consensus:** Terminal is "good," web UI is "awesome" — complements, doesn't replace, Option 1.

**Pro tip:** Add `mosh` for flaky mobile connections.

### Option 5: VPS + Caddy/nginx Reverse Proxy + TLS + Basic Auth

**Cost:** $0 (+~$10/yr domain)  
**Exposure:** Public, self-managed  
**Mobile UX:** Excellent (browser)  
**Setup:** High

Full self-managed control with your own domain. Caddy gives automatic Let's Encrypt HTTPS. Set `OPENCODE_SERVER_PASSWORD` and put it behind the proxy.

**Better alternatives for Option 5:**
- **code-server / OpenVSCode Server** — full editor + terminal from browser alongside OpenCode
- **VS Code Remote SSH** from laptop + OpenCode web for mobile
- **VPS remote desktop / noVNC / Kasm** — if Chrome DevTools is essential
- **Tailscale Serve / Funnel** — built into Tailscale, no extra proxy needed

**When to use:** You already run a web stack on the VPS or want zero third-party dependencies.

---

## Part 3: Recommended Implementation Strategy

### Decision tree for your situation

1. **If you mainly need chat/code-agent access from phone/iPad/laptop:**  
   Tailscale + `opencode web` on VPS (Option 1)

2. **If you need terminal/editor workflows:**  
   Add SSH/tmux or code-server/OpenVSCode

3. **If you need Chrome DevTools/control-chrome:**  
   Add headless Chrome or remote desktop on VPS (**this is the gating question**)

4. **If you need reliable scheduled jobs:**  
   Migrate scheduler configs, validate timers/logs, test contention with long-running server

### My recommendation for you

**Primary:** Option 1 (Tailscale + `opencode web` on the VPS), with Options 3 and 4 layered on.

- Run it as a **systemd user service** with `loginctl enable-linger` so it survives reboots and runs without an active SSH session (this is what keeps your scheduled jobs alive 24/7).
- Set `OPENCODE_SERVER_PASSWORD` as a belt-and-suspenders layer even inside the tailnet.
- Use the **browser web UI** on iPad/phone for review and quick prompts; install **OpenCode Mobile/WhisperCode** for native tool-approval + diffs; keep **SSH+tmux** for shell ops.

**Reference systemd unit:**
```ini
# ~/.config/systemd/user/opencode.service
[Unit]
Description=OpenCode Server
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/home/you/.opencode/bin/opencode web --hostname 0.0.0.0 --port 4096
Restart=on-failure
Environment=OPENCODE_SERVER_PASSWORD=your-strong-password

[Install]
WantedBy=default.target
```

**Enable and start:**
```bash
systemctl --user daemon-reload
systemctl --user enable --now opencode
loginctl enable-linger your-username
```

**Verify port isn't public:**
```bash
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://$(curl -s ifconfig.me):4096
# Should time out (exit code 28). A status code means firewall rules aren't applied.
```

---

## Part 4: Critical Migration Checklist

### 4.1 Chrome/Control-Chrome MCP (GATING CONCERN)

Your current workflow uses Chrome DevTools / control-chrome MCP. On a VPS, this doesn't "just work."

**Decision required:** Do your Chrome workflows require:
- A real logged-in browser profile (cookies, extensions, interactive debugging)?
- Or can they work with headless page inspection?

**If logged-in profile needed:**
- **Remote desktop / noVNC / Kasm** on VPS
- Dedicated browser profile on VPS (your local Chrome profile won't be there)
- Sync cookies/sessions manually or via extension

**If headless OK:**
- **Headless Chromium** with `--remote-debugging-port=9222 --no-sandbox --headless=new` as a systemd service
- Point Chrome DevTools MCP at it via `--browser-url=http://127.0.0.1:9222`

**Reference setup (from bergkaese.dev):**
```bash
# Install chromium-browser via apt
# Start Chromium Browser MCP
pkill -f "chromium.*user-data-dir=/tmp/chrome-profile" 2>/dev/null || true

chromium-browser \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile \
  --disable-gpu \
  --no-sandbox \
  --disable-dev-shm-usage \
  --headless=new
```

**Systemd service:**
```ini
# ~/.config/systemd/user/chrome-mcp.service
[Unit]
Description=Chromium Browser for Chrome DevTools MCP
After=network.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5
ExecStart=/home/you/mcp-services/start-chrome-mcp.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**OpenCode config:**
```json
{
  "mcp": {
    "chrome": {
      "type": "local",
      "command": [
        "npx",
        "-y",
        "chrome-devtools-mcp@latest",
        "--browser-url=http://127.0.0.1:9222",
        "--slim"
      ],
      "enabled": true,
      "timeout": 30000
    }
  }
}
```

### 4.2 MCP Duplicate-Process Resource Bug (Issue #31554)

OpenCode spawns 2–4 duplicate processes *per* MCP server on Linux restart, and orphans accumulate. On a small VPS this exhausts `TasksMax` (~660MB+ wasted) and makes servers report "failed."

**Mitigation:**
- Raise `TasksMax` in systemd service (e.g., `TasksMax=500`)
- Limit MCP count (audit which MCPs you actually need on VPS)
- Restart cleanly (kill orphaned processes before restart)
- Monitor memory: `ps aux | grep opencode`
- Watch for `EAGAIN: resource temporarily unavailable, posix_spawn` errors

### 4.3 "Do Everything Locally" Ceiling

Local Windows paths, your local Chrome profile, local services, and some MCPs are inherently machine-bound.

**Action required:** Define explicitly which workflows *must* work remotely vs. stay laptop-only.

**Common gaps:**
- Windows paths in AGENTS.md → need Linux equivalents
- Local file paths in skills/references → update or conditionally load
- Local services (databases, dev servers) → replicate on VPS or tunnel
- Desktop-bound MCPs → audit and decide

### 4.4 Secrets & Provider Auth on VPS

**API keys and OAuth tokens must live on the VPS:**
- `~/.config/opencode/` — config, skills, references
- `~/.local/share/opencode/auth.json` — provider OAuth tokens
- `secrets-index.jsonc` — metadata index (never commit values)

**Headless provider OAuth uses device-code flow:**
1. Run `/connect` on VPS
2. Open printed URL on laptop/phone
3. Approve on that device
4. VPS polls for tokens and stores them; refresh is automatic

**Security:**
- Never commit secrets
- Tailscale shrinks attack surface
- Set `OPENCODE_SERVER_PASSWORD` as additional layer

### 4.5 Repos & Data on VPS

**Code and knowledge-base files must physically be on the VPS:**
- `git clone` with deploy keys (not personal access tokens if possible)
- Copy knowledge-base directories
- Update `AGENTS.md` path references (Windows → Linux)
- Verify file permissions and ownership

**Sync strategy:**
- Git for code repos
- rsync or syncthing for knowledge-base/docs
- Manual copy for one-time setup files

### 4.6 Scheduled-Job Migration

Your opencode-scheduler plugin uses **systemd user timers on Linux**.

**Migration checklist:**
- Jobs are scoped by `workdir` — configs/logs/runs live under `~/.config/opencode/scheduler/...`
- Logs under `~/.config/opencode/logs/...`
- `systemctl --user` + `loginctl enable-linger` (so timers run without active SSH)
- PATH/env/provider auth/MCP configs must exist in the systemd user environment
- **Scheduled runs may contend with the long-running server** for:
  - Model quotas (5-hour and weekly limits)
  - MCP processes (memory, locks)
  - Browser profile access (if Chrome MCP is shared)

**Validation commands:**
```bash
systemctl --user list-timers | grep opencode
journalctl --user -u opencode-scheduler -f
opencode mcp list
```

**Test with a non-critical job first** before migrating email triage / knowledge-base jobs.

### 4.7 VPS Sizing

Inference is offloaded to API providers (no GPU needed), so:
- **2 vCPU / 4–8 GB RAM / 20 GB+ disk** is fine for lightweight OpenCode
- **8 GB RAM is safer** given Chrome + MCPs + scheduler contention
- Monitor: `htop`, `free -h`, `df -h`

### 4.8 TLS / Secure-Context Caveat

Tailscale is encrypted, so HTTP-on-tailnet is safe — *but* some browser features (clipboard, service workers) require an HTTPS **secure context**.

**If you hit this:**
- Use `tailscale serve` or `tailscale funnel` for HTTPS
- Or use Caddy for automatic Let's Encrypt
- Or accept the limitation (clipboard may not work over HTTP)

### 4.9 Backups

**VPS can die. Back up:**
- `~/.config/opencode` — config, skills, references, scheduler jobs
- `~/.local/share/opencode` — auth.json, sessions DB, accounts
- Scheduler logs/runs under `~/.config/opencode/logs/...`
- Provider auth, MCP OAuth state
- Project repos (git remotes are the backup)
- Knowledge-base directories
- `.env` / secret files (store securely, e.g., encrypted archive)

**Schedule:** Weekly automated backup to external storage (S3, Backblaze B2, or another VPS).

### 4.10 Security Baseline

"Basic security is fine" shouldn't mean "bind 0.0.0.0 on public internet with only basic auth over HTTP." OpenCode can run shell commands and edit files.

**Safe baseline:**
- **Tailscale-only access** (or firewall port 4096 to Tailscale interface only)
- `OPENCODE_SERVER_PASSWORD` set
- **No public HTTP exposure** unless behind HTTPS + Cloudflare Access / reverse proxy
- Provider secrets protected (device-code OAuth flow for headless)
- Regular security updates: `sudo apt update && sudo apt upgrade`
- Fail2ban for SSH (if exposed)

---

## Part 5: Phased Implementation Plan

### Phase 1: Base Remote Access (1-2 hours)
1. Install Tailscale on VPS + phone + iPad + laptop
2. Install OpenCode on VPS
3. Set `OPENCODE_SERVER_PASSWORD`
4. Create systemd user service for `opencode web`
5. Enable linger: `loginctl enable-linger`
6. Configure firewall: `sudo ufw allow in on tailscale0 to any port 4096`
7. Test access from phone browser: `http://100.x.y.z:4096`

### Phase 2: Environment Migration (2-4 hours)
1. Clone repos to VPS with deploy keys
2. Copy knowledge-base directories
3. Update `AGENTS.md` path references (Windows → Linux)
4. Migrate secrets (API keys, OAuth tokens) using device-code flow
5. Audit MCP servers — decide which must work remotely
6. Test basic OpenCode workflows from phone

### Phase 3: Chrome/Control-Chrome MCP (2-3 hours)
1. Decide: headless Chromium or remote desktop?
2. Install and configure browser environment on VPS
3. Set up systemd service for headless Chrome
4. Update OpenCode MCP config to point to VPS browser
5. Test Chrome DevTools workflows from phone

### Phase 4: Scheduler Migration (1-2 hours)
1. Copy scheduler configs to VPS
2. Verify systemd user environment (PATH, env vars)
3. Test with a non-critical job
4. Migrate email triage / knowledge-base jobs
5. Validate timers, logs, contention with long-running server

### Phase 5: Mobile Client Setup (30 min)
1. Install OpenCode Mobile (Android) or WhisperCode (iOS)
2. Configure connection to VPS via Tailscale
3. Test streaming chat, diff viewer, tool-call approval
4. Set up biometric unlock

### Phase 6: Security & Backup Hardening (1 hour)
1. Set up weekly backup job (config, auth, sessions, knowledge-base)
2. Verify firewall rules (port 4096 not public)
3. Test failover: kill VPS, restore from backup
4. Document recovery procedure

**Total estimated time:** 7-12 hours over 2-3 days

---

## Part 6: Validation Commands

After each phase, verify:

```bash
# OpenCode server status
systemctl --user status opencode
journalctl --user -u opencode -f

# Tailscale connectivity
tailscale status
curl -I http://100.x.y.z:4096

# Port not public
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://$(curl -s ifconfig.me):4096

# MCP servers
opencode mcp list

# Scheduler
systemctl --user list-timers | grep opencode
journalctl --user -u opencode-scheduler -f

# Resource usage
htop
free -h
df -h
```

---

## Part 7: Cost Summary

| Component | Cost |
|-----------|------|
| VPS (existing) | $0 (already paid) |
| Tailscale (personal, 100 devices) | $0 |
| OpenCode | $0 (open-source) |
| OpenCode Mobile / WhisperCode | $0 (open-source) |
| Cloudflare Tunnel (if used) | $0 |
| Cloudflare Access (≤50 users) | $0 |
| Custom domain (optional) | ~$10/yr |
| Cloudflare Workers Paid (if using opencode-remote) | ~$5/mo |
| **Total for recommended setup** | **$0** |

---

## Part 8: Sources

- OpenCode official docs: https://opencode.ai/docs/server/
- Jakob Osterberger's guide: https://www.jakobosterberger.com/posts/opencode-server-tailscale/
- BSWEN comparison: https://docs.bswen.com/blog/2026-03-24-opencode-remote-access-cloudflare-tailscale/
- Vibe Co-Pilot supervision guide: https://www.vibebrowser.app/blog/2026-05-26-opencode-server-tailscale-agent-supervision
- bergkaese.dev Chrome MCP setup: https://bergkaese.dev/articles/opencode-and-chromium-via-mcp
- OpenCode Mobile: https://github.com/dzianisv/opencode-mobile
- GitHub issue #31554 (MCP duplicate processes): https://github.com/anomalyco/opencode/issues/31554
- Reddit discussions: r/opencodeCLI, r/ClaudeCode, r/selfhosted

---

## Next Steps

**Before starting implementation, answer this:**

> Do your Chrome/control-chrome workflows require a real logged-in browser profile (cookies, extensions, interactive debugging), or can they work with headless page inspection?

That determines whether the VPS setup is straightforward (headless Chromium) or needs a full browser environment (remote desktop / noVNC).

Once that's clarified, proceed with Phase 1.

---

**Document location:** `C:\development\opencode\docs\remote-opencode-migration-plan.md`
