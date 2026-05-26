#!/usr/bin/env python3
"""
Stop-hook payload (JSON) → Telegram message styled like a Pull Request.

Layout (single message, auto-split at area boundaries if > 3900 chars):

  🚀 Claude PR · 📁 project
  📌 <Title>                              ← first meaningful line of Claude's text
  📝 Summary
  • bullet 1                              ← bullets parsed from Claude's text
  • bullet 2                              ← fallback: first few sentences
  📊 N files · +abc −xyz                  ← total stats
  📂 Changes
  ▸ layers/reports
    📄 file.vue  +45 −38
       ปรับหลายส่วน — กระทบ template + script   ← heuristic per-file summary
  ▸ .claude/hooks
    📄 file.py  +120 −15
       rewrite ใหญ่ — เพิ่ม heuristic_summary, …
  🔧 Tools: Edit ×2, Write ×3

Skips silently (exit 0) when the turn has no Edit/Write/NotebookEdit/MultiEdit.

Env vars (set by the .sh wrapper):
  - TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID  (required)
"""
import sys, json, os, re, html, time, urllib.request, urllib.parse, difflib, subprocess
from collections import Counter, OrderedDict
from pathlib import Path

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

BRIDGE_DIR = Path.home() / ".claude" / "tools" / "tg-bridge"
MAPPINGS_FILE = BRIDGE_DIR / "mappings.json"
MAPPING_CAP = 500

MAX_MSG = 3900
DIFF_CONTEXT = 3
FILE_DIFF_CAP = 12
TITLE_MAX = 90
BULLET_MAX_LEN = 320     # visible chars per bullet — fit a full descriptive line
BULLET_CAP = 10          # carry the full bullet list, not just the first few


# ─── Telegram sender ──────────────────────────────────────────────────────────

def send_message(text: str) -> int | None:
    """Send a Telegram message. Returns the Telegram message_id on success,
    or None on failure / empty input."""
    if not BOT_TOKEN or not CHAT_ID or not text.strip():
        return None
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "parse_mode": "HTML",
        "text": text,
        "disable_web_page_preview": "true",
    }).encode()
    try:
        raw = urllib.request.urlopen(f"{TG_API}/sendMessage", data=data, timeout=10).read()
        resp = json.loads(raw.decode())
        if resp.get("ok"):
            return resp.get("result", {}).get("message_id")
    except Exception:
        pass
    return None


# ─── Mapping store (telegram message_id → Claude session_id) ──────────────────

def record_mapping(message_id: int, session_id: str, cwd: str, project: str) -> None:
    """Append a Telegram message_id → session mapping so the tg-bridge daemon
    can route replies back to the right Claude Code session."""
    if not message_id or not session_id:
        return
    try:
        BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
        existing: list[dict] = []
        if MAPPINGS_FILE.exists():
            try:
                existing = json.loads(MAPPINGS_FILE.read_text())
                if not isinstance(existing, list):
                    existing = []
            except Exception:
                existing = []
        existing.append({
            "message_id": message_id,
            "session_id": session_id,
            "cwd": cwd,
            "project": project,
            "sent_at": int(time.time()),
        })
        # Roll: keep last N entries
        if len(existing) > MAPPING_CAP:
            existing = existing[-MAPPING_CAP:]
        MAPPINGS_FILE.write_text(json.dumps(existing, ensure_ascii=False))
    except Exception:
        pass


# ─── Transcript parsing ───────────────────────────────────────────────────────

def fail_silent() -> None:
    sys.exit(0)


try:
    payload = json.load(sys.stdin)
except Exception:
    fail_silent()

cwd = payload.get("cwd", "")
project = os.path.basename(cwd) or "unknown"
transcript_path = payload.get("transcript_path", "")
session_id = payload.get("session_id", "") or ""

if not transcript_path or not os.path.exists(transcript_path):
    fail_silent()


def wait_for_stable_transcript(path: str, max_wait: float = 2.0, stable_for: float = 0.3) -> None:
    """Poll the transcript file until its size stays unchanged for `stable_for`
    seconds (or `max_wait` elapses). Handles the race where Claude Code fires
    the Stop hook before the assistant's final text block is flushed to disk."""
    last_size = -1
    stable_start = None
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            size = os.path.getsize(path)
        except OSError:
            size = -1
        if size == last_size:
            if stable_start is None:
                stable_start = time.time()
            elif time.time() - stable_start >= stable_for:
                return
        else:
            last_size = size
            stable_start = None
        time.sleep(0.1)


wait_for_stable_transcript(transcript_path)

try:
    with open(transcript_path) as f:
        lines = [json.loads(l) for l in f if l.strip()]
except Exception:
    fail_silent()


def is_real_user_msg(entry) -> bool:
    if entry.get("type") != "user":
        return False
    content = entry.get("message", {}).get("content", "")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        return any(isinstance(b, dict) and b.get("type") == "text" for b in content)
    return False


boundary_idx = 0
for i in range(len(lines) - 1, -1, -1):
    if is_real_user_msg(lines[i]):
        boundary_idx = i
        break

MOD_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}

tool_use_by_id: dict[str, dict] = {}
for entry in lines:
    if entry.get("type") != "assistant":
        continue
    for block in entry.get("message", {}).get("content", []) or []:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            tid = block.get("id")
            if tid:
                tool_use_by_id[tid] = block


def iter_tool_results(entry):
    content = entry.get("message", {}).get("content", [])
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                yield b


def extract_text(tr) -> str:
    c = tr.get("content", "")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(
            b.get("text", "") for b in c
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


LINE_PREFIX = re.compile(r"^\s*\d+\t(.*)$")


def strip_line_numbers(text: str) -> str:
    kept = []
    for line in text.splitlines():
        m = LINE_PREFIX.match(line)
        if m:
            kept.append(m.group(1))
    if not kept:
        return ""
    return "\n".join(kept) + "\n"


# Snapshot latest known content of each file from Read tool_results
read_snapshots: dict[str, str] = {}
for entry in lines:
    if entry.get("type") != "user":
        continue
    for tr in iter_tool_results(entry):
        if tr.get("is_error"):
            continue
        tu = tool_use_by_id.get(tr.get("tool_use_id", ""))
        if not tu or tu.get("name") != "Read":
            continue
        fp = (tu.get("input") or {}).get("file_path")
        if not fp:
            continue
        body = extract_text(tr)
        stripped = strip_line_numbers(body)
        if stripped:
            read_snapshots[fp] = stripped


# ─── Collect modifications + final assistant text in current turn ─────────────

modifications: list[dict] = []
tool_counts: Counter = Counter()
text_blocks: list[str] = []
turn_tokens: dict[str, int] = {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0}
turn_model: str = ""

for entry in lines[boundary_idx:]:
    if entry.get("type") != "assistant":
        continue
    msg = entry.get("message") or {}
    usage = msg.get("usage") or {}
    turn_tokens["input"] += usage.get("input_tokens", 0)
    turn_tokens["output"] += usage.get("output_tokens", 0)
    turn_tokens["cache_read"] += usage.get("cache_read_input_tokens", 0)
    turn_tokens["cache_create"] += usage.get("cache_creation_input_tokens", 0)
    if not turn_model and msg.get("model"):
        turn_model = msg["model"]
    for block in entry.get("message", {}).get("content", []) or []:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        if btype == "tool_use":
            name = block.get("name", "?")
            tool_counts[name] += 1
            if name not in MOD_TOOLS:
                continue
            inp = block.get("input", {}) or {}
            fp = inp.get("file_path") or inp.get("notebook_path") or ""
            if not fp:
                continue
            if name == "Edit":
                modifications.append({
                    "file": fp, "kind": "edit",
                    "old": inp.get("old_string", ""),
                    "new": inp.get("new_string", ""),
                })
            elif name == "MultiEdit":
                for e in inp.get("edits", []) or []:
                    modifications.append({
                        "file": fp, "kind": "edit",
                        "old": e.get("old_string", ""),
                        "new": e.get("new_string", ""),
                    })
            elif name == "Write":
                new_content = inp.get("content", "")
                old_content = read_snapshots.get(fp, "")
                modifications.append({
                    "file": fp, "kind": "write",
                    "old": old_content, "new": new_content,
                })
                read_snapshots[fp] = new_content
            elif name == "NotebookEdit":
                modifications.append({
                    "file": fp, "kind": "edit",
                    "old": inp.get("old_string", "") or inp.get("old_source", ""),
                    "new": inp.get("new_string", "") or inp.get("new_source", ""),
                })
        elif btype == "text":
            txt = block.get("text", "").strip()
            if txt:
                text_blocks.append(txt)

# ─── GitHub PR detection ──────────────────────────────────────────────────────

pr_bash_ids: dict[str, str] = {}   # tool_use_id → "create" | "edit"
for entry in lines[boundary_idx:]:
    if entry.get("type") != "assistant":
        continue
    for block in entry.get("message", {}).get("content", []) or []:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        if block.get("name") != "Bash":
            continue
        cmd = (block.get("input") or {}).get("command", "")
        if "gh pr create" in cmd:
            pr_bash_ids[block.get("id", "")] = "create"
        elif "gh pr edit" in cmd:
            pr_bash_ids[block.get("id", "")] = "edit"

pr_events: list[dict] = []
if pr_bash_ids:
    for entry in lines[boundary_idx:]:
        if entry.get("type") != "user":
            continue
        for tr in iter_tool_results(entry):
            tid = tr.get("tool_use_id", "")
            if tid not in pr_bash_ids:
                continue
            text = extract_text(tr)
            m = re.search(r"https://github\.com/[^\s\n]+/pull/\d+", text)
            if m:
                pr_events.append({"url": m.group(), "kind": pr_bash_ids[tid]})

if not modifications and not pr_events:
    fail_silent()


# Pick the most descriptive text block as our summary source.
# Prefer the block with the most markdown bullets (richer description);
# break ties by length, then by recency (later block wins on ties).
def _score_text(t: str) -> tuple[int, int]:
    bullet_count = sum(1 for ln in t.splitlines() if re.match(r"^\s*[-*•]\s+", ln))
    return (bullet_count, len(t))


last_text = ""
best_score: tuple[int, int] = (-1, -1)
for t in text_blocks:
    s = _score_text(t)
    if s >= best_score:
        best_score = s
        last_text = t


# ─── Diff generation ──────────────────────────────────────────────────────────

def make_unified_diff(old: str, new: str, label: str) -> str:
    old_lines = old.splitlines(keepends=True) if old else []
    new_lines = new.splitlines(keepends=True) if new else []
    if old_lines and not old_lines[-1].endswith("\n"):
        old_lines[-1] += "\n"
    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] += "\n"
    return "".join(difflib.unified_diff(
        old_lines, new_lines,
        fromfile=f"a/{label}", tofile=f"b/{label}",
        n=DIFF_CONTEXT,
    ))


def make_new_file_diff(new: str, label: str) -> str:
    lines = new.splitlines(keepends=True) or [""]
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    return f"--- /dev/null\n+++ b/{label}\n" + "".join("+" + ln for ln in lines)


def diff_stats(diff_text: str) -> tuple[int, int]:
    plus = minus = 0
    for ln in diff_text.split("\n"):
        if ln.startswith("+") and not ln.startswith("+++"):
            plus += 1
        elif ln.startswith("-") and not ln.startswith("---"):
            minus += 1
    return plus, minus


by_file: "OrderedDict[str, list[dict]]" = OrderedDict()
for m in modifications:
    by_file.setdefault(m["file"], []).append(m)


def rel_of(fp: str) -> str:
    if cwd and fp.startswith(cwd):
        return os.path.relpath(fp, cwd)
    return os.path.basename(fp)


def compute_diff(fp: str, mods: list[dict]) -> str:
    rel = rel_of(fp)
    sections = []
    for idx, m in enumerate(mods, 1):
        label = f"{rel} (#{idx})" if len(mods) > 1 else rel
        if m["kind"] == "write" and not m["old"]:
            sections.append(make_new_file_diff(m["new"], label))
        else:
            d = make_unified_diff(m["old"], m["new"], label)
            if d:
                sections.append(d)
    return "\n".join(sections)


file_paths = list(by_file.keys())
files_to_detail = file_paths[:FILE_DIFF_CAP]
files_omitted = len(file_paths) - len(files_to_detail)

file_diffs: "OrderedDict[str, str]" = OrderedDict()
for fp in files_to_detail:
    file_diffs[fp] = compute_diff(fp, by_file[fp])


# ─── Heuristic per-file summary ───────────────────────────────────────────────

RE_PY_DEF = re.compile(r"^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)")
RE_JS_FN = re.compile(
    r"^\s*(?:export\s+(?:default\s+)?)?(?:async\s+)?function\s+([A-Za-z_]\w*)"
)
RE_JS_CONST = re.compile(r"^\s*(?:export\s+)?const\s+([A-Za-z_]\w*)\s*=")
RE_SH_FN = re.compile(r"^\s*(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{")

RE_TEMPLATE_HINT = re.compile(
    r"<(?:template|/?[A-Za-z][\w-]*)|v-[a-z]+|@[a-z]+|:[a-z][\w-]*="
)
RE_SCRIPT_HINT = re.compile(
    r"\b(?:const|let|var|function|return|import|export|await|async|definePageMeta"
    r"|computed|watch(?:Effect)?|ref\b|reactive|useRoute|useFetch|useState"
    r"|onMounted|onUnmounted)\b"
)
RE_STYLE_HINT = re.compile(
    r"^\s*[.#@][\w-]+\s*\{|^\s*[\w-]+\s*:\s*[^;}]+;\s*$|@media|@page"
)


def collect_top_idents(lines: list[str], ext: str, limit: int = 4) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for ln in lines:
        candidates: list[str] = []
        if ext == ".py":
            m = RE_PY_DEF.match(ln)
            if m:
                candidates.append(m.group(1))
        elif ext in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".vue"}:
            for rx in (RE_JS_FN, RE_JS_CONST):
                m = rx.match(ln)
                if m:
                    candidates.append(m.group(1))
                    break
        elif ext in {".sh", ".bash"}:
            m = RE_SH_FN.match(ln)
            if m:
                candidates.append(m.group(1))
        for name in candidates:
            if name in {"_", "__"} or len(name) <= 1:
                continue
            if name not in seen:
                seen.add(name)
                found.append(name)
                if len(found) >= limit:
                    return found
    return found


def detect_vue_sections(plus_lines: list[str], minus_lines: list[str]) -> list[str]:
    has: set[str] = set()
    for ln in plus_lines + minus_lines:
        stripped = ln.lstrip()
        if not stripped or stripped.startswith("//"):
            continue
        if RE_STYLE_HINT.search(ln):
            has.add("style")
            continue
        if RE_TEMPLATE_HINT.search(ln):
            has.add("template")
            continue
        if RE_SCRIPT_HINT.search(ln):
            has.add("script")
    return [s for s in ("template", "script", "style") if s in has]


def heuristic_summary(diff_text: str, file_path: str) -> dict:
    """Return structured change info so the renderer can format it on multiple lines."""
    plus_lines: list[str] = []
    minus_lines: list[str] = []
    for ln in diff_text.split("\n"):
        if ln.startswith("+++") or ln.startswith("---") or ln.startswith("@@"):
            continue
        if ln.startswith("+"):
            plus_lines.append(ln[1:])
        elif ln.startswith("-"):
            minus_lines.append(ln[1:])

    ext = os.path.splitext(file_path)[1].lower()
    is_new = diff_text.startswith("--- /dev/null")
    p, m = len(plus_lines), len(minus_lines)

    empty = {
        "is_new": False, "plus": 0, "minus": 0,
        "size": "", "vue_sections": [],
        "added": [], "removed": [],
    }
    if not plus_lines and not minus_lines:
        return empty

    if is_new:
        return {
            "is_new": True,
            "plus": p, "minus": 0,
            "size": f"ไฟล์ใหม่ {p} บรรทัด",
            "vue_sections": [],
            "added": collect_top_idents(plus_lines, ext, limit=4),
            "removed": [],
        }

    total = p + m
    if total > 300:
        size = "rewrite ใหญ่"
    elif total > 80:
        size = "ปรับหลายส่วน"
    elif total > 20:
        size = "ปรับปานกลาง"
    else:
        size = "ปรับเล็กน้อย"

    sections = detect_vue_sections(plus_lines, minus_lines) if ext == ".vue" else []

    new_ids = collect_top_idents(plus_lines, ext, limit=4)
    gone_ids = collect_top_idents(minus_lines, ext, limit=4)
    added = [i for i in new_ids if i not in gone_ids][:4]
    removed = [i for i in gone_ids if i not in new_ids][:4]

    return {
        "is_new": False,
        "plus": p, "minus": m,
        "size": size,
        "vue_sections": sections,
        "added": added,
        "removed": removed,
    }


file_changes: dict[str, dict] = {
    fp: heuristic_summary(file_diffs[fp], fp) for fp in files_to_detail
}


# ─── PR-style title + summary extraction from last_text ───────────────────────

BT = chr(96)


def clean_inline(text: str) -> str:
    """Strip markdown to plain text (used for length measurement + title)."""
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(BT + r"([^" + BT + r"]+)" + BT, r"\1", text)
    return text.strip()


def visible_len(md_text: str) -> int:
    """Length of text as it will render — without markdown markers."""
    return len(clean_inline(md_text))


def fix_unclosed_md(text: str) -> str:
    """Trim back any unmatched ** or ` so md→HTML conversion stays well-formed."""
    while text.count("**") % 2 != 0:
        idx = text.rfind("**")
        text = text[:idx]
    while text.count(BT) % 2 != 0:
        idx = text.rfind(BT)
        text = text[:idx]
    return text


def inline_md_to_html(text: str) -> str:
    """Convert **bold** + `code` markdown to Telegram HTML; HTML-escape everything else.

    Two-phase: stash markdown spans behind null-byte placeholders → escape the
    remaining plain text → expand placeholders with escaped content wrapped in tags.
    Keeps user emphasis (bold prefixes like 'โครงสร้าง:' and code identifiers)
    that would otherwise be lost.
    """
    placeholders: list[tuple[str, str]] = []

    def stash(content: str, tag: str) -> str:
        idx = len(placeholders)
        placeholders.append((tag, content))
        return f"\x00{idx}\x00"

    text = re.sub(BT + r"([^" + BT + r"]+)" + BT, lambda m: stash(m.group(1), "code"), text)
    text = re.sub(r"\*\*([^*]+)\*\*", lambda m: stash(m.group(1), "b"), text)
    text = re.sub(r"__([^_]+)__", lambda m: stash(m.group(1), "b"), text)

    text = html.escape(text)

    def expand(m: re.Match) -> str:
        idx = int(m.group(1))
        tag, content = placeholders[idx]
        return f"<{tag}>{html.escape(content)}</{tag}>"

    return re.sub(r"\x00(\d+)\x00", expand, text)


def shorten_plain(text: str, max_len: int) -> str:
    """Truncate plain text at the nicest sentence/word boundary."""
    if len(text) <= max_len:
        return text
    cut = text[:max_len]
    for ch in ("ฯ", ".", "!", "?", "—", " "):
        idx = cut.rfind(ch)
        if idx > max_len * 0.55:
            return cut[: idx + 1].rstrip().rstrip(".") + "…"
    return cut.rstrip() + "…"


def shorten_md(text: str, max_visible: int) -> str:
    """Truncate markdown text targeting a visible-character cap.

    Binary search for the longest prefix that — after closing any dangling
    `**` / `` ` `` markers — fits the cap. Lets bullets stay long enough to be
    informative while still respecting Telegram message-size constraints.
    """
    if visible_len(text) <= max_visible:
        return text
    lo, hi = 0, len(text)
    best = ""
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = fix_unclosed_md(text[:mid])
        if visible_len(candidate) <= max_visible:
            best = candidate
            lo = mid + 1
        else:
            hi = mid - 1
    best = best.rstrip(" \t-—•·.")
    return (best + "…") if best else text[:max_visible]


def extract_title(text: str) -> str:
    if not text:
        return "Update"
    cleaned = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for raw_line in cleaned.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "|", ">", "---")):
            continue
        # Drop leading bullet marker if present
        line = re.sub(r"^[-*•]\s+", "", stripped)
        line = clean_inline(line)
        if not line:
            continue
        return shorten_plain(line, TITLE_MAX)
    return "Update"


def extract_bullets(text: str, title: str) -> list[str]:
    """Return HTML-formatted bullet strings (already escaped + tagged).

    Preserves **bold** and `code` markdown so descriptive prefixes like
    'โครงสร้าง:' and code identifiers stay visually distinct in Telegram.
    """
    if not text:
        return []
    cleaned = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    raw_bullets: list[str] = []

    # Pass 1: explicit markdown bullets
    for raw_line in cleaned.splitlines():
        stripped = raw_line.strip()
        m = re.match(r"^[-*•]\s+(.+)", stripped)
        if not m:
            continue
        content = m.group(1).strip()
        if content:
            raw_bullets.append(content)
            if len(raw_bullets) >= BULLET_CAP:
                break

    # Pass 2: sentence-based fallback when no bullets were found
    if not raw_bullets:
        body = clean_inline(cleaned)
        title_core = title.rstrip("…").strip()
        if title_core and title_core in body:
            body = body.replace(title_core, "", 1).strip()
        sentences = re.split(r"(?<=[.!?ฯ])\s+|\n+", body)
        for s in sentences:
            s = s.strip(" \t-—•·")
            if len(s) < 8:
                continue
            raw_bullets.append(s)
            if len(raw_bullets) >= 5:
                break

    return [
        inline_md_to_html(shorten_md(b, BULLET_MAX_LEN))
        for b in raw_bullets
    ]


# ─── Group files by area (directory) for PR-style "Changes" section ───────────

def area_of(rel_path: str) -> str:
    parts = rel_path.split(os.sep)
    if len(parts) <= 1:
        return "."
    if parts[0] == "layers" and len(parts) >= 2:
        return f"layers/{parts[1]}"
    if parts[0].startswith("."):                 # .claude/, .github/, etc.
        return "/".join(parts[:2]) if len(parts) >= 2 else parts[0]
    if len(parts) >= 3:
        return "/".join(parts[:2])
    return parts[0]


def group_by_area(fps: list[str]) -> "OrderedDict[str, list[str]]":
    groups: "OrderedDict[str, list[str]]" = OrderedDict()
    for fp in fps:
        groups.setdefault(area_of(rel_of(fp)), []).append(fp)
    return groups


# ─── Compose PR-style message ─────────────────────────────────────────────────

title = extract_title(last_text)
bullets = extract_bullets(last_text, title)

total_plus = sum(c["plus"] for c in file_changes.values())
total_minus = sum(c["minus"] for c in file_changes.values())

NOISY = {"Read", "Grep", "Glob"}
display_tools = [(n, c) for n, c in tool_counts.most_common() if n not in NOISY]
hidden_count = sum(c for n, c in tool_counts.items() if n in NOISY)
tool_parts = [f"{n} ×{c}" for n, c in display_tools]
if hidden_count:
    tool_parts.append(f"lookup ×{hidden_count}")
tools_line = ", ".join(tool_parts) if tool_parts else "(none)"

groups = group_by_area(files_to_detail)


def render_file_block(fp: str, area: str) -> str:
    """Render one file as a <blockquote> with the filename + multi-line summary."""
    h = file_changes[fp]
    rel = rel_of(fp)
    if area != "." and rel.startswith(area + os.sep):
        display = rel[len(area) + 1 :]
    else:
        display = rel

    lines = [f"<b>📄 {html.escape(display)}</b>"]

    if h["is_new"]:
        lines.append(f"✨ {h['size']}")
    elif h["plus"] or h["minus"]:
        head = f"<code>+{h['plus']} −{h['minus']}</code>"
        if h["size"]:
            head += f" · {h['size']}"
        lines.append(head)
    elif h["size"]:
        lines.append(h["size"])

    if h["vue_sections"]:
        lines.append(f"🎯 {' + '.join(h['vue_sections'])}")

    if h["added"]:
        items = ", ".join(html.escape(s) for s in h["added"])
        lines.append(f"➕ {items}")

    if h["removed"]:
        items = ", ".join(html.escape(s) for s in h["removed"])
        lines.append(f"➖ {items}")

    return "<blockquote>" + "\n".join(lines) + "</blockquote>"


# Build header/intro
header_block = f"🚀 <b>Claude PR</b> · 📁 <code>{html.escape(project)}</code>"
title_block = f"📌 <b>{html.escape(title)}</b>"

if bullets:
    # bullets are already HTML-formatted by extract_bullets (escaped + <b>/<code> tags)
    bullet_lines = "\n".join(f"• {b}" for b in bullets)
    summary_block = f"📝 <b>Summary</b>\n{bullet_lines}"
else:
    summary_block = ""

stats_block = (
    f"📊 <b>{len(file_paths)} file"
    f"{'s' if len(file_paths) != 1 else ''}</b> · "
    f"<code>+{total_plus} −{total_minus}</code>"
)

# Build per-area blocks for Changes section
area_blocks: list[str] = []
for area, fps in groups.items():
    sub_lines = [f"📁 <b>{html.escape(area)}/</b>"]
    for fp in fps:
        sub_lines.append(render_file_block(fp, area))
    area_blocks.append("\n".join(sub_lines))

if files_omitted:
    area_blocks.append(f"<i>… +{files_omitted} more file(s)</i>")

tools_block = f"🔧 <b>Tools</b>: {html.escape(tools_line)}"

def fmt_tok(n: int) -> str:
    return f"{n:,}"

def fmt_model(raw: str) -> str:
    """claude-opus-4-7 → Opus 4.7 (short display name)."""
    m = re.match(r"claude-(\w+)-([\d]+)[\.-]?([\d]*)", raw)
    if not m:
        return raw
    family = m.group(1).capitalize()
    major = m.group(2)
    minor = m.group(3)
    return f"{family} {major}.{minor}" if minor else f"{family} {major}"

tok_parts = [
    f"in {fmt_tok(turn_tokens['input'])}",
    f"out {fmt_tok(turn_tokens['output'])}",
]
if turn_tokens["cache_read"]:
    tok_parts.append(f"⚡{fmt_tok(turn_tokens['cache_read'])}")
if turn_tokens["cache_create"]:
    tok_parts.append(f"💾{fmt_tok(turn_tokens['cache_create'])}")
model_str = f" · 🤖 <code>{html.escape(fmt_model(turn_model))}</code>" if turn_model else ""
tokens_block = "🪙 <b>Tokens</b>: <code>" + " · ".join(tok_parts) + "</code>" + model_str

# Assemble
intro_sections = [header_block, title_block]
if summary_block:
    intro_sections.append(summary_block)
intro_sections.append(stats_block)
intro_block = "\n\n".join(intro_sections)

changes_header = "📂 <b>Changes</b>"
changes_full = changes_header
if area_blocks:
    changes_full += "\n\n" + "\n\n".join(area_blocks)

full = "\n\n".join([intro_block, changes_full, tools_block, tokens_block])

def fetch_pr_info(url: str) -> dict:
    try:
        m = re.search(r"github\.com/([^/]+/[^/]+)/pull/(\d+)", url)
        if not m:
            return {}
        repo, number = m.group(1), m.group(2)
        raw = subprocess.check_output(
            ["gh", "pr", "view", number, "--repo", repo,
             "--json", "number,title,url"],
            timeout=10, stderr=subprocess.DEVNULL,
        )
        return json.loads(raw.decode())
    except Exception:
        return {}


def build_pr_message(event: dict) -> str:
    kind = event["kind"]
    url = event["url"]
    icon = "🔀" if kind == "create" else "✏️"
    label = "PR Created" if kind == "create" else "PR Updated"

    info = fetch_pr_info(url)
    number = info.get("number", "")
    pr_title = info.get("title", "")

    parts = [f"{icon} <b>{label}</b> · 📁 <code>{html.escape(project)}</code>"]
    if number and pr_title:
        parts.append(
            f'📌 <b>#{number}</b> · <a href="{url}">{html.escape(pr_title)}</a>'
        )
    else:
        parts.append(f'🔗 <a href="{url}">{html.escape(url)}</a>')

    if bullets:
        bullet_lines = "\n".join(f"• {b}" for b in bullets[:5])
        parts.append(f"📝 <b>Overview</b>\n{bullet_lines}")

    return "\n\n".join(parts)


def send_and_map(text: str) -> None:
    """Send a Telegram message and record its message_id → session_id mapping
    so the tg-bridge daemon can route replies back here."""
    mid = send_message(text)
    if mid is not None:
        record_mapping(mid, session_id, cwd, project)


# ─── Send PR notifications ────────────────────────────────────────────────────
for event in pr_events:
    send_and_map(build_pr_message(event))

if not modifications:
    sys.exit(0)

# ─── Send file-change notification ────────────────────────────────────────────
if len(full) <= MAX_MSG:
    send_and_map(full)
else:
    # Split: intro first, then changes (split per area), then tools
    send_and_map(intro_block)
    current = changes_header
    for ab in area_blocks:
        candidate = current + "\n\n" + ab
        if len(candidate) <= MAX_MSG:
            current = candidate
            continue
        if current and current != changes_header:
            send_and_map(current)
            current = changes_header + "\n\n" + ab
        else:
            # Single area too large → hard truncate
            send_and_map((current + "\n\n" + ab)[: MAX_MSG - 3] + "...")
            current = changes_header
    if current and current != changes_header:
        send_and_map(current)
    send_and_map(tools_block + "\n\n" + tokens_block)

sys.exit(0)
