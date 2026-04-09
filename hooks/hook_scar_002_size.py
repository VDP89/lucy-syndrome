#!/usr/bin/env python3
"""
PreToolUse Write|Edit hook — scar_002 code_review_absent

If the file is code (py/js/ts/jsx/tsx) and the block being written exceeds
LINE_THRESHOLD lines, remind the model to run a 3-step self-review before
declaring the code ready to execute.

Severity: warn (no blocking, context injection only).
"""
import json
import sys

CODE_EXTENSIONS = (".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs")
LINE_THRESHOLD = 200

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

if not file_path.endswith(CODE_EXTENSIONS):
    sys.exit(0)

line_count = content.count("\n") + (1 if content else 0)
if line_count <= LINE_THRESHOLD:
    sys.exit(0)

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": (
            f"scar_002 (code_review_absent) | You are editing code "
            f"({line_count} lines, > {LINE_THRESHOLD}). "
            "REMINDER: before declaring this ready, run the 3-step self-review: "
            "(1) read the file end to end, (2) grep for the known anti-patterns "
            "(see scar doc), (3) validate the function contracts against the caller. "
            "See ./scars/scar_002_code_review_absent.md"
        ),
    },
    "systemMessage": f"scar_002 active: {line_count}-line block requires self-review",
}

json.dump(output, sys.stdout)
