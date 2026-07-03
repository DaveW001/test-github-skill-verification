# SkillShare Evaluation and Decision

## Decision

VERDICT: Adopt SkillShare.

Dave has decided to move forward with SkillShare as the team's shared skill-distribution mechanism.

## Why SkillShare Was Chosen

SkillShare was chosen because it provides multi-tool auto-injection across Claude Desktop, Claude Cowork, OpenCode, and future AI-client targets.

SkillShare uses native Windows NTFS junctions without requiring administrator rights, ships as a single Go binary with no Node runtime dependency, includes `skillshare audit`, offers `skillshare ui` for a non-technical dashboard, and supports a single-source private-repo Git-backed model.

## Future Work / Revisit Later

Future work item 1: Per-user selective profiles are not built in; SkillShare is skill/target-centric opt-out filtering, not machine-centric sparse-checkout manifests.

Future work item 2: A background daemon is not built in; SkillShare is pull-based and manual through `skillshare sync`.

Future work item 3: Gotcha hardening is not built in; auth connectivity pre-checks, conflict-to-abort-and-notify behavior, and client cache reload guidance must be designed later.

## Easy Install Goal

The rollout goal is to find an easy install path for non-technical team members who use Claude Desktop, Claude Cowork, or OpenCode, with those AI clients able to help run copy-paste install commands.
