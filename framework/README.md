# Framework Guide

> How the Lucy Syndrome scarring system works, from theory to wired hook.

---

## The core loop

```
Mistake happens
       ↓
Write a scar (what/where/why/fix/verify/metrics)
       ↓
Install a hook that fires when the trigger condition is met
       ↓
Hook injects reminder context at the moment of risk
       ↓
Model applies the fix before the mistake occurs
       ↓
Log the activation. If it failed, sharpen the rule.
```

This is the entire framework. Everything else — the templates, the `settings.json` wiring, the SCARRING_INDEX — is scaffolding around this loop.

---

## Files in this directory

| File | Purpose |
|---|---|
| `scar_template.md` | Blank scar to copy and fill in |
| `hook_template.py` | Blank Python hook to copy and customize |
| `settings.json.example` | Claude Code hook wiring example |

---

## When to write a scar

**Do not write scars preemptively.** A scar written against a hypothetical failure has no weight — nothing in the model's reasoning will remember it at the moment of temptation. The failure is what creates the scar.

Write a scar when:

1. The same mistake has occurred at least twice, despite being documented
2. A single very costly mistake occurred that you cannot afford to repeat
3. A feedback note or preference has been added to memory more than once and still keeps getting violated

The threshold is exactly the one that defines Lucy Syndrome: the correction exists in writing, and the system ignores it anyway. That is when a behavioral memory entry becomes a scar.

---

## The six required sections

Every scar has these six sections. All are load-bearing:

**1. What happened (origin)**
The specific failure that justified this scar. Write it while the details are fresh. This section is the reason the scar has teeth: a rule without a concrete origin feels like advice; a rule that recalls a specific incident recalls the cost of the mistake. Do not summarize; describe.

**2. Where it applies (trigger)**
The observable conditions under which the mistake can recur: file extensions, content patterns, task types, phrases in prompts, tool names. The narrower you write this, the better — a scar whose trigger is "anytime you write code" is not a scar. A scar whose trigger is "any Python file exceeding 200 lines that will be executed by the operator" is a scar.

**3. Why it gets forgotten (root cause)**
The mechanism that causes the mistake to repeat despite the correction being documented. Common root causes: friction is too low (nothing forces the check), rule is too vague (cannot be evaluated mechanically), trigger is too slow (the reminder arrives after the decision), confirmation bias (the model assumes it already knows).

**4. Scar (fix)**
The concrete action — either automated via hook or procedural via protocol — that the operator/model executes when the trigger fires. The fix must be cheap enough to perform every time the trigger fires. If executing the fix costs more than skipping it, it will be skipped.

**5. How to verify**
The observable artifact that proves the scar was applied: a log block printed, a file created, a grep that returns zero matches. If you cannot point to something concrete that the scar leaves behind, you cannot audit whether it ran.

**6. Metrics**
- Activations: how many times the trigger fired
- Success: how many times the error was prevented
- Last applied: date
- Post-scar recurrences: how many times the error occurred anyway

These numbers exist to refine the rule, not to report success.

---

## The five persistence invariants

Based on the production dataset (163 findings, 17 source files), the research identifies five properties that distinguish corrections that persist from those that decay:

| Invariant | What it means | Escape rate without it |
|---|---|---|
| Binary rule | Expressible as a concrete check, not a judgment | >75% |
| Durable physical support | Lives in a file loaded every session | ~100% (verbal only) |
| Structural integration | Wired into the output, not a note | >50% |
| Non-passive technical trigger | Hook fires at moment of risk | Varies |
| Refinable metric | Tracks success/failure | Cannot improve |

A scar that satisfies all five has a measured escape rate below 10% in the dataset. A verbal correction with no physical support has an escape rate of 100%.

---

## Hook design principles

1. **Silent exit on non-matching invocations.** A hook wired to `PreToolUse Write|Edit` fires on every file write. The vast majority are irrelevant — the hook must exit silently (code 0, no output) for all of them, and emit JSON only when the actual trigger fires.

2. **Silent exit on malformed input.** Wrap stdin parsing in `try/except`. A hook that crashes on unexpected input breaks tool calls. Combined with `2>/dev/null || true` in `settings.json`, a broken hook should be invisible.

3. **Warn-only by default.** Return `additionalContext` and `systemMessage` — do not return `permissionDecision: deny` unless the mistake is genuinely catastrophic. A blocking hook interrupts flow; resentment gets hooks disabled.

4. **Small and dependency-free.** Each hook should be under 100 lines of standard-library Python. No `requirements.txt`. No network calls. Invocation must complete in milliseconds.

5. **Test before wiring.** Pipe a representative JSON payload into the hook from the command line before installing it:
   ```bash
   echo '{"tool_input": {"file_path": "foo.py", "content": "..."}}' | python hook_template.py
   ```
   A hook that works in isolation works in the harness.

---

## Wiring hooks into Claude Code

Claude Code reads hook configuration from `.claude/settings.json`. The relevant structure:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \".claude/scarring/hooks/hook_session_start.py\" 2>/dev/null || true"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \".claude/scarring/hooks/hook_example_review.py\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

Claude Code watches `settings.json` live. Changes take effect on the next tool call without restarting. See `settings.json.example` in this directory for the full example.

---

## Growing the system

Start with one scar. Wire one hook. Watch it fire. Then add the next scar only after you have a real mistake to record.

The production case in `examples/production-case/` grew from 5 scars to 11 over the course of five months of operation, each scar born from a real failure. The system scales naturally because each scar is self-contained — adding a new one does not require modifying the others.
