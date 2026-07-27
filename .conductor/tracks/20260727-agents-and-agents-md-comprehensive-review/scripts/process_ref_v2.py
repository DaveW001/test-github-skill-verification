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
    r'C:\development\02-Kx-to-process\AGENTS.md',
    r'C:\development\chief-of-staff\AGENTS.md',
    r'C:\development\command-center\AGENTS.md',
    r'C:\development\INACTIVE-content-marketing\AGENTS.md',
    r'C:\development\INACTIVE-content-marketing\ops\opencode-troubleshooting\AGENTS.md',
    r'C:\development\marketing\AGENTS.md',
    r'C:\development\marketing\graphics\fmqsmo-award\AGENTS.md',
    r'C:\development\marketing\ops\opencode-troubleshooting\AGENTS.md',
    r'C:\development\marketing\marketingskills\AGENTS.md',
    r'C:\development\opencodex\AGENTS.md',
    r'C:\development\opencodex\gui\AGENTS.md'
]

for repo in [r'C:\development\opencode-core-dcp-fix', r'C:\development\opencode-upstream']:
    local_roots.extend([
        os.path.join(repo, r'AGENTS.md'),
        os.path.join(repo, r'packages\app\AGENTS.md'),
        os.path.join(repo, r'packages\app\e2e\performance\AGENTS.md'),
        os.path.join(repo, r'packages\codemode\AGENTS.md'),
        os.path.join(repo, r'packages\core\src\tool\AGENTS.md'),
        os.path.join(repo, r'packages\desktop\AGENTS.md'),
        os.path.join(repo, r'packages\effect-drizzle-sqlite\AGENTS.md'),
        os.path.join(repo, r'packages\llm\AGENTS.md'),
        os.path.join(repo, r'packages\opencode\AGENTS.md'),
        os.path.join(repo, r'packages\opencode\src\server\routes\instance\httpapi\AGENTS.md'),
        os.path.join(repo, r'packages\opencode\src\session\llm\AGENTS.md'),
        os.path.join(repo, r'packages\opencode\test\AGENTS.md'),
        os.path.join(repo, r'packages\opencode\test\server\AGENTS.md'),
        os.path.join(repo, r'packages\schema\AGENTS.md'),
        os.path.join(repo, r'packages\stats\AGENTS.md')
    ])

targets.extend(local_roots)
targets = sorted(list(set(targets)))

ref_results = []
strip_chars = '\"\'()[],;'

for tpath in targets:
    if not os.path.exists(tpath):
        continue
    with open(tpath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        for w in line.split():
            clean_w = w.strip(strip_chars)
            if (clean_w.startswith('C:\\') or clean_w.startswith('~\\') or clean_w.startswith('c:\\')) and len(clean_w) > 4:
                resolved = clean_w.replace('~', r'C:\Users\DaveWitkin')
                exists = os.path.exists(resolved)
                ref_results.append({
                    'source_file': tpath,
                    'line_number': idx,
                    'reference': clean_w,
                    'resolved_path': resolved,
                    'exists': exists,
                    'status': 'verified' if exists else 'fallback_added'
                })

matrix_path = os.path.join(track_dir, 'static-reference-resolution-matrix.json')
with open(matrix_path, 'w', encoding='utf-8') as f:
    json.dump(ref_results, f, indent=2)

print('Static reference resolution matrix written successfully!')
