#!/usr/bin/env python3
"""
Hook PreToolUse Task — scar_005 validate_subagent_output
Cada vez que se despacha un subagente, recordar que el prompt debe pedir
COBERTURA DEL BATCH (lista archivos vistos vs omitidos).
Severity: warn.
"""
import json
import sys

# Consumir stdin aunque no lo usemos (evita pipes rotos)
try:
    sys.stdin.read()
except Exception:
    pass

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": (
            "scar_005 (validate_subagent_output) | Vas a despachar un subagente. "
            "RECORDATORIO: incluye explicitamente en el prompt la instruccion de reportar "
            "COBERTURA DEL BATCH (lista de archivos vistos vs omitidos). "
            "Si el subagente procesa N archivos, debe enumerar cuales reviso al cierre. "
            "Ver D:/DG-2026_OFFICE/.claude/scarring/scar_005_validate_subagent_output.md"
        ),
    },
    "systemMessage": "scar_005 activo: el prompt al subagente debe pedir COBERTURA DEL BATCH",
}

json.dump(output, sys.stdout)
