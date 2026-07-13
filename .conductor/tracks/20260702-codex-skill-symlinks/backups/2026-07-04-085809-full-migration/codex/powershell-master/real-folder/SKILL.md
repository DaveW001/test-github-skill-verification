---
name: powershell-master
description: PowerShell expert guidance for scripts, modules, CI/CD, and cloud automation. Use for PowerShell debugging, cross-platform pwsh, writing .ps1, module installs (Az/Microsoft.Graph/PnP/AWS), and secure automation.
compatibility: Works on Windows/Linux/macOS. Best with PowerShell 7+ (`pwsh`). Some examples require Windows PowerShell 5.1 or specific modules.
---

# PowerShell Master

Use this skill when the user wants PowerShell help and needs high-confidence guidance (syntax, modules, cross-platform, CI/CD, automation).

## Decision Tree

Use this skill when the user asks for:
- writing/debugging PowerShell scripts (.ps1), functions, modules
- cmdlets and module selection/install (PSGallery, Az, Microsoft.Graph, PnP, AWS Tools)
- CI/CD automation that uses PowerShell (GitHub Actions, Azure DevOps, Bitbucket)
- cross-platform PowerShell (pwsh on Linux/macOS) and portability fixes
- security best practices (credentials, signing, logging, constrained endpoints)

Do not use this skill when:
- the task is primarily Bash/shell scripting (use normal tools)
- the user needs only conceptual cloud guidance without PowerShell

## Quick Start

1) Ask what environment we're in:
- OS (Windows/Linux/macOS)
- PowerShell version (`pwsh -Version` or `$PSVersionTable`)
- execution context (interactive, scheduled task, CI runner)

2) Pick the right toolchain:
- Prefer PowerShell 7+ for cross-platform work.
- Use Windows PowerShell 5.1 only when required by legacy modules.

3) Provide a minimal, working snippet first, then harden:
- add parameter validation
- add error handling (`try/catch`, `$ErrorActionPreference`)
- add logging (without secrets)

## Activation Examples

Use this skill for prompts like:
- "Fix this PowerShell script" / "why is my .ps1 failing"
- "Write a PowerShell script to..."
- "Install and use the Az module" / "Connect-MgGraph example"
- "Make this PowerShell script work on Linux/macOS"
- "PowerShell in GitHub Actions / Azure DevOps pipeline"

## References

- Full reference (legacy content): `references/legacy-SKILL-2026-01-18.md`
