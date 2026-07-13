# Content Best Practices for GitHub

## Overview

When creating GitHub issues, pull requests, or comments, follow these guidelines to ensure content is:
- **Secure:** No sensitive system information
- **Reproducible:** Anyone can follow the steps
- **Professional:** Clean, focused, actionable

---

## ❌ NEVER Include

### Local System Information

**Bad:**
```
My username is DaveWitkin and I'm on Windows 11 at C:\Users\DaveWitkin\projects\
```

**Good:**
```
Environment: Windows 11, Node.js v20.x
Project path: /path/to/project
```

### Specific Paths

**Bad:**
```
The error occurred in /c/Users/DaveWitkin/.config/opencode/skills/github-management/SKILL.md
```

**Good:**
```
The error occurred in the skill file at: skills/github-management/SKILL.md
```

### Testing/Validation Artifacts

**Bad:**
```
## Test Results

Test 1a: PASSED - /c/Users/DaveWitkin/.config/test-output.log
Test 1b: FAILED - See validation track at .conductor/tracks/20260301-test/

Status: Complete
```

**Good:**
```
## Test Results

- Feature A: Working as expected
- Feature B: Has the following issue: [description]
```

### Internal Workarounds

**Bad:**
```
## Bug Description

The tool crashes. As a workaround, I manually edited the file at 
~/.config/opencode/temp/fix.json and it works for now.

TODO: Fix this properly later
```

**Good:**
```
## Bug Description

The tool crashes when processing large files.

## Expected Behavior

Should handle files up to 100MB without crashing.

## Actual Behavior

Crashes with "Out of memory" error on files > 50MB.
```

---

## ✅ ALWAYS Include

### Reproduction Steps

```markdown
## Steps to Reproduce

1. Install version 1.2.3
2. Run: `command --flag value`
3. Observe the error
```

### Version Information (Generic)

```markdown
## Environment

- OS: Windows 11 / macOS 14 / Ubuntu 22.04
- Node.js: v20.x (LTS)
- Tool version: 1.2.3
```

### Clear Bug Description

```markdown
## Bug Description

When using the `--verbose` flag, the output is truncated after 1000 characters.

## Expected

Full output should be displayed regardless of length.

## Actual

Output is cut off mid-message at exactly 1000 characters.
```

---

## Sanitization Checklist

Before posting any content to GitHub:

- [ ] No local usernames (use "user" or omit)
- [ ] No absolute paths (use relative paths or generic examples)
- [ ] No home directories (use `/home/user` or `~`)
- [ ] No Windows user folders (use `/path/to/...`)
- [ ] No testing tracks or validation files
- [ ] No "TODO" or internal notes
- [ ] No workarounds (describe the bug, not the hack)
- [ ] No environment variables with sensitive data
- [ ] No machine-specific IDs or GUIDs

---

## Examples by Content Type

### Bug Reports

**Sanitized:**
```markdown
## Bug: Export fails on large files

**Environment:**
- OS: Windows 11
- Node.js: v20.11.0
- Tool version: 1.2.3

**Steps:**
1. Create a file > 50MB
2. Run: `tool export large-file.txt`
3. Observe error

**Error:**
```
RangeError: Maximum call stack size exceeded
```

**Expected:** Export should complete successfully
**Actual:** Process crashes with stack overflow
```

### Pull Requests

**Sanitized:**
```markdown
## Fix: Handle large file exports

This PR adds streaming support for files > 50MB to prevent stack overflow.

**Changes:**
- Added chunked processing for large files
- Updated buffer size limits
- Added test case for 100MB file

**Testing:**
- [x] Unit tests pass
- [x] Manual test with 100MB file
- [x] No regression on small files
```

### Comments

**Sanitized:**
```markdown
Good catch! I can reproduce this on my end as well.

Looking at the code, the issue is in the buffer allocation. I'll submit a fix shortly.
```

---

## Quick Reference

| Instead of... | Use... |
|---------------|--------|
| `C:\Users\DaveWitkin\...` | `/path/to/project` or relative path |
| `/home/dave/...` | `~/project` or relative path |
| `DaveWitkin` | `user` or omit |
| `.conductor/tracks/2026...` | Omit testing artifacts |
| `TODO: fix this` | Just describe the issue |
| Workaround steps | Bug description only |

