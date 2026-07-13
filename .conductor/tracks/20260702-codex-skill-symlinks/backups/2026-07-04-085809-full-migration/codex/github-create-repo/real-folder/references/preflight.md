# Preflight (github-create-repo)

Run these checks before creating or linking a GitHub repository.

## Tooling

- PowerShell available:
  - `pwsh -v` (preferred) or `powershell -v`
- git installed:
  - `git --version`
- GitHub CLI installed:
  - `gh --version`

## Authentication

- Confirm `gh` is authenticated:
  - `gh auth status`
- If not authenticated:
  - `gh auth login`

## Project State

- Confirm you are in the intended directory.
- Check if it is already a git repo:
  - `git rev-parse --is-inside-work-tree`
- If not a git repo, confirm whether to run:
  - `git init`

## Repo Naming + Visibility

Confirm:
- repo name (default suggestion: current folder name)
- visibility (private default unless user explicitly wants public)
- optional description
- owner/org (if relevant)

## Remote Safety

- Check if `origin` already exists:
  - `git remote -v`
- If it exists, confirm whether to keep/replace/add a different remote.
