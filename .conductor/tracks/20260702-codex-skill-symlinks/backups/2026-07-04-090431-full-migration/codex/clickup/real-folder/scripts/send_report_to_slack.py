import sys
import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Resolve the external repo via the shared ClickUp skill helper.
from common import setup_path
repo_path = setup_path()

try:
    from scripts.prioritization_helpers import detect_output_format
except ImportError:
    print("⚠️ Could not import prioritization_helpers. Slack report may not find correct file.")
    detect_output_format = None

def get_slack_user_id_by_email(token, email):
    """Lookup Slack User ID by email."""
    url = "https://slack.com/api/users.lookupByEmail"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"email": email}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        if data.get("ok"):
            return data["user"]["id"]
        else:
            print(f"⚠️ Could not find user by email {email}: {data.get('error')}")
            return None
    except Exception as e:
        print(f"❌ Error looking up user: {e}")
        return None

def send_prioritization_to_slack(token, channel_id=None):
    # Find the latest prioritization report based on modification time
    # (Since we now use timestamps in filenames, relying on generic detection might be safer)
    exports_dir = (Path(repo_path) / "exports") if repo_path else Path("exports")
    
    # We want the absolute latest markdown file in the exports folder
    files = list(exports_dir.glob("prioritization_shortlist_*.md"))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_file = files[0] if files else None
    
    if not latest_file:
        print("❌ No prioritization report found to send.")
        return

    print(f"📄 Found report: {latest_file.name}")
    content = latest_file.read_text(encoding="utf-8")
    
    # Send message via API
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # If channel_id is not provided, try env var, then lookup
    if not channel_id:
        channel_id = os.getenv("SLACK_DEFAULT_CHANNEL")
    
    if not channel_id:
        print("🔍 Looking up Dave Witkin's Slack ID...")
        email = "dave.witkin@packagedagile.com" 
        channel_id = get_slack_user_id_by_email(token, email)
        
        if not channel_id:
            print("❌ Could not determine destination channel/user.")
            return

    print(f"📨 Sending to Slack Channel/User ID: {channel_id}")
    
    payload = {
        "channel": channel_id,
        "text": f"🚀 *Daily Prioritization Report*\n\n{content}",
        "unfurl_links": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if data.get("ok"):
            print("✅ Report sent to Slack successfully!")
        else:
            print(f"❌ Failed to send to Slack: {data.get('error')}")
    except Exception as e:
        print(f"❌ Error sending to Slack: {e}")

if __name__ == "__main__":
    if repo_path:
        load_dotenv(Path(repo_path) / ".env")
    
    token = os.getenv("SLACK_BOT_TOKEN")
    
    if not token:
        print("❌ SLACK_BOT_TOKEN not found in .env. Skipping Slack send.")
        sys.exit(0)
        
    send_prioritization_to_slack(token)
