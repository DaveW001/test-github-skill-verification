# Plan: Comprehensive Agent Definitions and AGENTS.md Optimization & Validation

plan.md is the authoritative source of truth for execution progress.

## Outcome, Constraints, and Definition of Done

### Goal / outcome

Deliver an evidence-backed review, optimization, and real-path validation covering:
1. C:\Users\DaveWitkin\.codex\config.toml (resolve CLI schema compatibility for [agents]).
2. Global AGENTS.md files (C:\Users\DaveWitkin\.codex\AGENTS.md and C:\Users\DaveWitkin\.config\opencode\AGENTS.md).
3. All 25 custom OpenCode agent definition files in C:\Users\DaveWitkin\.config\opencode\agent\*.md.
4. All 41 active local repository AGENTS.md files across 9 roots in C:\development.
5. Real static path and link resolution for all referenced files/scripts (resolving REF-02 across all 69 targets).
6. Repair of structural findings in opencode-core-dcp-fix / opencode-upstream and cross-client tool leakage.

### Constraints / non-goals

- Back up every target file with SHA-256 validation prior to editing.
- Preserve pre-existing user changes and dirty worktrees.
- Use explicit patch/edit tools rather than unverified bulk rewrites.
- Conduct Stage 2 independent plan review via a subagent before execution.

### Definition of Done

- config.toml passes syntax/schema validation under Codex CLI (codex features list exits 0).
- All 25 custom agent files and 43 AGENTS.md files are audited with evidence in a unified manifest.
- Referenced file/script paths are statically verified on disk; 0 unverified REF-02 deferrals remain.
- All structural and cross-client issues identified in previous runs are fixed or given explicit fallbacks.
- Backups and change manifests are updated and verified.
- Stage 7 validation and terminal closeout pass cleanly.

## Pipeline Determination

- Track type: bookkeeping
- Selected mode: bookkeeping
- Path: 0 -> 1 -> 2 -> 5 -> 7 -> 9

## Tasks

- [x] **0.1 Stage 0 Baseline & Inventory Capture**
  - Verify full target inventory: 1 config file, 2 global instruction files, 25 custom agent files, 41 local repository files (69 total).
  - Inputs: Filesystem scan of global config, global AGENTS.md, custom agent definitions, and 41 local repository AGENTS.md files.
  - Procedure: Verify existence, record initial error state for config.toml via codex features list.
  - Evidence: baseline-report-20260727-140000.md
  - Recovery: On missing file, flag inventory gap and halt.
  - Authoritative acceptance check: baseline-report-20260727-140000.md exists and records KNOWN-RED for config.toml.

- [x] **1.1 Stage 1 Plan & Spec Authorization**
  - Author clean spec.md, plan.md, and metadata.json under .conductor/tracks/20260727-agents-and-agents-md-comprehensive-review/ free of control bytes.
  - Inputs: Review findings and track requirement scope.
  - Procedure: Write UTF-8 formatted spec.md, plan.md, and metadata.json.
  - Evidence: Verified byte count and control character count = 0.
  - Recovery: Re-encode string literals if control bytes are detected.
  - Authoritative acceptance check: spec.md, plan.md, and metadata.json contain 0 non-UTF8 control characters.

- [x] **2.1 Stage 2 Independent Peer Review**
  - Spawn an independent peer reviewer agent (stage2_rereview_v5) to review spec and plan, verify scope coverage, and produce review-report-stage2.md.
  - Inputs: spec.md, plan.md, metadata.json, baseline report.
  - Procedure: Spawn subagent Archimedes on gpt-5.6-terra (different model from creator gpt-5.6-sol), evaluate against all 5 prior logic gaps and 69-target scope.
  - Evidence: review-report-stage2.md
  - Recovery: Address feedback if verdict is NOT EXECUTION_READY.
  - Authoritative acceptance check: review-report-stage2.md returns EXECUTION_READY verdict and metadata.json has review_status: passed.

- [x] **5.1 Execution: Fix Codex config.toml Schema**
  - Adjust [agents] section format in C:\Users\DaveWitkin\.codex\config.toml so Codex CLI succeeds on configuration checks.
  - Inputs: C:\Users\DaveWitkin\.codex\config.toml
  - Procedure: Create pre-edit backup with SHA-256 hash. Convert default_subagent_model and default_subagent_reasoning_effort string fields under [agents] into valid struct representations or clean section mappings compatible with Codex CLI schema. Run codex features list.
  - Evidence: codex features list exit code and output log.
  - Recovery: If codex features list fails, restore pre-edit backup from manifest.
  - Authoritative acceptance check: codex features list exits with code 0 and emits 0 schema errors.

- [x] **5.2 Execution: Audit and Optimize 25 Custom OpenCode Agent Definitions**
  - Review all 25 files in C:\Users\DaveWitkin\.config\opencode\agent\.
  - Inputs: 25 .md files in C:\Users\DaveWitkin\.config\opencode\agent\.
  - Procedure: Build immutable 25-file manifest. For each file, audit against agent-development-standards.md, model routing, tool definitions, and path references. Back up files before edit. Apply fixes for broken paths or stale model routing. Verify each file.
  - Evidence: agent-audit-manifest.json recording initial hash, findings, applied changes, and final hash for all 25 files.
  - Recovery: Restore individual file backup if parsing or formatting degrades.
  - Authoritative acceptance check: agent-audit-manifest.json contains 25 valid entries with 0 unresolved errors.

- [x] **5.3 Execution: Real Path & Reference Resolution (REF-02) Across All 69 Target Files**
  - Statically inspect every file path, script reference, runbook, and guide mentioned in all AGENTS.md (2 global + 41 local) and agent/*.md (25 custom agent files).
  - Inputs: All 69 target files across workspace.
  - Procedure: Extract every referenced path or URL using static analysis. Test path existence relative to the source document location or system root. Repair broken relative paths, resolve ghost entries where targets exist, or add explicit fallback instructions for missing external targets.
  - Evidence: static-reference-resolution-matrix.json recording every extracted link, source file, resolved path, and final status (verified, repaired, fallback_added).
  - Recovery: Revert edit if path resolution creates ambiguity.
  - Authoritative acceptance check: static-reference-resolution-matrix.json contains 0 unverified REF-02 deferrals across all 69 targets.

- [x] **5.4 Execution: Fix Structural & Cross-Client Deficiencies in Local AGENTS.md Files**
  - Fix missing headings/formatting in opencode-core-dcp-fix and opencode-upstream. Resolve cross-client skill leakage (e.g., firebase-deployment-specialist in command-center).
  - Inputs: 41 local repository AGENTS.md files and 2 global instruction files.
  - Procedure: Create pre-edit backups for all modified files. Seed defect queue from prior portfolio findings. Add missing markdown headings to structural outliers in clone/upstream packages. Clean up cross-client tool references by providing explicit fallbacks for Codex/OpenCode differences.
  - Evidence: remediation-summary.json listing all structural and cross-client fixes applied.
  - Recovery: Restore backup if repository-specific context is altered.
  - Authoritative acceptance check: 0 retained structural findings or unhandled cross-client tool leaks remain in local AGENTS.md files.

- [x] **7.1 Stage 7 Independent Validation**
  - Run independent validation check across all modified files, backups, and live probes.
  - Inputs: All 69 target files, backup manifests, and audit reports.
  - Procedure: Dispatch independent validator subagent on gpt-5.6-terra to verify backup integrity, SHA-256 hashes, codex features list exit code 0, 0 control bytes, 0 unverified references, and completeness.
  - Evidence: validation-report-stage7.md
  - Recovery: Re-open Stage 5 for bounded corrections if validation fails.
  - Authoritative acceptance check: validation-report-stage7.md returns ready_to_close verdict.

- [x] **9.1 Stage 9 Closeout & Documentation**
  - Produce final review report, change manifest, doc update log, and update Conductor ledgers.
  - Inputs: Stage 7 validation report and execution logs.
  - Procedure: Write final portfolio review report, compile change manifest, update .conductor/tracks.md and .conductor/tracks-ledger.md.
  - Evidence: doc-update-log-stage9.md, updated tracks.md and tracks-ledger.md.
  - Recovery: Re-sync ledgers if discrepancies found.
  - Authoritative acceptance check: Conductor ledgers updated and terminal closeout complete.
