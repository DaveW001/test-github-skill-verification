import os
import re

skills = [
    r"C:\Users\DaveWitkin\.agents\skills\outlook-inbox-triage",
    r"C:\Users\DaveWitkin\.config\opencode\skill\email-draft-reply",
    r"C:\Users\DaveWitkin\.config\opencode\skills\email-auto-sorter",
    r"C:\Users\DaveWitkin\.config\opencode\skill\email-to-clickup",
    r"C:\Users\DaveWitkin\.config\opencode\skills\calendar-today",
    r"C:\Users\DaveWitkin\.config\opencode\skills\calendar-schedule"
]

for skill_dir in skills:
    skill_file = os.path.join(skill_dir, "SKILL.md")
    ref_file = os.path.join(skill_dir, "reference.md")
    
    if not os.path.exists(skill_file):
        print(f"Skipping {skill_dir}")
        continue
        
    with open(skill_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # FLAW 2: Frontmatter
    if "tool_context:" not in content:
        content = re.sub(r"^---$", r"---\ntool_context:\n  with_tools: [bash]", content, count=1, flags=re.MULTILINE)
        
    # FLAW 1: Move PowerShell blocks
    # Find the section starting with ## Graph PowerShell Execution up to the next ##
    match = re.search(r"(## Graph PowerShell Execution.*?)(\n## )", content, re.DOTALL)
    if match:
        ps_block = match.group(1)
        
        # FLAW 3: Timezone Bug in calendar queries
        if "calendar-" in skill_dir:
            # Calendar today specific timezone logic fix
            ps_block = re.sub(
                r"\$today = Get-Date -Format 'yyyy-MM-dd'\n\$tomorrow = \(Get-Date\)\.AddDays\(1\)\.ToString\('yyyy-MM-dd'\)",
                r"$start = (Get-Date).Date.ToUniversalTime().ToString('s') + 'Z'\n$end = (Get-Date).Date.AddDays(1).ToUniversalTime().ToString('s') + 'Z'",
                ps_block
            )
            ps_block = re.sub(
                r"-StartDateTime \"\$\{today\}T00:00:00\" `\n\s*-EndDateTime \"\$\{tomorrow\}T00:00:00\" `",
                r"-StartDateTime $start `\n    -EndDateTime $end `",
                ps_block
            )
            
            # Any remaining bad naked format (just in case)
            if 'ToString("yyyy-MM-ddTHH:mm:ss")' in ps_block:
                ps_block = ps_block.replace(
                    'ToString("yyyy-MM-ddTHH:mm:ss")', 
                    'ToUniversalTime().ToString("s")+"Z"'
                )
            
        # Write to reference.md
        ref_content = ""
        if os.path.exists(ref_file):
            with open(ref_file, "r", encoding="utf-8") as f:
                ref_content = f.read()
                
        if "Graph PowerShell Execution" not in ref_content:
            with open(ref_file, "w", encoding="utf-8") as f:
                if ref_content:
                    f.write(ref_content + "\n\n" + ps_block)
                else:
                    f.write("# Reference\n\n" + ps_block)
                    
        # Replace in SKILL.md
        content = content.replace(ps_block, "## Graph PowerShell Execution\n\nSee [reference.md](reference.md) for PowerShell cmdlets and syntax.\n")
        
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(content)
            
print("Fixes applied.")