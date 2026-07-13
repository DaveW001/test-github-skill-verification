# Troubleshooting (github-create-repo)

## gh auth failures

- Check: `gh auth status`
- Fix: `gh auth login`

## Repo already exists

Options:
- use a different name
- link existing repo as remote:
  - `git remote add origin "<existing-clone-url>"` (or update origin if it already exists)

## "remote origin already exists"

Options:
- keep existing origin
- replace:
  - `git remote set-url origin "<clone-url>"`
- add different remote name:
  - `git remote add "<remote-name>" "<clone-url>"`

## Push fails (missing upstream)

- Confirm branch: `git branch --show-current`
- Push with upstream:

```bash
git push -u origin "<branch-name>"
```

## Org restrictions / permission denied

- Confirm owner/org targeted.
- Confirm the authenticated account has permissions.
- If org requires SSO, complete required authorization flow.
