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
#   7. Install chrome-devtools MCP (user scope) — powers debug/ux/audit/fe browser playbooks
#   8. (opt-in) Install CodeGraph MCP — semantic ripple check for sa/fe/debug/migrate
#   9. Print next steps + missing-dependency warnings
#
# Flags:
#   --force           Overwrite existing CLAUDE.md / RTK.md without prompting (destructive — back up first)
#   --skip-link       Skip symlink step (if you already linked manually)
#   --skip-mcp        Skip chrome-devtools MCP install (if you don't want browser automation)
#   --skip-deps       Skip auto-install of system dependencies (rg, etc.)
#   --with-codegraph  Install CodeGraph binary + register MCP in ~/.claude.json (opt-in)

REPO="$(cd "$(dirname "$0")/.." && pwd)"
HOME_CLAUDE="$HOME/.claude"

FORCE=0
SKIP_LINK=0
SKIP_MCP=0
SKIP_DEPS=0
WITH_CODEGRAPH=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --skip-link) SKIP_LINK=1 ;;
    --skip-mcp) SKIP_MCP=1 ;;
    --skip-deps) SKIP_DEPS=1 ;;
    --with-codegraph) WITH_CODEGRAPH=1 ;;
    -h|--help)
      sed -n '3,23p' "$0"
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

  # Node.js / npx — needed for chrome-devtools MCP + per-project work
  if command -v npx &>/dev/null; then
    ok "Node.js + npx found: $(node --version 2>/dev/null || echo "node version unknown")"
  else
    warn "Node.js / npx missing — chrome-devtools MCP install will fail"
    echo "      install Node 18+ from https://nodejs.org or via $PM"
    MISSING_SOFT_DEPS+=("Node.js + npx (required for chrome-devtools MCP and JS projects)")
  fi

  # Chrome / Chromium — warn only (platform-specific, heavyweight)
  CHROME_FOUND=0
  CHROME_CANDIDATES=(
    "google-chrome"
    "chromium"
    "chromium-browser"
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Chromium.app/Contents/MacOS/Chromium"
  )
  for chrome_bin in "${CHROME_CANDIDATES[@]}"; do
    if command -v "$chrome_bin" &>/dev/null || [ -x "$chrome_bin" ]; then
      CHROME_FOUND=1
      break
    fi
  done
  if [ "$CHROME_FOUND" -eq 1 ]; then
    ok "Chrome/Chromium binary detected"
  else
    warn "Chrome/Chromium not detected — chrome-devtools MCP needs it to run"
    echo "      macOS: download from https://www.google.com/chrome/"
    echo "      Linux: $PM install chromium (or google-chrome-stable)"
    MISSING_SOFT_DEPS+=("Chrome/Chromium browser (required for chrome-devtools MCP playbooks)")
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

# ---------- 6. chrome-devtools MCP ----------
#
# Powers the browser-automation playbooks in debug/ux/audit/fe skills.
# Without this, those skills fall back to "ask user for screenshot" path —
# functional but ~35-55% less effective per quality lift estimates.
#
# Installs at user scope so it's available across all projects.
# Idempotent — skip if already registered.

if [ "$SKIP_MCP" -eq 1 ]; then
  note "Skipping chrome-devtools MCP install (--skip-mcp)"
else
  note "Installing chrome-devtools MCP (browser automation for debug/ux/audit/fe)"

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
      echo "      First call will download chrome-devtools-mcp via npx (one-time, ~10MB)"
      echo "      Requires Chrome/Chromium installed on this machine"
    else
      warn "chrome-devtools MCP install failed — try manually:"
      echo "      claude mcp add --scope user chrome-devtools -- npx -y chrome-devtools-mcp@latest"
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

  echo ""
  echo "      Next: run once per project to build the index:"
  echo "        cd /your/project && codegraph init -i"
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

  4. Memory starts empty — that's expected. Lessons accumulate as you work.
     Read CLAUDE.md sections "Save triggers" + "Graduation pipeline" for how it grows.

  5. Customize for your project: add a CLAUDE.md inside your project root with
     stack info, conventions, and project-specific rules.

Files touched:
  $HOME_CLAUDE/skills/                  (symlinks → $REPO/skills/**)
  $HOME_CLAUDE/CLAUDE.md                (Universal Phase 0)
  $HOME_CLAUDE/RTK.md                   (optional — RTK CLI ref)
  $HOME_CLAUDE/memory/                  (empty — your global lessons go here)
  $HOME_CLAUDE/projects/                (empty — per-project memory goes here)
  $HOME_CLAUDE/scripts/.venv            (Python venv for lint tooling)
  $HOME_CLAUDE/scripts/lint-skills.py   (symlink → $REPO/scripts/lint-skills.py)
  $HOME_CLAUDE/hooks/lint-on-edit.sh    (symlink → $REPO/hooks/lint-on-edit.sh)
  $HOME_CLAUDE/settings.json            (PostToolUse hook registered)
  Claude MCP servers                    (chrome-devtools registered at user scope)

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
