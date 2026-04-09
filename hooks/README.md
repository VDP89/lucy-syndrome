# Hooks

> Claude Code hooks that enforce four of the five scars at the
> harness layer. Warn-only: no hook blocks a tool call; each one
> only injects reminder context at the moment the trigger fires.

## What is in this directory

| File | Purpose |
|---|---|
| `hook_session_start.py` | Injects a summary of all active scars at the start of every session |
| `hook_scar_001_docx.py` | Fires on Write/Edit of a Python file that touches `docx` |
| `hook_scar_002_size.py` | Fires on Write/Edit of a code file exceeding 200 lines |
| `hook_scar_005_subagent.py` | Fires on any `Task` tool call (subagent dispatch) |
| `settings.json.example` | Example `.claude/settings.json` wiring for the four hooks above |
| `REVERSIBILITY.md` | How to disable or roll back the hooks |

Scars 003 and 004 do not have hooks because their triggers cannot
be observed at the `PreToolUse` boundary — they are behavioral
protocols the model follows from session context alone.

## Installation

1. Copy the `hooks/` directory into your project. The natural
   location is `.claude/hooks/` inside your project root, but any
   path is fine as long as you adjust the command strings in
   `settings.json` to match.

2. Copy the contents of `settings.json.example` into your project's
   `.claude/settings.json`, adjusting the path in each `command`
   string if you placed the hooks somewhere other than `./hooks/`.
   If you already have a `settings.json` with unrelated hooks in
   it, merge the `hooks` key rather than overwriting.

3. Claude Code watches `settings.json` live. The hooks take effect
   on the next tool call; no restart is required. You can verify
   that the SessionStart hook fired by starting a new session and
   checking that the scar summary appears in the model's context.

4. Read [`REVERSIBILITY.md`](REVERSIBILITY.md) before adopting.
   All four hooks are warn-only by design, but you should know
   how to disable them before you install them.

## Severity design

All four hooks return `hookSpecificOutput.additionalContext` and a
`systemMessage` string. None of them return
`permissionDecision: deny`. This is a deliberate choice: the scars
are meant to be reminders, not gates. A hook that blocks a tool
call interrupts the operator's flow and produces resentment;
resentment gets scars disabled.

Warn-only hooks have a different failure mode: the model can
receive the reminder and still make the mistake. In practice,
having the reminder fire at the right moment is enough to catch
the mistake most of the time, because Lucy Syndrome fails through
absence of context, not through willful override.

If you find that a warn-only hook is not enough for a
particular scar in your environment, the path to a blocking hook
is simple: add `"permissionDecision": "deny"` and a `reason` field
to the output JSON. Use this sparingly.

## Hook anatomy

All four hooks share the same structural shape:

```python
#!/usr/bin/env python3
"""
Docstring naming the event, matcher, and scar.
"""
import json
import sys

# 1. Read the tool input from stdin (or ignore it, for SessionStart)
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

# 2. Decide whether this invocation should fire
tool_input = data.get("tool_input") or {}
# ... extract file_path, content, etc. and check triggers ...
if not trigger_matches(...):
    sys.exit(0)

# 3. Emit the response JSON on stdout
output = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",  # or "SessionStart"
        "additionalContext": "...",
    },
    "systemMessage": "short line shown to the operator",
}
json.dump(output, sys.stdout)
```

Key decisions in this shape:

- **Silent exit on non-matching invocations.** A hook that matches
  `Write|Edit` fires on every Write and every Edit. The vast
  majority of those invocations are not the case this hook cares
  about. The hook exits with code 0 and no output for all of them,
  and only emits JSON when the trigger actually fires. This keeps
  the hook invisible in normal use.

- **Silent exit on malformed input.** `try/except` around the
  stdin read means the hook cannot break a tool call by parsing
  badly. Combined with `2>/dev/null || true` in `settings.json`,
  a broken hook is equivalent to no hook.

- **Small, fast, dependency-free.** Each hook is under 50 lines
  of standard-library Python. No imports outside `json` and `sys`.
  This keeps invocation latency at a few milliseconds and makes
  the hooks portable to any Python 3 environment without a
  requirements file.

## Adapting a hook for your own environment

The four hooks here are reference implementations. If you want to
write your own:

1. Start from the hook that is closest in shape to what you need.
   `hook_scar_002_size.py` is the best starting point for any
   pattern that triggers on file extension + content threshold.
   `hook_scar_001_docx.py` is the best starting point for content-
   pattern triggers.

2. Decide on the event and matcher. The event goes in
   `settings.json` (e.g. `PreToolUse`), and the matcher restricts
   which tool invocations fire the hook (e.g. `Write|Edit`,
   `Task`, `Bash`). Be as narrow as you can — a broad matcher
   fires often and carries more risk of false positives.

3. Write the trigger detection in Python. Read the `tool_input`
   fields you care about and exit with code 0 if the trigger
   does not match.

4. Write the `additionalContext` string. This is the text the
   model will see in its context window when the hook fires.
   Make it specific: name the scar, name what to do, name where
   the scar doc lives. Avoid generalities — "be careful" is
   noise; "run the tilde fix after generating the docx" is a
   reminder.

5. Test the hook directly before installing it. Pipe a JSON
   payload representing a tool call into the hook and check that
   it produces the expected output:

   ```bash
   echo '{"tool_input": {"file_path": "foo.py", "content": "from docx import Document"}}' \
     | python hooks/hook_scar_001_docx.py
   ```

   This catches trivial bugs before the hook is wired into
   `settings.json`.

6. Wire it in, verify it fires in a real session, and log the
   first few activations. If the hook fires too often, tighten
   the trigger. If it never fires when the mistake happens, the
   trigger is too narrow.
