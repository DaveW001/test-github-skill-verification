# Upstream Tracking

Track issues you have reported in external repositories to ensure they don't get lost.

## Finding My Reported Issues
Search for open issues you created in any repository:
```bash
gh search issues --author "@me" --state open
```

## Monitoring Specific Repos
If you reported a bug in a specific upstream repo:
```bash
gh issue list --repo [owner/repo] --author "@me"
```

## Proactive Check Flow
1. Run `gh search issues --author "@me" --state open`
2. For any relevant issues, check for recent activity: `gh issue view [number] --repo [owner/repo] --comments`
