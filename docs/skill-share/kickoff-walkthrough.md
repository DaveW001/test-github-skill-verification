# SkillShare Kickoff Walkthrough

**End-to-end onboarding guide for running a SkillShare setup session with a teammate.**

This walks the facilitator (and the teammate) through the *whole* process in order:
pre-call prep, installing the AI tool, GitHub access, SkillShare, and verifying a skill
works. You do this once per person; after that, updates are two commands.

> **Companion docs (link out rather than duplicate):**
> - Self-serve command reference: [`quickstart-for-team.md`](quickstart-for-team.md)
> - Troubleshooting & operations: [`skillshare-operations-guide.md`](skillshare-operations-guide.md)
> - Pilot invitation / comms template: [`pilot-invitation-template.md`](pilot-invitation-template.md)

---

## Roles in this guide
- **Facilitator** - the person running the call (maintains the skill library; for Packaged
  Agile, that's Dave).
- **Teammate** - the person being set up (for example, Jess).

---

## Before the call (facilitator checklist)

- [ ] **GitHub org membership** - the `packaged-agile` org already exists. Make sure the
  teammate's GitHub account has been **invited** and has **accepted**:
  - Invite / manage members: https://github.com/orgs/packaged-agile/people
  - Teammate accepts at: https://github.com/orgs/packaged-agile/invitation
- [ ] **Confirm the AI tool** the teammate will use (this decides a few commands below).
- [ ] **Decide when to install the AI tool** - before the call (saves time) or on the call
  (walk through it together). Step 2 covers it either way.
- [ ] Have this guide + the [operations guide](skillshare-operations-guide.md) open in case
  something breaks.

### Which AI tool? (confirm with the teammate)

| Tool | SkillShare target | Needs Node.js? | Notes |
|------|-------------------|----------------|-------|
| **OpenAI Codex** | `codex` | Yes (Node 22+) | Default for Jess. |
| **OpenCode** | `opencode` | No (use scoop/choco) | |
| **Claude Code** | `claude` | No (native installer) | |

> The rest of this guide uses `codex` as the example. Swap in `opencode` or `claude`
> wherever you see `codex`.

---

## Step 1 - Confirm GitHub access

The skill library is **private**, so the teammate must be a member of `packaged-agile` and
signed in.

1. Teammate accepts the org invite: https://github.com/orgs/packaged-agile/invitation
   (check the email tied to their GitHub account).
2. If they don't have a GitHub account yet: https://github.com/signup

---

## Step 2 - Install the AI tool (Codex / OpenCode / Claude Code)

Do this if the teammate doesn't already have their AI tool installed. **Before the call is
fine; on the call is fine too.**

### Prerequisite: Node.js 22+ (only for Codex, and only via npm)
Codex (and the npm install of Claude Code) need Node.js 22 or later. Install from
https://nodejs.org if not present. Verify with `node --version` (expect v22+).

> OpenCode (via scoop/choco) and Claude Code's native installer do **not** need Node.

### Option A - OpenAI Codex (default for Jess)
```powershell
npm install -g @openai/codex
```
- The package is `@openai/codex` - **not** `codex`. The unscoped `codex` is an unrelated
  2012 package that installs and then does nothing.
- Verify: `codex --version`
- First run: `codex` - sign in with the teammate's ChatGPT / OpenAI account.
- Docs: https://developers.openai.com/codex/cli | npm: https://www.npmjs.com/package/@openai/codex

### Option B - OpenCode
```powershell
# Windows (recommended)
scoop install opencode
# or
choco install opencode
```
- Verify: `opencode --version`
- Docs: https://opencode.ai/docs/
- (`npm i -g opencode-ai` works too but has Windows wrapper issues - prefer scoop/choco.)

### Option C - Claude Code
```powershell
# Windows native install (recommended; no Node needed)
irm https://claude.ai/install.ps1 | iex
# or
winget install Anthropic.ClaudeCode
```
- Verify: `claude --version`
- First run: `claude` - sign in with their Anthropic account.
- Docs: https://code.claude.com/docs/

> After installing **any** tool: if `codex` / `opencode` / `claude` is "not recognized,"
> **close and reopen PowerShell** so the new command is picked up.

---

## Step 3 - Install the GitHub CLI and sign in

The teammate's machine needs to prove who it is to reach the private library.

```powershell
winget install --id GitHub.cli
```
**Close and reopen PowerShell**, then:
```powershell
gh auth login          # choose: GitHub.com -> HTTPS -> Login with a web browser
gh auth setup-git
```
- A browser opens; sign in with the teammate's GitHub account and approve.
- `gh auth setup-git` makes git reuse that sign-in so they aren't asked twice.
- Stuck? See the [operations guide](skillshare-operations-guide.md).

---

## Step 4 - Install SkillShare

SkillShare is the little tool that delivers the team's skills into the AI tool.

```powershell
irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex
```
**Close and reopen PowerShell**, then verify:
```powershell
skillshare --version     # if "not recognized", try: ss --version
```
- Upstream tool: https://github.com/runkids/skillshare

---

## Step 5 - Point SkillShare at the AI tool

Replace `codex` with `opencode` or `claude` if that's the teammate's tool. The flags avoid
opening the interactive picker.

```powershell
skillshare init --targets codex --no-copy --no-git --no-skill
```
> Using more than one tool? Comma-separate: `--targets codex,opencode`.

---

## Step 6 - Connect to the shared library and sync

```powershell
skillshare install github.com/packaged-agile/skillshare-skills --track
skillshare sync
```
- `--track` remembers the library so future updates are easy.
- A short security scan runs on install - that's normal.
- You can't combine `--all`/`--yes` with `--track`; just run the command as shown.

---

## Step 7 - Verify it worked

Ask the AI tool to use a real skill, for example the **humanizer**:

> Use the humanizer skill on this text and make it sound less corporate: [paste a LinkedIn
> post, email, or paragraph]

If the tool recognizes and applies the skill, setup is complete.

> The skill folder may appear as `_skillshare-skills__skills__humanizer` - that's expected.

---

## Fast path: let the AI tool do steps 2-6

If the teammate prefers, paste this into their AI assistant and let it run each command,
reporting each result before continuing:

```
Set up my machine for the Packaged Agile team's shared skills. Run these one at a time and
tell me the result of each before continuing:

1. (Only if I don't have an AI tool yet) npm install -g @openai/codex
2. winget install --id GitHub.cli
3. gh auth login   (GitHub.com -> HTTPS -> Login with a web browser)
4. gh auth setup-git
5. irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex
6. Close & reopen terminal, then: skillshare --version
7. skillshare init --targets codex --no-copy --no-git --no-skill
8. skillshare install github.com/packaged-agile/skillshare-skills --track
9. skillshare sync

If any step fails, stop and tell me what went wrong before the next one.
```
> Swap `codex` for `opencode` or `claude` (and the install line for that tool) as needed.

---

## After the call

**Updates later (everyday, two commands):**
```powershell
skillshare update --all
skillshare sync
```

**Ask the teammate to report back** (see the [pilot template](pilot-invitation-template.md)):
did each step succeed/fail, how long it took, and any friction.

---

## If something breaks

Full detail in the [operations guide](skillshare-operations-guide.md). Most common fixes:

- `codex` / `opencode` / `claude` / `gh` / `skillshare` **not recognized** -> close & reopen
  PowerShell.
- Codex install did nothing -> wrong package; use `@openai/codex`, not `codex`. Node 22+ is
  required.
- Full-screen tool picker appeared -> arrow keys + Space to select, then Enter; or run the
  `init --targets <tool>` step first.
- `install` asks to log in again -> run `gh auth setup-git`, then retry.
- **Rule of thumb:** stop after about 10 minutes of debugging and ask the facilitator.

---

## All the links

| What | Link |
|------|------|
| Team skill library (private) | https://github.com/packaged-agile/skillshare-skills |
| Packaged Agile org | https://github.com/packaged-agile |
| Accept org invite | https://github.com/orgs/packaged-agile/invitation |
| Manage members | https://github.com/orgs/packaged-agile/people |
| SkillShare installer | https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 |
| SkillShare tool repo | https://github.com/runkids/skillshare |
| Codex CLI docs | https://developers.openai.com/codex/cli |
| Codex on npm | https://www.npmjs.com/package/@openai/codex |
| OpenCode docs | https://opencode.ai/docs/ |
| Claude Code docs | https://code.claude.com/docs/ |
| GitHub CLI | https://cli.github.com |
| Node.js (for Codex) | https://nodejs.org |

---

*This guide sequences the full end-to-end. For just the raw commands, see
[`quickstart-for-team.md`](quickstart-for-team.md). For troubleshooting, see
[`skillshare-operations-guide.md`](skillshare-operations-guide.md).*
