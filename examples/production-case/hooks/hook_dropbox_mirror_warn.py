#!/usr/bin/env python3
"""
Hook SessionStart — anti Dropbox mirror.

Detecta si Claude Code se abrio desde la copia Dropbox de DG Office en lugar de la raiz D:/.
Trabajar desde la copia Dropbox duplica bootstrap de KBs y suma tokens innecesarios
(hallazgo de la auditoria de tokens 2026-04-24: 16.6M tokens en 72 sesiones desde mirror).

Si detecta cwd con "Dropbox/CONTABILIDAD" o ruta similar, emite warning como additionalContext.
Si no, salida vacia (no estorba).
"""
import json
import os
import sys

# Patrones de la copia Dropbox de DG Office
MIRROR_PATTERNS = [
    "dropbox/contabilidad",
    "dropbox\\contabilidad",
    "dg ing/contabilidad y detalles",
]

CANONICAL_PATH = "D:/DG-2026_OFFICE"

cwd = ""
try:
    raw = sys.stdin.read()
    if raw:
        data = json.loads(raw)
        cwd = data.get("cwd") or data.get("workspace") or ""
except Exception:
    pass

if not cwd:
    cwd = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()

cwd_lower = cwd.lower().replace("\\", "/")
is_mirror = any(p in cwd_lower for p in MIRROR_PATTERNS)

if is_mirror:
    msg = (
        "⚠️  AVISO: estas trabajando desde la copia Dropbox de DG Office "
        f"({cwd}). La auditoria de tokens 2026-04-24 detecto 16.6M tokens "
        f"consumidos en 72 sesiones desde esta copia (bootstrap duplicado). "
        f"Recomendacion: cerrar y reabrir Claude Code desde {CANONICAL_PATH}."
    )
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": msg,
        }
    }
    json.dump(output, sys.stdout)
# silencio si no es mirror
