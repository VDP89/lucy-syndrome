#!/usr/bin/env python3
"""
Hook PreToolUse Write|Edit — scar_001 docx_tildes
Si el archivo editado es .py y el contenido toca docx, recordar fix_tildes.py.
Severity: warn (no bloquea, solo inyecta additionalContext + systemMessage).
"""
import json
import sys
import time

_START = time.time()

# --- logger import (falla silenciosamente si logs/ no existe aun) ---
try:
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).parent.parent / "logs"))
    from log_scar_fire import log_scar_fire as _log
except Exception:
    _log = None

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

_CONTEXT = (
    "scar_001 (docx_tildes) | Estas editando un script Python que toca docx. "
    "RECORDATORIO: tras generar el .docx hay que ejecutar fix_tildes.py para corregir "
    "tildes perdidas. Ver D:/DG-2026_OFFICE/.claude/scarring/scar_001_docx_tildes.md"
)
_SYSMSG = "scar_001 activo: recordar fix_tildes.py post-generacion DOCX"

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": _CONTEXT,
    },
    "systemMessage": _SYSMSG,
}

if _log:
    _log(
        scar_id="scar_001",
        hook_id="hook_scar_001_docx",
        event_type="PreToolUse",
        trigger_match=f"{file_path.rsplit('/', 1)[-1]} — docx",
        severity="warn",
        tool_name=data.get("tool_name", "Write"),
        context_injected=_CONTEXT,
        system_message=_SYSMSG,
        payload_raw=content[:500],
        start_time=_START,
    )

json.dump(output, sys.stdout)
