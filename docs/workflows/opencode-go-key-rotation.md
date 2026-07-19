# Workflow: Rotate the Default OpenCode Go Workspace Key

**Created:** 2026-07-18  
**Last verified:** 2026-07-18  
**Status:** Active — manual switching selected  
**Skill:** `opencode-go-key-rotation`

## Purpose

Switch the built-in `opencode-go` provider between approved Workspace 01 and Workspace 02 credentials without changing its provider ID or any hardcoded `opencode-go/model` agent assignments.

This is an explicit operational switch. It is not automatic quota detection or failover.

## Current operating decision

For now, use **manual switching** between the two approved workspace keys. The expected cadence is approximately once every 10 days or less often, so automatic failover or a Windows-specific proxy is not justified at this time.

- Keep the built-in `opencode-go` provider and its existing model namespace.
- Switch only `opencode-go.key` when Workspace 01 or Workspace 02 needs to be selected.
- Use the approved Workspace 01/02 environment-variable mappings; never paste a key into chat or documentation.
- Restart existing OpenCode sessions after every switch.
- Reconsider automation only if switching becomes frequent, disruptive, or operationally risky.

## Why this exists

On 2026-07-18, Workspace 01 exhausted available usage and agents pinned to `opencode-go/*` could not run. Rather than introduce custom provider IDs and migrate every agent, the default provider credential was changed to the Workspace 02 key. This preserved all existing provider/model identities and immediately restored agent compatibility.

The same procedure can be used in either direction when one workspace is unavailable.

## Canonical files

| Purpose | Path |
|---|---|
| Workspace key sources | `C:\Users\DaveWitkin\.config\opencode\.env` |
| OpenCode credential store | `C:\Users\DaveWitkin\.local\share\opencode\auth.json` |
| Rotation skill | `C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-go-key-rotation\SKILL.md` |
| Detailed safe procedure | `C:\Users\DaveWitkin\.opencode-lazy-vault\opencode-go-key-rotation\references\rotation-procedure.md` |

Approved mappings:

- Workspace 01: `OPENCODE_GO_WORKSPACE01_API_KEY`
- Workspace 02: `OPENCODE_GO_WORKSPACE02_API_KEY`

Never print or copy their values into documentation, logs, chats, or command output.

## What the switch changes

Only this field is changed:

```text
C:\Users\DaveWitkin\.local\share\opencode\auth.json
  -> opencode-go.key
```

It does not change:

- The provider ID `opencode-go`
- Model names
- Agent frontmatter
- `opencode.jsonc`
- Other provider credentials
- The source `.env` values

The built-in provider's workspace binding comes from the API key in `auth.json`.

## Standard procedure

1. Use `skill_find "rotate OpenCode Go key"` and load `opencode-go-key-rotation`.
2. Select Workspace 01 or Workspace 02 by approved environment-variable name.
3. Follow the skill's preflight and safe switch algorithm.
4. Verify target equality using a short SHA-256 fingerprint without printing either key.
5. Verify all non-Go provider entries remained semantically unchanged.
6. Confirm no temporary or rollback files remain.
7. Start a fresh OpenCode process and run `opencode models opencode-go`.
8. Run one low-cost generation to prove authentication, not only model discovery.
9. Restart existing OpenCode sessions before dispatching pinned agents.

## Rotation record: Workspace 02

**Date:** 2026-07-18  
**Reason:** Workspace 01 usage was exhausted and hardcoded `opencode-go/*` agents were unavailable.  
**Action:** Replaced only `opencode-go.key` with the value referenced by `OPENCODE_GO_WORKSPACE02_API_KEY`.  
**Safety:** Used a verified temporary file and ephemeral rollback copy; neither remained after success. All other provider entries were verified unchanged.  
**Verification:**

- Credential store remained valid JSON.
- Stored Go credential matched Workspace 02 without exposing its value.
- `opencode models opencode-go` returned the expected model catalog.
- Fresh-process authentication succeeded with `opencode-go/mimo-v2.5-pro`, returning the expected smoke-test response.

**Outcome:** Default `opencode-go` now authenticates through Workspace 02. Existing running sessions must be restarted.

## Revert to Workspace 01

Run the same skill procedure with Workspace 01. No provider or agent edits are required.

## When to switch

Switch when the active workspace is exhausted, unavailable, or intentionally being reserved. Do not switch on a timer unless usage patterns change; the current expectation is roughly one manual switch per 10 days or less.

## Provider naming

Do not rename the provider ID. Hardcoded references rely on the literal `opencode-go/model` identity. A display-name override is not necessary for rotation and was intentionally not applied.

## Related configuration note

Repository documentation designates `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc` as the sole canonical global config. After the urgent credential rotation succeeded, the reappeared `opencode.json` was handled separately: 17 unique OpenAI models were merged into `opencode.jsonc`, the duplicate JSON file was removed, and the effective configuration plus OpenCode Go authentication were re-verified.
