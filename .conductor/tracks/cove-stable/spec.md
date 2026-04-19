# CoVe System - Stable Release Specification

**Track:** cove-stable  
**Status:** PRODUCTION READY  
**Date:** 2026-03-12  
**Version:** 1.0.0

---

## Overview

The Chain-of-Verification (CoVe) system provides auditable, multi-agent fact-checking with tier-aware model routing and explicit status contracts.

---

## Architecture

### Agents

| Agent | Mode | Purpose | Model Tier |
|-------|------|---------|------------|
| `cove-orchestrator` | subagent | Coordinates workflow, reconciliation, reporting | mid |
| `cove-verifier` | subagent | Low-tier single-fact verification | low |

### Configuration

- Tier policy: `.opencode/model-tiers.json`
- Orchestrator config: `~/.config/opencode/agent/cove-orchestrator.md`
- Verifier config: `~/.config/opencode/agent/cove-verifier.md`

---

## Features

### 1. Tier-Aware Routing
- Low tier (cheap): Simple factual verification
- Mid tier (balanced): Claim reconciliation, reporting
- High tier (expensive): Reserved for security/legal/financial/medical

### 2. Preflight Check (10s budget)
- Tests verifier availability before full run
- Falls back to manual verification if verifier channel degraded

### 3. Retry Logic
- Automatic retry (1x) for malformed verifier responses
- Falls back to manual verification on second failure

### 4. Explicit Status Contracts
- `PIPELINE_STATUS`: PASS/FAIL (execution health)
- `CONTENT_STATUS`: PASS/FAIL (factual accuracy)
- `VERIFIER_STATUS`: PASS/FAIL (verifier execution health)

### 5. Mandatory Artifacts
- Execution log: `.conductor/verification-logs/YYYY-MM-DD-HHMMSS-cove-run.md`
- Verification report: `.conductor/verification-reports/YYYY-MM-DD-HHMMSS-report.md`

---

## Input/Output Contracts

### Input
Plain text draft to verify

### Output Format (exact headings)

```
PIPELINE_STATUS: PASS | FAIL
CONTENT_STATUS: PASS | FAIL
LOG_PATH: .conductor/verification-logs/YYYY-MM-DD-HHMMSS-cove-run.md
REPORT_PATH: .conductor/verification-reports/YYYY-MM-DD-HHMMSS-report.md
CORRECTED_DRAFT: "<corrected text>"
```

---

## Usage

```text
Run subagent_type "cove-orchestrator" on this draft:
"<draft text to verify>"
```

---

## Known Limitations

- Verifier spawn must be sequential (OpenCode limitation)
- Maximum 10s preflight check budget
- Retry limit: 1 attempt for malformed responses

---

## Validation Results

| Test | Result | Date |
|------|--------|------|
| End-to-end verification | PASS | 2026-03-12 |
| Claim extraction | PASS | 2026-03-12 |
| Verifier spawn | PASS | 2026-03-12 |
| Retry logic | PASS | 2026-03-12 |
| Artifact creation | PASS | 2026-03-12 |
| Path reporting | PASS | 2026-03-12 |

---

## Files

| File | Purpose |
|------|---------|
| `~/.config/opencode/agent/cove-orchestrator.md` | Orchestrator agent config |
| `~/.config/opencode/agent/cove-verifier.md` | Verifier agent config |
| `.opencode/model-tiers.json` | Tier routing policy |
| `.conductor/tracks/cove-stable/spec.md` | This specification |
| `.conductor/tracks/cove-stable/plan.md` | Implementation plan |
