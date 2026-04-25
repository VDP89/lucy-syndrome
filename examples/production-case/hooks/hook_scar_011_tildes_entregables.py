#!/usr/bin/env python3
"""
Hook PreToolUse Write|Edit — scar_011 tildes_entregables
Si el archivo editado es un entregable textual en español y el contenido tiene
palabras comunes sin tilde (funcion, gestion, tambien, ingenieria, etc.),
emite warning. Severity: warn (no bloquea).
"""
import json
import re
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

# Paths de entregables publicos donde la regla aplica
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
    "manual_marca",
    "manual-marca",
    "propuesta",
    "informe_",
    "brochure",
)
# Extensiones textuales de entregable
TEXT_EXTENSIONS = (".md", ".html", ".htm", ".txt", ".mdx")

# Palabras-trigger sin tildes que deberian tenerlas en entregables
UNACCENTED_WORDS = [
    # -cion / -sion
    "funcion", "gestion", "fiscalizacion", "prediccion", "aplicacion",
    "seccion", "revision", "decision", "accion", "direccion", "dimension",
    "version", "construccion", "comunicacion", "regulacion", "informacion",
    "implementacion", "relacion", "navegacion", "solucion", "atencion",
    # -ia / -ias
    "ingenieria", "tecnologia", "tipografia", "fotografia", "energia",
    "ergonomia", "teoria", "categoria", "filosofia", "geometria",
    # -ico / -ica
    "fisico", "economico", "tecnico", "tecnologico", "tipografico",
    "grafico", "critico", "clasico", "historico", "mecanico", "publico",
    "semantico", "estrategico", "estetico", "logico",
    # adverbios / comunes
    "tambien", "despues", "ademas", "aqui", "alli", "ahi", "segun",
    # sustantivos
    "pagina", "linea", "nucleo", "raiz", "pais", "titulo", "numero",
    "codigo", "proposito",
    # n
    "dueno", "diseno", "pequeno", "acompanado", "senal",
    # propios
    "Asuncion", "Aristoteles", "Nicomaco",
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

# Skip archivos internos, tooling, bakups, previews
if "/.claude/" in file_path or "/memory/" in file_path or "/node_modules/" in file_path:
    sys.exit(0)
if ".bak" in file_path or "_previews" in file_path or "_capture_" in file_path or "_fix_tildes" in file_path:
    sys.exit(0)
# Skip scripts (se escriben sin tildes por regla)
if file_path.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yml", ".yaml", ".toml")):
    sys.exit(0)

# Solo entregables
path_match = any(frag in file_path for frag in TRIGGER_PATH_FRAGMENTS)
name_match = any(frag in file_path for frag in TRIGGER_NAME_FRAGMENTS)
if not (path_match or name_match):
    sys.exit(0)

if not file_path.endswith(TEXT_EXTENSIONS):
    sys.exit(0)
if not content:
    sys.exit(0)

# Construir regex unico con todas las palabras (case-insensitive, word boundary)
pattern = r"\b(" + "|".join(re.escape(w) for w in UNACCENTED_WORDS) + r")\b"
matches = re.findall(pattern, content, flags=re.IGNORECASE)

if not matches:
    sys.exit(0)

# Deduplicar, conservando primeras ocurrencias
seen = []
for w in matches:
    wl = w.lower()
    if wl not in seen:
        seen.append(wl)
    if len(seen) >= 8:
        break

_CONTEXT = (
    f"scar_011 (tildes_entregables) | Entregable en español con {len(matches)} palabra(s) "
    f"sin tilde. Primeras detectadas: {', '.join(seen)}.\n"
    "REGLA: entregables (HTML publico, MD publico, PPTX, PDF, landing, brochure) "
    "exigen ortografia completa. Aplicar tildes antes de cerrar o ejecutar "
    "_fix_tildes_brand.py / fix_tildes.py segun el tipo. Ver "
    "D:/DG-2026_OFFICE/.claude/scarring/scar_011_tildes_entregables.md"
)
_SYSMSG = f"scar_011 activo: {len(matches)} palabra(s) sin tilde en entregable"

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": _CONTEXT,
    },
    "systemMessage": _SYSMSG,
}

if _log:
    _log(
        scar_id="scar_011",
        hook_id="hook_scar_011_tildes_entregables",
        event_type="PreToolUse",
        trigger_match=", ".join(seen[:5]),
        severity="warn",
        tool_name=data.get("tool_name", "Write"),
        context_injected=_CONTEXT,
        system_message=_SYSMSG,
        payload_raw=content[:500],
        start_time=_START,
    )

json.dump(output, sys.stdout)
