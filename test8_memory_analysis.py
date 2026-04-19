"""
Test Case 8: Memory Snapshot Analysis
Analyzes memory usage before and after page interactions
"""
from playwright.sync_api import sync_playwright
import json
from datetime import datetime

def get_memory_metrics(page):
    """Get JavaScript heap metrics using Chrome DevTools Protocol"""
    client = page.context.new_cdp_session(page)
    
    # Enable required domains
    client.send("HeapProfiler.enable")
    
    # Get heap usage
    metrics = client.send("Runtime.getHeapUsage")
    
    # Get object counts by taking a sample
    client.send("HeapProfiler.collectGarbage")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "used_heap_size": metrics.get("usedSize", 0),
        "total_heap_size": metrics.get("totalSize", 0)
    }

def main():
    results = {
        "test_name": "Test Case 8: Memory Snapshot Analysis",
        "url": "https://packagedagile.com",
        "interactions": [],
        "console_logs": [],
        "memory_snapshots": {},
        "screenshot_path": "C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test8_memory.png"
    }
    
    with sync_playwright() as p:
        # Launch browser with CDP access for memory profiling
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--js-flags=--expose-gc',  # Enable manual GC
                '--enable-precise-memory-info'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        # Capture console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }))
        
        try:
            print("=" * 70)
            print("TEST CASE 8: MEMORY SNAPSHOT ANALYSIS")
            print("=" * 70)
            
            # Step 1: Navigate to page
            print("\n[1/7] Navigating to https://packagedagile.com...")
            page.goto("https://packagedagile.com")
            page.wait_for_load_state("networkidle")
            print("[OK] Page loaded successfully")
            
            # Step 2: Take initial memory snapshot
            print("\n[2/7] Capturing initial memory snapshot...")
            page.wait_for_timeout(1000)  # Let page settle
            initial_memory = get_memory_metrics(page)
            results["memory_snapshots"]["initial"] = initial_memory
            print(f"[OK] Initial Memory Captured:")
            print(f"  - Used Heap Size: {initial_memory['used_heap_size']:,} bytes ({initial_memory['used_heap_size']/1024/1024:.2f} MB)")
            print(f"  - Total Heap Size: {initial_memory['total_heap_size']:,} bytes ({initial_memory['total_heap_size']/1024/1024:.2f} MB)")
            
            # Step 3: Interact with page elements
            print("\n[3/7] Interacting with page elements...")
            
            # Find and click links/buttons
            interactions = []
            
            # Click 1: Try to find and click navigation links
            try:
                links = page.locator("a[href^='/']").all()
                if len(links) > 0:
                    link = links[0]
                    link_text = link.text_content() or "Navigation link"
                    print(f"  Clicking: {link_text[:50]}...")
                    link.click()
                    page.wait_for_timeout(1000)
                    interactions.append({"action": "click", "element": link_text[:50], "type": "navigation_link"})
                    print(f"  [OK] Clicked navigation link")
            except Exception as e:
                print(f"  ! Navigation link click failed: {e}")
            
            # Navigate back to main page
            page.goto("https://packagedagile.com")
            page.wait_for_load_state("networkidle")
            
            # Click 2: Look for buttons
            try:
                buttons = page.locator("button").all()
                if len(buttons) > 0:
                    button = buttons[0]
                    button_text = button.text_content() or "Button"
                    print(f"  Clicking button: {button_text[:50]}...")
                    button.click()
                    page.wait_for_timeout(500)
                    interactions.append({"action": "click", "element": button_text[:50], "type": "button"})
                    print(f"  [OK] Clicked button")
            except Exception as e:
                print(f"  ! Button click failed: {e}")
            
            # Click 3: Look for CTA links
            try:
                cta_links = page.locator("a[href*='#'], a.cta, .btn, .button").all()
                if len(cta_links) > 0:
                    cta = cta_links[0]
                    cta_text = cta.text_content() or "CTA"
                    print(f"  Clicking CTA: {cta_text[:50]}...")
                    cta.click()
                    page.wait_for_timeout(500)
                    interactions.append({"action": "click", "element": cta_text[:50], "type": "cta"})
                    print(f"  [OK] Clicked CTA")
            except Exception as e:
                print(f"  ! CTA click failed: {e}")
            
            results["interactions"] = interactions
            print(f"[OK] Completed {len(interactions)} interactions")
            
            # Step 4: Scroll down
            print("\n[4/7] Scrolling down the page...")
            for i in range(5):
                page.keyboard.press("PageDown")
                page.wait_for_timeout(300)
            results["interactions"].append({"action": "scroll", "direction": "down", "amount": "5 pages"})
            print("[OK] Scrolled down 5 pages")
            
            # Step 5: Take memory snapshot after interaction
            print("\n[5/7] Capturing memory snapshot after interaction...")
            page.wait_for_timeout(1000)  # Let page settle
            final_memory = get_memory_metrics(page)
            results["memory_snapshots"]["final"] = final_memory
            print(f"[OK] Final Memory Captured:")
            print(f"  - Used Heap Size: {final_memory['used_heap_size']:,} bytes ({final_memory['used_heap_size']/1024/1024:.2f} MB)")
            print(f"  - Total Heap Size: {final_memory['total_heap_size']:,} bytes ({final_memory['total_heap_size']/1024/1024:.2f} MB)")
            
            # Step 6: Take screenshot
            print("\n[6/7] Taking final screenshot...")
            import os
            screenshot_dir = os.path.dirname(results["screenshot_path"])
            os.makedirs(screenshot_dir, exist_ok=True)
            page.screenshot(path=results["screenshot_path"], full_page=True)
            print(f"[OK] Screenshot saved to: {results['screenshot_path']}")
            
            # Step 7: Check console messages
            print("\n[7/7] Checking console messages...")
            results["console_logs"] = console_logs
            
            # Filter memory-related logs
            memory_logs = [log for log in console_logs if any(
                keyword in log["text"].lower() 
                for keyword in ["memory", "leak", "heap", "gc", "garbage"]
            )]
            
            errors = [log for log in console_logs if log["type"] == "error"]
            warnings = [log for log in console_logs if log["type"] == "warning"]
            
            print(f"  Total console messages: {len(console_logs)}")
            print(f"  Errors: {len(errors)}")
            print(f"  Warnings: {len(warnings)}")
            print(f"  Memory-related messages: {len(memory_logs)}")
            
            if memory_logs:
                print("\n  Memory-related messages found:")
                for log in memory_logs[:5]:
                    print(f"    [{log['type']}] {log['text'][:100]}")
            
            if errors:
                print("\n  Errors found:")
                for error in errors[:5]:
                    print(f"    - {error['text'][:100]}")
            
            print("[OK] Console analysis complete")
            
        except Exception as e:
            print(f"\n[FAIL] Test failed with error: {e}")
            results["error"] = str(e)
            import traceback
            traceback.print_exc()
        
        finally:
            browser.close()
    
    # Calculate and display summary
    print("\n" + "=" * 70)
    print("MEMORY ANALYSIS REPORT")
    print("=" * 70)
    
    if "initial" in results["memory_snapshots"] and "final" in results["memory_snapshots"]:
        initial = results["memory_snapshots"]["initial"]
        final = results["memory_snapshots"]["final"]
        
        used_delta = final["used_heap_size"] - initial["used_heap_size"]
        total_delta = final["total_heap_size"] - initial["total_heap_size"]
        used_delta_mb = used_delta / 1024 / 1024
        total_delta_mb = total_delta / 1024 / 1024
        
        print(f"\n[DATA] INITIAL MEMORY SNAPSHOT:")
        print(f"   Used Heap:  {initial['used_heap_size']:,} bytes ({initial['used_heap_size']/1024/1024:.2f} MB)")
        print(f"   Total Heap: {initial['total_heap_size']:,} bytes ({initial['total_heap_size']/1024/1024:.2f} MB)")
        
        print(f"\n[DATA] FINAL MEMORY SNAPSHOT:")
        print(f"   Used Heap:  {final['used_heap_size']:,} bytes ({final['used_heap_size']/1024/1024:.2f} MB)")
        print(f"   Total Heap: {final['total_heap_size']:,} bytes ({final['total_heap_size']/1024/1024:.2f} MB)")
        
        print(f"\n[DATA] MEMORY DELTA:")
        print(f"   Used Heap Change:  {used_delta:+,} bytes ({used_delta_mb:+.2f} MB)")
        print(f"   Total Heap Change: {total_delta:+,} bytes ({total_delta_mb:+.2f} MB)")
        
        # Memory leak detection
        print(f"\n[ANALYSIS] MEMORY LEAK ANALYSIS:")
        if used_delta > 10 * 1024 * 1024:  # > 10MB increase
            print(f"   [WARN]  SIGNIFICANT INCREASE: {used_delta_mb:.2f} MB increase detected")
            print(f"   This may indicate a memory leak or normal page growth from interactions")
        elif used_delta > 5 * 1024 * 1024:  # > 5MB increase
            print(f"   [WARN]  MODERATE INCREASE: {used_delta_mb:.2f} MB increase detected")
        elif used_delta > 0:
            print(f"   [OK] NORMAL: {used_delta_mb:.2f} MB increase (within expected range)")
        else:
            print(f"   [OK] GOOD: Memory decreased by {abs(used_delta_mb):.2f} MB")
        
        # Calculate percentage change
        if initial["used_heap_size"] > 0:
            pct_change = (used_delta / initial["used_heap_size"]) * 100
            print(f"   Percentage Change: {pct_change:+.2f}%")
    
    print(f"\n[INPUT]  INTERACTIONS PERFORMED:")
    for i, interaction in enumerate(results["interactions"], 1):
        print(f"   {i}. {interaction['action'].upper()}: {interaction.get('element', interaction.get('direction', 'N/A'))}")
    
    print(f"\n[LOG] CONSOLE SUMMARY:")
    print(f"   Total Messages: {len(results['console_logs'])}")
    print(f"   Errors: {len([l for l in results['console_logs'] if l['type'] == 'error'])}")
    print(f"   Warnings: {len([l for l in results['console_logs'] if l['type'] == 'warning'])}")
    
    print(f"\n[IMG] SCREENSHOT:")
    print(f"   Saved to: {results['screenshot_path']}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    
    # Save detailed results to JSON
    import os
    results_dir = os.path.dirname(results["screenshot_path"])
    results_path = os.path.join(results_dir, "test8_memory_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {results_path}")
    
    return results

if __name__ == "__main__":
    main()
