#!/usr/bin/env python3
"""
Move Junk Emails to Deleted Items using Microsoft Graph API.

This script provides an alternative to the ms365_move-mail-message tool
for environments where that specific tool is not available.

Usage:
    python move_junk_via_graph.py --token YOUR_ACCESS_TOKEN
    
Or with a token file:
    python move_junk_via_graph.py --token-file ~/.msgraph_token
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Try to import requests, provide fallback instructions
try:
    import requests
except ImportError:
    print("ERROR: requests library not installed.")
    print("Install with: pip install requests")
    sys.exit(1)


# Configuration
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

# Folder IDs (from workflow documentation)
JUNK_EMAIL_FOLDER_ID = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAASHvdAAA="
DELETED_ITEMS_FOLDER_ID = "AAMkAGU4NTQ1NTVkLThiZGUtNDYwMC05N2FjLWIzZmU1Y2I5MjVjZQAuAAAAAAA8K5fYAynyTot_fsDj7yapAQD9YgbCLDoDRqbmmlLG6VOsAAAAAAEKAAA="


def load_message_ids(filepath: str = "delete_ids.txt") -> list:
    """Load message IDs from file."""
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: Message IDs file not found: {filepath}")
        print("Create this file with one message ID per line.")
        sys.exit(1)
    
    with open(path, 'r') as f:
        ids = [line.strip() for line in f if line.strip()]
    
    return ids


def move_message(access_token: str, user_id: str, message_id: str, 
                 destination_folder_id: str, verbose: bool = False) -> bool:
    """
    Move a single message using Microsoft Graph API.
    
    Returns True on success, False on failure.
    """
    url = f"{GRAPH_API_BASE}/users/{user_id}/messages/{message_id}/move"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "destinationId": destination_folder_id
    }
    
    try:
        response = requests.post(url, json=body, headers=headers)
        
        if response.status_code == 201:
            if verbose:
                print(f"✓ Moved: {message_id[-20:]}")
            return True
        elif response.status_code == 429:
            # Throttled
            retry_after = int(response.headers.get('Retry-After', 5))
            if verbose:
                print(f"⚠ Throttled. Waiting {retry_after}s...")
            time.sleep(retry_after)
            return False  # Caller should retry
        elif response.status_code == 404:
            if verbose:
                print(f"✗ Not found (already moved?): {message_id[-20:]}")
            return True  # Consider this success - message is not in source
        else:
            if verbose:
                print(f"✗ Error {response.status_code}: {message_id[-20:]}")
                print(f"   {response.text[:100]}")
            return False
            
    except requests.exceptions.RequestException as e:
        if verbose:
            print(f"✗ Request failed: {e}")
        return False


def process_batch(access_token: str, user_id: str, message_ids: list,
                  delay_ms: int = 500, max_retries: int = 3) -> dict:
    """
    Process a batch of message moves with throttling protection.
    
    Returns statistics dict with success/failure counts.
    """
    stats = {
        'total': len(message_ids),
        'success': 0,
        'failed': 0,
        'throttled': 0
    }
    
    print(f"\nProcessing {len(message_ids)} messages...")
    print(f"Delay between requests: {delay_ms}ms")
    print(f"Max retries per message: {max_retries}")
    print("-" * 60)
    
    for i, msg_id in enumerate(message_ids, 1):
        print(f"[{i:3d}/{len(message_ids)}] ", end="", flush=True)
        
        success = False
        retries = 0
        
        while not success and retries <= max_retries:
            result = move_message(
                access_token, user_id, msg_id, 
                DELETED_ITEMS_FOLDER_ID, verbose=False
            )
            
            if result:
                success = True
                stats['success'] += 1
                print(f"✓ {msg_id[-20:]}")
            else:
                retries += 1
                if retries <= max_retries:
                    print(f"R", end="", flush=True)  # Retry indicator
                    time.sleep(5)  # Wait before retry
                else:
                    stats['failed'] += 1
                    print(f"✗ FAILED: {msg_id[-20:]}")
        
        # Delay between messages to avoid throttling
        if i < len(message_ids):
            time.sleep(delay_ms / 1000)
    
    return stats


def get_access_token_interactive() -> str:
    """
    Guide user through getting an access token.
    
    This is a placeholder - in production, use proper authentication flow.
    """
    print("""
To use this script, you need a Microsoft Graph access token with Mail.ReadWrite permissions.

Options to obtain a token:

1. Azure AD Portal:
   - Go to https://portal.azure.com
   - Navigate to Azure Active Directory > App registrations
   - Create or select an app with Mail.ReadWrite permission
   - Generate a client secret or use device code flow

2. Microsoft Graph Explorer (for testing):
   - Go to https://developer.microsoft.com/en-us/graph/graph-explorer
   - Sign in and consent to Mail.ReadWrite
   - Copy the access token from the request headers

3. PowerShell (if you have the Graph module):
   Connect-MgGraph -Scopes "Mail.ReadWrite"
   (Get-MgContext).AuthToken

Enter your access token below (or provide via --token argument):
""")
    
    token = input("Access token: ").strip()
    return token


def main():
    parser = argparse.ArgumentParser(
        description="Move junk emails to Deleted Items via Microsoft Graph API"
    )
    parser.add_argument(
        "--token", 
        help="Microsoft Graph access token"
    )
    parser.add_argument(
        "--token-file",
        help="Path to file containing access token"
    )
    parser.add_argument(
        "--user-id",
        default="dave.witkin@packagedagile.com",
        help="User ID (email address)"
    )
    parser.add_argument(
        "--message-ids-file",
        default="delete_ids.txt",
        help="File containing message IDs to move"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=500,
        help="Delay between requests in milliseconds (default: 500)"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retries per message (default: 3)"
    )
    parser.add_argument(
        "--remaining-only",
        action="store_true",
        help="Only process the remaining 19 messages (lines 24-42)"
    )
    
    args = parser.parse_args()
    
    # Get access token
    access_token = None
    if args.token:
        access_token = args.token
    elif args.token_file:
        token_path = Path(args.token_file)
        if token_path.exists():
            access_token = token_path.read_text().strip()
        else:
            print(f"ERROR: Token file not found: {args.token_file}")
            sys.exit(1)
    else:
        access_token = get_access_token_interactive()
    
    if not access_token:
        print("ERROR: No access token provided")
        sys.exit(1)
    
    # Load message IDs
    all_message_ids = load_message_ids(args.message_ids_file)
    
    if args.remaining_only:
        # Process only lines 24-42 (remaining 19 messages)
        message_ids = all_message_ids[23:42]  # 0-indexed: 23-41 inclusive
        print(f"Processing remaining 19 messages (indices 23-41)")
    else:
        message_ids = all_message_ids
        print(f"Processing all {len(message_ids)} messages")
    
    # Process the batch
    stats = process_batch(
        access_token, args.user_id, message_ids,
        delay_ms=args.delay, max_retries=args.max_retries
    )
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total messages:   {stats['total']}")
    print(f"Successfully moved: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"Failed:           {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    
    if stats['failed'] > 0:
        print("\nSome messages failed to move. You may need to:")
        print("1. Check your access token hasn't expired")
        print("2. Verify the messages still exist in Junk Email")
        print("3. Wait a few minutes and retry (throttling)")
        sys.exit(1)
    else:
        print("\n✓ All messages moved successfully!")
        print(f"\nNext step: Verify Junk Email folder is empty in Outlook")
        sys.exit(0)


if __name__ == "__main__":
    main()
