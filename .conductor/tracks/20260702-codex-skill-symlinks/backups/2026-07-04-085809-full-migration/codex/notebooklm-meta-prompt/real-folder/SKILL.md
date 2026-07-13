---
name: notebooklm-meta-prompt
description: Extract deeper insights from NotebookLM sources using meta-prompt analysis and blind-spot detection.

version: "5.1"
---

# NotebookLM Meta-Prompt — Insight Extraction Engine

Generate surgical, high-leverage sub-prompts that expose non-obvious insights from your NotebookLM sources. This is NOT a summarization tool — it is a **thinking red-team** that maps blind spots, hidden tensions, and untapped leverage in your material.

## Decision Tree

```
User wants to...
│
├─► Get deeper insights from NotebookLM sources
│   └─► Run the Meta-Prompt Protocol (Step 1 → 2 → 3)
│       See: references/usage-guide.md
│
├─► Understand the 5 analytical frameworks
│   └─► See: references/frameworks.md
│       (Shadow Audit, Inversion Engine, Second-Order Catalyst,
│        Asymmetric Leverage, Paradigm Destroyer)
│
├─► Get the raw v5.1 prompt to paste into Gemini
│   └─► See: references/meta-prompt-v5.md
│       (Copy-paste ready for Gemini /pro/)
│
├─► Apply meta-prompt to specific material
│   └─► Gather material → Run Step 1 diagnosis → Generate prompts
│       Use: references/meta-prompt-v5.md (full protocol)
│
└─► Customize the meta-prompt for a specific domain
    └─► Modify frameworks in references/frameworks.md
        Adjust epistemic tags and evidence thresholds
```

## Quick Start

### Option A: Use in OpenCode (AI-Driven Analysis)

1. Provide your material (paste text, point to files, or reference a NotebookLM notebook)
2. Say: "Run the meta-prompt protocol on this material"
3. OpenCode executes Steps 1-3 and outputs 5 surgical sub-prompts

### Option B: Get the Copy-Paste Prompt for Gemini /pro/

1. Say: "Give me the v5.1 meta-prompt"
2. Copy the full prompt from `references/meta-prompt-v5.md`
3. Paste into Gemini /pro/, attach your NotebookLM notebook
4. Gemini executes the protocol directly

## Core Principles

These principles govern every output the meta-prompt produces:

1. **Truth > Originality**: Accuracy over flair. A precise, grounded prompt beats a bold, unverified one.
2. **Decision Delta**: Every prompt must drive output that alters at least one of: reality interpretation, prioritization, resource allocation, execution sequence, or confidence level.
3. **Anti-Overlap**: The 5 prompts must have materially distinct analytical vectors.
4. **Evidence Threshold**: No strong claims without ≥2 independent notebook signals, unless explicitly tagged `[H]` (Hypothesis).
5. **Density & Edge**: Maximum intellectual payload, minimum word count. Zero fluff.
6. **Anti-Hallucination**: Do not invent author intent. Implicit-layer claims require extra caution.

## Epistemic Tag System

Every output from generated prompts uses this mandatory framing:

| Tag | Meaning | Rules |
|-----|---------|-------|
| `[F]` | **Fact** from the notebook | Directly traceable to source material |
| `[I]` | **Inference** from multiple signals | Requires ≥2 converging signals |
| `[H]` | **Hypothesis** requiring testing | Explicitly flagged, not treated as fact |
| `[M]` | **Missing variable** | Critical unknown that would change analysis |

## The 5 Frameworks (Summary)

See **[references/frameworks.md](references/frameworks.md)** for full details.

| # | Framework | Purpose | Value Profile |
|---|-----------|---------|---------------|
| 1 | **Shadow Audit** | Exposes omissions, ignored factors, masked realities | [Best for Reframing] |
| 2 | **Inversion Engine** | Analyzes how current state is guaranteed to fail | [Best for Risk Detection] |
| 3 | **Second-Order Catalyst** | Maps non-intuitive downstream effects 2-3 steps ahead | [Best for Fast Validation] |
| 4 | **Asymmetric Leverage** | Hunts small intervention points with disproportionate impact | [Best for Leverage] |
| 5 | **Paradigm Destroyer** | Hard red-team: how the smartest critic would dismantle this | [Best for Red Team] |

## Execution Protocol (3 Steps)

### STEP 1: Notebook Diagnosis
Output first, before generating any prompts:
- **Material Type**: Strategy, research, operations, etc.
- **Explicit vs. Implicit Layers**: What's stated directly vs. assumed silently
- **Insight Potential**: Core tensions, anomalies, missing variables
- **Dominant Failure Mode**: How a smart but busy user misinterprets this
- **Analytical Risks**: Risks of superficial reading
- **Evidence Signals**: 2-5 specific notebook signals supporting the diagnosis

### STEP 2: Generate 5 Metaprompts
Each prompt includes:
- Name (short, punchy)
- Primary Analytical Question (1 sentence, proves anti-overlap)
- Why Standard Analysis Fails
- When to Use & Expected Output
- Ready-to-Copy Prompt (in codeblock, includes Role, objective, rules, [F/I/H/M] framework, differentiating experiment, and decision impact)
- Failure Risk / Blind Spots

### STEP 3: Usage Protocol
- **MVP Prompt**: The ONE prompt with highest expected decision leverage
- **Value Profile**: Label each prompt's dominant value
- **Combinatorics & Sequencing**: Which 2 prompts stack best, exact sequence
- **Warning**: Where the user is most likely to overvalue insight and undervalue missing variables

## Required Actionability

Every generated prompt MUST mandate:

1. **Differentiating Experiment**: At least one cheap, reversible test that discriminates between competing explanations and would change the next decision if the result goes either way.
2. **Decision Impact**: A dedicated section answering: "How does this insight alter a decision, priority, or resource allocation?"

## Fallback Mode

If the material is too chaotic, shallow, or incomplete for deep extraction:
- State this explicitly
- Pivot to designing prompts that first fix thinking structures, refine questions, or expose critical missing data

## Integration with NotebookLM Workflow

See **[references/usage-guide.md](references/usage-guide.md)** for end-to-end patterns combining this meta-prompt with `nlm` CLI or MCP tools.

## Gotchas / Guardrails

- **Do NOT use this for summarization** — the entire point is to go beyond summaries
- **The [H] tag is not optional** — if you can't find ≥2 signals, it's a hypothesis, not a fact
- **Fallback mode is not failure** — shallow material genuinely needs different treatment
- **Combinatorics matter** — running Prompt 1 before Prompt 2 changes what Prompt 2 reveals
- **The MVP prompt is usually NOT the most interesting one** — it's the one with highest decision leverage
- **Differentiating experiments must be cheap and reversible** — if the experiment costs more than the decision, redesign it

## Reference Files

- **[references/meta-prompt-v5.md](references/meta-prompt-v5.md)**: Full v5.1 meta-prompt, copy-paste ready for Gemini /pro/
- **[references/frameworks.md](references/frameworks.md)**: Deep dive into all 5 analytical frameworks with examples
- **[references/usage-guide.md](references/usage-guide.md)**: NotebookLM-specific usage patterns and integration guide
