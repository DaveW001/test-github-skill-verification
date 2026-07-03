# SkillShare Quickstart for Team Members

This guide is for non-technical team members, or for Claude Desktop, Claude Cowork, or OpenCode helping a team member run the commands.

## Step 1: Install SkillShare

Copy and paste this into PowerShell:

```powershell
irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex
skillshare --version
```

## Step 2: Connect to the shared skill source

Dave will provide the final private repository URL from the packaged-agile GitHub organization.

```powershell
skillshare install https://github.com/packaged-agile/TEAM-SKILLS-REPO.git
```

## Step 3: Run your first sync

```powershell
skillshare sync
```

If `skillshare` is not recognized, try `ss --version` and `ss sync`, or close and reopen PowerShell.

## Future Work / Not Required for First Sync

Future work: per-user selective profiles will be designed later.

Future work: background automatic sync through Task Scheduler or another daemon-style wrapper will be designed later.

Future work: gotcha hardening for auth checks, conflict handling, and client cache reloads will be designed later.
