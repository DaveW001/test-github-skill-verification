# Prompt Suite: Osgrep CLI-Only Canary

**Track ID**: 20260312-osgrep-cli-only-reenable
**Purpose**: Fixed prompts for repeatable CLI-only validation.

## Core Usage Prompts

1. find code path for auth token refresh
2. find where feature flag X is read and written
3. locate all call sites of function Y and related interfaces

## Reliability and Edge Prompts

4. in the opencode repo, find conductor track references related to osgrep
5. in the spaced-path test repo, find refreshAuthToken definition

## Safety Prompts

6. run normal semantic discovery and verify no mcp workflow is used
7. force an osgrep failure and continue using grep/glob/read fallback

## Extended Reliability Prompts

8. run two semantic searches concurrently and verify no hang
9. run a semantic query while indexing and verify behavior remains stable
10. run a known-answer query and verify non-empty relevant result
11. run stale-index query before reindex and evaluate degradation behavior
12. run broad semantic query expected to return many matches
