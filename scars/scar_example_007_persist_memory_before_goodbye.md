---
id: scar_example_007
name: persist_memory_before_goodbye
severity: high
created: 2026-04-26
status: example
---

# scar_example_007 — Session-end discoveries lost because memory was not updated before signoff

> **Example scar.** This file is a domain-independent template derived from the production case.
> Adapt the trigger, fix, and metrics to your own environment.
> The originating incident is documented in `examples/production-case/scars/scar_007_memory_update_session_close.md`.

---

## What happened (origin)

A live session in which the agent had:

- reorganized a substantial body of scheduled work (≈19 calendar operations)
- discovered a previously-unknown duplicate calendar that was the actual source of authority for a recurring channel
- updated the public status of an in-flight project across several platforms

…ended without the agent updating any persistent memory. The operator had to ask, after the goodbye message had been drafted, "did you save the memories?". Five memory updates were pending (two new files plus three edits to existing ones) that the agent had been planning to do "at the end" — and nearly didn't.

The shape of the failure: when the operator signals "we're done", the agent shifts into wrap-up mode. Wrap-up mode prioritizes a clean summary of **what was accomplished** over a transfer of **what should persist**. The two are not the same. Anything in active context but not yet written to a memory file is one session away from being lost — and "the next session" is exactly when that information would be needed.

If the operator had not asked, the next session would have repeated a discovered error (looking only at the wrong calendar), would have lacked the context of the reorganization, and would have been starting from a strictly worse position than this session ended in.

## Where it applies (trigger)

- Any session-closing signal from the operator: "we're done", "let's wrap", "that's it for today", "ttyl", "see you tomorrow", or the equivalent in any language
- Sessions in which something was discovered about the environment, tools, or workflow that future sessions will need
- Sessions in which decisions were made that affect work outside this session
- Sessions in which the state of an in-flight project changed (status, milestone, blocking issue resolved, new constraint surfaced)
- Sessions in which the operator corrected the agent on an approach that was not obviously wrong

## Why it gets forgotten (root cause)

- **Wrap-up mode rewards quick goodbyes.** A long final message feels like overrunning; a short one feels polite. Memory updates make the close longer.
- **The summary describes accomplishments, not transfers.** The summary template the agent reaches for lists what was *done*, not what should *persist*. These are different surfaces and only the second one survives the session.
- **In-context information feels saved.** Anything currently in the working context feels durable in the moment. It is not — it dies with the session.
- **No automatic trigger.** Nothing forces a memory review at session close. The only mechanism is the agent remembering to run it.

## Scar (fix)

**Three-step protocol every time the operator signals close.**

### Step 1 — Detect the closing signal

Before producing the goodbye message, treat any of the following (or the operator's equivalent) as a close-trigger and pause:

- "we're done" / "we're good" / "let's wrap" / "that's it"
- "ttyl" / "see you" / "talk tomorrow" / "ciao"
- Any signoff that is clearly terminal rather than a pause

### Step 2 — Internal memory checklist

Before responding, walk through these questions:

1. Did I learn something about the environment, tools, or workflow that a future session will need? → **reference** memory
2. Did I make an error here that I should not repeat? → **feedback** memory
3. Did the state of an in-flight project change? → **project** memory update
4. Did the operator correct or confirm an approach in a way that is not obvious? → **feedback** memory
5. Were there decisions taken that affect work in subsequent sessions? → **project** or **feedback** memory

If any answer is yes, list the specific files to write or update.

### Step 3 — Persist BEFORE the goodbye message

Write the memory updates first, then send the wrap-up message. Include in the wrap-up a one-line confirmation: "Memory updates: [files written / updated]". This makes the persistence step visible and auditable.

If the operator has to ask "did you save the memories?", the protocol failed at step 1 or step 2.

## How to verify

- If the operator asks "did you save the memories?" after a goodbye message — log a scar failure. The detection step was missed.
- If the next session repeats an error that this session discovered — log a critical failure. Persistence was either skipped or done incorrectly.
- Auto-check: does the wrap-up message contain a "Memory updates:" line? Sessions where that line is absent should be either trivial (no discoveries) or scar failures.

## Metrics

- Activations: 0
- Success: 0 (N/A — adapt to your own environment)
- Last applied: never
- Post-scar recurrences: 0
- Notes: Memory persistence is the only mechanism for cross-session continuity. The cost of saving is small (2-5 minutes); the cost of not saving is large (repeating known errors, losing earned context, wasting the operator's next-session time on rediscovery). A `Stop` hook (Claude Code's session-end hook event) that injects a memory-checklist reminder before the agent produces its final output would convert this from a behavioral protocol into an enforced one.
