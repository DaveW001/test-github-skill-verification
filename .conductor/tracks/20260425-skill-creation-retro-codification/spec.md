# Spec

## Goal

Codify the retrospective findings from the `nlm-meta-prompt` skill creation session into reusable templates, checklists, and snippets so that future AI agents and human users can replicate high-quality skill creation without rediscovering best practices.

## Background

During this session we:
1. Created the `nlm-meta-prompt` skill (4 files: SKILL.md + 3 references)
2. Ran a full-session system retro identifying 6 systemic improvements
3. Identified 4 concrete codification deliverables

This track operationalizes those retro findings into durable, reusable artifacts.

## Requirements

- [ ] **Skill Creation Runbook**: Step-by-step checklist covering preflight, creation, fidelity guard, and validation — usable by both AI agents and humans
- [ ] **Retro Delivery Checklist for Skill Work**: Template with the 6 mandatory retro questions + systemic action mapping, specific to skill creation sessions
- [ ] **Verbatim Preservation Snippet**: Reusable snippet with instructions for preserving user-provided prompt blocks without summarization
- [ ] **Global Skill Index Note**: A discoverable index in the repo docs pointing to global skill assets so team members can find and reuse them

## Non-Requirements

- [ ] Modifying the existing `nlm-meta-prompt` skill (already delivered and validated)
- [ ] Creating a full retro skill (the `retro` skill already exists)
- [ ] Changing the skill-writer skill itself (would be a separate track)
- [ ] Automating retro execution (manual-triggered only)

## Acceptance Criteria

- [ ] All 4 deliverables exist at their target paths
- [ ] Skill Creation Runbook covers: naming check, path selection, frontmatter rules, fidelity guard, reference structure, activation smoke test
- [ ] Retro checklist includes all 6 questions from the retro format and maps answers to actionable categories
- [ ] Verbatim Preservation Snippet follows snippet-writer frontmatter standards
- [ ] Global Skill Index Note is in repo docs and references the actual global skill path
- [ ] Each file has been read-back validated for content correctness
