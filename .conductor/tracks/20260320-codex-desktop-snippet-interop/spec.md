# Spec: OpenCode Snippet Interop for Codex Desktop

**Track ID**: 20260320-codex-desktop-snippet-interop  
**Created**: 2026-03-20  
**Status**: Planned  
**Priority**: High  
**Owner**: 01-Planner

---

## Problem Statement

The operator has an existing OpenCode snippet library in `C:\Users\DaveWitkin\.config\opencode\snippet` and wants the same snippet corpus to be usable from Codex Desktop with the same `#name` invocation style. The desired end state is one shared source of truth for snippets, no duplicate snippet maintenance across apps, and validation that can be run mostly by the agent rather than relying on manual operator testing.

---

## Current State (Verified)

1. OpenCode snippet source of truth exists at `C:\Users\DaveWitkin\.config\opencode\snippet`.
2. Snippets are Markdown files with YAML frontmatter supporting:
   - file-name based lookup
   - aliases
   - plain content expansion
   - shell command interpolation via ``!`command` ``
   - recursive includes via `#other-snippet`
   - block features such as `<append>` and experimental `<inject>`
3. Current snippet config at `C:\Users\DaveWitkin\.config\opencode\snippet\config.jsonc` enables debug logging but does not define alternative runtime behavior.
4. Codex Desktop local config is present at `C:\Users\DaveWitkin\.codex\config.toml` and currently exposes sandbox, apps, and MCP settings, but no verified native snippet registry or `#snippet` expander was found in local config/state inspection.
5. Codex Desktop local state shows prompt history and slash-command style usage patterns, but no verified built-in compatibility with OpenCode snippet files.

---

## Goal

Enable `#snippet-name` usage in Codex Desktop against the existing OpenCode snippet corpus, with behavior that is predictable, testable, and compatible with ongoing OpenCode usage.

---

## In Scope

- Inventory and normalize the effective OpenCode snippet feature set that must be supported for Codex Desktop compatibility.
- Determine whether Codex Desktop already has a native extension point that can support shared snippets.
- If native support is absent, design and implement a compatibility layer that:
  - reads from existing OpenCode snippet directories
  - resolves names and aliases
  - expands snippet content before prompt submission in Codex Desktop
  - preserves OpenCode compatibility by leaving source snippets unchanged
- Build an agent-run validation harness covering parser behavior, expansion behavior, recursion safety, and real-snippet fixture coverage.
- Automate as much end-to-end validation as possible, limiting operator work to a short final smoke check only if the desktop input surface cannot be fully exercised by the agent.
- Produce rollback and operating documentation.

---

## Out of Scope

- Rewriting the entire OpenCode snippet format.
- Maintaining two separate snippet libraries for OpenCode and Codex Desktop.
- Modifying unrelated Codex Desktop features unless required for snippet interoperability.
- Depending on brittle one-off clipboard workflows if a more deterministic integration point is available.

---

## Requirements

### Functional Requirements

1. Codex Desktop must support invoking a shared snippet by file name using `#name`.
2. Alias resolution must work for the same aliases already defined in OpenCode frontmatter.
3. Expansion must operate from the existing snippet directories:
   - global: `C:\Users\DaveWitkin\.config\opencode\snippet`
   - project override: `.opencode\snippet`
4. Recursive snippet includes must resolve deterministically and fail safely on cycles.
5. Shell interpolation behavior must be explicitly defined for Codex Desktop compatibility:
   - supported as-is, or
   - supported with Windows-safe adaptation, or
   - intentionally disabled with clear fallback behavior
6. `<append>` handling must preserve the practical output shape expected by the operator.
7. Experimental `<inject>` handling must be explicitly addressed rather than left ambiguous.

### Operational Requirements

1. OpenCode snippet files remain the single editable source of truth.
2. The chosen Codex Desktop approach must be restart-safe and documented.
3. The implementation must include clear logs or traces sufficient to debug failed expansions.
4. A rollback path must return Codex Desktop to its pre-integration state without modifying snippet content.

### Validation Requirements

1. Real snippet fixtures from the current global snippet directory must be used in automated tests.
2. Tests must cover at minimum:
   - file-name lookup
   - alias lookup
   - recursive include expansion
   - missing snippet behavior
   - duplicate alias conflict handling
   - cycle detection
   - shell command execution policy
   - append/inject block behavior
3. End-to-end validation must prove that a prompt containing `#context` or another existing snippet token results in the expected expanded prompt text before model submission.
4. Agent-run validation must be maximized; operator validation must be limited to final confirmation only if the desktop surface cannot be fully automated.

---

## Architecture Options to Resolve

### Option A: Native Codex Desktop Support

Use a built-in Codex Desktop command, skill, or config extension point if a verified native snippet hook exists.

### Option B: Command/Prompt Shim Inside Codex Ecosystem

Create a Codex-facing command or helper that expands snippets from the OpenCode directories before submission, while preserving the same snippet corpus.

### Option C: External Compatibility Layer

Implement a local Windows-side compatibility layer, likely PowerShell or AutoHotkey backed, that intercepts `#snippet` usage for Codex Desktop and replaces it with expanded text sourced from the OpenCode snippet files.

### Preferred Direction (Current Recommendation)

Assume Option C until Option A or B is proven. Current local evidence does not show native `#snippet` support in Codex Desktop, so the plan should prioritize a deterministic shim over speculation.

---

## Risks and Mitigations

- **Risk:** Codex Desktop has no supported native prompt-preprocessing hook.
  - **Mitigation:** Treat native support as a discovery gate, not an assumption; keep a compatibility shim as the main execution path.
- **Risk:** OpenCode shell interpolation syntax is Unix-oriented in some snippets and may not map cleanly to Windows PowerShell.
  - **Mitigation:** Add snippet portability audit and explicit execution-policy tests before enabling shell interpolation.
- **Risk:** Recursive includes or alias collisions behave differently between OpenCode and Codex Desktop.
  - **Mitigation:** Build parser/expander tests against the real snippet corpus and fail fast on ambiguous cases.
- **Risk:** Desktop UI automation may be partially inaccessible from the agent environment.
  - **Mitigation:** Separate parser/runtime proof from UI proof; keep only a minimal final manual smoke test if needed.
- **Risk:** The compatibility layer drifts from OpenCode semantics over time.
  - **Mitigation:** Keep fixture-based regression tests tied to the actual snippet directory and document supported semantics.

---

## Success Criteria

- A shared snippet from `C:\Users\DaveWitkin\.config\opencode\snippet` can be invoked in Codex Desktop using `#name`.
- The same snippet remains usable in OpenCode without modification.
- Alias resolution and recursive include behavior are validated against the real snippet corpus.
- The chosen shell interpolation policy is documented and tested.
- Agent-run tests provide primary validation evidence.
- Operator involvement is limited to a short final smoke confirmation only if required by desktop UI constraints.
- Rollback and troubleshooting instructions are written and validated.
