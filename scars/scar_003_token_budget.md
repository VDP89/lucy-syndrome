---
id: scar_003
name: token_budget
severity: medium
date_detected: 2026-03-31
date_codified: 2026-04-06
status: active
---

# scar_003 — Token budget drained by inattention

## What happened (origin)

Exhausted a paid Claude Code plan mid-month because three corrective
habits exist in the team's documentation but were not being applied
systematically in-session:

1. `/clear` between tasks that do not share context
2. Chrome MCP left enabled on sessions that never touch a browser
3. Subagents defaulting to Sonnet/Opus for tasks that would run fine
   on Haiku

Each habit is cheap individually. Together they shift monthly token
consumption by a multiple that turns into real dollars when a single
session on a frontier model is 30-50k tokens of low-value context
overhead.

## Where it applies (trigger)

- Starting a new task that does not share context with the previous
  task in the same session.
- When the current session's context has grown past ~120k tokens.
- When about to dispatch a subagent (Explore, general-purpose) for a
  task that is clearly mechanical (read N files, return a list).
- Before beginning work that does not require a browser at all
  (pure code, document generation, calculation, writing).

## Why it gets forgotten (root cause)

- **Token consumption is invisible in real time.** The model cannot
  see its own context size. The operator can see it only if they
  check the CLI's indicator, which nobody does between every turn.
- **`/clear` is a user action, not a model action.** The model can
  recommend it, but cannot execute it. This means the scar depends
  on a recommendation firing at the right moment — which is exactly
  the kind of signal Lucy Syndrome erases.
- **MCP servers are configured out-of-band.** Enabling or disabling
  Chrome MCP requires touching a settings file or restarting the
  session. The friction is medium, and the cost is invisible until
  the bill arrives.
- **Subagent model selection is a per-call decision.** It is easy to
  default to the "strong" model without thinking, because the
  "strong" model has never produced a wrong answer.

## Scar (fix)

Three proactive behaviors. None of these are enforced by a hook in
this repo because they are either user actions (`/clear`),
configuration actions (disabling MCP), or model-side judgment
(Haiku vs Sonnet). The scar is behavioral: the model must be
primed to recommend them at the right trigger.

### Behavior 1 — Recommend `/clear` on task context breaks

When a new user request arrives that does not share context with the
previous one, the model should recommend `/clear` explicitly:

> "This task is independent of the previous one. I recommend
> running `/clear` before starting so the previous context is
> released."

The recommendation should be visible, not buried in parenthesis. The
goal is to give the operator a clean decision point every time the
session changes topic.

### Behavior 2 — Flag unused MCPs at task start

When the toolset includes an MCP that will not be used for the
current task (e.g. a browser MCP on a pure-code task, a database
MCP on a documentation task), the model should flag it:

> "This task does not require a browser. Consider disabling Chrome
> MCP to free context space."

This is particularly valuable for long sessions where the MCP tool
definitions alone can occupy several thousand tokens of context.

### Behavior 3 — Default to the smallest capable subagent model

Before dispatching a subagent, evaluate the task:

- **Mechanical: read N files and return a synthesis** → default to
  Haiku. Escalate only if output is insufficient.
- **Judgment: code review, design decisions, complex reasoning** →
  Sonnet or Opus.
- **When in doubt**, start with Haiku and escalate. The cost of a
  failed Haiku call is one retry; the cost of a gratuitous Opus
  call is ~10x tokens for the same result.

## How to verify

- At the end of a long session, check whether the recommendation of
  `/clear` was made at least once when the topic changed.
- Look at the session's subagent dispatch log: the ratio of Haiku to
  Sonnet should reflect the real distribution of task complexity,
  not a reflex default.
- If the billing report shows an unexpectedly high month, that is
  this scar failing. Review which of the three behaviors was missing.

## Metrics

- Activations: 0
- Successes: 0 (N/A; this scar is measured as a rate of
  recommendation, not a blocking action)
- Recurrences after scar was installed: 0

## Notes

This scar has a structural limitation: most of its corrective actions
have to be taken by the operator, not the model. The model's role is
to **recommend at the right moment**, not to enforce. The success
metric is "timely recommendation rate", not "applied rate". That
distinction matters when evaluating whether this scar is working —
a failure is the model going silent when it should have spoken, not
the operator choosing not to act.

There is no hook script for this scar. Enforcement at the harness
level would require observing context size over time, which is not
something a PreToolUse hook has access to.
