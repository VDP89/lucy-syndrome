---
id: scar_example_004
name: validate_subagent_output
severity: high
created: 2026-04-26
status: example
---

# scar_example_004 — Subagent silently dropped a file from a batch

> **Example scar.** This file is a domain-independent template derived from the production case.
> Adapt the trigger, fix, and metrics to your own environment.
> The originating incident is documented in `examples/production-case/scars/scar_005_validate_subagent_output.md`.

---

## What happened (origin)

A general-purpose subagent was dispatched via the `Task` tool to process a batch of eight source files and return categorized findings. The subagent returned findings from seven files. **It omitted the eighth file entirely** — not as an "I could not process this" line, but as silence: the omitted file simply was not mentioned in the output. The agent that received the output assumed full coverage and closed the task as complete.

The operator caught it by asking, almost in passing, "did you actually re-read file eight?". The honest answer was no. A manual re-read of the omitted file revealed it contained the **highest density of relevant content of any file in the batch** — roughly twice the average. Without that question, ~15% of the dataset would have been silently lost, and the conclusions drawn from the partial data would have looked solid.

The shape of the failure: subagent output is unstructured text. There is no machine-readable manifest of "files processed: 8 / 8". The output reads as complete because the missing file is simply not there to flag its absence. A long, well-written synthesis from a subagent **creates the illusion of full coverage**.

This is a Lucy-Syndrome-shaped failure that lives one layer up from a single agent: it is not the model forgetting a correction across sessions, but a parent agent failing to verify a child agent's coverage **within the same task**. The mechanism is the same — confidence without calibration — applied to a different boundary.

## Where it applies (trigger)

- Any `Task` tool dispatch that hands the subagent a batch of **three or more** files, records, or entities to process
- Any subagent prompt of the shape "read these N files and return a synthesis / extraction / categorization"
- Any audit, coverage, or extraction task that delegates to a subagent
- Any orchestration step that consumes a subagent's output and treats it as authoritative without a structural coverage check

## Why it gets forgotten (root cause)

- Subagent output is **prose, not data**. There is no required field that says "I covered files X, Y, Z; I did not cover Q because R."
- The "task done" reflex inhibits post-hoc verification. By the time the subagent returns, the parent agent's attention has shifted to the next step.
- Long, well-written synthesis is itself a confidence signal — the brain reads "this is thorough" and stops checking.
- There is no built-in coverage-validation tool for subagents. The check has to be designed in by the prompt and enforced by the parent.

## Scar (fix)

**Three-step protocol every time a subagent is dispatched on a batch:**

### Step 1 — Coverage clause in the subagent prompt

Append this clause to every batch dispatch:

```
COVERAGE REQUIRED: your output MUST end with a section titled
"BATCH COVERAGE" that lists every input file explicitly:

  - <file_1> — N items extracted | "0 items: <explicit reason>"
  - <file_2> — N items extracted | "0 items: <explicit reason>"
  - ...

Every file from the input list must appear. If a file was not
processed, declare why. Silence about a file in the input is
not acceptable.
```

The clause shifts the failure mode from invisible (silence) to visible (a missing line in a structured section).

### Step 2 — Coverage validation in the parent agent

When the subagent's output arrives, **before consuming it**:

1. Find the `BATCH COVERAGE` section in the output.
2. Verify that **every file from the original input list appears** in the coverage section.
3. If any input file is missing from coverage → re-dispatch the subagent for that single file, or read the file directly. Do not paper over the gap.
4. If a file appears with `0 items` and the justification is vague (e.g. "nothing relevant found") → re-verify by hand. A "no findings" claim deserves the same skepticism as a positive claim.

### Step 3 — Pre-completion self-check

Before declaring the parent task complete:

- Were all input files processed or explicitly justified?
- Does any file have a count that is suspiciously low relative to its size?
- Is total coverage 100%, or is there a delta the parent has not addressed?

## How to verify

- **Files-processed / files-in-batch ratio** must be exactly 1.0 (or have an explicit, line-by-line exclusion justification).
- If the operator surfaces an omitted file after the parent declared "complete" → log as a top-priority scar failure. The miss bypassed Step 2.
- Audit pattern: count the dispatches in a session that returned without a `BATCH COVERAGE` section. That number is the scar's leak rate.

## Metrics

- Activations: 0
- Success: 0 (N/A — adapt to your own environment)
- Last applied: never
- Post-scar recurrences: 0
- Notes: A reference implementation of the hook side lives at `../examples/production-case/hooks/hook_scar_005_subagent.py` — it injects a `PreToolUse Task` reminder that the dispatch must include the coverage clause. The hook does not itself parse the subagent's output; the parent agent still has to perform Step 2.
