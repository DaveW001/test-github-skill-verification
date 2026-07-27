# Spec: Comprehensive Agent Definitions and AGENTS.md Optimization & Validation

## Goal

Perform a comprehensive, evidence-backed audit, optimization, and real-path validation covering:
1. Global Codex & OpenCode configuration files (C:\Users\DaveWitkin\.codex\config.toml, C:\Users\DaveWitkin\.codex\AGENTS.md, C:\Users\DaveWitkin\.config\opencode\AGENTS.md).
2. All custom OpenCode agent definition files (C:\Users\DaveWitkin\.config\opencode\agent\*.md, 25 active agent files).
3. All active repository/directory AGENTS.md files (41 local files across 9 qualifying roots in C:\development).
4. Real static resolution and validation of every referenced file path, script, and doc link across all instruction and agent files (eliminating deferred REF-02 unverified flags).
5. Correction of cross-client reference leakage, missing structural headings, and stale instructions across all clone/upstream files.

## Scope & Target Inventory (69 Total Target Files)

### Configuration & Global Instructions (3 files)
1. C:\Users\DaveWitkin\.codex\config.toml
2. C:\Users\DaveWitkin\.codex\AGENTS.md
3. C:\Users\DaveWitkin\.config\opencode\AGENTS.md

### Custom OpenCode Agent Definition Files (25 files under C:\Users\DaveWitkin\.config\opencode\agent\)
1. 01-planner.md
2. boost.md
3. brand-voice-validator.md
4. build.md
5. conductor-doc-writer.md
6. conductor-pipeline-orchestrator.md
7. conductor-plan-creator.md
8. conductor-plan-reviewer-alt.md
9. conductor-plan-reviewer.md
10. conductor-test-runner.md
11. conductor-test-writer.md
12. conductor-track-executor-glm51.md
13. conductor-track-executor-mimo2.5pro.md
14. conductor-track-executor.md
15. conductor-track-validator-alt.md
16. conductor-track-validator-m3.md
17. conductor-track-validator.md
18. cove-orchestrator.md
19. cove-verifier.md
20. gen-headlines.md
21. peer-review.md
22. pptx-deck-qa.md
23. pptx-outline-architect.md
24. pptx-template-onboarder.md
25. seo-auditor.md

### Active Local Repository AGENTS.md Files (41 files across 9 roots in C:\development)
- C:\development\02-Kx-to-process (1 file)
- C:\development\chief-of-staff (1 file)
- C:\development\command-center (1 file)
- C:\development\INACTIVE-content-marketing (2 files)
- C:\development\marketing (3 files)
- C:\development\marketing\marketingskills (1 file)
- C:\development\opencode-core-dcp-fix (15 files)
- C:\development\opencode-upstream (15 files)
- C:\development\opencodex (2 files)

## Core Requirements & Acceptance Criteria

1. **Codex CLI Config & Global Validation:**
   - Audit C:\Users\DaveWitkin\.codex\config.toml against Codex CLI schema. Fix invalid struct in [agents] section so codex features list succeeds cleanly.
2. **Custom Agent Definition Review (25 Files):**
   - Review each of the 25 custom OpenCode agent prompt files against agent-development-standards.md and model routing guidelines.
   - Fix broken path references, outdated model routing, ambiguous tool directives, or inconsistent formatting.
3. **Real Path & Reference Resolution (REF-02 Elimination):**
   - Perform static path checking on every file path, script reference, runbook, and guide mentioned in all AGENTS.md and agent/*.md files.
   - Fix broken relative/absolute paths, update ghost entries where targets exist, or explicitly tag permanently missing references with clean cross-client fallbacks.
4. **Structural & Content Remediation Across All Local Repos:**
   - Address structural findings in opencode-core-dcp-fix and opencode-upstream (e.g. missing Markdown headings, missing project context) rather than leaving them in place.
   - Clean up cross-client leakage in command-center and other repos (providing clear fallbacks when OpenCode-specific or Codex-specific tools are referenced).
5. **Backups, Verification, and Peer Review:**
   - Maintain pre-edit backups with SHA-256 hashes for all modified files.
   - Conduct independent peer review (Stage 2) using a separate subagent before proceeding to execution.
