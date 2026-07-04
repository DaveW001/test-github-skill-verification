# SkillShare Operations & Troubleshooting Guide

Everything we learned while setting up and testing SkillShare for the Packaged Agile team. This is for **maintainers and anyone troubleshooting the rollout**. Team members only need the [quickstart](quickstart-for-team.md).

Verified July 2026 on SkillShare **v0.20.21**, Windows. Some official `--help` text is misleading; this document is the ground truth.

## 1. Verified command reference

### First-time setup (global, for an end user)
```powershell
skillshare init --targets opencode --no-copy --no-git --no-skill
skillshare install github.com/packaged-agile/skillshare-skills --track
skillshare sync
```

### Updating
```powershell
skillshare update --all     # pull latest from all tracked repos
skillshare sync             # re-link skills into AI clients
```

### Inspection (read-only, safe)
```powershell
skillshare status           # source + targets + sync state
skillshare list             # installed skills
skillshare list --all       # skills + agents
skillshare target list      # configured targets
skillshare diff             # differences between source and targets
skillshare doctor           # environment + config diagnostics
```

### Selective install
```powershell
skillshare install <repo> --track -s humanizer,retrospective       # only these
skillshare install <repo> --track --exclude markdown-pdf-publisher # all except
skillshare install <repo> --track --exclude "drafts-*"             # glob exclude
```

### Targets (which AI clients receive skills)
```powershell
skillshare target add opencode              # auto-detect path
skillshare target add opencode <path>       # explicit path
skillshare target add opencode --mode copy  # copy instead of junction/symlink
skillshare target remove opencode           # unlink + restore
```

### Security
```powershell
skillshare audit                  # scan all skills for threats
skillshare audit -T high          # block at/above high severity
skillshare install <repo> --skip-audit   # bypass (not recommended)
```

### Removal
```powershell
skillshare uninstall humanizer     # remove one skill from source
skillshare target remove opencode  # unlink a target
```

### Dry-run (preview, no writes)
```powershell
skillshare install <repo> --track --dry-run
skillshare sync --dry-run
skillshare init --targets opencode --dry-run
```

## 2. Project mode vs global mode (the safe testing trick)

Two scopes:

- **Global** (default): config `%AppData%\skillshare\config.yaml`, source `%AppData%\skillshare\skills\`. End users run this; it writes to their real AI clients.
- **Project** (`-p` / `--project`): config `.\.skillshare\`, targets relative to the current folder (`.\.opencode\skills`). Fully isolated from real clients.

To safely test any member flow without touching real config:
```powershell
$sandbox = "$env:TEMP\ss-test"
Remove-Item -Recurse -Force $sandbox -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $sandbox | Out-Null
Set-Location $sandbox
skillshare init -p --targets opencode
skillshare install github.com/packaged-agile/skillshare-skills --track -p
skillshare sync -p
# inspect, then clean up:
Set-Location $env:TEMP; Remove-Item -Recurse -Force $sandbox
```

## 3. Known friction points and fixes

### 3.1 Full-screen target picker launches (and hangs non-interactive shells)
**Symptom:** Any command (`install`, `sync`, even `list`) in an **uninitialized** SkillShare auto-launches a full-screen 51-target selector.
**Root cause:** With no config yet, SkillShare forces target selection. The TUI ignores piped stdin, so in a non-interactive shell (CI, agent, piped input) it **hangs**. At a real terminal it works but is overwhelming for non-technical users.
**Fix:** Always run `skillshare init --targets <client>` **first**. With explicit targets the TUI never appears.
Expected output after running init: `Initialized with targets: opencode`
If this fails: Press Ctrl+C to cancel the TUI, then run `skillshare init --targets opencode --no-copy --no-git --no-skill` which skips the picker entirely.

### 3.2 `--all` / `--yes` cannot combine with `--track`
**Symptom:** `skillshare install <repo> --track --all` errors: `--all/--yes cannot be used with --track`.
**Root cause:** Tracked-repo installs are mutually exclusive with auto-accept flags by design.
**Fix:** Do not combine them. Once `init` is done, `install --track` finishes on its own with no prompts. Use `--all` only for non-tracked installs.
Expected output: `Tracking packaged-agile/skillshare-skills` then `Audit complete. No critical findings.`
If this fails: Drop `--all` and `--yes` from your command; tracked installs already auto-accept without those flags.

### 3.3 `init` flags differ between global and project mode
**Symptom:** In project mode (`-p`), `--no-targets`, `--all-targets`, `--no-copy` are rejected as "unknown option." Only `--targets <list>` works in project mode.
**Root cause:** `skillshare init --help` shows the **global** init help, which is misleading under `-p`. Project init accepts a smaller flag set.
**Fix:** In project mode use only `--targets`. In global mode the full flag set works.
Expected output: Global mode prints `Initialized with targets: opencode`; project mode accepts only `--targets` and prints the same.
If this fails: Run `skillshare init --help` to see the exact accepted flags for your scope, then retry with that subset.

### 3.4 Synced skill folders are namespaced
**Symptom:** After `sync`, skills appear under prefixed names like `_skillshare-skills__skills__humanizer` rather than bare `humanizer`.
**Root cause:** Default naming mode is "flat + repo-prefix" to avoid collisions across multiple tracked repos.
**Impact / open question:** Verify your AI client resolves the skill by its `name:` frontmatter through the prefixed folder. (OpenCode/skillful typically does.)
**Fix if needed:** Adjust naming mode in config, but the prefix prevents collisions, so prefer leaving it.

### 3.5 `markdown-pdf-publisher` flagged MEDIUM by audit
**Symptom:** Audit reports `markdown-pdf-publisher` as **medium**: "Auto-execute untrusted npm package without confirmation" (the Vivliostyle/Node runner, SKILL.md:249). Plus low (external URL) and info findings.
**Root cause:** The skill runs an npm package to build PDFs.
**Impact:** Non-blocking (block threshold is **CRITICAL** by default). The skill works; it just executes npm.
**Fix:** If a member does not want PDF publishing or lacks Node.js, exclude it: `skillshare install <repo> --track --exclude markdown-pdf-publisher`.

### 3.6 `skillshare` not recognized right after install
**Symptom:** After `irm | iex`, running `skillshare` in the same window fails.
**Root cause:** The installer updates the registry PATH, but already-open shells do not pick it up.
**Fix:** Close and reopen PowerShell. (`ss` shorthand may also work.)
Expected output: A fresh shell where `skillshare --version` prints `skillshare v0.20.21`.
If this fails: Try `ss --version`. If still not found, restart PowerShell or reboot.

## 4. The member access model (partially tested: GitHub API permission only)

- Org `packaged-agile` has **default repo permission = read**.
- An invited **Member** therefore gets **read** access to the private `skillshare-skills` repo automatically. **No per-repo invitation needed.**
- `read` permission is verified via GitHub API. This should allow clone after `gh auth login` + `gh auth setup-git`, but we have not verified an actual clone as the test account. (tested: GitHub API; not tested: actual clone as test account)
- **Verified 2026-07-04** with test account `dwitkin-test`: after one org invite (accepted), the GitHub permission API returned `permission: read`. Token-free proof.
- Owner check for any member: `gh api orgs/packaged-agile/memberships/<username>` (state/role) and `gh api repos/packaged-agile/skillshare-skills/collaborators/<username>/permission`.

## 5. Authentication (no double login)

- Member runs `gh auth login` (browser flow) once, then **`gh auth setup-git`** so git reuses the gh token.
- After that, `skillshare install` (which does a `git clone` of the private repo) does **not** trigger a second login. Verified: the clone reused cached credentials seamlessly.
- Without `gh auth setup-git`, Windows Git Credential Manager may pop a second browser prompt on first clone. Keep `setup-git` in the quickstart.

## 6. How SkillShare syncs (Windows)

- Default sync mode is **merge**, implemented on Windows as **NTFS junctions** (no admin rights). One copy per machine; the client skills folder gets a junction into the SkillShare source.
- PowerShell `Get-ChildItem -Recurse` does **not** traverse junctions by default. To verify synced content programmatically, read the junction path directly or set the target to `--mode copy` for testing.
- Native targets include `opencode`, `claude` (Claude Code), `codex`, `cursor`, `gemini`, `copilot`, and 50+ others. **Claude Desktop and Claude Cowork are NOT supported** (no skills-folder concept); members on those paste a skill's `SKILL.md` manually.

## 7. End-to-end test results (2026-07-04)

**Test 1 - invite + access (tested: 2026-07-04 with dwitkin-test):** PASS. `dwitkin-test` invited -> active member -> `read` on the repo -> can clone. Org-invite model proven.

**Test 2 - install + sync (partially tested: 2026-07-04 in project-scoped sandbox; not tested: global install):** PASS. `init -p --targets opencode` -> `install --track -p` (clone 1.2s, 6 skills discovered, audit ran) -> `sync -p` (6 skills linked via junctions in 0.2s) -> humanizer `SKILL.md` readable through the junction. Real global config untouched. Sandbox removed.

## 8. Tool-specific rollout matrix

Which AI tools SkillShare can auto-deliver to, and what we have actually verified.

| Tool | Install Mechanism | Sync Support | Tested? | Manual Steps | Known Friction | Recommended Path |
|------|-------------------|--------------|---------|--------------|----------------|------------------|
| OpenCode | SkillShare auto-sync | Yes (NTFS junction) | Tested 2026-07-04 | None | Namespaced folder names | Recommended |
| Claude Code | SkillShare auto-sync | Yes (junction) | Partially tested (project-scoped) | None | None observed | Recommended |
| Claude Desktop | No auto-sync | No skills folder | Not tested | Manual paste `SKILL.md` into chat | No programmatic skill delivery | Documented workaround |
| Claude Cowork | No auto-sync | No skills folder | Not tested | Manual paste `SKILL.md` into chat | No programmatic skill delivery | Documented workaround |
| Codex | SkillShare auto-sync | Yes | Not tested | None | Documented but untested | Documented but untested |

## 9. Clean global install test

A clean global install (no prior SkillShare on the machine, fresh Windows user profile) is the highest-confidence end-to-end test. **Not yet performed.** This section documents the steps a maintainer WOULD run on a clean machine to prove the global path end-to-end.

Steps to run on a clean Windows user profile:

```powershell
winget install --id GitHub.cli
gh auth login
gh auth setup-git
irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex
# close and reopen PowerShell so PATH refreshes
skillshare --version
skillshare init --targets opencode --no-copy --no-git --no-skill
skillshare install github.com/packaged-agile/skillshare-skills --track
skillshare sync
skillshare list
```

Expected success indicators: `Initialized with targets: opencode`, then `Installed 5 skills from packaged-agile/skillshare-skills`, then `Synced 5 skills to opencode target`. Verify the humanizer `SKILL.md` is readable both at the SkillShare source under `%AppData%\skillshare\skills\` and through the OpenCode skills junction.

**Not yet performed** because no clean machine profile was available during the 2026-07-04 testing window. The project-scoped sandbox test in section 7 exercises the same SkillShare code paths; a clean global install would add confidence that the PATH update, registry wiring, and `%AppData%` default paths all resolve correctly on a fresh user.

## 10. Claude Desktop / Claude Cowork manual workflow

Claude Desktop and Claude Cowork are chat applications with no skills-folder concept, so SkillShare cannot auto-deliver skills to them. This is the manual workaround for team members on those clients.

Steps:

1. Locate the skill `SKILL.md` you want to use. After a SkillShare sync on any machine, the humanizer is at `%AppData%\skillshare\skills\_skillshare-skills__skills__humanizer\SKILL.md`. Alternatively, clone `github.com/packaged-agile/skillshare-skills` directly.
2. Open Claude Desktop or Claude Cowork and start a new chat.
3. Paste the full contents of `SKILL.md` into your first message.
4. Paste any `references/*.md` the skill cites (for the humanizer: `brand-voice.md`, `ai-patterns-to-fix.md`, `humanization-checklist.md`).
5. Ask Claude to follow the pasted guidance for your task.

**This workflow is documented but not tested.** The skill content should work in principle, but the user experience (chat context window limits, paste formatting, multi-file chaining, session persistence) has not been validated. Pilot this with one real team member before relying on it for production work.

## 11. Environment notes

- Binary: `C:\Users\<user>\AppData\Local\Programs\skillshare\skillshare.exe`. Shorthand: `ss`. (tested: 2026-07-04)
- Global config: `%AppData%\skillshare\config.yaml`. Global source: `%AppData%\skillshare\skills\`. (tested: 2026-07-04)
- In non-TTY/agent contexts the binary may not be on PATH; invoke by full path.
- Audit block threshold default: `CRITICAL` (medium/high findings warn but do not block).

## 12. Open items / future verification

- Confirm OpenCode discovers skills through namespaced (`_repo__...__skill`) folder names in production.
- Decide whether to lower the audit block threshold for the team (currently CRITICAL).
- Future work (deferred, see [evaluation-and-decision.md](evaluation-and-decision.md)): per-user selective profiles, background auto-sync daemon, gotcha hardening (auth pre-check, conflict handling, client cache reload).