#!/usr/bin/env bash
set -euo pipefail

# Bootstrap a fresh machine to behave like the upstream skill system.
# Idempotent — safe to re-run; never overwrites existing files without confirmation.
#
# What this does:
#   1. Link skills/* into ~/.claude/skills/ (via link-skills.sh)
#   2. Install ~/.claude/CLAUDE.md from CLAUDE.template.md (if missing or with --force)
#   3. Install ~/.claude/RTK.md from RTK.template.md (if missing or with --force)
#   4. Create empty ~/.claude/memory/ + ~/.claude/projects/ if missing
#   5. Print next steps
#
# Flags:
#   --force   Overwrite existing CLAUDE.md / RTK.md without prompting (destructive — back up first)
#   --skip-link  Skip symlink step (if you already linked manually)

REPO="$(cd "$(dirname "$0")/.." && pwd)"
HOME_CLAUDE="$HOME/.claude"

FORCE=0
SKIP_LINK=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --skip-link) SKIP_LINK=1 ;;
    -h|--help)
      sed -n '3,18p' "$0"
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

# ---------- Summary ----------

note "Done"
cat <<EOF

Next steps:
  1. Test a skill — open Claude Code in any project and ask:
       "ใช้ skill debug ตรวจอะไรก่อนเริ่ม?"
     Expect mantra recital + Phase 0 reference.

  2. (Optional) Install RTK CLI if you want token savings on shell commands.
     Skip if you don't have it — skills still work, just no rtk filtering.

  3. Memory starts empty — that's expected. Lessons accumulate as you work.
     Read CLAUDE.md sections "Save triggers" + "Graduation pipeline" for how it grows.

  4. Customize for your project: add a CLAUDE.md inside your project root with
     stack info, conventions, and project-specific rules.

Files touched:
  $HOME_CLAUDE/skills/        (symlinks → $REPO/skills/**)
  $HOME_CLAUDE/CLAUDE.md      (Universal Phase 0)
  $HOME_CLAUDE/RTK.md         (optional — RTK CLI ref)
  $HOME_CLAUDE/memory/        (empty — your global lessons go here)
  $HOME_CLAUDE/projects/      (empty — per-project memory goes here)

EOF
