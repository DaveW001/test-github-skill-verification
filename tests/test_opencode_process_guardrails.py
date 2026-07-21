import re
from pathlib import Path


CONFIG_ROOT = Path.home() / ".config" / "opencode"


def test_global_config_blocks_broad_process_termination():
    text = (CONFIG_ROOT / "opencode.jsonc").read_text(encoding="utf-8-sig")
    required = {
        '"Stop-Process *": "ask"',
        '"Stop-Process -Force *": "deny"',
        '"Stop-Process -Name *": "deny"',
        '"taskkill *opencode*": "deny"',
    }
    assert required.issubset(set(line.strip().rstrip(",") for line in text.splitlines()))


def test_primary_agents_do_not_override_global_bash_guardrails():
    agent_dir = CONFIG_ROOT / "agent"
    offenders = []
    for path in agent_dir.glob("*.md"):
        text = path.read_text(encoding="utf-8-sig")
        frontmatter = text.split("---", 2)[1] if text.startswith("---") else ""
        if re.search(r"(?m)^mode:\s*primary\s*$", frontmatter) and re.search(
            r"(?m)^\s+bash:\s+allow\s*$", frontmatter
        ):
            offenders.append(path.name)
    assert offenders == []
