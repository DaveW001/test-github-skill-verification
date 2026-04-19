#!/usr/bin/env python3
"""
Test Case 1: Performance Audit of Packaged Agile Website
Uses Playwright to navigate, screenshot, and collect performance metrics
"""

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime

def run_performance_audit():
    results = {
        "test_case": "Performance Audit - Packaged Agile Website",
        "url": "https://packagedagile.com",
        "timestamp": datetime.now().isoformat(),
        "steps": []
    }
    
    client = None
    
    with sync_playwright() as p:
        # Launch browser with performance monitoring enabled
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        # Enable CDP session for performance metrics
        page = context.new_page()
        
        # Step 1: Navigate to the website
        print("=" * 70)
        print("STEP 1: Navigating to https://packagedagile.com")
        print("=" * 70)
        
        try:
            start_time = time.time()
            response = page.goto("https://packagedagile.com", wait_until="networkidle")
            navigation_time = time.time() - start_time
            
            nav_result = {
                "step": 1,
                "action": "navigate_page",
                "status": "SUCCESS",
                "url": "https://packagedagile.com",
                "response_status": response.status if response else "N/A",
                "navigation_time_seconds": round(navigation_time, 2)
            }
            results["steps"].append(nav_result)
            
            print(f"[OK] Navigation successful")
            print(f"  URL: https://packagedagile.com")
            print(f"  Response Status: {response.status if response else 'N/A'}")
            print(f"  Navigation Time: {navigation_time:.2f} seconds")
            
        except Exception as e:
            nav_result = {
                "step": 1,
                "action": "navigate_page",
                "status": "FAILED",
                "error": str(e)
            }
            results["steps"].append(nav_result)
            print(f"[FAIL] Navigation failed: {e}")
            browser.close()
            return results
        
        # Step 2: Take screenshot
        print("\n" + "=" * 70)
        print("STEP 2: Capturing Screenshot")
        print("=" * 70)
        
        try:
            screenshot_path = "C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test1_screenshot.png"
            page.screenshot(path=screenshot_path, full_page=True)
            
            screenshot_result = {
                "step": 2,
                "action": "take_screenshot",
                "status": "SUCCESS",
                "path": screenshot_path,
                "full_page": True
            }
            results["steps"].append(screenshot_result)
            
            print(f"[OK] Screenshot saved successfully")
            print(f"  Path: {screenshot_path}")
            print(f"  Full Page: Yes")
            
        except Exception as e:
            screenshot_result = {
                "step": 2,
                "action": "take_screenshot",
                "status": "FAILED",
                "error": str(e)
            }
            results["steps"].append(screenshot_result)
            print(f"[FAIL] Screenshot failed: {e}")
        
        # Step 3 & 4: Start performance trace and wait
        print("\n" + "=" * 70)
        print("STEP 3 & 4: Starting Performance Trace & Waiting 5 seconds")
        print("=" * 70)
        
        try:
            # Start tracing
            page.context.tracing.start(screenshots=True, snapshots=True)
            
            # Also collect performance metrics via CDP
            client = page.context.new_cdp_session(page)
            
            # Enable performance monitoring
            client.send("Performance.enable")
            
            trace_result = {
                "step": 3,
                "action": "performance_start_trace",
                "status": "SUCCESS",
                "method": "Playwright Tracing + CDP Performance API"
            }
            results["steps"].append(trace_result)
            
            print(f"[OK] Performance trace started")
            print(f"  Method: Playwright Tracing + CDP Performance API")
            
            # Wait 5 seconds
            print(f"  Waiting 5 seconds for metrics collection...")
            time.sleep(5)
            
            wait_result = {
                "step": 4,
                "action": "wait",
                "status": "SUCCESS",
                "duration_seconds": 5
            }
            results["steps"].append(wait_result)
            
            print(f"[OK] Wait completed (5 seconds)")
            
        except Exception as e:
            trace_result = {
                "step": 3,
                "action": "performance_start_trace",
                "status": "FAILED",
                "error": str(e)
            }
            results["steps"].append(trace_result)
            print(f"[FAIL] Performance trace failed: {e}")
        
        # Step 5: Stop trace and collect metrics
        print("\n" + "=" * 70)
        print("STEP 5: Stopping Performance Trace & Collecting Metrics")
        print("=" * 70)
        
        try:
            # Get performance metrics
            performance_metrics = client.send("Performance.getMetrics") if client else {}
            
            # Stop tracing
            trace_path = "C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test1_trace.zip"
            page.context.tracing.stop(path=trace_path)
            
            # Extract key metrics
            metrics_data = {}
            if "metrics" in performance_metrics:
                for metric in performance_metrics["metrics"]:
                    metrics_data[metric["name"]] = metric["value"]
            
            stop_result = {
                "step": 5,
                "action": "performance_stop_trace",
                "status": "SUCCESS",
                "trace_saved": trace_path,
                "metrics_collected": len(metrics_data)
            }
            results["steps"].append(stop_result)
            
            print(f"[OK] Performance trace stopped")
            print(f"  Trace saved: {trace_path}")
            print(f"  Metrics collected: {len(metrics_data)}")
            
            # Store metrics for analysis
            results["performance_metrics"] = metrics_data
            
        except Exception as e:
            stop_result = {
                "step": 5,
                "action": "performance_stop_trace",
                "status": "FAILED",
                "error": str(e)
            }
            results["steps"].append(stop_result)
            print(f"[FAIL] Stopping trace failed: {e}")
            metrics_data = {}
        
        # Step 6: Analyze insights
        print("\n" + "=" * 70)
        print("STEP 6: Analyzing Performance Insights")
        print("=" * 70)
        
        try:
            insights = {
                "page_load_analysis": {},
                "memory_analysis": {},
                "rendering_analysis": {},
                "recommendations": []
            }
            
            # Analyze key metrics
            if metrics_data:
                # Navigation timing
                if "NavigationStart" in metrics_data:
                    nav_start = metrics_data["NavigationStart"]
                    insights["page_load_analysis"]["navigation_start"] = nav_start
                
                if "DOMContentLoaded" in metrics_data:
                    dcl = metrics_data["DOMContentLoaded"]
                    insights["page_load_analysis"]["dom_content_loaded"] = dcl
                    if dcl < 2000:
                        insights["page_load_analysis"]["dom_load_rating"] = "EXCELLENT"
                    elif dcl < 4000:
                        insights["page_load_analysis"]["dom_load_rating"] = "GOOD"
                    else:
                        insights["page_load_analysis"]["dom_load_rating"] = "NEEDS_IMPROVEMENT"
                
                if "FirstMeaningfulPaint" in metrics_data:
                    fmp = metrics_data["FirstMeaningfulPaint"]
                    insights["page_load_analysis"]["first_meaningful_paint"] = fmp
                
                # Memory metrics
                if "JSHeapUsedSize" in metrics_data:
                    heap_used = metrics_data["JSHeapUsedSize"] / (1024 * 1024)  # Convert to MB
                    insights["memory_analysis"]["js_heap_used_mb"] = round(heap_used, 2)
                    if heap_used < 50:
                        insights["memory_analysis"]["memory_rating"] = "EXCELLENT"
                    elif heap_used < 100:
                        insights["memory_analysis"]["memory_rating"] = "GOOD"
                    else:
                        insights["memory_analysis"]["memory_rating"] = "NEEDS_ATTENTION"
                
                if "JSHeapTotalSize" in metrics_data:
                    heap_total = metrics_data["JSHeapTotalSize"] / (1024 * 1024)
                    insights["memory_analysis"]["js_heap_total_mb"] = round(heap_total, 2)
                
                # Rendering metrics
                if "LayoutCount" in metrics_data:
                    insights["rendering_analysis"]["layout_count"] = metrics_data["LayoutCount"]
                
                if "RecalcStyleCount" in metrics_data:
                    insights["rendering_analysis"]["style_recalc_count"] = metrics_data["RecalcStyleCount"]
                
                # Generate recommendations
                if "DOMContentLoaded" in metrics_data and metrics_data["DOMContentLoaded"] > 4000:
                    insights["recommendations"].append("Consider optimizing DOM loading - current load time exceeds 4 seconds")
                
                if "JSHeapUsedSize" in metrics_data and metrics_data["JSHeapUsedSize"] / (1024 * 1024) > 100:
                    insights["recommendations"].append("High JavaScript heap usage detected - review memory leaks or unnecessary objects")
                
                if "LayoutCount" in metrics_data and metrics_data["LayoutCount"] > 10:
                    insights["recommendations"].append("High layout thrashing detected - consider optimizing CSS and layout operations")
                
                if not insights["recommendations"]:
                    insights["recommendations"].append("Page performance appears good - no major issues detected")
            
            # Collect additional page metrics
            page_metrics = page.evaluate("""() => {
                return {
                    title: document.title,
                    url: window.location.href,
                    loadEventEnd: performance.timing.loadEventEnd - performance.timing.navigationStart,
                    domComplete: performance.timing.domComplete - performance.timing.navigationStart,
                    resourceCount: performance.getEntriesByType('resource').length,
                    totalResourceSize: performance.getEntriesByType('resource').reduce((acc, r) => acc + (r.transferSize || 0), 0)
                }
            }""")
            
            insights["page_metrics"] = page_metrics
            insights["page_metrics"]["total_resource_size_mb"] = round(page_metrics["totalResourceSize"] / (1024 * 1024), 2)
            
            analyze_result = {
                "step": 6,
                "action": "performance_analyze_insight",
                "status": "SUCCESS",
                "insights_generated": len(insights)
            }
            results["steps"].append(analyze_result)
            results["insights"] = insights
            
            print(f"[OK] Performance analysis completed")
            print(f"  Insights generated: {len(insights)}")
            print(f"  Recommendations: {len(insights['recommendations'])}")
            
        except Exception as e:
            analyze_result = {
                "step": 6,
                "action": "performance_analyze_insight",
                "status": "FAILED",
                "error": str(e)
            }
            results["steps"].append(analyze_result)
            print(f"[FAIL] Performance analysis failed: {e}")
        
        # Collect final page info
        try:
            results["final_page_info"] = {
                "title": page.title(),
                "url": page.url,
                "viewport": {"width": 1920, "height": 1080}
            }
        except:
            pass
        
        browser.close()
    
    return results

if __name__ == "__main__":
    results = run_performance_audit()
    
    # Save detailed results to JSON
    json_path = "C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test1_results.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("TEST EXECUTION COMPLETE")
    print("=" * 70)
    print(f"Detailed results saved to: {json_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("EXECUTION SUMMARY")
    print("=" * 70)
    
    for step in results["steps"]:
        status_icon = "[OK]" if step["status"] == "SUCCESS" else "[FAIL]"
        print(f"{status_icon} Step {step['step']}: {step['action']} - {step['status']}")
    
    # Print key insights
    if "insights" in results:
        print("\n" + "=" * 70)
        print("PERFORMANCE INSIGHTS")
        print("=" * 70)
        
        if "page_metrics" in results["insights"]:
            pm = results["insights"]["page_metrics"]
            print(f"\nPage Information:")
            print(f"  Title: {pm.get('title', 'N/A')}")
            print(f"  Resources Loaded: {pm.get('resourceCount', 'N/A')}")
            print(f"  Total Resource Size: {pm.get('total_resource_size_mb', 'N/A')} MB")
            print(f"  Load Event Time: {pm.get('loadEventEnd', 'N/A')} ms")
        
        if "memory_analysis" in results["insights"]:
            ma = results["insights"]["memory_analysis"]
            print(f"\nMemory Analysis:")
            print(f"  JS Heap Used: {ma.get('js_heap_used_mb', 'N/A')} MB")
            print(f"  JS Heap Total: {ma.get('js_heap_total_mb', 'N/A')} MB")
            print(f"  Rating: {ma.get('memory_rating', 'N/A')}")
        
        if "rendering_analysis" in results["insights"]:
            ra = results["insights"]["rendering_analysis"]
            print(f"\nRendering Analysis:")
            print(f"  Layout Count: {ra.get('layout_count', 'N/A')}")
            print(f"  Style Recalc Count: {ra.get('style_recalc_count', 'N/A')}")
        
        if "recommendations" in results["insights"]:
            print(f"\nRecommendations:")
            for i, rec in enumerate(results["insights"]["recommendations"], 1):
                print(f"  {i}. {rec}")
    
    print("\n" + "=" * 70)
    print("All artifacts saved to:")
    print("  C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/")
    print("=" * 70)
