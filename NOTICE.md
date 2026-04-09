# Notice

## Origin and context

The scars and hooks in this repository were developed while
operating DG Ingenieria SRL, a civil engineering firm in Paraguay,
on top of Claude Code. They are the artifacts described in Part V
of the accompanying essay, *The Lucy Syndrome and AI*
(<https://victordelpuerto.com/posts/lucy-syndrome/>), and the essay
is the canonical reference for the motivation, the theory, and the
empirical observations that produced them.

The contents of this repository are the **sanitized, reusable**
portion of a larger operational system. The rest of the system
remains private for reasons explained below.

## What is not in this repository

The following are intentionally excluded and will not be published:

- **Project logs and bitacoras.** The source material for the essay
  was a dataset of real project logs across nine business areas.
  Those logs contain client names, project identifiers, internal
  decision history, and financial details. They are confidential
  by client agreement and are not republishable in any sanitized
  form without violating the confidentiality obligation.

- **The domain-specific knowledge bases.** The firm operates on top
  of dense, private knowledge bases for civil engineering,
  highway design, paving, industrial plants, and construction
  specifications, each with its own `CLAUDE.md` configuration.
  These are not in scope for a general-purpose scar repository.

- **Scars that are domain-specific.** Several scars beyond the five
  published here are specific to engineering documentation formats,
  local regulations, or internal tooling that is only meaningful
  inside the firm. They have been omitted because they would not
  be reusable for anyone outside that context.

- **Internal identifiers.** Project codes, client codes, file
  paths, and internal tracking numbers have been removed from all
  scar documents. Where the original scar cited "project X case
  N.NN" as supporting evidence, the sanitized scar either
  generalizes the description or cites the case as "a real case
  in a project with a dense knowledge base" without naming it.

- **Exact metrics tied to cost.** The originating scar documents
  contain some figures tied to the firm's actual spending on
  tooling and compute. Those have been removed from the published
  scars; the metrics sections in the published files reference
  activation counts only.

## What is in this repository

- **Five scar documents** describing patterns the originator
  considers universal enough to be useful to any operator running
  a production LLM workflow. The origin sections reference the
  originating environment generically ("a technical specification
  document I was generating", "a civil engineering firm operating
  on Claude Code") but omit specifics.

- **Four Claude Code hooks** that enforce four of the five scars at
  the harness layer. The hooks are warn-only by design and can be
  disabled without breaking a session. See `hooks/REVERSIBILITY.md`.

- **Accompanying documentation** explaining what a scar is, how to
  read one, how to adopt one, and how to write your own.

## Attribution

If you adopt material from this repository in your own work, you
are not required to cite it (the Apache License 2.0 covers
attribution legally). It is however useful to link to the essay
and this repository when the framework is discussed, because the
value of a functional-scar framework depends partly on the
vocabulary becoming shared — the term is useless if it does not
spread, and it spreads through citation.

Suggested citation format for written work:

> Del Puerto Gauto, Victor Daniel. *The Lucy Syndrome and AI.*
> Independent research, 2026.
> <https://victordelpuerto.com/posts/lucy-syndrome/>

## Contact

Questions about adaptation, commercial advisory on LLM operations,
or discussion of the framework in your own environment:

- Email: see the blog above.
- Issues on this repository are welcome for bugs in the hooks or
  sanitization issues in the scar documents. Feature requests and
  "please write a scar for my use case" are out of scope; see the
  "How to write your own" section in `scars/README.md` for that.
