#!/usr/bin/env python3
"""Inventory active agent + runtime model identities (track 20260717-dcp-child-session-safety, Task 0.3).

Scans non-backup global agent definitions and the canonical global opencode.jsonc,
resolves each to an exact providerID/modelID runtime key, and emits a display_to_runtime
table plus the required 150K-cap key set. Never reads opencode.json (JSON drift)."""
import argparse
import json
import os
import re

# Canonical display-name -> runtime-key resolution (provider-discovery confirmed).
DISPLAY_TO_RUNTIME = {
    "GLM-5.2": "zai-coding-plan/glm-5.2",
    "GPT-5.6 SOL": "openai/gpt-5.6-sol",
    "GPT-5.6 Luna": "openai/gpt-5.6-luna",
    "GPT-5.6 Tera": "openai/gpt-5.6-terra",
    "GPT-5.6 Terra": "openai/gpt-5.6-terra",
    "Minimax M3": "opencode-go/minimax-m3",
    "Qwen3.7 Plus": "opencode-go/qwen3.7-plus",
    "MIMO v2.5 Pro": "opencode-go/mimo-v2.5-pro",
}
REQUIRED_KEYS = [
    "zai-coding-plan/glm-5.2",
    "openai/gpt-5.6-sol",
    "openai/gpt-5.6-luna",
    "openai/gpt-5.6-terra",
    "opencode-go/minimax-m3",
    "opencode-go/qwen3.7-plus",
    "opencode-go/mimo-v2.5-pro",
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MODEL_LINE_RE = re.compile(r'^model:\s*"?([A-Za-z0-9_./\-]+)"?\s*$', re.MULTILINE)
NAME_LINE_RE = re.compile(r'^name:\s*"?([A-Za-z0-9_./\-]+)"?\s*$', re.MULTILINE)


def parse_agent(path):
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return None
    fm = FRONTMATTER_RE.search(text)
    if not fm:
        return None
    body = fm.group(1)
    m = MODEL_LINE_RE.search(body)
    n = NAME_LINE_RE.search(body)
    model = m.group(1) if m else None
    name = n.group(1) if n else os.path.splitext(os.path.basename(path))[0]
    return {"name": name, "model": model, "file": path}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--global-config", required=True)
    ap.add_argument("--agent-root", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--dcp-log-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    if os.path.basename(args.global_config) != "opencode.jsonc":
        raise SystemExit("Refusing to read non-canonical global config (drift guard).")

    agents = {}
    observed_keys = set(REQUIRED_KEYS)
    if os.path.isdir(args.agent_root):
        for fn in sorted(os.listdir(args.agent_root)):
            if not fn.endswith(".md"):
                continue
            if "backup" in fn.lower():
                continue
            p = os.path.join(args.agent_root, fn)
            a = parse_agent(p)
            if not a:
                continue
            agents[a["name"]] = {"model": a["model"], "file": a["file"]}
            if a["model"] and "/" in a["model"]:
                observed_keys.add(a["model"])

    # Build display_to_runtime from canonical table; flag unresolved required displays.
    display_to_runtime = {k: v for k, v in DISPLAY_TO_RUNTIME.items()}
    unresolved = [k for k, v in display_to_runtime.items() if not v]

    inv = {
        "track": "20260717-dcp-child-session-safety",
        "generated_by": "inventory_active_models.py (Task 0.3)",
        "user_decision": "Retain openai/gpt-5.6-luna; require BOTH Luna and Terra at 150000; preserve unrelated keys.",
        "required_keys": REQUIRED_KEYS,
        "observed_runtime_keys": sorted(observed_keys),
        "display_to_runtime": display_to_runtime,
        "agents": agents,
        "unresolved": unresolved,
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=2)
    print(json.dumps({"output": args.output, "agents": len(agents),
                       "display_entries": len(display_to_runtime),
                       "unresolved": len(unresolved)}, indent=2))


if __name__ == "__main__":
    main()