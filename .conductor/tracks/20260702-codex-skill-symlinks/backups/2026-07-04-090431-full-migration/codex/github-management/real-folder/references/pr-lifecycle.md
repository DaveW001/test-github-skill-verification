# PR Lifecycle

## Automated Body Drafting
When creating a PR, use the `--fill` flag to automatically use the first commit's message or title as the PR body:
```bash
gh pr create --fill
```

## Creation with Session Summaries
For complex changes, provide a summary:
```bash
gh pr create --title "Feature: X" --body "Summary of changes and impact..."
```

## Status Checks
Check the status of your current branch's PR:
```bash
gh pr status
```
Check CI/CD run status:
```bash
gh pr checks
```

## Merging
Merge the PR once approved and checks pass:
```bash
gh pr merge --auto --squash
```
