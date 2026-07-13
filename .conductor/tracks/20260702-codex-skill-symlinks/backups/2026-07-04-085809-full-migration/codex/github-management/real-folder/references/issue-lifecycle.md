# Issue Lifecycle

## Creation

To create a new issue for a bug or feature request:

```bash
gh issue create --title "Short Description" --body "Detailed description of the issue"
```

For interactive creation:
```bash
gh issue create
```

### Important: Clean Your Content First!

Before creating an issue, ensure the body content:
- ✅ Contains no local paths (use relative paths)
- ✅ Contains no usernames or system-specific info
- ✅ Contains no testing/validation artifacts
- ✅ Describes the bug, not workarounds
- ✅ Is reproducible by anyone

**See [Content Best Practices](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/content-best-practices.md) for detailed examples.**

### Quick Sanitization Checklist

- [ ] Replace `/c/Users/username/...` with `/path/to/project`
- [ ] Remove `.conductor/tracks/...` references
- [ ] Remove "Status:" or tracking metadata
- [ ] Remove "TODO" items
- [ ] Generalize version numbers if specific to your build

## Searching and Listing

List open issues assigned to you:
```bash
gh issue list --assignee "@me"
```

Search for issues across the entire organization:
```bash
gh search issues --owner [org] --state open
```

## Status Updates

View details of a specific issue:
```bash
gh issue view [issue-number]
```

Close an issue when resolved:
```bash
gh issue close [issue-number]
```

## Adding Comments

When commenting on issues, apply the same sanitization rules:

```bash
gh issue comment [issue-number] --body "Your sanitized comment here"
```

