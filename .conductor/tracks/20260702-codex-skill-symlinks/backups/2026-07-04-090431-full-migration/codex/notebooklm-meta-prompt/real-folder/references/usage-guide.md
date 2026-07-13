# NotebookLM Integration Guide

How to use the Meta-Prompt v5.1 with NotebookLM notebooks via OpenCode (nlm CLI/MCP) or Gemini /pro/.

---

## Method 1: OpenCode-Driven (nlm CLI or MCP)

Use this method when you want OpenCode to execute the entire meta-prompt protocol on your NotebookLM sources without leaving your workflow.

### Prerequisites

- `nlm` CLI installed and authenticated (`nlm login`)
- A NotebookLM notebook with sources already loaded
- This skill activated

### Step-by-Step Workflow

```
1. IDENTIFY THE NOTEBOOK
   nlm notebook list
   nlm notebook describe <notebook-id>    # Get AI summary of contents

2. EXTRACT SOURCE CONTENT
   nlm source list <notebook-id>          # See what sources are available
   nlm source content <source-id>         # Get raw text of each source

   OR for all content at once:
   nlm notebook query <notebook-id> "Provide a comprehensive summary of all source material including key claims, data points, arguments, assumptions, and conclusions"

3. RUN THE META-PROMPT PROTOCOL
   Provide the extracted material to OpenCode and say:
   "Run the meta-prompt protocol on this material"

   OpenCode will execute Steps 1-3 and produce:
   - Notebook Diagnosis
   - 5 Surgical Metaprompts
   - Usage Protocol with MVP, sequencing, and warnings

4. EXECUTE GENERATED PROMPTS BACK IN NOTEBOOKLM
   For each generated prompt, run:
   nlm notebook query <notebook-id> "<generated-prompt-text>"

   This queries the NotebookLM sources directly, grounding the analysis
   in the actual source material rather than the extracted summary.

5. ITERATE
   Review the outputs. If a prompt reveals something important:
   nlm notebook query <notebook-id> "Based on the previous analysis, drill deeper into [specific finding]"
```

### Batch Workflow (Multiple Notebooks)

```
1. CROSS-notebook query for initial context:
   nlm cross query "What are the key themes and tensions across all sources?" --tags "your-tag"

2. Run meta-prompt on the cross-notebook output

3. Use generated prompts across all notebooks:
   nlm batch query "<generated-prompt>" --tags "your-tag"
```

### Why Query NotebookLM Directly Instead of Using Extracted Text

Running the generated prompts back through `nlm notebook query` is superior to running them on extracted text because:
- **Grounding**: NotebookLM grounds responses in actual source documents with citations
- **Completeness**: Extraction may miss nuances; NotebookLM has the full source material
- **Anti-hallucination**: NotebookLM's grounding layer reduces fabrication risk
- **Citation**: Responses include source-level citations you can trace back

---

## Method 2: Gemini /pro/ Direct

Use this method when you want to run the meta-prompt directly in Gemini with NotebookLM notebook attached.

### Step-by-Step Workflow

```
1. GET THE PROMPT
   Say: "Give me the v5.1 meta-prompt"
   OpenCode provides the full copy-paste prompt from meta-prompt-v5.md

2. PREPARE YOUR MATERIAL
   Option A: Open NotebookLM (notebooklm.google.com), select your notebook
   Option B: Export source content:
     nlm source content <source-id> -o material.txt

3. RUN IN GEMINI
   - Open gemini.google.com (requires Pro subscription)
   - Paste the full v5.1 prompt
   - Attach your NotebookLM notebook or paste your exported material
   - Submit

4. REVIEW OUTPUT
   Gemini produces Steps 1-3:
   - Notebook Diagnosis
   - 5 Metaprompts (ready-to-copy in codeblocks)
   - Usage Protocol

5. RUN GENERATED PROMPTS
   Copy each generated prompt and run it:
   - Back in Gemini (same chat for context, or new chat for independence)
   - Through nlm notebook query for NotebookLM-grounded analysis
   - Or provide to OpenCode for further processing
```

---

## Method 3: Hybrid (Best Results)

Combine both methods for the most rigorous analysis.

```
1. INITIAL EXTRACTION (OpenCode + nlm)
   nlm notebook query <id> "Comprehensive synthesis of all source material"

2. META-PROMPT GENERATION (Gemini /pro/)
   - Paste v5.1 prompt in Gemini
   - Attach notebook + include extracted synthesis
   - Get 5 surgical metaprompts

3. GROUNDED EXECUTION (OpenCode + nlm)
   For each generated prompt:
   nlm notebook query <id> "<generated-prompt-text>"

   This grounds each analysis directly in source material

4. CROSS-VALIDATION
   nlm notebook query <id> "Compare and synthesize the findings from these five analytical perspectives: [summary of key findings]. Where do they agree? Where do they contradict? What does the convergence and divergence tell us?"
```

---

## Common Patterns

### Pattern 1: Strategy Document Review

```bash
# Load strategy documents into NotebookLM
nlm source add <id> --url "https://strategy-doc-1.com"
nlm source add <id> --text "internal notes..." --title "Strategy Notes"

# Get comprehensive extraction
nlm notebook query <id> "Extract all strategic claims, assumptions, dependencies, success metrics, and risk factors"

# Run meta-prompt protocol on the extraction
# → Get 5 prompts focused on strategic blind spots

# Execute top 2 prompts back through NotebookLM
nlm notebook query <id> "<shadow-audit-prompt>"
nlm notebook query <id> "<inversion-engine-prompt>"
```

### Pattern 2: Research Synthesis

```bash
# Research phase
nlm research start "topic" --notebook-id <id> --mode deep
nlm research status <id>
nlm research import <id> <task-id>

# Meta-prompt analysis
nlm notebook query <id> "Full synthesis of all research sources"
# Run meta-prompt protocol on the synthesis
# Execute generated prompts through NotebookLM for grounded analysis
```

### Pattern 3: Personal Knowledge Audit

```bash
# Load your notes/brain-dumps
nlm source add <id> --text "messy brain dump..." --title "Raw Notes"
nlm source add <id> --text "half-formed ideas..." --title "Draft Ideas"

# The meta-prompt works BEST on messy material
# Run full protocol — the chaos IS the signal
# Pay special attention to [M] (Missing) and [H] (Hypothesis) tags
```

### Pattern 4: Pre-Meeting Preparation

```bash
# Load meeting materials
nlm source add <id> --url "https://meeting-doc.com"
nlm source add <id> --text "agenda items..." --title "Agenda"

# Quick meta-prompt: just run the MVP prompt
# Fast version: Shadow Audit + Inversion Engine (2-prompt stack)
nlm notebook query <id> "<shadow-audit-from-meta-prompt>"
nlm notebook query <id> "<inversion-engine-from-meta-prompt>"

# You now enter the meeting knowing:
# - What the materials are NOT saying
# - How the plan will fail
# - What to ask about
```

---

## Choosing the Right Method

| Factor | Method 1 (OpenCode) | Method 2 (Gemini) | Method 3 (Hybrid) |
|--------|--------------------|--------------------|--------------------|
| **Speed** | Medium | Fast | Slowest |
| **Grounding** | High (nlm query) | Medium (attachment) | Highest |
| **Convenience** | Stay in workflow | Context switch | Multiple switches |
| **Depth** | Good | Best (Gemini Pro reasoning) | Best |
| **Automation** | Fully scriptable | Manual | Semi-automated |
| **Best for** | Repeated analysis | One-time deep dives | Critical decisions |

---

## Tips & Tricks

1. **Messy material > Clean material**: The meta-prompt is designed to find signal in noise. Don't pre-edit or clean up your notes before running it.

2. **Run on brain-dumps first**: The moment you see it map out your implicit assumptions and hand you a prompt that shatters them — it clicks.

3. **The MVP prompt is usually not the most interesting one**: It's the one with the highest decision leverage. Start there for practical impact.

4. **Stack 2 prompts, not 5**: The combinatorics section of Step 3 tells you the best 2-prompt sequence. Running all 5 is overkill for most situations.

5. **[M] tags are gold**: Missing variables are where the real insight lives. Every [M] tag is a question you didn't know to ask.

6. **[H] tags demand testing**: Don't treat hypotheses as insights. Treat them as prompts for experiments.

7. **Use nlm notebook query for grounding**: Running generated prompts through `nlm notebook query` grounds the analysis in actual source material with citations. This is superior to running prompts on extracted text alone.

8. **Session management**: NotebookLM auth expires in ~20 minutes. If `nlm notebook query` starts failing, run `nlm login` and retry.

9. **Combine with cross-notebook query**: Use `nlm cross query` to run meta-prompt analyses across multiple notebooks simultaneously — powerful for comparative analysis.

10. **The Warning section matters**: Step 3 includes a "Warning" about where you're most likely to overvalue insight and undervalue missing variables. Read it carefully. It's the meta-prompt's way of telling you its own blind spots.
