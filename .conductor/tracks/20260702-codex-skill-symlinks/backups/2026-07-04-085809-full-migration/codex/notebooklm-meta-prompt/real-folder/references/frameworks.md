# The 5 Analytical Frameworks — Deep Dive

Each framework targets a distinct analytical vector. Together they create a comprehensive red-team of your thinking.

---

## 1. THE SHADOW AUDIT

**One-line purpose**: Exposes what the material omits, ignores, or inadvertently masks.

### What It Does

The Shadow Audit doesn't analyze what's in your material — it maps what's **absent**. Every document, every set of notes, every strategic plan has a shadow: the set of factors, perspectives, and data points that are conspicuously missing from the frame.

This framework treats omissions as active signals, not passive gaps. The question isn't "what did they forget?" but "what is the structure of this material actively preventing the reader from seeing?"

### Why Standard Analysis Fails

Standard analysis reads what's on the page. It can comment on quality, logic, and consistency of what's present. But it has no mechanism for identifying what's systematically excluded from consideration. The absence of something is invisible to analysis that only looks at presence.

### When to Use

- Strategic documents that feel complete but might be missing critical perspectives
- Research that seems thorough but may have blind spots in methodology
- Brain-dumps that circle around a topic without naming the elephant in the room
- Any material where "what's not being said" is more important than what is

### Expected Output

A structured inventory of:
- Topics/concepts that are implicitly excluded from the frame
- Perspectives that would be natural to include but are absent
- Data types or evidence categories that the material never considers
- Assumptions that the material makes by omission (i.e., assumes as settled what isn't)
- Second-order effects of these omissions on the material's conclusions

### Value Profile
**[Best for Reframing]** — Changes how you see the entire landscape by revealing what was outside your frame.

### Typical Blind Spots of This Framework

- May identify omissions that are intentional and strategic (not every gap is a blind spot)
- Can over-generate "missing perspectives" that aren't actually relevant
- Works best when the material has enough structure to make absences detectable; very chaotic material may not have clear enough boundaries to identify shadows

---

## 2. THE INVERSION ENGINE

**One-line purpose**: Analyzes vulnerabilities — how the current state is guaranteed to fail.

### What It Does

The Inversion Engine applies Charlie Munger's inversion principle at scale: instead of asking "how do we succeed?", it asks "how would we guarantee failure?" — and then maps the specific mechanisms by which the current approach or material leads to that failure.

This isn't pessimism. It's engineering. By mapping failure modes precisely, you identify the exact points where intervention is needed and the specific assumptions that, if wrong, collapse the entire structure.

### Why Standard Analysis Fails

Standard analysis evaluates the probability of success. It asks "will this work?" and estimates odds. The Inversion Engine doesn't care about probability — it asks "under what conditions does this necessarily fail?" and maps those conditions back to the present material to see which are already present or likely.

### When to Use

- Plans, strategies, or roadmaps that need stress-testing
- Material that presents a confident narrative with clear logic chains
- Any situation where the cost of being wrong is high
- When confidence is high and critical thinking is needed most

### Expected Output

A failure-mode map including:
- The specific mechanism of guaranteed failure (not "it might not work" but "here's exactly how it breaks")
- Which elements of the current material create that vulnerability
- The earliest detectable signal that failure is approaching
- The single assumption that, if invalidated, collapses the most downstream logic
- A differentiating experiment that would reveal whether this failure mode is already active

### Value Profile
**[Best for Risk Detection]** — Surfaces specific, actionable failure mechanisms rather than generic risk categories.

### Typical Blind Spots of This Framework

- Can generate failure modes that are theoretically possible but practically unlikely
- May undervalue the material's existing risk mitigations
- Works best on structured, confident material; very tentative material already contains its own uncertainty
- The "guaranteed to fail" framing can feel overly aggressive — remember this is analytical posture, not prediction

---

## 3. THE SECOND-ORDER CATALYST

**One-line purpose**: Maps non-intuitive downstream effects 2-3 steps ahead.

### What It Does

Most analysis stops at first-order effects: "If we do X, then Y happens." The Second-Order Catalyst maps what happens after Y — the cascading effects that are invisible because they're not directly caused by the original action, but by the first-order effects of that action.

This is where the most consequential outcomes often live. First-order effects are usually anticipated. Second and third-order effects are where surprise lives — both positive and negative.

### Why Standard Analysis Fails

Standard analysis is locked into a linear causal model. It traces A→B and stops. But real systems are networks: A→B→C→D, with feedback loops, time delays, and interactions between causal chains. The Second-Order Catalyst forces the model to follow the chain further and map where non-obvious consequences emerge.

### When to Use

- Material involving decisions with broad or systemic impact
- Strategies that affect multiple stakeholders or systems
- Any situation where "and then what?" hasn't been asked enough times
- When the first-order effects seem obvious (that's exactly when second-order effects are most dangerous)

### Expected Output

A cascade map including:
- The first-order effects that are most likely to trigger significant downstream consequences
- 2nd and 3rd-order effects mapped explicitly with causal chains
- Feedback loops (where an effect circles back to amplify or dampen the original cause)
- Time delays that make second-order effects harder to detect
- The one downstream effect that would most fundamentally change the decision if anticipated

### Value Profile
**[Best for Fast Validation]** — Quickly reveals whether the obvious analysis is sufficient or dangerously incomplete.

### Typical Blind Spots of This Framework

- Cascade maps can become speculative if stretched too far (3rd-order effects are already pushing it)
- May generate dramatic-sounding chains that have very low actual probability
- Works best on material with clear causal structure; purely descriptive material may not have enough causal hooks
- The further you go from first-order, the more [H] tags you should expect

---

## 4. THE ASYMMETRIC LEVERAGE

**One-line purpose**: Hunts for small intervention points with disproportionate impact.

### What It Does

The Asymmetric Leverage framework searches for the "keystone" in your material: the single element, assumption, or variable that, if changed, would produce outsized effects on the rest of the system. It's looking for the 1% of effort that moves 50% of the outcome.

This framework explicitly rejects the idea that all variables are equally important. It treats the material as a system with leverage points — some obvious (and already being exploited) and some hidden (because they're small, counterintuitive, or assumed to be fixed).

### Why Standard Analysis Fails

Standard analysis treats all elements as roughly equivalent in importance. It evaluates each on its own merits and might rank them. But it doesn't systematically search for points where tiny changes create massive downstream effects — because those points often look unimportant at first glance.

### When to Use

- Resource-constrained situations where you need maximum impact from minimum effort
- Material that presents many options and you need to prioritize
- When the material seems to be treating everything as equally important (a sign that leverage points are being missed)
- After running the Shadow Audit or Inversion Engine (they reveal the landscape; this finds the leverage)

### Expected Output

A leverage analysis including:
- The 2-3 highest-leverage intervention points identified in the material
- Why each is asymmetric (what makes the input:output ratio unusual)
- What prevents this leverage from being obvious to a standard reader
- A specific, cheap experiment to test whether this leverage point is real
- The risk of exploiting the leverage point (high-leverage points often have high-leverage failure modes too)

### Value Profile
**[Best for Leverage]** — Directly targets decision impact and resource allocation efficiency.

### Typical Blind Spots of This Framework

- May identify leverage points that are theoretically high-impact but practically difficult to exploit
- Can undervalue boring, incremental improvements in favor of dramatic leverage points
- Works best when the material has enough specificity to identify concrete intervention points
- High-leverage points often have hidden dependencies — the framework may not fully map these

---

## 5. THE PARADIGM DESTROYER

**One-line purpose**: Hard red-team audit — how the smartest critic would dismantle this.

### What It Does

The Paradigm Destroyer is the most aggressive framework. It doesn't look for gaps, failures, cascades, or leverage — it challenges the **fundamental frame** of the material. It asks: "What if the core assumption this entire document is built on is wrong?"

This isn't about finding flaws in execution. It's about challenging the paradigm itself — the worldview, the model, the foundational assumption that makes everything else in the material make sense.

### Why Standard Analysis Fails

Standard analysis operates within the paradigm of the material. It accepts the frame and evaluates content within it. The Paradigm Destroyer refuses to accept the frame and instead asks what the smartest possible critic would say about the decision to use this frame at all.

### When to Use

- Material that feels "right" but you can't articulate why you might be wrong
- When everyone agrees on the approach (consensus is a red flag for paradigm blindness)
- Strategic decisions with long time horizons (where paradigm shifts are most costly)
- When you need to prepare for the strongest possible counterargument, not just the most obvious one

### Expected Output

A paradigm challenge including:
- The core assumption that the entire material rests on (usually unstated)
- The strongest possible argument for why that assumption is wrong
- What the material would look like if built on the opposite assumption
- The evidence that would distinguish between the two paradigms
- A specific experiment or observation that would stress-test the paradigm itself

### Value Profile
**[Best for Red Team]** — The most intellectually aggressive framework; designed to prevent paradigm trap.

### Typical Blind Spots of This Framework

- Can be intellectually thrilling but practically paralyzing (if you challenge every paradigm, you can't act)
- The "smartest critic" is a construct — real critics may not be this sophisticated
- Works best when the material has a clear, articulable core assumption; very diffuse material may not have a single paradigm to challenge
- This framework has the highest risk of generating [H] tags — paradigm challenges are inherently speculative

---

## Framework Interaction Guide

### Best 2-Prompt Sequences

| Sequence | First Prompt | Second Prompt | Why This Order |
|----------|-------------|---------------|----------------|
| **Reframing → Risk** | Shadow Audit | Inversion Engine | Shadow reveals what's missing; Inversion shows how those gaps create failure modes |
| **Risk → Leverage** | Inversion Engine | Asymmetric Leverage | Inversion maps failure; Leverage finds the intervention that prevents it |
| **Validation → Paradigm** | Second-Order Catalyst | Paradigm Destroyer | Second-order maps the cascade; Paradigm challenges whether the cascade model is even right |
| **Leverage → Shadow** | Asymmetric Leverage | Shadow Audit | Leverage finds intervention points; Shadow reveals what you're not seeing about those points |

### When to Use All 5

Use all 5 frameworks when:
- The decision is high-stakes and irreversible (or expensive to reverse)
- The material is complex enough to warrant comprehensive analysis
- You have time to process and integrate multiple analytical angles
- You're preparing for a critical presentation, debate, or decision meeting

### When to Use Just 1-2

Use 1-2 frameworks when:
- You need a quick gut-check on a specific angle
- Time is limited
- The material is simple enough that full coverage would be overkill
- You already know which analytical vector is most relevant
