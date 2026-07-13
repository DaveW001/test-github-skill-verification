# Usage (github-create-repo)

Two supported paths:
1) Preferred: GitHub CLI (`gh`) end-to-end
2) Optional: user-provided PowerShell helper script (path supplied/configured)

## Path A: gh-only (recommended)

Create a repo and connect it to the current directory:

Private repo (common default):

```bash
gh repo create "<repo-name>" --private --source . --remote origin --push
```

Public repo:

```bash
gh repo create "<repo-name>" --public --source . --remote origin --push
```

Notes:
- `--source .` uses the current directory.
- `--remote origin` sets `origin`.
- `--push` pushes the current branch; confirm you are on the intended branch.

## Path B: PowerShell helper script

If the user has a helper script:
- Ask for its path (or use a configured env var like `GITHUB_REPO_SCRIPT`).
- Do not assume a hard-coded machine path.

Example usage:

```bash
pwsh -File "<PATH_TO_SCRIPT>" -Name "<repo-name>" -Description "<description>"
```

Then ensure local repo is linked and pushed:

```bash
git remote add origin "<clone-url>"
git push -u origin "<branch-name>"
```

## Confirmation Questions

Before creating/linking:
- repo name + owner/org
- visibility
- whether to initialize git
- whether to add/replace `origin`
- whether to push immediately
