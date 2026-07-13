---
name: frontend-design
description: Create production-grade frontend interfaces with high design quality.
compatibility: Web UI (HTML/CSS/JS) and React/Next.js; prefers Tailwind when available; if project has an existing design system, preserve it
license: Complete terms in LICENSE.txt
metadata:
  category: ui-design
---

# Frontend Design

Create distinctive, production-grade frontend interfaces that avoid generic "AI" aesthetics. Implement real working code with deliberate, context-specific design choices.

## Decision Tree

Need frontend design?

- Build new page/component -> output working code + layout + styling
- Restyle existing UI -> ask for target file(s) or screenshot + constraints, then propose edits
- Fix layout/spacing/typography -> tighten type scale + rhythm + grid and reduce visual noise
- Add motion/interaction -> add 1-2 meaningful animations (page load + hover), not scattered micro-motion
- Make it accessible -> semantics + focus states + contrast + reduced-motion

## Design Thinking (Before Coding)

- Purpose: what problem does the interface solve and who uses it?
- Tone: pick a clear direction (brutally minimal, editorial, brutalist, luxury, playful, industrial, etc.). Commit.
- Constraints: framework, performance, accessibility, existing design system.
- Differentiation: choose one unforgettable signature detail (typography, layout move, background texture, interaction).

## Defaults (Use Unless The Project Already Has Standards)

- Typography: pick a distinctive pairing and stick to it.
  - See `references/02-typography-pairs.md`
- Color: define CSS variables for bg/surface/text/accent.
  - See `references/01-css-variables.md`
- Motion: one strong page-load moment + one consistent hover pattern.
  - See `references/03-motion-scaffold.md`
- Accessibility: ship with focus states, semantics, contrast, reduced motion.
  - See `references/04-accessibility-basics.md`

## Hard Anti-Patterns

- Avoid overused defaults (Inter/Roboto/system-only stacks) unless required by the project.
- Avoid cliche palettes (especially generic purple-on-white gradients).
- Avoid cookie-cutter layouts and component patterns.
- Avoid sprinkling random micro-interactions; orchestrate a small set of meaningful motions.

## Activation Examples (Expected Behavior)

- "polish this UI" -> ask for existing component/page or screenshot; propose edits that improve type, spacing, hierarchy, and color system
- "design a landing page" -> pick a bold aesthetic direction; produce a responsive page with cohesive typography, atmosphere, and CTAs
- "make this hero section better" -> improve type scale, spacing rhythm, background treatment, and CTA styling
- "add animations" -> implement staggered page load + hover lift pattern; respect reduced-motion
- "make this accessible" -> correct semantics, add focus states, check contrast, label forms
