#!/usr/bin/env bash
set -euo pipefail

# Symlink every shippable skill in this repo into ~/.claude/skills/ so
# Claude Code can find them. Skills under personal/, in-progress/, or
# deprecated/ are skipped.
#
# Usage:
#   ./scripts/link-skills.sh

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.claude/skills"

# Safety: if DEST is a symlink that resolves back into the repo, bail out.
if [ -L "$DEST" ]; then
  resolved="$(readlink -f "$DEST" 2>/dev/null || readlink "$DEST")"
  case "$resolved" in
    "$REPO"|"$REPO"/*)
      echo "error: $DEST is a symlink into this repo ($resolved)." >&2
      echo "Remove it (rm \"$DEST\") and re-run; the script will recreate it as a real dir." >&2
      exit 1
      ;;
  esac
fi

mkdir -p "$DEST"

linked=0
skipped=0

while IFS= read -r skill_md; do
  skill_dir="$(dirname "$skill_md")"
  skill_name="$(basename "$skill_dir")"
  target="$DEST/$skill_name"

  # If target already exists and isn't a symlink we own, skip and warn.
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "skip: $target exists and is not a symlink (won't overwrite)" >&2
    skipped=$((skipped + 1))
    continue
  fi

  ln -snf "$skill_dir" "$target"
  echo "linked: $skill_name -> $skill_dir"
  linked=$((linked + 1))
done < <(
  find "$REPO/skills" -name SKILL.md \
    -not -path '*/node_modules/*' \
    -not -path '*/deprecated/*' \
    -not -path '*/in-progress/*' \
    -not -path '*/personal/*'
)

echo ""
echo "done: $linked linked, $skipped skipped"
