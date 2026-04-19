#!/usr/bin/env python3
"""Process junk email triage for 96 messages from Junk Email folder."""

import json
import sys
from datetime import datetime
from pathlib import Path

# Fix encoding issues
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add opencode directory to path
sys.path.insert(0, r'C:\development\opencode')

from junk_triage import classify_email

# Read the email data
emails_path = Path(r'C:\Users\DaveWitkin\.local\share\opencode\tool-output\tool_ceed0c7cd001pQ9r6fHLexvXWQ')
with open(emails_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

emails = data.get('value', [])

# Process each email
results = {
    'timestamp': datetime.now().isoformat(),
    'total': len(emails),
    'delete': [],
    'review': [],
    'keep': [],
    'details': []
}

for email in emails:
    sender = email.get('from', {}).get('emailAddress', {}).get('address', '')
    sender_name = email.get('from', {}).get('emailAddress', {}).get('name', '')
    subject = email.get('subject', '')
    body = email.get('bodyPreview', '')
    received = email.get('receivedDateTime', '')
    msg_id = email.get('id', '')
    
    # Classify the email
    classification = classify_email(sender, subject, body)
    
    # Store detailed result
    detail = {
        'id': msg_id,
        'receivedDateTime': received,
        'subject': subject,
        'sender_email': sender,
        'sender_name': sender_name,
        'bodyPreview': body[:200] if body else '',
        'classification': classification
    }
    
    results['details'].append(detail)
    results[classification['action']].append(detail)

# Save detailed report
report_path = Path(r'C:\development\opencode\reports\junk-triage-results-20250314.json')
report_path.parent.mkdir(parents=True, exist_ok=True)

with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Generate summary
print("=" * 80)
print("JUNK EMAIL TRIAGE SUMMARY")
print("=" * 80)
print(f"Total messages processed: {results['total']}")
print(f"Timestamp: {results['timestamp']}")
print()

# Statistics
delete_count = len(results['delete'])
review_count = len(results['review'])
keep_count = len(results['keep'])

delete_pct = delete_count / results['total'] * 100
review_pct = review_count / results['total'] * 100
keep_pct = keep_count / results['total'] * 100

print("STATISTICS BREAKDOWN")
print("-" * 40)
print(f"DELETE: {delete_count} ({delete_pct:.1f}%)")
print(f"REVIEW: {review_count} ({review_pct:.1f}%)")
print(f"KEEP:   {keep_count} ({keep_pct:.1f}%)")
print()

# DELETE recommendations
if results['delete']:
    print("=" * 40)
    print("DELETE RECOMMENDATIONS (High Confidence)")
    print("=" * 40)
    for item in results['delete']:
        c = item['classification']
        print(f"\n  {item['sender_email']}")
        print(f"  Name: {item['sender_name']}")
        print(f"  Subject: {item['subject'][:70]}..." if len(item['subject']) > 70 else f"  Subject: {item['subject']}")
        print(f"  Reason: {c['reason']}")
        print(f"  Indicators: {', '.join(c['indicators'])}")
    print()

# REVIEW recommendations
if results['review']:
    print("=" * 40)
    print("REVIEW RECOMMENDATIONS (Medium Confidence)")
    print("=" * 40)
    for item in results['review']:
        c = item['classification']
        print(f"\n  {item['sender_email']}")
        print(f"  Name: {item['sender_name']}")
        print(f"  Subject: {item['subject'][:70]}..." if len(item['subject']) > 70 else f"  Subject: {item['subject']}")
        print(f"  Reason: {c['reason']}")
        print(f"  Indicators: {', '.join(c['indicators'])}")
    print()

# KEEP recommendations
if results['keep']:
    print("=" * 40)
    print("KEEP RECOMMENDATIONS (Safe Domains)")
    print("=" * 40)
    for item in results['keep']:
        c = item['classification']
        print(f"\n  {item['sender_email']}")
        print(f"  Name: {item['sender_name']}")
        print(f"  Subject: {item['subject'][:70]}..." if len(item['subject']) > 70 else f"  Subject: {item['subject']}")
        print(f"  Reason: {c['reason']}")
    print()

# Notable patterns
print("=" * 40)
print("NOTABLE PATTERNS DETECTED")
print("=" * 40)

# Count by domain
domain_counts = {}
for item in results['details']:
    domain = item['sender_email'].split('@')[-1] if '@' in item['sender_email'] else 'unknown'
    action = item['classification']['action']
    if domain not in domain_counts:
        domain_counts[domain] = {'delete': 0, 'review': 0, 'keep': 0}
    domain_counts[domain][action] += 1

# Top suspicious domains
print("\nTop domains marked for DELETE:")
for domain, counts in sorted(domain_counts.items(), key=lambda x: x[1]['delete'], reverse=True)[:5]:
    if counts['delete'] > 0:
        print(f"  {domain}: {counts['delete']} messages")

print("\nTop domains marked for REVIEW:")
for domain, counts in sorted(domain_counts.items(), key=lambda x: x[1]['review'], reverse=True)[:5]:
    if counts['review'] > 0:
        print(f"  {domain}: {counts['review']} messages")

print(f"\n{'=' * 80}")
print(f"Full detailed report saved to:")
print(f"  {report_path}")
print(f"{'=' * 80}")
