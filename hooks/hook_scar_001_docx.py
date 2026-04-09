#!/usr/bin/env python3
"""
PreToolUse Write|Edit hook — scar_001 docx_tildes

If the file being edited is Python and the content touches the docx
library, remind the model to run a post-generation tilde/accent fix
script.

Severity: warn (no blocking, context injection only).
"""
import json
import sys

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

if not file_path.endswith(".py"):
    sys.exit(0)

if "docx" not in content.lower():
    sys.exit(0)

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": (
            "scar_001 (docx_tildes) | You are editing a Python script that touches docx. "
            "REMINDER: after generating the .docx, run the tilde/accent fix "
            "post-processor to correct missing diacritics in uppercase headings. "
            "See ./scars/scar_001_docx_tildes.md"
        ),
    },
    "systemMessage": "scar_001 active: remember to run fix_tildes after DOCX generation",
}

json.dump(output, sys.stdout)
