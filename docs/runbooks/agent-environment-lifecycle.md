# Agent Environment Lifecycle

## Ownership
Dave Witkin owns all configuration. The manifest at agent-environment-manifest.json is the authoritative record.

## Change protocol
1. Canary: run the relevant test suite.
2. Validation: run all-suites acceptance; check baseline.
3. Promotion: record in owned-changes.jsonl; update manifest.
4. Rollback: restore from owned-changes.jsonl hash; re-run acceptance.

## Update triggers
- OpenCode or Codex version upgrade
- New skill added or removed
- Config file changed
- Skill topology change

## Known gaps
- Plugin-contributed skills: floating versions, no pinning
- SkillShare/lazy-vault junction: same-target ambiguity (explicit exception)
- Harness versions: floating (no pinning mechanism)

## Credentials
Never stored in manifest. Reference secrets-index.jsonc for locations.
