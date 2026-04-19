# Operator Auth Runbook: Multi-Account Codex OAuth

## What the Agent Can Do Directly

- Edit `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` to switch plugins.
- Run validation commands (`opencode debug config`, `opencode --version`) and capture evidence.
- Verify package metadata/versions and capture logs/evidence.
- Validate post-login account visibility by invoking `codex-*` tools from inside an active OpenCode session.

## What You Must Do (Interactive OAuth)

- Complete browser OAuth consent flow for each account when `opencode auth login` opens the sign-in URL.
- During second login flow, choose add-another-account behavior when prompted.
- If account has MFA or workspace picker, complete those steps in browser.

## Command Sequence

```bash
# 1) Login first account
opencode auth login

# 2) Login second account
opencode auth login

# 3) Confirm plugin is loaded in runtime
opencode debug config
```

In an active OpenCode session, ask the agent to run these tool calls:

```text
codex-list
codex-status
codex-health
codex-switch index=2
codex-refresh
codex-health
```

## Account Priority and Session Consistency

- Set preferred primary account after both accounts are enrolled (use `codex-switch` inside OpenCode session).
- Open a second OpenCode session and run `codex-status` in both sessions to confirm state consistency.
- If session state disagrees, restart both sessions and rerun `codex-list` and `codex-status`.

## Post-Setup Verification Checklist

- `codex-list` shows two accounts.
- One account is active and at least one backup account is healthy.
- `codex-status` does not show global auth failure.
- OpenCode requests succeed with selected OpenAI model.

## Fast Troubleshooting

- Re-auth one account: `opencode auth login`
- Refresh all tokens: run `codex-refresh` inside OpenCode session
- Re-check health: run `codex-health` inside OpenCode session
- Inspect active runtime config: `opencode debug config`

## Rollback Procedure

- Trigger rollback if any of the following occur after migration:
  - Multi-auth plugin fails to load.
  - Account tools (`codex-list`/`codex-status`) are unavailable from OpenCode tool surface.
  - Repeated auth failures persist after one re-login attempt.
- Restore backup of `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`.
- Confirm runtime rollback with `opencode debug config` and verify original auth plugin is active.

## Post-Handover Monitoring (24-48h)

- Run `codex-health` inside OpenCode session at least twice daily and after any auth incident.
- Check for account drift (unexpected active account changes) via `codex-status`.
- Record any failed auto-switch events and recovery action used.
- If failures repeat, execute rollback and open follow-up track for root-cause analysis.
