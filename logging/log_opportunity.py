#!/usr/bin/env python3
"""
log_opportunity.py — Lucy Syndrome Phase 3: Opportunity logging module.

Appends one JSON line to opportunities.jsonl per candidate opportunity detected
by the opportunity observer hook.

Together with fires.jsonl this enables computing recall/coverage:
  recall   = confirmed_fires / total_real_opportunities
  coverage = fires / (fires + missed_opportunities)

Schema: docs/logging-schema.json in this repo.
All failures are silent — this module must never break a hook.
"""
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

_LOGS_DIR = Path(__file__).parent.parent / "logs"
_OPPORTUNITIES_FILE = _LOGS_DIR / "opportunities.jsonl"


def _project_id() -> str:
    return hashlib.sha256(os.getcwd().encode()).hexdigest()[:8]


def log_opportunity(
    *,
    scar_id: str,
    session_id: str,
    event_type: str = "PreToolUse",
    tool_name: str | None = None,
    context_hash: str = "",
    project_context: str = "other",
    notes: str = "",
    fired: bool = False,
    validated: bool | None = None,
) -> None:
    """
    Append one OpportunityEvent to opportunities.jsonl.

    Parameters
    ----------
    scar_id         : e.g. "scar_002"
    session_id      : 8-char session hash (from log_scar_fire._session_id pattern)
    event_type      : SessionStart | PreToolUse | PostToolUse | UserPromptSubmit
    tool_name       : tool that triggered detection
    context_hash    : sha256[:16] of file_path + content[:200]
    project_context : project slug or "other"
    notes           : short description of what triggered detection
    fired           : False by default; True when a matching fire is linked
    validated       : None = pending review; True = real opportunity; False = false positive
    """
    try:
        entry = {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
            "session_id": session_id,
            "event_id": str(uuid.uuid4()),
            "scar_id": scar_id,
            "candidate": True,
            "validated": validated,
            "fired": fired,
            "source": "observer",
            "event_type": event_type,
            "tool_name": tool_name,
            "context_hash": context_hash,
            "project_id": _project_id(),
            "project_context": project_context,
            "notes": notes,
        }
        _OPPORTUNITIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _OPPORTUNITIES_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Never break the hook
