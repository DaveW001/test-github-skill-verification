# Migration Inventory

## Keep Native

- conductor
- git-push
- osgrep
- perplexity-search

## Do Not Move / Not A Skill

- `.osgrep` — hidden osgrep cache/index directory under `C:\Users\DaveWitkin\.config\opencode\skill`; it does not contain `SKILL.md` and should not be moved to the lazy skill vault.

## Move To Lazy Vault

- agent-writer
- calendar-schedule
- calendar-today
- clickup
- clickup-cli
- command-writer
- content-trend-researcher
- design-system-extractor
- doc-to-markdown
- email-auto-sorter
- email-draft-reply
- email-routing-config
- email-to-clickup
- firebase-deployment-specialist
- first-principles-mastery
- frontend-design
- gemini-proxy
- github-create-repo
- github-management
- gmail-draft-reply
- gmail-inbox-triage
- google-calendar-schedule
- google-calendar-today
- google-contacts
- html-demo-design
- huashu-design
- image-generator
- image-manifest-builder
- image-to-html-reconstruction
- knowledge-graph-builder
- markdown-pdf-publisher
- markdown-render
- notebooklm-cli
- notebooklm-meta-prompt
- outlook-email-search
- outlook-inbox-triage
- pa-ui-design
- powershell-master
- pptx-to-pdf-converter
- scheduled-job-best-practices
- session-retro
- skill-writer
- snippet-writer
- terminal-aliases
- thinking-partner
- unified-calendar-today
- webapp-testing
- windows-task-scheduler
- youtube-shorts

## Inventory Verification

- Native skills: 4
- Lazy skills listed here: 49
- Non-skill cache directories excluded: 1 (`.osgrep`)

Note: Prior audit counted 53 unique skills because package-provided skills such as `snippets` may come from npm package cache rather than `C:\Users\DaveWitkin\.config\opencode\skill`. This migration inventory covers the currently observed canonical skill directories under `C:\Users\DaveWitkin\.config\opencode\skill`.
