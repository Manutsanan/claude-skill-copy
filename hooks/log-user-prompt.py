#!/usr/bin/env python3
"""UserPromptSubmit hook: log truncated prompt as JSONL.

Stdin JSON: { session_id, cwd, prompt }

Stored: ~/.claude/logs/prompts-YYYY-MM.jsonl
- prompt truncated to 200 chars (per privacy decision)
- cwd hashed (8-char sha256 prefix)
- skips empty prompts and slash-command meta-prompts (start with '/')

Errors: written to ~/.claude/logs/hook-errors.jsonl, never block (exit 0).
"""
import hashlib
import json
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path.home() / ".claude" / "logs"
HOOK_NAME = "log-user-prompt"
TRUNC = 200

# Redact obvious secrets before write (defense-in-depth; logs stay local but
# still avoid accidental token capture if user pastes one).
REDACT_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                     # OpenAI/Anthropic-style
    re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}"),              # GitHub token
    re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),                 # Google API key
    re.compile(r"[A-Za-z0-9+/]{40,}={0,2}\b"),              # base64 blob ≥ 40
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),            # email
]


def redact(text: str) -> str:
    for pat in REDACT_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text


def cwd_hash(cwd: str) -> str:
    return hashlib.sha256(cwd.encode()).hexdigest()[:8]


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

    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return

    # Skip pure slash-command lines (those are tracked via Skill hook anyway)
    if prompt.startswith("/") and "\n" not in prompt:
        return

    now = datetime.now(timezone.utc)
    record = {
        "ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session": (payload.get("session_id") or "")[:8],
        "cwd_hash": cwd_hash(payload.get("cwd") or ""),
        "prompt": redact(prompt[:TRUNC]),
        "len": len(prompt),
    }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"prompts-{now.strftime('%Y-%m')}.jsonl"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


try:
    main()
except Exception as e:
    log_error(e)

sys.exit(0)
