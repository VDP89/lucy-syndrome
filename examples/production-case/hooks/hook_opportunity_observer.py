#!/usr/bin/env python3
"""
hook_opportunity_observer.py — Lucy Syndrome Phase 3: Opportunity Logging

Registers candidate opportunities in opportunities.jsonl (separate from fires.jsonl).
An "opportunity" is a context where a scar SHOULD apply, broader than the hook's
actual trigger threshold.

Key distinction:
- fires.jsonl   = "the hook actually fired" (precision signal)
- opportunities.jsonl = "the hook should have had a chance to fire" (recall denominator)

Without opportunities, recall = coverage = fires / fires = 1.0 (trivially useless).

Event type: notification only — never blocks execution.
All failures are silent.

Rules per scar (broader than hook trigger):
  scar_001: any .docx file being generated (not just scripts that touch docx)
  scar_002: any code file Write/Edit in DG context (no project filter, no line threshold)
  scar_004: any task touching files that exist in the project (not just keyword matches)
  scar_005: any Task tool dispatch (already broad, same as hook — for completeness)
  scar_010: any Write/Edit to entregables paths (content may need cerrar-puertas check)
  scar_011: any Write/Edit to entregables paths (tilde check)
"""
import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

_START = time.time()

# --- logger import ---
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "logs"))
    from log_opportunity import log_opportunity as _log_opp
except Exception:
    _log_opp = None

# ------------------------------------------------------------------ #
# Configuration
# ------------------------------------------------------------------ #

CODE_EXTENSIONS = (".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs", ".cs", ".java", ".go", ".rs")

ENTREGABLE_PATTERNS = (
    "05_imagen", "07_marca", "04_comercial", "04_leads",
    "brand", "marca", "landing", "ergon", "entregable",
    "informe", "reporte", "report", "memoria",
)

PROJECT_KEYWORDS = {
    "ergon": ["ergon"],
    "lucy": ["lucy", "lucy-syndrome", "lucy_syndrome"],
    "astro": ["dgingenieriapy", "astro", "web_dg", "sitio_web"],
    "istram": ["marco", "istram", "marco_istram"],
    "deflecto": ["deflecto", "deflectopro", "cartago"],
}


def _detect_project(path: str, content: str) -> str:
    """Best-effort project context from path + content."""
    combined = (path + " " + content[:300]).lower()
    for project, keywords in PROJECT_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return project
    return "other"


def _context_hash(payload: str) -> str:
    return "sha256:" + hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()[:16]


def _session_id() -> str:
    cwd = os.getcwd()
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return hashlib.sha256(f"{cwd}|{day}".encode()).hexdigest()[:8]


# ------------------------------------------------------------------ #
# Parse stdin
# ------------------------------------------------------------------ #

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

hook_name = data.get("hook_name", "")
tool_name = data.get("tool_name", "")
tool_input = data.get("tool_input") or {}
file_path = (tool_input.get("file_path") or "").lower().replace("\\", "/")
content = (
    tool_input.get("content")
    or tool_input.get("new_string")
    or tool_input.get("prompt")
    or ""
)

event_type = data.get("event", "PreToolUse")

# ------------------------------------------------------------------ #
# Opportunity detection rules
# ------------------------------------------------------------------ #

opportunities_detected = []

# scar_001: any .docx being written/created (broader than: py script that touches docx)
if tool_name in ("Write", "Edit") and file_path.endswith(".docx"):
    opportunities_detected.append({
        "scar_id": "scar_001",
        "notes": f"direct .docx write: {Path(file_path).name}",
    })

# scar_002: ANY code file Write/Edit in DG — no line threshold, no project filter
if tool_name in ("Write", "Edit") and file_path.endswith(CODE_EXTENSIONS):
    line_count = content.count("\n") + (1 if content else 0)
    opportunities_detected.append({
        "scar_id": "scar_002",
        "notes": f"code write {line_count}L: {Path(file_path).name}",
    })

# scar_004: Write/Edit to a file path that already exists (implies KB files exist to consult)
if tool_name in ("Write", "Edit") and file_path:
    # Opportunity: anything that writes to paths with project structure suggests
    # there may be KB to consult first. More conservative than hook (no keyword match needed).
    path_parts = file_path.replace("\\", "/").split("/")
    # Trigger if writing inside a known area or project directory (2+ depth)
    if len(path_parts) >= 3 and any(
        seg in file_path for seg in ["02_areas", "08_proyectos", "kb_", "_kb", "normativa"]
    ):
        opportunities_detected.append({
            "scar_id": "scar_004",
            "notes": f"write to project area: {'/'.join(path_parts[-2:])}",
        })

# scar_005: any Task tool dispatch
if tool_name == "Task":
    opportunities_detected.append({
        "scar_id": "scar_005",
        "notes": "Task dispatch detected",
    })

# scar_010: Write/Edit to entregables paths
if tool_name in ("Write", "Edit") and any(pat in file_path for pat in ENTREGABLE_PATTERNS):
    opportunities_detected.append({
        "scar_id": "scar_010",
        "notes": f"entregable write: {Path(file_path).name}",
    })

# scar_011: Write/Edit to any text entregable (html/md/txt/docx at entregable paths)
ENTREGABLE_TEXT_EXTS = (".html", ".md", ".txt", ".docx")
if tool_name in ("Write", "Edit") and (
    file_path.endswith(ENTREGABLE_TEXT_EXTS)
    and any(pat in file_path for pat in ENTREGABLE_PATTERNS)
):
    opportunities_detected.append({
        "scar_id": "scar_011",
        "notes": f"entregable text: {Path(file_path).name}",
    })

# No opportunities detected — exit cleanly
if not opportunities_detected:
    sys.exit(0)

# ------------------------------------------------------------------ #
# Log each opportunity
# ------------------------------------------------------------------ #

payload_for_hash = file_path + content[:200]
ctx_hash = _context_hash(payload_for_hash)
project_ctx = _detect_project(file_path, content)
session = _session_id()

if _log_opp:
    for opp in opportunities_detected:
        try:
            _log_opp(
                scar_id=opp["scar_id"],
                session_id=session,
                event_type=event_type,
                tool_name=tool_name,
                context_hash=ctx_hash,
                project_context=project_ctx,
                notes=opp.get("notes", ""),
                fired=False,
            )
        except Exception:
            pass

# Emit empty output — observer never blocks
json.dump({}, sys.stdout)
