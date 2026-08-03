# Rollback Manifest — 2026-07-31

The authoritative machine-readable manifest is `backup-manifest.json` in this track. Pre-existing modified files are backed up under:

`C:\Users\DaveWitkin\.config\opencode\backups\20260731-agents-md-remediation\`

Rollback rules:

- Restore only modified targets from their manifest backup and verify the recorded SHA-256.
- Remove only created targets marked `created-no-preimage` in the manifest.
- Never alter or remove `C:\Users\DaveWitkin\.config\opencode\.env` or `secrets-index.jsonc` as part of rollback.
- After rollback, rerun the validator and the bounded effective-config check, then record the reason in the Conductor execution log.
