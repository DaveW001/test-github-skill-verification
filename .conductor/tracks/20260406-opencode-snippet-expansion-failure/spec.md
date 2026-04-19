# Spec: Diagnose and Restore OpenCode Snippet Expansion

## Goal

Identify why `#snippet` expansion in OpenCode stopped working for existing snippets such as `#planrev`, document the most likely root causes, and produce an implementation-ready fix and validation plan that restores reliable snippet expansion.

## Context

- **User symptom:** entering a known snippet alias such as `#planrev` no longer expands inline; the raw hashtag passes through unchanged.
- **Known-good snippet file:** `C:\Users\DaveWitkin\.config\opencode\snippet\plan-review.md`
  - aliases include `planrev`, `plan-review`, and `revplan`
- **Active plugin config:** `C:\Users\DaveWitkin\.config\opencode\opencode.jsonc`
  - plugin entry includes `opencode-snippets@1.8.0`
- **Installed package:** `C:\Users\DaveWitkin\.config\opencode\package.json`
  - dependency includes `opencode-snippets: 1.8.0`
- **Current snippet config:** `C:\Users\DaveWitkin\.config\opencode\snippet\config.jsonc`
  - only `logging.debug: true`
- **Recent successful history:** snippet logs on `2026-04-02` and `2026-04-04` show normal startup and snippet expansion timing.
- **Recent failure evidence:** snippet logs on `2026-04-05` and `2026-04-06` show repeated parse/load failures:
  - `parseJsonc is not a function`
  - `matter is not a function`
- **Prior related track:** `.conductor\tracks\20260405-opencode-snippets-upgrade-1-8-0\`
  - upgrade verification passed, but it relied heavily on static checks and did not capture the later runtime failure now seen in daily logs.

## Key Findings From Research

### Highest-Likelihood Cause

1. **OpenCode host runtime/session state is stale or divergent from the installed plugin package**
   - direct standalone expansion works, but the user-facing OpenCode session still passes `#planrev` through unchanged.
   - runtime logs show intermittent startup failures and later successful startups, which fits a stale-process / mixed-runtime / restart-required failure better than a permanently broken snippet corpus.

### Supporting Causes To Evaluate

2. **OpenCode runtime/autoupdate changed plugin loading behavior after prior validation**
   - logs prove expansion worked on 2026-04-02 and startup worked on 2026-04-04, then broke on 2026-04-05/06.
3. **Intermittent or context-dependent loader behavior**
   - 2026-04-06 includes both failure bursts and later successful startup lines, suggesting multiple runtimes, stale processes, or non-deterministic loader behavior rather than a permanently missing file.
   - a live process check found three OpenCode-related processes on the machine (`opencode`, `OpenCode`, and `opencode-cli`), which increases the odds of divergent state between the GUI, CLI, and plugin host.
4. **Validation gap in the prior upgrade track**
   - previous track verified package presence, parsing assumptions, and version consistency, but did not lock in a repeatable end-to-end smoke test around real alias expansion plus log inspection after restart.

### New Evidence From Standalone Runtime Checks

5. **The installed plugin package expands `#planrev` correctly when invoked directly outside OpenCode**
   - a Bun script importing `./node_modules/opencode-snippets/dist/src/loader.js` and `./node_modules/opencode-snippets/dist/src/expander.js` loaded 46 snippets and expanded `#planrev` to the full `plan-review.md` body.
   - this strongly suggests the snippet corpus and plugin package are healthy, shifting suspicion toward the OpenCode host session/runtime, stale state, or using a different plugin instance than the one tested locally.
6. **The hyphenated form `#P-L-A-N-R-E-V` does not currently match**
   - direct plugin expansion leaves it unchanged; this is consistent with the documented alias behavior and indicates the real failure is not the hyphenated form itself.

## Requirements

- [ ] Determine whether the failure is caused by the plugin package itself, the OpenCode host runtime, cache/state, or an interaction between them.
- [ ] Confirm why `plan-review.md` exists and is valid, yet `#planrev` does not expand.
- [ ] Define the smallest safe fix path.
- [ ] Include verification steps that prove alias expansion, primary filename expansion, shell-enabled snippets, and startup logging all work.
- [ ] Include rollback options if the preferred fix fails.

## Non-Requirements

- [ ] Writing or refactoring production application code in this repository.
- [ ] Changing snippet content unless a malformed snippet file is proven causal.
- [ ] Reworking unrelated OpenCode plugins.
- [ ] Shipping the fix without end-to-end runtime testing.

## Acceptance Criteria

- [ ] A builder can execute the plan without additional discovery.
- [ ] The plan ranks the most likely root causes with supporting evidence.
- [ ] The plan includes explicit tests for `#planrev` and at least one non-alias snippet.
- [ ] The plan requires checking snippet logs for absence of `matter is not a function` and `parseJsonc is not a function` warnings.
- [ ] The plan includes a post-fix restart and regression smoke test sequence.
