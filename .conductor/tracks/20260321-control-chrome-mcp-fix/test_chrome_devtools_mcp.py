#!/usr/bin/env python3
"""
Chrome DevTools MCP Test Suite
Comprehensive testing script for validating chrome-devtools-mcp functionality

Usage:
    python test_chrome_devtools_mcp.py

Requirements:
    - Chrome DevTools MCP server must be configured and running
    - opencode CLI must be available
"""

import subprocess
import sys
import time
from datetime import datetime

class TestResult:
    def __init__(self, name, status, details=""):
        self.name = name
        self.status = status
        self.details = details
        self.timestamp = datetime.now().isoformat()

    def __str__(self):
        status_icon = "[PASS]" if self.status == "PASS" else "[FAIL]" if self.status == "FAIL" else "[PENDING]"
        return f"{status_icon} {self.name}\n    Status: {self.status}\n    Details: {self.details}\n    Time: {self.timestamp}"

def run_opencode_command(args):
    """Run an opencode CLI command"""
    try:
        result = subprocess.run(
            ["opencode"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_mcp_server_connection():
    """Test Case 0: Verify MCP server is connected"""
    print("\n" + "="*60)
    print("TEST CASE 0: MCP Server Connection")
    print("="*60)
    
    success, stdout, stderr = run_opencode_command(["mcp", "list"])
    
    if success and "control-chrome" in stdout and "connected" in stdout.lower():
        return TestResult(
            "MCP Server Connection",
            "PASS",
            "control-chrome server is connected and available"
        )
    else:
        return TestResult(
            "MCP Server Connection",
            "FAIL",
            f"Server not connected. Output: {stdout} Error: {stderr}"
        )

def test_navigate_and_screenshot():
    """Test Case 1: Navigate to website and take screenshot"""
    print("\n" + "="*60)
    print("TEST CASE 1: Navigate and Screenshot")
    print("="*60)
    print("Target: https://packagedagile.com")
    
    # Note: This test documents what SHOULD work with control-chrome tools
    # The actual tool invocation would be through OpenCode's MCP integration
    
    test_steps = [
        "1. Navigate to https://packagedagile.com",
        "2. Wait for page to load (networkidle)",
        "3. Take full-page screenshot",
        "4. Verify screenshot was captured"
    ]
    
    print("\nTest Steps:")
    for step in test_steps:
        print(f"  {step}")
    
    print("\nExpected Tools:")
    print("  - control-chrome_navigate_page")
    print("  - control-chrome_take_screenshot")
    
    return TestResult(
        "Navigate and Screenshot",
        "PENDING",
        "Test documented. Execute manually via OpenCode with MCP tools enabled."
    )

def test_performance_audit():
    """Test Case 2: Performance Audit"""
    print("\n" + "="*60)
    print("TEST CASE 2: Performance Audit")
    print("="*60)
    print("Target: https://packagedagile.com")
    
    test_steps = [
        "1. Navigate to https://packagedagile.com",
        "2. Start performance trace (performance_start_trace)",
        "3. Wait 3-5 seconds for page to stabilize",
        "4. Stop performance trace (performance_stop_trace)",
        "5. Analyze trace (performance_analyze_insight)",
        "6. Verify insights are generated"
    ]
    
    print("\nTest Steps:")
    for step in test_steps:
        print(f"  {step}")
    
    print("\nExpected Tools:")
    print("  - control-chrome_navigate_page")
    print("  - control-chrome_performance_start_trace")
    print("  - control-chrome_performance_stop_trace")
    print("  - control-chrome_performance_analyze_insight")
    
    return TestResult(
        "Performance Audit",
        "PENDING",
        "Test documented. Execute manually via OpenCode with MCP tools enabled."
    )

def test_lighthouse_audit():
    """Test Case 3: Lighthouse Audit"""
    print("\n" + "="*60)
    print("TEST CASE 3: Lighthouse Audit")
    print("="*60)
    print("Target: https://packagedagile.com")
    
    test_steps = [
        "1. Navigate to https://packagedagile.com",
        "2. Run lighthouse_audit tool",
        "3. Capture scores for:",
        "   - Performance",
        "   - Accessibility",
        "   - Best Practices",
        "   - SEO",
        "4. Verify audit completes successfully"
    ]
    
    print("\nTest Steps:")
    for step in test_steps:
        print(f"  {step}")
    
    print("\nExpected Tools:")
    print("  - control-chrome_navigate_page")
    print("  - control-chrome_lighthouse_audit")
    
    return TestResult(
        "Lighthouse Audit",
        "PENDING",
        "Test documented. Execute manually via OpenCode with MCP tools enabled."
    )

def test_network_monitoring():
    """Test Case 4: Network Request Monitoring"""
    print("\n" + "="*60)
    print("TEST CASE 4: Network Request Monitoring")
    print("="*60)
    print("Target: https://packagedagile.com")
    
    test_steps = [
        "1. Navigate to https://packagedagile.com",
        "2. Wait for page to fully load",
        "3. List network requests (list_network_requests)",
        "4. Inspect specific requests (get_network_request)",
        "5. Check console messages for errors",
        "6. Verify all resources loaded correctly"
    ]
    
    print("\nTest Steps:")
    for step in test_steps:
        print(f"  {step}")
    
    print("\nExpected Tools:")
    print("  - control-chrome_navigate_page")
    print("  - control-chrome_list_network_requests")
    print("  - control-chrome_get_network_request")
    print("  - control-chrome_list_console_messages")
    
    return TestResult(
        "Network Monitoring",
        "PENDING",
        "Test documented. Execute manually via OpenCode with MCP tools enabled."
    )

def test_javascript_execution():
    """Test Case 5: JavaScript Execution"""
    print("\n" + "="*60)
    print("TEST CASE 5: JavaScript Execution")
    print("="*60)
    print("Target: https://packagedagile.com")
    
    test_steps = [
        "1. Navigate to https://packagedagile.com",
        "2. Execute JavaScript: document.title",
        "3. Execute JavaScript: document.querySelectorAll('h1').length",
        "4. Execute JavaScript: window.location.href",
        "5. Verify all scripts execute without errors",
        "6. Check console for any warnings"
    ]
    
    print("\nTest Steps:")
    for step in test_steps:
        print(f"  {step}")
    
    print("\nExpected Tools:")
    print("  - control-chrome_navigate_page")
    print("  - control-chrome_evaluate_script")
    print("  - control-chrome_list_console_messages")
    
    return TestResult(
        "JavaScript Execution",
        "PENDING",
        "Test documented. Execute manually via OpenCode with MCP tools enabled."
    )

def test_form_interaction():
    """Test Case 6: Contact Form Testing"""
    print("\n" + "="*60)
    print("TEST CASE 6: Contact Form Testing")
    print("="*60)
    print("Target: https://packagedagile.com/contact")
    
    test_steps = [
        "1. Navigate to https://packagedagile.com/contact",
        "2. Take screenshot of initial form state",
        "3. Fill form fields using fill or fill_form tool",
        "4. Take screenshot of filled form",
        "5. Check console for JavaScript errors",
        "6. Verify form is ready for submission"
    ]
    
    print("\nTest Steps:")
    for step in test_steps:
        print(f"  {step}")
    
    print("\nExpected Tools:")
    print("  - control-chrome_navigate_page")
    print("  - control-chrome_take_screenshot")
    print("  - control-chrome_fill")
    print("  - control-chrome_fill_form")
    print("  - control-chrome_list_console_messages")
    
    return TestResult(
        "Contact Form Testing",
        "PENDING",
        "Test documented. Execute manually via OpenCode with MCP tools enabled."
    )

def test_multi_page_navigation():
    """Test Case 7: Multi-Page Navigation"""
    print("\n" + "="*60)
    print("TEST CASE 7: Multi-Page Navigation")
    print("="*60)
    print("Targets: Homepage, Services, About, Contact")
    
    test_steps = [
        "1. Navigate to homepage",
        "2. List all pages (list_pages)",
        "3. Take screenshot of homepage",
        "4. Navigate to /services",
        "5. Take screenshot of services page",
        "6. Navigate to /about",
        "7. Take screenshot of about page",
        "8. Navigate to /contact",
        "9. Take screenshot of contact page",
        "10. Verify navigation works smoothly"
    ]
    
    print("\nTest Steps:")
    for step in test_steps:
        print(f"  {step}")
    
    print("\nExpected Tools:")
    print("  - control-chrome_navigate_page")
    print("  - control-chrome_list_pages")
    print("  - control-chrome_take_screenshot")
    
    return TestResult(
        "Multi-Page Navigation",
        "PENDING",
        "Test documented. Execute manually via OpenCode with MCP tools enabled."
    )

def test_memory_analysis():
    """Test Case 8: Memory Snapshot Analysis"""
    print("\n" + "="*60)
    print("TEST CASE 8: Memory Snapshot Analysis")
    print("="*60)
    print("Target: https://packagedagile.com")
    
    test_steps = [
        "1. Navigate to https://packagedagile.com",
        "2. Take initial memory snapshot",
        "3. Interact with page (scroll, click elements)",
        "4. Take second memory snapshot",
        "5. Compare snapshots for memory usage",
        "6. Check for memory leaks"
    ]
    
    print("\nTest Steps:")
    for step in test_steps:
        print(f"  {step}")
    
    print("\nExpected Tools:")
    print("  - control-chrome_navigate_page")
    print("  - control-chrome_take_memory_snapshot")
    print("  - control-chrome_click")
    print("  - control-chrome_press_key (for scrolling)")
    
    return TestResult(
        "Memory Analysis",
        "PENDING",
        "Test documented. Execute manually via OpenCode with MCP tools enabled."
    )

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    pending = sum(1 for r in results if r.status == "PENDING")
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Pending: {pending}")
    
    print("\nDetailed Results:")
    for result in results:
        print(f"\n{result}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
To execute these tests with actual MCP tool invocations:

1. Open OpenCode desktop application
2. Ensure control-chrome MCP server shows green dot (connected)
3. Ask OpenCode to run any of these test cases:
   
   Example prompts:
   - "Run Test Case 1: Navigate to https://packagedagile.com and take a screenshot"
   - "Run Test Case 2: Perform a performance audit on https://packagedagile.com"
   - "Run Test Case 3: Run a Lighthouse audit on the PA website"

The MCP tools available include:
  - navigate_page, new_page, close_page, list_pages
  - take_screenshot, take_snapshot
  - performance_start_trace, performance_stop_trace, performance_analyze_insight
  - lighthouse_audit
  - evaluate_script
  - list_network_requests, get_network_request
  - list_console_messages, get_console_message
  - click, fill, fill_form, type_text, press_key, hover, drag
  - take_memory_snapshot
  - emulate, resize_page
  - wait_for, handle_dialog, upload_file
""")

def main():
    """Run all test cases"""
    print("="*60)
    print("CHROME DEVTOOLS MCP TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Target Website: https://packagedagile.com")
    print("="*60)
    
    results = []
    
    # Run all test cases
    results.append(test_mcp_server_connection())
    results.append(test_navigate_and_screenshot())
    results.append(test_performance_audit())
    results.append(test_lighthouse_audit())
    results.append(test_network_monitoring())
    results.append(test_javascript_execution())
    results.append(test_form_interaction())
    results.append(test_multi_page_navigation())
    results.append(test_memory_analysis())
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()
