#!/usr/bin/env python3
"""
Hook PreToolUse Write|Edit — scar_002 code_review_absent
Si el archivo es codigo (py/js/ts/jsx/tsx) y el bloque escrito >200 lineas,
recordar auto-revision en 3 pasos antes de entregar.
Severity: warn.
"""
import json
import sys
import time

_START = time.time()

# --- logger import ---
try:
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).parent.parent / "logs"))
    from log_scar_fire import log_scar_fire as _log
except Exception:
    _log = None

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

_CONTEXT = (
    f"scar_002 (code_review_absent) | Estas editando codigo "
    f"({line_count} lineas, > {LINE_THRESHOLD}). "
    "RECORDATORIO: antes de entregar ejecuta auto-revision en 3 pasos: "
    "(1) leer el archivo completo, (2) buscar bugs y edge cases, "
    "(3) validar contra el requerimiento. "
    "Ver D:/DG-2026_OFFICE/.claude/scarring/scar_002_code_review_absent.md"
)
_SYSMSG = f"scar_002 activo: bloque de {line_count} lineas requiere auto-revision"

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": _CONTEXT,
    },
    "systemMessage": _SYSMSG,
}

if _log:
    _log(
        scar_id="scar_002",
        hook_id="hook_scar_002_size",
        event_type="PreToolUse",
        trigger_match=f"{file_path.rsplit('/', 1)[-1]} — {line_count} lines",
        severity="warn",
        tool_name=data.get("tool_name", "Write"),
        context_injected=_CONTEXT,
        system_message=_SYSMSG,
        payload_raw=content[:500],
        start_time=_START,
    )

json.dump(output, sys.stdout)
