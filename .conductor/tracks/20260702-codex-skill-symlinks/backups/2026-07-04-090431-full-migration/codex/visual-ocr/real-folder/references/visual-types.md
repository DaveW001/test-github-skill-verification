# Supported Visual Types

## Type Detection

The `auto` prompt type lets the model detect visual structures. For known types, use `--prompt-type` for better results.

## Visual Types and Output Schemas

### 1. Org Charts
**Visual cues:** Boxes with names/roles connected by lines, hierarchical layout
**Output:** Nested markdown lists preserving hierarchy
**Key data:** Names, titles, reporting relationships, unit assignments

### 2. Timelines / Roadmaps
**Visual cues:** Horizontal/vertical bars, milestone markers, date labels, phase separators
**Output:** Chronological list with status indicators
**Key data:** Dates, milestone names, status (complete/in-progress/planned), dependencies

### 3. Portfolio Matrices
**Visual cues:** Grid with RAG colors, program names in rows, categories in columns
**Output:** Markdown table with status indicators
**Key data:** Program names, category assignments, RAG status, phase

### 4. Comparison Tables
**Visual cues:** Multi-column layout with spec rows, checkmarks, numeric values
**Output:** Markdown comparison table
**Key data:** Feature names, values per option, highlight indicators

### 5. Relationship Diagrams
**Visual cues:** Nodes with labeled edges, arrows, dotted/solid lines, grouped boxes
**Output:** Entity list + relationship list + groups
**Key data:** Entity names, connection types, group membership

### 6. Process Flows
**Visual cues:** Sequential boxes with arrows, decision diamonds, swim lanes
**Output:** Numbered step sequence with decision points
**Key data:** Step names, decision criteria, parallel paths, responsible parties
