#!/usr/bin/env python3
"""
Hook PreToolUse Write|Edit — scar_001 docx_tildes
Si el archivo editado es .py y el contenido toca docx, recordar fix_tildes.py.
Severity: warn (no bloquea, solo inyecta additionalContext + systemMessage).
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
            "scar_001 (docx_tildes) | Estas editando un script Python que toca docx. "
            "RECORDATORIO: tras generar el .docx hay que ejecutar fix_tildes.py para corregir "
            "tildes perdidas. Ver D:/DG-2026_OFFICE/.claude/scarring/scar_001_docx_tildes.md"
        ),
    },
    "systemMessage": "scar_001 activo: recordar fix_tildes.py post-generacion DOCX",
}

json.dump(output, sys.stdout)
