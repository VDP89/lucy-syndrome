#!/usr/bin/env bash
# install.sh — bootstrap the Lucy Syndrome scarring system into your Claude Code project
#
# Usage:
#   ./install.sh /path/to/your/project
#
# What it does:
#   - Creates .claude/scarring/ and .claude/scarring/hooks/ in your project
#   - Copies the blank scar template as your first scar to fill in
#   - Copies the generic session-start hook and example review hook
#   - Creates a minimal SCARRING_INDEX.md
#   - Outputs next steps

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-}"

# ---- Validate arguments ----
if [ -z "$PROJECT_DIR" ]; then
  echo "Usage: $0 /path/to/your/project"
  echo ""
  echo "Example: $0 ~/my-claude-project"
  exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: Project directory not found: $PROJECT_DIR"
  exit 1
fi

CLAUDE_DIR="${PROJECT_DIR}/.claude"
SCARRING_DIR="${CLAUDE_DIR}/scarring"
HOOKS_DIR="${SCARRING_DIR}/hooks"

# ---- Warn if already installed ----
if [ -d "$SCARRING_DIR" ]; then
  echo "Warning: ${SCARRING_DIR} already exists. Existing files will not be overwritten."
  echo "Press Ctrl+C to cancel, or Enter to continue and add missing files only."
  read -r
fi

# ---- Create directories ----
mkdir -p "$HOOKS_DIR"
echo "Created: $SCARRING_DIR"
echo "Created: $HOOKS_DIR"

# ---- Copy scar template (as first scar placeholder) ----
FIRST_SCAR="${SCARRING_DIR}/scar_001_your_first_scar.md"
if [ ! -f "$FIRST_SCAR" ]; then
  cp "${REPO_DIR}/framework/scar_template.md" "$FIRST_SCAR"
  echo "Copied:  $FIRST_SCAR"
else
  echo "Skipped: $FIRST_SCAR (already exists)"
fi

# ---- Copy generic hooks ----
for hook in hook_session_start.py hook_example_review.py; do
  DEST="${HOOKS_DIR}/${hook}"
  if [ ! -f "$DEST" ]; then
    cp "${REPO_DIR}/hooks/${hook}" "$DEST"
    echo "Copied:  $DEST"
  else
    echo "Skipped: $DEST (already exists)"
  fi
done

# ---- Copy REVERSIBILITY doc ----
REV="${SCARRING_DIR}/REVERSIBILITY.md"
if [ ! -f "$REV" ]; then
  cp "${REPO_DIR}/hooks/REVERSIBILITY.md" "$REV"
  echo "Copied:  $REV"
fi

# ---- Copy settings example ----
SETTINGS_EXAMPLE="${CLAUDE_DIR}/settings.json.example"
if [ ! -f "$SETTINGS_EXAMPLE" ]; then
  cp "${REPO_DIR}/framework/settings.json.example" "$SETTINGS_EXAMPLE"
  echo "Copied:  $SETTINGS_EXAMPLE"
fi

# ---- Create minimal SCARRING_INDEX.md ----
INDEX="${SCARRING_DIR}/SCARRING_INDEX.md"
if [ ! -f "$INDEX" ]; then
  cat > "$INDEX" << 'EOF'
# Scarring Index

> Edit this file to track your active scars.
> Created by install.sh — Lucy Syndrome framework
> See https://github.com/Vdp89/lucy-syndrome for full documentation.

## Active Scars

| ID | Name | Severity | Activations | Last applied |
|---|---|---|---:|---|
| scar_001 | your_first_scar | medium | 0 | never |

## Management Policy

- **Append-only**: scars are never deleted. If a scar becomes obsolete, mark it `[ARCHIVED]` with date and reason — the file stays.
- **Lifetime review**: if a scar has not activated in 30 days, review whether the trigger is still relevant.
- **Refinement**: if a scar fires but the error still occurs, the rule is too fuzzy — edit the scar to sharpen it.
- **New scars**: if an error pattern recurs 2+ times, codify it as a new scar.
EOF
  echo "Created: $INDEX"
fi

# ---- Done ----
echo ""
echo "Installation complete. Next steps:"
echo ""
echo "  1. Edit the blank scar:"
echo "       ${FIRST_SCAR}"
echo "     Fill in what happened, the trigger, the fix."
echo ""
echo "  2. Configure hooks in your Claude Code settings:"
echo "       ${SETTINGS_EXAMPLE}  ← example to adapt"
echo "       ${CLAUDE_DIR}/settings.json  ← merge the 'hooks' key into here"
echo ""
echo "  3. Optionally review the production case for inspiration:"
echo "       ${REPO_DIR}/examples/production-case/"
echo ""
echo "  4. Read the framework guide:"
echo "       ${REPO_DIR}/framework/README.md"
echo ""
echo "  Full documentation: https://github.com/Vdp89/lucy-syndrome"
