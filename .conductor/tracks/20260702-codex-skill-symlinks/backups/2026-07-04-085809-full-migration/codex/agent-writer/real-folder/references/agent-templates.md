# Agent Templates

## Read-Only Subagent (Canonical)

```yaml
---
description: [What this agent does]
mode: subagent
tools:
  write: false   # Cannot create files
  edit: false    # Cannot modify files
  bash: false    # Cannot run shell commands
  skill: true    # CAN use all read-only skills
permission:
  skill:
    perplexity-search: allow
    notebooklm: allow
    content-trend-researcher: allow
    google_search: allow
    webfetch: allow
---
```

## Primary Agent (Template)

```yaml
---
description: [Primary agent with user-facing workflow]
mode: primary
tools:
  write: true   # Justify
  edit: true    # Justify
  bash: true    # Justify
  skill: true
permission:
  skill:
    perplexity-search: allow
    notebooklm: allow
    content-trend-researcher: allow
    google_search: allow
    webfetch: allow
---
```

## Write-Enabled Subagent (Template)

```yaml
---
description: [Specific purpose requiring write access]
mode: subagent
hidden: true

# Justification: list exactly what it writes/creates
# Example: Creates markdown reports in reports/.
tools:
  write: true
  edit: false
  bash: false
  skill: true
permission:
  skill:
    perplexity-search: allow
    notebooklm: allow
    content-trend-researcher: allow
    google_search: allow
    webfetch: allow
---
```
