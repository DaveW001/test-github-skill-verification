# Activation Examples (youtube-shorts)

Use these examples when you want the agent to select and run the `youtube-shorts` skill.

## Natural language (agent)

- "Use the youtube-shorts skill to create a 60-second script about FedRAMP automation. Target persona is Claire. Include one concrete government stat."
- "Draft a YouTube Short script: why shared services fail in government. Make it evidence-first, no buzzwords."
- "Generate 3 alternate hooks for a B2G YouTube Short about zero trust, then pick the best and write the full script."
- "Write a short-form video script on modernizing COBOL systems; then run the Claire CIO review and revise until it passes."

## CLI (local)

Interactive:
```bash
python scripts/create_script.py
```

Non-interactive (topic + evidence):
```bash
python scripts/create_script.py "Zero Trust in practice" "OMB M-22-09"
```

Skip review:
```bash
python scripts/create_script.py "Procurement myths" --skip-review
```

## Prompts that work well

- Provide one specific artifact to anchor credibility: memo name, policy ID, GAO report number, NIST control family, etc.
- Ask for "under 130 words" if you want a tight Shorts pace.
- Ask for 2-3 suggested on-screen text overlays if you want editing guidance.
