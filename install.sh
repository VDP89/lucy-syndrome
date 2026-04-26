#!/usr/bin/env bash
# install.sh -- bootstrap the Lucy Syndrome scarring system into your Claude Code project
#
# Usage:
#   ./install.sh /path/to/your/project
#
# What it does:
#   - Creates .claude/scarring/{hooks,logs}/ in your project
#   - Copies the blank scar template as scar_001_your_first_scar.md
#   - Copies the generic SessionStart hook (auto-discovers scars) and example review hook
#   - Copies the JSONL fire logger
#   - Wires hooks: writes .claude/settings.json verbatim if absent; otherwise leaves your
#     settings.json alone and prints merge instructions
#   - Runs a smoke test against the installed hooks
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
LOGS_DIR="${SCARRING_DIR}/logs"
SETTINGS_FILE="${CLAUDE_DIR}/settings.json"
SETTINGS_EXAMPLE_SRC="${REPO_DIR}/framework/settings.json.example"

# ---- Warn if already installed ----
if [ -d "$SCARRING_DIR" ]; then
  echo "Warning: ${SCARRING_DIR} already exists. Existing files will not be overwritten."
  echo "Press Ctrl+C to cancel, or Enter to continue and add missing files only."
  read -r
fi

# ---- Create directories ----
mkdir -p "$HOOKS_DIR"
mkdir -p "$LOGS_DIR"
echo "Created: $SCARRING_DIR"
echo "Created: $HOOKS_DIR"
echo "Created: $LOGS_DIR"

# ---- Copy scar template (as first scar placeholder) ----
FIRST_SCAR="${SCARRING_DIR}/scar_001_your_first_scar.md"
if [ ! -f "$FIRST_SCAR" ]; then
  cp "${REPO_DIR}/framework/scar_template.md" "$FIRST_SCAR"
  echo "Copied:  $FIRST_SCAR"
else
  echo "Skipped: $FIRST_SCAR (already exists)"
fi

# ---- Copy logger module ----
LOGGER_DEST="${LOGS_DIR}/log_scar_fire.py"
if [ ! -f "$LOGGER_DEST" ]; then
  cp "${REPO_DIR}/logging/log_scar_fire.py" "$LOGGER_DEST"
  echo "Copied:  $LOGGER_DEST"
else
  echo "Skipped: $LOGGER_DEST (already exists)"
fi

# ---- Create logs .gitignore (fires.jsonl is operational data, not code) ----
LOGS_GITIGNORE="${LOGS_DIR}/.gitignore"
if [ ! -f "$LOGS_GITIGNORE" ]; then
  cp "${REPO_DIR}/logging/.gitignore" "$LOGS_GITIGNORE"
  echo "Copied:  $LOGS_GITIGNORE"
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

# ---- Wire settings.json ----
SETTINGS_WIRED=0
if [ ! -f "$SETTINGS_FILE" ]; then
  cp "$SETTINGS_EXAMPLE_SRC" "$SETTINGS_FILE"
  echo "Created: $SETTINGS_FILE  (hooks wired automatically)"
  SETTINGS_WIRED=1
else
  # Always keep an up-to-date reference example next to user's existing settings.
  cp "$SETTINGS_EXAMPLE_SRC" "${CLAUDE_DIR}/settings.json.example"
  echo "Found:   $SETTINGS_FILE  (left untouched -- merge the 'hooks' key manually)"
  echo "Copied:  ${CLAUDE_DIR}/settings.json.example  (reference)"
fi

# ---- Create minimal SCARRING_INDEX.md ----
INDEX="${SCARRING_DIR}/SCARRING_INDEX.md"
if [ ! -f "$INDEX" ]; then
  cat > "$INDEX" << 'EOF'
# Scarring Index

> Edit this file to track your active scars.
> Created by install.sh -- Lucy Syndrome framework
> See https://github.com/VDP89/lucy-syndrome for full documentation.

## Active Scars

| ID | Name | Severity | Activations | Last applied |
|---|---|---|---:|---|
| scar_001 | your_first_scar | medium | 0 | never |

## Management Policy

- **Append-only**: scars are never deleted. If a scar becomes obsolete, mark it `[ARCHIVED]` with date and reason -- the file stays.
- **Lifetime review**: if a scar has not activated in 30 days, review whether the trigger is still relevant.
- **Refinement**: if a scar fires but the error still occurs, the rule is too fuzzy -- edit the scar to sharpen it.
- **New scars**: if an error pattern recurs 2+ times, codify it as a new scar.
EOF
  echo "Created: $INDEX"
fi

# ---- Smoke test ----
echo ""
echo "Running smoke test..."
SMOKE_OK=1
if ! command -v python3 >/dev/null 2>&1; then
  echo "  Skipped: python3 not found on PATH. Install Python 3.10+ before using the hooks."
  SMOKE_OK=0
else
  # Run hook_session_start with empty stdin from inside the project dir so the
  # default SCAR_DIR resolves to the freshly-installed .claude/scarring/.
  if (cd "$PROJECT_DIR" && echo '{}' | python3 "$HOOKS_DIR/hook_session_start.py" 2>/dev/null) \
       | python3 -c 'import json, sys; d=json.load(sys.stdin); assert d["hookSpecificOutput"]["hookEventName"]=="SessionStart"' 2>/dev/null; then
    echo "  OK: hook_session_start.py emits valid SessionStart output"
  else
    echo "  FAIL: hook_session_start.py did not emit valid output"
    SMOKE_OK=0
  fi
  # hook_example_review on a small payload should exit silently with no stdout.
  REVIEW_OUT=$(echo '{"tool_name":"Write","event":"PreToolUse","tool_input":{"file_path":"x.py","content":"x=1"}}' \
                 | python3 "$HOOKS_DIR/hook_example_review.py" 2>/dev/null || true)
  if [ -z "$REVIEW_OUT" ]; then
    echo "  OK: hook_example_review.py exits silently for short files"
  else
    echo "  FAIL: hook_example_review.py produced unexpected output for a 1-line file"
    SMOKE_OK=0
  fi
fi

# ---- Done ----
echo ""
if [ "$SMOKE_OK" -eq 1 ]; then
  echo "Installation complete and smoke test passed."
else
  echo "Installation complete -- smoke test had warnings (see above)."
fi
echo ""
echo "Next steps:"
echo ""
echo "  1. Edit the blank scar:"
echo "       ${FIRST_SCAR}"
echo "     Fill in what happened, the trigger, the fix."
echo ""
if [ "$SETTINGS_WIRED" -eq 1 ]; then
  echo "  2. Hooks are wired in ${SETTINGS_FILE}."
  echo "     Restart Claude Code (or open it from this project) to pick them up."
else
  echo "  2. Merge the 'hooks' key from ${CLAUDE_DIR}/settings.json.example"
  echo "     into your existing ${SETTINGS_FILE}."
fi
echo ""
echo "  3. Add log_scar_fire() calls to your custom hooks (see logging/README.md):"
echo "       ${LOGS_DIR}/log_scar_fire.py  <-- already installed"
echo "       ${REPO_DIR}/logging/README.md  <-- integration pattern"
echo ""
echo "  4. Optionally review the production case for inspiration:"
echo "       ${REPO_DIR}/examples/production-case/"
echo ""
echo "  5. Read the framework guide:"
echo "       ${REPO_DIR}/framework/README.md"
echo ""
echo "  Full documentation: https://github.com/VDP89/lucy-syndrome"
