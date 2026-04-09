#!/usr/bin/env python3
"""
SessionStart hook — Lucy Syndrome / functional scars

Injects a short summary of active scars as additionalContext at the start
of every Claude Code session so the model is primed with the list of
known traps before any work begins.

Severity: warn (no blocking, context injection only).
"""
import json
import sys

# Consume stdin even if unused (avoids broken pipe when harness passes data)
try:
    sys.stdin.read()
except Exception:
    pass

context = (
    "Functional scars active (Lucy Syndrome Phase 2 hooks). "
    "Scars live in ./scars/:\n"
    "- scar_001 docx_tildes [medium]: run fix_tildes after generating DOCX\n"
    "- scar_002 code_review_absent [high]: large code blocks require 3-step self-review\n"
    "- scar_003 token_budget [medium]: monitor context on long sessions\n"
    "- scar_004 consult_kb_first [high]: read project knowledge base before generating\n"
    "- scar_005 validate_subagent_output [high]: subagents must report BATCH COVERAGE\n\n"
    "Before any substantive technical task, re-read the relevant scar_NNN_*.md."
)

output = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}

json.dump(output, sys.stdout)
