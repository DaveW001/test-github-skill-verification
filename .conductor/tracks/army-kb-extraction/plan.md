# Plan

## Track Context

This track extracts reusable Army knowledge for the Packaged Agile knowledge base from two NotebookLM notebooks:

- `C2/CC2 Portfolio Engagement Kx` — ID `5125c1f1-71b3-4dbe-afc5-d725d1a4db2c`
- `Interview Notebook` — ID `a6341a1d-e4d2-4cd1-8cb9-5dfcb0c4cfac`

Default execution mode is **read-only**. Do not create NotebookLM Studio artifacts unless the user explicitly approves. This means avoid `nlm data-table create`, `nlm report create`, `nlm audio create`, `nlm slides create`, etc. Use `nlm source list`, `nlm cross query`, `nlm notebook query`, and targeted `nlm source content` exports.

Recommended output directory:

```powershell
C:\development\opencode\.conductor\tracks\army-kb-extraction\outputs
```

If the directory does not exist, create it before writing final Markdown outputs.

---

## Phase 0 - Execution Guardrails

- [x] Confirm `nlm` auth is active before starting:
- [x] If auth has expired, ask the user to run:
- [x] Confirm the two target notebooks are accessible:
- [x] Create output folder if needed:
- [x] Reconfirm with the user before running any non-read-only NotebookLM command.

---

## Phase 1 - Source Inventory and Source Classification

Purpose: understand what evidence exists before asking broad synthesis questions.

- [x] Export/list sources for the C2/CC2 notebook:
- [x] Export/list sources for the Interview notebook:
- [x] Create `outputs/army-source-index.md` with the following columns:
- [x] Classify each source into one or more categories:
- [x] Mark likely high-priority full-source candidates. 

---

## Phase 2 - Baseline Cross-Notebook Query Matrix

Purpose: extract structured baseline claims across both notebooks.

### Required query output format

Every query should ask NotebookLM to return:

- `Claim`
- `Evidence / source title(s)`
- `Direct quote or near-quote if available`
- `Confidence`: high / medium / low
- `Reusable Packaged Agile insight`
- `Sensitivity`: public-safe / internal-only / sensitive-review / exclude
- `Follow-up source pull needed?` yes / no, with reason

### Query 2.1 - Army / PAE Operating Context
- [x] Run operating context query

### Query 2.2 - Stakeholder and Key People Map
- [x] Run stakeholder map query

### Query 2.3 - Systemic Challenges and Blockers
- [x] Run systemic challenges query

### Query 2.4 - Decision Rights, Governance, and Authority
- [x] Run governance query

### Query 2.5 - Portfolio vs Program/Product Transition
- [x] Run portfolio transition query

### Query 2.6 - Culture, Incentives, and Change Resistance
- [x] Run culture and incentives query

### Query 2.7 - Agile/Scrum Adoption Challenges
- [x] Run Agile adoption query

### Query 2.8 - Metrics, Outcomes, and Value Evidence
- [x] Run metrics query

### Query 2.9 - Reusable Packaged Agile Patterns
- [x] Run reusable patterns query

### Query 2.10 - Risks, Sensitive Claims, and Verification Needs
- [x] Run sensitive claims query

- [x] Capture outputs from all ten baseline queries into `outputs/army-claims-register.md`, preserving query labels and source references.

---

## Phase 3 - Notebook-Specific Deepening Queries

Purpose: use each notebook for its strongest evidence type instead of treating both as interchangeable.

### 3A - C2/CC2 Portfolio Engagement Kx Deepening

- [x] Run operating model query
- [x] Run blocker/risk query
- [x] Run strategic language query

### 3B - Interview Notebook Deepening

- [x] Run interview themes query
- [x] Run contradictions query
- [x] Run stakeholder-specific needs query
- [x] Append all notebook-specific query outputs to `outputs/army-claims-register.md`.

---

## Phase 4 - Targeted Full Source Pulls

Purpose: pull raw source content only where needed for traceability, quote fidelity, or canonical definitions.

- [x] Create the source export folder:
- [x] Pull only selected high-value sources and record every pull in `army-source-index.md`.
- [x] After each pull, update any affected claim with better quote fidelity and confidence.

---

## Phase 5 - Meta-Prompt Deep Analysis

Purpose: use `notebooklm-meta-prompt` after the baseline claims register exists, so the red-team prompts are evidence-grounded rather than abstract.

### 5.1 Step 1 - Notebook Diagnosis
- [x] Produce diagnosis 

### 5.2 Step 2 - Generate 5 Meta-Prompts
- [x] Generate the five framework prompts

### 5.3 Step 3 - Execute Highest-Leverage Analysis
- [x] Execute at least these two analyses first:
- [x] If time/auth allows, execute others
- [x] Save results to `outputs/army-meta-prompt-insights.md`.

---

## Phase 6 - KB Asset Drafting

Purpose: convert evidence into reusable Packaged Agile knowledge assets.

- [x] Draft `outputs/army-context-overview.md`
- [x] Draft `outputs/army-stakeholder-map.md`
- [x] Draft `outputs/army-challenges-and-patterns.md`
- [x] Draft `outputs/army-pae-c2cc2-operating-model.md`
- [x] Draft `outputs/army-agile-adoption-lessons.md`
- [x] Ensure `outputs/army-claims-register.md` remains the source-of-truth for evidence and confidence.

---

## Phase 7 - Sensitivity, Quality, and Handoff Review

- [x] Review every output for sensitivity labels:
- [x] Move or remove any `exclude` content from KB-ready outputs.
- [x] Ensure public-safe claims do not include sensitive named-person details, facility/security/CAC details, or unsupported strategic claims.
- [x] Ensure every major claim has at least one source title and a confidence rating.
- [x] Add a `Known Gaps / Follow-up Questions` section to each output document.
- [x] Update this `plan.md` checkbox status and `metadata.json` phase/status before handing off.

---

## Optional Phase 8 - Artifact Creation Only If User Approves

Do not run this phase unless the user explicitly approves creating NotebookLM artifacts.

- [ ] Execute `nlm data-table create` if user approves (Skipped)

---

## Checkbox states

- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: `plan.md` is the authoritative source of truth for task progress.
