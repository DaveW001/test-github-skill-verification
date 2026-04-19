#!/usr/bin/env python3
"""
Junk Mail Triage Script
Automated detection and classification of junk emails based on configurable indicators.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Load configuration
CONFIG_PATH = Path(__file__).parent / "config" / "junk-indicators.json"


def load_config() -> Dict:
    """Load junk indicators configuration."""
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def extract_domain(email: str) -> str:
    """Extract domain from email address."""
    if '@' not in email:
        return ""
    return email.split('@')[1].lower()


def extract_local_part(email: str) -> str:
    """Extract local part (username) from email address."""
    if '@' not in email:
        return email.lower()
    return email.split('@')[0].lower()


def is_consumer_provider(domain: str, consumer_providers: List[str]) -> bool:
    """Check if domain is a consumer email provider."""
    return domain.lower() in [p.lower() for p in consumer_providers]


def check_local_part_patterns(email: str, patterns: List[str]) -> Tuple[bool, str]:
    """Check if email local part matches junk patterns.
    
    Returns: (is_match, matched_pattern)
    """
    local = extract_local_part(email)
    
    for pattern in patterns:
        try:
            if re.search(pattern, local, re.IGNORECASE):
                return True, pattern
        except re.error:
            continue
    
    return False, ""


def check_subject_patterns(subject: str, keywords: List[str]) -> Tuple[bool, str]:
    """Check if subject matches junk keywords.
    
    Returns: (is_match, matched_keyword)
    """
    subject_lower = subject.lower()
    
    for keyword in keywords:
        if keyword.lower() in subject_lower:
            return True, keyword
    
    return False, ""


def check_body_patterns(body: str, phrases: List[str]) -> Tuple[bool, str]:
    """Check if email body matches junk phrases.
    
    Returns: (is_match, matched_phrase)
    """
    body_lower = body.lower()
    
    for phrase in phrases:
        if phrase.lower() in body_lower:
            return True, phrase
    
    return False, ""


def classify_email(
    sender: str,
    subject: str = "",
    body: str = "",
    config: Dict = None
) -> Dict:
    """Classify an email based on junk indicators.
    
    Returns classification result with:
    - action: 'delete', 'review', or 'keep'
    - reason: explanation of classification
    - confidence: 'high', 'medium', or 'low'
    """
    if config is None:
        config = load_config()
    
    domain = extract_domain(sender)
    local = extract_local_part(sender)
    
    # Check safe domains first (whitelist)
    if domain.lower() in [d.lower() for d in config.get('safe_domains', [])]:
        return {
            'action': 'keep',
            'reason': f'Domain {domain} is in safe list',
            'confidence': 'high',
            'indicators': []
        }
    
    indicators = []
    
    # Check if domain is in junk list
    if domain.lower() in [d.lower() for d in config.get('junk_domains', [])]:
        indicators.append(f'Junk domain: {domain}')
    
    # Check local part patterns for ALL domains (including consumer providers)
    is_pattern_match, matched_pattern = check_local_part_patterns(
        sender, config.get('junk_patterns', {}).get('local_part', [])
    )
    if is_pattern_match:
        indicators.append(f'Suspicious username pattern: {matched_pattern}')
    
    # Check subject patterns
    is_subject_match, matched_keyword = check_subject_patterns(
        subject, config.get('junk_patterns', {}).get('subject_keywords', [])
    )
    if is_subject_match:
        indicators.append(f'Subject keyword: {matched_keyword}')
    
    # Check body patterns
    is_body_match, matched_phrase = check_body_patterns(
        body, config.get('junk_patterns', {}).get('body_phrases', [])
    )
    if is_body_match:
        indicators.append(f'Body phrase: {matched_phrase}')
    
    # Determine action based on indicators
    if len(indicators) >= 2:
        return {
            'action': 'delete',
            'reason': f'Multiple indicators detected ({len(indicators)})',
            'confidence': 'high',
            'indicators': indicators
        }
    elif len(indicators) == 1:
        # Single indicator - review unless it's a known junk domain
        if 'Junk domain' in indicators[0]:
            return {
                'action': 'delete',
                'reason': 'Known junk domain',
                'confidence': 'high',
                'indicators': indicators
            }
        else:
            return {
                'action': 'review',
                'reason': 'Single suspicious indicator',
                'confidence': 'medium',
                'indicators': indicators
            }
    else:
        return {
            'action': 'keep',
            'reason': 'No junk indicators detected',
            'confidence': 'high',
            'indicators': []
        }


def triage_batch(emails: List[Dict]) -> Dict:
    """Triage a batch of emails.
    
    Args:
        emails: List of dicts with 'sender', 'subject', 'body' keys
    
    Returns:
        Summary dict with counts and detailed results
    """
    config = load_config()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total': len(emails),
        'delete': [],
        'review': [],
        'keep': [],
        'details': []
    }
    
    for email in emails:
        classification = classify_email(
            email.get('sender', ''),
            email.get('subject', ''),
            email.get('body', ''),
            config
        )
        
        result = {
            'sender': email.get('sender'),
            'subject': email.get('subject', '')[:80],
            'classification': classification
        }
        
        results['details'].append(result)
        results[classification['action']].append(result)
    
    return results


def print_report(results: Dict):
    """Print formatted triage report."""
    print("=" * 80)
    print("JUNK MAIL TRIAGE REPORT")
    print("=" * 80)
    print(f"Timestamp: {results['timestamp']}")
    print(f"Total emails processed: {results['total']}")
    print()
    print(f"DELETE NOW: {len(results['delete'])} ({len(results['delete'])/results['total']*100:.1f}%)")
    print(f"REVIEW:     {len(results['review'])} ({len(results['review'])/results['total']*100:.1f}%)")
    print(f"KEEP:       {len(results['keep'])} ({len(results['keep'])/results['total']*100:.1f}%)")
    print()
    
    if results['delete']:
        print("-" * 40)
        print("DELETE RECOMMENDATIONS:")
        print("-" * 40)
        for item in results['delete']:
            c = item['classification']
            print(f"  {item['sender']}")
            print(f"    Subject: {item['subject'][:60]}...")
            print(f"    Reason: {c['reason']}")
            print(f"    Indicators: {', '.join(c['indicators'])}")
            print()
    
    if results['review']:
        print("-" * 40)
        print("REVIEW RECOMMENDATIONS:")
        print("-" * 40)
        for item in results['review']:
            c = item['classification']
            print(f"  {item['sender']}")
            print(f"    Subject: {item['subject'][:60]}...")
            print(f"    Reason: {c['reason']}")
            print(f"    Indicators: {', '.join(c['indicators'])}")
            print()


def main():
    """Main entry point for command-line usage."""
    import sys
    
    # Example: Test with a few emails
    test_emails = [
        {
            'sender': 'clarab2bdatabase@gmail.com',
            'subject': 'B2B Database for your marketing needs',
            'body': 'I came across your profile and wanted to reach out.'
        },
        {
            'sender': 'noreply@myskylight.com',
            'subject': 'Your account update',
            'body': 'Here is your monthly statement.'
        }
    ]
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        results = triage_batch(test_emails)
        print_report(results)
    else:
        print("Junk Triage Script v1.0")
        print("Usage:")
        print("  python junk_triage.py --test    # Run test examples")
        print()
        print("Import this module to use programmatically:")
        print("  from junk_triage import classify_email, triage_batch")


if __name__ == '__main__':
    main()
