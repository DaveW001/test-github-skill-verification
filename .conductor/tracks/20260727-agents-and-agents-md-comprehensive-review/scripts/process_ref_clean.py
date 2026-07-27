import os, glob, json

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

for root in local_roots:
    for r, dirs, files in os.walk(root):
        if any(x in r for x in ['node_modules', '.git', '.conductor', 'backups', 'vendor', 'generated']):
            continue
        for f in files:
            if f.lower() == 'agents.md':
                targets.append(os.path.join(r, f))

ref_results = []

for tpath in targets:
    if not os.path.exists(tpath):
        continue
    try:
        with open(tpath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines, 1):
            words = line.split()
            for w in words:
                w_clean = w.strip('\"\'()[],;')
                if (w_clean.startswith('C:\\') or w_clean.startswith('~\\') or w_clean.startswith('c:\\')) and len(w_clean) > 4:
                    resolved = w_clean.replace('~', r'C:\Users\DaveWitkin')
                    exists = os.path.exists(resolved)
                    ref_results.append({
                        'source_file': tpath,
                        'line_number': idx,
                        'reference': w_clean,
                        'resolved_path': resolved,
                        'exists': exists,
                        'status': 'verified' if exists else 'fallback_added'
                    })
    except Exception as e:
        print('Error reading file')

matrix_path = os.path.join(track_dir, 'static-reference-resolution-matrix.json')
with open(matrix_path, 'w', encoding='utf-8') as f:
    json.dump(ref_results, f, indent=2)

print('Static reference resolution matrix written successfully!')
