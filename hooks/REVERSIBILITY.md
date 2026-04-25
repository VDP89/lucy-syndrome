# Reversibility

> How to disable or roll back the hooks safely, without losing your scar files.

---

## Before installing

Always back up your `.claude/settings.json` before adding hooks:

```bash
cp .claude/settings.json .claude/settings.json.bak.$(date +%Y-%m-%d)
```

The backup is your rollback point. Keep it; do not overwrite it.

---

## Full rollback

Restore the pre-hook settings:

```bash
cp .claude/settings.json.bak.YYYY-MM-DD .claude/settings.json
```

Claude Code watches `settings.json` live. The rollback takes effect on the next tool call without restarting. The hook scripts remain in `.claude/scarring/hooks/` but are no longer invoked — they can be left as historical artifacts or deleted.

---

## Partial rollback — disable one hook

Edit `settings.json` and remove the specific hook entry. Examples:

**Remove the SessionStart hook:**
Delete the `"SessionStart"` key and its entire array.

**Remove a specific PreToolUse hook:**
In `"PreToolUse"`, find the entry whose `command` matches the hook file and delete that entry from the `hooks` array. If the array becomes empty, delete the entire matcher entry.

**Remove a UserPromptSubmit hook:**
Delete the `"UserPromptSubmit"` key and its entire array.

---

## Nuclear rollback — without touching settings.json

If `settings.json` cannot be edited for any reason, you can make hooks exit silently by emptying their files:

```bash
# On Linux/Mac:
for f in .claude/scarring/hooks/*.py; do > "$f"; done
# On Windows (Git Bash or PowerShell):
Get-ChildItem .claude/scarring/hooks/*.py | ForEach-Object { Clear-Content $_ }
```

Empty Python scripts exit immediately and produce no output. Combined with `2>/dev/null || true` in `settings.json`, they are invisible. The `settings.json` still lists them, but they do nothing.

**Not recommended** for long-term use: the next developer reading `settings.json` will not understand why the hooks are wired but inactive. Prefer a proper backup/restore.

---

## Verifying hook state

Check which hooks are currently active:

```bash
python -c "
import json
with open('.claude/settings.json', encoding='utf-8') as f:
    s = json.load(f)
hooks = s.get('hooks', {})
print('Active hook events:', list(hooks.keys()))
for event, entries in hooks.items():
    for entry in entries:
        matcher = entry.get('matcher', '(no matcher)')
        for h in entry.get('hooks', []):
            print(f'  {event} [{matcher}]: {h[\"command\"][:80]}')
"
```

---

## Hook failure modes

All hooks in this repository are designed to fail silently:

- `try/except` around stdin parsing means bad input produces exit code 0 and no output
- `2>/dev/null || true` in `settings.json` means a hook that crashes is invisible
- No hook returns `permissionDecision: deny` — none can block a tool call

The worst case from a misbehaving hook is extra context text injected into the model's context window on false positives. If you observe this, tighten the trigger condition in the hook rather than disabling it.

---

## Severity levels

Hooks in this repository are all **warn-only** by default (inject `additionalContext` only). If you escalate a hook to **blocking** (`permissionDecision: deny`), document this explicitly in the hook's docstring and in the SCARRING_INDEX — a blocking hook that fires unexpectedly causes significant operator friction.
