# Plan: OpenCode Snippet Interop for Codex Desktop

**Track ID**: 20260320-codex-desktop-snippet-interop  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-03-20  
**Status**: Planned

---

## Phase 0: Baseline and Evidence Capture

- [ ] Snapshot the current OpenCode snippet corpus:
  - file inventory
  - alias inventory
  - feature inventory (`!` commands, recursive `#` includes, `<append>`, `<inject>`)
- [ ] Record the active snippet config from `C:\Users\DaveWitkin\.config\opencode\snippet\config.jsonc`.
- [ ] Record Codex Desktop baseline:
  - current `C:\Users\DaveWitkin\.codex\config.toml`
  - any local evidence of command/skill extension points relevant to prompt preprocessing
  - current Codex Desktop version/build if available locally
- [ ] Produce a portability audit identifying which existing snippets are:
  - fully portable
  - portable with shell-command adaptation
  - not safe to auto-run in Codex Desktop without special handling

## Phase 1: Native Hook Discovery (Hard Gate)

- [ ] Verify whether Codex Desktop has any native support for:
  - custom prompt templates
  - custom slash commands
  - input preprocessing
  - text expansion hooks
- [ ] Verify whether any native hook can preserve the required user experience:
  - user types `#name`
  - system resolves against shared OpenCode snippets
  - expanded text reaches the prompt before submission
- [ ] If native support exists, document exact configuration surface and proceed with a native implementation spike.
- [ ] If native support does not exist or is insufficient, formally choose the compatibility-layer path and record that decision in track artifacts.

## Phase 2: Shared Runtime Design

- [ ] Define the snippet resolution algorithm:
  - project overrides global
  - file name and aliases are case-insensitive or otherwise explicitly normalized
  - duplicate alias conflicts fail deterministically
- [ ] Define the expansion semantics for Codex Desktop:
  - content body handling
  - recursive includes
  - append blocks
  - inject blocks
  - shell command interpolation policy
- [ ] Choose implementation lane:
  - native Codex Desktop hook, or
  - Codex command/helper, or
  - external Windows compatibility shim
- [ ] Define logging and debug output expectations for failed or partial expansions.
- [ ] Define rollback path before implementation starts.

## Phase 3: Compatibility Implementation

- [ ] Implement a shared snippet loader against:
  - `C:\Users\DaveWitkin\.config\opencode\snippet`
  - `.opencode\snippet`
- [ ] Implement frontmatter parsing and body extraction.
- [ ] Implement name and alias indexing.
- [ ] Implement safe recursive expansion with cycle detection.
- [ ] Implement explicit handling for `<append>` and `<inject>`.
- [ ] Implement shell interpolation policy:
  - enable with safe runner, or
  - disable with explicit warning and test coverage
- [ ] Implement the Codex Desktop invocation path that preserves `#name` usage as closely as possible.
- [ ] Preserve OpenCode snippet files unchanged.

## Phase 4: Agent-Run Validation Harness

- [ ] Add automated tests for parser and resolver behavior.
- [ ] Add automated tests for real snippets in the current global corpus.
- [ ] Add negative tests for:
  - malformed YAML
  - duplicate aliases
  - missing includes
  - cyclic includes
  - shell command failures
- [ ] Add fixture snapshots for expanded output of representative real snippets such as:
  - `#context`
  - `#conductor-spec`
  - `#code-review`
- [ ] Add validation logs or reports that can be archived under this track.

## Phase 5: End-to-End Codex Desktop Proof

- [ ] Automate prompt expansion proof as far as the environment allows:
  - launch or attach to the desktop-compatible path if possible
  - inject a prompt containing an existing snippet token
  - confirm expanded text before send
- [ ] If direct desktop automation is not feasible, automate the nearest deterministic boundary:
  - expander output
  - input-shim behavior
  - clipboard or text insertion behavior
- [ ] Run regression checks against OpenCode usage assumptions so the shared snippet files still behave as expected there.
- [ ] Capture evidence of actual behavior in an artifact report.

## Phase 6: Operator-Minimized Final Validation

- [ ] Reduce operator work to one short smoke check only if still required after agent-run testing.
- [ ] Provide a single exact validation script for the operator:
  - type one or two known snippet invocations
  - confirm visible expansion/result
- [ ] Record operator result and fold it into the final validation report.

## Phase 7: Documentation and Handover

- [ ] Write operating instructions:
  - how Codex Desktop snippet interop works
  - where snippets live
  - what syntax/features are supported
  - how to troubleshoot failures
- [ ] Write rollback instructions.
- [ ] Document any remaining semantic differences between OpenCode and Codex Desktop.
- [ ] Close the track only after the validation matrix is complete and evidence is stored.

---

## Acceptance Checklist

- [ ] Shared OpenCode snippets are callable from Codex Desktop with `#name` or the closest feasible equivalent explicitly approved by the operator.
- [ ] OpenCode remains the single source of truth for snippet content.
- [ ] Real-snippet automated coverage exists for the current snippet corpus.
- [ ] The chosen architecture is documented and justified by verified local evidence.
- [ ] Agent-run validation covers the majority of testing effort.
- [ ] Rollback and troubleshooting docs are complete.
