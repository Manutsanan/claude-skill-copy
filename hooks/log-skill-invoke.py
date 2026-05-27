#!/usr/bin/env python3
"""PreToolUse hook (matcher=Skill): log every skill invocation as JSONL.

Stdin JSON (Claude Code hook payload):
  { session_id, cwd, tool_name, tool_input: { skill, args } }

Output: ~/.claude/logs/skill-invocations-YYYY-MM.jsonl (one line per invoke).
Errors: written to ~/.claude/logs/hook-errors.jsonl, never block (exit 0).
"""
import hashlib
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path.home() / ".claude" / "logs"
HOOK_NAME = "log-skill-invoke"


def cwd_hash(cwd: str) -> str:
    return hashlib.sha256(cwd.encode()).hexdigest()[:16]


def log_error(err: Exception):
    """Append error trace to hook-errors.jsonl. Last-resort silent on its own failure."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "hook": HOOK_NAME,
            "error": f"{type(err).__name__}: {err}",
            "traceback": traceback.format_exc()[:2000],
        }
        with (LOG_DIR / "hook-errors.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return  # malformed stdin is not an error — silently skip

    if payload.get("tool_name") != "Skill":
        return

    tool_input = payload.get("tool_input") or {}
    skill = tool_input.get("skill")
    if not skill:
        return

    now = datetime.now(timezone.utc)
    record = {
        "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session": (payload.get("session_id") or "")[:8],
        "cwd_hash": cwd_hash(payload.get("cwd") or ""),
        "skill": skill,
        "args": (tool_input.get("args") or "")[:120],
    }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"skill-invocations-{now.strftime('%Y-%m')}.jsonl"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


try:
    main()
except Exception as e:
    log_error(e)

sys.exit(0)
