#!/usr/bin/env python3
"""
Hook SessionStart — Lucy Syndrome scarring system
Injects a summary of active scars as additionalContext at the start of every session.

Customize: edit the SCARS list below with your own scar IDs, names, severities,
and one-line descriptions. Keep each entry short — this fires on every session start.
"""
import json
import sys

# ---- Edit this list to match your active scars ----
SCARS = [
    ("scar_001", "review_before_deliver", "high",
     "3-step self-review before delivering any code >200 lines"),
    ("scar_002", "verify_before_claiming", "critical",
     "no URL = no item; never compute day-of-week from memory"),
    ("scar_003", "check_context_before_generating", "high",
     "read the KB before generating — index entries are not content"),
    # Add your own scars here:
    # ("scar_004", "your_scar_name", "medium", "one-line description"),
]

SCAR_DIR = ".claude/scarring"  # Adjust to your project's scar location


def build_context() -> str:
    lines = [
        "Scarring system active. Active scars in " + SCAR_DIR + ":\n"
    ]
    for scar_id, name, severity, description in SCARS:
        lines.append(f"- {scar_id} {name} [{severity}]: {description}")
    lines.append(
        "\nBefore starting technical work, check relevant scar files if the task "
        "matches a known trigger. See SCARRING_INDEX.md for the full list."
    )
    return "\n".join(lines)


output = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": build_context(),
    }
}

json.dump(output, sys.stdout)
