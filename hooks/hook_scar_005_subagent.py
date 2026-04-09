#!/usr/bin/env python3
"""
PreToolUse Task hook — scar_005 validate_subagent_output

Every time a subagent is dispatched, remind the model that the subagent
prompt must explicitly request a BATCH COVERAGE section listing every
file or entity the subagent saw vs omitted.

Severity: warn (no blocking, context injection only).
"""
import json
import sys

# Consume stdin even if unused (avoids broken pipes)
try:
    sys.stdin.read()
except Exception:
    pass

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": (
            "scar_005 (validate_subagent_output) | You are about to dispatch a subagent. "
            "REMINDER: include the BATCH COVERAGE instruction in the prompt, requiring "
            "the subagent to list every input file or entity it saw (and any it skipped, "
            "with a reason) at the end of its output. Silence about a batch item is a "
            "known failure mode. "
            "See ./scars/scar_005_validate_subagent_output.md"
        ),
    },
    "systemMessage": "scar_005 active: subagent prompt must request BATCH COVERAGE",
}

json.dump(output, sys.stdout)
