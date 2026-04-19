# CoVe System - Implementation Plan

**Track:** cove-stable  
**Status:** COMPLETE  

---

## Phase 1: Foundation ✅ COMPLETE

### Tasks
- [x] Create cove-verifier agent config
- [x] Create cove-orchestrator agent config
- [x] Define model tier policy
- [x] Establish artifact directory structure

### Deliverables
- `~/.config/opencode/agent/cove-verifier.md`
- `~/.config/opencode/agent/cove-orchestrator.md`
- `.opencode/model-tiers.json`
- `.conductor/verification-logs/` directory
- `.conductor/verification-reports/` directory

---

## Phase 2: Core Workflow ✅ COMPLETE

### Tasks
- [x] Implement claim extraction logic
- [x] Implement neutral question generation
- [x] Implement sequential verifier spawning
- [x] Implement claim reconciliation
- [x] Implement corrected draft generation

### Deliverables
- Working claim-to-question pipeline
- Sequential verifier execution
- Verified/Corrected/Unverified classification

---

## Phase 3: Reliability ✅ COMPLETE

### Tasks
- [x] Add preflight availability check (10s budget)
- [x] Add fallback to manual verification
- [x] Add retry logic for malformed responses (1x retry)
- [x] Add artifact creation with exact path tracking
- [x] Add explicit status contracts (PIPELINE_STATUS, CONTENT_STATUS, VERIFIER_STATUS)

### Deliverables
- Preflight probe in orchestrator
- Retry logic with automatic fallback
- Exact file path reporting in responses
- Unambiguous status semantics

---

## Phase 4: Validation ✅ COMPLETE

### Tests
- [x] Single claim verification
- [x] Multiple claim verification (2-5 claims)
- [x] Correction detection (false claim)
- [x] Verification confirmation (true claim)
- [x] Artifact creation and persistence
- [x] Path reporting accuracy
- [x] Status contract compliance

### Results
All tests passed. System is production-ready.

---

## Phase 5: Documentation ✅ COMPLETE

### Tasks
- [x] Document agent configs
- [x] Document tier policy
- [x] Document usage patterns
- [x] Document known limitations
- [x] Create conductor track with spec and plan

### Deliverables
- Agent configuration files (documented inline)
- `.opencode/model-tiers.json` (documented)
- This implementation plan
- CoVe stable specification

---

## Maintenance

### Monitoring
- Watch for verifier spawn failures
- Monitor artifact creation success rate
- Track correction vs verification rates

### Future Enhancements (Optional)
- [ ] Parallel verifier spawning (when OpenCode supports it)
- [ ] Caching layer for repeated verifications
- [ ] Integration with external fact-checking APIs
- [ ] Metrics dashboard for verification accuracy

---

## Success Criteria

| Criteria | Status |
|----------|--------|
| End-to-end workflow executes without errors | ✅ |
| Factual errors are detected and corrected | ✅ |
| True claims are verified as accurate | ✅ |
| Artifacts are created with correct paths | ✅ |
| Status contracts are explicit and unambiguous | ✅ |
| System is stable across multiple test runs | ✅ |

---

**Status: PRODUCTION READY** ✅
