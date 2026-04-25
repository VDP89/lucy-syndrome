#!/usr/bin/env python3
"""
Hook SessionStart — Sistema RECUERDOS Fase 2
Inyecta resumen del SCARRING_INDEX como additionalContext al inicio de sesion.
"""
import json
import sys
import time

_START = time.time()

context = (
    "Sistema RECUERDOS activo (Fase 2 hooks). "
    "Cicatrices funcionales en D:/DG-2026_OFFICE/.claude/scarring/:\n"
    "- scar_001 docx_tildes [media]: ejecutar fix_tildes.py despues de generar DOCX\n"
    "- scar_002 code_review_absent [alta]: codigo grande requiere auto-revision en 3 pasos\n"
    "- scar_003 token_budget [media]: monitorear contexto en sesiones largas\n"
    "- scar_004 consult_kb_first [alta]: leer KB del area antes de generar\n"
    "- scar_005 validate_subagent_output [alta]: subagentes deben reportar COBERTURA DEL BATCH\n"
    "- scar_007 memory_update_session_close [alta]: AL CERRAR SESION actualizar memorias ANTES de despedir, sin esperar que Victor lo pida\n"
    "- scar_008 no_fabricar_contenido [critica]: sin URL verificable = no incluir. NUNCA inventar posts/threads que no existen\n"
    "- scar_009 verificar_dia_semana [critica]: NUNCA calcular dia de semana mentalmente. Contar desde fecha ancla del sistema o usar Bash/WebSearch\n\n"
    "Antes de tareas tecnicas relevantes invocar `Skill scar-check` o leer scar_NNN_*.md."
)

output = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}

# --- logging ---
try:
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).parent.parent / "logs"))
    from log_scar_fire import log_scar_fire as _log
    _log(
        scar_id="session_start",
        hook_id="hook_session_start",
        event_type="SessionStart",
        trigger_match="SessionStart",
        severity="warn",
        tool_name=None,
        context_injected=context,
        system_message="",
        payload_raw="SessionStart",
        start_time=_START,
        criticidad="baja",
    )
except Exception:
    pass

json.dump(output, sys.stdout)
