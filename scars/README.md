# Scars

> A scar is a short document that records a mistake you already made
> once, and the specific operational rule you now apply so the same
> mistake cannot repeat silently.

Each file in this directory is one scar. They all follow the same
structure, and each one stands alone — you do not need to read them
in order, and you do not need to read all of them to adopt any one
of them.

## What a scar is

A scar is **not** a best practice, a style guide, or a checklist of
hygiene tips. Those things are cheap to write and easy to ignore,
and they tend to accumulate faster than they get read.

A scar is narrower and more expensive. It has three properties:

1. **It is born from a real failure.** Every scar in this
   directory exists because the corresponding mistake actually
   happened, in production, and it cost something to recover from.
   The origin section of each file describes what that failure
   looked like.
2. **It has a trigger you can check for.** The scar names the
   specific context where the mistake can recur: a file extension,
   a library import, a kind of task, a phrase in a prompt. This is
   what makes it enforceable — either the trigger fires and the
   scar applies, or it doesn't.
3. **It has a fix that can be executed in the moment.** Not
   "think more carefully", not "remember to check"; a concrete
   action that either runs automatically (via a hook) or that the
   operator performs mechanically when the trigger fires.

The motivation, the theory, and the naming of the pattern live in
the essay [*The Lucy Syndrome and AI*](https://victordelpuerto.com/posts/lucy-syndrome/).
This directory is the applied side.

## How to read a scar file

Every file in this directory has the same sections, in order:

- **YAML frontmatter** — `id`, `name`, `severity`, dates, `status`.
- **What happened (origin)** — the failure that justified the scar.
  Read this first. If the failure does not look like something your
  environment could produce, the scar probably does not apply to
  you.
- **Where it applies (trigger)** — the concrete context where the
  scar fires. If you want to adopt the scar, this is the section
  you translate into your own trigger (file paths, extensions, task
  shapes).
- **Why it gets forgotten (root cause)** — a brief explanation of
  the mechanism that causes the mistake to repeat. This matters
  because scars only work against mechanisms you understand; a scar
  against a mechanism you haven't named will get overridden by the
  mechanism.
- **Scar (fix)** — the actual rule, in executable form. If the
  scar has a hook, this section describes what the hook does and
  what it reminds the operator of. If the scar is behavioral only,
  this section describes the protocol the operator follows when
  the trigger fires.
- **How to verify** — how you know the scar is working, and what
  a failure of the scar looks like.
- **Metrics** — activation counts from the originating environment.
  These are reference numbers; they are not targets for your own
  adoption.
- **Notes** — context that did not fit elsewhere.

## How to adopt a scar

1. **Read the origin section.** Does the failure shape match
   something that could happen in your own work? If not, skip the
   scar.
2. **Check the trigger.** Can you produce an equivalent trigger in
   your own environment? If the original trigger is "any Python
   file that imports `docx`" and your environment doesn't generate
   Word documents, the scar does not apply to you.
3. **Translate the fix.** The fix is written in terms of the
   originating environment's tooling. Your version might be a
   different script, a different command, or a different prompt
   template, but it should have the same structural property:
   it runs in the moment the trigger fires, and it produces an
   observable artifact (a log line, a printed block, a file edit)
   that can be audited later.
4. **Install or enforce.** If there is a hook, copy it from
   `../hooks/` and point your `settings.json` at it. If the scar
   is behavioral, write the protocol into your project's `CLAUDE.md`
   or equivalent so the model re-encounters it every session.
5. **Track failures.** When the scar fails (the mistake happens
   anyway, the trigger missed, the fix was skipped) → that is
   actionable data. Update the scar text to make the trigger or
   the fix sharper.

## How to write your own

The five scars in this directory are not meant to be exhaustive.
They are starter material; your operation has its own failure modes.
If you want to write your own scar:

1. Wait for a real mistake. Do not preemptively write scars for
   hypothetical failures; they will not stick, because nothing
   in your reasoning will remember them at the moment of
   temptation. The failure is what creates the scar.
2. Write the failure down immediately after recovery, while the
   details are present. The origin section is the load-bearing
   one; if you compress it too much, the scar loses its teeth.
3. Name the trigger narrowly. A scar whose trigger is "anytime you
   write code" is not a scar; it is a wish. A scar whose trigger
   is "any Python file importing `requests` that also calls
   `json.loads` on the response" is a scar.
4. Make the fix cheap. If the fix takes five minutes, you will
   skip it. If the fix is one command or one block of text in a
   self-review, it runs.
5. Add a hook if you can. A behavioral scar lives or dies on the
   model remembering to apply it; a scar with a PreToolUse hook
   has the harness firing it automatically in the right moment.
   See `../hooks/` for how the existing hooks are structured.

## The five scars in this directory

| File | Severity | Has hook | What it catches |
|---|---|---|---|
| [`scar_001_docx_tildes.md`](scar_001_docx_tildes.md) | medium | yes | Accents silently stripped from uppercase headings in generated DOCX files |
| [`scar_002_code_review_absent.md`](scar_002_code_review_absent.md) | high | yes | Large generated code blocks shipping without a source-level review |
| [`scar_003_token_budget.md`](scar_003_token_budget.md) | medium | no | Token budget drained by `/clear`, MCP, and subagent-model defaults |
| [`scar_004_consult_kb_first.md`](scar_004_consult_kb_first.md) | high | no | Generating a response before consulting the project knowledge base |
| [`scar_005_validate_subagent_output.md`](scar_005_validate_subagent_output.md) | high | yes | A subagent silently omitting a file from a batch without reporting it |
