"""
Test Case 7: Lighthouse Audit
Comprehensive Lighthouse audit with network monitoring and screenshot capture
Target: https://packagedagile.com
"""

from playwright.sync_api import sync_playwright
import json
import subprocess
import os
from datetime import datetime
from collections import defaultdict

def run_lighthouse_audit():
    """Run Lighthouse audit using Node.js lighthouse CLI"""
    url = 'https://packagedagile.com'
    output_path = 'C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test7_lighthouse_raw.json'
    
    try:
        # Use full path to lighthouse on Windows
        lighthouse_cmd = 'C:/Users/DaveWitkin/AppData/Roaming/npm/lighthouse.cmd'
        
        result = subprocess.run(
            [lighthouse_cmd, url, 
             '--output=json',
             '--output-path=' + output_path,
             '--chrome-flags=--headless --no-sandbox --disable-gpu',
             '--only-categories=performance,accessibility,best-practices,seo',
             '--preset=desktop',
             '--quiet'],
            capture_output=True,
            text=True,
            timeout=120,
            shell=False
        )
        
        if result.returncode == 0 or os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Lighthouse stderr: {result.stderr}")
            return None
    except Exception as e:
        print(f"Lighthouse error: {e}")
        return None

def test_lighthouse_audit():
    # Storage for network data
    network_requests = []
    console_messages = []
    
    print("="*70)
    print("TEST CASE 7: LIGHTHOUSE AUDIT")
    print("="*70)
    print(f"Target: https://packagedagile.com")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Capture console messages
        def handle_console(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text,
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
            for req in network_requests:
                if req['url'] == response.url and 'response' not in req:
                    req['response'] = {
                        'status': response.status,
                        'status_text': response.status_text,
                        'headers': dict(response.headers)
                    }
                    break
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # Step 1: Navigate to page
        print("\n[1/4] Navigating to https://packagedagile.com")
        page.goto('https://packagedagile.com', wait_until='networkidle')
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(2000)  # Wait for any late requests
        print("  [OK] Page loaded successfully")
        
        # Step 2: Run Lighthouse audit
        print("\n[2/4] Running Lighthouse audit (this may take 30-60 seconds)...")
        lighthouse_result = run_lighthouse_audit()
        
        # Step 3: Take screenshot
        print("\n[3/4] Taking screenshot")
        screenshot_path = 'C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test7_lighthouse.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"  [OK] Screenshot saved to: {screenshot_path}")
        
        # Step 4: List network requests
        print("\n[4/4] Analyzing network requests")
        print(f"  Total network requests: {len(network_requests)}")
        
        # Breakdown by resource type
        resource_types = defaultdict(int)
        for req in network_requests:
            resource_types[req['resource_type']] += 1
        
        browser.close()
    
    # Generate Report
    print("\n" + "="*70)
    print("LIGHTHOUSE AUDIT REPORT")
    print("="*70)
    
    # Initialize variables
    performance = accessibility = best_practices = seo = 0
    lcp = fid = cls = fcp = tti = tbt = si = {}
    
    # Lighthouse Scores
    print("\n[LIGHTHOUSE SCORES (0-100)]")
    print("-" * 40)
    
    if lighthouse_result and 'categories' in lighthouse_result:
        categories = lighthouse_result['categories']
        
        performance = categories.get('performance', {}).get('score', 0) * 100
        accessibility = categories.get('accessibility', {}).get('score', 0) * 100
        best_practices = categories.get('best-practices', {}).get('score', 0) * 100
        seo = categories.get('seo', {}).get('score', 0) * 100
        
        print(f"  Performance:    {performance:.0f}/100 {'[PASS]' if performance >= 90 else '[WARN]' if performance >= 50 else '[FAIL]'}")
        print(f"  Accessibility:  {accessibility:.0f}/100 {'[PASS]' if accessibility >= 90 else '[WARN]' if accessibility >= 50 else '[FAIL]'}")
        print(f"  Best Practices: {best_practices:.0f}/100 {'[PASS]' if best_practices >= 90 else '[WARN]' if best_practices >= 50 else '[FAIL]'}")
        print(f"  SEO:            {seo:.0f}/100 {'[PASS]' if seo >= 90 else '[WARN]' if seo >= 50 else '[FAIL]'}")
        
        # Core Web Vitals
        print("\n[CORE WEB VITALS]")
        print("-" * 40)
        audits = lighthouse_result.get('audits', {})
        
        lcp = audits.get('largest-contentful-paint', {})
        fid = audits.get('max-potential-fid', {})
        cls = audits.get('cumulative-layout-shift', {})
        fcp = audits.get('first-contentful-paint', {})
        tti = audits.get('interactive', {})
        tbt = audits.get('total-blocking-time', {})
        si = audits.get('speed-index', {})
        
        print(f"  Largest Contentful Paint (LCP): {lcp.get('displayValue', 'N/A')}")
        print(f"  First Input Delay (FID):        {fid.get('displayValue', 'N/A')}")
        print(f"  Cumulative Layout Shift (CLS):  {cls.get('displayValue', 'N/A')}")
        print(f"  First Contentful Paint (FCP):   {fcp.get('displayValue', 'N/A')}")
        print(f"  Time to Interactive (TTI):      {tti.get('displayValue', 'N/A')}")
        print(f"  Total Blocking Time (TBT):      {tbt.get('displayValue', 'N/A')}")
        print(f"  Speed Index (SI):               {si.get('displayValue', 'N/A')}")
        
        # Key Audit Findings
        print("\n[KEY AUDIT FINDINGS]")
        print("-" * 40)
        
        # Check for common issues
        issues_found = []
        
        if 'render-blocking-resources' in audits:
            rbr = audits['render-blocking-resources']
            if rbr.get('score') is not None and rbr.get('score') < 1:
                items = rbr.get('details', {}).get('items', [])
                issues_found.append(f"Render-blocking resources: {len(items)} files")
        
        if 'unused-css-rules' in audits:
            ucr = audits['unused-css-rules']
            if ucr.get('score') is not None and ucr.get('score') < 1:
                issues_found.append("Unused CSS rules detected")
        
        if 'unused-javascript' in audits:
            uj = audits['unused-javascript']
            if uj.get('score') is not None and uj.get('score') < 1:
                issues_found.append("Unused JavaScript detected")
        
        if 'modern-image-formats' in audits:
            mi = audits['modern-image-formats']
            if mi.get('score') is not None and mi.get('score') < 1:
                items = mi.get('details', {}).get('items', [])
                issues_found.append(f"Images not in modern format: {len(items)} images")
        
        if 'efficiently-encode-images' in audits:
            eei = audits['efficiently-encode-images']
            if eei.get('score') is not None and eei.get('score') < 1:
                issues_found.append("Images could be better optimized")
        
        if 'server-response-time' in audits:
            srt = audits['server-response-time']
            if srt.get('score') is not None and srt.get('score') < 1:
                issues_found.append(f"Slow server response time: {srt.get('displayValue', 'N/A')}")
        
        if issues_found:
            for issue in issues_found[:10]:
                print(f"  [WARN] {issue}")
        else:
            print("  [OK] No major issues detected")
        
        # Accessibility findings
        print("\n[ACCESSIBILITY FINDINGS]")
        print("-" * 40)
        
        a11y_issues = []
        if 'accessibility' in categories:
            a11y_audits = categories['accessibility'].get('auditRefs', [])
            for ref in a11y_audits:
                audit = audits.get(ref['id'], {})
                if audit.get('score') == 0 and audit.get('details', {}).get('items'):
                    items = audit.get('details', {}).get('items', [])
                    if items:
                        a11y_issues.append(f"{audit.get('title', ref['id'])}: {len(items)} issues")
        
        if a11y_issues:
            for issue in a11y_issues[:5]:
                print(f"  [WARN] {issue}")
        else:
            print("  [OK] No accessibility issues detected")
        
    else:
        print("  [WARN] Could not retrieve Lighthouse scores")
        print("  Note: Lighthouse CLI may not be installed. Run: npm install -g lighthouse")
    
    # Network Analysis
    print("\n[NETWORK ANALYSIS]")
    print("-" * 40)
    print(f"  Total Requests: {len(network_requests)}")
    
    # Resource breakdown
    print("\n  Resource Breakdown:")
    for res_type, count in sorted(resource_types.items(), key=lambda x: -x[1]):
        print(f"    - {res_type}: {count}")
    
    # Console messages
    errors = [m for m in console_messages if m['type'] == 'error']
    warnings = [m for m in console_messages if m['type'] == 'warning']
    
    print("\n[CONSOLE MESSAGES]")
    print("-" * 40)
    print(f"  Errors:   {len(errors)} {'[FAIL]' if errors else '[OK]'}")
    print(f"  Warnings: {len(warnings)} {'[WARN]' if warnings else '[OK]'}")
    
    if errors:
        print("\n  Error Details (first 3):")
        for err in errors[:3]:
            print(f"    - {err['text'][:100]}")
    
    # Critical Issues Summary
    print("\n[CRITICAL ISSUES SUMMARY]")
    print("-" * 40)
    critical_issues = []
    
    if lighthouse_result:
        if performance < 50:
            critical_issues.append(f"Performance score critically low ({performance:.0f}/100)")
        if accessibility < 50:
            critical_issues.append(f"Accessibility score critically low ({accessibility:.0f}/100)")
        if best_practices < 50:
            critical_issues.append(f"Best Practices score critically low ({best_practices:.0f}/100)")
        if seo < 50:
            critical_issues.append(f"SEO score critically low ({seo:.0f}/100)")
    
    if len(errors) > 5:
        critical_issues.append(f"High number of console errors ({len(errors)})")
    
    if critical_issues:
        for issue in critical_issues:
            print(f"  [FAIL] {issue}")
    else:
        print("  [OK] No critical issues identified")
    
    # Save comprehensive report
    report = {
        'timestamp': datetime.now().isoformat(),
        'url': 'https://packagedagile.com',
        'lighthouse': {
            'scores': {
                'performance': performance if lighthouse_result else None,
                'accessibility': accessibility if lighthouse_result else None,
                'best_practices': best_practices if lighthouse_result else None,
                'seo': seo if lighthouse_result else None
            },
            'core_web_vitals': {
                'lcp': lcp.get('displayValue') if lighthouse_result else None,
                'fid': fid.get('displayValue') if lighthouse_result else None,
                'cls': cls.get('displayValue') if lighthouse_result else None,
                'fcp': fcp.get('displayValue') if lighthouse_result else None,
                'tti': tti.get('displayValue') if lighthouse_result else None
            } if lighthouse_result else None
        },
        'network': {
            'total_requests': len(network_requests),
            'resource_breakdown': dict(resource_types)
        },
        'console': {
            'errors': len(errors),
            'warnings': len(warnings),
            'total': len(console_messages)
        },
        'screenshot': screenshot_path,
        'critical_issues': critical_issues
    }
    
    report_path = 'C:/development/opencode/.conductor/tracks/20260321-control-chrome-mcp-fix/test7_lighthouse_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*70)
    print("FILES GENERATED")
    print("="*70)
    print(f"  Screenshot: {screenshot_path}")
    print(f"  Report:     {report_path}")
    print("="*70)
    
    return report

if __name__ == '__main__':
    test_lighthouse_audit()
