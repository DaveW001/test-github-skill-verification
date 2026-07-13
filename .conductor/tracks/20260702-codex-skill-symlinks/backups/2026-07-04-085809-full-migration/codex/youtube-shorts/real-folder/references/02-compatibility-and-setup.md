# Compatibility and Setup (youtube-shorts)

## Requirements

- Python 3.10+
- Gemini CLI installed and authenticated
- Access to the content repository that contains the knowledge base inputs

## Gemini CLI authentication

This skill shells out to the `gemini` CLI. Ensure you can run this successfully in the same shell session where you'll run the script:

```bash
gemini --help
```

If the CLI supports a login/auth command in your environment, complete that once so `gemini` can run non-interactively.

## Content repository input

The generator loads company context from a knowledge-base file within a content repository.

To keep things portable, set `CONTENT_ROOT` to the root of that repository.

PowerShell:
```powershell
$env:CONTENT_ROOT = "./content-marketing"
python scripts/create_script.py
```

bash/zsh:
```bash
export CONTENT_ROOT=./content-marketing
python scripts/create_script.py
```

Notes:
- Use a relative path when possible (e.g., `./content-marketing`) so the skill works on other machines.
- If `CONTENT_ROOT` is not set, the script may fall back to an OS-specific default.
