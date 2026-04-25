#!/usr/bin/env python3
"""
Hook PreToolUse Write|Edit — scar_002 code_review_absent
Si el archivo es codigo (py/js/ts/jsx/tsx) y el bloque escrito >200 lineas,
recordar auto-revision en 3 pasos antes de entregar.
Severity: warn.
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
            f"scar_002 (code_review_absent) | Estas editando codigo "
            f"({line_count} lineas, > {LINE_THRESHOLD}). "
            "RECORDATORIO: antes de entregar ejecuta auto-revision en 3 pasos: "
            "(1) leer el archivo completo, (2) buscar bugs y edge cases, "
            "(3) validar contra el requerimiento. "
            "Ver D:/DG-2026_OFFICE/.claude/scarring/scar_002_code_review_absent.md"
        ),
    },
    "systemMessage": f"scar_002 activo: bloque de {line_count} lineas requiere auto-revision",
}

json.dump(output, sys.stdout)
