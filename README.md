# The Lucy Syndrome

> Hooks and scars I use to keep an LLM from making the same mistake twice.
>
> Companion code to [*The Lucy Syndrome and AI*](https://victordelpuerto.com/posts/lucy-syndrome/) —
> an essay on why models forget every morning, and what an operator can
> do about it.

---

## The short version

A large language model does not remember yesterday. Every session
begins from the same frozen weights, the same priors, the same blind
spots. Corrections made last week — even when documented, even when
loaded back into context — do not carry the weight of having been
made. Reading that fire burns is not the same as having been burned.

The essay is about that gap. This repository is what I built to
close it in my own operation.

It contains five **functional scars**: short documents that record a
mistake I already made once, along with the specific operational
rule I now apply so the same mistake cannot repeat silently. Four
of them are enforced by Claude Code hooks that fire automatically at
the triggering event. None of the hooks block anything; they only
inject reminder context.

This is not a framework, a paper, or a product. It is a small,
pragmatic toolkit born from running a civil engineering firm on top
of Claude Code for several months. It is the minimum-viable version
of a practice, not a finished one.

## What is in this repository

```
lucy-syndrome/
├── README.md                 ← you are here
├── LICENSE                   ← Apache 2.0
├── NOTICE.md                 ← what is NOT here + attribution
│
├── scars/                    ← the five functional scars
│   ├── README.md             ← what a scar is, how to read one, how to write your own
│   ├── scar_001_docx_tildes.md
│   ├── scar_002_code_review_absent.md
│   ├── scar_003_token_budget.md
│   ├── scar_004_consult_kb_first.md
│   └── scar_005_validate_subagent_output.md
│
└── hooks/                    ← Claude Code hooks (reference implementation)
    ├── README.md             ← install guide, hook anatomy, how to adapt
    ├── REVERSIBILITY.md      ← how to disable or roll back
    ├── settings.json.example ← copy-paste wiring for .claude/settings.json
    ├── hook_session_start.py
    ├── hook_scar_001_docx.py
    ├── hook_scar_002_size.py
    └── hook_scar_005_subagent.py
```

## The five scars

| Scar | Severity | Hook | What it catches |
|---|---|---|---|
| [`scar_001`](scars/scar_001_docx_tildes.md) | medium | yes | Accents silently stripped from uppercase headings in generated DOCX files |
| [`scar_002`](scars/scar_002_code_review_absent.md) | high | yes | Large generated code blocks shipping without a source-level review |
| [`scar_003`](scars/scar_003_token_budget.md) | medium | no | Token budget drained by missing `/clear`, unused MCP servers, and subagent-model defaults |
| [`scar_004`](scars/scar_004_consult_kb_first.md) | high | no | Generating a response before consulting the project knowledge base |
| [`scar_005`](scars/scar_005_validate_subagent_output.md) | high | yes | A subagent silently omitting a file from a batch without reporting it |

## Quickstart

Install the hooks in your own Claude Code project:

```bash
git clone https://github.com/VDP89/lucy-syndrome.git
cd lucy-syndrome

# Copy the hooks into your project
mkdir -p /path/to/your-project/.claude/hooks
cp hooks/hook_*.py /path/to/your-project/.claude/hooks/

# Merge settings.json.example into your project's .claude/settings.json
# (adjusting the command paths to point at .claude/hooks/ if needed)
```

Claude Code watches `settings.json` live; the hooks take effect on
the next tool call. Verify the `SessionStart` hook by starting a new
session — you should see the scar summary appear in the model's
context.

Read [`hooks/REVERSIBILITY.md`](hooks/REVERSIBILITY.md) before
installing. All four hooks are warn-only; disabling them is a
single-file edit.

## How to use this repository

The scars are not a checklist to adopt wholesale. They are worked
examples. For each one:

1. Read the origin section. If the failure shape does not match
   something that could happen in your own work, the scar does not
   apply to you. Skip it.
2. If the shape matches, read the trigger section. Translate the
   trigger into your own environment (your file paths, your
   extensions, your task shapes).
3. Copy the hook, adapt the `additionalContext` text to reference
   your own paths, install it.
4. Track failures. When the scar fires but the mistake still
   happens, the trigger or the fix needs sharpening. Edit the
   scar doc in your fork.

If you want to write your own scars, the `scars/README.md` file has
a section on how to do that. The short version: wait for a real
failure, name the trigger narrowly, make the fix cheap, add a hook
if you can.

## Why "Lucy"

From the movie *50 First Dates*. Lucy Whitmore wakes up every
morning with no memory of the day before — a brain injury wiped her
ability to convert short-term memories into long-term ones. Her
boyfriend Henry plays her a video every morning that recaps their
relationship. She watches, orients, functions. Some days
brilliantly. And she never — not once — remembers watching it.

The essay argues that large language models have the same condition,
and that the industry's current solutions (context windows, system
prompts, knowledge bases, memory systems, RAG) are all Henry's
videos in one form or another. They work, and they are not nothing,
but they do not change the underlying condition. The scar mechanism
is a different class of intervention: it makes a prior mistake
structurally harder to repeat, rather than trying to make the model
remember.

The full argument, with the supporting cases and the framework it
derives, is in the [essay](https://victordelpuerto.com/posts/lucy-syndrome/).

## License

Apache License 2.0. See [`LICENSE`](LICENSE).

The Apache license was chosen over MIT because of its explicit
patent grant. The code in this repository is small enough that this
is almost certainly overkill, but costs nothing and protects
downstream adopters in the edge case where something derivative
gets patented.

## Attribution

If you adopt material from this repository, you are not required to
cite it — the license covers attribution legally. Linking to the
essay and the repository when discussing the framework is useful
because the vocabulary depends on shared citation to spread.

Suggested citation for written work:

> Del Puerto Gauto, Victor Daniel. *The Lucy Syndrome and AI.*
> Independent research, 2026.
> <https://victordelpuerto.com/posts/lucy-syndrome/>

## Contact

Victor Daniel Del Puerto Gauto — civil engineer and independent
researcher, based in Paraguay. Writing and research at
[victordelpuerto.com](https://victordelpuerto.com).

For advisory on LLM operations in production — adapting the
framework to your own environment, designing your own scars,
auditing a running workflow for Lucy Syndrome failure modes — see
the contact information on the blog.
