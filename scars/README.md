# Scars

> A scar is a short structured document that records a mistake you already made once,
> and the specific operational rule you now apply so the same mistake cannot repeat silently.

---

## What a scar is

A scar is **not** a best practice, a style guide, or a checklist of hygiene tips. Those things are cheap to write and easy to ignore. A scar has three properties:

1. **It is born from a real failure.** Every scar in the production case exists because the corresponding mistake actually happened, in production, and it cost something to recover from.

2. **It has a trigger you can check for.** The scar names the specific context where the mistake can recur: a file extension, a library import, a task type, a phrase in a prompt. This is what makes it enforceable.

3. **It has a fix that can be executed in the moment.** Not "think more carefully" — a concrete action that either runs automatically (via a hook) or that the operator performs mechanically when the trigger fires.

---

## The scar schema

Every scar file has the same sections:

| Section | Purpose |
|---|---|
| YAML frontmatter | `id`, `name`, `severity`, `created`, `status` |
| What happened (origin) | The specific failure that justified this scar |
| Where it applies (trigger) | Observable conditions under which the mistake can recur |
| Why it gets forgotten (root cause) | The mechanism that causes repetition despite documentation |
| Scar (fix) | The concrete action to execute when the trigger fires |
| How to verify | The observable artifact that proves the scar ran |
| Metrics | Activations, success, recurrences |

---

## The example scars in this directory

These are domain-independent examples derived from the production case (see `../examples/production-case/`). Together they cover the universal subset of the production case (5 of 11 production scars; the rest are domain-specific). Use them as starting points, not as final implementations — adapt the triggers and fixes to your own environment.

| File | Severity | Has hook | What it catches |
|---|---|---|---|
| `scar_example_001_review_before_deliver.md` | high | yes | Code shipped without source-level review |
| `scar_example_002_verify_before_claiming.md` | critical | no | Fabricated external content; wrong day-of-week labels |
| `scar_example_003_check_context_before_generating.md` | high | no | Generating before consulting the knowledge base |
| `scar_example_004_validate_subagent_output.md` | high | reference impl. in production-case | Subagent silently omits a file from a batch dispatched via `Task` |
| `scar_example_005_token_budget_hygiene.md` | medium | no | Context bloat: missed `/clear` between unrelated tasks, unused MCPs left loaded, oversized models on simple subagents |
| `scar_example_006_pre_deploy_audit.md` | high | no | Inconsistent state shipped to production: retired strings still live, edits applied locally instead of swept globally |
| `scar_example_007_persist_memory_before_goodbye.md` | high | no | Session-end discoveries lost because memory was not written before the wrap-up message |

---

## How to adopt a scar

1. **Read the origin section.** If the failure shape does not match something your environment could produce, the scar does not apply to you.

2. **Check the trigger.** Translate the trigger conditions to your own tooling. If the original trigger is "any Python file that imports `docx`" and your environment does not generate Word documents, the scar does not apply.

3. **Translate the fix.** Your version may use different scripts or commands, but it should have the same structural property: it runs *at the moment the trigger fires*, and it leaves an observable artifact.

4. **Install or enforce.** If there is a hook, copy it from `../hooks/` and point your `.claude/settings.json` at it. If the scar is behavioral, add the protocol to your `CLAUDE.md` so the model re-reads it every session.

5. **Track failures.** When the scar fires but the error still occurs, that is actionable data. Update the scar to sharpen the trigger or the fix.

---

## How to write your own

1. Wait for a real mistake. Do not preemptively write scars for hypothetical failures.
2. Write the failure down immediately after recovery, while the details are present.
3. Name the trigger narrowly.
4. Make the fix cheap to execute — if it costs more than skipping it, it will be skipped.
5. Add a hook if you can. A behavioral scar lives or dies on the model remembering to apply it; a scar with a `PreToolUse` hook fires automatically.

See `../framework/scar_template.md` for the blank template and `../framework/README.md` for the full guide.
