---
name: Skill Writer
description: Guide users through creating Agent Skills for OpenCode. Use when the user wants to create, write, author, or design a new Skill, or needs help with SKILL.md files, frontmatter, or skill structure.
---

# Skill Writer

This Skill helps you create well-structured Agent Skills for OpenCode that follow best practices and validation requirements.

## When to use this Skill

Use this Skill when:

- Creating a new Agent Skill
- Writing or updating SKILL.md files
- Designing skill structure and frontmatter
- Troubleshooting skill discovery issues
- Converting existing prompts or workflows into Skills

## Instructions

### Step 1: Determine Skill scope

First, understand what the Skill should do:

1. **Ask clarifying questions**:
   - What specific capability should this Skill provide?
   - When should OpenCode use this Skill?
   - What tools or resources does it need?
   - Is this for personal use or team sharing?

2. **Keep it focused**: One Skill = one capability
   - Good: "PDF form filling", "Excel data analysis"
   - Too broad: "Document processing", "Data tools"

### Step 2: Choose Skill location

Determine where to create the Skill. There are now **four** skill locations, each with a different purpose:

**Always-Loaded Skills** (`~/.config/opencode/skills/`):
- Core skills loaded on every session (listed in system prompt)
- Only for skills used very frequently (e.g., `conductor`, `git-push`, `osgrep`, `perplexity-search`)
- Keep this directory small to minimize system prompt overhead

**Lazy-Loaded Skills — Lazy Vault** (`~/.opencode-lazy-vault/`):
- The primary location for most skills
- Discovered via the `skill_find` → `skill_use` lookup workflow
- NOT loaded into the system prompt until explicitly requested
- Ideal for domain-specific skills, tool integrations, and specialized workflows
- Contains bundled scripts, references, and templates
- Examples: `gmail-workspace`, `gmail-inbox-triage`, `firebase-deployment-specialist`, `pa-ui-design`
- **This is the recommended default location for new skills**

**Personal Skills** (`~/.config/opencode/skill/`):
- Individual workflows and preferences
- Experimental Skills
- Personal productivity tools

**Project Skills** (`.opencode/skill/`):
- Team workflows and conventions
- Project-specific expertise
- Shared utilities (committed to git)

**Note**: OpenCode also supports Claude-compatible paths (`.claude/skills/` and `~/.claude/skills/`) for cross-compatibility.

#### Skill Lookup Add-in

The lazy vault uses a skill lookup add-in pattern:
1. **`skill_find("<keyword>")`** — Search for a skill by keyword
2. **`skill_use(["<skill_name>"])`** — Load the skill into the current conversation
3. Skills in the lazy vault are NOT auto-discovered — they must be explicitly loaded

This pattern keeps the system prompt lean while making dozens of specialized skills available on demand.

### Step 3: Follow Naming Standards

⚠️ **CRITICAL REQUIREMENT**: The frontmatter `name` field MUST exactly match the directory name. This is not optional.

Before creating your skill, review the naming standards:

**See:** @~/.config/opencode/skill/SKILL-NAMING-STANDARDS.md

**Quick Reference:**
- **Directory name**: lowercase, hyphen-separated (e.g., `my-new-skill`)
- **Frontmatter name** (frontmatter `name`): must match the directory slug (eg `my-new-skill`) per OpenCode official rules
- NO EXCEPTIONS: Product names, branding, or special cases do NOT override this rule - the frontmatter name must always match the directory exactly

**Example:**
```yaml
---
name: my-new-skill
description: Brief description of what this skill does and when to use it
---
```

### Step 4: Create Skill structure

Create the directory and files:

```bash
# Lazy vault (recommended default)
mkdir -p ~/.opencode-lazy-vault/skill-name

# Personal
mkdir -p ~/.config/opencode/skill/skill-name

# Project
mkdir -p .opencode/skill/skill-name
```

For multi-file Skills:

```
skill-name/
├── SKILL.md (required)
├── reference.md (optional)
├── examples.md (optional)
├── scripts/
│   └── helper.py (optional)
└── templates/
    └── template.txt (optional)
```

### Step 5: Write SKILL.md frontmatter

Create YAML frontmatter with required fields:

```yaml
---
name: my-skill-name
description: Brief description of what this does and when to use it
---
```

**Field requirements**:

- **name**:
  - Must match the directory name (lowercase, hyphen-separated)
  - 1-64 characters
  - Must match regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
  - Example: directory `my-new-skill` -> `name: my-new-skill`
  - See naming standards: @~/.config/opencode/skill/SKILL-NAMING-STANDARDS.md

- **description**:
  - 1-1024 characters
  - Include BOTH what it does AND when to use it
  - Use specific trigger words users would say
  - Mention file types, operations, and context

**Optional frontmatter fields**:

- **license**: MIT, Apache-2.0, etc.
- **compatibility**: opencode (or other compatible systems)
- **metadata**: String-to-string map for additional context
- **triggers**: Structured discovery hints (optional, additive, no runtime behavior change)

**Optional `triggers` block (v1):**

```yaml
triggers:
  intent:
    - semantic search
    - architecture discovery
  user_phrases:
    - where do we handle
    - how does this work
  file_context:
    extensions: [ts, tsx, js]
    paths: [src/**, docs/**]
  tool_context:
    before_tools: [read, grep]
    with_tools: [bash]
  error_context:
    - unknown code location
  priority: high
  suggest_only: true
```

`triggers` is optional in v1. Keep `description` complete and standalone.

### Step 6: Write effective descriptions

The description is critical for OpenCode to discover your Skill.

**Formula**: `[What it does] + [When to use it] + [Key triggers]`

**Examples**:

✅ **Good**:
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

✅ **Good**:
```yaml
description: Analyze Excel spreadsheets, create pivot tables, and generate charts. Use when working with Excel files, spreadsheets, or analyzing tabular data in .xlsx format.
```

❌ **Too vague**:
```yaml
description: Helps with documents
description: For data analysis
```

**Tips**:
- Include specific file extensions (.pdf, .xlsx, .json)
- Mention common user phrases ("analyze", "extract", "generate")
- List concrete operations (not generic verbs)
- Add context clues ("Use when...", "For...")

### Step 7: Structure the Skill content

Use clear Markdown sections:

````markdown
# Skill Name

Brief overview of what this Skill does.

## Quick start

Provide a simple example to get started immediately.

## Instructions

Step-by-step guidance for OpenCode:
1. First step with clear action
2. Second step with expected outcome
3. Handle edge cases

## Examples

Show concrete usage examples with code or commands.

## Best practices

- Key conventions to follow
- Common pitfalls to avoid
- When to use vs. not use

## Requirements

List any dependencies or prerequisites:
```bash
pip install package-name
```

## Advanced usage

For complex scenarios, see [reference.md](reference.md).
````

### Step 8: Add supporting files (optional)

Create additional files for progressive disclosure:

**reference.md**: Detailed API docs, advanced options, OpenCode-specific configuration
**examples.md**: Extended examples and use cases
**scripts/**: Helper scripts and utilities
**templates/**: File templates or boilerplate

Reference them from SKILL.md:
```markdown
For advanced usage, see [reference.md](reference.md).

Run the helper script:
\`\`\`bash
python scripts/helper.py input.txt
\`\`\`
```

### Step 9: Validate the Skill

Check these requirements:

✅ **File structure**:
- ✓ SKILL.md exists in correct location
- ✓ Directory name is lowercase, hyphen-separated
- ✓ Frontmatter `name` matches directory slug (lowercase, hyphen-separated)

✅ **YAML frontmatter**:
- ✓ Opening `---` on line 1
- ✓ Closing `---` before content
- ✓ Valid YAML (no tabs, correct indentation)
- ✓ `name` follows naming rules
- ✓ `description` is specific and < 1024 chars

✅ **Content quality**:
- ✓ Clear instructions for OpenCode
- ✓ Concrete examples provided
- ✓ Edge cases handled
- ✓ Dependencies listed (if any)

✅ **Testing**:
- ✓ Description matches user questions
- ✓ Skill activates on relevant queries
- ✓ Instructions are clear and actionable
- [check] **Script syntax valid** (if scripts included): Python - python -c "import ast; ast.parse(...)"; PowerShell - PSParser::Tokenize(). Takes <1 second, catches broken code.

### Step 10: Functionally Test the Skill (Confirmed Skills)

Structural validation (Step 9) proves the skill files exist and the metadata is correct. **Functional testing proves the skill actually works when its instructions are followed.** Both are required for a confirmed skill.

#### Method A: Harness + sub-agent smoke test (recommended, works mid-session)

Use the skill smoke-test harness as the canonical Step 10 functional validation tool. Run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Users\DaveWitkin\.opencode-lazy-vault\skill-test-harness\scripts\skill-smoke-test.ps1" -SkillPath "<absolute-skill-path>" -PrintFunctionalPrompt
```

Then copy the printed `FUNCTIONAL PROMPT TEMPLATE` into a Task sub-agent. The sub-agent must attempt one representative skill test case using only the skill instructions and return either `FUNCTIONAL_SMOKE_TEST_PASSED` or `FUNCTIONAL_SMOKE_TEST_FAILED` with reasons.

Evaluate the sub-agent report:
- Did it understand the instructions without asking for missing context?
- Did it produce the expected output type and format?
- Did any step fail or require information not in the skill?
- Did it avoid forbidden actions such as real tokens, production APIs, or irreversible side effects?

If the sub-agent cannot complete the task, the skill instructions have a gap. Fix the skill before declaring it confirmed.

#### Method B: Live activation test (requires restart, optional)

1. Restart OpenCode to load the skill.
2. Verify the skill appears in the `skill` tool available skills list or is discoverable through `skill_find` / `skill_use`.
3. Ask realistic user requests that match the description and trigger metadata.
4. Verify OpenCode activates the skill and follows it correctly.

> Note: Method B requires a session restart and cannot be used mid-session. Prefer Method A for immediate confirmation.

#### Script syntax and functional checks (if scripts are included)

```powershell
# Python syntax check
python -c "import ast,pathlib,sys; ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')); print('SYNTAX VALID')" "scripts\helper.py"

# PowerShell syntax check
$errors = $null
[System.Management.Automation.PSParser]::Tokenize((Get-Content -Raw "scripts\Helper.ps1"), [ref]$errors) | Out-Null
if ($errors.Count -eq 0) { "SYNTAX VALID" } else { $errors; exit 1 }
```

For scripts with safe dry-run or `--help` modes, run at least one functional command and capture the output in the skill test report.

#### Distinction: structural validation vs functional confirmation

| Check type | Step | Proves | Does NOT prove |
|-----------|------|--------|----------------|
| Structural | Step 9 | Files exist, metadata valid, links resolve | The skill works |
| Functional | Step 10 | Instructions produce expected results | Files exist (that is Step 9) |

A skill that passes Step 9 but not Step 10 is structurally valid but unconfirmed. A confirmed skill passes both.

#### Test-case convention

Every new skill MUST include at least one functional test case in `tests\` or explicitly document that it is structurally valid but functionally unconfirmed. Use the canonical template at the `skill-test-harness` skill (`templates\test-case.template.md`). Record the closeout verdict from the Task sub-agent report as `FUNCTIONAL_SMOKE_TEST_PASSED` or `FUNCTIONAL_SMOKE_TEST_FAILED`.
### Step 11: Debug if needed

If OpenCode doesn't use the Skill:

1. **Make description more specific**:
   - Add trigger words
   - Include file types
   - Mention common user phrases

2. **Check file location**:
   ```bash
   ls ~/.opencode-lazy-vault/skill-name/SKILL.md
   ls ~/.config/opencode/skill/skill-name/SKILL.md
   ls .opencode/skill/skill-name/SKILL.md
   ```

3. **Validate YAML**:
   ```bash
   cat SKILL.md | head -n 10
   ```

4. **Check permissions**: Verify skill permissions in `opencode.json`:
   ```json
   {
     "permission": {
       "skill": {
         "skill-name": "allow"
       }
     }
   }
   ```

## Common patterns

### Read-only Skill

For Skills that should only read/analyze without making changes, document the expected tool usage:

```yaml
---
name: code-reader
description: Read and analyze code without making changes. Use for code review, understanding codebases, or documentation.
---

# Code Reader

## Instructions

1. Use Read, Grep, and Glob tools to analyze code
2. Never use Edit or Write tools
3. Provide analysis and recommendations only
```

### Script-based Skill

```yaml
---
name: data-processor
description: Process CSV and JSON data files with Python scripts. Use when analyzing data files or transforming datasets.
---

# Data Processor

## Instructions

1. Use the processing script:
\`\`\`bash
python scripts/process.py input.csv --output results.json
\`\`\`

2. Validate output with:
\`\`\`bash
python scripts/validate.py results.json
\`\`\`
```

### Multi-file Skill with progressive disclosure

```yaml
---
name: api-designer
description: Design REST APIs following best practices. Use when creating API endpoints, designing routes, or planning API architecture.
---

# API Designer

Quick start: See [examples.md](examples.md)

Detailed reference: See [reference.md](reference.md)

## Instructions

1. Gather requirements
2. Design endpoints (see examples.md)
3. Document with OpenAPI spec
4. Review against best practices (see reference.md)
```

## Best practices for Skill authors

1. **One Skill, one purpose**: Don't create mega-Skills
2. **Specific descriptions**: Include trigger words users will say
3. **Clear instructions**: Write for OpenCode, not humans
4. **Concrete examples**: Show real code, not pseudocode
5. **List dependencies**: Mention required packages in description
6. **Test with teammates**: Verify activation and clarity
7. **Version your Skills**: Document changes in content
8. **Use progressive disclosure**: Put advanced details in separate files

## Skill Creation Checklist (Required)

Use this checklist every time you create or update a Skill. It combines:
- Agent Skills standard fundamentals
- Advanced scaling patterns (decision trees, progressive disclosure)
- OpenCode-specific discovery/permissions rules

### 1) Scope and Intent

- ☐ One Skill = one capability (avoid "mega-skills")
- ☐ Clear "when to use" triggers (words a user will actually say)
- ☐ If the domain has multiple options/tools/products, include a decision tree that forces disambiguation

### 2) Naming and Placement (Discovery-Ready)

- ☐ Folder name is lowercase + hyphen separated (eg `my-new-skill`)
- ☐ `SKILL.md` filename is ALL CAPS
- ☐ Frontmatter includes `name` and `description`
- ☐ Skill name is unique across all locations (project + global)
- ☐ Follow OpenCode name rules for new skills: `^[a-z0-9]+(-[a-z0-9]+)*$` and 1-64 chars

### 3) Frontmatter and Description Quality

- ☐ `description` includes: what it does + when to use it + concrete trigger keywords
- ☐ `description` is 1-1024 characters
- ☐ Avoid vague descriptions ("helps with X")
- ☐ Optional fields (`license`, `compatibility`, `metadata`) only when they add real value
- ☐ If used, `triggers` follows the v1 schema (`intent`, `user_phrases`, `file_context`, `tool_context`, `error_context`, `priority`, `suggest_only`)
- ☐ Keep `suggest_only: true` for v1 trigger metadata
- ☐ Unknown frontmatter keys are ignored by OpenCode (don’t rely on them)

### 4) Structure for Progressive Disclosure

- ☐ Keep `SKILL.md` concise (Anthropic guidance: under ~5,000 tokens / ~500 lines)
- ☐ Put advanced details in reference files (loaded only when needed)
- ☐ Keep references one level deep (avoid `SKILL.md → A → B` chains)
- ☐ For complex domains, prefer a consistent multi-file layout (adapt as needed):
  - ☐ `README.md` (overview + when to use)
  - ☐ `configuration.md` (setup/config)
  - ☐ `api.md` (runtime API/reference)
  - ☐ `patterns.md` (workflows/best practices)
  - ☐ `gotchas.md` (tribal knowledge, pitfalls, limits)

### 5) Gotchas and Guardrails

- ☐ Include a `gotchas` section/file for non-obvious limits, common errors, and "things that bite"
- ☐ Pick a default approach/tool; mention alternatives only when they’re clearly distinct
- ☐ Don’t over-explain basics the model already knows; show concise, actionable examples

### 6) Scripts (If Included)

- ☐ Scripts handle errors gracefully (don’t just crash)
- ☐ No unexplained magic numbers; document why values exist
- ☐ Document dependencies and runtime requirements (`compatibility` + instructions)

### 7) Portability and Paths

- ☐ Use forward slashes in paths inside docs (even on Windows)
- ☐ Avoid platform-specific assumptions unless `compatibility` explicitly states them

### 8) Permissions and Safety (OpenCode)

- ☐ If the skill is sensitive (prod access, secrets, destructive operations), plan permission rules in `opencode.json`
- ☐ Use `permission.skill` patterns (`allow`/`deny`/`ask`) and wildcards (`internal-*`, `experimental-*`)
- ☐ Consider per-agent overrides when only some agents should access the skill

### 9) Testing (confirmed skills)

- [check] Test that the description reliably triggers activation.
- [check] Test at least one real task end-to-end via the Step 10 harness + sub-agent smoke test.
- [check] Validate script syntax for all included scripts.
- [check] Run at least one safe script functional test when scripts are included.
- [check] For critical skills, define an evaluation prompt plus expected behaviors and iterate.
- [check] If behavior is off, refine the description first; it controls activation.
- [check] If `triggers` exists, test at least two `user_phrases` against realistic user asks.
- [check] A skill is CONFIRMED only when both structural (Step 9) and functional (Step 10) checks pass.
### 10) Troubleshooting Quick Checks

- ☐ `SKILL.md` is all caps
- ☐ Frontmatter is valid YAML (no tabs, correct indentation)
- ☐ Skill name is unique across all locations
- ☐ Permissions aren’t hiding the skill (`deny`)
- ☐ File paths in references exist and are relative/valid

## Troubleshooting

**Skill doesn't activate**:
- Make description more specific with trigger words
- Include file types and operations in description
- Add "Use when..." clause with user phrases

**Multiple Skills conflict**:
- Make descriptions more distinct
- Use different trigger words
- Narrow the scope of each Skill

**Skill has errors**:
- Check YAML syntax (no tabs, proper indentation)
- Verify file paths (use appropriate separators)
- Ensure scripts have execute permissions
- List all dependencies

**Skill not discovered**:
- Verify SKILL.md is spelled in all caps
- Check directory name matches frontmatter `name`
- Ensure skill names are unique across all locations
- Check permissions in `opencode.json` (skills with `deny` are hidden)

## Configuration and permissions

OpenCode supports pattern-based permissions in `opencode.json`:

```json
{
  "permission": {
    "skill": {
      "pr-review": "allow",
      "internal-*": "deny",
      "experimental-*": "ask",
      "*": "allow"
    }
  }
}
```

**Permission levels**:
- `allow`: Skill loads immediately
- `deny`: Skill hidden from agent, access rejected
- `ask`: User prompted for approval before loading

**Per-agent overrides** (in `opencode.json`):

```json
{
  "agent": {
    "explore": {
      "permission": {
        "skill": {
          "internal-*": "allow"
        }
      }
    }
  }
}
```

**Disable skill tool for specific agents**:

```json
{
  "agent": {
    "explore": {
      "tools": {
        "skill": false
      }
    }
  }
}
```

## Output format

When creating a Skill, I will:

1. Ask clarifying questions about scope and requirements
2. Suggest a Skill name and location
3. Create the SKILL.md file with proper frontmatter
4. Include clear instructions and examples
5. Add supporting files if needed
6. Provide testing instructions
7. Validate against all requirements

The result will be a complete, working Skill that follows all best practices and validation rules.

## Reference

For detailed OpenCode skills documentation, see [reference.md](reference.md).
