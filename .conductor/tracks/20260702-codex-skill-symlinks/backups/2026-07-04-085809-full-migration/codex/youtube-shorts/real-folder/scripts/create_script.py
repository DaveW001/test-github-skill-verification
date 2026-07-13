import os
import sys
import json
import subprocess
import datetime
import re
import glob

# Set UTF-8 for Windows console
if sys.platform == "win32":
    try:
        getattr(sys.stdout, "reconfigure", lambda **_: None)(encoding="utf-8")
    except Exception:
        pass

# Configuration
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(SKILL_ROOT, "templates")
CONTENT_ROOT = os.environ.get("CONTENT_ROOT", r"C:\development\content-marketing")

def run_gemini(prompt):
    """Calls the Gemini CLI via stdin."""
    try:
        process = subprocess.Popen(
            ["gemini"], 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            shell=True
        )
        stdout, stderr = process.communicate(input=prompt)
        
        if process.returncode != 0:
            print(f"Error calling Gemini: {stderr}")
            return None
            
        lines = stdout.splitlines()
        clean_lines = [
            line for line in lines 
            if not line.startswith("Warning:") 
            and not line.startswith("Loading extension:")
            and not line.startswith("Server ")
            and not line.startswith("Loaded cached credentials")
        ]
        return "\n".join(clean_lines).strip()
    except Exception as e:
        print(f"Exception running Gemini: {e}")
        return None

def load_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_next_script_number(youtube_dir):
    """Finds the next available sfXX number by scanning all subfolders."""
    highest_num = 0
    if not os.path.exists(youtube_dir):
        return 1
        
    for root, dirs, files in os.walk(youtube_dir):
        for file in files:
            if file.startswith("sf") and file.endswith("-script.md"):
                try:
                    num_part = file[2:4]
                    num = int(num_part)
                    if num > highest_num:
                        highest_num = num
                except ValueError:
                    continue
    return highest_num + 1

def clean_slug_text(text):
    """Creates a slug and removes leading 'the-'."""
    slug = re.sub(r'[^a-zA-Z0-9]', '-', text).lower()
    slug = slug.strip('-')
    if slug.startswith("the-"):
        slug = slug[4:]
    return slug

def run_cio_review(script_path, folder_path):
    """Runs the CIO Review on a single script and saves review file."""
    print("\n🕵️  Running CIO Persona Review...")
    
    # Read script
    script_content = load_file(script_path)
    if not script_content:
        print("⚠️  Could not read script for review.")
        return None
    
    # Build review prompt
    review_prompt = f"""You are Claire, a skeptical Federal Agency CIO with 20+ years experience.
You oversee a $500M+ IT budget.
You hate vendor pitches, buzzwords ("leverage", "revolutionary"), and generic business advice.
You love concrete evidence (GAO, OMB), specific actions, and peer-to-peer honesty.

Review this YouTube Shorts script:

{script_content}

Score each criterion out of 10:
1. Hook (Did it stop the scroll?)
2. Credibility (Government-specific evidence?)
3. Value (Can I use this Monday?)
4. Voice (Peer-to-peer? No banned words?)
5. Story (Tension/conflict?)
6. CTA (Clear? Respectful?)

Provide your review in this exact markdown format:

## Script Review

| Criterion | Score | Notes |
|:---|:---:|:---|
| Hook | X/10 | ... |
| Credibility | X/10 | ... |
| Value | X/10 | ... |
| Voice | X/10 | ... |
| Story | X/10 | ... |
| CTA | X/10 | ... |
| **Overall** | **X/10** | **VERDICT**: PASS/REVISE/REJECT |

## Key Fixes Needed
- Fix 1 (if any)
- Fix 2 (if any)
"""
    
    review_result = run_gemini(review_prompt)
    
    if review_result:
        # Save review to timestamped file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M")
        review_filename = f"{timestamp}-critic-review.md"
        review_path = os.path.join(folder_path, review_filename)
        
        # Add header
        full_review = f"""# Critic Review

**Date**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
**Reviewer**: Claire (CIO Persona)
**Script**: {os.path.basename(script_path)}

---

{review_result}
"""
        with open(review_path, 'w', encoding='utf-8') as f:
            f.write(full_review)
        
        print(f"📝 Review saved to: {review_path}")
        return review_path
    else:
        print("⚠️  Review generation failed.")
        return None

def main():
    print("\n🎬 YouTube Shorts Script Generator (B2G Edition) 🎬")
    print("=====================================================\n")

    # Check for --skip-review flag
    skip_review = "--skip-review" in sys.argv
    if skip_review:
        sys.argv.remove("--skip-review")

    # 1. Inputs
    topic = ""
    persona = "Claire"
    framework = "Problem Solver"
    evidence = ""

    if len(sys.argv) > 1:
        topic = sys.argv[1]
        if len(sys.argv) > 2: evidence = sys.argv[2]
        print(f"Auto-mode: Topic='{topic}'")
    else:
        topic = input("Enter Topic: ").strip()
        if not topic:
            print("❌ Topic is required.")
            return
        persona = input("Target Persona [Claire]: ").strip() or "Claire"
        
        print("\nStory Frameworks:")
        print("1. Problem Solver (Contrast)")
        print("2. Listicle (Mistakes/Tips)")
        print("3. Breakdown (Discovery)")
        print("4. Case Study Analysis")
        
        fw_map = {
            "1": "Problem Solver",
            "2": "Listicle",
            "3": "Breakdown",
            "4": "Case Study Analysis"
        }
        fw_choice = input("Select Framework [1]: ").strip() or "1"
        framework = fw_map.get(fw_choice, "Problem Solver")

        evidence = input("Key Evidence: ").strip()
        if not evidence:
            evidence = "(Insert specific government statistic here)"

    # 2. Load Context
    profile_path = os.path.join(CONTENT_ROOT, "knowledge-base", "02_case_studies_and_performance", "packaged-agile-company-profile.md")
    company_profile = load_file(profile_path)

    # 3. Draft Script
    print(f"\n✍️  Drafting script for {persona} using {framework}...")
    
    creation_template = load_file(os.path.join(TEMPLATES_DIR, "creation_prompt.md"))
    draft_prompt = creation_template.replace("{target_persona}", persona) \
                                    .replace("{topic}", topic) \
                                    .replace("{framework}", framework) \
                                    .replace("{evidence}", evidence) \
                                    .replace("{company_context}", company_profile[:3000])

    draft_script = run_gemini(draft_prompt)
    if not draft_script:
        print("❌ Failed to generate script.")
        return

    # 4. Inline Review (Quick Pass)
    print("\n🕵️  Running quick 'Claire' review during generation...")
    review_template = load_file(os.path.join(TEMPLATES_DIR, "review_prompt.md"))
    review_prompt = review_template.replace("{script_content}", draft_script)
    review_raw = run_gemini(review_prompt)
    
    final_script = draft_script
    
    if review_raw:
        try:
            json_str = review_raw
            if "```json" in review_raw:
                json_str = review_raw.split("```json")[1].split("```")[0].strip()
            elif "```" in review_raw:
                json_str = review_raw.split("```")[1].split("```")[0].strip()
            
            review_data = json.loads(json_str)
            verdict = review_data.get("verdict", "UNKNOWN")
            print(f"Quick Verdict: {verdict}")

            if verdict in ["REVISE", "REJECT"]:
                print("🔧 Auto-Refining...")
                fix_prompt = f"Original:\n{draft_script}\n\nFeedback:\n{json_str}\n\nTask: Rewrite script to address feedback. Keep markdown format. Under 130 words."
                final_script = run_gemini(fix_prompt)
        except Exception:
            print("⚠️ Quick review parsing failed; skipping auto-refine.")

