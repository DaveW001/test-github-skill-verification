# Security (github-create-repo)

## Non-Negotiables

- Never print, paste, log, or commit secrets.
- Never include tokens in command examples or documentation.
- Redact sensitive values if they appear in output.

## Preferred Auth

Prefer GitHub CLI auth:

- `gh auth login`
- `gh auth status`

This avoids handling raw tokens in scripts and reduces accidental secret exposure.

## If a Script Requires a Token

Rules:
- Do not store secrets in the project repository.
- Keep `.env` (or secrets file) out of git via `.gitignore`.
- Do not echo token values.
- Use least privilege.

Safe placeholders:
- `<TOKEN_REDACTED>`
- `<SECRET_REDACTED>`
