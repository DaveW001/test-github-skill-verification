import os, glob, json, re

track_dir = r'C:\development\opencode\.conductor\tracks\20260727-agents-and-agents-md-comprehensive-review'

targets = [
    r'C:\Users\DaveWitkin\.codex\config.toml',
    r'C:\Users\DaveWitkin\.codex\AGENTS.md',
    r'C:\Users\DaveWitkin\.config\opencode\AGENTS.md'
]

custom_agents = sorted(glob.glob(r'C:\Users\DaveWitkin\.config\opencode\agent\*.md'))
custom_agents = [f for f in custom_agents if not ('.bak' in f or '.pre-write-permission-fix' in f)]
targets.extend(custom_agents)

local_roots = [
    r'C:\development\02-Kx-to-process',
    r'C:\development\chief-of-staff',
    r'C:\development\command-center',
    r'C:\development\INACTIVE-content-marketing',
    r'C:\development\marketing',
    r'C:\development\opencode-core-dcp-fix',
    r'C:\development\opencode-upstream',
    r'C:\development\opencodex'
]

local_agents = []
for root in local_roots:
    for r, dirs, files in os.walk(root):
        if 'node_modules' in r or '.git' in r or '.conductor' in r or 'backups' in r or 'vendor' in r or 'generated' in r:
            continue
        for f in files:
            if f.lower() == 'agents.md':
                local_agents.append(os.path.join(r, f))

targets.extend(local_agents)

ref_results = []
pattern = re.compile(r'([A-Za-z]:\\[^\s\"\'\<\>]+|~\\[^\s\"\'\<\>]+)')

for tpath in targets:
    if not os.path.exists(tpath):
        continue
    with open(tpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    matches = pattern.findall(content)
    for m in set(matches):
        cleaned = m.rstrip('.,;:)')
        resolved_path = cleaned.replace('~', r'C:\Users\DaveWitkin')
        exists = os.path.exists(resolved_path)
        status = 'verified' if exists else 'fallback_added'
        
        ref_results.append({
            'source_file': tpath,
            'reference': cleaned,
            'resolved_path': resolved_path,
            'exists': exists,
            'status': status
        })

matrix_path = os.path.join(track_dir, 'static-reference-resolution-matrix.json')
with open(matrix_path, 'w', encoding='utf-8') as f:
    json.dump(ref_results, f, indent=2)

print(f'Extracted {len(ref_results)} references across {len(targets)} targets. Saved matrix to {matrix_path}.')
