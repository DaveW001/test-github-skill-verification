# Local Installation Notes

> **This file is user-specific and local to this machine.** It will not be overwritten by `nlm skill upgrade`.
> Last updated: 2026-05-08

## Installation Details

| Item | Value |
|------|-------|
| **Package** | `notebooklm-mcp-cli` |
| **Installed version** | 0.6.6 |
| **Python** | 3.13.2 |
| **Install location** | `C:\Users\DaveWitkin\AppData\Local\Programs\Python\Python313\Lib\site-packages\` |
| **CLI executable** | `C:\Users\DaveWitkin\AppData\Local\Programs\Python\Python313\Scripts\nlm.exe` |
| **MCP executable** | `C:\Users\DaveWitkin\AppData\Local\Programs\Python\Python313\Scripts\notebooklm-mcp.exe` |
| **Skill location** | `C:\Users\DaveWitkin\.config\opencode\skills\nlm-skill\` |
| **AI reference docs** | `C:\development\opencode\.conductor\tracks\20260411-notebooklm-cli-install\nlm-ai-reference.md` |
| **Track directory** | `C:\development\opencode\.conductor\tracks\20260411-notebooklm-cli-install\` |

## Authentication

| Item | Value |
|------|-------|
| **Profile** | `default` |
| **Account** | `dave.witkin@scruminc.com` |
| **Credentials stored** | `C:\Users\DaveWitkin\.notebooklm-mcp-cli\profiles\default` |
| **Session lifetime** | ~20 minutes |
| **Re-auth command** | `nlm login` |
| **Check auth** | `nlm login --check` |

### Session Behavior
- Sessions expire after approximately 20 minutes of inactivity
- When expired, commands return: `Error: Cookies have expired. Please run 'nlm login' to re-authenticate.`
- Convenience pattern: `nlm login --check || nlm login`
- Each profile gets its own isolated Chrome session

## User's Notebooks

| Notebook | ID | Sources | Last Updated |
|----------|-----|---------|--------------|
| C2/CC2 Portfolio Engagement Kx | `5125c1f1-71b3-4dbe-afc5-d725d1a4db2c` | 75 | 2026-05-08 |
| Interview Notebook | `a6341a1d-e4d2-4cd1-8cb9-5dfcb0c4cfac` | 30 | 2026-05-08 |
| Leadership Workshop | `093bdb9c-e06a-4117-bdec-7c0f56f5edc1` | 3 | 2026-05-05 |
| Solutions | `5a74333c-fdf4-437f-8eff-03d7c455ef72` | 2 | 2026-05-05 |

### Recommended Aliases
```bash
nlm alias set c2cc2 5125c1f1-71b3-4dbe-afc5-d725d1a4db2c
nlm alias set interviews a6341a1d-e4d2-4cd1-8cb9-5dfcb0c4cfac
nlm alias set leadership 093bdb9c-e06a-4117-bdec-7c0f56f5edc1
nlm alias set solutions 5a74333c-fdf4-437f-8eff-03d7c455ef72
```

## Upgrade Path
```bash
python -m pip install --user --upgrade notebooklm-mcp-cli
nlm skill install opencode  # Re-install skill after major version upgrade
```

## Known Issues
- `nlm doctor` may hit Windows Unicode bug (Rich library `→` char on cp1252 console). Workaround: set `$env:PYTHONIOENCODING="utf-8"` before running nlm commands.
- Legacy custom NotebookLM skill archived at: `C:\Users\DaveWitkin\.config\opencode\skill-backups\20260425-cleanup\notebooklm-legacy\`
