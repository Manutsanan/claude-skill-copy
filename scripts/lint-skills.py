#!/usr/bin/env python3
"""Lint Claude Code skills and memory entries.

Usage:
  lint-skills.py              lint all skills + global memory + project memories
  lint-skills.py PATH ...     lint specific file or directory

Requires PyYAML. If the system Python lacks it, the script automatically
re-execs itself with ~/.claude/scripts/.venv/bin/python (created by setup.sh).
"""
import os
import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    venv_py = os.path.expanduser("~/.claude/scripts/.venv/bin/python")
    if os.path.exists(venv_py) and not os.environ.get("_LINT_SKILLS_RELAUNCHED"):
        os.environ["_LINT_SKILLS_RELAUNCHED"] = "1"
        os.execv(venv_py, [venv_py] + sys.argv)
    sys.exit(
        "ERROR: PyYAML missing. Install via:\n"
        "  python3 -m venv ~/.claude/scripts/.venv && \\\n"
        "  ~/.claude/scripts/.venv/bin/pip install pyyaml\n"
        "or re-run scripts/setup.sh from the repo."
    )

HOME = Path.home()
SKILLS_DIR = HOME / ".claude" / "skills"
MEMORY_DIR = HOME / ".claude" / "memory"
PROJECTS_DIR = HOME / ".claude" / "projects"

VALID_MEMORY_TYPES = {"user", "feedback", "project", "reference"}
VALID_SKILL_TAGS = {"fe", "ux", "sa", "debug", "migrate", "audit", "cross"}
VALID_SCOPES = {"global", "project"}

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK = re.compile(r"\[\[([a-z0-9_-]+)\]\]")
INDEX_LINK = re.compile(r"\[[^\]]+\]\(([^)]+\.md)\)")

errors: list[str] = []
warnings: list[str] = []


def err(path: Path, msg: str) -> None:
    errors.append(f"[FAIL] {path}: {msg}")


def warn(path: Path, msg: str) -> None:
    warnings.append(f"[WARN] {path}: {msg}")


FIELD_LINE = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")


def parse_frontmatter(path: Path, lenient: bool = False):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("missing leading '---'")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("missing closing '---'")

    block = parts[1]
    try:
        fm = yaml.safe_load(block)
        if not isinstance(fm, dict):
            raise ValueError("frontmatter is not a YAML mapping")
        return fm, parts[2]
    except yaml.YAMLError:
        if not lenient:
            raise
        fm: dict = {}
        for line in block.splitlines():
            if line.startswith(" ") or line.startswith("\t"):
                continue
            m = FIELD_LINE.match(line)
            if m:
                fm[m.group(1)] = m.group(2)
        return fm, parts[2]


def slug_normalize(s: str) -> str:
    return s.replace("_", "-").lower()


def lint_memory_file(path: Path) -> str | None:
    try:
        fm, body = parse_frontmatter(path, lenient=False)
    except yaml.YAMLError:
        warn(path, "frontmatter has YAML parse issue (likely ': ' in prose) — fell back to line-based parse")
        try:
            fm, body = parse_frontmatter(path, lenient=True)
        except Exception as e:
            err(path, f"frontmatter unrecoverable: {e}")
            return None
    except Exception as e:
        err(path, f"frontmatter: {e}")
        return None

    for key in ("name", "description"):
        if key not in fm or fm[key] in (None, ""):
            warn(path, f"missing field '{key}'")

    name = fm.get("name") or ""
    is_kebab = bool(KEBAB.match(name)) if name else False
    if name and not is_kebab:
        warn(path, f"name '{name}' not kebab-case (convention drift)")

    if is_kebab:
        stem_norm = slug_normalize(path.stem)
        name_norm = slug_normalize(name)
        if name_norm not in stem_norm and stem_norm not in name_norm:
            warn(path, f"name '{name}' doesn't match filename '{path.stem}'")

    meta = fm.get("metadata")
    if meta is None:
        warn(path, "missing 'metadata' block (convention drift)")
    elif not isinstance(meta, dict):
        err(path, "metadata is not a mapping")
    else:
        t = meta.get("type")
        if t is None:
            warn(path, "metadata.type missing")
        elif t not in VALID_MEMORY_TYPES:
            err(path, f"metadata.type '{t}' not in {sorted(VALID_MEMORY_TYPES)}")

        s = meta.get("skill")
        if s is not None and s not in VALID_SKILL_TAGS:
            err(path, f"metadata.skill '{s}' not in {sorted(VALID_SKILL_TAGS)}")

        sc = meta.get("scope")
        if sc is not None and sc not in VALID_SCOPES:
            err(path, f"metadata.scope '{sc}' not in {sorted(VALID_SCOPES)}")

    return name if is_kebab else None


def lint_memory_dir(dir_path: Path) -> None:
    if not dir_path.exists():
        return

    entries = [md for md in sorted(dir_path.glob("*.md")) if md.name != "MEMORY.md"]
    if not entries:
        return

    index = dir_path / "MEMORY.md"
    indexed: set[str] = set()
    if index.exists():
        for m in INDEX_LINK.finditer(index.read_text(encoding="utf-8")):
            indexed.add(m.group(1))
    else:
        warn(dir_path, "no MEMORY.md index (dir has entries)")

    on_disk: set[str] = set()
    names_seen: set[str] = set()

    for md in entries:
        on_disk.add(md.name)
        name = lint_memory_file(md)
        if name:
            names_seen.add(name)

    if index.exists():
        for fname in sorted(on_disk - indexed):
            warn(index, f"file '{fname}' exists but not listed in index")
        for fname in sorted(indexed - on_disk):
            err(index, f"index references '{fname}' but file missing")

    for md in dir_path.glob("*.md"):
        if md.name == "MEMORY.md":
            continue
        text = md.read_text(encoding="utf-8")
        if text.startswith("---"):
            text = text.split("---", 2)[-1]
        for m in LINK.finditer(text):
            target = m.group(1)
            if target not in names_seen:
                warn(md, f"orphan link [[{target}]]")


def lint_skill_dir(dir_path: Path) -> None:
    if dir_path.is_symlink() and not dir_path.exists():
        err(dir_path, f"broken symlink -> {dir_path.readlink()}")
        return

    skill_md = dir_path / "SKILL.md"
    if not skill_md.exists():
        err(dir_path, "missing SKILL.md")
        return

    try:
        fm, body = parse_frontmatter(skill_md, lenient=True)
    except Exception as e:
        err(skill_md, f"frontmatter: {e}")
        return

    for key in ("name", "description"):
        if key not in fm or fm[key] in (None, ""):
            err(skill_md, f"missing required field '{key}'")


def lint_all() -> None:
    if SKILLS_DIR.exists():
        for entry in sorted(SKILLS_DIR.iterdir()):
            if entry.is_dir() or entry.is_symlink():
                if entry.name.startswith("."):
                    continue
                lint_skill_dir(entry)

    lint_memory_dir(MEMORY_DIR)

    if PROJECTS_DIR.exists():
        for proj in sorted(PROJECTS_DIR.iterdir()):
            memdir = proj / "memory"
            if memdir.is_dir():
                lint_memory_dir(memdir)


def lint_path(target: str) -> None:
    p = Path(target).expanduser().resolve()

    if p.is_dir():
        if p.parent.resolve() == SKILLS_DIR.resolve():
            lint_skill_dir(p)
        elif p.name == "memory" or "memory" in {x.name for x in p.parents}:
            lint_memory_dir(p)
        else:
            warn(p, "directory not recognized as skill or memory dir")
        return

    if not p.exists():
        err(p, "path does not exist")
        return

    parts = set(p.parts)
    if p.name == "SKILL.md":
        lint_skill_dir(p.parent)
    elif p.name == "MEMORY.md":
        lint_memory_dir(p.parent)
    elif "memory" in parts:
        lint_memory_file(p)
    elif "skills" in parts:
        lint_skill_dir(p.parent)
    else:
        warn(p, "path not recognized as skill or memory file")


def main() -> int:
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            lint_path(arg)
    else:
        lint_all()

    out = sys.stderr
    for line in warnings:
        print(line, file=out)
    for line in errors:
        print(line, file=out)

    if errors or warnings:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)", file=out)
    else:
        print("lint passed", file=out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
