# Lazy-Loaded Skills Reference

> **Status:** Thin reference / pointer.  
> **Authoritative architecture:** `C:\development\opencode\docs\runbooks\codex-skill-architecture.md`  
> **Updated:** 2026-07-06.

This file used to be the main lazy-skill architecture document. It is no longer the source of truth because the local skill architecture changed after the Codex parent-junction repair work in July 2026.

For exact current paths, allowed operations, forbidden junction operations, `.agents\skills` policy, and OneDrive backing policy, read:

```text
C:\development\opencode\docs\runbooks\codex-skill-architecture.md
```

## Current summary

- Default new skill location:

  ```text
  C:\Users\DaveWitkin\.opencode-lazy-vault\<skill-name>\SKILL.md
  ```

- Codex sees lazy-vault skills through this parent junction:

  ```text
  C:\Users\DaveWitkin\.codex\skills
    -> C:\Users\DaveWitkin\.opencode-lazy-vault
  ```

- Always-on OpenCode skills live under:

  ```text
  C:\Users\DaveWitkin\.config\opencode\skill
  ```

  Keep that set small; only put skills there when they should be injected into every OpenCode session.

- `C:\Users\DaveWitkin\.agents\skills` is legacy/non-authoritative on this machine. It is not the current OpenCode or Codex runtime source of truth.

- Many existing lazy-vault entries are junctions to `C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config`, but that is historical sync/backup plumbing. New skills should normally be real folders directly under the lazy vault unless cross-machine sync is explicitly requested.

## Skillful plugin

OpenCode lazy loading is provided by `@zenobius/opencode-skillful`. The active config points to the lazy vault:

```text
C:\Users\DaveWitkin\.config\opencode-skillful\.opencode-skillful.json
C:\Users\DaveWitkin\.config\opencode-skillful\opencode-skillful.config.mjs
```

Both should keep `basePaths` pointed at:

```text
C:/Users/DaveWitkin/.opencode-lazy-vault
```

## Usage workflow

1. Find lazy skills with `skill_find "<keyword>"`.
2. Load with `skill_use "<skill-name>"`.
3. If `skill_find` does not find an existing skill, inspect the lazy vault directly before assuming it is absent.

## Historical note

Older versions of this document said:

- The always-on native set was only four skills.
- `.agents\skills` should contain only native skill entries.
- New global skills should be created under `C:\Users\DaveWitkin\.config\opencode\skill`.

Those statements are stale. Use the runbook above instead.
