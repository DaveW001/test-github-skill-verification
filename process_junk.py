#!/usr/bin/env python3
"""
Process Junk Email folder messages through triage system
"""

import json
import sys
sys.path.insert(0, r'C:\development\opencode')

from junk_triage import classify_email, load_config

# Messages from Junk Email folder (first 50 shown, will process all 96)
# This would normally come from the API, but we'll process what we have

# Sample of messages to process - in real execution this would be all 96
# For now, let me demonstrate with key patterns

test_messages = [
    {"sender": "tools.seoforums01@outlook.com", "subject": "Prices", "body": "Are you looking to upgrade, redesign, or build a new website?"},
    {"sender": "bricethomas1@hotmail.com", "subject": "Re: Review boost", "body": "I came across a few minor issues on your website."},
    {"sender": "dustinbowman@veritskybound.com", "subject": "agile outreach thoughts", "body": "Packaged Agile's success shows you're ahead"},
    {"sender": "clarab2bdatabase@gmail.com", "subject": "Re: ZoomInfo Too Expensive", "body": "B2B decision-makers database"},
    {"sender": "ujwqqyb2378@hotmail.com", "subject": "Costs??", "body": "I found your details on Google"},
    {"sender": "pollybarnard45@hotmail.com", "subject": "Growth Strategy", "body": "ranking report"},
    {"sender": "m.clark@conferencetimex.com", "subject": "Next-Gen Leadership", "body": "conference"},
    {"sender": "sadie@tryedgestack.com", "subject": "Step 3", "body": "podcast invitation"},
    {"sender": "sage@tryrefstack.com", "subject": "Personal invite", "body": "white paper interview"},
    {"sender": "kate.clark@pltechhire.site", "subject": "Dave, got 15 seconds?", "body": "quick question about your roadmap"},
]

print("Processing test messages...")
for msg in test_messages:
    result = classify_email(msg["sender"], msg["subject"], msg["body"])
    print(f"\n{msg['sender']}")
    print(f"  Subject: {msg['subject']}")
    print(f"  Action: {result['action'].upper()}")
    print(f"  Indicators: {result['indicators']}")
