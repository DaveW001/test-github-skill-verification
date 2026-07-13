---
name: webapp-testing
description: Toolkit for testing local web applications using Python Playwright. Use when the user asks to test a web app, click through UI flows, capture screenshots, debug UI behavior, or inspect browser console logs.
triggers:
  intent:
    - ui testing
    - browser automation
    - frontend ui validation
  user_phrases:
    - test this web app
    - click through the flow
    - capture screenshots
  file_context:
    extensions: [html, ts, tsx, js, jsx, css]
    paths: [src/**, app/**, public/**]
  tool_context:
    before_tools: [bash, read]
    with_tools: [bash]
  error_context:
    - ui bug reproduction
    - browser console issue
  priority: medium
  suggest_only: true
compatibility: Python 3.10+; Playwright (python) installed; browsers installed via `python -m playwright install`; local web server reachable
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

Helper scripts available (treat as black boxes):
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

Always run helper scripts with `--help` first to learn usage. Do not read script source unless a customized solution is truly necessary.

## Preflight (Before Writing Automation)

- Confirm Playwright is installed:
  - `python -c "import playwright; print('playwright ok')"`
- Confirm browsers are installed (run once per machine):
  - `python -m playwright install`
- Confirm target URL/port (example: `http://localhost:5173`) and that the server is reachable.

## Decision Tree: Choosing Your Approach

```
User task -> Is it static HTML?
  |- Yes -> Read HTML file directly to identify selectors
  |         |- Success -> Write Playwright script using selectors
  |         '- Fails/incomplete -> Treat as dynamic (below)
  |
  '- No (dynamic webapp) -> Is the server already running?
      |- No -> Run: python scripts/with_server.py --help
      |        Then use the helper + write simplified Playwright script
      |
      '- Yes -> Reconnaissance-then-action:
           1. Navigate and wait for networkidle
           2. Take screenshot or inspect DOM
           3. Identify selectors from rendered state
           4. Execute actions with discovered selectors
```

## Example: Using with_server.py

Start a server (run `--help` first), then run your Playwright automation.

Single server:

```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

Multiple servers (e.g., backend + frontend):

```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

Your automation script should contain only Playwright logic (servers are managed by the helper):

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Default to headless for speed and CI.
    # If debugging a flaky interaction, temporarily use headless=False.
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")  # Critical for JS-heavy apps

    # ... your automation logic

    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. Inspect rendered DOM (after `networkidle`):

```python
page.screenshot(path="/tmp/inspect.png", full_page=True)
html = page.content()
buttons = page.locator("button").all()
```

2. Identify selectors from inspection results.

3. Execute actions using discovered selectors.

## Gotchas

- Dynamic apps: do not inspect DOM before `page.wait_for_load_state("networkidle")`.
- Timeouts: if navigation/actions are slow, increase timeouts explicitly:
  - `page.set_default_timeout(60000)`
  - `page.set_default_navigation_timeout(60000)`
- Browser launch failures: run `python -m playwright install`.

## Best Practices

- Use bundled scripts as black boxes; prefer invoking them over re-implementing server management.
- Use `sync_playwright()` for simple, synchronous scripts.
- Always close the browser.
- Prefer robust selectors: `get_by_role`, `get_by_text`, `data-testid`, then CSS as needed.
- Add appropriate waits: `page.wait_for_selector()` or `expect(locator).to_be_visible()`.

## Activation Examples (Expected Behavior)

- "test this web app" -> pick approach via decision tree; use `with_server.py` if server not running; write Playwright script
- "take a screenshot of the settings page" -> navigate, wait `networkidle`, screenshot (full page if needed)
- "debug why this button doesn't click" -> inspect DOM + console logs; if needed, temporarily run headed (`headless=False`)
- "run a quick UI smoke test" -> minimal script: goto, wait, assert key selectors visible

## Reference Files

- `examples/`:
  - `element_discovery.py` - Discover buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation
