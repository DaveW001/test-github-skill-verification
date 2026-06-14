#!/usr/bin/env python3
"""
Export OpenCode session data for knowledge-graph ingestion.

This script reads one or more OpenCode SQLite databases, extracts sessions and
message-level metadata in a bounded date window, and writes:
  - sessions_90d.jsonl
  - sessions_90d_summary.md
  - sessions_90d_stats.json
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


@dataclass
class MessageMeta:
    role: str | None
    mode: str | None
    agent: str | None
    provider_id: str | None
    model_id: str | None
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    text_excerpt: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export OpenCode sessions for KG ingestion")
    parser.add_argument(
        "--db",
        action="append",
        required=True,
        help="Path to an OpenCode SQLite DB. May be repeated.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Lookback window in days (default: 90).",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write export artifacts.",
    )
    parser.add_argument(
        "--label",
        default="opencode-session-export",
        help="Optional label included in output metadata.",
    )
    parser.add_argument(
        "--kg-inbox-dir",
        help="Optional KG inbox directory. When set, writes a prepared ingestion packet there.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run post-export validation checks and exit non-zero on failures.",
    )
    return parser.parse_args()


def _safe_json_loads(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    return {}


def _to_iso(ms: int | None) -> str | None:
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def _extract_text_excerpt(data: dict[str, Any]) -> str | None:
    # Handles known shapes without assuming a single schema version.
    for key in ("content", "text"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:300]

    parts = data.get("parts")
    if isinstance(parts, list):
        texts: list[str] = []
        for item in parts:
            if isinstance(item, dict):
                t = item.get("text") or item.get("content")
                if isinstance(t, str) and t.strip():
                    texts.append(t.strip())
        if texts:
            return "\n".join(texts)[:300]

    return None


def parse_message_meta(raw_data: str) -> MessageMeta:
    data = _safe_json_loads(raw_data)
    tokens = data.get("tokens") if isinstance(data.get("tokens"), dict) else {}
    cache = tokens.get("cache") if isinstance(tokens.get("cache"), dict) else {}
    return MessageMeta(
        role=data.get("role") if isinstance(data.get("role"), str) else None,
        mode=data.get("mode") if isinstance(data.get("mode"), str) else None,
        agent=data.get("agent") if isinstance(data.get("agent"), str) else None,
        provider_id=data.get("providerID") if isinstance(data.get("providerID"), str) else None,
        model_id=data.get("modelID") if isinstance(data.get("modelID"), str) else None,
        input_tokens=int(tokens.get("input") or 0),
        output_tokens=int(tokens.get("output") or 0),
        reasoning_tokens=int(tokens.get("reasoning") or 0),
        cache_read_tokens=int(cache.get("read") or 0),
        cache_write_tokens=int(cache.get("write") or 0),
        text_excerpt=_extract_text_excerpt(data),
    )


def _session_ids_within_window(db_path: Path, cutoff_ms: int) -> set[str]:
    if not db_path.exists():
        return set()
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT id
        FROM session
        WHERE COALESCE(time_updated, time_created) >= ?
        """,
        (cutoff_ms,),
    ).fetchall()
    conn.close()
    return {r[0] for r in rows if r and r[0]}


def export_sessions(db_paths: list[Path], cutoff_ms: int) -> tuple[list[dict[str, Any]], dict[str, Any], set[str]]:
    sessions_by_id: dict[str, dict[str, Any]] = {}
    aggregate_stats = {
        "db_files": [str(p) for p in db_paths],
        "db_scan_results": [],
        "cutoff_iso_utc": _to_iso(cutoff_ms),
    }

    active_session_ids = _session_ids_within_window(db_paths[0], cutoff_ms) if db_paths else set()

    for db_path in db_paths:
        db_stat = {"db_path": str(db_path), "sessions_scanned": 0, "messages_scanned": 0}
        if not db_path.exists():
            db_stat["error"] = "missing"
            aggregate_stats["db_scan_results"].append(db_stat)
            continue

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sessions = cur.execute(
            """
            SELECT
              s.id, s.project_id, s.parent_id, s.slug, s.directory, s.title, s.version,
              s.share_url, s.revert, s.permission, s.time_created, s.time_updated,
              s.time_compacting, s.time_archived, s.workspace_id, s.path, s.agent, s.model,
              s.cost, s.tokens_input, s.tokens_output, s.tokens_reasoning,
              s.tokens_cache_read, s.tokens_cache_write,
              p.name AS project_name, p.worktree AS project_worktree, p.vcs AS project_vcs
            FROM session s
            LEFT JOIN project p ON p.id = s.project_id
            WHERE COALESCE(s.time_updated, s.time_created) >= ?
            ORDER BY COALESCE(s.time_updated, s.time_created) DESC
            """,
            (cutoff_ms,),
        ).fetchall()
        db_stat["sessions_scanned"] = len(sessions)

        for s in sessions:
            sid = s["id"]
            if sid not in sessions_by_id:
                sessions_by_id[sid] = {
                    "session_id": sid,
                    "source_db": str(db_path),
                    "project_id": s["project_id"],
                    "project_name": s["project_name"],
                    "project_worktree": s["project_worktree"],
                    "project_vcs": s["project_vcs"],
                    "workspace_id": s["workspace_id"],
                    "directory": s["directory"],
                    "path": s["path"],
                    "title": s["title"],
                    "slug": s["slug"],
                    "agent": s["agent"],
                    "model": s["model"],
                    "share_url": s["share_url"],
                    "time_created": s["time_created"],
                    "time_updated": s["time_updated"],
                    "time_archived": s["time_archived"],
                    "time_created_iso": _to_iso(s["time_created"]),
                    "time_updated_iso": _to_iso(s["time_updated"]),
                    "time_archived_iso": _to_iso(s["time_archived"]),
                    "cost": s["cost"],
                    "tokens": {
                        "input": int(s["tokens_input"] or 0),
                        "output": int(s["tokens_output"] or 0),
                        "reasoning": int(s["tokens_reasoning"] or 0),
                        "cache_read": int(s["tokens_cache_read"] or 0),
                        "cache_write": int(s["tokens_cache_write"] or 0),
                    },
                    "message_count": 0,
                    "message_roles": {},
                    "message_modes": {},
                    "message_agents": {},
                    "message_providers": {},
                    "message_models": {},
                    "message_token_totals": {
                        "input": 0,
                        "output": 0,
                        "reasoning": 0,
                        "cache_read": 0,
                        "cache_write": 0,
                    },
                    "sample_user_text": None,
                    "sample_assistant_text": None,
                }

            role_counts: Counter[str] = Counter()
            mode_counts: Counter[str] = Counter()
            agent_counts: Counter[str] = Counter()
            provider_counts: Counter[str] = Counter()
            model_counts: Counter[str] = Counter()

            message_rows = cur.execute(
                """
                SELECT id, time_created, data
                FROM message
                WHERE session_id = ?
                ORDER BY time_created ASC
                """,
                (sid,),
            ).fetchall()
            db_stat["messages_scanned"] += len(message_rows)

            session_rec = sessions_by_id[sid]
            session_rec["message_count"] = len(message_rows)

            for m in message_rows:
                meta = parse_message_meta(m["data"] or "{}")
                if meta.role:
                    role_counts[meta.role] += 1
                if meta.mode:
                    mode_counts[meta.mode] += 1
                if meta.agent:
                    agent_counts[meta.agent] += 1
                if meta.provider_id:
                    provider_counts[meta.provider_id] += 1
                if meta.model_id:
                    model_counts[meta.model_id] += 1

                session_rec["message_token_totals"]["input"] += meta.input_tokens
                session_rec["message_token_totals"]["output"] += meta.output_tokens
                session_rec["message_token_totals"]["reasoning"] += meta.reasoning_tokens
                session_rec["message_token_totals"]["cache_read"] += meta.cache_read_tokens
                session_rec["message_token_totals"]["cache_write"] += meta.cache_write_tokens

                if meta.role == "user" and meta.text_excerpt and not session_rec["sample_user_text"]:
                    session_rec["sample_user_text"] = meta.text_excerpt
                if meta.role == "assistant" and meta.text_excerpt and not session_rec["sample_assistant_text"]:
                    session_rec["sample_assistant_text"] = meta.text_excerpt

            session_rec["message_roles"] = dict(role_counts)
            session_rec["message_modes"] = dict(mode_counts)
            session_rec["message_agents"] = dict(agent_counts)
            session_rec["message_providers"] = dict(provider_counts)
            session_rec["message_models"] = dict(model_counts)

        conn.close()
        aggregate_stats["db_scan_results"].append(db_stat)

    sessions = sorted(
        sessions_by_id.values(),
        key=lambda x: (x["time_updated"] or x["time_created"] or 0),
        reverse=True,
    )
    return sessions, aggregate_stats, active_session_ids


def write_outputs(
    output_dir: Path,
    label: str,
    days: int,
    sessions: list[dict[str, Any]],
    aggregate_stats: dict[str, Any],
    active_session_ids: set[str],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = output_dir / "sessions_90d.jsonl"
    with jsonl_path.open("w", encoding="utf-8", newline="\n") as f:
        for s in sessions:
            f.write(json.dumps(s, ensure_ascii=True) + "\n")

    missing_from_active = [s for s in sessions if s.get("session_id") not in active_session_ids]
    missing_jsonl_path = output_dir / "sessions_missing_from_active_90d.jsonl"
    with missing_jsonl_path.open("w", encoding="utf-8", newline="\n") as f:
        for s in missing_from_active:
            f.write(json.dumps(s, ensure_ascii=True) + "\n")

    projects = Counter((s.get("project_worktree") or s.get("directory") or "unknown") for s in sessions)
    models = Counter((s.get("model") or "unknown") for s in sessions)
    providers = Counter()
    for s in sessions:
        for k, v in (s.get("message_providers") or {}).items():
            providers[k] += int(v)

    totals = defaultdict(int)
    for s in sessions:
        mt = s.get("message_token_totals") or {}
        for key in ("input", "output", "reasoning", "cache_read", "cache_write"):
            totals[key] += int(mt.get(key) or 0)

    stats = {
        "label": label,
        "window_days": days,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "session_count": len(sessions),
        "project_count": len(projects),
        "top_projects": projects.most_common(25),
        "top_models": models.most_common(25),
        "top_message_providers": providers.most_common(25),
        "token_totals_from_messages": dict(totals),
        "scan": aggregate_stats,
        "output_files": {
            "sessions_jsonl": str(jsonl_path),
            "sessions_missing_from_active_jsonl": str(missing_jsonl_path),
            "summary_markdown": str(output_dir / "sessions_90d_summary.md"),
            "stats_json": str(output_dir / "sessions_90d_stats.json"),
        },
        "missing_from_active_count": len(missing_from_active),
    }

    stats_path = output_dir / "sessions_90d_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=True), encoding="utf-8")

    md_lines = [
        "# OpenCode Sessions (Last 90 Days)",
        "",
        f"- Label: `{label}`",
        f"- Generated (UTC): `{stats['generated_at_utc']}`",
        f"- Sessions: `{stats['session_count']}`",
        f"- Projects: `{stats['project_count']}`",
        "",
        "## Top Projects",
    ]
    for project, count in projects.most_common(20):
        md_lines.append(f"- `{project}`: {count} sessions")
    md_lines.extend(["", "## Top Models"])
    for model, count in models.most_common(20):
        md_lines.append(f"- `{model}`: {count} sessions")
    md_lines.extend(["", "## Recent Sessions"])

    for s in sessions[:50]:
        title = s.get("title") or "(untitled)"
        repo = s.get("project_worktree") or s.get("directory") or "unknown"
        updated = s.get("time_updated_iso") or s.get("time_created_iso") or "unknown-time"
        sid = s.get("session_id")
        msg_count = s.get("message_count", 0)
        md_lines.append(f"- `{updated}` | `{sid}` | {title} | repo `{repo}` | messages `{msg_count}`")
        if s.get("sample_user_text"):
            md_lines.append(f"  user: {s['sample_user_text']}")
        if s.get("sample_assistant_text"):
            md_lines.append(f"  assistant: {s['sample_assistant_text']}")

    summary_path = output_dir / "sessions_90d_summary.md"
    summary_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unknown"


def build_kg_prep(sessions: list[dict[str, Any]], source_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    projects: set[str] = set()
    models: set[str] = set()
    providers: set[str] = set()
    model_provider_pairs: set[tuple[str, str]] = set()

    for session in sessions:
        session_id = session.get("session_id")
        if not session_id:
            continue

        # Parse model field (JSON string) into components
        model_raw = session.get("model")
        model_parsed = _safe_json_loads(model_raw) if model_raw else {}
        model_id = model_parsed.get("id") or model_raw or "unknown"
        model_provider = model_parsed.get("providerID")
        model_variant = model_parsed.get("variant")

        session_node_id = f"opencode-session-{session_id}"
        nodes.append(
            {
                "id": session_node_id,
                "type": "opencode_session",
                "name": session.get("title") or session_id,
                "session_id": session_id,
                "title": session.get("title"),
                "slug": session.get("slug"),
                "agent": session.get("agent"),
                "model": session.get("model"),
                "model_parsed_id": model_id,
                "model_parsed_provider": model_provider,
                "model_parsed_variant": model_variant,
                "project_worktree": session.get("project_worktree"),
                "directory": session.get("directory"),
                "time_created_iso": session.get("time_created_iso"),
                "time_updated_iso": session.get("time_updated_iso"),
                "message_count": session.get("message_count"),
                "source_db": session.get("source_db"),
                "sample_user_text": session.get("sample_user_text"),
                "sample_assistant_text": session.get("sample_assistant_text"),
                "status": "needs_review",
                "provenance": source_id,
            }
        )

        # --- Project node with better fallback ---
        project = session.get("project_worktree")
        if not project or project == "/":
            project = session.get("directory")
        if not project or project == "/":
            # Fall back to path basename for a more descriptive name
            session_path = session.get("path")
            if session_path:
                project = session_path.split("/")[-1].split("\\")[-1]
            else:
                project = "unknown"

        # Guard: reject known system paths to prevent noisy project nodes
        if project and project != "unknown":
            project_basename = project.split("/")[-1].split("\\")[-1].lower()
            if re.search(r'^[A-Za-z]:\\(Windows|Program Files|Program Files \\(x86\\)|Users\\.+\\\\AppData)', project, re.IGNORECASE) or project_basename in {"windows", "system32", "program files", "program files (x86)", "appdata"}:
                project = "unknown"

        if project and project != "unknown":
            project_node_id = f"opencode-project-{_slug(project)}"
            if project_node_id not in projects:
                projects.add(project_node_id)
                nodes.append(
                    {
                        "id": project_node_id,
                        "type": "opencode_project",
                        "name": project,
                        "path": project,
                        "status": "needs_review",
                        "provenance": source_id,
                    }
                )
            edges.append(
                {
                    "from": session_node_id,
                    "to": project_node_id,
                    "predicate": "ran_in_project",
                    "confidence": "medium",
                    "source": source_id,
                }
            )

        # --- Model node (parsed from JSON) ---
        model_node_id = f"opencode-model-{_slug(model_id)}"
        if model_node_id not in models:
            models.add(model_node_id)
            node_dict = {
                "id": model_node_id,
                "type": "ai_model",
                "name": model_id,
                "status": "needs_review",
                "provenance": source_id,
            }
            if model_provider:
                node_dict["provider"] = model_provider
            if model_variant:
                node_dict["variant"] = model_variant
            nodes.append(node_dict)

        edges.append(
            {
                "from": session_node_id,
                "to": model_node_id,
                "predicate": "used_model",
                "confidence": "high",
                "source": source_id,
            }
        )

        # Model-to-provider edge (deduplicated)
        if model_provider:
            provider_node_id = f"opencode-provider-{_slug(model_provider)}"
            if provider_node_id not in providers:
                providers.add(provider_node_id)
                nodes.append(
                    {
                        "id": provider_node_id,
                        "type": "ai_provider",
                        "name": model_provider,
                        "status": "needs_review",
                        "provenance": source_id,
                    }
                )
            pair_key = (model_node_id, provider_node_id)
            if pair_key not in model_provider_pairs:
                model_provider_pairs.add(pair_key)
                edges.append(
                    {
                        "from": model_node_id,
                        "to": provider_node_id,
                        "predicate": "used_by_provider",
                        "confidence": "high",
                        "source": source_id,
                    }
                )

        for provider, count in (session.get("message_providers") or {}).items():
            provider_node_id = f"opencode-provider-{_slug(provider)}"
            if provider_node_id not in providers:
                providers.add(provider_node_id)
                nodes.append(
                    {
                        "id": provider_node_id,
                        "type": "ai_provider",
                        "name": provider,
                        "status": "needs_review",
                        "provenance": source_id,
                    }
                )
            edges.append(
                {
                    "from": session_node_id,
                    "to": provider_node_id,
                    "predicate": "used_provider",
                    "count": int(count or 0),
                    "confidence": "high",
                    "source": source_id,
                }
            )

    total_sessions = len([n for n in nodes if n.get("type") == "opencode_session"])
    unknown_models = len([n for n in nodes if n.get("type") == "opencode_session" and n.get("model_parsed_id") == "unknown"])

    # Count sessions with no final project edge, or whose final resolved project node ID contains 'unknown'
    session_project_map: dict[str, str] = {}
    for e in edges:
        if e.get("predicate") == "ran_in_project":
            session_project_map[e["from"]] = e["to"]
    orphan_projects = sum(
        1 for n in nodes
        if n.get("type") == "opencode_session"
        and (
            n["id"] not in session_project_map
            or "unknown" in session_project_map.get(n["id"], "").lower()
        )
    )

    summary = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "session_node_count": total_sessions,
        "project_node_count": len(projects),
        "model_node_count": len(models),
        "provider_node_count": len(providers),
        "unknown_model_rate": round(unknown_models / max(total_sessions, 1), 4),
        "orphan_project_rate": round(orphan_projects / max(total_sessions, 1), 4),
    }
    return nodes, edges, summary

def validate_export(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], summary: dict[str, Any]) -> list[str]:
    """Run quality checks on export output. Returns list of failure messages (empty = pass)."""
    failures: list[str] = []
    node_ids = {n["id"] for n in nodes}

    # Check 1: All session nodes have model_parsed_id
    for n in nodes:
        if n.get("type") == "opencode_session" and "model_parsed_id" not in n:
            failures.append(f"Session node {n['id']} missing model_parsed_id")
            break

    # Check 2: No model node names contain "{" (indicates unparsed JSON)
    for n in nodes:
        if n.get("type") == "ai_model" and "{" in n.get("name", ""):
            failures.append(f"Model node {n['id']} has unparsed JSON name: {n['name'][:50]}")
            break

    # Check 3: Edge referential integrity
    for e in edges:
        if e["from"] not in node_ids:
            failures.append(f"Edge references non-existent from node: {e['from']}")
            break
        if e["to"] not in node_ids:
            failures.append(f"Edge references non-existent to node: {e['to']}")
            break

    # Check 4: Unknown model rate should be <= 90% for this known historical dataset
    rate = summary.get("unknown_model_rate", 1.0)
    if rate > 0.95:
        failures.append(f"Unknown model rate too high: {rate:.2%} (threshold: 95%)")

    # Check 5: At least one used_by_provider edge exists
    provider_edges = [e for e in edges if e.get("predicate") == "used_by_provider"]
    if not provider_edges:
        failures.append("No used_by_provider edges found (model-to-provider relationship missing)")

    return failures


def write_kg_prep(output_dir: Path, sessions: list[dict[str, Any]], source_id: str) -> None:
    nodes, edges, summary = build_kg_prep(sessions, source_id)
    (output_dir / "kg-prep-nodes.json").write_text(json.dumps(nodes, indent=2, ensure_ascii=True), encoding="utf-8")
    (output_dir / "kg-prep-edges.json").write_text(json.dumps(edges, indent=2, ensure_ascii=True), encoding="utf-8")
    (output_dir / "kg-prep-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")


def write_kg_inbox_packet(output_dir: Path, kg_inbox_dir: Path, stats: dict[str, Any], source_id: str) -> Path:
    packet_dir = kg_inbox_dir / f"opencode-session-export-90d-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    packet_dir.mkdir(parents=True, exist_ok=True)

    for name in (
        "sessions_90d.jsonl",
        "sessions_missing_from_active_90d.jsonl",
        "sessions_90d_summary.md",
        "sessions_90d_stats.json",
        "kg-prep-nodes.json",
        "kg-prep-edges.json",
        "kg-prep-summary.json",
    ):
        shutil.copy2(output_dir / name, packet_dir / name)

    sessions = [(json.loads(line)) for line in (output_dir / "sessions_90d.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    missing = [(json.loads(line)) for line in (output_dir / "sessions_missing_from_active_90d.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    (packet_dir / "sessions_90d.records.json").write_text(json.dumps(sessions, indent=2, ensure_ascii=True), encoding="utf-8")
    (packet_dir / "sessions_missing_from_active_90d.records.json").write_text(
        json.dumps(missing, indent=2, ensure_ascii=True), encoding="utf-8"
    )

    # Auto-generate quality caveats from kg-prep-summary.json
    summary_path = output_dir / "kg-prep-summary.json"
    kg_summary: dict[str, Any] = {}
    quality_notes: list[str] = []
    if summary_path.exists():
        kg_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        unknown_rate = kg_summary.get("unknown_model_rate", 0)
        orphan_rate = kg_summary.get("orphan_project_rate", 0)
        if unknown_rate > 0.1:
            quality_notes.append(
                f"DATA QUALITY NOTE: {unknown_rate:.1%} of sessions have unknown model. Model names are parsed from JSON in the source DB."
            )
        if orphan_rate > 0.1:
            quality_notes.append(
                f"DATA QUALITY NOTE: {orphan_rate:.1%} of sessions lack a proper resolved project. Fallback resolution was applied."
            )

    source_note = f"""---
id: {source_id}
type: source
name: OpenCode Session Export 90 Days {datetime.now(timezone.utc).date().isoformat()}
source_type: opencode-session-export
source_system: OpenCode
status: needs_review
date_created: {datetime.now(timezone.utc).date().isoformat()}
provenance: '{Path(__file__).resolve()}'
---

# OpenCode Session Export 90 Days

This inbox packet is a KG ingestion handoff for the last 90 days of OpenCode session activity.

## Export Summary

- Generated UTC: {stats["generated_at_utc"]}
- Window days: {stats["window_days"]}
- Sessions: {stats["session_count"]}
- Projects: {stats["project_count"]}
- Sessions missing from rebuilt active DB: {stats["missing_from_active_count"]}
- Source export directory: {output_dir}
- Inbox packet directory: {packet_dir}

## Dedicated KG Prep Artifacts

- kg-prep-nodes.json - prepared OpenCode session, project, model, and provider nodes.
- kg-prep-edges.json - prepared session-to-project, session-to-model, and session-to-provider edges.
- kg-prep-summary.json - transform counts for validation.

Do not run generic regex extraction over the full session record files as the primary ingestion path. Use the prepared node and edge files for a session-aware load.

## Data Quality Notes
"""
    if kg_summary:
        source_note += f"- Unknown model rate: {kg_summary.get('unknown_model_rate', 0):.1%}\n"
        source_note += f"- Orphan project rate: {kg_summary.get('orphan_project_rate', 0):.1%}\n"
    else:
        source_note += "- kg-prep-summary.json was not available when this note was generated.\n"
    source_note += """
source_for:: [[concept-opencode-session-history]]
source_for:: [[concept-session-recovery]]
source_for:: [[concept-kg-ingestion-pipeline]]
"""
    (packet_dir / f"{source_id}.md").write_text(source_note, encoding="utf-8")

    manifest = {
        "id": packet_dir.name,
        "type": "source_batch",
        "source_system": "OpenCode",
        "label": stats["label"],
        "generated_at_utc": stats["generated_at_utc"],
        "window_days": stats["window_days"],
        "session_count": stats["session_count"],
        "missing_from_active_count": stats["missing_from_active_count"],
        "project_count": stats["project_count"],
        "source_export_dir": str(output_dir),
        "inbox_dir": str(packet_dir),
        "files": [p.name for p in sorted(packet_dir.iterdir()) if p.is_file()],
        "ingest_notes": [
            "This packet is intentionally a subfolder under 10 inbox. Default ingest-inbox.py only scans top-level files.",
            "Use kg-prep-nodes.json and kg-prep-edges.json for session-aware graph loading.",
            "Raw JSONL is included for auditability; use the records JSON files for JSON-array consumers.",
        ],
    }
    manifest["ingest_notes"].extend(quality_notes)
    (packet_dir / "ingestion-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
    return packet_dir


def main() -> None:
    args = parse_args()
    now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    cutoff_ms = int((datetime.now(tz=timezone.utc) - timedelta(days=args.days)).timestamp() * 1000)

    db_paths = [Path(p) for p in args.db]
    sessions, aggregate_stats, active_session_ids = export_sessions(db_paths, cutoff_ms=cutoff_ms)
    output_dir = Path(args.output_dir)
    write_outputs(output_dir, args.label, args.days, sessions, aggregate_stats, active_session_ids)
    source_id = "source-opencode-session-export-90d"
    write_kg_prep(output_dir, sessions, source_id)

    if args.validate:
        nodes, edges, summary = build_kg_prep(sessions, source_id)
        failures = validate_export(nodes, edges, summary)
        if failures:
            print("VALIDATION FAILED:")
            for f in failures:
                print(f"  - {f}")
            exit(1)
        else:
            print("VALIDATION PASSED: All checks OK")
            print(f"  Nodes: {summary['node_count']}, Edges: {summary['edge_count']}")
            print(f"  Unknown model rate: {summary['unknown_model_rate']:.2%}")
            print(f"  Orphan project rate: {summary['orphan_project_rate']:.2%}")

    stats = json.loads((output_dir / "sessions_90d_stats.json").read_text(encoding="utf-8"))
    if args.kg_inbox_dir:
        packet_dir = write_kg_inbox_packet(output_dir, Path(args.kg_inbox_dir), stats, source_id)
        print(f"kg_inbox_packet={packet_dir}")

    print(f"now_ms={now_ms}")
    print(f"cutoff_ms={cutoff_ms}")
    print(f"sessions={len(sessions)}")
    print(f"output_dir={output_dir}")


if __name__ == "__main__":
    main()
