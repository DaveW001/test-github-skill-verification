import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_opencode_session_readable.py"
SPEC = importlib.util.spec_from_file_location("readable_export", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_render_excludes_hidden_parts_and_honors_limit(tmp_path):
    data = {
        "info": {"id": "ses_test", "title": "Test"},
        "messages": [
            {
                "info": {"role": "user", "time": {"created": 1_700_000_000_000}},
                "parts": [
                    {"type": "text", "text": "Visible request"},
                    {"type": "reasoning", "text": "SECRET_REASONING"},
                    {"type": "tool", "state": {"output": "SECRET_TOOL"}},
                    {"type": "patch", "hash": "SECRET_PATCH"},
                    {"type": "text", "ignored": True, "text": "SECRET_IGNORED"},
                ],
            },
            {
                "info": {"role": "assistant", "time": {"created": 1_700_000_001_000}},
                "parts": [{"type": "text", "text": "Visible answer"}],
            },
        ],
    }
    rendered = MODULE.render(data, tmp_path / "raw.json", 100)
    assert "Visible request" in rendered
    assert "Visible answer" in rendered
    assert "SECRET_REASONING" not in rendered
    assert "SECRET_TOOL" not in rendered
    assert "SECRET_PATCH" not in rendered
    assert "SECRET_IGNORED" not in rendered
    assert len(rendered.splitlines()) <= 100
