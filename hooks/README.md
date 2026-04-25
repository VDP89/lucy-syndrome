# Hooks

> Claude Code hooks that enforce scars at the harness layer.
> Warn-only: no hook blocks a tool call; each one injects reminder context at the moment the trigger fires.

---

## Files in this directory

| File | Event | Trigger | Scar |
|---|---|---|---|
| `hook_session_start.py` | `SessionStart` | Every session | All active scars (summary) |
| `hook_example_review.py` | `PreToolUse Write\|Edit` | Code file > 200 lines | `scar_example_001` |

`settings.json` wiring is in `../framework/settings.json.example`. Rollback instructions are in `REVERSIBILITY.md`.

---

## How hooks work in Claude Code

Claude Code hooks are shell commands configured in `.claude/settings.json`. They fire at specific points in the tool use lifecycle:

- **`SessionStart`** — once when a new session begins. Use this to inject a summary of active scars.
- **`PreToolUse`** — before any tool call. A `matcher` string filters which tools fire the hook (`Write|Edit`, `Task`, `Bash`, `Read`, etc.).
- **`PostToolUse`** — after any tool call completes.
- **`UserPromptSubmit`** — when the user submits a message, before the model generates a response.

Each hook is a Python script that reads a JSON payload on stdin and writes a JSON response on stdout. A hook that exits with code 0 and no stdout output is invisible — it fired, found nothing relevant, and left no trace.

---

## Hook anatomy

All hooks share the same structure:

```python
#!/usr/bin/env python3
import json, sys

try:
    data = json.load(sys.stdin)  # Read tool input
except Exception:
    sys.exit(0)                  # Exit silently on bad input

tool_input = data.get("tool_input") or {}
# ... extract file_path, content, etc. ...

if not trigger_matches():
    sys.exit(0)  # Exit silently when trigger does not fire

output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": "reminder text injected into model context",
    },
    "systemMessage": "short line shown to the operator",
}
json.dump(output, sys.stdout)
```

Key design decisions:

- **Silent exit on non-matching invocations.** A hook wired to `Write|Edit` fires on every write. Exit with code 0 and no output for irrelevant calls.
- **Silent exit on malformed input.** `try/except` around stdin parsing means a broken input cannot break a tool call.
- **No blocking.** The hooks in this repository return `additionalContext` only — never `"permissionDecision": "deny"`. This is a deliberate choice: warn-only hooks create reminders; blocking hooks create friction that gets hooks disabled.
- **No dependencies.** All hooks use only `json` and `sys`. No requirements file needed.

---

## Testing a hook before wiring

Pipe a representative JSON payload into the hook on the command line:

```bash
# Test that the review hook fires on a large Python file:
python -c "
import json, sys
payload = {
    'tool_input': {
        'file_path': 'generate_report.py',
        'content': '\n' * 250  # 250 lines
    }
}
print(json.dumps(payload))
" | python hooks/hook_example_review.py | python -m json.tool
```

Expected output: a JSON object with `hookSpecificOutput.additionalContext` and `systemMessage`.

```bash
# Test that it exits silently for a short file:
python -c "
import json
print(json.dumps({'tool_input': {'file_path': 'foo.py', 'content': 'x = 1\n' * 10}}))
" | python hooks/hook_example_review.py && echo "Exit: $?"
```

Expected output: nothing (exit code 0).

---

## Writing your own hook

1. Copy `../framework/hook_template.py` and fill in the configuration constants.
2. Choose the narrowest event and matcher that covers your trigger.
3. Write the trigger detection logic — exit silently when the trigger does not match.
4. Write the `additionalContext` string: be specific. Name the action, name the scar doc path.
5. Test it from the command line before adding it to `settings.json`.
6. Add it to `settings.json` (see `../framework/settings.json.example`).
7. Verify it fires in a live session by matching a trigger condition.

For more complex hooks — including a `UserPromptSubmit` hook that parses a memory index and recommends files to read before generating — see `../examples/production-case/hooks/hook_scar_004_expand.py` (~240 lines, standard library only).

---

## Severity escalation

All hooks in this repository are warn-only by design. If you find that warn-only is not sufficient for a particular scar in your environment, you can escalate to blocking by adding `"permissionDecision": "deny"` to the output:

```python
output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": "...",
        "permissionDecision": "deny",
        "permissionDecisionReason": "This action requires completing the review checklist first.",
    },
    "systemMessage": "Blocked: complete the review first",
}
```

Use this sparingly. A blocked tool call interrupts the operator's flow; frustration tends to get hooks disabled.
