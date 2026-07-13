# CSS Variables Scaffold

Use a small variable set so the UI stays cohesive.

```css
:root {
  --bg: #0b0d12;
  --surface: #121725;
  --text: #f2f4f8;
  --muted: rgba(242, 244, 248, 0.72);

  --accent: #ff4d2e;
  --accent-2: #27d4ff;

  --border: rgba(242, 244, 248, 0.12);
  --shadow: 0 20px 80px rgba(0, 0, 0, 0.35);
  --radius: 18px;
}

@media (prefers-color-scheme: light) {
  :root {
    --bg: #fbfaf7;
    --surface: #ffffff;
    --text: #151515;
    --muted: rgba(21, 21, 21, 0.68);

    --accent: #ff4d2e;
    --accent-2: #1f5dff;

    --border: rgba(21, 21, 21, 0.10);
    --shadow: 0 18px 60px rgba(25, 25, 25, 0.12);
  }
}
```

Notes:
- Keep 1 primary accent and 1 secondary accent.
- Apply variables everywhere (backgrounds, borders, shadows) to avoid "random gray" drift.
