---
id: scar_NNN
name: short_descriptive_name
severity: high | medium | low
created: YYYY-MM-DD
status: active
---

# scar_NNN — Brief title of the mistake

## What happened (origin)

[Describe the specific failure that justifies this scar. When did it happen? What was the context? What was the cost of the mistake? What made you decide to write this scar rather than just a note?

Be concrete. A vague description produces a vague rule. The more specific you are here, the more specific the trigger and fix can be. Write this section while the incident is fresh.]

## Where it applies (trigger)

[List the specific observable conditions under which this mistake can recur:
- File types or extensions (e.g., "any .py file that imports `requests`")
- Content patterns (e.g., "any code block exceeding 200 lines")
- Task types (e.g., "any subagent dispatch processing a batch of N+ files")
- Context phrases (e.g., "any response involving external date or time references")
- Tool names (e.g., "any Write or Edit tool call on files in `src/api/`")

Be as narrow as possible. A broad trigger fires too often and produces noise.]

## Why it gets forgotten (root cause)

[Explain the mechanism that causes this mistake to repeat despite being documented. Common mechanisms:
- Friction too low: nothing in the system forces the check
- Rule too vague: cannot be evaluated mechanically without judgment
- Trigger too slow: the reminder arrives after the key decision is made
- Confirmation bias: the model assumes it already knows the right answer
- "Already written" bias: the output looks complete before the check runs

Understanding the mechanism is what allows you to design a fix that actually intercepts it.]

## Scar (fix)

[The concrete action to execute when the trigger fires. Structure this as a numbered protocol or a single clear rule, not as general advice.

If you have a hook, describe what it injects and what the operator should do when it fires.

If the fix is behavioral only, write it as an explicit checklist: steps the model can execute mechanically without judgment.

A good fix: "Run `grep -n 'except.*pass' <file>` and fix any silent exception handlers before delivering."
A bad fix: "Be more careful with error handling."]

## How to verify

[Describe the observable artifact that proves the scar was applied:
- A printed block in the output (e.g., the self-review report)
- A grep that returns zero matches (e.g., no silent handlers)
- A file created or modified (e.g., the post-processed output)

If the scar was applied and you cannot point to anything concrete it left behind, the verification step is missing.]

## Metrics

- Activations: 0
- Success: 0 (N/A)
- Last applied: never
- Post-scar recurrences: 0
- Notes: [any context about specific failures or refinements]
