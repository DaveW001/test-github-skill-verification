"""
Test Case 6: Page Navigation and Multi-Page Testing
Tests navigation across packagedagile.com pages with screenshots and console monitoring.
"""
from playwright.sync_api import sync_playwright
import os

# Screenshot paths
SCREENSHOT_DIR = "C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

screenshots = {
    "homepage": f"{SCREENSHOT_DIR}/test6_homepage.png",
    "services": f"{SCREENSHOT_DIR}/test6_services.png",
    "about": f"{SCREENSHOT_DIR}/test6_about.png",
    "contact": f"{SCREENSHOT_DIR}/test6_contact.png"
}

# Console messages storage
console_messages = []
page_titles = {}
navigation_results = {}

def log(msg):
    # Replace Unicode checkmarks/X marks with ASCII equivalents for Windows console
    msg = msg.replace('✓', '[OK]').replace('✗', '[FAIL]').replace('📊', '[STATS]').replace('📄', '[PAGES]').replace('📸', '[SCREENSHOTS]').replace('🖼️', '[IMAGES]').replace('🚨', '[ALERTS]').replace('•', '-')
    print(f"[TEST-6] {msg}")

with sync_playwright() as p:
    # Launch browser
    log("Launching Chromium browser...")
    browser = p.chromium.launch(headless=True)
    
    # Create browser context with console logging
    context = browser.new_context()
    
    # Listen for console messages across all pages
    context.on("page", lambda page: page.on("console", lambda msg: console_messages.append({
        "page": page.url,
        "type": msg.type,
        "text": msg.text,
        "location": msg.location
    })))
    
    # Create initial page
    log("Creating initial page...")
    page = context.new_page()
    
    # Set default timeouts
    page.set_default_timeout(30000)
    page.set_default_navigation_timeout(30000)
    
    # Step 1: Navigate to homepage
    log("=" * 60)
    log("STEP 1: Navigating to homepage (https://packagedagile.com)")
    try:
        page.goto("https://packagedagile.com", wait_until="networkidle")
        page_titles["homepage"] = page.title()
        navigation_results["homepage"] = "SUCCESS"
        log(f"✓ Homepage loaded - Title: {page.title()}")
    except Exception as e:
        navigation_results["homepage"] = f"FAILED: {str(e)}"
        log(f"✗ Homepage navigation failed: {e}")
    
    # Step 2: List all open pages
    log("=" * 60)
    log("STEP 2: Listing all open pages")
    pages = context.pages
    log(f"Number of open pages: {len(pages)}")
    for i, p in enumerate(pages):
        log(f"  Page {i+1}: {p.url} (Title: {p.title()})")
    
    # Step 3: Take screenshot of homepage
    log("=" * 60)
    log("STEP 3: Capturing homepage screenshot")
    try:
        page.screenshot(path=screenshots["homepage"], full_page=True)
        log(f"✓ Screenshot saved: {screenshots['homepage']}")
    except Exception as e:
        log(f"✗ Screenshot failed: {e}")
    
    # Step 4: Navigate to /services
    log("=" * 60)
    log("STEP 4: Navigating to /services")
    try:
        page.goto("https://packagedagile.com/services", wait_until="networkidle")
        page_titles["services"] = page.title()
        navigation_results["services"] = "SUCCESS"
        log(f"✓ Services page loaded - Title: {page.title()}")
    except Exception as e:
        navigation_results["services"] = f"FAILED: {str(e)}"
        log(f"✗ Services navigation failed: {e}")
    
    # Step 5: Take screenshot of services page
    log("=" * 60)
    log("STEP 5: Capturing services page screenshot")
    try:
        page.screenshot(path=screenshots["services"], full_page=True)
        log(f"✓ Screenshot saved: {screenshots['services']}")
    except Exception as e:
        log(f"✗ Screenshot failed: {e}")
    
    # Step 6: Navigate to /about
    log("=" * 60)
    log("STEP 6: Navigating to /about")
    try:
        page.goto("https://packagedagile.com/about", wait_until="networkidle")
        page_titles["about"] = page.title()
        navigation_results["about"] = "SUCCESS"
        log(f"✓ About page loaded - Title: {page.title()}")
    except Exception as e:
        navigation_results["about"] = f"FAILED: {str(e)}"
        log(f"✗ About navigation failed: {e}")
    
    # Step 7: Take screenshot of about page
    log("=" * 60)
    log("STEP 7: Capturing about page screenshot")
    try:
        page.screenshot(path=screenshots["about"], full_page=True)
        log(f"✓ Screenshot saved: {screenshots['about']}")
    except Exception as e:
        log(f"✗ Screenshot failed: {e}")
    
    # Step 8: Navigate to /contact
    log("=" * 60)
    log("STEP 8: Navigating to /contact")
    try:
        page.goto("https://packagedagile.com/contact", wait_until="networkidle")
        page_titles["contact"] = page.title()
        navigation_results["contact"] = "SUCCESS"
        log(f"✓ Contact page loaded - Title: {page.title()}")
    except Exception as e:
        navigation_results["contact"] = f"FAILED: {str(e)}"
        log(f"✗ Contact navigation failed: {e}")
    
    # Step 9: Take screenshot of contact page
    log("=" * 60)
    log("STEP 9: Capturing contact page screenshot")
    try:
        page.screenshot(path=screenshots["contact"], full_page=True)
        log(f"✓ Screenshot saved: {screenshots['contact']}")
    except Exception as e:
        log(f"✗ Screenshot failed: {e}")
    
    # Step 10: List console messages
    log("=" * 60)
    log("STEP 10: Checking console messages")
    
    # Also check current page console
    page_console = page.evaluate("() => { return window.console_logs || []; }")
    
    log(f"Total console messages captured: {len(console_messages)}")
    
    # Filter errors and warnings
    errors = [m for m in console_messages if m["type"] == "error"]
    warnings = [m for m in console_messages if m["type"] == "warning"]
    
    log(f"Errors: {len(errors)}")
    log(f"Warnings: {len(warnings)}")
    
    if errors:
        log("\n--- Console Errors ---")
        for err in errors[:10]:  # Show first 10 errors
            log(f"  [{err['type'].upper()}] {err['text'][:100]}")
            log(f"    URL: {err['page']}")
    
    if warnings:
        log("\n--- Console Warnings ---")
        for warn in warnings[:5]:  # Show first 5 warnings
            log(f"  [{warn['type'].upper()}] {warn['text'][:100]}")
    
    if not errors and not warnings:
        log("✓ No console errors or warnings detected")
    
    # Final state
    final_pages = context.pages
    
    # Cleanup
    log("=" * 60)
    log("Cleaning up...")
    context.close()
    browser.close()
    log("Browser closed")
    
    # Print final report
    log("=" * 60)
    log("TEST CASE 6: FINAL REPORT")
    log("=" * 60)
    
    log("\n📊 NAVIGATION RESULTS:")
    for page_name, result in navigation_results.items():
        status = "✓" if result == "SUCCESS" else "✗"
        log(f"  {status} {page_name.upper()}: {result}")
    
    log(f"\n📄 PAGE COUNT: {len(final_pages)} open page(s)")
    
    log("\n📸 PAGE TITLES:")
    for page_name, title in page_titles.items():
        log(f"  • {page_name}: {title}")
    
    log("\n🖼️  SCREENSHOTS SAVED:")
    for page_name, path in screenshots.items():
        exists = "✓" if os.path.exists(path) else "✗"
        log(f"  {exists} {page_name}: {path}")
    
    log("\n🚨 CONSOLE SUMMARY:")
    log(f"  • Total messages: {len(console_messages)}")
    log(f"  • Errors: {len(errors)}")
    log(f"  • Warnings: {len(warnings)}")
    
    log("\n" + "=" * 60)
    log("Test Case 6 Complete!")
    log("=" * 60)
