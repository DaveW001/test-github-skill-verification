# Army Claims Register

## Legend
- **Fact** = directly supported by notebook/source evidence
- **Inference** = synthesized from multiple claims
- **Hypothesis** = plausible but needs more confirmation
- **Missing** = important unknown or unresolved variable

## Core claims

### 1) The Army is moving from program-centric acquisition to capability portfolio management.
- **Type:** Fact / Inference
- **Evidence:** WAS / PAE sources, portfolio transition notes, interview synthesis
- **Core claim:** The C2/CC2 effort is framed as a shift from isolated programs to integrated capability portfolios.
- **Why it matters:** This is the fundamental Packaged Agile positioning story.
- **Sensitivity:** Low/Medium
- **Reuse:** High

### 2) OpCon is being intentionally hardened while AdCon remains a fixed constraint.
- **Type:** Fact
- **Evidence:** Op model notes, governance outputs, daily sync notes
- **Core claim:** The operating model explicitly leaves Administrative Control with legacy commands and consolidates Operational Control inside the PAE box.
- **Why it matters:** This is the primary structural pattern to reuse for matrixed clients.
- **Sensitivity:** Medium
- **Reuse:** High

### 3) The PAE has strong strategic intent but limited formal authority.
- **Type:** Fact / Inference
- **Evidence:** Acquisition authorities, governance outputs, interviews
- **Core claim:** AAE retains MDA/DA; PAEs are expected to execute portfolio leadership without full acquisition authority.
- **Why it matters:** Requires a governance design that works despite authority boundaries.
- **Sensitivity:** High
- **Reuse:** Medium/High

### 4) Dual-hatted staffing and matrixed reporting are major execution risks.
- **Type:** Fact
- **Evidence:** Interview outputs, source index, workshop notes
- **Core claim:** Many staff hold multiple roles, receive conflicting directives, and struggle with context switching and ownership clarity.
- **Why it matters:** Velocity and accountability degrade fast in this setup.
- **Sensitivity:** High
- **Reuse:** High

### 5) The culture is permission-based and risk-averse.
- **Type:** Fact
- **Evidence:** Blockers query, workshop synthesis, interviews
- **Core claim:** People often wait for explicit permission before acting and fear blowback for surfacing problems.
- **Why it matters:** Agile transparency and autonomous delivery will fail without protection and air cover.
- **Sensitivity:** High
- **Reuse:** High

### 6) Manual CPR/reporting cycles create massive non-value-added drag.
- **Type:** Fact
- **Evidence:** CPR notes, operational friction, metrics outputs
- **Core claim:** Staff can spend months preparing for a one-hour review, driven by manual reporting and disconnected data systems.
- **Why it matters:** This is a high-leverage target for automation and flow metrics.
- **Sensitivity:** Medium
- **Reuse:** High

### 7) Flow metrics and telemetry are the preferred measurement direction.
- **Type:** Fact / Inference
- **Evidence:** Metrics TOR, product-to-project material, command center language
- **Core claim:** Success should be measured through flow time, efficiency, velocity, load, mission impact, and delivery speed rather than static milestone compliance.
- **Why it matters:** Gives Packaged Agile a measurement narrative that matches the Army context.
- **Sensitivity:** Medium
- **Reuse:** High

### 8) Funding rigidity is one of the biggest blockers to portfolio agility.
- **Type:** Fact
- **Evidence:** Interview outputs, portfolio transition, workshop synthesis
- **Core claim:** Legacy budgets, POM timing, and budget line rigidity make it hard to move money between priorities quickly.
- **Why it matters:** Agile portfolio management is constrained unless trade-space governance is real.
- **Sensitivity:** High
- **Reuse:** High

### 9) Leadership wants speed, but not abstract process theater.
- **Type:** Fact / Inference
- **Evidence:** Welch reactions, workshop notes, agile practices query
- **Core claim:** Senior leaders dislike abstract sticky-note consulting and prefer concrete, tactical, scenario-based decision support.
- **Why it matters:** Packaged Agile engagements should use tabletop scenarios and executable experiments.
- **Sensitivity:** Medium
- **Reuse:** High

### 10) The workforce needs a clearer North Star and priority cascade.
- **Type:** Fact
- **Evidence:** interview themes, metrics query, stakeholder notes
- **Core claim:** Staff repeatedly ask for a clear 1-to-n priority list and better guidance on what matters now.
- **Why it matters:** Priority clarity is a prerequisite for self-organization.
- **Sensitivity:** Medium
- **Reuse:** High

### 11) Some interviewees see dual reporting as manageable or even intentional.
- **Type:** Fact / Contradiction
- **Evidence:** interview contradictions output
- **Core claim:** Not everyone views the matrix as broken; some leaders believe the two-authority structure is working as intended.
- **Why it matters:** We must not oversimplify the situation as universally dysfunctional.
- **Sensitivity:** High
- **Reuse:** Medium

### 12) Several high-risk items should not enter a general KB.
- **Type:** Fact
- **Evidence:** sensitive claims query
- **Core claim:** Security/PII, CUI/FEDCON, facility access, real-world operations, and specific classified program details must be excluded or anonymized.
- **Why it matters:** Protects the Packaged Agile KB from accidental spillage.
- **Sensitivity:** Exclude
- **Reuse:** None

## Open questions / missing variables
- Which claims are safe for customer-facing use vs internal-only?
- What exact delegations of authority are formally documented for the current PAE structure?
- Which ad hoc processes can be replaced by automation without violating policy?
- Which proposed experiments have already been tried and with what result?
- What evidence exists for actual outcome improvement, not just better process language?
