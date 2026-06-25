# API Key Centralization Index

## Goal / Outcome

Create a lightweight, local-only API key discovery system for Dave's OpenCode environment so future agents can quickly determine which key name is needed, where the canonical value lives, and which repos consume it, without printing or storing secret values in documentation.

## Constraints / Non-Goals

- Do not print, copy, commit, or store API key values in any new artifact.
- Do not rotate, delete, move, or physically centralize any secret values in this track.
- Do not edit application source code; only documentation/config/hygiene files are in scope.
- Respect the user's preference: convenience and agent discoverability are prioritized over heavy secret-manager hardening.
- Do not migrate to OS keychain, cloud secret manager, dotenvx, direnv, or symlink-based loading in this track.
- Do not delete or alter Firebase `.env*` files, especially `C:\development\command-center\.firebase\command-ctr-pa\functions\.env.local`.
- Treat `NEXT_PUBLIC_*` Firebase values as project/public configuration, not high-risk secrets.

## Definition of Done

- `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc` exists and contains key names, services, scopes, canonical locations, consumers, duplicate locations, statuses, and notes, but no secret values.
- `C:\Users\DaveWitkin\.config\opencode\AGENTS.md` contains a short API key lookup rule instructing agents to consult the secrets index before repo searches.
- `C:\development\conductor-reporter\.gitignore` contains an `.env` ignore rule.
- The handover encoding artifacts in `C:\Users\DaveWitkin\.config\opencode\docs\handovers\api-key-centralization-handover-20260623.md` are cleaned up only for readability, without changing the audit findings.
- Deterministic validation commands confirm files exist, expected entries are present, no obvious secret values were introduced into the index, and the gitignore rule works.
- This Conductor track remains ready for execution by a build agent; this planning session does not execute implementation tasks.

## In-Scope Files

- Create: `C:\Users\DaveWitkin\.config\opencode\secrets-index.jsonc`
- Modify: `C:\Users\DaveWitkin\.config\opencode\AGENTS.md`
- Modify: `C:\development\conductor-reporter\.gitignore`
- Modify: `C:\Users\DaveWitkin\.config\opencode\docs\handovers\api-key-centralization-handover-20260623.md`
- Update during execution: `C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\plan.md`
- Update during execution: `C:\development\opencode\.conductor\tracks\20260623-api-key-centralization-index\metadata.json`

## Out-of-Scope Files / Actions

- Any `.env` file values.
- Any production/application source code file.
- Any API key rotation.
- Any deletion of inactive repo secrets until the user explicitly approves a separate cleanup track.
- Any Firebase toolchain changes.

## Architecture Decision

Use a **metadata-only secrets index** as the control plane for discoverability. The index is not the source of secret values; it maps service/key names to existing canonical locations and consumers. Physical centralization can be evaluated later after each consuming repo's env-loading behavior is confirmed.

## Required Index Shape

The new `secrets-index.jsonc` must use this shape:

```jsonc
{
  "version": 1,
  "last_audited": "2026-06-23",
  "policy": {
    "store_values": false,
    "preferred_lookup_order": [
      "C:\\Users\\DaveWitkin\\.config\\opencode\\secrets-index.jsonc",
      "documented canonical_location paths",
      "documented consumer repo .env files",
      "skill-scoped .env files"
    ],
    "never_print_secret_values": true
  },
  "secrets": {
    "example.service_key": {
      "env": "EXAMPLE_API_KEY",
      "service": "Example Service",
      "scope": "shared",
      "canonical_location": "C:\\path\\to\\canonical\\.env",
      "consumers": ["C:\\path\\to\\consumer"],
      "duplicate_locations": [],
      "status": "active",
      "rotation_impact": "single-location",
      "notes": "No values are stored in this index.",
      "last_verified": "2026-06-23"
    }
  }
}
```

Allowed `scope` values: `opencode-runtime`, `skill`, `shared`, `repo`, `project_config`, `public_config`, `unknown`, `orphan`.

Allowed `status` values: `active`, `unknown`, `stale`, `orphan`, `retired-candidate`.

## Initial Secrets to Represent

The build agent must populate entries for these audited keys only, using key names and locations from the handover document:

- OpenCode runtime: `OPENROUTER_API_KEY`, `OPENCODE_GO_DAVE_API_KEY`, `OPENCODE_GO_TIBERIUS_API_KEY`, `ZAI_API_KEY`.
- Skill scoped: `PERPLEXITYAI_API_KEY`.
- Shared automation candidates: `CLICKUP_API_TOKEN`, `SLACK_BOT_TOKEN`, `EXA_API_KEY`, `GOOGLE_API_KEY`, `GOOGLE_CSE_ID`, `SERPAPI_API_KEY`.
- Repo/project scoped: 2025 PA website KV/Redis/Resend/Vercel keys, command-center Firebase project config, margin-calc-firebase Firebase project config, govpulse GLM/SAM.gov/path config, create-new-github-repository GitHub token/user, cursor-clickup-mcp Slack/ClickUp/MCP config, music_duplicates AcoustID config.
- Orphan/retired-candidate: `OPENAI_API_KEY` and `GEMINI_API_KEY` in `C:\development\INACTIVE-content-marketing\.env.search`.

## Validation Strategy

Use PowerShell commands only. The previous session observed `glob`/`grep` failures with `Bun is not defined`; if file tools fail again, use PowerShell-first and do not repeatedly retry those tools.

Validation must confirm:

- `secrets-index.jsonc` exists.
- `AGENTS.md` includes the lookup rule.
- `conductor-reporter\.gitignore` ignores `.env`.
- `secrets-index.jsonc` contains expected key names.
- `secrets-index.jsonc` does not contain obvious secret assignment patterns such as `sk-`, `xoxb-`, `ghp_`, or raw `KEY=value` lines.
- Handover document no longer contains the known control characters from the prior session.

## Handoff Notes for Build Agent

- Execute `plan.md` exactly in order.
- Do not do extra repo exploration unless a validation command fails.
- Do not implement physical key movement even if it appears easy.
- Keep user-facing output brief and never include secret values.
