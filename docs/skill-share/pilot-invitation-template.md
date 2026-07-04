# Pilot Invitation: SkillShare for Packaged Agile Team

We are piloting SkillShare, a tool that automatically delivers our shared AI skills (humanizer, first-principles-mastery, etc.) to your AI assistant. We need one or two team members to try the setup and tell us what breaks before we roll it out to everyone.

This should take 15 to 30 minutes. You only do it once; after that, updates are two commands.

## What to test

Follow the [quickstart](quickstart-for-team.md) step by step. The five steps are:

1. **Step 0** - Install the GitHub CLI and sign in (`gh auth login` then `gh auth setup-git`).
2. **Step 1** - Install SkillShare (`irm ... | iex`), then close and reopen PowerShell and run `skillshare --version`.
3. **Step 2** - Point SkillShare at your AI tool (`skillshare init --targets opencode --no-copy --no-git --no-skill`).
4. **Step 3** - Connect to the shared library (`skillshare install github.com/packaged-agile/skillshare-skills --track`).
5. **Step 4** - Sync the skills (`skillshare sync`).

After setup, try using the **humanizer** skill in your AI tool on a real piece of writing (a LinkedIn post, an email, a paragraph of a proposal).

## What to report back

For each of the five steps above, tell Dave:

- Did it succeed or fail?
- If it failed, what was the exact error message?
- How long did that step take?
- Did any step feel confusing or need outside help?

After trying the humanizer:

- Did your AI assistant recognize and use the skill?
- Was the output noticeably better/different than without the skill?
- Any friction with the namespaced skill folder name (it may appear as `_skillshare-skills__skills__humanizer`)?

## Contact

- **Teams:** message **Dave Witkin** directly.
- **Email:** dave.witkin@packagedagile.com
- **Stuck?** The [operations guide](skillshare-operations-guide.md) has full troubleshooting. If it does not cover your issue, stop and tell Dave rather than spending more than 10 minutes debugging.

## How to roll back

If SkillShare causes problems or you want to remove it:

```powershell
# Remove all tracked skill libraries
skillshare uninstall --all

# Unlink SkillShare from your AI tools
skillshare target remove opencode

# Uninstall the SkillShare binary (optional)
# Delete the folder: %AppData%\..\Local\Programs\skillshare\
```

Uninstalling SkillShare does **not** uninstall the GitHub CLI or change your GitHub account. Your AI assistant will simply stop receiving skill updates.