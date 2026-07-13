import sys
import os
import argparse
from pathlib import Path

# Resolve the external repo via the shared ClickUp skill helper.
from common import setup_path
repo_path = setup_path()

try:
    from run_prioritization import main as run_prioritization_main
    from scripts.prioritization_helpers import detect_output_format
except ImportError as e:
    print(f"Error importing prioritization scripts: {e}")
    sys.exit(1)

def print_clickable_link(exports_dir):
    """Print a clickable file URI for the latest report."""
    has_format, latest_file = detect_output_format(exports_dir)
    if latest_file:
        uri = latest_file.resolve().as_uri()
        print("\n" + "="*50)
        print("🔗 OPEN REPORT:")
        print(f"{uri}")
        print("="*50 + "\n")
    else:
        print("⚠️  Could not locate generated file for linking.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run prioritization and optionally send to Slack.")
    parser.add_argument("--slack", action="store_true", help="Send the report to Slack.")
    parser.add_argument("--non-interactive", action="store_true", help="Skip cache prompts (passed to logic).")
    parser.add_argument("--business-only", action="store_true", help="Exclude Home space tasks.")
    args = parser.parse_args()

    print("🚀 Running prioritization logic...")
    
    # run_prioritization.py reads arguments directly from sys.argv using argparse.
    # Since we are invoking its main() method in the same process, we rely on sys.argv being populated.
    # However, if we pass args to this script, they are already in sys.argv!
    # So calling run_prioritization_main() should just work as it parses the same sys.argv.
    
    success = run_prioritization_main()
    
    if success:
        # Always print the clickable link
        print_clickable_link((Path(repo_path) / "exports") if repo_path else Path("exports"))

        if args.slack:
            print("\n📨 Attempting to send report to Slack...")
            import subprocess
            slack_script = os.path.join(os.path.dirname(__file__), "send_report_to_slack.py")
            if os.path.exists(slack_script):
                subprocess.run([sys.executable, slack_script])
            else:
                print(f"⚠️ Slack script not found at {slack_script}")
        else:
            print("\nℹ️  Slack send skipped. Use --slack to send.")
