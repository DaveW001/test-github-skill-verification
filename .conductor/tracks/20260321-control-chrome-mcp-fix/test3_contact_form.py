from playwright.sync_api import sync_playwright
import os

# Test Case 3: Contact Form Testing
url = 'https://packagedagile.com/contact'

# Screenshot paths
initial_screenshot = 'C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test3_initial.png'
filled_screenshot = 'C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test3_filled.png'

console_logs = []
results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    
    # Set up console log capture
    def handle_console_message(msg):
        log_entry = f"[{msg.type}] {msg.text}"
        console_logs.append(log_entry)
    
    page.on("console", handle_console_message)
    
    # Step 1: Navigate to contact page
    print("Navigating to contact page...")
    page.goto(url)
    page.wait_for_load_state('networkidle')
    results.append("[PASS] Navigation successful")
    
    # Step 2: Take initial screenshot
    print("Taking initial screenshot...")
    page.screenshot(path=initial_screenshot, full_page=True)
    results.append(f"[PASS] Initial screenshot saved to: {initial_screenshot}")
    
    # Step 3: Identify and fill form fields
    print("Identifying form fields...")
    
    # Discover form fields
    form_fields = page.locator('input, textarea, select').all()
    results.append(f"  Found {len(form_fields)} form elements")
    
    # Fill Name
    name_field = page.locator('input[type="text"], input[name*="name" i], input[id*="name" i], input[placeholder*="name" i]').first
    if name_field.count() > 0:
        name_field.fill("Test User")
        results.append("[PASS] Name field filled: 'Test User'")
    
    # Fill Email
    email_field = page.locator('input[type="email"], input[name*="email" i], input[id*="email" i]').first
    if email_field.count() > 0:
        email_field.fill("test@example.com")
        results.append("[PASS] Email field filled: 'test@example.com'")
    
    # Fill Company
    company_field = page.locator('input[name*="company" i], input[id*="company" i], input[placeholder*="company" i]').first
    if company_field.count() > 0:
        company_field.fill("Test Company")
        results.append("[PASS] Company field filled: 'Test Company'")
    elif name_field.count() > 1:
        # Try second text field if no explicit company field
        all_text = page.locator('input[type="text"]').all()
        if len(all_text) > 1:
            all_text[1].fill("Test Company")
            results.append("[PASS] Company field filled: 'Test Company' (2nd text field)")
    
    # Fill Message
    message_field = page.locator('textarea, input[name*="message" i], input[id*="message" i]').first
    if message_field.count() > 0:
        message_field.fill("This is a test message from chrome-devtools-mcp")
        results.append("[PASS] Message field filled: 'This is a test message from chrome-devtools-mcp'")
    
    # Step 4: Take screenshot of filled form
    print("Taking filled form screenshot...")
    page.screenshot(path=filled_screenshot, full_page=True)
    results.append(f"[PASS] Filled form screenshot saved to: {filled_screenshot}")
    
    # Step 5: Check for submit button (verify form is ready)
    submit_button = page.locator('button[type="submit"], input[type="submit"]').first
    if submit_button.count() > 0:
        is_visible = submit_button.is_visible()
        is_enabled = submit_button.is_enabled()
        results.append(f"[PASS] Submit button found (visible: {is_visible}, enabled: {is_enabled})")
    else:
        results.append("[WARN] No submit button found")
    
    browser.close()

# Print results
print("\n" + "="*60)
print("TEST CASE 3: CONTACT FORM TESTING - RESULTS")
print("="*60)
for result in results:
    print(result)

print("\n" + "-"*60)
print("CONSOLE MESSAGES:")
print("-"*60)
if console_logs:
    # Filter for errors
    errors = [log for log in console_logs if 'error' in log.lower() or 'warning' in log.lower()]
    if errors:
        print(f"Found {len(errors)} errors/warnings:")
        for err in errors:
            print(f"  {err}")
    else:
        print("No errors or warnings found")
    print(f"\nTotal console messages: {len(console_logs)}")
    if len(console_logs) <= 20:
        for log in console_logs:
            print(f"  {log}")
else:
    print("No console messages captured")

print("\n" + "="*60)
print("FORM SUBMISSION STATUS: Ready (not submitted as requested)")
print("="*60)
