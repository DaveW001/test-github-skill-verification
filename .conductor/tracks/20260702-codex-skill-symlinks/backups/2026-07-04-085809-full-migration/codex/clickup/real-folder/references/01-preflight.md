# Preflight

Before doing any ClickUp operation, confirm the integration is available.

**Codex Desktop note:** the examples below assume the mounted skill root. Use the same relative commands (`scripts/...`) from `C:/Users/DaveWitkin/.codex/skills/clickup`; OpenCode Desktop/CLI uses its own mounted skill root with the same relative layout.

## Quick Check

Run this to verify everything is working:

```bash
python scripts/preflight.py
```

## Auth Sanity Check (Do This Before Calling Any Specific Endpoint)

If you are about to read/create/update a task, prove authentication first.

Preferred: run the skill preflight (loads token from `.env.mcp` / `.env`):

```bash
python scripts/preflight.py
```

If you need a quick API ping that uses the same token-resolution behavior as the skill scripts, use this from the mounted skill root for your current app:

```bash
python scripts/preflight.py
```

Fallback (env-only; can be misleading if a placeholder token is set):

```bash
python -c "import os,requests; t=os.getenv('CLICKUP_API_TOKEN'); r=requests.get('https://api.clickup.com/api/v2/user', headers={'Authorization':t} if t else {}, timeout=20); print(r.status_code)"
```

Interpretation:
- `200`: auth is good; proceed.
- `401`: do not report "ClickUp API failed" yet. Run token-source checks below.

## Token Source Gotcha (Common)

Windows shell environment variables can override `.env` file loading.

Failure mode we have hit:
- `CLICKUP_API_TOKEN` is set in the shell to a placeholder (e.g., `yourtoken`) -> env-only checks (and ad-hoc scripts that don't load dotenv) return `401`, even though the real token exists in `.env`.

Note: the ClickUp client used by this skill (`clickup_client.py`) will prefer `C:\development\.env.mcp` and will override placeholder env tokens when loading dotenv.

If you see `401`:
1. Check whether `CLICKUP_API_TOKEN` is set in the environment and looks like a placeholder (too short, contains `yourtoken`, etc.).
2. If so, unset it (or set it to the real value) and re-run the auth sanity check.
3. If you cannot change the shell env, explicitly load the token from `C:\development\cursor-clickup-mcp\.env` for the current run.

Or, as a minimal import check:

```python
from common import setup_path, get_repo_path
repo_path = setup_path()
print(f"✅ External repo found: {repo_path}")
```

## Requirements

### 1. External Repository (cursor-clickup-mcp)

**Status:** Required for all operations

The skill depends on an external repository containing ClickUp API clients and utilities.

**Default location:** `C:\development\cursor-clickup-mcp`

**Verification:**
- Repo directory exists
- Required files present:
  - `clickup_api.py`
  - `scripts/clickup_client.py`
  - `scripts/date_utils.py`

**Auto-discovery:** The skill will automatically search common locations if the primary path is not found. See `config.yaml` for fallback paths.

**If not found:**
1. Check that cursor-clickup-mcp exists at `C:\development\cursor-clickup-mcp`
2. Or update the mounted skill root's `config.yaml` with the correct path
3. Or set environment variable: `CLICKUP_REPO_PATH=C:\your\path`

### 2. Environment Variables (.env file)

**Status:** Required for all operations

A `.env` file must exist with ClickUp API credentials.

**Search order:**
1. **Primary:** `C:\development\.env.mcp`
2. **Fallback:** `C:\development\cursor-clickup-mcp\.env`
3. **Local:** `.env` in the script's working directory

**Required variables:**
- `CLICKUP_API_TOKEN` - Your ClickUp API token
- `CLICKUP_WORKSPACE_ID` - Workspace ID (e.g., `59530`)
- `CLICKUP_USER_ID` - Your user ID (e.g., `80264`)
- `SLACK_WEBHOOK_URL` - Only required when sending Slack reports

**How to check:**
```bash
# Check if .env file exists
ls C:\development\.env.mcp

# Check if variables are set (from Python)
import os
print(os.getenv('CLICKUP_API_TOKEN'))  # Should show token (don't print in production!)
```

### 3. Python Dependencies

**Status:** Required for all operations

Required packages:
- `requests` - HTTP library for API calls
- `pyyaml` - YAML config parsing
- `python-dotenv` - Environment variable loading
- `click` - CLI framework
- `pytz` - Timezone handling

**Installation:**
```bash
pip install requests pyyaml python-dotenv click pytz
```

## Safety

- Never print or paste API tokens.
- Never commit `.env` files.
- Never commit `config.yaml` if it contains sensitive paths.

## Environment Variable Loading Order

The ClickUp client (`clickup_client.py`) loads environment variables in this order:

1. First checks `C:\development\.env.mcp` (central configuration)
2. If `CLICKUP_API_TOKEN` not found, checks `C:\development\cursor-clickup-mcp\.env` (repo-specific)
3. Finally loads from local `.env` if present

**Note:** This means you don't need a `.env` file in every location. The scripts will automatically find the variables from the central locations.

## Troubleshooting

### "External cursor-clickup-mcp repository not found!"

**Cause:** The skill cannot find the external repo.

**Solutions:**
1. Verify repo exists at `C:\development\cursor-clickup-mcp`
2. Edit the mounted skill root's `config.yaml`:
   ```yaml
   external_repo:
     path: "C:/your/actual/path/cursor-clickup-mcp"
   ```
3. The skill will auto-discover if placed in common locations

### "CLICKUP_API_TOKEN not found"

**Cause:** Environment variables not loaded.

**Solutions:**
1. Create `C:\development\.env.mcp` with required variables
2. Or create `.env` file in `cursor-clickup-mcp` directory
3. Verify file is not committed to git

### "Module not found" errors

**Cause:** External repo not in Python path.

**Solutions:**
1. Run preflight check to verify repo is found
2. Check that `common.py` is being imported before other imports
3. Verify `config.yaml` has correct path

## Configuration Files

### config.yaml
**Location:** the mounted skill root for your current app, then `config.yaml`

Contains:
- External repo path
- Fallback search locations
- Auto-discovery settings
- Validation options

### .env.mcp
**Location:** `C:\development\.env.mcp` (recommended)

Contains:
- API tokens
- Workspace IDs
- User IDs
- Other secrets

## If Checks Fail

If any preflight check fails:

1. **Stop** - Do not proceed with ClickUp operations
2. **Diagnose** - Use error messages to identify the issue
3. **Fix** - Follow troubleshooting steps above
4. **Verify** - Re-run preflight check
5. **Proceed** - Only continue when all checks pass

When in doubt, ask the user for guidance.
