#!/usr/bin/env python3
"""
Hook PreToolUse Task — scar_005 validate_subagent_output
Cada vez que se despacha un subagente, recordar que el prompt debe pedir
COBERTURA DEL BATCH (lista archivos vistos vs omitidos).
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

# Consumir stdin aunque no lo usemos (evita pipes rotos)
_raw = ""
try:
    _raw = sys.stdin.read()
except Exception:
    pass

_CONTEXT = (
    "scar_005 (validate_subagent_output) | Vas a despachar un subagente. "
    "RECORDATORIO: incluye explicitamente en el prompt la instruccion de reportar "
    "COBERTURA DEL BATCH (lista de archivos vistos vs omitidos). "
    "Si el subagente procesa N archivos, debe enumerar cuales reviso al cierre. "
    "Ver D:/DG-2026_OFFICE/.claude/scarring/scar_005_validate_subagent_output.md"
)
_SYSMSG = "scar_005 activo: el prompt al subagente debe pedir COBERTURA DEL BATCH"

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": _CONTEXT,
    },
    "systemMessage": _SYSMSG,
}

if _log:
    _log(
        scar_id="scar_005",
        hook_id="hook_scar_005_subagent",
        event_type="PreToolUse",
        trigger_match="Task event",
        severity="warn",
        tool_name="Task",
        context_injected=_CONTEXT,
        system_message=_SYSMSG,
        payload_raw=_raw[:500],
        start_time=_START,
    )

json.dump(output, sys.stdout)
