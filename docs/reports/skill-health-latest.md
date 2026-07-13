# Skill Health Latest

> **Status:** Regenerated documentation snapshot after skill-architecture reconciliation.  
> **Generated:** 2026-07-06.  
> **Authoritative policy:** `C:\development\opencode\docs\runbooks\codex-skill-architecture.md`.

## Summary

The old skill-health report was stale and referenced obsolete assumptions about `.agents\skills`, native/global skill locations, and junction repair behavior.

Current verified architecture:

| Surface | Current status | Notes |
|---|---|---|
| `C:\Users\DaveWitkin\.opencode-lazy-vault` | Active lazy-vault root | Default for new skills. |
| `C:\Users\DaveWitkin\.codex\skills` | Parent junction to lazy vault | Active Codex skill surface. |
| `C:\Users\DaveWitkin\.config\opencode\skill` | Active always-on native root | Keep small; seven current always-on skills. |
| `C:\Users\DaveWitkin\.agents\skills` | Archived / absent | Not required by current OpenCode/Codex setup; archived to `C:\Users\DaveWitkin\.agents\archive\skills-20260706-144958`. |
| OneDrive `development-config` backing | Historical sync/backup plumbing; OneDrive originals retained as backup | All 63 OneDrive-backed lazy-vault junctions localized to real folders on 2026-07-06 (track `20260706-lazy-vault-localization`). |

## Current always-on set

```text
conductor
conductor-pipeline
git-push
opencode-scheduler
osgrep
perplexity-search
skill-discovery
```

## Known non-blocking issues

### `.agents\skills` legacy drift

`.agents\skills` was legacy and partially broken, and it is not an active required surface under the current architecture. It has been archived and removed from the live location. Do not spend maintenance effort repairing it unless a future tool explicitly requires `.agents\skills`.

If it must be revived, prefer a deliberate parent junction to the lazy vault or configure that future tool to use `C:\Users\DaveWitkin\.codex\skills` / the lazy vault directly. Do not maintain partial child-junction mirrors.

### OneDrive-backed vault entries (localized 2026-07-06)

Previously, many lazy-vault entries were junctions to:

```text
C:\Users\DaveWitkin\OneDrive - Packaged Agile\Documents\development-config\.opencode-lazy-vault\<skill-name>
```

**Status (2026-07-06):** All 63 OneDrive-backed junctions were converted to local real folders (content-identical, SHA256-verified) via track `20260706-lazy-vault-localization`. The OneDrive originals remain as a backup layer. Current vault inventory: 70 real folders, 7 native-backed always-on junctions, 0 OneDrive-backed junctions, 0 broken, 0 self-referential.

## Superseded reports / tracks

The following should not be used as current architecture guidance:

```text
C:\development\opencode\.conductor\tracks\20260502-skill-junction-unification
```

It is now marked superseded. Use:

```text
C:\development\opencode\docs\runbooks\codex-skill-architecture.md
```

## Health-check guidance for future reports

A future automated health report should check:

1. `C:\Users\DaveWitkin\.codex\skills` is a parent junction to `C:\Users\DaveWitkin\.opencode-lazy-vault`.
2. No self-referential child junctions exist under the lazy vault.
3. Every active lazy-vault skill directory intended for use contains `SKILL.md`.
4. The always-on native set remains intentionally small.
5. No script creates per-skill child junctions under `C:\Users\DaveWitkin\.codex\skills`.
6. `.agents\skills` is ignored unless explicitly reactivated by a documented decision.

Do not auto-create or auto-repair `.agents\skills` child junctions based on this report.
