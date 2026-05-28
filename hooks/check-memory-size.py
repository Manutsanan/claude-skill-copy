#!/usr/bin/env python3
"""SessionStart hook: warn when project memory approaches its 30–50/skill cap,
and surface any hook errors logged in the past 24 hours.

Also:
  - Stale pipeline reminder: in-progress phase checkpoints from a prior session
  - Distill auto-inject: time-based suggestion when below count threshold but idle too long

Thresholds:
  WARN_THRESHOLD     project entries → suggest review
  CRITICAL_THRESHOLD project entries → strongly urge /distill-memory
  DISTILL_IDLE_DAYS  days since last distill → time-based suggestion (fires only below WARN)
  DISTILL_MIN_COUNT  minimum total entries before nagging about distill
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from _checkpoint_lib import checkpoint_dir, scan_in_progress

WARN_THRESHOLD = 30
CRITICAL_THRESHOLD = 45
HOOK_ERROR_WINDOW_HOURS = 24
DISTILL_IDLE_DAYS = 14
DISTILL_MIN_COUNT = 10
LOG_DIR = Path.home() / ".claude" / "logs"
SKILLS_DIR = Path.home() / ".claude" / "skills"
SKILL_WARN_LINES = 150
SKILL_CRITICAL_LINES = 200
SKILL_AUTO_TRIM_TARGET = 140  # trim to this after auto-prune (buffer below WARN)


def count_entries(memory_dir: Path) -> int:
    if not memory_dir.exists():
        return 0
    return sum(
        1
        for f in memory_dir.glob("*.md")
        if f.name != "MEMORY.md" and not f.name.startswith(".")
    )


def recent_hook_errors() -> dict:
    err_file = LOG_DIR / "hook-errors.jsonl"
    if not err_file.exists():
        return {}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOOK_ERROR_WINDOW_HOURS)
    counts: Counter = Counter()
    try:
        with err_file.open(encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    dt = datetime.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    if dt >= cutoff:
                        counts[rec.get("hook", "unknown")] += 1
                except Exception:
                    continue
    except Exception:
        return {}
    return dict(counts)


def last_distill_date() -> Optional[datetime]:
    """Scan skill invocation logs for most recent distill-memory run."""
    last: Optional[datetime] = None
    for log_file in sorted(LOG_DIR.glob("skill-invocations-*.jsonl"), reverse=True):
        try:
            lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            for line in reversed(lines):
                try:
                    rec = json.loads(line)
                    if rec.get("skill") == "distill-memory":
                        dt = datetime.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(
                            tzinfo=timezone.utc
                        )
                        if last is None or dt > last:
                            last = dt
                        return last  # first (most recent) match in this file is the answer
                except Exception:
                    continue
        except Exception:
            continue
        if last is not None:
            break
    return last


def stale_pipeline_warning(directory: Path) -> Optional[str]:
    """Warn if any in-progress phase checkpoints exist (left over from a prior session)."""
    checkpoints = scan_in_progress(directory)
    if not checkpoints:
        return None
    phases = []
    for name, _ in checkpoints:
        # filename: project_phase_checkpoint_<phase>_YYYY-MM-DD.md
        parts = name.replace(".md", "").split("_")
        # find index of 'checkpoint' then next token is the phase
        try:
            idx = parts.index("checkpoint")
            phases.append(parts[idx + 1])
        except (ValueError, IndexError):
            phases.append("?")
    phase_str = " + ".join(phases)
    return (
        f"⏸️ **Stale pipeline detected** — `{phase_str}` checkpoint(s) are `in_progress` "
        f"from a prior session. Resume from the checkpoint or mark it as `abandoned` to start fresh."
    )


def _parse_skill_entries(text: str):
    """Split learnings.md into (header_text, [(heading, body), ...]).
    Header = everything up to and including '## Entries'.
    Returns (None, []) if the expected structure is not found.
    """
    lines = text.split("\n")
    entries_line = next(
        (i for i, l in enumerate(lines) if l.strip() == "## Entries"), None
    )
    if entries_line is None:
        return None, []

    header = "\n".join(lines[: entries_line + 1])

    # Collect inter-header comment/blank lines before first entry
    preamble_end = entries_line + 1
    while preamble_end < len(lines) and not lines[preamble_end].startswith("## "):
        preamble_end += 1
    inter = "\n".join(lines[entries_line + 1 : preamble_end])  # e.g. "<!-- newest on top -->"

    entries: list[tuple[str, str]] = []
    cur_heading: Optional[str] = None
    cur_body: list[str] = []
    for line in lines[preamble_end:]:
        if line.startswith("## "):
            if cur_heading is not None:
                entries.append((cur_heading, "\n".join(cur_body)))
            cur_heading = line
            cur_body = []
        else:
            cur_body.append(line)
    if cur_heading is not None:
        entries.append((cur_heading, "\n".join(cur_body)))

    return (header, inter), entries


def _entry_date(body: str) -> str:
    m = re.search(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", body)
    return m.group(1) if m else "0000-00-00"


def auto_trim_skill_learnings(f: Path, skill: str) -> Optional[str]:
    """Remove oldest entries until line count ≤ SKILL_AUTO_TRIM_TARGET.
    Writes a dated backup before modifying. Returns a status string or None on failure.
    """
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
        header_tuple, entries = _parse_skill_entries(text)
        if header_tuple is None or not entries:
            return None  # unparseable — don't touch

        header, inter = header_tuple

        # Sort oldest-first for removal (preserve newest)
        dated = sorted(entries, key=lambda e: _entry_date(e[1]))

        def rebuild(ents):
            body = "\n\n".join(f"{h}\n{b}".rstrip() for h, b in ents)
            sep = f"\n{inter}\n\n" if inter.strip() else "\n\n"
            return header + sep + body + "\n"

        removed: list[tuple[str, str]] = []
        remaining = list(entries)  # original order (newest first)

        while len(rebuild(remaining).split("\n")) > SKILL_AUTO_TRIM_TARGET:
            if len(remaining) <= 1:
                break
            # Remove the oldest entry
            oldest = dated.pop(0)
            removed.append(oldest)
            remaining = [e for e in remaining if e[0] != oldest[0]]

        if not removed:
            return None

        # Write backup
        today_str = date.today().isoformat()
        backup = f.parent / f"learnings.trimmed.{today_str}.md"
        backup_content = (
            f"# Auto-trimmed entries from `{skill}` — {today_str}\n\n"
            + "\n\n".join(f"{h}\n{b}".rstrip() for h, b in removed)
            + "\n"
        )
        backup.write_text(backup_content, encoding="utf-8")

        # Write trimmed file
        f.write_text(rebuild(remaining), encoding="utf-8")

        new_lines = len(rebuild(remaining).split("\n"))
        return (
            f"auto-trimmed {len(removed)} oldest entries → {new_lines} lines "
            f"(backup: `{backup.name}`)"
        )
    except Exception:
        return None


def check_skill_learnings() -> Optional[str]:
    """Warn when any skill's learnings.md exceeds line thresholds.
    Auto-trims skills at CRITICAL by removing oldest entries (backup written first).
    """
    if not SKILLS_DIR.exists():
        return None
    trimmed_msgs, critical, warn = [], [], []
    for f in sorted(SKILLS_DIR.glob("*/learnings.md")):
        try:
            lines = len(f.read_text(encoding="utf-8", errors="ignore").splitlines())
            skill = f.parent.name
            if lines >= SKILL_CRITICAL_LINES:
                result = auto_trim_skill_learnings(f, skill)
                if result:
                    trimmed_msgs.append(f"`{skill}`: {result}")
                else:
                    critical.append(f"`{skill}` ({lines} lines)")
            elif lines >= SKILL_WARN_LINES:
                warn.append(f"`{skill}` ({lines} lines)")
        except Exception:
            pass
    parts = []
    if trimmed_msgs:
        parts.append(f"✂️ auto-trimmed: {'; '.join(trimmed_msgs)}")
    if critical:
        parts.append(f"🔴 critical (≥{SKILL_CRITICAL_LINES}, could not auto-trim): {', '.join(critical)}")
    if warn:
        parts.append(f"🟡 warn (≥{SKILL_WARN_LINES}): {', '.join(warn)}")
    if not parts:
        return None
    base = f"📚 **Skill learnings** — {'; '.join(parts)}."
    if warn or critical:
        base += " Large learnings.md files load fully on every skill invoke. Run `/distill-memory` to review."
    return base


def distill_idle_warning(global_count: int, project_count: int) -> Optional[str]:
    """Time-based distill suggestion — only fires when below count-based thresholds."""
    total = global_count + project_count
    if total < DISTILL_MIN_COUNT:
        return None
    # Count-based logic already handles high counts — don't double-fire
    if project_count >= WARN_THRESHOLD or global_count >= CRITICAL_THRESHOLD:
        return None
    last = last_distill_date()
    if last is None:
        days_idle = 999
    else:
        days_idle = (datetime.now(timezone.utc) - last).days
    if days_idle < DISTILL_IDLE_DAYS:
        return None
    idle_str = f"{days_idle}d ago" if last is not None else "never"
    return (
        f"💡 Last `/distill-memory` was **{idle_str}** ({total} memory entries total). "
        f"Consider running it to promote cross-project patterns and prune stale entries."
    )


def main():
    project_id = os.getcwd().replace("/", "-")
    project_mem = Path.home() / ".claude" / "projects" / project_id / "memory"
    global_mem = Path.home() / ".claude" / "memory"

    project_count = count_entries(project_mem)
    global_count = count_entries(global_mem)

    warnings: list = []

    stale_warn = stale_pipeline_warning(project_mem)
    if stale_warn:
        warnings.append(stale_warn)

    if project_count >= CRITICAL_THRESHOLD:
        warnings.append(
            f"🔴 Project memory has **{project_count} entries** (critical ≥ {CRITICAL_THRESHOLD}). "
            f"MEMORY.md truncates after 200 lines — echoed entries may be silently dropped. "
            f"Run `/distill-memory` before continuing."
        )
    elif project_count >= WARN_THRESHOLD:
        warnings.append(
            f"🟡 Project memory has **{project_count} entries** (warn ≥ {WARN_THRESHOLD}). "
            f"Consider `/distill-memory` to consolidate duplicates and promote cross-project lessons."
        )

    if global_count >= CRITICAL_THRESHOLD:
        warnings.append(
            f"🔴 Global memory has **{global_count} entries** — `/distill-memory` recommended."
        )

    skill_warn = check_skill_learnings()
    if skill_warn:
        warnings.append(skill_warn)

    distill_warn = distill_idle_warning(global_count, project_count)
    if distill_warn:
        warnings.append(distill_warn)

    hook_errors = recent_hook_errors()
    if hook_errors:
        total = sum(hook_errors.values())
        by_hook = ", ".join(f"{name}: {n}" for name, n in sorted(hook_errors.items()))
        warnings.append(
            f"🟠 **{total} hook error(s)** in last {HOOK_ERROR_WINDOW_HOURS}h ({by_hook}). "
            f"Inspect `~/.claude/logs/hook-errors.jsonl` or run `python3 ~/.claude/scripts/skill-report.py --errors`."
        )

    if not warnings:
        return

    body = "## ⚠️ SessionStart warnings\n\n" + "\n\n".join(warnings)
    print(json.dumps({"systemMessage": body}))


try:
    main()
except Exception:
    pass

sys.exit(0)
