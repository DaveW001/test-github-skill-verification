#!/usr/bin/env python3
"""
Test Case 5: JavaScript Execution and Debugging
Tests JavaScript execution capabilities and console monitoring on packagedagile.com
"""

from playwright.sync_api import sync_playwright
import json

# Store console messages
console_messages = []
errors = []
warnings = []

def main():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set up console message listeners
        page.on("console", lambda msg: handle_console(msg))
        page.on("pageerror", lambda err: errors.append(f"Page Error: {err}"))
        
        print("=" * 70)
        print("TEST CASE 5: JavaScript Execution and Debugging")
        print("=" * 70)
        
        # Step 1: Navigate to the page
        print("\n[Step 1] Navigating to https://packagedagile.com...")
        page.goto("https://packagedagile.com")
        page.wait_for_load_state("networkidle")
        print("[OK] Navigation complete\n")
        
        # Step 2: Execute document.title
        print("[Step 2] Executing: document.title")
        title = page.evaluate("document.title")
        print(f"  Result: {title}\n")
        
        # Step 3: Execute document.querySelectorAll('h1').length
        print("[Step 3] Executing: document.querySelectorAll('h1').length")
        h1_count = page.evaluate("document.querySelectorAll('h1').length")
        print(f"  Result: {h1_count}\n")
        
        # Step 4: Execute document.querySelectorAll('a').length
        print("[Step 4] Executing: document.querySelectorAll('a').length")
        link_count = page.evaluate("document.querySelectorAll('a').length")
        print(f"  Result: {link_count}\n")
        
        # Step 5: Execute window.location.href
        print("[Step 5] Executing: window.location.href")
        current_url = page.evaluate("window.location.href")
        print(f"  Result: {current_url}\n")
        
        # Step 6: Execute viewport and user agent info
        print("[Step 6] Executing viewport dimensions and user agent...")
        viewport_info = page.evaluate("""() => {
            return JSON.stringify({
                width: window.innerWidth,
                height: window.innerHeight,
                userAgent: navigator.userAgent.substring(0, 50)
            });
        }""")
        viewport_data = json.loads(viewport_info)
        print(f"  Result: {viewport_info}\n")
        
        # Step 7: Check for console errors
        print("[Step 7] Checking for console messages...")
        # Wait a bit to capture any late console messages
        page.wait_for_timeout(500)
        
        print("=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"\nPage Title:           {title}")
        print(f"Number of H1 elements: {h1_count}")
        print(f"Number of links:      {link_count}")
        print(f"Current URL:          {current_url}")
        print(f"Viewport Width:       {viewport_data['width']}")
        print(f"Viewport Height:      {viewport_data['height']}")
        print(f"User Agent:           {viewport_data['userAgent']}")
        
        print("\n" + "=" * 70)
        print("CONSOLE MESSAGES")
        print("=" * 70)
        
        if not console_messages:
            print("\n  No console messages captured.")
        else:
            for msg in console_messages:
                level = msg['level'].upper()
                text = msg['text']
                print(f"\n  [{level}] {text}")
        
        print("\n" + "=" * 70)
        print("ERRORS AND WARNINGS")
        print("=" * 70)
        
        if errors:
            print("\n  Page Errors:")
            for err in errors:
                print(f"    - {err}")
        else:
            print("\n  [OK] No page errors detected")
        
        browser.close()
        print("\n" + "=" * 70)
        print("TEST CASE 5 COMPLETED")
        print("=" * 70)

def handle_console(msg):
    """Handle console messages"""
    message_data = {
        'level': msg.type,
        'text': msg.text
    }
    console_messages.append(message_data)

if __name__ == "__main__":
    main()
