---
id: scar_004
name: consult_kb_first
severity: high
date_detected: 2026-04-06
date_codified: 2026-04-06
status: active
---

# scar_004 — Generating before consulting the knowledge base

## What happened (origin)

This is the **single most frequent anti-pattern** in the dataset that
became the source material for the essay accompanying this repo. It
appears across every project, every domain, every session that was
long enough to have a knowledge base to consult in the first place.
The failure mode is uniform, regardless of the specific technical
domain:

- The operator asks for a new document, analysis, or code file in a
  project that already has a knowledge base (CLAUDE.md files, project
  logs, prior versions, a style guide, normative references).
- The model generates a first pass immediately, drawing from prior
  training and from whatever prior context is already in the session.
- The first pass contradicts something in the knowledge base. A
  headcount that was already decided. A style rule that was already
  written down. A technical parameter that was already specified in
  a prior deliverable. A constraint that had already been called
  out in the project log.
- The operator catches the contradiction on review and points it out.
- The correction is absorbed into the current session, and the same
  failure mode recurs two days later in a fresh session on a
  different project.

The concrete forms vary. I have examples of this scar firing at
least eight distinct times across five separate projects over a
few weeks. The shape is always the same: **the model generates
before it looks**. And the reason is also always the same: looking
feels slower than generating, so generating wins under implicit
time pressure.

The variant that is hardest to catch is the one where the knowledge
base is a document the operator *explicitly loaded into the session*
in a previous turn, and the model then generates a response that
contradicts the loaded document a few turns later. The document was
in context, the content was accessible, and the model still wrote
from generic priors instead of checking. That is Lucy Syndrome in
its purest form: the information was available; the reflex to
consult it was not.

## Where it applies (trigger)

- Any technical task in a project with a non-trivial knowledge base:
  - A project with a `CLAUDE.md` file that encodes conventions,
    constraints, or prior decisions
  - A project with a log or `BITACORA.md` that records what was
    already decided, tried, rejected
  - A project that reads from external normative references
    (building codes, regulations, specifications, API docs with
    versioned behavior)
  - A project where prior deliverables exist and the new work must
    be consistent with them
- When the operator says "update the X document" or "generate the Y
  file" — the word "update" in particular is a strong signal that
  prior state exists and must be read before touching it.
- When the model is about to ask a clarifying question of the
  operator. The first check is: is the answer already in the
  project files?

## Why it gets forgotten (root cause)

- **Default model behavior favors generation.** Generating a response
  immediately is the default action loop. Stopping to search feels
  like a detour that delays the "real" work.
- **Unjustified confidence in general priors.** "I know how Python
  decorators work" / "I know the general shape of a civil
  engineering specification" — the general knowledge is real, but
  in a specific project the project's local conventions override
  the general knowledge, and the model does not feel the difference
  until it's been corrected.
- **Low structural friction.** Nothing in the workflow forces a
  search pass. The prompt arrives, and the prompt is what the model
  responds to.
- **Gravitational pull of the prompt.** The apparent urgency of the
  user's request inhibits preventive steps. A request that feels
  urgent pulls the model directly into generation. This is the
  same effect that produces rushed decisions in humans under time
  pressure — and in practice, the model has no actual time pressure,
  but the linguistic shape of the prompt simulates one.

## Scar (fix)

A three-stage "search first" protocol.

### Stage 1 — Before generating

For every new technical request, run a search pass **before writing
a single line of response**:

1. **Identify the project / area.** Which codebase, which domain,
   which subsystem is the request about?
2. **Consult the project knowledge base.** For each area, know where
   the authoritative files live:
   - Project-level: `CLAUDE.md`, `README.md`, style guides.
   - Log-level: project bitacoras, decision logs, ADRs.
   - Normative: external references the project binds to
     (regulations, API docs at pinned versions, tool manuals).
3. **Consult the specific project's log** if one exists. Any prior
   decision, tried approach, or explicit rejection should be
   visible to you before you start generating.
4. **If the answer is in the KB**: cite it literally with the file
   path and line reference. Do not paraphrase from memory — the
   whole point of the scar is that your memory is what got you into
   trouble.
5. **If the answer is not in the KB**: say so explicitly. "This is
   not covered in the project KB; I'm inferring from [general
   source]." Declaring the uncertainty is half of the fix.

### Stage 2 — Before asking

Before asking a clarifying question of the operator:

1. Check whether the answer might already be in the project files.
2. If it is → read it and proceed without asking.
3. If it isn't → ask, and in the question **cite explicitly** that
   you already verified the KB does not contain the answer. This
   closes the loop for the operator, who otherwise has to wonder
   whether you looked.

### Stage 3 — Before citing

Any time you are about to cite a specification, regulation,
parameter value, or technical fact:

1. Did you read the source in the current session?
2. Or are you paraphrasing from training data or from prior-session
   memory?
3. If the answer is #2: **declare it explicitly.** "This is from
   training-data memory, not verified against the KB in this
   session." The declaration is costly to ego and cheap to
   session — the ego cost is what makes it work.

## How to verify

- Every technical response should contain at least one literal
  citation from a KB file consulted during that session (path +
  line number or path + section heading).
- If the operator later corrects a technical fact that was actually
  in the KB → this is a **scar failure at full severity**. The
  correct response is to log the failure, re-read the scar, and
  sharpen the stage-1 checklist.
- End-of-session self-audit: how many times did I consult the KB
  *before* generating versus how many times did I generate first?
  The target ratio for high-severity technical tasks is 100% KB-
  first.

## Metrics

- Activations: 0 (this scar is behavioral; it has no firing hook)
- Successes: 0 (N/A)
- Recurrences after scar was installed: 0

## Notes

This is the **lever scar** of the set. It is the one with the
largest downstream effect if it works. The reason is causal: most
of the other scars are symptoms of this one. If the model
consistently consults the KB before generating, it also stops
repeating corrections that live in the KB (which is most of the
long-tail failures). If it does not, no amount of individual
symptom scars will keep up with the rate at which new symptoms
appear.

There is no enforcement hook for this scar. A PreToolUse hook
cannot verify "did the model read the KB before writing" — the
reading happens inside the model's reasoning loop, not at a tool
boundary. The enforcement is behavioral only, and it depends on
the model re-encountering the scar text often enough that the
protocol becomes a reflex rather than a rule.

The text of this scar is deliberately longer than the others. The
reason is that in practice, the scar has to compete against the
gravitational pull of the prompt at the moment of firing. A short
scar loses that competition. A long, specific scar with named
stages and explicit self-dialogue tends to win more often.
