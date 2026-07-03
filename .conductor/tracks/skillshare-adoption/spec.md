# SkillShare Adoption Prototype Spec

Track ID: `skillshare-adoption`

## Goal / Outcome

Adopt `runkids/skillshare` as Dave's team skill-distribution mechanism by documenting the evaluation decision, proving the local Windows sync mechanic, and producing a simple team quickstart for non-technical users who may be assisted by Claude Desktop, Claude Cowork, or OpenCode.

## Constraints / Non-goals

- The native file tools are considered unavailable because this session was reported as `Bun is not defined`; execution agents must use PowerShell-first via the `bash` tool and quote Windows paths with `-LiteralPath` and double-quoted paths.
- Do not scale rollout to all 5 team members in this track.
- Do not build per-user profile conventions, background daemon scheduling, or gotcha hardening in this track; record them as future work.
- Do not block on GitHub org repository creation or member provisioning for `https://github.com/packaged-agile`; treat it as deferred/manual unless `gh auth status` and owner access are already ready.
- Do not expose secrets or credential values in docs or logs.

## Definition of Done

- `docs/skill-share/evaluation-and-decision.md` exists and its body captures the adopt verdict, Dave's decision, SkillShare pros, gaps, and easy-install goal.
- SkillShare is installed on this Windows machine and `skillshare --version` or `ss --version` confirms the binary works.
- A minimal sample skill syncs into at least one local target directory and leaves a checkable artifact that proves the sync mechanic works.
- `docs/skill-share/quickstart-for-team.md` exists and is copy-pasteable for non-technical users or their AI assistant.
- The gaps are recorded explicitly as future-work/revisit-later items.
- Optional GitHub repo creation under `packaged-agile` is attempted only if auth/owner readiness is present, and never blocks completion.

## Source Context

- Objectives spec: `docs/skill-share/objectives.md`.
- Upstream project: `https://github.com/runkids/skillshare`.
- Install command: `irm https://raw.githubusercontent.com/runkids/skillshare/main/install.ps1 | iex`.
- Windows source directory: `%AppData%\skillshare\skills\`.
- Windows sync implementation: NTFS Junctions; admin rights should not be required.
- Useful commands: `init`, `sync`, `install <git-url>`, `update --all`, `audit`, `target <name> --mode copy`, `extras`, `commit`, `push`, `pull`, `ui`.

## Evaluation Verdict to Document

**VERDICT: Adopt SkillShare.** It is a better fit than the original objectives because it provides multi-tool auto-injection across the team's current AI clients and future targets, native Windows junctions without admin rights, a single Go binary with no runtime dependency, built-in `skillshare audit`, a `skillshare ui` dashboard for non-technical UX, a one-copy-per-machine symlink/junction model that reduces conflict surface, and a single-source private-repo Git-backed distribution model.

## Future Work / Revisit Later Gaps

1. No per-user selective profile system is built in. SkillShare is skill/target-centric with opt-out filtering through `.skillignore`, `targets:` frontmatter, and per-target include/exclude, not machine-centric sparse-checkout manifests.
2. No background daemon is built in. Sync is pull-based/manual through `skillshare sync` and can be wrapped later with Task Scheduler or LaunchAgent.
3. Gotcha hardening is not built in. Authentication/connectivity pre-checks, conflict-to-abort-and-notify behavior, and client cache reload guidance need a later conventions layer.

## Primary Deliverables

- `docs/skill-share/evaluation-and-decision.md`
- `docs/skill-share/quickstart-for-team.md`
- Local prototype source under `%AppData%\skillshare\skills\skillshare-sync-proof\`
- Local sync target artifact in at least one configured AI-client target directory
- Conductor execution log created by the executor
