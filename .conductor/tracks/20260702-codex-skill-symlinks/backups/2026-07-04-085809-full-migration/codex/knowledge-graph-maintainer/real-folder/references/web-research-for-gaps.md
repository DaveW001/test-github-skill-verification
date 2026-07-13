# Web Research for Gaps

This document defines when and how to use web research to fill knowledge gaps in the
graph. Web research is a controlled, citation-required activity, not a default behavior.

## When Web Research Is Allowed

Web research may be used to fill gaps when ALL of the following conditions are met:

1. The gap involves **public, non-sensitive information** (e.g., program definitions,
   technology descriptions, public organizational structures).
2. The information is **not available in internal sources** (email, Slack, OneDrive,
   meeting notes).
3. The gap was identified through the normal maintenance lifecycle (gap detection,
   contradiction resolution, or synthesis).
4. The maintainer has **specific questions** to answer, not a broad exploration task.

Acceptable web research targets:
- Public program descriptions from official government websites.
- Technology definitions and standards documentation.
- Public organizational charts and leadership information.
- Published strategy documents and policy papers.
- Conference proceedings and public briefings.

## When to Avoid Web Research

Web research must **not** be used for:

1. **Private mailbox or calendar content.** Email threads, meeting invitations, and
   calendar events are internal sources. Ask the user or search internal documents instead.
2. **Internal-only facts.** Personnel assignments, internal reorganizations, non-public
   budget figures, and draft proposals that are not published.
3. **Classified or sensitive information.** Any information with distribution restrictions.
4. **Ambiguous identity resolution.** If two entities might be the same person or org,
   web research can provide supporting evidence but cannot be the sole basis for a merge.
   The user must confirm.
5. **Broad exploratory research.** Do not use web search to "see what's out there."
   Each research action must target a specific knowledge gap.

## Citation Requirements

All facts added to the knowledge graph from web research must include:

1. **Source URL** - the specific page where the information was found.
2. **Access date** - when the information was retrieved (web content changes).
3. **Source credibility assessment** - official government site, industry publication,
   news article, or personal blog.
4. **Confidence level** - `high` for official sources, `medium` for reputable publications,
   `low` for unverified or informal sources.

Citation format in entity frontmatter:
```yaml
sources:
  - "[[source-web-YYYY-MM-DD-short-description]]"
```

Citation format in entity body:
```markdown
According to [official source](https://example.gov/page), accessed 2026-05-10.
```

## Public vs Internal Facts

| Fact Type | Web Research | Internal Source | User Approval Required |
|-----------|-------------|----------------|----------------------|
| Program definition (public) | Yes | N/A | No (with citation) |
| Program budget (public) | Yes, if published | If available | Yes |
| Program budget (internal) | No | Yes | Yes |
| Personnel assignment (public) | Yes, if officially published | If available | Yes |
| Personnel assignment (internal) | No | Yes | Yes |
| Technology definition | Yes | N/A | No (with citation) |
| Organizational restructuring | Only if publicly announced | If available | Yes |
| Risk assessment | No | Yes | Yes |
| Decision rationale | No | Yes | Yes |

Key rule: **If the information could be sensitive, internal, or non-public, do not use
web research. Ask the user or find an internal source instead.**

## Error Recovery

- If web research returns conflicting information, do not pick a side. Record all
  findings and add to the review queue.
- If the source URL is a paywalled or gated resource, note this in the citation and
  flag for the user to verify.
- If web research returns no useful results, note the search queries used and move on.
  Do not retry with minor query variations; this is a sign that the information may not
  be publicly available.
- If the web search tool is unavailable or returns errors, skip the research step and
  add the gap to the review queue with a note that web research was attempted but failed.
