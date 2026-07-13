# How to Use the Content Trend Researcher Skill

This guide shows you exactly how to invoke the `content-trend-researcher` skill for various content research scenarios.

## CRITICAL: File Location Confirmation

**Step 1: Ask BEFORE starting research**

Before you invoke the task tool, you MUST:

1. Ask the user where to save the trend report file
2. Make a suggestion based on the working directory (typically `topics/`)
3. Show the suggested filename with "trend-info" and today's date
4. Show the full path to the suggested file
5. Allow the user to accept or provide a different location

### Example Interaction

```
You: "I'll research [topic]. Where should I save the trend report file?

Suggested location: topics/[topic-slug]-trend-info-2026-01-01.md

Full path: C:\development\content-marketing\topics\[topic-slug]-trend-info-2026-01-01.md

Accept this location, or provide a different path?"

User: "Accept"
OR
User: "Use research/[custom-name].md"
```

### File Naming Convention

**Required format**: `{topic-slug}-trend-info-{YYYY-MM-DD}.md`

**Examples**:
- `agile-transformation-challenges-trend-info-2026-01-01.md`
- `devsecops-continuous-ato-trend-info-2026-01-01.md`
- `federal-cloud-procurement-trend-info-2026-01-01.md`

**Topic slug rules**:
- Convert topic to lowercase
- Replace spaces with hyphens
- Remove special characters
- Keep concise (3-6 words max)
- Add `-trend-info-{date}` suffix

## Step 2: Invoke Research

After user confirms the file location, invoke the task tool with `subagent_type="general"` and your research request.

## Step 3: Save Report with Full Path Header

After receiving the research report, save it to the confirmed location.

**CRITICAL**: The file header MUST include the full path:

```markdown
# [Topic] Trend Research Report

**Full Path**: C:\development\content-marketing\topics\[actual-filename].md
**Date**: 2026-01-01
**Research Date**: 2026-01-01
**Topic**: [Topic name]

---

[Research content...]
```

## Complete Workflow Example

### Step 1: Confirm File Location

```
You: "I'll research agile transformation challenges in government. Where should I save the trend report file?

Suggested location: topics/agile-transformation-challenges-trend-info-2026-01-01.md

Full path: C:\development\content-marketing\topics\agile-transformation-challenges-trend-info-2026-01-01.md

Accept this location, or provide a different path?"
```

### Step 2: User Responds

```
User: "Accept"
```

### Step 3: Conduct Research

Invoke task tool with research prompt.

### Step 4: Save Report

```markdown
# Agile Transformation Challenges Trend Research Report

**Full Path**: C:\development\content-marketing\topics\agile-transformation-challenges-trend-info-2026-01-01.md
**Date**: 2026-01-01
**Research Date**: 2026-01-01
**Topic**: Agile transformation challenges in government organizations

---

[Full research report...]
```

### Step 5: Confirm to User

```
You: "Report saved to C:\development\content-marketing\topics\agile-transformation-challenges-trend-info-2026-01-01.md"
```

## Research Request Examples

### Basic Topic Research

```
Research: AI automation for small businesses
Platforms: Google Trends, Reddit, LinkedIn, YouTube
```

**Suggested file**: `topics/ai-automation-small-business-trend-info-2026-01-01.md`

### Deep Platform Analysis

```
Research: Remote work productivity tools
Platforms: ALL
Include: User intent breakdown, content gap analysis, 3 article outlines
Target audience: SaaS founders and product managers
Analysis depth: deep
```

**Suggested file**: `topics/remote-work-productivity-trend-info-2026-01-01.md`

### Government/Federal IT Research

```
Research current trends, discussions, and evolving perspectives on Agile transformation challenges in large government organizations.

Focus on:
1. Cultural resistance to Agile/SAFe adoption
2. Procurement and contracting reform
3. Budget process modernization
4. DevSecOps and continuous ATO
5. Metrics that matter vs. vanity metrics
6. Lightweight Agile vs. heavy frameworks

Target platforms: Federal IT blogs, GovLoop, FedScoop, Defense Innovation Board, GAO reports, LinkedIn government tech groups

Include for each area:
- Current trend summary
- Key thought leaders and sources
- Recent developments (2024-2026)
- Debates and evolving perspectives
- Content gaps and opportunities
- Top 3-5 sources with URLs

Output: Data-driven article outline ideas
```

**Suggested file**: `topics/agile-transformation-challenges-trend-info-2026-01-01.md`

## Expected Output Structure

Each research report includes:

### Required File Header
```markdown
# [Topic] Trend Research Report

**Full Path**: [Actual file path]
**Date**: [YYYY-MM-DD]
**Research Date**: [YYYY-MM-DD]
**Topic**: [Topic name]

---

```

### Research Content

For each focus area:
- Current trend summary
- Key thought leaders and sources
- Recent developments (2024-2026)
- Debates and evolving perspectives
- Content gaps and opportunities
- Top 3-5 sources with URLs

Overall sections:
- Data-driven article outline ideas (3+ concepts)
- Content angle recommendations
- Platform-specific strategies
- Key insights and strategic recommendations

## Troubleshooting

### Issue: User didn't confirm file location
**Solution**: Always ask before starting research. Don't assume the location.

### Issue: User wants different filename
**Solution**: Accept their preference, but suggest the standardized format for consistency.

### Issue: Full path missing from header
**Solution**: Always include the full path in the file header. This is mandatory.

### Issue: Generic or broad research
**Solution**: Be more specific with topic and target audience in your research request.

### Issue: Missing sources/URLs
**Solution**: Explicitly request "top 3-5 sources with URLs for each area"

### Issue: No content gap analysis
**Solution**: Add "include content gaps and opportunities" to your research request

## Tips for Best Results

1. **Always ask before research starts** - Confirm file location with user
2. **Use suggested location** - Default to `topics/` unless user specifies otherwise
3. **Follow naming convention** - `{topic-slug}-trend-info-{YYYY-MM-DD}.md`
4. **Include full path in header** - Essential for file management
5. **Be specific with topics** - "Email marketing automation" beats "marketing"
6. **Choose relevant platforms** - Where your audience actually consumes content

## Quick Reference

**Before Research**:
- Ask user for file location
- Suggest `topics/[topic-slug]-trend-info-{date}.md`
- Show full path
- Wait for confirmation

**During Research**:
- Invoke task tool with subagent_type="general"
- Provide detailed research prompt

**After Research**:
- Save to confirmed location
- Include full path in file header
- Confirm to user: "Report saved to [full path]"

---

**Version**: 2.0.0
**Last Updated**: January 2026
