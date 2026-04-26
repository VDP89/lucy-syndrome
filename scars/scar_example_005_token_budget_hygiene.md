---
id: scar_example_005
name: token_budget_hygiene
severity: medium
created: 2026-04-26
status: example
---

# scar_example_005 — Context window and token plan exhausted by neglect

> **Example scar.** This file is a domain-independent template derived from the production case.
> Adapt the trigger, fix, and metrics to your own environment.
> The originating incident is documented in `examples/production-case/scars/scar_003_token_budget.md`.

---

## What happened (origin)

A monthly Claude Code plan was exhausted halfway through the billing period, despite operational rules in place to keep usage efficient. The rules existed in writing; nothing forced their application:

- `/clear` was rarely run between unrelated tasks, so unrelated context accumulated across the entire session
- Heavyweight MCP servers (in this case a browser-control MCP) stayed loaded for tasks that did not require them, consuming context
- Subagents dispatched via `Task` defaulted to the most capable model regardless of whether the work demanded it

The shape of the failure: token consumption is **invisible during the session**. There is no live meter the model can read. Token-saving fixes mostly require operator action (`/clear` is a user command, MCP toggles live in `settings.json`), so the agent's only lever is to **proactively recommend** them at the right moment. Without that prompt, the operator forgets, the session bloats, and the bill arrives early.

## Where it applies (trigger)

- Start of a new task that does not share context with the previous one (different project, different domain, different tool surface)
- Mid-session when accumulated context exceeds roughly the soft limit for your model (e.g. ~120K tokens for many Claude Code setups)
- Before dispatching a subagent for work that is plausibly handleable by a smaller / cheaper model
- Start of any task that clearly does not need a particular MCP server currently loaded (e.g. browser-control MCP active for a pure-code task)

## Why it gets forgotten (root cause)

- **No live signal.** Token consumption has no in-band indicator visible to the agent during normal turns. The cost only becomes visible at the bill.
- **The fixes are not the agent's to execute.** `/clear` is an operator command. MCP toggles require editing settings or restarting the session. The agent can only recommend.
- **Cheap default for subagents.** When dispatching a `Task`, the path of least resistance is to pass no `model` argument and inherit the parent's model. That defaults complex models for trivial work.
- **Compound effect.** Each individual neglect is small. Twenty of them across a week consume the plan.

## Scar (fix)

**Three proactive recommendations the agent must make at the right moments:**

### Recommendation 1 — `/clear` between unrelated tasks

When the operator's new prompt is clearly disjoint from the previous task (different project, different domain, no shared files or entities), include a one-line recommendation **before** starting:

> "This task is independent of the previous one. Consider running `/clear` first to free context."

Apply once, do not repeat within the same task.

### Recommendation 2 — flag unnecessarily-loaded MCPs

At the start of any task whose tool needs are obviously narrow (offline code, pure analysis, document drafting with no web research), if the toolset includes heavyweight MCP servers that will not be used (browser-control, large databases, etc.), mention it once:

> "This task does not need the [name] MCP. Consider disabling it for this session to free context."

Same rule: once per task, not repeated.

### Recommendation 3 — default subagents to a smaller model when the work allows

Before invoking the `Task` tool, evaluate the prompt:

- **Read N files and return a synthesis or extraction** with no judgment calls → pass `model: haiku` (or your provider's smallest viable model)
- **Code review, design decisions, multi-step reasoning, ambiguity resolution** → `model: sonnet` or larger is justified
- **Unsure** → start with the smaller model. If the output is insufficient, escalate explicitly. Don't pre-escalate.

Document the choice in one short line in the dispatch reasoning so the operator can audit the ratio later.

## How to verify

- At the end of a long session, count whether `/clear` was recommended at least once when the task changed. Zero recommendations across multiple task changes → scar failure.
- Sample subagent dispatches: the `model` chosen should reflect actual complexity, not be uniformly `sonnet`/`opus`.
- If the operator reports plan exhaustion mid-month → log as scar failure and review the session logs for missed recommendations.

## Metrics

- Activations: 0
- Success: 0 (N/A — adapt to your own environment)
- Last applied: never
- Post-scar recurrences: 0
- Notes: This scar has a structural limitation. The fixes are operator actions, not agent actions. The success metric should be *recommendation rate* (did the agent flag the moment correctly?), not *application rate* (did the operator actually run `/clear`?). A behavioral scar without a hook; a `UserPromptSubmit` hook that detects task-boundary signals could strengthen Recommendation 1.
