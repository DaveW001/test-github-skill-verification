# Git Push Recovery Plan

**Status:** Awaiting independent validation  
**Scope:** Five repositories whose commits could not be pushed  
**Prepared:** July 22, 2026

## Purpose

This plan explains how to recover the failed pushes without losing local commits, overwriting remote work, force-pushing, or sending changes to repositories where Dave does not have write access.

The plan is intentionally non-destructive. **Do not execute the repository-specific commands until this plan has been reviewed and approved.**

## Current Situation

| Repository | Local state | Remote | Recommended destination |
|---|---|---|---|
| `opencode-dcp-child-fix` | `master` is ahead of `origin/master` by 4 commits; latest local commit is `65d3198` | `origin` = `Opencode-DCP/opencode-dynamic-context-pruning`; `fork` = `DaveW001/opencode-dynamic-context-pruning` | Push to Dave's fork, then optionally open a PR |
| `opencode-core-dcp-fix` | Local `dev` contains the DCP commits; the displayed ahead count is stale until fetch | `origin` = `anomalyco/opencode`; `fork` = `DaveW001/opencode`; live `fork/dev` already points to local commit `4a7fc1833` | Verify the fork already contains the commits; fix tracking and optionally open a PR |
| `marketing/marketingskills` | `main` is ahead of its local `origin/main` by 1 commit | `origin` = `coreyhaines31/marketingskills`; remote has advanced since the earlier check | Create/use Dave's fork and publish a reviewed branch there |
| `marketing/playground/authy-export` | `master` is ahead of `origin/master` by 1 commit; local commit `f2cd414` | `origin` = `skrashevich/authy-export` | Create/use Dave's fork and publish a reviewed branch there |
| `INACTIVE-content-marketing` | `main` is ahead by 1 and behind by 100 commits | Configured URL names `DaveW001/content-marketing`, which GitHub resolves to canonical `packaged-agile/content-marketing`; authenticated user has `ADMIN` access | Confirm the organization destination is intended, then reconcile on a new branch from current remote `main`; do not force-push |

## Non-Negotiable Safety Rules

1. Never force-push.
2. Never delete a branch, tag, or commit until the remote result is verified.
3. Never push to an upstream repository that returns permission denied.
4. Do not use `git reset --hard`, `git clean -fd`, or `git push --force` in this recovery.
5. Fetch before comparing a repository with its remote. The remote may have changed since the last inspection.
6. Create a local backup branch before rebasing, cherry-picking, or reconciling divergence.
7. Review staged files and commit contents before publishing, especially binary documents, generated files, and research artifacts.
8. Do not publish credentials, OAuth files, `.env` files, private keys, tokens, or secret-bearing backups.
9. A 403 is an access-control problem, not a Git merge problem. Do not keep retrying the same upstream push.
10. Stop immediately when any command returns a nonzero exit code. Do not continue after a failed `branch`, `switch`, `fetch`, `cherry-pick`, remote check, or validation command.
11. Before using a named backup or review branch, verify whether it already exists. Never overwrite or silently reuse an existing branch whose tip has not been reviewed.
12. Before publishing to a writable organization repository, confirm that the canonical GitHub owner and repository are the intended destination.

## Phase 0 - Non-Publishing Preflight

Run this for each repository before making changes:

```powershell
$repo = 'C:\path\to\repo'
git -C $repo status -sb
if ($LASTEXITCODE -ne 0) { throw 'Initial status failed' }
git -C $repo remote -v
if ($LASTEXITCODE -ne 0) { throw 'Remote inspection failed' }
git -C $repo branch --show-current
if ($LASTEXITCODE -ne 0) { throw 'Branch inspection failed' }
git -C $repo log --oneline --decorate -10
if ($LASTEXITCODE -ne 0) { throw 'History inspection failed' }
git -C $repo fetch --all --prune
if ($LASTEXITCODE -ne 0) { throw 'Fetch failed; do not trust remote-tracking refs' }
git -C $repo status -sb
if ($LASTEXITCODE -ne 0) { throw 'Post-fetch status failed' }
```

`fetch` updates local remote-tracking references and may prune local refs; it does not change working files or publish anything. Treat this phase as non-publishing, not strictly read-only.

After fetching, record:

```powershell
git -C $repo diff --name-status "origin/<branch>...<branch>"
if ($LASTEXITCODE -ne 0) { throw 'Diff comparison failed' }
git -C $repo log --left-right --oneline "origin/<branch>...<branch>"
if ($LASTEXITCODE -ne 0) { throw 'History comparison failed' }
```

If the file list contains unexpected secrets or unrelated work, stop and ask before continuing.

## Repository 1: `opencode-dcp-child-fix`

### Diagnosis

The push was attempted against `origin`, which is the organization repository `Opencode-DCP/opencode-dynamic-context-pruning`. Dave's fork is already configured as the `fork` remote. The latest local commit is:

```text
65d3198 fix(state): harden child-session persistence
```

The fork contains the first three of the four commits that are ahead of the stored `origin/master`, through `fc0530b`, but not the latest commit `65d3198`.

### Recovery

1. Review the local commit and run the repository's relevant tests.
2. Confirm the fork remote is Dave's fork, not the organization repository.
3. Push `master` to `fork`, never to `origin`.
4. Set the local branch's upstream to `fork/master` so future status output reflects the intended publish destination.
5. Optionally open a pull request from `DaveW001:master` to `Opencode-DCP:master` after review.

Commands:

```powershell
$repo = 'C:\development\opencode-dcp-child-fix'
git -C $repo show --stat --summary 65d3198
if ($LASTEXITCODE -ne 0) { throw 'Commit inspection failed' }
git -C $repo diff --check
if ($LASTEXITCODE -ne 0) { throw 'Diff validation failed' }
$testApproval = Read-Host 'Type TESTS-PASSED only after the repository-relevant tests have passed'
if ($testApproval -cne 'TESTS-PASSED') { throw 'Test gate was not approved; real push is blocked' }
$expectedFork = 'https://github.com/DaveW001/opencode-dynamic-context-pruning.git'
$actualFork = git -C $repo remote get-url fork 2>$null
if ($LASTEXITCODE -ne 0) { throw 'Fork remote lookup failed' }
if ($actualFork.TrimEnd('/') -ne $expectedFork.TrimEnd('/')) { throw "Existing fork remote is unexpected: $actualFork" }
git -C $repo fetch fork --prune
if ($LASTEXITCODE -ne 0) { throw 'Fork fetch failed' }
$intendedTip = git -C $repo rev-parse master
if ($LASTEXITCODE -ne 0) { throw 'Local branch lookup failed' }
$worktreeState = git -C $repo status --porcelain
if ($LASTEXITCODE -ne 0) { throw 'Working-tree inspection failed' }
if ($worktreeState) { throw 'Working tree is not clean; real push is blocked' }
git -C $repo push --dry-run fork master
if ($LASTEXITCODE -ne 0) { throw 'Push dry-run failed; real push is blocked' }
git -C $repo push fork master
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
$remoteOutput = git -C $repo ls-remote fork refs/heads/master
if ($LASTEXITCODE -ne 0) { throw 'Remote tip lookup failed' }
$remoteTip = $remoteOutput.Split()[0]
if ($remoteTip -ne $intendedTip) { throw 'Remote tip verification failed' }
git -C $repo branch --set-upstream-to=fork/master master
if ($LASTEXITCODE -ne 0) { throw 'Upstream tracking update failed' }
git -C $repo status -sb
if ($LASTEXITCODE -ne 0) { throw 'Final status check failed' }
```

**Pass condition:** `fork/master` contains `65d3198`, its remote SHA was verified with `ls-remote`, the working tree is clean, and no force-push was used.

**Rollback:** The push adds commits to the fork but does not rewrite existing history. If only the local tracking metadata must be undone, restore the previous upstream with `git -C $repo branch --set-upstream-to=origin/master master`. Do not delete backup/history branches or reset the local branch.

## Repository 2: `opencode-core-dcp-fix`

### Diagnosis

The push was attempted against `origin`, which is `anomalyco/opencode` and denied Dave's account. This repository already has a `fork` remote pointing to `DaveW001/opencode`. The live `fork/dev` branch already points to local commit `4a7fc1833`, so the two DCP commits have reached Dave's fork even though the attempted `origin` push failed. The local `origin/dev` comparison is stale until a fresh fetch; it is not the decisive recovery check.

### Recovery

This repository should not be pushed again until the fork state is verified. The likely fix is to make the local branch track `fork/dev` instead of `origin/dev`.

Commands:

```powershell
$repo = 'C:\development\opencode-core-dcp-fix'
$expectedFork = 'https://github.com/DaveW001/opencode.git'
$actualFork = git -C $repo remote get-url fork 2>$null
if ($LASTEXITCODE -ne 0) { throw 'Fork remote lookup failed' }
if ($actualFork.TrimEnd('/') -ne $expectedFork.TrimEnd('/')) { throw "Existing fork remote is unexpected: $actualFork" }
git -C $repo fetch fork --prune
if ($LASTEXITCODE -ne 0) { throw 'Fork fetch failed' }
git -C $repo ls-remote fork refs/heads/dev
if ($LASTEXITCODE -ne 0) { throw 'Fork branch lookup failed' }
git -C $repo log --left-right --oneline fork/dev...dev
if ($LASTEXITCODE -ne 0) { throw 'Fork/local comparison failed' }
$localTip = git -C $repo rev-parse dev
if ($LASTEXITCODE -ne 0) { throw 'Local dev lookup failed' }
$forkTip = git -C $repo rev-parse fork/dev
if ($LASTEXITCODE -ne 0) { throw 'fork/dev lookup failed' }
if ($localTip -ne $forkTip) { throw 'fork/dev and local dev differ; review before changing tracking or pushing' }
git -C $repo branch --set-upstream-to=fork/dev dev
if ($LASTEXITCODE -ne 0) { throw 'Upstream tracking update failed' }
git -C $repo status -sb
if ($LASTEXITCODE -ne 0) { throw 'Final status check failed' }
```

If the local branch is not exactly represented by `fork/dev`, review the difference and use a dry-run before publishing:

```powershell
git -C $repo push --dry-run fork dev
if ($LASTEXITCODE -ne 0) { throw 'Push dry-run failed; real push is blocked' }
git -C $repo push fork dev
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
$remoteOutput = git -C $repo ls-remote fork refs/heads/dev
if ($LASTEXITCODE -ne 0) { throw 'Remote tip lookup failed' }
$remoteTip = $remoteOutput.Split()[0]
if ($remoteTip -ne $localTip) { throw 'Remote tip verification failed' }
```

**Pass condition:** local `dev` tracks `fork/dev`, the fork contains both DCP commits, and no push is attempted to `anomalyco/opencode` without explicit write access.

**Rollback:** Changing the upstream is local metadata only. If the previous tracking relationship must be restored, run `git -C $repo branch --set-upstream-to=origin/dev dev`. Do not push or reset either branch; the fork already contains the commits.

## Repository 3: `marketing/marketingskills`

### Diagnosis

The local commit is:

```text
34f729f chore(gitignore): ignore .osgrep workspace artifacts
```

The configured `origin` belongs to `coreyhaines31/marketingskills`, so Dave does not have push access. The upstream remote also advanced after the earlier inspection; therefore the old local `origin/main` reference must not be trusted.

### Recovery

Use a personal fork and publish a review branch. Do not push directly to `coreyhaines31/marketingskills`.

1. Check whether `DaveW001/marketingskills` already exists.
2. If it does not exist, create a fork without cloning another working copy.
3. Add the fork as a new `fork` remote.
4. Fetch both remotes.
5. Preserve the current local branch with a backup branch.
6. Create a fresh branch from the current `origin/main`.
7. Cherry-pick `34f729f` onto that fresh branch.
8. Resolve and review any conflict, then push the review branch to Dave's fork.
9. Open a PR to the upstream repository only if the change is intended for that project.

Example commands. The remote and branch checks are deliberately explicit so a rerun cannot silently use an unexpected destination or stale branch:

```powershell
$repo = 'C:\development\marketing\marketingskills'
gh repo view DaveW001/marketingskills 2>$null
if ($LASTEXITCODE -ne 0) {
  gh repo fork coreyhaines31/marketingskills --clone=false
  if ($LASTEXITCODE -ne 0) { throw 'Fork creation failed' }
}
 $expectedFork = 'https://github.com/DaveW001/marketingskills.git'
 $actualFork = git -C $repo remote get-url fork 2>$null
 if ($LASTEXITCODE -eq 0) {
   if ($actualFork.TrimEnd('/') -ne $expectedFork.TrimEnd('/')) { throw "Existing fork remote is unexpected: $actualFork" }
 } else {
   git -C $repo remote add fork $expectedFork
   if ($LASTEXITCODE -ne 0) { throw 'Adding fork remote failed' }
 }
git -C $repo fetch --all --prune
if ($LASTEXITCODE -ne 0) { throw 'Fetch failed' }
git -C $repo show-ref --verify --quiet refs/heads/backup/pre-recovery-34f729f
if ($LASTEXITCODE -eq 0) { throw 'Backup branch already exists; inspect it before continuing' }
git -C $repo branch backup/pre-recovery-34f729f main
if ($LASTEXITCODE -ne 0) { throw 'Backup branch creation failed' }
git -C $repo show-ref --verify --quiet refs/heads/davew001/osgrep-ignore
if ($LASTEXITCODE -eq 0) { throw 'Review branch already exists; inspect it before continuing' }
git -C $repo switch -c davew001/osgrep-ignore origin/main
if ($LASTEXITCODE -ne 0) { throw 'Review branch creation failed' }
git -C $repo cherry-pick 34f729f
if ($LASTEXITCODE -ne 0) { throw 'Cherry-pick failed; use the rollback procedure below' }
git -C $repo diff --check
if ($LASTEXITCODE -ne 0) { throw 'Diff validation failed' }
git -C $repo push --dry-run fork davew001/osgrep-ignore
if ($LASTEXITCODE -ne 0) { throw 'Push dry-run failed' }
git -C $repo push -u fork davew001/osgrep-ignore
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
$intendedTip = git -C $repo rev-parse davew001/osgrep-ignore
if ($LASTEXITCODE -ne 0) { throw 'Review branch tip lookup failed' }
$remoteOutput = git -C $repo ls-remote fork refs/heads/davew001/osgrep-ignore
if ($LASTEXITCODE -ne 0) { throw 'Remote verification failed' }
$remoteTip = $remoteOutput.Split()[0]
if ($remoteTip -ne $intendedTip) { throw 'Remote tip does not match intended review branch' }
```

**Pass condition:** the new fork branch contains the `.gitignore` change on top of the current upstream `main`; its remote SHA was verified with `ls-remote`; the original upstream is untouched.

**Rollback:** If cherry-pick is in progress and must be abandoned:

```powershell
git -C $repo cherry-pick --abort
if ($LASTEXITCODE -ne 0) { throw 'Cherry-pick abort failed; do not switch branches; inspect git status' }
git -C $repo switch main
if ($LASTEXITCODE -ne 0) { throw 'Return to main failed; inspect git status' }
```

If the review branch was created but not pushed, leave it intact for inspection or switch back to `main`; never delete the backup branch. If it was pushed, leave the fork branch unchanged and close the PR or leave it for review.

## Repository 4: `marketing/playground/authy-export`

### Diagnosis

The local commit is:

```text
f2cd414 chore(authy-export): sync local changes
```

The configured `origin` belongs to `skrashevich/authy-export`, so Dave does not have push access. This is an external project, so publishing the change requires an explicit decision that the change should be contributed upstream.

### Recovery

Use the same fork-and-review approach as `marketingskills`, but pause at the decision gate before creating a public PR:

1. Review `f2cd414`, especially the Go source change.
2. Decide whether the change is intended as a contribution to `skrashevich/authy-export` or is only a local customization.
3. If contribution is intended, create/use `DaveW001/authy-export`.
4. Fetch the current upstream `master`.
5. Create a fresh branch from current upstream `master`.
6. Cherry-pick `f2cd414`.
7. Run the project's tests/build checks.
8. Push the review branch to Dave's fork and optionally open a PR.
9. If contribution is not intended, keep the commit local and record that no push is required.

Do not publish this repository's change merely because the original push failed.

Example commands after the contribution decision is approved:

```powershell
$repo = 'C:\development\marketing\playground\authy-export'
gh repo view DaveW001/authy-export 2>$null
if ($LASTEXITCODE -ne 0) {
  gh repo fork skrashevich/authy-export --clone=false
  if ($LASTEXITCODE -ne 0) { throw 'Fork creation failed' }
}
 $expectedFork = 'https://github.com/DaveW001/authy-export.git'
 $actualFork = git -C $repo remote get-url fork 2>$null
 if ($LASTEXITCODE -eq 0) {
   if ($actualFork.TrimEnd('/') -ne $expectedFork.TrimEnd('/')) { throw "Existing fork remote is unexpected: $actualFork" }
 } else {
   git -C $repo remote add fork $expectedFork
   if ($LASTEXITCODE -ne 0) { throw 'Adding fork remote failed' }
 }
git -C $repo fetch --all --prune
if ($LASTEXITCODE -ne 0) { throw 'Fetch failed' }
git -C $repo show-ref --verify --quiet refs/heads/backup/pre-recovery-f2cd414
if ($LASTEXITCODE -eq 0) { throw 'Backup branch already exists; inspect it before continuing' }
git -C $repo branch backup/pre-recovery-f2cd414 master
if ($LASTEXITCODE -ne 0) { throw 'Backup branch creation failed' }
git -C $repo show-ref --verify --quiet refs/heads/davew001/authy-sync
if ($LASTEXITCODE -eq 0) { throw 'Review branch already exists; inspect it before continuing' }
git -C $repo switch -c davew001/authy-sync origin/master
if ($LASTEXITCODE -ne 0) { throw 'Review branch creation failed' }
git -C $repo cherry-pick f2cd414
if ($LASTEXITCODE -ne 0) { throw 'Cherry-pick failed; use the rollback procedure below' }
git -C $repo diff --check
if ($LASTEXITCODE -ne 0) { throw 'Diff validation failed' }
# This repository has a Go module. Both checks must pass before publication.
Push-Location -LiteralPath $repo -ErrorAction Stop
try {
  go test ./...
  if ($LASTEXITCODE -ne 0) { throw 'Go tests failed; real push is blocked' }
  go build ./...
  if ($LASTEXITCODE -ne 0) { throw 'Go build failed; real push is blocked' }
} finally {
  Pop-Location -ErrorAction Stop
}
git -C $repo push --dry-run fork davew001/authy-sync
if ($LASTEXITCODE -ne 0) { throw 'Push dry-run failed' }
git -C $repo push -u fork davew001/authy-sync
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
$intendedTip = git -C $repo rev-parse davew001/authy-sync
if ($LASTEXITCODE -ne 0) { throw 'Review branch tip lookup failed' }
$remoteOutput = git -C $repo ls-remote fork refs/heads/davew001/authy-sync
if ($LASTEXITCODE -ne 0) { throw 'Remote verification failed' }
$remoteTip = $remoteOutput.Split()[0]
if ($remoteTip -ne $intendedTip) { throw 'Remote tip does not match intended review branch' }
```

**Pass condition:** Either the change is recorded as intentionally local, or the reviewed branch on `DaveW001/authy-export` contains `f2cd414`'s patch on top of current upstream `master`; tests pass; its remote SHA was verified with `ls-remote`; upstream remains untouched; and no sensitive data is included.

**Rollback:** If cherry-pick is in progress and must be abandoned:

```powershell
git -C $repo cherry-pick --abort
if ($LASTEXITCODE -ne 0) { throw 'Cherry-pick abort failed; do not switch branches; inspect git status' }
git -C $repo switch master
if ($LASTEXITCODE -ne 0) { throw 'Return to master failed; inspect git status' }
```

If the review branch was created but not pushed, keep the backup branch and switch back to `master`. Do not delete or reset the original commit.

## Repository 5: `INACTIVE-content-marketing`

### Diagnosis

The local `main` branch has one local commit, `922e6543`, but is also 100 commits behind the remote `main`. A direct push was correctly rejected as non-fast-forward. The configured URL names `DaveW001/content-marketing`, but GitHub resolves it to canonical repository `packaged-agile/content-marketing`; the authenticated user has `ADMIN` permission. Confirm that this organization repository is the intended publication destination before publishing. The local commit contains a large content/workflow update, so it must be reconciled against the current remote before publication.

### Recovery

Do not use force-push and do not immediately rebase the only copy of `main`.

**Mandatory publication decision gate:** Before creating the reconciliation branch or pushing it, confirm that the organization-owned `packaged-agile/content-marketing` repository is the intended destination. This commit changes 186 files, including PDFs, ZIP, DOCX, PPTX, XLSX, `.opencode/agent` and `.opencode/skill` material, generated drafts, research artifacts, and a malformed-looking filename. Treat it as potentially publishable internal material until reviewed.

Before cherry-picking, review:

```powershell
$repo = 'C:\development\INACTIVE-content-marketing'
git -C $repo show --stat --summary 922e6543
if ($LASTEXITCODE -ne 0) { throw 'Commit summary inspection failed' }
git -C $repo diff-tree --no-commit-id --name-status -r 922e6543
if ($LASTEXITCODE -ne 0) { throw 'Commit file-list inspection failed' }
```

Then require all of the following before publication:

1. Confirm every changed file is intended for the canonical organization repository.
2. Inspect the malformed-looking filename and remove or correct it if accidental.
3. Run the repository-approved secret scanner over the resulting branch; do not substitute `git diff --check` for secret scanning.
4. Inspect metadata and contents of every binary document/archive and confirm it is intended for publication.
5. Confirm generated drafts, research artifacts, and internal `.opencode` files are intentionally public.
6. Stop and sanitize or split the commit if any file is questionable.

1. Fetch the current remote.
2. Create a permanent backup branch pointing at the current local `main`.
3. Create a new reconciliation branch from `origin/main`.
4. Cherry-pick `922e6543` onto the reconciliation branch.
5. If Git reports conflicts, resolve them one file at a time; do not choose “ours” or “theirs” blindly.
6. Review the resulting diff and run available content validation/tests.
7. Push the reconciliation branch to the confirmed organization repository only after every publication gate passes.
8. Open a PR into `main`, or fast-forward/merge only after reviewing the PR result.

Example commands:

```powershell
$repo = 'C:\development\INACTIVE-content-marketing'
$canonical = gh repo view packaged-agile/content-marketing --json nameWithOwner,viewerPermission -q '"\(.nameWithOwner)|\(.viewerPermission)"'
if ($LASTEXITCODE -ne 0 -or -not $canonical.StartsWith('packaged-agile/content-marketing|')) { throw 'Canonical repository identity could not be verified' }
if ($canonical -notmatch '\|(ADMIN|MAINTAIN|WRITE)$') { throw "Insufficient permission on canonical repository: $canonical" }
$approval = Read-Host 'Type APPROVED only after confirming packaged-agile/content-marketing is the intended destination'
if ($approval -cne 'APPROVED') { throw 'Publication destination was not approved' }
git -C $repo show --stat --summary 922e6543
if ($LASTEXITCODE -ne 0) { throw 'Commit summary inspection failed' }
git -C $repo diff-tree --no-commit-id --name-status -r 922e6543
if ($LASTEXITCODE -ne 0) { throw 'Commit file-list inspection failed' }
git -C $repo fetch origin --prune
if ($LASTEXITCODE -ne 0) { throw 'Fetch failed' }
$originUrl = git -C $repo remote get-url origin
if ($LASTEXITCODE -ne 0) { throw 'Origin remote lookup failed' }
if ($originUrl.TrimEnd('/') -notmatch 'github\.com/(DaveW001|packaged-agile)/content-marketing\.git$') { throw "Unexpected origin URL: $originUrl" }
git -C $repo show-ref --verify --quiet refs/heads/backup/pre-recovery-content-main
if ($LASTEXITCODE -eq 0) { throw 'Backup branch already exists; inspect it before continuing' }
git -C $repo branch backup/pre-recovery-content-main main
if ($LASTEXITCODE -ne 0) { throw 'Backup branch creation failed' }
git -C $repo show-ref --verify --quiet refs/heads/reconcile/content-main
if ($LASTEXITCODE -eq 0) { throw 'Reconciliation branch already exists; inspect it before continuing' }
git -C $repo switch -c reconcile/content-main origin/main
if ($LASTEXITCODE -ne 0) { throw 'Reconciliation branch creation failed' }
git -C $repo cherry-pick 922e6543
if ($LASTEXITCODE -ne 0) {
  git -C $repo status
  throw 'Cherry-pick did not complete; resolve a conflict or use cherry-pick --abort before continuing'
}
```

If the cherry-pick is empty, the remote already contains the same change. In that case:

```powershell
git -C $repo cherry-pick --skip
if ($LASTEXITCODE -ne 0) { throw 'Cherry-pick skip failed' }
```

If conflicts occur:

```powershell
# Resolve files manually, then:
git -C $repo status
if ($LASTEXITCODE -ne 0) { throw 'Conflict status inspection failed' }
git -C $repo diff --name-only --diff-filter=U
if ($LASTEXITCODE -ne 0) { throw 'Unmerged-file inspection failed' }
git -C $repo add <resolved-file>
if ($LASTEXITCODE -ne 0) { throw 'Staging resolved file failed' }
git -C $repo cherry-pick --continue
if ($LASTEXITCODE -ne 0) { throw 'Cherry-pick continuation failed' }
```

If the conflict or review must be abandoned instead:

```powershell
git -C $repo cherry-pick --abort
if ($LASTEXITCODE -ne 0) { throw 'Cherry-pick abort failed; do not switch branches; inspect git status' }
git -C $repo switch main
if ($LASTEXITCODE -ne 0) { throw 'Return to main failed; inspect git status' }
```

After the cherry-pick completes, perform the mandatory content gates. The scanner and manual approval are hard prerequisites; do not continue to the push block if either fails or is unavailable:

```powershell
$gitleaks = Get-Command gitleaks -ErrorAction SilentlyContinue
if ($null -eq $gitleaks) { throw 'gitleaks is required for this publication gate; install/use the repository-approved scanner before continuing' }
& $gitleaks.Source detect --source $repo --redact --no-banner
if ($LASTEXITCODE -ne 0) { throw 'Secret scan failed or found findings; real push is blocked' }

git -C $repo diff --check
if ($LASTEXITCODE -ne 0) { throw 'Diff validation failed' }
git -C $repo diff --name-status origin/main...reconcile/content-main
if ($LASTEXITCODE -ne 0) { throw 'Resulting file-list review failed' }

$contentApproval = Read-Host 'Type CONTENT-APPROVED only after binary metadata/content and all internal/generated files are reviewed'
if ($contentApproval -cne 'CONTENT-APPROVED') { throw 'Content publication gate was not approved' }
```

Only after the canonical destination, secret scan, file review, binary review, internal-material review, and content approval have all passed:

```powershell
git -C $repo diff --check
if ($LASTEXITCODE -ne 0) { throw 'Diff validation failed; real push is blocked' }
git -C $repo push --dry-run origin reconcile/content-main
if ($LASTEXITCODE -ne 0) { throw 'Push dry-run failed; real push is blocked' }
git -C $repo push -u origin reconcile/content-main
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
$intendedTip = git -C $repo rev-parse reconcile/content-main
if ($LASTEXITCODE -ne 0) { throw 'Reconciliation branch tip lookup failed' }
$remoteOutput = git -C $repo ls-remote origin refs/heads/reconcile/content-main
if ($LASTEXITCODE -ne 0) { throw 'Remote verification failed' }
$remoteTip = $remoteOutput.Split()[0]
if ($remoteTip -ne $intendedTip) { throw 'Remote tip does not match intended reconciliation branch' }
```

**Pass condition:** the canonical organization destination was explicitly approved; secret scan, file-list review, binary review, internal-material review, and required validation all passed; the current remote history is preserved; the local content change is represented on top of it; the reconciliation branch's remote SHA was verified; and `main` was not overwritten.

**Rollback:** Before publication, `backup/pre-recovery-content-main` preserves the original local `main`, and `cherry-pick --abort` returns the worktree to the pre-cherry-pick state. After a review branch is pushed, do not merge it until the publication gate is approved; close the PR or leave the branch for review rather than rewriting `main`.

## Execution Order

Execute in this order:

1. `opencode-core-dcp-fix` — verify; it may already be solved on the fork.
2. `opencode-dcp-child-fix` — push to the already-configured personal fork.
3. `marketingskills` — create/use fork and cherry-pick onto current upstream.
4. `authy-export` — review contribution intent, then fork/cherry-pick if approved.
5. `INACTIVE-content-marketing` — reconcile the 100-commit divergence last.

The first four should not modify their upstream repositories. The fifth must use a new reconciliation branch because its remote has substantial intervening history.

## Validation Checklist for Another AI

An independent reviewer should confirm:

- Every 403 is handled by using a personal fork or requesting access, not by retrying the protected remote.
- `opencode-dcp-child-fix` pushes to `fork/master`.
- `opencode-core-dcp-fix` already has its commits on `fork/dev`, or has a safe dry-run push path.
- `marketingskills` and `authy-export` use fresh branches based on current upstream history.
- `INACTIVE-content-marketing` uses a backup branch plus a reconciliation branch and never force-pushes.
- Every repository has an explicit abort/rollback procedure, including `git cherry-pick --abort` where applicable.
- Existing fork remotes and proposed branch names are verified before they are reused; unexpected values stop execution.
- The canonical owner of `INACTIVE-content-marketing` is confirmed as `packaged-agile/content-marketing` before publication.
- Repository 5 passes its file-list, malformed-name, secret-scan, binary-review, and internal-material publication gates.
- Every prerequisite native command checks `$LASTEXITCODE` before a later command can publish or validate work.
- Repository 2 compares the local and fork branch tips directly with `rev-parse` before changing tracking.
- Every actual push is followed by `ls-remote` verification and its remote SHA is recorded.
- No command uses `reset --hard`, `clean -fd`, or `push --force`.
- No secrets or private files are added to a fork or pull request.
- Each repository has a clear pass condition and rollback path.

## Definition of Done

For each repository, one of these outcomes is recorded:

1. **Published:** the intended commit is visible on a writable fork or personal remote, with the commit SHA recorded.
2. **PR-ready:** the reviewed branch is pushed to a fork and awaits a pull request or owner decision.
3. **Already resolved:** the commit is already on the personal fork; only tracking metadata needs adjustment.
4. **Intentionally local:** the change is not intended for publication.
5. **Blocked:** access, conflict, or review requires a decision; local backup remains intact.

No repository is considered fixed merely because a local commit exists.
