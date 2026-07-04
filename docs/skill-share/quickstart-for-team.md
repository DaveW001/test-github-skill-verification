# SkillShare Quickstart for Team Members

This guide sets up your machine to receive the Packaged Agile team's shared AI skills (humanizer, first-principles-mastery, and others). You only do this **once**. After that, getting updates is two commands.

You have two paths. **Most people should take Path A.**

---

## Path A (recommended): Let your AI assistant do it

If you use **Claude Code**, **OpenAI Codex**, or **OpenCode**, you do not need to open PowerShell or type commands yourself. Your AI assistant will run everything for you.

### Step A1 - Open your AI tool

Open the AI assistant you normally use (Claude Code, Codex, or OpenCode) in any folder on your computer.

### Step A2 - Paste this prompt

Copy everything in the box below, paste it into your AI assistant as your message, and press Enter.

```
Please install SkillShare and connect it to my team's shared skill library. Run these PowerShell commands one at a time and tell me the result of each before continuing to the next:

1. winget install --id GitHub.cli
2. gh auth login   (when it asks, choose: GitHub.com -> HTTPS -> Login with a web browser; sign in with your GitHub account in the browser tab that opens)
3. gh auth setup-git
4. irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex
5. Close and reopen this terminal, then run: skillshare --version
6. skillshare init --targets opencode --no-copy --no-git --no-skill   (replace "opencode" with "claude" if you use Claude Code, or "codex" if you use Codex)
7. skillshare install github.com/packaged-agile/skillshare-skills --track
8. skillshare sync

Before you start: check with me that I have accepted the GitHub org invite from packaged-agile. If any step fails, stop and tell me what went wrong before trying the next one.
```

### Step A3 - Watch and confirm

The AI will run each command and report back. When it reaches `gh auth login` (step 2), a browser tab will open — sign in with your GitHub account there. When it finishes step 8, you're done. Your AI now knows the Packaged Agile skills.

> If your AI tool is **Claude Desktop** or **Claude Cowork**, these chat apps can't run commands for you. Use **Path B** below, or ask Dave for the manual workflow for those apps.

**Skip to "Try a skill" below to confirm it worked.**

---

## Path B (manual): Run the commands yourself in PowerShell

Use this path if you don't have an AI assistant that can run commands, or if you prefer to do it yourself.

### Step B0 - How to open PowerShell (do this first)

Everything below happens in **PowerShell**, a command window built into Windows. You will type commands into it. To open it:

1. Press the **Windows key** on your keyboard (or click the Start button).
2. Type `powershell`.
3. You will see **Windows PowerShell** or **PowerShell** in the results. Click it.
4. A blue (or black) window opens with a prompt that looks like `PS C:\Users\YourName>`. This is where you type commands.

> **Tip:** You can also right-click the Start button and pick **Terminal** or **Windows Terminal** — same thing. Throughout this guide, "PowerShell" means any of these.
>
> **Mac user?** Open the **Terminal** app (Cmd+Space, type `Terminal`). The SkillShare commands are the same, but `winget` does not exist on Mac — see the note under Step B1.

### Step B1 - Install the GitHub CLI (one time)

Our skill library is **private**, so your machine needs permission to reach it. The GitHub CLI is the tool that proves who you are.

In your PowerShell window, paste this line and press Enter:

```powershell
winget install --id GitHub.cli
```

> **What you'll see:** text scrolling as it downloads and installs. When it finishes, you'll be back at the `PS C:\Users\YourName>` prompt.
>
> **Mac user?** `winget` is Windows-only. Instead run: `brew install gh` (if you have Homebrew), or download gh from https://cli.github.com and install it.
>
> **If it asks "Source requires agreement"** type `Y` and press Enter.

**Close PowerShell and open a fresh one** (Step B0 again) so it recognizes the new `gh` command. Then confirm:

```powershell
gh --version
```

You should see something like `gh version 2.xx.x`.

### Step B2 - Sign in to GitHub (one time)

```powershell
gh auth login
```

This launches a short menu. Use the arrow keys and Enter to choose:

1. **GitHub.com**
2. **HTTPS**
3. **Login with a web browser**

It shows a one-time code (like `XXXX-XXXX`) and opens your browser. **Copy the code**, paste it in the browser page, and approve. Then let git reuse that sign-in so you're not asked to log in twice:

```powershell
gh auth setup-git
```

> ✓ Logged in to github.com as <username> (oauth token saved to keyring).
>
> **If a browser tab doesn't open** copy the URL it prints into your browser manually.

### Step B3 - Install SkillShare (one time)

```powershell
irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex
```

> **What this does:** downloads and installs the SkillShare tool from the official source.

**Important:** SkillShare will not be recognized in this window yet. **Close and reopen PowerShell** (Step B0), then confirm:

```powershell
skillshare --version
```

> ✓ skillshare v0.20.21
>
> **If it says "not recognized"** try `ss --version` instead (`ss` is the shorthand). If neither works, see "If something goes wrong" below.

### Step B4 - Point SkillShare at your AI tool (one time)

Tell SkillShare which AI tool to deliver skills to. Replace `opencode` below with the tool you use:

| Your AI tool | Use this target name |
|--------------|---------------------|
| OpenCode | `opencode` |
| Claude Code | `claude` |
| OpenAI Codex | `codex` |

```powershell
skillshare init --targets opencode --no-copy --no-git --no-skill
```

Use more than one? Comma-separate them: `--targets opencode,claude`.

> ✓ Initialized with targets: opencode
>
> **Claude Desktop or Claude Cowork?** These chat apps have no skills folder, so SkillShare cannot auto-deliver. Skip this step and open a skill's `SKILL.md`, pasting the guidance into your chat when you need it. (Or use OpenCode / Claude Code for automatic delivery.)

### Step B5 - Connect to the shared skill library (one time)

```powershell
skillshare install github.com/packaged-agile/skillshare-skills --track
```

The `--track` flag remembers this library so updates are easy. You will see a short security scan run. That is normal.

> ✓ Installed 5 skills from packaged-agile/skillshare-skills
>
> **Note:** you cannot add `--all` or `--yes` to a `--track` install (SkillShare blocks that combination). Just run the command as shown; it finishes on its own.

### Step B6 - Send the skills to your AI tool

```powershell
skillshare sync
```

Done. Your AI assistant now knows the Packaged Agile skills.

> ✓ Synced 5 skills to opencode target

---

## Try a skill (confirm it worked)

Open your AI assistant and ask it to use the **humanizer** on a real piece of writing (a LinkedIn post, an email, a paragraph of a proposal). For example:

> Use the humanizer skill on this text and make it sound less corporate: [paste your text]

If it recognizes and applies the skill, setup worked. If it doesn't, tell Dave (see "If something goes wrong" below).

---

## Updating later (the everyday command)

When Dave adds or improves a skill, open PowerShell (Path B, Step B0) — or ask your AI assistant — and run:

```powershell
skillshare update --all
skillshare sync
```

That's it. Two commands, done.

---

## A note on `markdown-pdf-publisher`

This skill turns documents into branded PDFs. It needs **Node.js** on your machine and runs an npm package (Vivliostyle) to build the PDF. SkillShare's security scan flags it as **medium** for that reason. If you do not need PDF publishing, skip it:

```powershell
skillshare install github.com/packaged-agile/skillshare-skills --track --exclude markdown-pdf-publisher
```

---

## If something goes wrong

Full troubleshooting is in **[skillshare-operations-guide.md](skillshare-operations-guide.md)**. The most common fixes:

- **`skillshare` not recognized** -> close and reopen PowerShell.
- **A full-screen list of AI tools appeared** -> that is the target picker. Select yours with arrow keys + Space, then Enter. (Running Step B4 first avoids it entirely.)
- **`install` asks you to log in again** -> run `gh auth setup-git`, then retry.
- **`gh auth login` fails** -> check you have a GitHub account and accepted the packaged-agile org invite. Try `winget uninstall GitHub.cli` then reinstall.
- **`gh` not recognized after installing it** -> close PowerShell and reopen it (Step B0). Windows only learns about new commands when a fresh window opens.
- **`skillshare init` shows the TUI** -> press Ctrl+C, then run `skillshare init --targets opencode --no-copy --no-git --no-skill`.

When in doubt, **stop and ask Dave** rather than spending more than 10 minutes debugging.

---

## Before you start (checklist)

- [ ] Dave invited your GitHub account to the `packaged-agile` organization.
- [ ] You **accepted the invite** (check the email tied to your GitHub account, or go to https://github.com/orgs/packaged-agile/invitation).
- [ ] You know which AI tool you'll point SkillShare at (OpenCode, Claude Code, or Codex).

---

## Want to pilot this?

See the [pilot invitation template](pilot-invitation-template.md) for what to test and how to report back.