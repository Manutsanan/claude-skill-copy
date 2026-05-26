#!/usr/bin/env bash
set -euo pipefail

# Bootstrap a fresh machine to behave like the upstream skill system.
# Idempotent — safe to re-run; never overwrites existing files without confirmation.
#
# What this does:
#   1. Check + install system dependencies (ripgrep, etc.)
#   2. Link skills/* into ~/.claude/skills/ (via link-skills.sh)
#   3. Install ~/.claude/CLAUDE.md from CLAUDE.template.md (if missing or with --force)
#   4. Install ~/.claude/RTK.md from RTK.template.md (if missing or with --force)
#   5. Create empty ~/.claude/memory/ + ~/.claude/projects/ if missing
#   6. Install lint tooling (PostToolUse hook + Python venv)
#   7. Install lifecycle hooks (SessionStart + PostCompact + UserPromptSubmit)
#   8. Install playwright-chromium MCP (user scope) — default browser MCP for all skills
#   9. (opt-in) Install playwright-firefox + playwright-webkit — cross-browser engine testing
#  10. (opt-in) Install chrome-devtools MCP — Lighthouse / perf trace / memory heap only
#  11. (opt-in) Install CodeGraph MCP — semantic ripple check for sa/fe/debug/migrate
#  12. (opt-in) Install Context7 MCP — live library docs for fe/debug/migrate/sa
#  13. Print next steps + missing-dependency warnings
#
# Flags:
#   --force            Overwrite existing CLAUDE.md / RTK.md without prompting (destructive — back up first)
#   --skip-link        Skip symlink step (if you already linked manually)
#   --skip-mcp              Skip playwright-chromium MCP install (if you don't want browser automation)
#   --skip-deps             Skip auto-install of system dependencies (rg, etc.)
#   --with-playwright       Register playwright-firefox + playwright-webkit (cross-browser, opt-in)
#   --with-chrome-devtools  Register chrome-devtools MCP (Lighthouse/perf/memory, opt-in)
#   --with-codegraph        Install CodeGraph binary + register MCP in ~/.claude.json (opt-in)
#   --with-context7         Register Context7 MCP in ~/.claude.json — live library docs (opt-in)
#   --with-weekly-distill   Install weekly memory distill cron (Mon 09:00) — opt-in, requires Telegram credentials at ~/.claude/.secrets/tg.env

REPO="$(cd "$(dirname "$0")/.." && pwd)"
HOME_CLAUDE="$HOME/.claude"

FORCE=0
SKIP_LINK=0
SKIP_MCP=0
SKIP_DEPS=0
WITH_PLAYWRIGHT=0
WITH_CHROME_DEVTOOLS=0
WITH_CODEGRAPH=0
WITH_CONTEXT7=0
WITH_WEEKLY_DISTILL=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --skip-link) SKIP_LINK=1 ;;
    --skip-mcp) SKIP_MCP=1 ;;
    --skip-deps) SKIP_DEPS=1 ;;
    --with-playwright) WITH_PLAYWRIGHT=1 ;;
    --with-chrome-devtools) WITH_CHROME_DEVTOOLS=1 ;;
    --with-codegraph) WITH_CODEGRAPH=1 ;;
    --with-context7) WITH_CONTEXT7=1 ;;
    --with-weekly-distill) WITH_WEEKLY_DISTILL=1 ;;
    -h|--help)
      sed -n '3,26p' "$0"
      exit 0
      ;;
    *)
      echo "error: unknown flag '$arg' (use --help)" >&2
      exit 2
      ;;
  esac
done

note() { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }
ok()   { printf '  \033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[1;33m!\033[0m %s\n' "$*"; }

# Track missing soft deps for final summary
MISSING_SOFT_DEPS=()

# ---------- 0. System dependencies ----------
#
# Auto-install heavy-use CLI tools that skills depend on.
# Hard required: rg (ripgrep) — used by audit/sa/fe/debug for code scans.
# Soft required: curl (almost always preinstalled), Chrome/Chromium (warn only).

detect_pkg_manager() {
  if [[ "$OSTYPE" == "darwin"* ]] && command -v brew &>/dev/null; then echo "brew"
  elif command -v apt-get &>/dev/null; then echo "apt"
  elif command -v dnf &>/dev/null; then echo "dnf"
  elif command -v yum &>/dev/null; then echo "yum"
  elif command -v pacman &>/dev/null; then echo "pacman"
  else echo ""
  fi
}

install_pkg() {
  local pkg="$1"
  local pm="$2"
  case "$pm" in
    brew)   brew install "$pkg" ;;
    apt)    sudo apt-get install -y "$pkg" ;;
    dnf)    sudo dnf install -y "$pkg" ;;
    yum)    sudo yum install -y "$pkg" ;;
    pacman) sudo pacman -S --noconfirm "$pkg" ;;
    *)      return 1 ;;
  esac
}

if [ "$SKIP_DEPS" -eq 1 ]; then
  note "Skipping system dependency install (--skip-deps)"
else
  note "Checking system dependencies"

  PM="$(detect_pkg_manager)"

  # ripgrep (rg) — hard required for skill pattern scans
  if command -v rg &>/dev/null; then
    ok "ripgrep (rg) found: $(rg --version | head -1)"
  elif [ -n "$PM" ]; then
    warn "ripgrep (rg) missing — installing via $PM"
    if install_pkg ripgrep "$PM"; then
      ok "ripgrep installed"
    else
      warn "ripgrep install failed — install manually: $PM install ripgrep"
      MISSING_SOFT_DEPS+=("ripgrep (used heavily by audit/sa/fe/debug skills)")
    fi
  else
    warn "ripgrep (rg) missing + no package manager detected"
    echo "      install manually: https://github.com/BurntSushi/ripgrep#installation"
    MISSING_SOFT_DEPS+=("ripgrep (used heavily by audit/sa/fe/debug skills)")
  fi

  # curl — soft required, almost always present
  if command -v curl &>/dev/null; then
    ok "curl found"
  else
    warn "curl missing — skills can't HTTP-check dev server"
    MISSING_SOFT_DEPS+=("curl (used to verify dev server HTTP 200)")
  fi

  # python3 — required for lint tooling (PostToolUse hook)
  if command -v python3 &>/dev/null; then
    ok "python3 found: $(python3 --version 2>&1)"
  elif [ -n "$PM" ]; then
    # Package name varies: brew=python@3.x or python3, debian=python3, fedora/rhel=python3, arch=python
    case "$PM" in
      brew)   PY_PKG="python3" ;;
      pacman) PY_PKG="python" ;;
      *)      PY_PKG="python3" ;;
    esac
    warn "python3 missing — installing via $PM"
    if install_pkg "$PY_PKG" "$PM"; then
      ok "python3 installed"
    else
      warn "python3 install failed — install manually: $PM install $PY_PKG"
      MISSING_SOFT_DEPS+=("python3 (required for lint tooling — skill/memory validator)")
    fi
  else
    warn "python3 missing + no package manager detected"
    echo "      install manually: https://www.python.org/downloads/"
    MISSING_SOFT_DEPS+=("python3 (required for lint tooling — skill/memory validator)")
  fi

  # jq — required for lint tooling (settings.json hook registration)
  if command -v jq &>/dev/null; then
    ok "jq found: $(jq --version 2>&1)"
  elif [ -n "$PM" ]; then
    warn "jq missing — installing via $PM"
    if install_pkg jq "$PM"; then
      ok "jq installed"
    else
      warn "jq install failed — install manually: $PM install jq"
      MISSING_SOFT_DEPS+=("jq (required for lint tooling — PostToolUse hook registration)")
    fi
  else
    warn "jq missing + no package manager detected"
    echo "      install manually: https://stedolan.github.io/jq/download/"
    MISSING_SOFT_DEPS+=("jq (required for lint tooling — PostToolUse hook registration)")
  fi

  # Node.js / npx — needed for playwright-chromium MCP + per-project work
  if command -v npx &>/dev/null; then
    ok "Node.js + npx found: $(node --version 2>/dev/null || echo "node version unknown")"
  else
    warn "Node.js / npx missing — playwright-chromium MCP install will fail"
    echo "      install Node 18+ from https://nodejs.org or via $PM"
    MISSING_SOFT_DEPS+=("Node.js + npx (required for playwright-chromium MCP and JS projects)")
  fi
fi

# ---------- 1. Link skills ----------

if [ "$SKIP_LINK" -eq 0 ]; then
  note "Linking skills into $HOME_CLAUDE/skills/"
  "$REPO/scripts/link-skills.sh"
else
  warn "Skipped skill linking (--skip-link)"
fi

# ---------- 2 & 3. Install global config files ----------

install_template() {
  local template="$1"
  local target="$2"
  local label="$3"

  if [ ! -f "$template" ]; then
    warn "$label template missing at $template — skipping"
    return
  fi

  if [ -f "$target" ]; then
    if [ "$FORCE" -eq 1 ]; then
      cp "$target" "$target.bak.$(date +%Y-%m-%d)"
      cp "$template" "$target"
      ok "$label overwritten (backup saved as $target.bak.$(date +%Y-%m-%d))"
    else
      # Compare; if identical, no-op
      if cmp -s "$template" "$target"; then
        ok "$label already up-to-date — no change"
      else
        warn "$label exists at $target and differs from template"
        echo "      run with --force to overwrite (will back up first)"
        echo "      or diff manually: diff \"$target\" \"$template\""
      fi
    fi
  else
    cp "$template" "$target"
    ok "$label installed at $target"
  fi
}

note "Installing CLAUDE.md (Universal Phase 0 + skill orchestration)"
install_template "$REPO/CLAUDE.template.md" "$HOME_CLAUDE/CLAUDE.md" "CLAUDE.md"

note "Installing RTK.md (optional — for RTK CLI users)"
install_template "$REPO/RTK.template.md" "$HOME_CLAUDE/RTK.md" "RTK.md"

# ---------- 4. Memory dirs ----------

note "Bootstrapping memory directories"

for d in "$HOME_CLAUDE/memory" "$HOME_CLAUDE/projects"; do
  if [ -d "$d" ]; then
    ok "Already exists: $d"
  else
    mkdir -p "$d"
    ok "Created: $d"
  fi
done

# ---------- 5. Lint tooling ----------
#
# Installs:
#   - Python venv at ~/.claude/scripts/.venv with PyYAML
#   - Symlinks scripts/lint-skills.py and hooks/lint-on-edit.sh into ~/.claude
#   - Registers PostToolUse hook in ~/.claude/settings.json (idempotent merge)
#
# Lint surfaces frontmatter drift, broken symlinks, missing required files,
# enum typos, MEMORY.md sync gaps, and orphan [[links]]. Warn-only — never
# blocks an edit. Skip cleanly if python3 or jq is missing.

note "Installing lint tooling (skill + memory frontmatter validator)"

LINT_VENV="$HOME_CLAUDE/scripts/.venv"
LINT_SCRIPT_SRC="$REPO/scripts/lint-skills.py"
LINT_SCRIPT_DST="$HOME_CLAUDE/scripts/lint-skills.py"
LINT_HOOK_SRC="$REPO/hooks/lint-on-edit.sh"
LINT_HOOK_DST="$HOME_CLAUDE/hooks/lint-on-edit.sh"
SETTINGS="$HOME_CLAUDE/settings.json"

if ! command -v python3 &>/dev/null; then
  warn "python3 not found — skipping lint install (skills will still work)"
elif ! command -v jq &>/dev/null; then
  warn "jq not found — skipping lint install (needed for hook registration)"
else
  mkdir -p "$HOME_CLAUDE/scripts" "$HOME_CLAUDE/hooks"

  # 5a. Venv + PyYAML
  if [ -x "$LINT_VENV/bin/python" ]; then
    ok "Venv already exists: $LINT_VENV"
  else
    python3 -m venv "$LINT_VENV"
    ok "Created venv: $LINT_VENV"
  fi

  if "$LINT_VENV/bin/python" -c "import yaml" 2>/dev/null; then
    ok "PyYAML already installed in venv"
  else
    "$LINT_VENV/bin/pip" install --quiet pyyaml
    ok "Installed PyYAML in venv"
  fi

  # 5b. Symlink lint script + hook
  if [ -L "$LINT_SCRIPT_DST" ] && [ "$(readlink "$LINT_SCRIPT_DST")" = "$LINT_SCRIPT_SRC" ]; then
    ok "lint-skills.py already linked"
  elif [ -e "$LINT_SCRIPT_DST" ] && [ ! -L "$LINT_SCRIPT_DST" ]; then
    warn "lint-skills.py exists at $LINT_SCRIPT_DST but is not a symlink — leaving alone (run with --force to overwrite)"
    if [ "$FORCE" -eq 1 ]; then
      cp "$LINT_SCRIPT_DST" "$LINT_SCRIPT_DST.bak.$(date +%Y-%m-%d)"
      ln -snf "$LINT_SCRIPT_SRC" "$LINT_SCRIPT_DST"
      ok "lint-skills.py replaced with symlink (backup saved)"
    fi
  else
    ln -snf "$LINT_SCRIPT_SRC" "$LINT_SCRIPT_DST"
    ok "Linked lint-skills.py -> $LINT_SCRIPT_SRC"
  fi

  if [ -L "$LINT_HOOK_DST" ] && [ "$(readlink "$LINT_HOOK_DST")" = "$LINT_HOOK_SRC" ]; then
    ok "lint-on-edit.sh already linked"
  elif [ -e "$LINT_HOOK_DST" ] && [ ! -L "$LINT_HOOK_DST" ]; then
    warn "lint-on-edit.sh exists at $LINT_HOOK_DST but is not a symlink — leaving alone (run with --force to overwrite)"
    if [ "$FORCE" -eq 1 ]; then
      cp "$LINT_HOOK_DST" "$LINT_HOOK_DST.bak.$(date +%Y-%m-%d)"
      ln -snf "$LINT_HOOK_SRC" "$LINT_HOOK_DST"
      ok "lint-on-edit.sh replaced with symlink (backup saved)"
    fi
  else
    ln -snf "$LINT_HOOK_SRC" "$LINT_HOOK_DST"
    ok "Linked lint-on-edit.sh -> $LINT_HOOK_SRC"
  fi

  # 5c. Register PostToolUse hook in settings.json (idempotent merge)
  if [ ! -f "$SETTINGS" ]; then
    echo '{"hooks":{}}' > "$SETTINGS"
    ok "Created $SETTINGS"
  fi

  if jq -e --arg cmd "$LINT_HOOK_DST" '.hooks.PostToolUse // [] | map(.hooks[]?.command) | flatten | any(. == $cmd)' "$SETTINGS" >/dev/null 2>&1; then
    ok "PostToolUse hook already registered"
  else
    cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y-%m-%d-%H%M%S)"
    tmp="$(mktemp)"
    jq --arg cmd "$LINT_HOOK_DST" '
      .hooks //= {} |
      .hooks.PostToolUse //= [] |
      .hooks.PostToolUse += [{
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [{"type": "command", "command": $cmd}]
      }]
    ' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
    ok "Registered PostToolUse hook in $SETTINGS (backup saved)"
  fi
fi

# ---------- 7. Lifecycle hooks (SessionStart + PostCompact + UserPromptSubmit) ----------
#
# Installs 3 hooks that work together to restore pipeline state after context compaction:
#   check-cross-project.py  → SessionStart (async)     — scan project memories for slugs in ≥2 projects
#   post-compact.py         → PostCompact              — show in-progress checkpoints as systemMessage
#   inject-checkpoint.py    → UserPromptSubmit         — inject checkpoints as additionalContext (once per compaction)
#
# All hooks exit silently (no output / no token cost) when there's nothing to report.
# Hooks are copied (not symlinked) so they work independently of the repo location.

note "Installing lifecycle hooks (cross-project memory + checkpoint restore)"

CROSS_PROJECT_HOOK_SRC="$REPO/hooks/check-cross-project.py"
CROSS_PROJECT_HOOK_DST="$HOME_CLAUDE/hooks/check-cross-project.py"
POST_COMPACT_HOOK_SRC="$REPO/hooks/post-compact.py"
POST_COMPACT_HOOK_DST="$HOME_CLAUDE/hooks/post-compact.py"
INJECT_HOOK_SRC="$REPO/hooks/inject-checkpoint.py"
INJECT_HOOK_DST="$HOME_CLAUDE/hooks/inject-checkpoint.py"
CHECKPOINT_LIB_SRC="$REPO/hooks/_checkpoint_lib.py"
CHECKPOINT_LIB_DST="$HOME_CLAUDE/hooks/_checkpoint_lib.py"
MEM_SIZE_HOOK_SRC="$REPO/hooks/check-memory-size.py"
MEM_SIZE_HOOK_DST="$HOME_CLAUDE/hooks/check-memory-size.py"

if ! command -v python3 &>/dev/null; then
  warn "python3 not found — skipping lifecycle hooks (skills still work without them)"
elif ! command -v jq &>/dev/null; then
  warn "jq not found — skipping lifecycle hook registration (needed for settings.json merge)"
else
  mkdir -p "$HOME_CLAUDE/hooks"

  if [ ! -f "$SETTINGS" ]; then
    echo '{"hooks":{}}' > "$SETTINGS"
    ok "Created $SETTINGS"
  fi

  # Copy hook scripts (not symlinked — standalone Python, not skill assets)
  # _checkpoint_lib.py is a shared module imported by post-compact + inject-checkpoint —
  # must be copied alongside them or both hooks fail.
  for PAIR in \
    "$CROSS_PROJECT_HOOK_SRC:$CROSS_PROJECT_HOOK_DST" \
    "$CHECKPOINT_LIB_SRC:$CHECKPOINT_LIB_DST" \
    "$POST_COMPACT_HOOK_SRC:$POST_COMPACT_HOOK_DST" \
    "$INJECT_HOOK_SRC:$INJECT_HOOK_DST" \
    "$MEM_SIZE_HOOK_SRC:$MEM_SIZE_HOOK_DST"; do
    SRC="${PAIR%%:*}"
    DST="${PAIR##*:}"
    FNAME="$(basename "$DST")"
    if [ ! -f "$SRC" ]; then
      warn "$FNAME missing in repo hooks/ — skipping"
      continue
    fi
    if [ -f "$DST" ] && cmp -s "$SRC" "$DST"; then
      ok "$FNAME already up-to-date"
    else
      cp "$SRC" "$DST"
      chmod +x "$DST"
      ok "Installed $FNAME"
    fi
  done

  # Register SessionStart hook — check-cross-project.py (async, zero latency)
  CROSS_CMD="python3 $CROSS_PROJECT_HOOK_DST"
  if jq -e --arg cmd "$CROSS_CMD" \
    '.hooks.SessionStart // [] | map(.hooks[]?.command) | flatten | any(. == $cmd)' \
    "$SETTINGS" >/dev/null 2>&1; then
    ok "SessionStart hook (check-cross-project.py) already registered"
  else
    cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y-%m-%d-%H%M%S)"
    tmp="$(mktemp)"
    jq --arg cmd "$CROSS_CMD" '
      .hooks //= {} |
      .hooks.SessionStart //= [] |
      .hooks.SessionStart += [{"hooks": [{"type": "command", "command": $cmd, "async": true}]}]
    ' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
    ok "Registered SessionStart hook (check-cross-project.py async)"
  fi

  # Register SessionStart hook — check-memory-size.py (async, warns when memory > 30 entries)
  MEM_SIZE_CMD="python3 $MEM_SIZE_HOOK_DST"
  if jq -e --arg cmd "$MEM_SIZE_CMD" \
    '.hooks.SessionStart // [] | map(.hooks[]?.command) | flatten | any(. == $cmd)' \
    "$SETTINGS" >/dev/null 2>&1; then
    ok "SessionStart hook (check-memory-size.py) already registered"
  else
    cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y-%m-%d-%H%M%S)"
    tmp="$(mktemp)"
    jq --arg cmd "$MEM_SIZE_CMD" '
      .hooks //= {} |
      .hooks.SessionStart //= [] |
      .hooks.SessionStart += [{"hooks": [{"type": "command", "command": $cmd, "async": true}]}]
    ' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
    ok "Registered SessionStart hook (check-memory-size.py async)"
  fi

  # Register PostCompact hook — post-compact.py (shows systemMessage + writes sentinel)
  COMPACT_CMD="python3 $POST_COMPACT_HOOK_DST"
  if jq -e --arg cmd "$COMPACT_CMD" \
    '.hooks.PostCompact // [] | map(.hooks[]?.command) | flatten | any(. == $cmd)' \
    "$SETTINGS" >/dev/null 2>&1; then
    ok "PostCompact hook (post-compact.py) already registered"
  else
    cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y-%m-%d-%H%M%S)"
    tmp="$(mktemp)"
    jq --arg cmd "$COMPACT_CMD" '
      .hooks //= {} |
      .hooks.PostCompact //= [] |
      .hooks.PostCompact += [{"hooks": [{"type": "command", "command": $cmd}]}]
    ' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
    ok "Registered PostCompact hook (post-compact.py)"
  fi

  # Register UserPromptSubmit hook — inject-checkpoint.py (fires once per compaction via sentinel)
  INJECT_CMD="python3 $INJECT_HOOK_DST"
  if jq -e --arg cmd "$INJECT_CMD" \
    '.hooks.UserPromptSubmit // [] | map(.hooks[]?.command) | flatten | any(. == $cmd)' \
    "$SETTINGS" >/dev/null 2>&1; then
    ok "UserPromptSubmit hook (inject-checkpoint.py) already registered"
  else
    cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y-%m-%d-%H%M%S)"
    tmp="$(mktemp)"
    jq --arg cmd "$INJECT_CMD" '
      .hooks //= {} |
      .hooks.UserPromptSubmit //= [] |
      .hooks.UserPromptSubmit += [{"hooks": [{"type": "command", "command": $cmd}]}]
    ' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
    ok "Registered UserPromptSubmit hook (inject-checkpoint.py)"
  fi
fi

# ---------- 6. playwright-chromium MCP (default browser) ----------
#
# Default browser MCP — powers navigate/click/screenshot/console/network/evaluate
# across all skills (verify/debug/run/ux/fe/security-review).
# chrome-devtools is reserved for Lighthouse / perf trace / memory heap only.
#
# Also installs the browser binary (chrome-for-testing) via playwright's installer.
# Installs at user scope so it's available across all projects.
# Idempotent — skip if already registered.

if [ "$SKIP_MCP" -eq 1 ]; then
  note "Skipping playwright-chromium MCP install (--skip-mcp)"
else
  note "Installing playwright-chromium MCP (default browser for all skills)"

  CLAUDE_JSON="$HOME/.claude.json"

  if ! command -v npx &>/dev/null; then
    warn "npx not found (need Node.js) — install Node then run:"
    echo '      Add to ~/.claude.json mcpServers: "playwright-chromium": {"type":"stdio","command":"npx","args":["@playwright/mcp@latest","--browser","chromium"]}'
  elif [ ! -f "$CLAUDE_JSON" ]; then
    warn "~/.claude.json not found — add manually under mcpServers:"
    echo '      "playwright-chromium": {"type":"stdio","command":"npx","args":["@playwright/mcp@latest","--browser","chromium"]}'
  elif ! command -v jq &>/dev/null; then
    warn "jq not found — add manually to ~/.claude.json under mcpServers:"
    echo '      "playwright-chromium": {"type":"stdio","command":"npx","args":["@playwright/mcp@latest","--browser","chromium"]}'
  elif jq -e '.mcpServers["playwright-chromium"]' "$CLAUDE_JSON" >/dev/null 2>&1; then
    ok "playwright-chromium MCP already registered"
  else
    cp "$CLAUDE_JSON" "$CLAUDE_JSON.bak.$(date +%Y-%m-%d-%H%M%S)"
    tmp="$(mktemp)"
    jq '.mcpServers //= {} | .mcpServers["playwright-chromium"] = {"type":"stdio","command":"npx","args":["@playwright/mcp@latest","--browser","chromium"]}' \
      "$CLAUDE_JSON" > "$tmp" && mv "$tmp" "$CLAUDE_JSON"
    ok "playwright-chromium registered in ~/.claude.json"
  fi

  # Install browser binary (idempotent — playwright skips if already present)
  if command -v npx &>/dev/null; then
    note "Installing chrome-for-testing browser binary (playwright-chromium needs it)"
    if npx @playwright/mcp install-browser chrome-for-testing 2>&1 | tail -3; then
      ok "chrome-for-testing browser binary ready"
    else
      warn "Browser binary install failed — run manually:"
      echo "      npx @playwright/mcp install-browser chrome-for-testing"
    fi
  fi
fi

# ---------- 7. CodeGraph MCP (opt-in) ----------
#
# Adds semantic codebase intelligence to ripple checks across all skills:
#   sa/fe  — callers list + impact analysis (replaces rg for named symbols)
#   debug  — call path trace from crash site
#   migrate — discover scope by callers graph before regex scan
#
# Opt-in (--with-codegraph) because CodeGraph requires per-project init
# (codegraph init -i) and is not useful until that step is done.
# After global install, run `codegraph init -i` once per project.

if [ "$WITH_CODEGRAPH" -eq 0 ]; then
  note "CodeGraph MCP skipped (add --with-codegraph to install)"
else
  note "Installing CodeGraph MCP (semantic ripple check for sa/fe/debug/migrate)"

  CODEGRAPH_BIN="$HOME/.local/bin/codegraph"

  # 7a. Install binary if missing
  if command -v codegraph &>/dev/null || [ -x "$CODEGRAPH_BIN" ]; then
    ok "codegraph already installed: $(codegraph --version 2>/dev/null || "$CODEGRAPH_BIN" --version 2>/dev/null || echo "version unknown")"
  elif command -v curl &>/dev/null; then
    warn "codegraph not found — downloading installer"
    if curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh; then
      ok "codegraph installed: $("$CODEGRAPH_BIN" --version 2>/dev/null || echo "version unknown")"
    else
      warn "codegraph install failed — install manually:"
      echo "      curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh"
      MISSING_SOFT_DEPS+=("codegraph binary (see https://github.com/colbymchenry/codegraph)")
    fi
  else
    warn "curl not found — install codegraph manually:"
    echo "      curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh"
    MISSING_SOFT_DEPS+=("codegraph binary (requires curl)")
  fi

  # 7b. Detect actual binary path (post-install)
  CODEGRAPH_CMD="$(command -v codegraph 2>/dev/null || echo "$CODEGRAPH_BIN")"

  # 7c. Register MCP config in ~/.claude.json (idempotent)
  CLAUDE_JSON="$HOME/.claude.json"
  if [ ! -f "$CLAUDE_JSON" ]; then
    warn "~/.claude.json not found — add manually under mcpServers:"
    printf '      "codegraph": {"type":"stdio","command":"%s","args":["serve","--mcp"]}\n' "$CODEGRAPH_CMD"
  elif ! command -v jq &>/dev/null; then
    warn "jq not found — add manually to ~/.claude.json under mcpServers:"
    printf '      "codegraph": {"type":"stdio","command":"%s","args":["serve","--mcp"]}\n' "$CODEGRAPH_CMD"
  elif jq -e '.mcpServers.codegraph' "$CLAUDE_JSON" >/dev/null 2>&1; then
    ok "codegraph MCP already registered in ~/.claude.json"
  else
    cp "$CLAUDE_JSON" "$CLAUDE_JSON.bak.$(date +%Y-%m-%d-%H%M%S)"
    tmp="$(mktemp)"
    jq --arg cmd "$CODEGRAPH_CMD" '
      .mcpServers //= {} |
      .mcpServers.codegraph = {"type":"stdio","command":$cmd,"args":["serve","--mcp"]}
    ' "$CLAUDE_JSON" > "$tmp" && mv "$tmp" "$CLAUDE_JSON"
    ok "codegraph MCP registered in ~/.claude.json (backup saved)"
    echo "      Restart Claude Code to pick up the new MCP server"
  fi

  # 7d. Register SessionStart hook — auto-init codegraph on first session in any project
  #     Detects JS/TS, Python, Go, Rust, Ruby, Java via common signal files.
  #     Skips silently if no project signal file present or db already exists — zero overhead.
  AUTOINIT_CMD="[ ! -f .codegraph/codegraph.db ] && { [ -f package.json ] || [ -f pyproject.toml ] || [ -f go.mod ] || [ -f Cargo.toml ] || [ -f Gemfile ] || [ -f pom.xml ] || [ -f setup.py ]; } && codegraph init -i . 2>&1 | tail -2 || true"
  if command -v jq &>/dev/null && [ -f "$SETTINGS" ]; then
    if jq -e --arg cmd "$AUTOINIT_CMD" \
      '.hooks.SessionStart // [] | map(.hooks[]?.command) | flatten | any(. == $cmd)' \
      "$SETTINGS" >/dev/null 2>&1; then
      ok "SessionStart auto-init hook already registered"
    else
      cp "$SETTINGS" "$SETTINGS.bak.$(date +%Y-%m-%d-%H%M%S)"
      tmp="$(mktemp)"
      jq --arg cmd "$AUTOINIT_CMD" '
        .hooks //= {} |
        .hooks.SessionStart //= [] |
        .hooks.SessionStart += [{"hooks": [{"type": "command", "command": $cmd}]}]
      ' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
      ok "Registered SessionStart auto-init hook (codegraph init on new projects)"
    fi
  fi

  echo ""
  echo "      Next: run once per project to build the index:"
  echo "        cd /your/project && codegraph init -i"
  echo "      (or open any project with a recognized signal file — SessionStart hook auto-inits"
  echo "       for: package.json, pyproject.toml, go.mod, Cargo.toml, Gemfile, pom.xml, setup.py)"
fi

# ---------- 8. Context7 MCP (opt-in) ----------
#
# Adds live library documentation to fe/debug/migrate/sa:
#   fe      — verify Nuxt UI / Valibot / Pinia API before implementing
#   debug   — check known breaking changes when error involves library
#   migrate — query migration guide before bulk transform
#   sa      — verify external library API spec (opt-in)
#
# Opt-in (--with-context7) because it requires npx per invocation.
# No binary install needed — Context7 runs via npx directly.

if [ "$WITH_CONTEXT7" -eq 0 ]; then
  note "Context7 MCP skipped (add --with-context7 to install)"
else
  note "Installing Context7 MCP (live library docs for fe/debug/migrate/sa)"

  CLAUDE_JSON="$HOME/.claude.json"
  if [ ! -f "$CLAUDE_JSON" ]; then
    warn "~/.claude.json not found — add manually under mcpServers:"
    echo '      "context7": {"type":"stdio","command":"npx","args":["-y","@upstash/context7-mcp@latest"]}'
  elif ! command -v jq &>/dev/null; then
    warn "jq not found — add manually to ~/.claude.json under mcpServers:"
    echo '      "context7": {"type":"stdio","command":"npx","args":["-y","@upstash/context7-mcp@latest"]}'
  elif jq -e '.mcpServers.context7' "$CLAUDE_JSON" >/dev/null 2>&1; then
    ok "context7 MCP already registered in ~/.claude.json"
  else
    cp "$CLAUDE_JSON" "$CLAUDE_JSON.bak.$(date +%Y-%m-%d-%H%M%S)"
    tmp="$(mktemp)"
    jq '
      .mcpServers //= {} |
      .mcpServers.context7 = {"type":"stdio","command":"npx","args":["-y","@upstash/context7-mcp@latest"]}
    ' "$CLAUDE_JSON" > "$tmp" && mv "$tmp" "$CLAUDE_JSON"
    ok "context7 MCP registered in ~/.claude.json (backup saved)"
    echo "      Restart Claude Code to pick up the new MCP server"
    echo "      First call will download @upstash/context7-mcp via npx (one-time, ~5MB)"
  fi
fi

# ---------- 9. playwright-firefox + playwright-webkit (opt-in, cross-browser) ----------
#
# Adds real cross-browser engine testing beyond the default playwright-chromium:
#   debug  — reproduce bugs in Firefox/WebKit; browser_select_option for form bugs
#   ux     — cross-browser visual screenshot comparison
#   audit  — cross-browser a11y: ARIA + keyboard nav differences per engine
#   fe     — cross-browser hydration/reactivity verify when issue is engine-specific
#
# playwright-chromium is already installed by step 6 — this step adds firefox + webkit only.
# Requires: Node.js + npx (already checked in step 0)

if [ "$WITH_PLAYWRIGHT" -eq 0 ]; then
  note "Playwright cross-browser MCP skipped (add --with-playwright to install firefox + webkit)"
else
  note "Installing playwright-firefox + playwright-webkit (cross-browser engines)"

  CLAUDE_JSON="$HOME/.claude.json"

  if [ ! -f "$CLAUDE_JSON" ]; then
    warn "~/.claude.json not found — add manually under mcpServers:"
    echo '      "playwright-firefox":  {"type":"stdio","command":"npx","args":["@playwright/mcp@latest","--browser","firefox"]}'
    echo '      "playwright-webkit":   {"type":"stdio","command":"npx","args":["@playwright/mcp@latest","--browser","webkit"]}'
  elif ! command -v jq &>/dev/null; then
    warn "jq not found — add manually to ~/.claude.json under mcpServers"
  elif ! command -v npx &>/dev/null; then
    warn "npx not found (need Node.js) — install Node then re-run with --with-playwright"
  else
    cp "$CLAUDE_JSON" "$CLAUDE_JSON.bak.$(date +%Y-%m-%d-%H%M%S)"
    tmp="$(mktemp)"

    for BROWSER in firefox webkit; do
      KEY="playwright-$BROWSER"
      if jq -e ".mcpServers[\"$KEY\"]" "$CLAUDE_JSON" >/dev/null 2>&1; then
        ok "$KEY MCP already registered in ~/.claude.json"
      else
        jq --arg key "$KEY" --arg browser "$BROWSER" '
          .mcpServers //= {} |
          .mcpServers[$key] = {
            "type": "stdio",
            "command": "npx",
            "args": ["@playwright/mcp@latest", "--browser", $browser]
          }
        ' "$CLAUDE_JSON" > "$tmp" && mv "$tmp" "$CLAUDE_JSON"
        ok "$KEY registered in ~/.claude.json"
      fi
    done

    echo "      Restart Claude Code to pick up the new Playwright MCP servers"
    echo "      Each engine is independent — use playwright-firefox / playwright-webkit for cross-browser bugs"
    echo "      Playwright will download required browser binaries on first run via npx"
  fi
fi

# ---------- 10. chrome-devtools MCP (opt-in — Lighthouse / perf trace / memory heap) ----------
#
# Reserve for: Lighthouse score, performance traces (Web Vitals), memory heap snapshots.
# All other browser tasks use playwright-chromium (already installed in step 6).
# Requires: Chrome/Chromium installed on this machine (not bundled like playwright).

if [ "$WITH_CHROME_DEVTOOLS" -eq 0 ]; then
  note "chrome-devtools MCP skipped (add --with-chrome-devtools to install — needed only for Lighthouse/perf/memory)"
else
  note "Installing chrome-devtools MCP (Lighthouse / perf trace / memory heap)"

  if ! command -v claude &>/dev/null; then
    warn "claude CLI not found — install manually later:"
    echo "      claude mcp add --scope user chrome-devtools -- npx -y chrome-devtools-mcp@latest"
  elif ! command -v npx &>/dev/null; then
    warn "npx not found (need Node.js) — install Node then run:"
    echo "      claude mcp add --scope user chrome-devtools -- npx -y chrome-devtools-mcp@latest"
  elif claude mcp list 2>/dev/null | grep -qi "chrome-devtools"; then
    ok "chrome-devtools MCP already registered"
  else
    if claude mcp add --scope user chrome-devtools -- npx -y chrome-devtools-mcp@latest 2>&1 | tail -5; then
      ok "chrome-devtools MCP installed at user scope"
      echo "      Requires Chrome/Chromium installed on this machine"
      echo "      Use only for: lighthouse_audit, performance_start_trace, take_memory_snapshot"
    else
      warn "chrome-devtools MCP install failed — try manually:"
      echo "      claude mcp add --scope user chrome-devtools -- npx -y chrome-devtools-mcp@latest"
    fi
  fi
fi

# ---------- 11. Weekly memory distill cron (opt-in) ----------
#
# Installs a macOS cron entry that runs Mon 09:00 local time:
#   scripts/distill-dry-run.py → markdown digest
#   scripts/distill-dry-run-notify.sh → sends digest to Telegram + archives to ~/.claude/memory/.last-distill-report.md
#
# Requires Telegram credentials at ~/.claude/.secrets/tg.env (chmod 600). If they're
# absent the report is still archived locally; the cron job exits 0 either way.
# Skip without --with-weekly-distill — most users won't want a weekly TG ping.

if [ "$WITH_WEEKLY_DISTILL" -eq 1 ]; then
  note "Installing weekly memory distill cron (Mon 09:00)"

  DISTILL_SCANNER_SRC="$REPO/scripts/distill-dry-run.py"
  DISTILL_SCANNER_DST="$HOME_CLAUDE/scripts/distill-dry-run.py"
  DISTILL_NOTIFY_SRC="$REPO/scripts/distill-dry-run-notify.sh"
  DISTILL_NOTIFY_DST="$HOME_CLAUDE/scripts/distill-dry-run-notify.sh"

  mkdir -p "$HOME_CLAUDE/scripts"
  for PAIR in \
    "$DISTILL_SCANNER_SRC:$DISTILL_SCANNER_DST" \
    "$DISTILL_NOTIFY_SRC:$DISTILL_NOTIFY_DST"; do
    SRC="${PAIR%%:*}"
    DST="${PAIR##*:}"
    if [ ! -f "$SRC" ]; then
      warn "$(basename "$DST") missing in repo — skipping cron install"
      WITH_WEEKLY_DISTILL=0
      break
    fi
    if [ -f "$DST" ] && cmp -s "$SRC" "$DST"; then
      ok "$(basename "$DST") already up-to-date"
    else
      cp "$SRC" "$DST"
      chmod +x "$DST"
      ok "Installed $(basename "$DST")"
    fi
  done

  if [ "$WITH_WEEKLY_DISTILL" -eq 1 ]; then
    CRON_LINE="0 9 * * 1 $DISTILL_NOTIFY_DST >> $HOME_CLAUDE/memory/.distill-cron.log 2>&1"
    if crontab -l 2>/dev/null | grep -qF "$DISTILL_NOTIFY_DST"; then
      ok "Weekly cron already registered"
    else
      EXISTING="$(crontab -l 2>/dev/null || true)"
      {
        if [ -n "$EXISTING" ]; then printf '%s\n' "$EXISTING"; fi
        echo "# Weekly memory distill dry-run → Telegram digest (added by setup.sh)"
        echo "PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
        echo "$CRON_LINE"
      } | crontab -
      ok "Registered cron: $CRON_LINE"
      warn "First run is next Monday 09:00. Run manually now: $DISTILL_NOTIFY_DST"
    fi

    if [ ! -f "$HOME_CLAUDE/.secrets/tg.env" ]; then
      warn "TG credentials not found at ~/.claude/.secrets/tg.env"
      warn "Cron will run + archive locally, but no Telegram message will be sent."
      warn "To enable: cp $REPO/.secrets-template/tg.env.example ~/.claude/.secrets/tg.env && chmod 600 ~/.claude/.secrets/tg.env && \$EDITOR ~/.claude/.secrets/tg.env"
    fi
  fi
else
  note "Weekly distill cron skipped (add --with-weekly-distill to enable)"
fi

# ---------- Summary ----------

note "Done"
cat <<EOF

Next steps:
  1. Test a skill — open Claude Code in any project and ask:
       "ใช้ skill debug ตรวจอะไรก่อนเริ่ม?"
     Expect mantra recital + Phase 0 reference.

  2. (Optional) Install RTK CLI if you want token savings on shell commands.
     Skip if you don't have it — skills still work, just no rtk filtering.

  3. (Optional) Install CodeGraph MCP for semantic ripple checks:
       ./scripts/setup.sh --with-codegraph
     Then init once per project: cd /your/project && codegraph init -i

  4. (Optional) Install Context7 MCP for live library documentation:
       ./scripts/setup.sh --with-context7
     Queries real docs for Nuxt UI / Valibot / Pinia instead of using training data.

  5. (Optional) Install playwright-firefox + webkit for cross-browser testing:
       ./scripts/setup.sh --with-playwright
     Registers playwright-firefox, playwright-webkit in ~/.claude.json
     Enables: cross-browser reproduce in debug, visual diff in ux, a11y verify in audit.
     (playwright-chromium is already installed by default in step 6)

  6. (Optional) Install chrome-devtools MCP for Lighthouse / perf trace / memory heap:
       ./scripts/setup.sh --with-chrome-devtools
     Use only when you need: lighthouse score, Web Vitals trace, memory heap snapshot.

  6. Memory starts empty — that's expected. Lessons accumulate as you work.
     Read CLAUDE.md sections "Save triggers" + "Graduation pipeline" for how it grows.

  7. Customize for your project: add a CLAUDE.md inside your project root with
     stack info, conventions, and project-specific rules.

Files touched:
  $HOME_CLAUDE/skills/                       (symlinks → $REPO/skills/**)
  $HOME_CLAUDE/CLAUDE.md                     (Universal Phase 0)
  $HOME_CLAUDE/RTK.md                        (optional — RTK CLI ref)
  $HOME_CLAUDE/memory/                       (empty — your global lessons go here)
  $HOME_CLAUDE/projects/                     (empty — per-project memory goes here)
  $HOME_CLAUDE/scripts/.venv                 (Python venv for lint tooling)
  $HOME_CLAUDE/scripts/lint-skills.py        (symlink → $REPO/scripts/lint-skills.py)
  $HOME_CLAUDE/hooks/lint-on-edit.sh         (symlink → $REPO/hooks/lint-on-edit.sh)
  $HOME_CLAUDE/hooks/check-cross-project.py  (copy — SessionStart async hook)
  $HOME_CLAUDE/hooks/post-compact.py         (copy — PostCompact hook)
  $HOME_CLAUDE/hooks/inject-checkpoint.py    (copy — UserPromptSubmit hook)
  $HOME_CLAUDE/settings.json                 (PostToolUse + SessionStart + PostCompact + UserPromptSubmit hooks registered)
  Claude MCP servers                         (chrome-devtools registered at user scope)

Verify chrome-devtools MCP:
  claude mcp list                       # should show "chrome-devtools"
  (requires Chrome/Chromium on this machine to actually run)

EOF

if [ ${#MISSING_SOFT_DEPS[@]} -gt 0 ]; then
  printf '\n\033[1;33m== Missing soft dependencies (skills will degrade gracefully) ==\033[0m\n'
  for dep in "${MISSING_SOFT_DEPS[@]}"; do
    printf '  \033[1;33m!\033[0m %s\n' "$dep"
  done
  echo
fi

cat <<EOF


Lint manually:
  ~/.claude/scripts/lint-skills.py              # full sweep
  ~/.claude/scripts/lint-skills.py PATH         # one file or dir

EOF
