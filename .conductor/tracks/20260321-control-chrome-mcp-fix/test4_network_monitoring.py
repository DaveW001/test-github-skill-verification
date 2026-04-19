"""
Test Case 4: Network Request Monitoring
Monitors all network requests on packagedagile.com and generates a report
"""

from playwright.sync_api import sync_playwright
import json
from datetime import datetime
from collections import defaultdict

def test_network_monitoring():
    # Storage for network data
    network_requests = []
    console_messages = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Capture console messages
        def handle_console(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text,
                'location': msg.location if hasattr(msg, 'location') else None,
                'timestamp': datetime.now().isoformat()
            })
        
        page.on('console', handle_console)
        
        # Capture network requests
        def handle_request(request):
            network_requests.append({
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type,
                'headers': dict(request.headers),
                'timestamp': datetime.now().isoformat()
            })
        
        def handle_response(response):
            # Find matching request and add response data
            for req in network_requests:
                if req['url'] == response.url and 'response' not in req:
                    req['response'] = {
                        'status': response.status,
                        'status_text': response.status_text,
                        'headers': dict(response.headers),
                        'size': None  # Will be populated if possible
                    }
                    break
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        print("Step 1: Navigating to https://packagedagile.com")
        page.goto('https://packagedagile.com', wait_until='networkidle')
        
        print("Step 2: Waiting for page to fully load")
        page.wait_for_load_state('networkidle')
        
        # Wait a bit more for any late requests
        page.wait_for_timeout(2000)
        
        print("Step 3: Capturing final network state")
        
        # Find main document request
        main_doc_request = None
        for req in network_requests:
            if req['url'] == 'https://packagedagile.com/' or req['url'].endswith('packagedagile.com/'):
                main_doc_request = req
                break
        
        # Take screenshot
        print("Step 4: Taking screenshot")
        page.screenshot(path='C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test4_network.png', full_page=True)
        
        # Generate Report
        print("\n" + "="*70)
        print("TEST CASE 4: NETWORK REQUEST MONITORING REPORT")
        print("="*70)
        
        print(f"\nTotal Network Requests: {len(network_requests)}")
        
        # Breakdown by resource type
        resource_types = defaultdict(int)
        for req in network_requests:
            resource_types[req['resource_type']] += 1
        
        print("\nBreakdown by Resource Type:")
        for res_type, count in sorted(resource_types.items(), key=lambda x: -x[1]):
            print(f"  - {res_type}: {count}")
        
        # Main document request details
        print("\nMain Document Request:")
        if main_doc_request:
            print(f"  URL: {main_doc_request['url']}")
            print(f"  Method: {main_doc_request['method']}")
            if 'response' in main_doc_request:
                resp = main_doc_request['response']
                print(f"  Status: {resp['status']} {resp['status_text']}")
                print(f"  Headers: {json.dumps(resp['headers'], indent=4)[:500]}...")
        else:
            print("  Main document request not found in captured requests")
            print(f"  Available URLs: {[r['url'][:80] + '...' for r in network_requests[:5]]}")
        
        # Console messages
        print("\nConsole Messages:")
        errors = [m for m in console_messages if m['type'] == 'error']
        warnings = [m for m in console_messages if m['type'] == 'warning']
        
        if errors:
            print(f"  ERRORS ({len(errors)}):")
            for err in errors[:5]:
                print(f"    - {err['text'][:150]}")
        else:
            print("  [OK] No console errors")
        
        if warnings:
            print(f"  WARNINGS ({len(warnings)}):")
            for warn in warnings[:5]:
                print(f"    - {warn['text'][:150]}")
        else:
            print("  [OK] No console warnings")
        
        print(f"\nTotal console messages: {len(console_messages)}")
        
        # Summary of resources
        print("\nResource Summary:")
        js_files = [r for r in network_requests if r['resource_type'] == 'script']
        css_files = [r for r in network_requests if r['resource_type'] == 'stylesheet']
        images = [r for r in network_requests if r['resource_type'] == 'image']
        fonts = [r for r in network_requests if r['resource_type'] == 'font']
        xhr = [r for r in network_requests if r['resource_type'] == 'xhr']
        fetch = [r for r in network_requests if r['resource_type'] == 'fetch']
        
        print(f"  - JavaScript files: {len(js_files)}")
        print(f"  - CSS files: {len(css_files)}")
        print(f"  - Images: {len(images)}")
        print(f"  - Fonts: {len(fonts)}")
        print(f"  - XHR requests: {len(xhr)}")
        print(f"  - Fetch requests: {len(fetch)}")
        print(f"  - Document: {len([r for r in network_requests if r['resource_type'] == 'document'])}")
        print(f"  - Other: {len(network_requests) - len(js_files) - len(css_files) - len(images) - len(fonts) - len(xhr) - len(fetch)}")
        
        print("\n" + "="*70)
        print("Screenshot saved to: C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test4_network.png")
        print("="*70)
        
        # Save detailed report to JSON
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'url': 'https://packagedagile.com',
            'total_requests': len(network_requests),
            'resource_breakdown': dict(resource_types),
            'main_document': main_doc_request,
            'console_messages': console_messages,
            'errors_count': len(errors),
            'warnings_count': len(warnings)
        }
        
        report_path = 'C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test4_network_report.json'
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        print(f"\nDetailed report saved to: {report_path}")
        
        browser.close()
        
        return report_data

if __name__ == '__main__':
    test_network_monitoring()
