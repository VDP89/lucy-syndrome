#!/usr/bin/env python3
"""
Hook UserPromptSubmit — scar_004 Etapa 0 (expand_kb)

Proposito:
    Detectar cuando el prompt del usuario referencia proyectos/temas conocidos
    (presentes en MEMORY.md) o usa frases-trigger que implican contexto persistido,
    y recordar al operador que DEBE expandir los archivos puntero antes de generar
    claims sobre infraestructura/canales/estado del usuario.

Origen:
    Incidente 2026-04-15 (A3.1, expansion_vs_lectura). Primera reincidencia
    registrada de scar_004 tras publicacion Fase 2. El operador cumplio la cicatriz
    formalmente (leyo indice) y fallo funcionalmente (no expandio los archivos
    puntero referenciados por el task). Ver:
    05_IMAGEN_COMUNICACION/08_LABORATORIO_DG/00_PROYECTO_LUCY/02_ANALISIS/
      incidente_2026-04-15_expansion_vs_lectura.md

Severity: warn (inyecta additionalContext + systemMessage, no bloquea).

Rollout:
    Semana 1 — soft (solo recordatorio)
    Semana 2+ — evaluar si endurecer a bloqueo PreToolUse
"""
import json
import re
import sys
import time
from pathlib import Path

_START = time.time()

# --- logger import ---
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "logs"))
    from log_scar_fire import log_scar_fire as _log
except Exception:
    _log = None

# --- Configuracion ---

MEMORY_PATH = Path.home() / ".claude" / "projects" / "D--DG-2026-OFFICE" / "memory" / "MEMORY.md"

# Frases-trigger: referencias a contexto compartido que implican memoria persistida.
TRIGGER_PHRASES = [
    "nuestro plan",
    "nuestra estrategia",
    "nuestro proyecto",
    "nuestra base",
    "como quedamos",
    "lo que definimos",
    "la base que construimos",
    "segun quedamos",
    "nuestro acuerdo",
    "lo que acordamos",
    "nuestro enfoque",
]

# Stopwords para extraccion de keywords desde titulos/hooks de MEMORY.md.
STOPWORDS = {
    "para", "desde", "hasta", "entre", "segun", "sobre", "esta", "este", "esto",
    "estos", "estas", "como", "cuando", "donde", "pero", "porque", "aunque",
    "mientras", "hacer", "tener", "poner", "usar", "debe", "debes", "seria",
    "sera", "fue", "son", "los", "las", "del", "con", "por", "una", "uno",
    "que", "mas", "muy", "asi", "mismo", "cada", "todo", "toda", "otro", "otra",
    "and", "the", "for", "with", "from", "this", "that", "into", "onto", "upon",
    "but", "yet", "not", "can", "may", "has", "have", "had", "are", "was",
    "project", "feedback", "reference", "user", "files", "file", "memory",
    "mem", "note", "notes",
    # stopwords administrativos (evitar false positives en cierres de sesion)
    "sesion", "session", "cerramos", "cerrar", "cerrar", "abrir", "guardar",
    "despedir", "terminar", "finalizar", "listo", "listos", "hecho", "hechos",
}

# Frontmatter/indice a ignorar cuando hacemos parsing.
HEADER_PATTERNS = [
    re.compile(r"^\s*#"),  # headers markdown
    re.compile(r"^\s*$"),  # lineas vacias
]

# Patron de entry del indice: `- [Title](file.md) — hook` o variantes.
ENTRY_LINE_PATTERN = re.compile(
    r"""^\s*[-*]\s*                           # guion inicial
        (?:\[(?P<title>[^\]]+)\]              # [Title] opcional
        \((?P<link>[^)]+\.md)\)               # (file.md) opcional
        |(?P<bare_name>[a-z_][a-z0-9_\-]*)\s*→) # o `bare-name → ...` (permite guiones)
        \s*[—\-–]?\s*                         # separador
        (?P<hook>.*)$                         # resto de la linea
    """,
    re.VERBOSE | re.IGNORECASE,
)

MAX_RESULTS = 5
MIN_KEYWORD_LEN = 4
MIN_MATCH_COUNT = 2  # subido de 1 a 2 para reducir false positives (calibracion 2026-04-25)


def extract_keywords(text: str) -> set:
    """Extrae keywords relevantes (>= MIN_KEYWORD_LEN chars, no stopwords, lowercase)."""
    if not text:
        return set()
    tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())
    return {
        t for t in tokens
        if len(t) >= MIN_KEYWORD_LEN
        and t not in STOPWORDS
    }


def parse_memory_index(path: Path) -> list:
    """
    Parse MEMORY.md y devuelve lista de entries:
    [{file: str, title: str, hook: str, keywords: set}, ...]
    """
    entries = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return entries

    for line in text.splitlines():
        if any(p.match(line) for p in HEADER_PATTERNS):
            continue
        m = ENTRY_LINE_PATTERN.match(line)
        if not m:
            continue

        link = m.group("link") or ""
        bare = m.group("bare_name") or ""
        file_ref = link or (bare + ".md" if bare else "")
        if not file_ref:
            continue

        title = m.group("title") or bare
        hook = (m.group("hook") or "").strip()

        # Keywords: combinamos basename (sin prefijo project_/feedback_/etc),
        # palabras del title, y primeras palabras del hook.
        basename = file_ref.replace(".md", "").rsplit("/", 1)[-1]
        basename_clean = re.sub(r"^(project|feedback|reference|user|agent)_", "", basename)
        basename_words = re.sub(r"[_\-]", " ", basename_clean)

        kw = set()
        kw.update(extract_keywords(basename_words))
        kw.update(extract_keywords(title))
        kw.update(extract_keywords(hook[:120]))

        entries.append({
            "file": file_ref,
            "title": title.strip(),
            "hook": hook,
            "keywords": kw,
        })

    return entries


def score_entries(entries: list, prompt_kw: set) -> list:
    """Ranking: count de keywords matcheados por entry, descendente."""
    scored = []
    for e in entries:
        matched = e["keywords"] & prompt_kw
        if len(matched) >= MIN_MATCH_COUNT:
            scored.append({
                **e,
                "matched": sorted(matched),
                "score": len(matched),
            })
    scored.sort(key=lambda x: (-x["score"], x["file"]))
    return scored


def build_context_message(prompt: str, matches: list, trigger_hit: bool) -> str:
    """Arma el additionalContext inyectado."""
    lines = []
    lines.append("scar_004 Etapa 0 (expand_kb) | ")

    if trigger_hit and not matches:
        lines.append(
            "Detecte frase-trigger que implica contexto persistido "
            "(ej: 'nuestro plan', 'nuestra estrategia'). "
            "Antes de responder con claims sobre infraestructura/canales/estado del usuario, "
            "expandir archivos relevantes de MEMORY.md (no solo el indice). "
        )
    elif matches:
        lines.append(
            f"Tu prompt referencia temas presentes en memoria persistida "
            f"({', '.join(sorted({k for m in matches for k in m['matched']})[:8])}). "
            "Antes de responder, leer con Read:"
        )
        base = str(MEMORY_PATH.parent).replace("\\", "/").rstrip("/") + "/"
        for m in matches[:MAX_RESULTS]:
            hook_short = m["hook"][:90] + ("..." if len(m["hook"]) > 90 else "")
            lines.append(f"\n  - {base}{m['file']} — {hook_short}")

    lines.append(
        "\nEl indice MEMORY.md NO satisface scar_004 — requiere Read sobre los "
        "archivos puntero. Ver scar_004_consult_kb_first.md § Etapa 0."
    )
    return "".join(lines)


def main():
    # Forzar stdout UTF-8 (em-dashes y tildes del contenido inyectado).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    # Leer input (no criticamos si falla — salir silencioso).
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        sys.exit(0)

    prompt_lower = prompt.lower()

    # Deteccion de frases-trigger (literal, case-insensitive).
    trigger_hit = any(phrase in prompt_lower for phrase in TRIGGER_PHRASES)

    # Matching de keywords contra entries de MEMORY.md.
    entries = parse_memory_index(MEMORY_PATH)
    prompt_kw = extract_keywords(prompt)
    matches = score_entries(entries, prompt_kw)

    # Si no hay nada que decir, salir silencioso.
    if not trigger_hit and not matches:
        sys.exit(0)

    context = build_context_message(prompt, matches, trigger_hit)

    _sysmsg = (
        f"scar_004 Etapa 0: expandir {len(matches[:MAX_RESULTS])} archivo(s) de memoria"
        if matches else
        "scar_004 Etapa 0: frase-trigger detectada, expandir memoria relevante"
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        },
        "systemMessage": _sysmsg,
    }

    if _log:
        _kw_summary = ", ".join(sorted({k for m in matches for k in m["matched"]})[:5]) if matches else "trigger_phrase"
        _log(
            scar_id="scar_004",
            hook_id="hook_scar_004_expand",
            event_type="UserPromptSubmit",
            trigger_match=_kw_summary[:200],
            severity="warn",
            tool_name=None,
            context_injected=context,
            system_message=_sysmsg,
            payload_raw=prompt[:500],
            start_time=_START,
        )

    json.dump(output, sys.stdout)


if __name__ == "__main__":
    main()
