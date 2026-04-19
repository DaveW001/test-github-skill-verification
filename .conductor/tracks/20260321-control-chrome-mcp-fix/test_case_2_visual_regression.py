#!/usr/bin/env python3
"""
Test Case 2: Visual Regression Testing for packagedagile.com
"""
from playwright.sync_api import sync_playwright
import os

def main():
    # Ensure output directory exists
    output_dir = "C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix"
    os.makedirs(output_dir, exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Set longer timeouts for navigation
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(30000)
        
        print("=" * 60)
        print("Test Case 2: Visual Regression Testing")
        print("=" * 60)
        
        # Step 1: Navigate to packagedagile.com
        print("\n[Step 1] Navigating to https://packagedagile.com...")
        try:
            page.goto("https://packagedagile.com", wait_until="networkidle")
            print("  [OK] Navigation successful")
            print(f"  URL: {page.url}")
            print(f"  Title: {page.title()}")
        except Exception as e:
            print(f"  [FAIL] Navigation failed: {e}")
            browser.close()
            return
        
        # Step 2: Set desktop viewport
        print("\n[Step 2] Setting viewport to desktop (1280x720)...")
        page.set_viewport_size({"width": 1280, "height": 720})
        # Wait for layout to settle
        page.wait_for_timeout(500)
        print("  [OK] Desktop viewport set")
        
        # Step 3: Take desktop screenshot
        print("\n[Step 3] Capturing desktop screenshot...")
        desktop_path = os.path.join(output_dir, "test2_desktop.png")
        page.screenshot(path=desktop_path, full_page=False)
        desktop_size = os.path.getsize(desktop_path)
        print(f"  [OK] Desktop screenshot saved: {desktop_path}")
        print(f"  File size: {desktop_size:,} bytes ({desktop_size/1024:.1f} KB)")
        
        # Step 4: Set mobile viewport
        print("\n[Step 4] Setting viewport to mobile (375x667)...")
        page.set_viewport_size({"width": 375, "height": 667})
        # Wait for layout to settle
        page.wait_for_timeout(500)
        print("  [OK] Mobile viewport set")
        
        # Step 5: Take mobile screenshot
        print("\n[Step 5] Capturing mobile screenshot...")
        mobile_path = os.path.join(output_dir, "test2_mobile.png")
        page.screenshot(path=mobile_path, full_page=False)
        mobile_size = os.path.getsize(mobile_path)
        print(f"  [OK] Mobile screenshot saved: {mobile_path}")
        print(f"  File size: {mobile_size:,} bytes ({mobile_size/1024:.1f} KB)")
        
        # Step 6: Capture DOM snapshot
        print("\n[Step 6] Capturing DOM structure...")
        
        # Get page metrics
        dom_stats = page.evaluate("""() => {
            return {
                totalNodes: document.querySelectorAll('*').length,
                bodyNodes: document.body ? document.body.querySelectorAll('*').length : 0,
                links: document.querySelectorAll('a').length,
                images: document.querySelectorAll('img').length,
                headings: document.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
                buttons: document.querySelectorAll('button').length,
                inputs: document.querySelectorAll('input').length,
                forms: document.querySelectorAll('form').length,
                scripts: document.querySelectorAll('script').length,
                stylesheets: document.querySelectorAll('link[rel="stylesheet"]').length,
                h1Text: Array.from(document.querySelectorAll('h1')).map(h => h.textContent.trim()).join(', ')
            };
        }""")
        
        # Get page HTML for structure
        html_content = page.content()
        
        # Save DOM snapshot
        snapshot_path = os.path.join(output_dir, "test2_dom_snapshot.html")
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        snapshot_size = os.path.getsize(snapshot_path)
        
        print(f"  [OK] DOM snapshot saved: {snapshot_path}")
        print(f"  File size: {snapshot_size:,} bytes ({snapshot_size/1024:.1f} KB)")
        
        # Report DOM statistics
        print("\n" + "=" * 60)
        print("DOM SNAPSHOT SUMMARY")
        print("=" * 60)
        print(f"  Total DOM nodes: {dom_stats['totalNodes']:,}")
        print(f"  Body nodes: {dom_stats['bodyNodes']:,}")
        print(f"  Links (<a>): {dom_stats['links']}")
        print(f"  Images (<img>): {dom_stats['images']}")
        print(f"  Headings (h1-h6): {dom_stats['headings']}")
        print(f"  Buttons: {dom_stats['buttons']}")
        print(f"  Input fields: {dom_stats['inputs']}")
        print(f"  Forms: {dom_stats['forms']}")
        print(f"  Scripts: {dom_stats['scripts']}")
        print(f"  Stylesheets: {dom_stats['stylesheets']}")
        print(f"\n  Primary H1 text: {dom_stats['h1Text'] if dom_stats['h1Text'] else '(no H1 found)'}")
        
        # Report summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"  Navigation: [OK] Success")
        print(f"  Desktop viewport (1280x720): [OK] Set")
        print(f"  Mobile viewport (375x667): [OK] Set")
        print(f"  Desktop screenshot: {desktop_size/1024:.1f} KB")
        print(f"  Mobile screenshot: {mobile_size/1024:.1f} KB")
        print(f"  DOM snapshot: {dom_stats['totalNodes']:,} nodes")
        
        browser.close()
        print("\n[OK] Test Case 2 completed successfully")

if __name__ == "__main__":
    main()
