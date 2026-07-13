# Superseded Note - Skill Junction Unification

Date: 2026-07-06

This track is **superseded** and should not be executed as written.

## Why

The original May 2026 plan proposed a single-source skill layout where both of these paths would become parent junctions to the lazy vault:

```text
C:\Users\DaveWitkin\.codex\skills
C:\Users\DaveWitkin\.agents\skills
```

Later work refined the architecture. The active Codex path is now correctly implemented as:

```text
C:\Users\DaveWitkin\.codex\skills
  -> C:\Users\DaveWitkin\.opencode-lazy-vault
```

But `.agents\skills` is no longer treated as a required active surface. Current evidence shows it is legacy/non-authoritative for this machine's OpenCode/Codex setup.

## Current authority

Use this runbook for the current policy:

```text
C:\development\opencode\docs\runbooks\codex-skill-architecture.md
```

Use this later Conductor track for the parent-junction root-cause repair history:

```text
C:\development\opencode\.conductor\tracks\20260704-session-continuation-codex-skill-architecture-fix
```

## Stale assumptions in this track

- Skill counts are outdated.
- The always-on set is outdated.
- Plugin config location/details are outdated.
- `.agents\skills` is no longer a required mirror.
- New skills should not default to `C:\Users\DaveWitkin\.config\opencode\skill`.
- OneDrive-backed lazy-vault junctions are optional historical sync plumbing, not the default for new skills.

## Current policy snapshot

- New normal skills default to real folders under `C:\Users\DaveWitkin\.opencode-lazy-vault`.
- Codex sees those skills through `C:\Users\DaveWitkin\.codex\skills` parent junction.
- Always-on OpenCode skills remain under `C:\Users\DaveWitkin\.config\opencode\skill` only when intentionally prompt-injected.
- `.agents\skills` should not be maintained as a partial live mirror.
