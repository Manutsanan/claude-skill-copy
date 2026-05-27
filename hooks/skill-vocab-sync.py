#!/usr/bin/env python3
"""PostToolUse hook (matcher=Write|Edit|NotebookEdit):
Detect when Claude saves a feedback_skill_trigger_* memory file, then:
  1. Auto-append the new phrase to skill_trigger_vocabulary.md immediately (host-side)
  2. POST to n8n /webhook/claude-vocab-correction for tracking + recurring-mismatch alerts

Exits in <2 ms for any non-trigger file — safe to run on every write.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Optional

VOCAB_PATH = Path.home() / ".claude" / "memory" / "skill_trigger_vocabulary.md"
N8N_BASE = "http://localhost:5678"
VALID_SKILLS = {
    "sa", "ux", "fe", "debug", "migrate",
    "pr", "audit", "simplify", "review",
    "distill-memory", "verify", "run",
}


def is_trigger_file(file_path: str) -> bool:
    return "feedback_skill_trigger" in Path(file_path).name


def extract_content(payload: dict) -> str:
    ti = payload.get("tool_input", {})
    if ti.get("content"):
        return ti["content"]
    if ti.get("new_string"):
        return ti["new_string"]
    fp = ti.get("file_path", "")
    if fp:
        try:
            return Path(fp).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass
    return ""


def parse_correction(content: str) -> Optional[tuple]:
    """Return (phrase, correct_skill, wrong_skill) or None."""
    desc_m = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    desc = desc_m.group(1).strip() if desc_m else ""

    pattern = (
        r'["“”`]([^"“”`\n]{2,60})["“”`]'
        r'\s*[→\->]+\s*`?(\w[\w-]*)`?'
        r'(?:\s*\(?not\s+`?(\w[\w-]*)`?\)?)?'
    )
    for src in (desc, content):
        m = re.search(pattern, src)
        if m:
            phrase = m.group(1).strip()
            correct = m.group(2).strip()
            wrong = (m.group(3) or "").strip()
            if correct in VALID_SKILLS and len(phrase) >= 2:
                return phrase, correct, wrong
    return None


def append_to_vocabulary(phrase: str, correct_skill: str) -> bool:
    if not VOCAB_PATH.exists():
        return False
    try:
        text = VOCAB_PATH.read_text(encoding="utf-8")
    except Exception:
        return False

    # Avoid duplicates
    if phrase in text:
        return False

    marker = f"## `{correct_skill}`"
    idx = text.find(marker)
    if idx == -1:
        return False

    # Slice out just this section
    rest = text[idx + len(marker):]
    end_m = re.search(r'\n(?:---|\#\#)', rest)
    section_content = rest[: end_m.start()] if end_m else rest

    bullets = list(re.finditer(r'\n- .+', section_content))
    if not bullets:
        return False

    insert_at = idx + len(marker) + bullets[-1].end()
    new_text = text[:insert_at] + f"\n- {phrase}" + text[insert_at:]
    try:
        VOCAB_PATH.write_text(new_text, encoding="utf-8")
        return True
    except Exception:
        return False


def notify_n8n(phrase: str, correct_skill: str, wrong_skill: str, applied: bool):
    try:
        payload = json.dumps({
            "phrase": phrase,
            "correct_skill": correct_skill,
            "wrong_skill": wrong_skill,
            "auto_applied": applied,
        }).encode()
        req = urllib.request.Request(
            f"{N8N_BASE}/webhook/claude-vocab-correction",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return

    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not is_trigger_file(file_path):
        return

    content = extract_content(payload)
    if not content:
        return

    result = parse_correction(content)
    if not result:
        notify_n8n("(unparsed)", "?", "?", False)
        return

    phrase, correct_skill, wrong_skill = result
    applied = append_to_vocabulary(phrase, correct_skill)
    notify_n8n(phrase, correct_skill, wrong_skill, applied)


try:
    main()
except Exception:
    pass

sys.exit(0)
