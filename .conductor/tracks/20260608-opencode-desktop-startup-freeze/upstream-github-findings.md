# Upstream GitHub Findings

Date: 2026-06-08

## Repository and release context

- Canonical upstream repo confirmed: `opencode-ai/opencode`
- Default branch: `main`
- Latest release reported by `gh repo view`: `v0.0.55`
- Release list reviewed: `v0.0.55` through `v0.0.46`
- The incident notes reference Desktop `1.16.0` / `1.16.2`, but that versioning does not appear in the upstream release metadata reviewed here.

## Commands run

- `gh auth status`
- `gh repo view opencode-ai/opencode --json nameWithOwner,url,defaultBranchRef,latestRelease`
- `gh release list --repo opencode-ai/opencode --limit 10`
- `gh issue list --repo opencode-ai/opencode --state all --search "renderer unresponsive constructMessageRows loadMessages Desktop SQLite session message timeline" --limit 30 --json number,title,state,url,createdAt,updatedAt,labels`
- `gh issue list --repo opencode-ai/opencode --state all --search "renderer unresponsive" --limit 20 --json number,title,state,url,createdAt,updatedAt,labels`
- `gh search commits --repo opencode-ai/opencode "constructMessageRows OR loadMessages OR session_message.seq OR renderer unresponsive OR opencode.db" --limit 20`

## Findings

- No upstream issue match was returned for the renderer/session-load symptom searches.
- No upstream commit match was returned for the constructor/message timeline/session database searches.
- Based on the upstream metadata reviewed, there is no direct evidence here that upgrading to a newer upstream release will address the Desktop startup freeze.

## Recommended next local action

- Proceed with the local Desktop state isolation steps in Phase 1.
- Preserve the backup created for `opencode.db` and `opencode.global.dat` before any state mutation.

