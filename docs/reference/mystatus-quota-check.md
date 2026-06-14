# mystatus - AI Account Quota Checker

**Status:** Reference guide  
**Applies To:** OpenCode agents and users needing to check AI platform quota usage  
**Plugin:** `opencode-mystatus` v1.2.4  
**Last Updated:** May 25, 2026

---

## What It Does

The `opencode-mystatus` plugin queries quota usage across multiple AI platforms in a single command:

| Platform | Account Type | Data Source |
|----------|-------------|-------------|
| OpenAI | Plus / Team / Pro | `~/.local/share/opencode/auth.json` |
| Zhipu AI | Coding Plan | `~/.local/share/opencode/auth.json` |
| Z.ai | Coding Plan | `~/.local/share/opencode/auth.json` |
| GitHub Copilot | Individual / Business | `~/.local/share/opencode/auth.json` |
| Google Cloud | Antigravity | `%APPDATA%/opencode/antigravity-accounts.json` |

## How to Use It

### Option A: Slash Command (Preferred)

```
/mystatus
```

This is the intended usage. The slash command template instructs the LLM to call the `mystatus` tool registered by the plugin. The tool is read-only and safe.

### Option B: Ask in Natural Language

Say things like:

- "Check my OpenAI quota"
- "How much quota do I have left?"
- "Show my AI account status"
- "Use the mystatus tool to query quota usage"

### Option C: Manual CLI Fallback (If Plugin Tool Is Unavailable)

If the `mystatus` tool is **not in the agent's active tool list** (see [Root Cause](#root-cause-why-the-tool-may-be-missing)), any agent can replicate the query by running a Node.js script directly.

**Quick command** (copy-paste into bash/pwsh):

```powershell
node -e "const fs=require('fs'),path=require('path'),os=require('os');async function main(){const ap=path.join(os.homedir(),'.local','share','opencode','auth.json');let a;try{a=JSON.parse(fs.readFileSync(ap,'utf-8'))}catch(e){console.error('Auth file error:',e.message);process.exit(1)}const R=[],E=[];if(a.openai&&a.openai.type==='oauth'&&a.openai.access){try{const p=a.openai.access.split('.');if(p.length===3){const pl=JSON.parse(Buffer.from(p[1].replace(/-/g,'+').replace(/_/g,'/'),'base64').toString()),em=pl['https://api.openai.com/profile']?.email||'unknown',ai=pl['https://api.openai.com/auth']?.chatgpt_account_id,h={'Authorization':'Bearer '+a.openai.access,'User-Agent':'OpenCode-Status-Plugin/1.0'};if(ai)h['ChatGPT-Account-Id']=ai;const r=await fetch('https://chatgpt.com/backend-api/wham/usage',{headers:h,signal:AbortSignal.timeout(10000)});if(r.ok){const d=await r.json(),l=[];l.push('## OpenAI Account Quota','');l.push('Account:        '+em+' ('+d.plan_type+')','');function fw(w){const dy=Math.round(w.limit_window_seconds/86400),wn=dy>=1?dy+'-day limit':Math.round(w.limit_window_seconds/3600)+'-hour limit',rm=Math.round(100-w.used_percent),br='\u2588'.repeat(Math.round(rm/100*30))+'\u2591'.repeat(30-Math.round(rm/100*30)),s=w.reset_after_seconds,rs=(Math.floor(s/86400)?Math.floor(s/86400)+'d ':'')+Math.floor((s%86400)/3600)+'h '+Math.floor((s%3600)/60)+'m';return[wn,br+' '+rm+'% remaining','Resets in: '+rs]}if(d.rate_limit?.primary_window)l.push(...fw(d.rate_limit.primary_window));if(d.rate_limit?.secondary_window){l.push('');l.push(...fw(d.rate_limit.secondary_window))}R.push(l.join('\n'))}else E.push('OpenAI API failed: '+r.status)}}catch(e){E.push('OpenAI error: '+e.message)}}if(a['zai-coding-plan']&&a['zai-coding-plan'].type==='api'&&a['zai-coding-plan'].key){try{const k=a['zai-coding-plan'].key,m=k.slice(0,4)+'****'+k.slice(-4),r=await fetch('https://api.z.ai/api/monitor/usage/quota/limit',{headers:{Authorization:k,'Content-Type':'application/json','User-Agent':'OpenCode-Status-Plugin/1.0'},signal:AbortSignal.timeout(10000)});if(r.ok){const d=await r.json();if(d.success){const l=[];l.push('## Z.ai Account Quota','','Account:        '+m+' (Z.ai)','');const tl=d.data.limits?.find(x=>x.type==='TOKENS_LIMIT');if(tl){const rm=Math.round(100-tl.percentage),br='\u2588'.repeat(Math.round(rm/100*30))+'\u2591'.repeat(30-Math.round(rm/100*30));l.push('5-hour token limit',br+' '+rm+'% remaining');if(tl.currentValue!=null&&tl.usage!=null)l.push('Used: '+(tl.currentValue/1e6).toFixed(1)+'M / '+(tl.usage/1e6).toFixed(1)+'M');if(tl.nextResetTime){const rs=Math.max(0,Math.floor((tl.nextResetTime-Date.now())/1000));l.push('Resets in: '+Math.floor(rs/3600)+'h '+Math.floor((rs%3600)/60)+'m')}}R.push(l.join('\n'))}}else E.push('Z.ai API failed: '+r.status)}catch(e){E.push('Z.ai error: '+e.message)}}const gp=path.join(process.env.APPDATA||path.join(os.homedir(),'AppData','Roaming'),'opencode','antigravity-accounts.json');try{const g=JSON.parse(fs.readFileSync(gp,'utf-8'));if(g.accounts)for(const ac of g.accounts){if(!ac.email||!ac.refreshToken)continue;try{const pa=new URLSearchParams({client_id:'***REDACTED-OAUTH-CLIENT-ID***',client_secret:'***REDACTED-OAUTH-CLIENT-SECRET***',refresh_token:ac.refreshToken,grant_type:'refresh_token'}),tr=await fetch('https://oauth2.googleapis.com/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:pa,signal:AbortSignal.timeout(10000)});if(!tr.ok){E.push(ac.email+': Google token refresh failed');continue}const td=await tr.json(),pi=ac.projectId||ac.managedProjectId;if(!pi){E.push(ac.email+': Missing project_id');continue}const qr=await fetch('https://cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+td.access_token,'User-Agent':'antigravity/1.11.9 windows/amd64'},body:JSON.stringify({project:pi}),signal:AbortSignal.timeout(10000)});if(qr.ok){const qd=await qr.json(),md=[{key:'gemini-3-pro-high',alt:'gemini-3-pro-low',display:'G3 Pro'},{key:'gemini-3-pro-image',display:'G3 Image'},{key:'gemini-3-flash',display:'G3 Flash'},{key:'claude-opus-4-5-thinking',alt:'claude-opus-4-5',display:'Claude'}],l=[];l.push('## Google Cloud Account Quota','','### '+ac.email,'');for(const m of md){let mi=qd.models?.[m.key];if(!mi&&m.alt)mi=qd.models?.[m.alt];if(mi){const pc=Math.round((mi.quotaInfo?.remainingFraction??0)*100),br='\u2588'.repeat(Math.round(pc/100*20))+'\u2591'.repeat(20-Math.round(pc/100*20));let rs='-';if(mi.quotaInfo?.resetTime){const rd=new Date(mi.quotaInfo.resetTime),df=rd-new Date();if(df>0){const dm=Math.floor(df/60000);rs=Math.floor(dm/1440)+'d '+Math.floor((dm%1440)/60)+'h '+dm%60+'m'}}l.push(m.display.padEnd(10)+' '+rs.padEnd(10)+' '+br+' '+pc+'%')}}R.push(l.join('\n'))}else E.push(ac.email+': Google quota API failed '+qr.status)}catch(e){E.push(ac.email+': '+e.message)}}}catch(e){}let o=R.join('\n\n');if(E.length>0){if(o)o+='\n\n';o+='\u274C Failed to query accounts:\n'+E.join('\n')}if(!o)o='No configured accounts found.';console.log(o)}main().catch(e=>console.error(e))"
```

---

## Configuration

The plugin is registered in `~/.config/opencode/opencode.json` (or `.jsonc`):

```json
{
  "plugin": ["opencode-mystatus"],
  "command": {
    "mystatus": {
      "description": "Query quota usage for all AI accounts",
      "template": "Use the mystatus tool to query quota usage. Return the result as-is without modification."
    }
  }
}
```

### Plugin File Locations

| What | Path |
|------|------|
| Plugin source (installed) | `%USERPROFILE%\.cache\opencode\packages\opencode-mystatus@latest\node_modules\opencode-mystatus\` |
| Bun cache | `%USERPROFILE%\.bun\install\cache\opencode-mystatus@1.2.4@@@1\` |
| Auth data (read-only) | `%USERPROFILE%\.local\share\opencode\auth.json` |
| Google accounts (read-only) | `%APPDATA%\opencode\antigravity-accounts.json` |
| Copilot PAT config (optional) | `%USERPROFILE%\.config\opencode\copilot-quota-token.json` |

### GitHub Copilot PAT Setup (Optional)

The internal Copilot quota API requires either a legacy OAuth token or a fine-grained PAT:

1. Create a fine-grained PAT at https://github.com/settings/tokens?type=beta
2. Under **Account permissions**, set **Plan** to **Read-only**
3. Save to `~/.config/opencode/copilot-quota-token.json`:
   ```json
   { "token": "github_pat_xxx...", "username": "YourUsername", "tier": "pro" }
   ```
4. Valid tiers: `free`, `pro`, `pro+`, `business`, `enterprise`

---

## Root Cause: Why the Tool May Be Missing

**Problem:** The `mystatus` tool does not appear in the agent's active tool list, even though the plugin is listed in `opencode.json`.

**Root Cause:** The `opencode-mystatus` plugin registers its tool via the `@opencode-ai/plugin` `tool()` API at OpenCode startup. If any of these conditions are true, the tool won't be available:

1. **Plugin load failure** - The plugin may fail to load silently (e.g., missing dependency, version mismatch, runtime error during registration).
2. **Session started before plugin was added** - If OpenCode was already running when the plugin was added to config, it requires a restart to activate.
3. **Tool not propagated to subagents** - Plugin-registered tools may not be available to all agent types (e.g., planner agents, subagents launched via the `task` tool). They are primarily available to the main coding agent.
4. **Model-specific tool routing** - Some model providers may not support the full tool schema, causing plugin tools to be filtered out.

**Workaround:** Use the CLI fallback script in Option C above. The script replicates the exact same API calls and formatting logic as the plugin, reading from the same auth files.

**Verification:** To check if the tool loaded, ask the agent "do you have a mystatus tool?" or look for it in the tool list. If missing, the CLI fallback is the reliable path.

---

## How the Plugin Works (For Agent Developers)

The plugin's architecture is straightforward:

1. **Entry point:** `dist/plugin/mystatus.js` exports `MyStatusPlugin()` which registers a single tool named `mystatus`
2. **On execute:** Reads `~/.local/share/opencode/auth.json` to discover all configured providers
3. **Parallel queries:** Calls each provider's quota API concurrently via `Promise.all()`
4. **Per-provider modules:**
   - `lib/openai.js` - Decodes JWT for email/account, calls `chatgpt.com/backend-api/wham/usage`
   - `lib/zhipu.js` - Handles both Zhipu AI and Z.ai via API key auth
   - `lib/google.js` - Reads `antigravity-accounts.json`, refreshes OAuth tokens, calls `fetchAvailableModels`
   - `lib/copilot.js` - Tries PAT config first, then OAuth token exchange, then direct API call
5. **Formatting:** Each module returns formatted output with progress bars and reset countdowns
6. **i18n:** Auto-detects language (English/Chinese) via `Intl` API and `LANG` env var

---

## API Endpoints Used (All Official, Read-Only)

| Platform | Endpoint |
|----------|----------|
| OpenAI | `https://chatgpt.com/backend-api/wham/usage` |
| Zhipu AI | `https://bigmodel.cn/api/monitor/usage/quota/limit` |
| Z.ai | `https://api.z.ai/api/monitor/usage/quota/limit` |
| GitHub Copilot | `https://api.github.com/copilot_internal/v2/token` (exchange) + `/copilot_internal/user` (quota) |
| GitHub Copilot (PAT) | `https://api.github.com/users/{user}/settings/billing/premium_request/usage` |
| Google Cloud | `https://oauth2.googleapis.com/token` (refresh) + `https://cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels` (quota) |

All requests timeout after 10 seconds. No data is stored or cached.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "No configured accounts found" | No matching auth entries in `auth.json` | Ensure at least one AI provider is configured in OpenCode |
| OpenAI returns 401 | OAuth token expired | Use an OpenAI model in OpenCode to refresh the token |
| Z.ai shows "NaNM / NaNM" | API returns non-numeric `currentValue`/`usage` fields | Known minor bug in the plugin; percentage and reset time are still correct |
| Google accounts missing | No `antigravity-accounts.json` or no accounts with `email` | Install `opencode-antigravity-auth` plugin and authenticate |
| Copilot shows setup instructions | No PAT config and OAuth token lacks copilot scope | Set up PAT config as described above |
| Tool not found by agent | Plugin not loaded into session | Use CLI fallback (Option C) or restart OpenCode |

---

## Example Output

```
## OpenAI Account Quota

Account:        user@example.com (team)

5-hour limit
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 99% remaining
Resets in: 5h 0m

7-day limit
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  98% remaining
Resets in: 5d 0h 56m

## Z.ai Account Quota

Account:        118a****S5yH (Z.ai)

5-hour token limit
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 99% remaining
Used: 0.5M / 10.0M
Resets in: 0h 35m

## Google Cloud Account Quota

### user@gmail.com

G3 Flash   0d 4h 59m  >>>>>>>>>>>>>>>>>>>>>> 100%
```

---

## Source

- **npm package:** https://www.npmjs.com/package/opencode-mystatus
- **GitHub:** https://github.com/vbgate/opencode-mystatus
- **Author:** javazys
- **License:** MIT