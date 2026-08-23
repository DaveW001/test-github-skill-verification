# Workaround: Restore Native File Tools in OpenCode Desktop via Local `opencode serve`

**Status:** Active workaround (candidate - not yet adopted as default)
**Applies To:** OpenCode Desktop (Node.js sidecar) on Windows - native file tools fail with `Bun is not defined`
**Date Captured:** 2026-08-17
**Source:** anomalyco/opencode issue #35573, comment by panhaoyu (2026-08-16)

---

## TL;DR

OpenCode Desktop's built-in sidecar runs on **Node.js**, so the native file tools
(`read` / `write` / `edit` / `glob` / `grep`) fail instantly with
`Bun is not defined`. A commenter on our issue confirmed a workaround: start a
**Bun-based CLI server** (`opencode serve`) in a terminal, connect Desktop to it
via **Settings -> Add Server**, and run sessions against that server. Tool calls
are then executed by the Bun-based server instead of the Node sidecar, and all five
native file tools work. Verified by the commenter on **Desktop 1.18.18 / Windows 11**
- the same CLI version we are running (1.18.18).

---

## Issue context

- **Issue:** https://github.com/anomalyco/opencode/issues/35573
  - Title: "[Bug] Native built-in file tools (Read/Write/Edit/glob/grep) return \"Bun is not defined\" under Desktop"
  - **State: OPEN.** Filed by us (DaveW001) 2026-07-06 with canonical session-database
    evidence: 2,611 failing tool parts across 494 sessions (2026-05-31 -> 2026-07-06).
  - **Root cause (hypothesis):** The Desktop sidecar switched from Bun to Node.js;
    native tool implementations reference Bun globals / APIs (`Bun.file`,
    `Bun.write`, etc.) that do not exist in the Node sidecar process. Failures are
    2-4 ms, before any filesystem work.
- **Related issues:**
  - #25880 (open) - Desktop v1.14.39: Bun-target *plugins* fail to load (Node sidecar lacks Bun APIs). Shared underlying root cause.
  - #41033 (open) - native-tools variant still broken on Desktop 1.18.15 (cited by Talya1412 comment).
  - #25799 (closed) - earlier Bun-related report.
- **Key data points from comments:**
  - Installing Bun on the host does **NOT** fix it (Talya1412, 2026-08-07).
  - MCP-based file tools (`@modelcontextprotocol/server-filesystem`) work as an alternative since they are Node-based.
  - panhaoyu (2026-08-16) confirmed the `opencode serve` workaround below.

## What we use today (PowerShell-first protocol)

The canonical runbook
(`C:\Users\DaveWitkin\.config\opencode\docs\troubleshooting\tool-failure-bun-undefined.md`,
referenced by global AGENTS.md) directs us to switch the whole session to
PowerShell-first via the `bash` tool:

| Native tool | PowerShell equivalent |
|---|---|
| read | `Get-Content -LiteralPath <p> -Raw` |
| write | `Set-Content -LiteralPath <p> -Encoding utf8` (or verbatim here-string) |
| edit | `Select-String` to locate + literal `[string]::Replace()` (NOT regex `-replace`) |
| glob | `Get-ChildItem -Recurse` |
| grep | `Select-String` |

This works but **loses the native tools' structured output** and forces every file
operation through shell quoting - higher-variance and hazard-prone for structural
character edits (indentation bleed, quote balance, etc.). The serve workaround is a
potential upgrade because it restores the native tools themselves.

---

## The workaround (panhaoyu, 2026-08-16)

Source comment:
https://github.com/anomalyco/opencode/issues/35573#issuecomment-5307816389

**Why it works:** the CLI runs under Bun, so a server started from the CLI executes
tools in an environment where Bun globals exist.

### Steps

1. **Start the Bun-based CLI server** in a terminal: `opencode serve`
   Default settings, no extra arguments. The port is auto-generated and printed on
   startup (no need to specify it manually).
2. **Connect Desktop to the server:** Desktop **Settings -> Add Server**, connect to
   the local server.
3. **Open your project** in the connected server panel and **start a new session**.

### Verified result (commenter)

- `read` / `write` / `edit` / `glob` / `grep` all working.
- Environment: Desktop 1.18.18, Windows 11.
- **No computer or Desktop restart needed:** just restart the `opencode serve`
  process and reconnect.
- **Each server can host multiple projects;** opening a previous project reuses its
  session history.

---

## Local verification (2026-08-17)

- Our CLI is **1.18.18** - the same version the commenter verified.
- `opencode serve --help` confirms the command surface:
  - headless server, listens on `127.0.0.1` by default;
  - `--port` (default 0 = auto; observed 4096 in practice), `--hostname`,
    `--mdns` (LAN discovery via `opencode.local`), `--cors`, `--pure`.
- A short local smoke test booted the server successfully: printed
  `opencode server listening on http://127.0.0.1:4096` - and warned
  `OPENCODE_SERVER_PASSWORD is not set; server is unsecured.`
- The smoke-test process was stopped afterward (port 4096 freed; no residual process).

## CLI A/B test (2026-08-17): local vs. served - results match

**Method:** same probe prompt run twice - once plain CLI (Bun, no server) and once
attached to `opencode serve --port 4099` via
`opencode run --attach http://127.0.0.1:4099`. Probe steps: glob *.txt, read
sample.txt, create native-write.txt via apply_patch, edit sample.txt ("one" ->
"ONE"), grep for "native". Both runs used `--format json` so every tool call was
captured as a tool event with status; file effects were then verified on disk.

**Result: identical in both modes - everything succeeded:**

| Operation | Plain CLI (no server) | Served (attach 4099) |
|---|---|---|
| glob | completed | completed |
| read | completed | completed |
| write (apply_patch create) | completed | completed |
| edit (apply_patch replace) | completed | completed |
| grep | completed | completed |

- File effects confirmed on disk in both runs: sample.txt first line changed
  one -> ONE; native-write.txt created with exact content "native-write-ok".
- No `Bun is not defined` in either mode; exit code 0 in both.
- Toolset listing is identical in both modes (see toolset caveat below).
- Evidence: JSON event logs and fixture at
  `C:\Users\DaveWitkin\AppData\Local\Temp\oc-filetools-probe\`
  (baseline-files.json, served-files.json, toolset.json, served-toolset.json).

**Toolset caveat (important for expectations):** on this installation the agent
toolset exposes **apply_patch** for file writes/edits instead of native `write`
and `edit` (the first loose probe reported `write tool unavailable in the
provided toolset`; a direct toolset listing confirmed it). `read`, `glob`,
`grep` are exposed natively. This is identical locally and via the served
server, so a Desktop session connected to `opencode serve` should get the same
working behavior: native read/glob/grep plus apply_patch for write/edit.

**Bottom line:** the "works in CLI -> should work in Desktop via serve" premise
holds for everything the CLI can execute. The remaining unknown is Desktop's own
connection/UI layer (Settings -> Add Server), which cannot be exercised from the
CLI and requires a one-time Desktop trial.

## Why we might want to use it

- Restores native tool semantics and structured output - no PowerShell quoting or regex-escape hazards.
- Simple and reversible: start one process; restart it to reset.
- No Desktop/OS restart, no Bun reinstall, no config edits.
- Session history is preserved per project on the server.

## Tradeoffs / cautions (before we adopt it as default)

- **Extra long-running process.** If `opencode serve` dies, sessions routed through
  it break; scheduled/background jobs would need the server managed (startup,
  restart-on-failure).
- **Unsecured by default.** It binds localhost only (`127.0.0.1`), but the server
  explicitly warns when `OPENCODE_SERVER_PASSWORD` is unset. If we ever expose it
  (e.g. `--hostname 0.0.0.0` / `--mdns`), set a password first.
- **Not a fix.** Upstream still needs the runtime fix; track #35573 / #41033.
- **Not yet tested against our specific workflows** (plugins, MCP servers,
  control-chrome, Conductor child sessions). The commenter verified the five native
  file tools only. Verify Desktop-side differences before treating this as the
  default over PowerShell-first.
- **Server cwd matters.** Ensure the server is started from (or pointed at) the
  right project directory, since tool execution resolves against the server.

---

## Recommended next step

1. **Done (CLI):** served sessions verified - same toolset, same successful
   tool behavior as plain CLI; see A/B test above.
2. **Remaining (Desktop):** start `opencode serve`, connect Desktop via
   Settings -> Add Server, run one real session exercising read/glob/grep and
   apply_patch writes/edits (plus one plugin/MCP workflow we rely on), and record
   the result here. This step needs the Desktop UI and cannot be done from CLI.
3. If it holds up, decide whether to update the canonical runbook and AGENTS.md
   protocol (PowerShell-first -> serve-first) and whether the server should be
   auto-started (scheduled task) for always-on use.

## References

- Issue #35573: https://github.com/anomalyco/opencode/issues/35573
- Workaround comment (panhaoyu): https://github.com/anomalyco/opencode/issues/35573#issuecomment-5307816389
- Reproduction-confirmation comment (Talya1412): https://github.com/anomalyco/opencode/issues/35573#issuecomment-5219189353
- Related: #25880 (plugins, open), #41033 (native tools, open), #25799 (closed)
- Canonical runbook: `C:\Users\DaveWitkin\.config\opencode\docs\troubleshooting\tool-failure-bun-undefined.md`
- Remote serve/web background: `C:\development\opencode\docs\remote-opencode-migration-plan.md`
