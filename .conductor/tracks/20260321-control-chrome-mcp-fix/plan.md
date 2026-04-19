# Plan

## Phase 1 - Investigation
- [x] Search for "control-chrome" in OpenCode configuration files
- [x] Check global and project-specific MCP configurations
- [x] Use `opencode mcp list` to see registered MCP servers
- [x] Use `opencode mcp debug control-chrome` to test connection
- [x] Research OpenCode documentation about MCP servers

## Phase 2 - Root Cause Analysis
- [x] Determine if "control-chrome" is a built-in MCP server
- [x] Check if it's defined in remote configuration or organization defaults
- [x] Examine OpenCode application logs for error details
- [x] Check if there's a way to reset or clear MCP server states

## Phase 3 - Solution Implementation
- [x] Based on findings, either:
  - Option A: Add proper configuration for "control-chrome" to enable it
  - Option B: Remove/disable the server if it's not needed
  - Option C: Clear the error state if it's a cached/stale entry
- [x] Move "control-chrome" MCP server from project-level config to global user-level config
  - [x] Add to global config: C:/Users/DaveWitkin/.config/opencode/opencode.jsonc
  - [x] Remove from project config: C:/development/marketing/opencode.jsonc
  - [x] Fix command format: Change from ["chrome-devtools-mcp"] to ["npx", "-y", "chrome-devtools-mcp@latest"]
- [x] Test the solution to ensure it resolves the red dot issue
  - [x] Verified `opencode mcp list` shows control-chrome as connected
  - [x] Confirmed command is correctly set to `npx -y chrome-devtools-mcp@latest`
- [x] Verify other MCP servers still function correctly
  - [x] Slack server: connected
  - [x] Playwright server: disabled (as expected)

## Phase 4 - Documentation
- [x] Document the root cause and solution
  - [x] Created detailed spec.md with requirements and acceptance criteria
  - [x] Created comprehensive plan.md with all phases and tasks
  - [x] Created metadata.json with root cause and solution summary
- [x] Update any relevant configuration files or documentation
  - [x] Updated global config: C:/Users/DaveWitkin/.config/opencode/opencode.jsonc
  - [x] Updated project config: C:/development/marketing/opencode.jsonc
- [x] Create a troubleshooting guide if needed
  - [x] Documented the issue and solution in conductor track
  - [x] Verified fix via `opencode mcp list` command

## Phase 5 - Real-World Test Cases
- [x] Documented 8 comprehensive test cases
- [x] Created executable test script: test_chrome_devtools_mcp.py
- [x] Test execution requires manual invocation via OpenCode chat (agents cannot directly invoke MCP tools)

**Note:** OpenCode agents cannot directly invoke MCP tools programmatically. The chrome-devtools-mcp tools are designed to be used during OpenCode chat interactions. To execute these tests, use the prompts provided below in your OpenCode chat.

Based on research of chrome-devtools-mcp capabilities and local project analysis (2025-pa-website, marketing), here are practical test cases to validate the MCP server functionality:

### Test Case 1: Performance Audit of 2025 PA Website [COMPLETED ✓]
**Scenario:** Test the website's performance using Chrome DevTools performance analysis
**Test Steps:**
1. Open a new page to the 2025 PA website (https://packagedagile.com or local dev server)
2. Run a performance trace using `performance_start_trace`
3. Stop the trace with `performance_stop_trace`
4. Analyze the trace using `performance_analyze_insight` to get actionable performance insights
5. Take a screenshot to document the current state

**Expected Outcome:** Performance trace records successfully, insights are generated, and screenshot captures the page

---

### Test Case 2: Visual Regression Testing - Homepage Screenshot
**Scenario:** Verify the homepage renders correctly across different viewports
**Test Steps:**
1. Navigate to the 2025 PA website homepage
2. Take a full-page screenshot with default viewport
3. Resize the page to mobile viewport (375x667)
4. Take another screenshot to verify mobile responsiveness
5. Take a DOM snapshot to verify page structure

**Expected Outcome:** Both screenshots capture the page correctly, DOM snapshot shows expected structure

---

### Test Case 3: Contact Form Testing
**Scenario:** Test interactive form elements on the contact page
**Test Steps:**
1. Navigate to the contact page
2. Take a snapshot to identify form fields
3. Fill form fields using `fill` or `fill_form` tool
4. Take a screenshot to verify form is filled correctly
5. List console messages to check for any JavaScript errors

**Expected Outcome:** Form fills successfully, no console errors, screenshot shows filled form

---

### Test Case 4: Network Request Monitoring
**Scenario:** Monitor network requests to verify API calls and resource loading
**Test Steps:**
1. Navigate to a page with dynamic content (e.g., blog page or homepage)
2. List network requests using `list_network_requests`
3. Examine specific requests using `get_network_request`
4. Check console messages for any errors
5. Take a screenshot of the final loaded state

**Expected Outcome:** Network requests are captured and can be inspected, no errors in console

---

### Test Case 5: JavaScript Execution and Debugging
**Scenario:** Execute JavaScript in the page context and verify results
**Test Steps:**
1. Navigate to the 2025 PA website
2. Use `evaluate_script` to execute custom JavaScript (e.g., check page title, count elements)
3. Get console messages to verify script execution
4. Take a screenshot to document the state

**Expected Outcome:** JavaScript executes successfully, results are returned, no errors

---

### Test Case 6: Page Navigation and Multi-Page Testing
**Scenario:** Test navigation across multiple pages
**Test Steps:**
1. Navigate to the homepage
2. List all pages using `list_pages`
3. Take a screenshot of the homepage
4. Navigate to the services page
5. Take a screenshot of the services page
6. Navigate to the about page
7. List console messages across pages
8. Take final screenshot

**Expected Outcome:** Successfully navigate between pages, screenshots capture each page

---

### Test Case 7: Lighthouse Audit
**Scenario:** Run a comprehensive Lighthouse audit on the website
**Test Steps:**
1. Navigate to the 2025 PA website homepage
2. Run `lighthouse_audit` to get performance, accessibility, SEO scores
3. Take a screenshot for visual reference
4. List network requests to understand resource loading

**Expected Outcome:** Lighthouse audit completes with scores for all categories

---

### Test Case 8: Memory Snapshot Analysis
**Scenario:** Check for memory leaks or issues
**Test Steps:**
1. Navigate to the 2025 PA website
2. Take a memory snapshot using `take_memory_snapshot`
3. Interact with the page (scroll, click elements)
4. Take another memory snapshot
5. Compare the two snapshots for memory usage patterns

**Expected Outcome:** Memory snapshots are captured successfully

---

### Implementation Notes
- All tests should be run with the chrome-devtools-mcp server connected
- Use `opencode mcp list` to verify connection status before testing
- Tests can be run against local dev server (localhost:3000) or production (packagedagile.com)
- Use `--no-usage-statistics` flag if privacy concerns exist

---

## Phase 6 - Test Execution Guide

**Important:** MCP tools can only be invoked through OpenCode's chat interface, not programmatically by agents. To execute these tests, copy and paste the prompts below into your OpenCode chat.

### Ready-to-Use Test Prompts

#### Test Case 1: Performance Audit
```
Run a performance audit on https://packagedagile.com using control-chrome:
1. Navigate to the website
2. Start a performance trace
3. Wait 3-5 seconds for the page to stabilize
4. Stop the performance trace
5. Analyze the trace and give me actionable performance insights
```

#### Test Case 2: Visual Regression Testing
```
Take screenshots of the Packaged Agile homepage using control-chrome:
1. Navigate to https://packagedagile.com
2. Take a full-page screenshot at desktop viewport (1280x720)
3. Resize to mobile viewport (375x667)
4. Take another full-page screenshot
5. Save both screenshots for comparison
```

#### Test Case 3: Contact Form Testing
```
Test the contact form on https://packagedagile.com/contact using control-chrome:
1. Navigate to the contact page
2. Take a screenshot of the initial form
3. Fill in the form fields with test data (but don't submit)
4. Take a screenshot of the filled form
5. Check the browser console for any JavaScript errors
6. Report the results
```

#### Test Case 4: Network Monitoring
```
Monitor network requests on https://packagedagile.com using control-chrome:
1. Navigate to the website
2. Wait for the page to fully load
3. List all network requests made
4. Show me the main document request and any API calls
5. Check the console for errors
6. Summarize what resources were loaded
```

#### Test Case 5: JavaScript Execution
```
Execute JavaScript on https://packagedagile.com using control-chrome:
1. Navigate to the website
2. Execute: document.title
3. Execute: document.querySelectorAll('h1').length
4. Execute: document.querySelectorAll('a').length
5. Execute: window.location.href
6. Check console for any errors
7. Report all results
```

#### Test Case 6: Multi-Page Navigation
```
Test navigation across the Packaged Agile website using control-chrome:
1. Navigate to https://packagedagile.com (homepage)
2. Take a screenshot
3. Navigate to /services
4. Take a screenshot
5. Navigate to /about
6. Take a screenshot
7. Navigate to /contact
8. Take a screenshot
9. List any console errors encountered
```

#### Test Case 7: Lighthouse Audit
```
Run a Lighthouse audit on https://packagedagile.com using control-chrome:
1. Navigate to the website
2. Run a comprehensive Lighthouse audit
3. Get scores for Performance, Accessibility, Best Practices, and SEO
4. Report the scores and any recommendations
```

#### Test Case 8: Memory Analysis
```
Analyze memory usage on https://packagedagile.com using control-chrome:
1. Navigate to the website
2. Take an initial memory snapshot
3. Scroll down the page and click on a few elements
4. Take a second memory snapshot
5. Compare the memory usage between the two snapshots
```

### Available MCP Tools Reference

**Navigation:**
- `navigate_page` - Navigate to a URL
- `new_page` - Open a new browser page
- `close_page` - Close a page
- `list_pages` - List all open pages

**Screenshots & Snapshots:**
- `take_screenshot` - Capture screenshot
- `take_snapshot` - Capture DOM snapshot

**Performance:**
- `performance_start_trace` - Start performance tracing
- `performance_stop_trace` - Stop performance tracing
- `performance_analyze_insight` - Analyze performance trace

**Auditing:**
- `lighthouse_audit` - Run Lighthouse audit

**Debugging:**
- `evaluate_script` - Execute JavaScript
- `list_console_messages` - List console messages
- `get_console_message` - Get specific console message

**Network:**
- `list_network_requests` - List network requests
- `get_network_request` - Get specific request details

**Interaction:**
- `click`, `fill`, `fill_form`, `type_text`, `press_key`, `hover`, `drag`

**Memory:**
- `take_memory_snapshot` - Capture memory snapshot

Checkbox states:
- [ ] Pending (not started)
- [~] In Progress (currently working on)
- [x] Completed (finished)

Important: plan.md is the authoritative source of truth for task progress.