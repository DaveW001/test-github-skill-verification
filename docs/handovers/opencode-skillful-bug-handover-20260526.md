# Session Handover: opencode-skillful Bug & Skill/MCP Ecosystem Research

**Date:** 2026-05-26
**Session ID:** opencode-skillful-bug-research
**Status:** Awaiting Gemini deep research results

---

## 1. Original Task

Research GitHub issues for @zenobius/opencode-skillful OpenCode plugin bug:
- **Error:** TypeError: __require is not a function at dist/index.js
- **Root cause:** Package uses Bun-specific import.meta.require (via un build --target bun) in an ESM bundle loaded by Node.js/Electron (OpenCode Desktop)

## 2. Key Findings

### Repository
- **URL:** https://github.com/zenobi-us/opencode-skillful
- **Status:** ARCHIVED (read-only, no new issues/PRs possible)
- **npm package:** @zenobius/opencode-skillful@1.2.5 (latest, published 2026-02-13)
- **License:** MIT

### Issue Search Results
- **No matching issues found** across all keywords: __require, ESM/CommonJS/CJS, undling/esbuild, 
ot a function
- Repo has 13 historical issues, none related to this bug
- No newer releases after v1.2.5

### Root Cause Analysis (Verified by Downloading npm Tarball)

**Build command** (.mise/tasks/build):
`ash
bun build ./src/index.ts --outdir dist --target bun
`

**Line 28 of dist/index.js** (833KB bundled file):
`js
var __require = import.meta.require;
`

import.meta.require is a **Bun-only API** -- undefined in Node.js/Electron.

**Crash site** (line 3389, inside gray-matter's CJS wrapper):
`js
var require_gray_matter = __commonJS((exports, module) => {
  var fs = __require("fs");  // <- TypeError here
  ...
});
`

**Only 4 __require references in entire bundle:**
| Line | Usage | Guarded? |
|------|-------|----------|
| 28 | Definition (ar __require = import.meta.require;) | N/A |
| 1037 | _require = __require; (js-yaml binary) | Yes (try/catch) |
| 1330 | _require = __require; (js-yaml function) | Yes (try/catch) |
| 3389 | ar fs = __require("fs"); (gray-matter) | **No -- crash site** |

**Evidence markers:**
- Line 1 of dist/index.js: // @bun (Bun bundler output marker)
- package.json: "type": "module", "main": "dist/index.js", **no xports field**

### Package Metadata
`json
{
  "name": "@zenobius/opencode-skillful",
  "version": "1.2.5",
  "type": "module",
  "main": "dist/index.js",
  "module": "src/index.ts",
  "repository": "https://github.com/zenobi-us/opencode-skillful"
}
`

### Release History
| Version | Date |
|---------|------|
| v1.2.5 | 2026-02-13 (latest) |
| v1.2.4 | 2026-02-05 |
| v1.2.3 | 2026-01-03 |
| v1.2.2 | 2026-01-03 |
| v1.2.1 | 2026-01-02 |
| v1.2.0 | 2025-12-30 |
| v1.1.0 | 2025-12-26 |
| v1.0.0 | 2025-12-06 |

## 3. Actions Taken

1. Loaded github-management skill
2. Found repo: zenobi-us/opencode-skillful
3. Searched issues with 4 keyword sets -- all returned empty
4. Listed all 13 issues (all closed) -- none match
5. Listed all 8 releases -- v1.2.5 is latest
6. Downloaded npm tarball and verified __require in dist/index.js
7. Analyzed build config (.mise/tasks/build, mise.toml, package.json)
8. Drafted GitHub issue with root cause, crash site, evidence, and fix suggestions
9. Attempted to create issue via gh issue create -- **failed: repo is archived**
10. Verified archived status via GitHub API

## 4. Drafted GitHub Issue (Never Submitted)

**Title:** [BUG] TypeError: __require is not a function -- plugin fails to load on OpenCode Desktop (non-Bun runtime)

Full draft was prepared with:
- Description, error message, root cause analysis
- Specific crash site (line 3389, gray-matter)
- Evidence table (4 __require references, // @bun header)
- Environment details (Windows 11, OpenCode Desktop, v1.2.5)
- Steps to reproduce
- Three possible fix approaches (change target, conditional exports, external deps)

**Not submitted because the repo is archived.**

## 5. User's Follow-Up Request

The user wants to find **alternatives** to opencode-skillful with these requirements:

### Must-Have
- **Lazy-loaded skills** -- ~100+ skills that only consume tokens when actively used
- **Lazy-loaded MCP servers** -- ~50+ MCP servers that only connect on-demand
- **Well-maintained** -- active development, not archived
- **Open source** (GitHub) -- preferred
- **Free or extremely low cost**

### Nice-to-Have
- Combined skill + MCP management in one solution
- Native OpenCode compatibility
- Community adoption

## 6. Deep Research Prompt Created

A detailed research prompt was created for Google Gemini covering:
- OpenCode's built-in skill system maturity
- Third-party OpenCode plugins on npm
- MCP server lazy-loading / discovery tools
- Combined skill + MCP management solutions
- OpenCode's roadmap (issues, discussions, releases)
- Evaluation criteria (maintenance, cost, token efficiency, scalability)

**Status:** User will run this prompt in Google Gemini. Results are pending.

## 7. Potential Paths Forward (Discussed)

1. **Contact maintainer** -- npm: @zenobius, GitHub org: zenobi-us
2. **Fork and fix** -- Change --target bun to --target node, publish under own scope
3. **Raise with OpenCode** -- Report to https://github.com/anomalyco/opencode
4. **Local patch** -- Polyfill import.meta.require in 
ode_modules (fragile)
5. **Find alternative** -- Current focus, awaiting Gemini research results

## 8. Relevant URLs

| Resource | URL |
|----------|-----|
| GitHub Repo (archived) | https://github.com/zenobi-us/opencode-skillful |
| npm Package | https://www.npmjs.com/package/@zenobius/opencode-skillful |
| OpenCode Docs | https://opencode.ai/docs |
| OpenCode GitHub | https://github.com/anomalyco/opencode |
| MCP Protocol | https://github.com/modelcontextprotocol |

## 9. Next Steps

1. **Await Gemini deep research results** from the prompt provided in Section 6
2. **Evaluate findings** against criteria: maintenance, open source, free/low-cost, lazy-loading for both skills and MCP
3. **Recommend top solution(s)** with migration path from opencode-skillful
4. **If no suitable alternative exists**, consider forking opencode-skillful and applying the --target node fix

## 10. Context Notes for Next Agent

- The user's **number one priority is skills** (lazy-loaded), MCP is secondary but desired
- The user prefers **open source on GitHub** over paid solutions
- The user wants something that can scale to **100+ skills and 50+ MCP servers**
- The opencode-skillful plugin is **currently non-functional** on OpenCode Desktop due to the Bun-specific build target
- The repo being **archived** means no upstream fix is coming
- OpenCode's own built-in skill system may have evolved -- worth investigating as a primary alternative
