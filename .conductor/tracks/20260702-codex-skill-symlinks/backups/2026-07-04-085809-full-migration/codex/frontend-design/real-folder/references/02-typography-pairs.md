# Typography Pair Defaults

Avoid default/system stacks unless a project already mandates them.

Pick one pairing, then commit:

## Pair A (Editorial)

- Display: Fraunces
- Body: IBM Plex Sans

## Pair B (Confident / Industrial)

- Display: Bebas Neue
- Body: Source Sans 3

## Pair C (Refined)

- Display: DM Serif Display
- Body: Work Sans

## Next.js (example)

If using Next.js, prefer `next/font/google`:

```ts
import { Fraunces, IBM_Plex_Sans } from "next/font/google";

export const display = Fraunces({ subsets: ["latin"], variable: "--font-display" });
export const body = IBM_Plex_Sans({ subsets: ["latin"], weight: ["400", "600"], variable: "--font-body" });
```

Then apply:

```css
:root {
  font-family: var(--font-body), sans-serif;
}

h1, h2, h3 {
  font-family: var(--font-display), serif;
}
```

If the project already has typography rules, follow them.
