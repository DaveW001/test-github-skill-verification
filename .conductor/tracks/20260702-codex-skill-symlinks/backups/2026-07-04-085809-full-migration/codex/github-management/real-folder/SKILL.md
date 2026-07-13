---
name: github-management
description: Handles GitHub workflow automation including issues, PRs, cross-repo dashboards, and upstream issue tracking using the gh CLI.
---

# GitHub Management

Use this skill to automate GitHub workflows for solo developers. This includes managing issues, pull requests, cross-repo status tracking, and monitoring upstream contributions.

## Activation
- "Check my GitHub dashboard"
- "Create a PR for these changes"
- "Open an issue for the bug we found"
- "Track the issue I reported in the [repo] repository"
- "Give me a summary of my active PRs"

## Important Guidelines

### Content Security & Privacy
When creating GitHub issues, PRs, or comments:

1. **NEVER include local system information:**
   - Usernames (e.g., `DaveWitkin`, `AzureAD+DaveWitkin`)
   - Local paths (e.g., `/c/Users/...`, `C:\Users\...`, `~/.config/...`)
   - Machine-specific IDs or GUIDs
   - Environment variables with sensitive data

2. **NEVER include testing/validation artifacts:**
   - Test scripts or temporary files
   - Local debugging output with paths
   - Validation tracks or test plans (e.g., `.conductor/tracks/...`)
   - Internal-only documentation

3. **Clean file content before posting:**
   - Use relative paths only (`docs/guides/...`, not `/home/user/...`)
   - Redact or generalize system-specific identifiers
   - Remove "Status:" or tracking metadata meant for internal use

### Issue Content Best Practices

**DO include:**
- Clear bug descriptions
- Steps to reproduce
- Expected vs actual behavior
- Version numbers (generic, not build-specific)
- Error messages (sanitized)

**DO NOT include:**
- Internal workarounds or temporary fixes
- "TODO" items or notes to self
- Local file references
- Testing status or validation notes

### When in Doubt
- **Generalize:** Use `/path/to/project` instead of actual paths
- **Sanitize:** Replace usernames with generic terms
- **Minimize:** Only include what's needed to reproduce the issue
- **Ask:** "Would this expose sensitive system info?"

## Decision Tree

1. **Are you managing items in the current repo?**
   - **Issues:** Use `gh issue [create|list|view|close]`. See [Issue Lifecycle](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/issue-lifecycle.md).
   - **PRs:** Use `gh pr [create|status|view|merge]`. See [PR Lifecycle](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/pr-lifecycle.md).

2. **Are you looking for a bird's-eye view?**
   - Use `gh search issues` with specific flags for the user. See [Dashboard](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/dashboard.md).

3. **Are you tracking issues in external repositories?**
   - Use `gh search issues` filtered by author. See [Upstream Tracking](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/upstream-tracking.md).

## Core Commands
- `gh issue list --assignee "@me"`
- `gh pr status`
- `gh pr create --fill --draft`
- `gh search issues --author "@me" --state open`

## References
- [Issue Lifecycle](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/issue-lifecycle.md)
- [PR Lifecycle](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/pr-lifecycle.md)
- [Dashboard](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/dashboard.md)
- [Upstream Tracking](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/upstream-tracking.md)
- [Content Best Practices](file:///C:/Users/DaveWitkin/.config/opencode/skill/github-management/references/content-best-practices.md)
