#!/usr/bin/env python3
"""
log_scar_fire.py — Lucy Syndrome Phase 2 logging module.

Appends one JSON line to fires.jsonl per hook fire.
Schema: ../docs/logging-schema.json
DOI: 10.5281/zenodo.19555971

Usage (from a hook script installed by install.sh):

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "logs"))
    from log_scar_fire import log_scar_fire

    log_scar_fire(
        scar_id="scar_001",
        hook_id="hook_scar_001_your_name",
        event_type="PreToolUse",
        trigger_match="file.py — keyword",
        tool_name="Write",
        context_injected=context_string,
        system_message=system_msg_string,
        payload_raw=content[:500],
        start_time=_START,
    )

Install path
------------
When install.sh runs, this file is copied to:
    <your-project>/.claude/scarring/logs/log_scar_fire.py

Fires are written to:
    <your-project>/.claude/scarring/logs/fires.jsonl

fires.jsonl is listed in .gitignore — it contains operational data, not code.

All failures are silent — the logger must never break the hook.
"""
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Log file lives in the same directory as this module.
# When installed: .claude/scarring/logs/fires.jsonl
_LOGS_DIR = Path(__file__).parent
_FIRES_FILE = _LOGS_DIR / "fires.jsonl"

# Default criticality per scar ID.
# Update this map to match your own scar criticalities.
# Fallback for unknown IDs: "media".
_CRITICIDAD_MAP: dict[str, str] = {
    # Add your own scar IDs here:
    # "scar_001": "media",
    # "scar_002": "alta",
    # "scar_003": "critica",
}


def _session_id() -> str:
    """8-char hash of cwd + UTC date — stable within a calendar day."""
    cwd = os.getcwd()
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return hashlib.sha256(f"{cwd}|{day}".encode()).hexdigest()[:8]


def _project_id() -> str:
    """8-char hash of the working directory — project-stable identifier."""
    return hashlib.sha256(os.getcwd().encode()).hexdigest()[:8]


def _active_model() -> str:
    for var in ("CLAUDE_MODEL", "ANTHROPIC_MODEL", "CLAUDE_CODE_MODEL"):
        val = os.environ.get(var)
        if val:
            return val
    return "unknown"


def _estimate_tokens(context: str, system_msg: str = "") -> int:
    return max(0, (len(context) + len(system_msg)) // 4)


def log_scar_fire(
    *,
    scar_id: str,
    hook_id: str,
    event_type: str,
    trigger_match: str,
    severity: str = "warn",
    outcome: str = "unknown",
    notes: str | None = None,
    tool_name: str | None = None,
    criticidad: str | None = None,
    hook_version: str = "1.0.0",
    context_injected: str = "",
    system_message: str = "",
    payload_raw: str = "",
    start_time: float | None = None,
) -> None:
    """
    Append one ScarFireEvent to fires.jsonl.

    Parameters
    ----------
    scar_id         : e.g. "scar_001". Pattern: scar_NNN (schema).
                      Non-scar hooks may use "infra_NNN" — noted as non-conformant.
    hook_id         : script filename without .py extension.
    event_type      : SessionStart | PreToolUse | PostToolUse | UserPromptSubmit
    trigger_match   : short fragment that matched the filter (<200 chars).
    severity        : warn | confirm | deny  (default: warn)
    outcome         : unknown (set by operator after review).
    notes           : optional operator annotation.
    tool_name       : tool that fired PreToolUse/PostToolUse; None for others.
    criticidad      : overrides _CRITICIDAD_MAP default.
    hook_version    : semantic version of the hook script.
    context_injected: additionalContext string emitted — used for token estimate.
    system_message  : systemMessage string emitted — used for token estimate.
    payload_raw     : raw trigger content for hashing (first 500 chars recommended).
    start_time      : time.time() recorded at hook script entry point.
    """
    try:
        latency_ms = round(
            (time.time() - (start_time if start_time is not None else time.time())) * 1000,
            2,
        )
        tokens = _estimate_tokens(context_injected, system_message)
        if criticidad is None:
            criticidad = _CRITICIDAD_MAP.get(scar_id, "media")

        ph_source = payload_raw or trigger_match
        payload_hash = (
            "sha256:"
            + hashlib.sha256(ph_source.encode("utf-8", errors="replace")).hexdigest()
        )

        entry = {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
            "session_id": _session_id(),
            "event_id": str(uuid.uuid4()),
            "scar_id": scar_id,
            "hook_id": hook_id,
            "hook_version": hook_version,
            "model": _active_model(),
            "project_id": _project_id(),
            "event_type": event_type,
            "tool_name": tool_name,
            "trigger_match": (trigger_match or "")[:200],
            "latency_ms": latency_ms,
            "tokens_added": tokens,
            "severity": severity,
            "outcome": outcome,
            "criticidad": criticidad,
            "payload_hash": payload_hash,
            "reviewed_by_human": False,
            "notes": notes,
        }

        _FIRES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _FIRES_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    except Exception:
        pass  # Never break the hook
