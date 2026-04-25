#!/usr/bin/env python3
"""
opportunity_observer.py — Lucy Syndrome Phase 3: Opportunity logging hook.

Registers candidate opportunities in opportunities.jsonl (separate from fires.jsonl).

The key distinction:
  fires.jsonl        = "the hook actually fired"     → precision signal
  opportunities.jsonl = "the hook should have had a chance to fire" → recall denominator

Without opportunities, all coverage metrics collapse to fires/fires = 1.0 (trivially useless).

IMPORTANT: The opportunity rules are intentionally BROADER than the hook trigger thresholds.
A scar_002 hook might only fire when code exceeds 200 lines, but any code generation is an
opportunity — three 80-line blocks in one task are still three opportunities.

Installation
------------
Copy to .claude/scarring/hooks/hook_opportunity_observer.py and register in settings.json
as a PostToolUse hook for Write|Edit|Task events (notification type, never blocks).

Adapt _OPPORTUNITY_RULES to match your local scar definitions.

Schema: docs/logging-schema.json in this repo.
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

# --- logger import (fails silently if not installed) ---
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "logs"))
    from log_opportunity import log_opportunity as _log_opp
except Exception:
    _log_opp = None

# ------------------------------------------------------------------ #
# Configuration — adapt to your local scar definitions
# ------------------------------------------------------------------ #

# Code file extensions — any Write/Edit to these is a scar_002 opportunity
CODE_EXTENSIONS = (".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
                   ".cs", ".java", ".go", ".rs", ".rb", ".swift", ".kt")

# Paths/name patterns that indicate deliverable files (for scar_010/011)
DELIVERABLE_PATTERNS = (
    "landing", "report", "informe", "brand", "entregable",
)

# Project keywords for project_context classification
PROJECT_KEYWORDS: dict[str, list[str]] = {
    # Override with your own project names
    "project_a": ["project_a", "proj-a"],
    "project_b": ["project_b", "proj-b"],
}


def _detect_project(path: str, content: str) -> str:
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
# Opportunity detection rules (broader than hook trigger thresholds)
# ------------------------------------------------------------------ #

opportunities_detected: list[dict] = []

# scar_001: any .docx file written — broader than "Python scripts that touch docx"
if tool_name in ("Write", "Edit") and file_path.endswith(".docx"):
    opportunities_detected.append({
        "scar_id": "scar_001",
        "notes": f"direct .docx write: {Path(file_path).name}",
    })

# scar_002: ANY code file Write/Edit — no line-count threshold, no project filter.
# The hook fires only at >200 lines; the opportunity exists at 1 line.
if tool_name in ("Write", "Edit") and file_path.endswith(CODE_EXTENSIONS):
    line_count = content.count("\n") + (1 if content else 0)
    opportunities_detected.append({
        "scar_id": "scar_002",
        "notes": f"code write {line_count}L: {Path(file_path).name}",
    })

# scar_005: any Task dispatch — same breadth as the hook, but recorded as opportunity
if tool_name == "Task":
    opportunities_detected.append({
        "scar_id": "scar_005",
        "notes": "Task dispatch detected",
    })

# scar_010 / scar_011: Write/Edit to deliverable paths
if tool_name in ("Write", "Edit") and any(pat in file_path for pat in DELIVERABLE_PATTERNS):
    opportunities_detected.append({
        "scar_id": "scar_010",
        "notes": f"deliverable write: {Path(file_path).name}",
    })
    if file_path.endswith((".html", ".md", ".txt", ".docx")):
        opportunities_detected.append({
            "scar_id": "scar_011",
            "notes": f"deliverable text: {Path(file_path).name}",
        })

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

# Observer never blocks — always emit empty output
json.dump({}, sys.stdout)
