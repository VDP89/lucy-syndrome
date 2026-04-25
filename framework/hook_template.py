#!/usr/bin/env python3
"""
Hook [EventName] [Matcher] — scar_NNN short_name

[One sentence describing what this hook detects and what it reminds the model to do.]

Event: SessionStart | PreToolUse | PostToolUse | UserPromptSubmit
Matcher (PreToolUse only): Write|Edit | Task | Bash | Read | ...
Severity: warn (injects additionalContext + systemMessage; does not block)
"""
import json
import sys

# ---- Configuration ----
# Adjust these constants for your specific trigger:

# For PreToolUse Write|Edit hooks: file extensions to watch
TRIGGER_EXTENSIONS = (".py", ".js", ".ts")  # e.g. (".py",) or () to skip extension check

# For content-pattern hooks: strings whose presence in the file content triggers the hook
TRIGGER_CONTENT_PATTERNS = ("keyword_one", "keyword_two")  # or () to skip

# Line count threshold for size-based triggers (0 to disable)
LINE_THRESHOLD = 0


# ---- Input parsing ----
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = data.get("tool_input") or {}

# For SessionStart hooks, tool_input will be empty — skip the checks below
# and go directly to emitting the output.

# ---- Trigger detection ----
file_path = (tool_input.get("file_path") or "").lower()
content = (
    tool_input.get("content")
    or tool_input.get("new_string")
    or ""
)

# Extension check (delete if not needed)
if TRIGGER_EXTENSIONS and not file_path.endswith(TRIGGER_EXTENSIONS):
    sys.exit(0)

# Content pattern check (delete if not needed)
if TRIGGER_CONTENT_PATTERNS:
    content_lower = content.lower()
    if not any(p in content_lower for p in TRIGGER_CONTENT_PATTERNS):
        sys.exit(0)

# Line count check (delete if not needed)
if LINE_THRESHOLD > 0:
    line_count = content.count("\n") + (1 if content else 0)
    if line_count <= LINE_THRESHOLD:
        sys.exit(0)

# ---- Emit the reminder ----
output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",  # Change to "SessionStart" etc. if needed
        "additionalContext": (
            "scar_NNN (short_name) | [One-line reminder of what to do. "
            "Be specific: name the action, name where the scar doc lives.] "
            "See .claude/scarring/scar_NNN_short_name.md"
        ),
    },
    "systemMessage": "scar_NNN active: [short action prompt shown to operator]",
}

json.dump(output, sys.stdout)
