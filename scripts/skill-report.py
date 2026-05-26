#!/usr/bin/env python3
"""Skill invocation analytics (MVP).

Reads ~/.claude/logs/skill-invocations-*.jsonl and prompts-*.jsonl, prints:
  - per-skill invocation count (configurable window)
  - top trigger phrases per skill (clustered by matched_phrase / prompt prefix)
  - silent skills (zero invokes in window)
  - skills declared by file in ~/.claude/skills/ but never invoked

Usage:
  skill-report.py                # last 30 days
  skill-report.py --days 7
  skill-report.py --skill sa     # detail for one skill
  skill-report.py --silent       # only show silent skills
  skill-report.py --errors       # dump recent hook errors for forensics
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOG_DIR = Path.home() / ".claude" / "logs"
SKILLS_DIR = Path.home() / ".claude" / "skills"


def load_jsonl(pattern: str, cutoff: datetime):
    rows = []
    for path in sorted(LOG_DIR.glob(pattern)):
        try:
            with path.open(encoding="utf-8") as f:
                for line in f:
                    try:
                        row = json.loads(line)
                    except Exception:
                        continue
                    ts = row.get("ts")
                    if not ts:
                        continue
                    try:
                        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    except Exception:
                        continue
                    if dt >= cutoff:
                        row["_dt"] = dt
                        rows.append(row)
        except Exception:
            continue
    return rows


def list_installed_skills():
    if not SKILLS_DIR.exists():
        return []
    return sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir() or p.is_symlink())


def correlate_prompts(invokes, prompts, window_sec=10):
    """Attach the most recent prompt within `window_sec` to each invoke (same session)."""
    by_session = defaultdict(list)
    for p in prompts:
        by_session[p.get("session")].append(p)
    for s in by_session.values():
        s.sort(key=lambda r: r["_dt"])
    for inv in invokes:
        candidates = by_session.get(inv.get("session"), [])
        best = None
        for p in candidates:
            delta = (inv["_dt"] - p["_dt"]).total_seconds()
            if 0 <= delta <= window_sec:
                best = p
        inv["_prompt"] = (best or {}).get("prompt")


def report_overview(invokes, days):
    counts = Counter(r["skill"] for r in invokes)
    installed = set(list_installed_skills())
    invoked = set(counts.keys())
    silent = sorted(installed - invoked)

    print(f"\n📊 Skill invocation report — last {days} days")
    print(f"Total invocations: {len(invokes)}")
    print(f"Installed skills:  {len(installed)}   Invoked: {len(invoked)}   Silent: {len(silent)}")
    print()
    print(f"{'skill':<20} {'count':>6}")
    print("-" * 28)
    for skill, n in counts.most_common():
        print(f"{skill:<20} {n:>6}")

    if silent:
        print("\n💤 Silent skills (no invokes in window):")
        for s in silent:
            print(f"  - {s}")


def report_skill_detail(invokes, skill):
    rows = [r for r in invokes if r["skill"] == skill]
    if not rows:
        print(f"No invocations for `{skill}` in window.")
        return

    print(f"\n🔍 Skill detail — `{skill}` ({len(rows)} invokes)")

    prompt_starts = Counter()
    for r in rows:
        p = r.get("_prompt") or ""
        if p:
            # cluster by first 40 chars (normalized)
            key = " ".join(p.split()[:6])[:40]
            prompt_starts[key] += 1

    if prompt_starts:
        print("\nTop trigger phrases:")
        for phrase, n in prompt_starts.most_common(10):
            print(f"  {n:>3}× {phrase}")
    else:
        print("(No prompt correlation available — run more sessions for data.)")


def report_hook_errors(days: int):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    err_file = LOG_DIR / "hook-errors.jsonl"
    if not err_file.exists():
        print("No hook-errors.jsonl — no errors recorded.")
        return

    rows = []
    with err_file.open(encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                dt = datetime.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            except Exception:
                continue
            if dt >= cutoff:
                rows.append(rec)

    if not rows:
        print(f"No hook errors in last {days} days.")
        return

    by_hook = Counter(r.get("hook", "?") for r in rows)
    print(f"\n🟠 Hook errors — last {days} days ({len(rows)} total)\n")
    for hook, n in by_hook.most_common():
        print(f"  {n:>3}× {hook}")

    print("\nRecent traces (newest 5):\n" + "-" * 60)
    for rec in rows[-5:]:
        print(f"\n[{rec.get('ts')}] {rec.get('hook')}")
        print(f"  {rec.get('error')}")
        tb = (rec.get("traceback") or "").strip().splitlines()
        for tline in tb[-6:]:  # last 6 traceback lines = where the error happened
            print(f"    {tline}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--skill", help="Show detail for one skill")
    ap.add_argument("--silent", action="store_true", help="List only silent skills")
    ap.add_argument("--errors", action="store_true", help="Show recent hook errors")
    args = ap.parse_args()

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    if args.errors:
        report_hook_errors(args.days)
        return

    invokes = load_jsonl("skill-invocations-*.jsonl", cutoff)
    prompts = load_jsonl("prompts-*.jsonl", cutoff)
    correlate_prompts(invokes, prompts)

    if args.silent:
        installed = set(list_installed_skills())
        invoked = {r["skill"] for r in invokes}
        for s in sorted(installed - invoked):
            print(s)
        return

    if args.skill:
        report_skill_detail(invokes, args.skill)
    else:
        report_overview(invokes, args.days)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
