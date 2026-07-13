# GitHub Dashboard

To get a bird's-eye view of your active tasks across all repositories.

## Active Issues
List all open issues assigned to Dave Witkin across all repos:
```bash
gh search issues --assignee "@me" --state open
```

## Active Pull Requests
List all open PRs authored by Dave Witkin:
```bash
gh search prs --author "@me" --state open
```

## Combined View
To see everything currently pending:
```bash
gh search issues --author "@me" --assignee "@me" --state open
```
