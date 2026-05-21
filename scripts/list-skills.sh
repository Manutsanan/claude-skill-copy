#!/usr/bin/env bash
set -euo pipefail

# List every SKILL.md in the repo, grouped by bucket.
#
# Usage:
#   ./scripts/list-skills.sh

REPO="$(cd "$(dirname "$0")/.." && pwd)"

find "$REPO/skills" -name SKILL.md \
  -not -path '*/node_modules/*' \
  | sort
