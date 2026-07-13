# Agent Validation Checklist

## Frontmatter
- [ ] description is present and specific
- [ ] mode is set (primary or subagent)
- [ ] tools section is explicit
- [ ] permission.skill defined when skill tools are enabled

## Permissions
- [ ] Read-only agents grant ALL read-only research skills
- [ ] Write-enabled agents justify write/edit/bash access
- [ ] No unnecessary write-capable skills

## Location + Naming
- [ ] File location matches OpenCode rules (global vs project)
- [ ] Filename uses .md with no extra extension
- [ ] No duplicate agent names across locations

## Safety + Scope
- [ ] Agent purpose is narrow and explicit
- [ ] No hidden tool escalation
- [ ] Templates and references are linked, not duplicated
