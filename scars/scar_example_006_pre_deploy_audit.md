---
id: scar_example_006
name: pre_deploy_audit
severity: high
created: 2026-04-26
status: example
---

# scar_example_006 — Inconsistent state shipped to production

> **Example scar.** This file is a domain-independent template derived from the production case.
> Adapt the trigger, fix, and metrics to your own environment.
> The originating incident is documented in `examples/production-case/scars/scar_006_pre_deploy_audit.md`.

---

## What happened (origin)

Multiple deploys to a public-facing site went out without a consistency sweep. Two distinct kinds of drift made it into production at the same time:

- **Sensitive data leak:** a private contact number had been replaced in two places (the footer and a sticky CTA) but **not** on the dedicated contact page. Visitors saw a number the team had deliberately retired.
- **Stale copy:** phrasings the team had decided to remove (deprecated brand language, retired service names, old partnership references) survived in some pages because they were edited per-file rather than swept across the codebase.

The shape of the failure: edits that should have been **global** were applied as local patches in whichever file the edit session happened to open. Nothing in the workflow forced a "did you grep the whole tree?" step before the deploy. The deploy itself succeeded mechanically — `git push` worked, the build passed — and the inconsistencies only surfaced after they were live, when the operator (or worse, a visitor) noticed.

## Where it applies (trigger)

- Any `git push` to a branch that auto-deploys (main / production / a Vercel- or Netlify-watched branch)
- Any explicit deploy command (`vercel deploy --prod`, `npm run release`, `cap deploy`, etc.)
- Any merge of a PR labelled `release`, `deploy`, or similar
- Any task whose output is a public-facing artifact (site, doc, dataset, package release)

## Why it gets forgotten (root cause)

- **The mechanical step succeeds.** A successful build / passing CI is mistaken for "the deploy is correct". CI checks code; it does not check that the team's editorial decisions were applied uniformly.
- **Edits are local by default.** When the operator opens one file to fix a phrase, the same phrase elsewhere stays unfixed. There is no automatic "this string appears in 7 files, edit all 7?" prompt unless the agent introduces one.
- **No friction at the boundary.** Nothing intercepts the moment of deploy with a checklist. The path from "looks ready" to "live" is one command.
- **Compound risk.** Each individual missed edit is a small inconsistency. Across many deploys, they accumulate into a public-facing identity that does not match the team's current decisions.

## Scar (fix)

**Mandatory consistency audit before every production deploy. Five steps, all greppable, all under a minute.**

### Step 1 — Sensitive-data sweep

Maintain a project-local list of strings that must NOT appear in shipped artifacts (retired phone numbers, retired emails, internal usernames, sample API keys, placeholder copy). Grep for each before deploy:

```bash
grep -rn -E "(retired_string_1|retired_string_2|...)" <build_or_src_dir>
```

Any non-zero result → block the deploy until the matches are addressed.

### Step 2 — Forbidden-phrase sweep

Maintain a list of phrasings the team has explicitly decided to remove (rebranded language, copy retired in editorial review, anti-patterns that re-appear across files). Same form:

```bash
grep -rn -E "(deprecated_phrase_1|deprecated_phrase_2|...)" <src_dir>
```

### Step 3 — Stale-reference sweep

Names of retired projects, partnerships, products, or features. These tend to live in cross-references the operator forgot existed (sidebar links, related-content blocks, sitemap entries).

### Step 4 — Cross-page concordance check

For values that should match across multiple files (canonical title, contact info, version number, copyright year), grep with `-h` (suppress filenames) and reduce to unique matched lines — divergence shows up as more than one unique line:

```bash
grep -rh "canonical_value" <src> | sort -u
# expect exactly one unique line; multiple means the value differs across files
```

If the value lives in a `key: value` pattern and you only care about the value itself (not the surrounding line), extract it explicitly rather than reaching for `awk -F:` — the colon in `key:` collides with grep's `path:lineno:line` separator and silently collapses different values to the same key token, producing a false-clean audit:

```bash
# Correct: extract just the value after `canonical_key:`
grep -rho 'canonical_key:[[:space:]]*\S.*' <src> \
  | sed 's/^canonical_key:[[:space:]]*//' \
  | sort -u
# expect exactly one unique value
```

### Step 5 — Build / type / link check

`npm run build`, `cargo check`, `mypy`, `pytest`, link-checker — whichever the project uses. This is the only step that is mostly automated already; the four above are the gap this scar is closing.

A single shell script (`audit_pre_deploy.sh`) that runs all five and exits non-zero on any failure is the canonical implementation. The audit must run **after** `git add`/staging and **before** `git push`/`vercel deploy`.

## How to verify

- The audit script (or its checklist equivalent) ran and returned a clean result before the deploy command was issued — verifiable in shell history or CI logs
- If a forbidden phrase or sensitive datum is found in production after deploy → top-priority scar failure; the audit step was either skipped or its grep list is incomplete
- Audit pattern over time: track how often the audit returns a non-empty result. A sustained zero suggests the grep list has gone stale; a sustained high count suggests the editorial process needs a step earlier than deploy

## Metrics

- Activations: 0
- Success: 0 (N/A — adapt to your own environment)
- Last applied: never
- Post-scar recurrences: 0
- Notes: A `PreToolUse Bash` hook that intercepts `git push` to deploy branches (or `vercel deploy --prod`) and either runs the audit script or reminds the operator to run it would make this scar enforceable rather than purely behavioral. The grep lists in steps 1-3 should live in a project-local file (`.claude/scarring/audit_lists.txt` or similar) so they evolve with the project.
