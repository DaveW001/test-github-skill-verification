# Accessibility Basics

Minimum expectations for any UI output.

## Semantics

- Use correct landmarks: `header`, `nav`, `main`, `footer`.
- Use a single `h1`, then descend `h2` -> `h3`.

## Keyboard + Focus

- All interactive elements must be reachable via keyboard.
- Visible focus states (do not rely on default outline removal).

Example focus ring:

```css
:focus-visible {
  outline: 3px solid color-mix(in oklab, var(--accent), white 25%);
  outline-offset: 3px;
}
```

## Contrast

- Ensure readable contrast (aim for WCAG AA).
- Avoid gray-on-gray text.

## Motion

- Respect `prefers-reduced-motion`.

## Forms

- Labels connected via `for` / `id`.
- Error messages should be announced (`role="alert"` when appropriate).
