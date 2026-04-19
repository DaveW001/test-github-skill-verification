#!/usr/bin/env python3
"""
Batch delete junk emails from triage results
"""

import json
import subprocess
import sys
import time

# Deleted Items folder ID
DELETED_ITEMS_ID = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAAAAEKAAA="

# Load triage results
with open(r'C:\development\opencode\reports\junk-triage-results-20250314.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get all delete message IDs (skip first 5 which were already processed)
delete_messages = data['delete'][5:]
total = len(delete_messages)

print(f"Processing {total} remaining deletions...")
print(f"First few IDs: {[m['id'][:50] + '...' for m in delete_messages[:3]]}")

# Save IDs to a file for batch processing
with open(r'C:\development\opencode\delete_ids.txt', 'w') as f:
    for msg in delete_messages:
        f.write(msg['id'] + '\n')

print(f"Saved {total} message IDs to delete_ids.txt")
print("Ready for batch deletion")
