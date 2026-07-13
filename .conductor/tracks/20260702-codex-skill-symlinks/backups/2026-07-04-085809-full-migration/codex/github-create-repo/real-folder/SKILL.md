---
name: github-create-repo
description: Create a GitHub repository for the current project directory and connect it to git (init repo, set origin, push). Use when the user asks to publish/push a project to GitHub.
compatibility:
  - PowerShell (pwsh) recommended
  - git
  - gh (GitHub CLI) recommended
---

# github-create-repo

Create a new GitHub repository from a local project directory, then optionally initialize git, add an origin remote, and push the default branch.

## Activation Examples

Use this skill when the user says things like:
- Create a GitHub repo for this folder
- Publish this project to GitHub
- Create the repo and set up origin
- Make this repo public/private

## Core Behavior

- Prefer gh workflows over custom scripts.
- Propose defaults (repo name, visibility, description) and confirm before creating anything.
- If the GitHub repo already exists, offer to link it as origin.

## CRITICAL: Default to PRIVATE Repositories

**ALWAYS default to creating PRIVATE repositories unless the user explicitly requests public.**

This is a security best practice. Only create public repositories when:
1. The user explicitly asks for public visibility
2. The project is specifically intended to be open source
3. No sensitive data, credentials, or proprietary code is present

## Safety Policy

- Never print, paste, log, or commit secrets (tokens, .env, credential files).
- Redact sensitive values if they appear in tool output.
- Default to PRIVATE repositories for security.

## Progressive Disclosure

- Preflight checks: references/preflight.md
- Usage patterns: references/usage.md
- Troubleshooting: references/troubleshooting.md
- Security guidance: references/security.md
