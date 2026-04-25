---
id: scar_example_003
name: check_context_before_generating
severity: high
created: 2026-04-25
status: example
---

# scar_example_003 — Generating before consulting the knowledge base

> **Example scar.** This file is a domain-independent template derived from the production case.
> Adapt the trigger, fix, and metrics to your own environment.
> The originating incidents are documented in `examples/production-case/scars/scar_004_consult_kb_first.md`.

---

## What happened (origin)

The most frequent anti-pattern in the 163-finding dataset: the model generates a response before consulting the project's knowledge base. Documented in 8+ metacognitive friction events (D), 6 false confidence events (C), and 4 repeated errors (A) in a single production environment.

Representative failures:
- A staffing table was generated with 33 people when the project brief already in the knowledge base specified 25
- A document was generated in "greenfield" tone when the project brief explicitly specified "brownfield renovation" — the brief was a loaded file, not read
- Three clarifying questions were asked about project parameters that were all answered in existing files, visible in the same session

The failure is not about missing information. The information was present. The failure is the model generating *before* looking.

**The research names this the "gravitational pull" effect**: the apparent urgency of the user's request creates pressure to respond immediately, and that pressure overrides the preventive step of reading first. The pull is stronger when the model has general knowledge about the domain — it substitutes confident general knowledge for the specific ground truth in the files.

## Where it applies (trigger)

- Before generating any document, code, or technical response in a domain with a project knowledge base (KB)
- When the operator uses phrases like "update the X", "generate a Y", "what does Z say"
- When the response will make claims about project-specific state: staffing numbers, specifications, standards, decisions, constraints
- Before asking a clarifying question — check whether the answer is already in project files first

## Why it gets forgotten (root cause)

- **Generating immediately feels more useful** than pausing to search. The model's default is to produce output.
- **Overconfidence in general domain knowledge**: "I know about civil engineering / software architecture / tax law" becomes a substitute for reading the specific documents the operator maintains
- **Low friction**: nothing in the default workflow forces a search before generation
- **Urgency signal from prompt**: imperative prompts ("generate", "update", "write") create pressure to act without the preventive step
- **Index is not content**: reading a file index or a memory summary creates the *feeling* of having read the files without actually having done so. This is the subtlest form of the failure — compliance in form, non-compliance in function.

## Scar (fix)

**"Search first" protocol in three stages:**

### Stage 1 — Before generating

For any technical request in a domain with a KB:

1. Identify the relevant area of the KB (domain, project, topic)
2. Read the key files — not their index entries or one-line summaries, the actual files
3. If the answer is in the KB: cite it literally with file path and line. Do not paraphrase from memory.
4. If the answer is NOT in the KB: declare this explicitly before generating: "This is not in the KB for area X; I am inferring from [source]. Confidence: [level]."

**Critical distinction**: reading a file index (e.g., `MEMORY.md`, a table of contents, a README listing files) is NOT the same as reading the files. An index entry is a pointer. If the task requires the content, read the content.

### Stage 2 — Before asking a clarifying question

Before asking the operator for information:
1. Check whether the answer could be in existing project files
2. If yes: read the files, proceed without asking
3. If no: ask, but cite explicitly that you already checked ("I've read X and Y — this is not covered there")

### Stage 3 — Before citing a fact

Before including a domain-specific fact, number, or specification:
1. Was this read from a file in this session?
2. Or is it from training data / memory without a session-level read?
3. If (2): flag it explicitly: "From training data, not verified against project KB"

## How to verify

- Every technical response contains at least one citation to a file that was actually read in this session
- If the operator corrects a fact that was present in the KB → scar failure; log it and review which stage failed
- Self-check at end of each technical session: how many times was the KB consulted before generating vs. after?

## Metrics

- Activations: 0
- Success: 0 (N/A — adapt to your own environment)
- Last applied: never
- Post-scar recurrences: 0
- Notes: A `UserPromptSubmit` hook that detects project keywords in the prompt and reminds the model to read relevant KB files before generating is the strongest technical enforcement for this scar. See `examples/production-case/hooks/hook_scar_004_expand.py` for a production-ready implementation (~240 lines, standard library only).
