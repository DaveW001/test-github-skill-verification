# Spec

## Goal
Address the gaps identified in the peer review of the SkillShare adoption work. The peer review returned "Do not accept" because it could not independently verify artifacts and because several validation claims were overstated or insufficiently tested.

## Requirements
- [ ] Add tool-specific rollout matrix (OpenCode vs Claude Desktop vs Claude Cowork) to operations guide
- [ ] Add "what good looks like" outputs to quickstart (show expected terminal output at each step)
- [ ] Add recovery paths for common failures (gh/npm/terminal issues)
- [ ] Add "tested / not tested / partially tested" labels to all validation claims
- [ ] Reword "org invite = read access = can clone" to avoid overclaiming (we proved GitHub permission via API, not actual clone)
- [ ] Inspect humanizer skill for portability issues beyond Dave-personal refs (local paths, tool assumptions, brand-private context)
- [ ] Test loading humanizer in a clean SkillShare checkout (not just grep scan)
- [ ] Run clean global (not project-scoped) SkillShare install/sync test
- [ ] Document Claude Desktop/Cowork manual workflow (even if not fully tested)
- [ ] Create pilot invitation template for one real team member test
- [ ] Update operations guide with explicit "tested / not tested" labels

## Non-Requirements
- [ ] Actually running the pilot with a real team member (that's a human task)
- [ ] Generating a PAT for dwitkin-test (requires Dave to do it)
- [ ] Full end-to-end clone test as dwitkin-test (requires PAT, which we don't have)
- [ ] Screenshots in quickstart (nice-to-have, not blocking)

## Acceptance Criteria
- [ ] Operations guide has tool-specific rollout matrix
- [ ] Quickstart has "what good looks like" outputs for each step
- [ ] Quickstart has recovery paths for common failures
- [ ] All validation claims in operations guide have "tested / not tested" labels
- [ ] Humanizer skill passes portability audit (no hidden assumptions)
- [ ] Clean global SkillShare install/sync test documented in operations guide
- [ ] Claude Desktop/Cowork manual workflow documented
- [ ] Pilot invitation template created
- [ ] All tasks in plan.md marked [x]
- [ ] metadata.json status = complete
- [ ] tracks.md and tracks-ledger.md updated
