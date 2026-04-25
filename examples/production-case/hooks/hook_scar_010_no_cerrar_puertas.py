#!/usr/bin/env python3
"""
Hook PreToolUse Write|Edit — scar_010 definir_por_lo_que_somos
Si el archivo editado es entregable de comunicacion/marca y el contenido tiene
patrones de negacion que cierran puertas ("no es X", "sin Y", "lo que NO", etc.)
emite warning. Severity: warn (no bloquea).
"""
import json
import re
import sys

# Paths donde la regla aplica (deliverables de comunicacion publica)
TRIGGER_PATH_FRAGMENTS = (
    "05_imagen_comunicacion",
    "07_marca",
    "04_comercial",
    "04_leads",
    "08_compendio_final",
)
TRIGGER_NAME_FRAGMENTS = (
    "brand",
    "marca",
    "landing",
    "brochure",
    "pitch",
    "propuesta",
    "manual_marca",
    "manual-marca",
    "ergon",
    "marco_brand",
)
# Extensiones de entregable textual donde grepear
TEXT_EXTENSIONS = (".md", ".html", ".htm", ".txt", ".mdx")

# Patrones prohibidos en copy publico
PATTERNS = [
    (r"\bno\s+(es|somos|hacemos|ejecutamos)\b", "no es/somos/hacemos"),
    (r"\bNo\s+(un|una)\b", "No un/una"),
    (r"[Ss]in\s+(bombo|teatro|excepciones|gradientes|glassmorphism|sombras)\b", "sin X peyorativo"),
    (r"Lo\s+que\s+(NO|no)\s+(es|somos|hacemos)\b", "Lo que NO es"),
    (r"\ba\s+evitar\b", "a evitar"),
    (r"\bSensacion\s+a\s+evitar\b", "Sensacion a evitar"),
    (r"\bReferencias?\s+a\s+evitar\b", "Referencias a evitar"),
    (r"\bEn\s+lugar\s+de\s+[\"A-Z]", "En lugar de X"),
    (r"\b[Nn]unca\s+otros\b", "nunca otros"),
    (r"\b[Nn]ada\s+de\s+(gradientes|glassmorphism|sombras|stock)\b", "nada de X peyorativo"),
]

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = data.get("tool_input") or {}
file_path = (tool_input.get("file_path") or "").replace("\\", "/").lower()
content = (
    tool_input.get("content")
    or tool_input.get("new_string")
    or ""
)

# Skip archivos internos y tooling
if "/.claude/" in file_path or "/memory/" in file_path or "/node_modules/" in file_path:
    sys.exit(0)
if ".bak" in file_path or "_previews" in file_path or file_path.endswith(".py") or file_path.endswith(".js"):
    sys.exit(0)

# Solo en entregables
path_match = any(frag in file_path for frag in TRIGGER_PATH_FRAGMENTS)
name_match = any(frag in file_path for frag in TRIGGER_NAME_FRAGMENTS)
if not (path_match or name_match):
    sys.exit(0)

# Solo extensiones textuales
if not file_path.endswith(TEXT_EXTENSIONS):
    sys.exit(0)

if not content:
    sys.exit(0)

# Buscar matches
hits = []
for pattern, label in PATTERNS:
    m = re.search(pattern, content)
    if m:
        hits.append(f'{label}: "{m.group(0)}"')

if not hits:
    sys.exit(0)

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": (
            "scar_010 (definir_por_lo_que_somos) | Estas escribiendo copy en un entregable "
            "de marca/comunicacion con patrones de negacion que cierran puertas:\n- "
            + "\n- ".join(hits[:5])
            + "\n\nREGLA: copy publico describe SOLO lo que DG/ERGON/MARCO SON y HACEN. "
            "Reformular en afirmativo antes de cerrar. Ver "
            "D:/DG-2026_OFFICE/.claude/scarring/scar_010_definir_por_lo_que_somos.md"
        ),
    },
    "systemMessage": f"scar_010 activo: {len(hits)} patron(es) de negacion en copy publico",
}

json.dump(output, sys.stdout)
