# Global Skills Index

**Purpose:** Reference index of all personal/global OpenCode skills installed at `C:\Users\DaveWitkin\.config\opencode\skill\`. These skills are available in every project and session.

> For project-specific skills, check `.opencode/skill/` in the project root.

---

## Content Creation

| Skill | Description |
|-------|-------------|
| `content-trend-researcher` | Research content and topic trends across web/social sources; produce data-driven article ideas and outlines |
| `image-generator` | Generate on-brand visual prompts for hero images and diagrams (LEGO 3D Isometric, Hand-Drawn Whiteboard styles) |
| `image-manifest-builder` | Analyze content to identify graphics needs; generate image-manifest.json with prioritized prompt drafts |
| `youtube-shorts` | Generate B2G YouTube Shorts scripts with skeptical CIO review loop and evidence-first hooks |

## Visuals & Design

| Skill | Description |
|-------|-------------|
| `design-system-extractor` | Extract design tokens and system elements from URLs or graphic files |
| `frontend-design` | Create distinctive, production-grade frontend interfaces with high design quality |
| `html-demo-design` | HTML Demo Design System — high-fidelity demos, mockups, prototypes, video capture (formerly huashu-design) |
| `pa-ui-design` | Packaged Agile UI design system for React/Next.js using Tailwind and shadcn/ui |

## NotebookLM & Research

| Skill | Description |
|-------|-------------|
| `notebooklm-cli` | Expert guide for NotebookLM CLI (`nlm`) and MCP server — create notebooks, add sources, generate podcasts/reports/quizzes |
| `notebooklm-meta-prompt` | Meta-Prompt v5.1 insight extraction — red-team thinking, expose blind spots, generate surgical sub-prompts from NotebookLM sources |
| `perplexity-search` | Web-grounded research with Perplexity (Sonar) via LiteLLM/OpenRouter |
| `osgrep` | Semantic code search in CLI-only canary mode |

## Development & Deployment

| Skill | Description |
|-------|-------------|
| `firebase-deployment-specialist` | Firebase deployment for Next.js projects (Hosting/Functions) |
| `github-create-repo` | Create GitHub repository, init git, set origin, push |
| `github-management` | GitHub workflow automation: issues, PRs, dashboards, upstream tracking |
| `powershell-master` | PowerShell expert guidance for scripts, modules, CI/CD, cloud automation |
| `webapp-testing` | Test local web applications using Python Playwright |

## Documents & Publishing

| Skill | Description |
|-------|-------------|
| `doc-to-markdown` | Convert PDF and HTML files to structured Markdown |
| `markdown-pdf-publisher` | Generate professional PDFs from Markdown using Vivliostyle pipeline |
| `markdown-render` | Convert Markdown files into polished, branded static HTML pages |
| `pptx-to-pdf-converter` | Convert PowerPoint presentations to PDF via COM automation |

## Productivity & Workflow

| Skill | Description |
|-------|-------------|
| `clickup` / `clickup-cli` | Manage ClickUp tasks, sprints, comments via `cup` CLI |
| `conductor` | Context-Driven Development — manage tracks, specs, plans in `.conductor/` |
| `git-push` | Standardized git stage+commit+push workflow for Windows |
| `session-retro` | Retrospective analysis after OpenCode sessions — capture changes, identify improvements (formerly retro) |
| `scheduled-job-best-practices` | Patterns for resilient, non-interactive scheduled OpenCode jobs |
| `terminal-aliases` | Add/update terminal aliases across PowerShell 5.x, 7.x, and Git Bash |
| `windows-task-scheduler` | Create and modify Windows scheduled tasks |

## Email & Communication

| Skill | Description |
|-------|-------------|
| `email-auto-sorter` | Headless inbox sorting — routes unread emails to priority folders |
| `email-draft-reply` | Draft email replies in Dave Witkin's voice using Microsoft 365 context |
| `email-to-clickup` | Convert email to ClickUp task and archive for Inbox Zero |
| `outlook-inbox-triage` | Triage Outlook inbox — sort, prioritize, decide whether to respond |

## Thinking & Analysis

| Skill | Description |
|-------|-------------|
| `first-principles-mastery` | First principles thinking — deconstruct problems, strip assumptions, rebuild from fundamentals |
| `thinking-partner` | Challenge assumptions, apply mental models, stress-test ideas, play devil's advocate |

## AI & Agent Tooling

| Skill | Description |
|-------|-------------|
| `agent-writer` | Create and update OpenCode agents |
| `command-writer` | Create and improve OpenCode slash commands |
| `skill-writer` | Create and update OpenCode skills with valid frontmatter |
| `snippet-writer` | Create and manage OpenCode snippets |
| `gemini-proxy` | Manage local Gemini API Key Rotator Proxy |
| `notebooklm-meta-prompt` | NotebookLM Meta-Prompt v5.1 insight extraction |

---

## Path Reference

| Location | Path | Scope |
|----------|------|-------|
| **Global skills** | `C:\Users\DaveWitkin\.config\opencode\skill\<name>\SKILL.md` | Personal, all projects |
| **Project skills** | `<repo>\.opencode\skill\<name>\SKILL.md` | Team, repo-specific |
| **Global templates** | `C:\Users\DaveWitkin\.config\opencode\templates\<name>.md` | Personal, all projects |
| **Global snippets** | `C:\Users\DaveWitkin\.config\opencode\snippet\<name>.md` | Personal, all projects |

---

## Adding a New Skill

See the **Skill Creation Runbook**: `C:\Users\DaveWitkin\.config\opencode\templates\skill-creation-runbook.md`

Quick path:
1. Create directory: `C:\Users\DaveWitkin\.config\opencode\skill\<skill-name>\`
2. Create `SKILL.md` with valid frontmatter (name must match directory)
3. Add reference files as needed (one level deep)
4. Run activation smoke test
5. Update this index with the new skill

---

*Last updated: 2026-04-25*
