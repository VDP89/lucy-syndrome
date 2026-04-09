---
id: scar_005
name: validate_subagent_output
severity: high
date_detected: 2026-04-06
date_codified: 2026-04-06
status: active
---

# scar_005 — A subagent can omit files without alerting

## What happened (origin)

A live case from the lab behind this repo. I dispatched an Explore
subagent to process eight project logs from my own research lab and
extract categorized findings from each. The subagent returned
findings from seven files. **It silently omitted one file** — a
373-line consolidated log that happened to be the single densest
source in the entire dataset — without any mention in its output
that the file existed, had been seen, or had been skipped. The
subagent wrote a long, well-structured synthesis of the other seven
files that read as a complete report.

I accepted the output as complete, closed the batch, and marked the
omitted file as "insufficient evidence" in the session state — a
conclusion the subagent had never actually reached, because the
subagent had never opened the file.

The omission was caught by the human operator asking one Socratic
question: *"Did you manually re-read the log for [that file]?"* I
had to admit I had not. On manual re-read, that single file
contained 26 pre-categorized cases: the single highest-density
source in the dataset, by roughly a factor of two. Had the omission
not been caught, the eventual analysis would have been missing
roughly 15% of its findings — and, more importantly, the single
strongest piece of empirical support for the framework the analysis
was building toward.

The failure mode is important to name: the subagent did not report
the file as failed, skipped, or problematic. It reported silence.
A synthesis that reads as complete over seven files looks
indistinguishable from a synthesis that reads as complete over
eight.

## Where it applies (trigger)

- Any call to the `Agent` / `Task` tool that processes a batch of
  three or more files or entities.
- Explore subagents with tasks phrased as "read these N files and
  return a synthesis" / "audit this list" / "extract findings from
  each of these documents".
- General-purpose subagents with coverage-sensitive tasks: audit,
  extraction, categorization, consolidation.

## Why it gets forgotten (root cause)

- **Subagent output looks complete.** A well-written synthesis fills
  the reader's attention. There is no structured metadata saying
  "processed X of Y inputs". The reader fills in the blank from the
  tone of the text.
- **"Task complete" is a strong attractor.** Once the top-level
  agent has a synthesis in hand, the instinct is to move forward,
  not to audit backward.
- **Length is mistaken for coverage.** A long, confident synthesis
  is not evidence that all inputs were seen. It is evidence that
  the subagent produced text. These are not the same thing.
- **No automatic coverage check.** There is no tool in the default
  Claude Code toolbox that verifies "the subagent opened every file
  in its input list". It has to be added to the prompt by the
  dispatcher.

## Scar (fix)

A three-step validation protocol.

### Step 1 — In the subagent prompt

When dispatching a subagent for any batch processing task, **always
append this instruction at the end of the prompt**:

```
BATCH COVERAGE REQUIRED: your output MUST include a final section
called "BATCH COVERAGE" that lists every input file or entity
explicitly:
- File 1: <name> — N findings extracted | "0 findings: <reason>"
- File 2: <name> — N findings extracted | "0 findings: <reason>"
- ...
If you could not process an input, declare why. Do NOT return silence
about any item in the batch.
```

This is the single most important line in the protocol. Without it,
the subagent has no structural obligation to account for every input.
With it, silence becomes impossible — a missing item in the coverage
list is visible on inspection.

### Step 2 — Coverage check in the dispatching agent

When the subagent's output arrives, **before using it**:

1. Locate the "BATCH COVERAGE" section in the output. If it is
   missing entirely, the subagent ignored the instruction — re-
   dispatch with the instruction stated more forcefully.
2. Verify that **every file in the original batch appears in the
   coverage list**. Cross-reference against the list you sent in.
3. If any file is missing from the coverage list → **red alarm**.
   Re-dispatch a fresh subagent for only that file, or read it
   manually yourself.
4. If any file appears with "0 findings" and no justification,
   re-verify manually. It may be a real empty result or a silent
   skip dressed up.

### Step 3 — Auto-check at task closure

Before declaring the batch-processing task complete:

- Is the processed-vs-input ratio 100%, or explicitly justified?
- Does any file show a result conspicuously smaller than its size
  would suggest? (A 400-line log with one finding is worth a
  manual re-read before closure.)
- Did coverage verification fire at least once? If the model jumped
  from "subagent returned" to "task done" without the verification
  step, the protocol was violated — note it and fix the next
  invocation.

## How to verify

- Processed-to-batch ratio should always be 100%, or have an
  explicit documented exclusion per file.
- If a human operator later discovers an omitted file after the task
  was marked complete, that is a **failure of this scar at maximum
  severity**. Log it, re-read the scar, sharpen the prompt template
  if the failure mode was a new one.
- Post-task audit: count the number of batch-processing tasks you
  dispatched and how many of them included the BATCH COVERAGE
  instruction. The target is 100%.

## Metrics

- Activations: 0 (the scar was installed the same day the failure
  was discovered; no activations yet as of codification)
- Successes: 0 (N/A)
- Recurrences after scar was installed: 0

## Notes

This scar is special because it was born from the lab that was
studying the Lucy Syndrome itself, in real time, while the lab was
running. The failure happened *inside* the session whose purpose was
to describe exactly this class of failure. It was caught by the human
operator asking a single Socratic question. Within minutes of
catching it, the failure was documented, the prompt template was
written, and the scar was installed — the complete
observation → friction → intervention → functional scar loop ran
inside one afternoon.

For anyone reading this repo from the accompanying essay: this case
is the clearest instance of a *meta-Lucy event* the lab produced.
It is also, not incidentally, the strongest argument that the
framework is actionable at all. If the framework could produce a
scar against a live failure of its own reasoning, it can produce
scars against less reflexive failures too.
