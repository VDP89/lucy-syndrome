---
id: scar_example_001
name: review_before_deliver
severity: high
created: 2026-04-25
status: example
---

# scar_example_001 — Code delivered without source-level review

> **Example scar.** This file is a domain-independent template derived from the production case.
> Adapt the trigger, fix, and metrics to your own environment.
> The originating incident is documented in `examples/production-case/scars/scar_002_code_review_absent.md`.

---

## What happened (origin)

An audit of a production Claude Code operation found that 100% of generated code was being executed without source-level review by the operator. The operator checked functionality only — did the output look right? — not the code itself.

Over several months, this allowed a set of anti-patterns to accumulate undetected:
- Silent exception handlers (`except: pass`) masking errors
- Spread operators on arrays that could grow beyond safe size limits
- f-string templates with mismatched placeholder types
- Hardcoded absolute paths that broke across environments

The failure mode is not that any single bug was catastrophic. The failure mode is that bugs compound invisibly, and the model has no mechanism to flag "I should double-check this" — because from the model's perspective, output is always complete.

**Root of the pattern** is identified in the research as "confidence without calibration": the model generates with the same assurance regardless of whether the code has been validated or not.

## Where it applies (trigger)

- Any generated code file exceeding ~200 lines that is about to be delivered to the operator for execution
- Generator scripts (files whose names contain `generate_`, `_generator`, `_writer`)
- Data processing scripts (parsers, converters, batch processors, migration scripts)
- Any modification to existing code exceeding ~50 lines changed in a single edit

## Why it gets forgotten (root cause)

- **No enforced gate**: nothing in the workflow prevents delivering unreviewed code. The review is optional.
- **"Already written" bias**: once the code is generated, it feels done. The mental effort of generation is mistaken for the work of verification.
- **Speed-quality tradeoff**: reviewing 300 lines of code takes 5–15 minutes. Under time pressure, this step gets compressed or skipped.
- **Self-referential confidence**: the model has no mechanism to doubt its own output. It treats its own generated code the same way it treats external reference code — as potentially valid.

## Scar (fix)

**3-step self-review before marking any code "ready to execute":**

### Step 1 — Random read

Pick 5 functions or sections at random and read them in full, checking specifically for:
- Silent exception handlers: `except: pass`, `except Exception: pass`, `catch {}`, `catch (_) {}`
- Spread operators on potentially large arrays: `Math.min(...arr)`, `[...bigArray]` without size guard
- f-string or template string mismatches: `f"...{js_var}..."` with wrong-language placeholders
- Hardcoded absolute paths without environment variables or config
- Unused imports or debug code left from development (`console.log`, `print("DEBUG")`)

### Step 2 — Contract check

For each public function:
1. Does the caller pass arguments in the order the function expects?
2. Are the types compatible (string where int expected, list where scalar expected)?
3. Does the return value match what callers assume?

### Step 3 — Review report

Before delivering, write this block explicitly in the response:

```
SELF-REVIEW scar_001:
- Functions reviewed: [list 5+ function names]
- Anti-patterns found: [list, or "none"]
- Anti-patterns fixed: [list, or "none"]
- Confidence: high | medium | low
```

The review block is the verification artifact. Its presence confirms the step ran. Its absence is a failure.

## How to verify

- The review block appears in the response before the code is delivered
- If the operator reports a bug matching one of the anti-pattern categories → log as scar failure, sharpen the checklist
- Audit: count how many deliveries included the review block vs. how many skipped it

## Metrics

- Activations: 0
- Success: 0 (N/A — adapt to your own environment)
- Last applied: never
- Post-scar recurrences: 0
- Notes: A `PreToolUse Write|Edit` hook fires when a code file exceeds the line threshold. See `../hooks/hook_example_review.py`.
