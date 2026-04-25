#!/usr/bin/env python3
"""
Hook PreToolUse Write|Edit — scar_example_001 review_before_deliver

Fires when a code file exceeding LINE_THRESHOLD lines is about to be written.
Reminds the model to run the 3-step self-review before delivering.

Severity: warn (injects additionalContext + systemMessage; does not block).
"""
import json
import sys

# ---- Configuration ----
CODE_EXTENSIONS = (".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".go", ".rb")
LINE_THRESHOLD = 200  # Lines; adjust to your tolerance

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = data.get("tool_input") or {}
file_path = (tool_input.get("file_path") or "").lower()
content = (
    tool_input.get("content")
    or tool_input.get("new_string")
    or ""
)

# Extension check
if not file_path.endswith(CODE_EXTENSIONS):
    sys.exit(0)

# Size check
line_count = content.count("\n") + (1 if content else 0)
if line_count <= LINE_THRESHOLD:
    sys.exit(0)

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": (
            f"scar_001 (review_before_deliver) | You are writing a code file "
            f"({line_count} lines, above the {LINE_THRESHOLD}-line threshold). "
            "REMINDER: before marking this as ready to execute, run the 3-step self-review: "
            "(1) read 5 random functions looking for silent handlers, spread-on-large-array, "
            "hardcoded paths; (2) verify function signatures match callers; "
            "(3) write the SELF-REVIEW block in your response. "
            "See .claude/scarring/scar_001_review_before_deliver.md"
        ),
    },
    "systemMessage": f"scar_001 active: {line_count}-line code file requires self-review before delivery",
}

json.dump(output, sys.stdout)
