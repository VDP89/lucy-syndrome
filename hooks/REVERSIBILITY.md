# Reversibility — Lucy Syndrome hooks

> How to disable or roll back the functional-scar hooks if they generate
> noise, interfere with a workflow, or you simply want to try them for a
> session and then remove them.

## Design guarantee

All four hooks in this repo are **warn-only**. None of them return a
`permissionDecision: deny` or block a tool call. The worst-case behavior
of a hook is that it injects extra text into the model's context window.
You will never see a hook prevent a Write, Edit, or Task from executing.

Every command invocation in `settings.json.example` also ends with
`2>/dev/null || true`. This means that if a hook script is missing,
moved, or throws a Python exception, the tool call proceeds normally
and the failure is silent. **You cannot break your Claude Code session
by deleting a hook file.**

## Full rollback

Before adding the hooks, back up your existing `settings.json`:

```bash
cp .claude/settings.json .claude/settings.json.bak.$(date +%Y-%m-%d)
```

To fully remove the hooks:

1. Edit `.claude/settings.json` and delete the `SessionStart` block, the
   `PreToolUse` entries that reference `hook_scar_*`, or the entire
   `hooks` key if you have nothing else in it.
2. Save the file. Claude Code watches `settings.json` live — the change
   takes effect on the next tool call without a restart.
3. Optionally delete `./hooks/*.py`. This is not required; orphaned
   hook scripts have no effect if nothing in `settings.json` invokes
   them.

## Partial rollback — disable a single hook

To disable a single scar without removing the others, edit
`settings.json` and remove the specific `{ "type": "command", ... }`
entry that references the hook you want to disable. For example, to
disable only scar_001 while keeping scar_002 and scar_005 active:

```json
"PreToolUse": [
  {
    "matcher": "Write|Edit",
    "hooks": [
      {
        "type": "command",
        "command": "python \"./hooks/hook_scar_002_size.py\" 2>/dev/null || true"
      }
    ]
  },
  {
    "matcher": "Task",
    "hooks": [
      {
        "type": "command",
        "command": "python \"./hooks/hook_scar_005_subagent.py\" 2>/dev/null || true"
      }
    ]
  }
]
```

## Verification

After removing or adjusting hooks, you can confirm the current hook
state with a small Python check:

```bash
python -c "
import json
with open('.claude/settings.json', encoding='utf-8') as f:
    s = json.load(f)
print('active hook events:', list(s.get('hooks', {}).keys()))
for event, entries in s.get('hooks', {}).items():
    for entry in entries:
        for h in entry.get('hooks', []):
            print(f'  {event} [{entry.get(\"matcher\", \"*\")}]:', h.get('command', '')[:80])
"
```

## Notes

- **Append-only backups.** Never overwrite a `.bak` file. If you need
  another backup, create `settings.json.bak.YYYY-MM-DD-N`.
- **The live reloader.** Claude Code's harness watches `settings.json`
  and applies changes on the next tool call. A rollback takes effect
  immediately; you do not need to restart the CLI.
- **Testing a hook once.** To verify a hook fires without running a real
  tool call, you can invoke it directly with an empty JSON input:

  ```bash
  echo '{}' | python hooks/hook_session_start.py
  ```

  The hook prints its JSON response to stdout. This is useful when
  adapting a hook to your own environment and wanting to confirm the
  additionalContext string before installing it.
