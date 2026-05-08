# Lucy Syndrome

**A practitioner framework for making LLM corrections persist across sessions.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19555971.svg)](https://doi.org/10.5281/zenodo.19555971)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

> *"Every session starts from zero. I've built the equivalent of Henry's videos — a system prompt, knowledge base overlays, instruction files. Every morning, the system reads its 'video' and functions. Often brilliantly. But it doesn't remember watching it yesterday."*
>
> — [The Lucy Syndrome and AI](https://victordelpuerto.com/posts/lucy-syndrome/)

---

## What This Is

Large Language Model agents operating in production environments systematically lose corrections between sessions. An operator fixes an error, the model acknowledges the fix, and the next session reproduces the original mistake as if the correction never happened.

This repository is a practitioner framework for closing that gap. It contains:

- **Functional scars** — short structured documents that record a mistake, why it recurs, and the specific operational rule that prevents repetition
- **Claude Code hooks** — Python scripts that enforce those rules automatically at inference time, without requiring discipline from the operator
- **An install script** — to bootstrap the system into your own project in under two minutes
- **A production case study** — 11 published scars + 9 hooks from a civil engineering firm running 9 business areas through Claude Code, grounded in 163 findings extracted from 17 operational session logs

The companion research paper (DOI: [10.5281/zenodo.19555971](https://doi.org/10.5281/zenodo.19555971)) describes the underlying dataset, the five persistence invariants, and the three-layer implementation model. A first derivative essay extending the four-layer progression argument is now published: [*From Memory to Scar*](https://victordelpuerto.com/posts/from-memory-to-scar/) (May 2026).

---

## Why It Matters

The standard industry solutions — system prompts, knowledge bases, memory systems, RAG — share a fundamental limitation: they present information, but do not create the weight of experience. A correction documented after a costly mistake gets read with the same attention as a style preference. There is no mechanism for "this one matters more because it hurt last time."

This pattern is not hypothetical. Anthropic's [Managed Agents Memory](https://platform.claude.com/docs/en/managed-agents/memory) (beta released 2026-04-24) packages the standard prescription — a workspace-scoped memory store the agent reads and writes — and ships it as a primitive. The companion essay [*From Memory to Scar*](https://victordelpuerto.com/posts/from-memory-to-scar/) argues that this is Layer 3 industrialized: the agent remains reader, decider, and writer, with no enforcement layer outside the model. The same gap the paper identifies persists.

Functional scars are an attempt to add the missing layer. The research identifies five invariants that distinguish corrections that persist from those that decay:

1. **Binary rule** — expressible as a concrete check, not a judgment call
2. **Durable physical support** — lives in a file the model reads every session
3. **Structural integration** — wired into the output format, not appended as an afterthought
4. **Non-passive technical trigger** — a hook that fires at the moment of risk, not just at session start
5. **Refinable activation metric** — tracks its own success/failure so it can be sharpened over time

Scars satisfying all five invariants in the dataset have a measured escape rate below 10%. Rules failing any single invariant have rates above 30%.

---

## Quick Start

### Install into your Claude Code project

```bash
git clone https://github.com/Vdp89/lucy-syndrome.git
cd lucy-syndrome
./install.sh /path/to/your/project
```

The script creates `.claude/scarring/` in your project with a blank scar template and a minimal session-start hook. From there, add your own scars as mistakes accumulate.

### Your first scar

1. Copy `framework/scar_template.md` to `.claude/scarring/scar_001_your_mistake.md`
2. Fill in the six sections: what happened, where it applies, why it is forgotten, the fix, how to verify, metrics
3. Edit `hooks/hook_session_start.py` to include a one-line summary of the new scar
4. Wire the hook into `.claude/settings.json` (see `framework/settings.json.example`)

The first time the trigger fires and the reminder injects automatically, the value of the system becomes concrete.

---

## Status — Phase E (deployed 2026-04-25)

This repository is **operational, not theoretical**. As of 2026-05-08 the framework has been running 13 days under Phase E (full logging + opportunity observation):

```
fires logged       : 359
opportunities      : 910
active scars       : 7 with hooks (+ 5 documented without enforcement)
hooks instrumented : 9 (8 production + 1 generic example)
latency p50        : 29.2 ms
latency p99        : 390 ms (outlier: scar_004 memory-index parse)
```

### Per-scar activity

| Scar | Fires (13 days) | Opportunities | Recall | Notes |
|---|---:|---:|---:|---|
| scar_004 (consult_kb_first) | 197 | 171 | n/a* | Most active scar; UserPromptSubmit |
| scar_002 (code_review_absent) | 66 | 553 | 11.9% | PreToolUse, 200-line threshold |
| session_start | 51 | n/a | n/a | Fires once per session |
| scar_001 (docx_tildes) | 24 | (no observer) | n/a | PreToolUse, .py touching docx |
| scar_005 (validate_subagent) | 11 | (no observer) | n/a | PreToolUse Task |
| scar_011 (tildes_entregables) | 6 | 34 | 17.6% | PreToolUse, deliverable paths |
| scar_010 (no_cerrar_puertas) | 4 | 152 | 2.6% | PreToolUse, brand copy |

\* scar_004 has more fires than observed opportunities because the observer rule is currently narrower than the hook's trigger; this is a known issue (the observer rule should be the broader filter, not the narrower one) and will be fixed in a future release.

### What "recall" means here

`recall = fires / opportunities`. An "opportunity" is a context where a scar should have had a chance to fire — observed independently by `hook_opportunity_observer.py`, broader than the scar's own trigger threshold. A low recall (e.g. scar_010 at 2.6%) means the scar trigger is too narrow relative to the contexts where the rule applies; the hook is missing most cases. A high recall (e.g. scar_011 at 17.6%) is closer to the trigger doing its job. These numbers are inputs for tuning, not pass/fail grades.

This kind of measurement is precisely what invariant I5 ("refinable activation metric") requires. Phase E is the closing of I5 in operational form.

---

## Observability: closing I5

The fifth persistence invariant requires that every scar have a *refinable activation metric* — a way to know whether it is firing, whether it is preventing errors, and whether its trigger is too broad or too narrow.

`logging/log_scar_fire.py` writes one JSON line to `fires.jsonl` on each fire, capturing: timestamp, session ID, scar ID, hook version, tokens injected, hook latency, trigger fragment, and payload hash.

`hook_opportunity_observer.py` (Phase 3, added in this release) writes one JSON line to `opportunities.jsonl` on every context where a scar **could have** fired — broader than the actual trigger threshold. Without observed opportunities, recall = fires / fires = 1.0 (trivially useless). With them, recall is a real metric.

From these two files, the nine Phase 2 metrics in [`docs/metrics.md`](docs/metrics.md) become computable — including `activation_rate`, `false_positive_rate`, `latency_overhead`, and `severity_adjusted_harm`.

`install.sh` copies both loggers to `.claude/scarring/logs/` automatically. Both `.jsonl` files are gitignored by default. See [`logging/README.md`](logging/README.md) for the integration pattern.

---

## Repository Structure

```
lucy-syndrome/
├── README.md                    ← you are here
├── LICENSE                      ← Apache 2.0
├── NOTICE.md                    ← attribution and what is not here
├── CITATION.cff                 ← academic citation file
├── CHANGELOG.md                 ← release history
├── install.sh                   ← bootstrap script
│
├── framework/                   ← templates and guides
│   ├── README.md               ← how the framework works end to end
│   ├── ARCHITECTURE.md         ← Mermaid diagrams of the layers
│   ├── scar_template.md        ← blank scar to fill in
│   ├── hook_template.py        ← blank hook to customize
│   └── settings.json.example   ← Claude Code hook configuration
│
├── logging/                     ← Phase 2 + 3 observability
│   ├── log_scar_fire.py        ← fires logger (closes I5 — fires side)
│   ├── log_opportunity.py      ← opportunities logger (Phase 3 — recall denominator)
│   ├── README.md               ← integration pattern + schema reference
│   └── .gitignore              ← excludes fires.jsonl + opportunities.jsonl from git
│
├── scars/                       ← generic example scars (domain-independent)
│   ├── README.md               ← scar schema, rationale, adoption guide
│   ├── scar_example_001_review_before_deliver.md
│   ├── scar_example_002_verify_before_claiming.md
│   └── scar_example_003_check_context_before_generating.md
│
├── hooks/                       ← generic hooks for the example scars
│   ├── README.md               ← hook anatomy and adaptation guide
│   ├── REVERSIBILITY.md        ← how to disable or roll back hooks safely
│   ├── hook_session_start.py   ← injects scar summary at session start
│   └── hook_example_review.py  ← fires on large code writes
│
├── docs/
│   ├── logging-schema.json     ← JSON Schema for fires.jsonl entries
│   ├── metrics.md              ← 9 Phase 2 metrics derived from fires.jsonl
│   ├── escalation-policy.md   ← thresholds for warn→deny escalation
│   └── experimental-design.md ← methodology notes
│
├── examples/
│   └── production-case/         ← real 11 scars + 9 hooks from production
│       ├── README.md           ← context: civil engineering operation, 163 findings
│       ├── scars/              ← the actual production scar files
│       └── hooks/              ← the actual production hook scripts (with logging)
│
└── research/
    ├── paper.md                 ← The Lucy Syndrome and AI (full paper text)
    ├── statistics.md            ← dataset statistics: 163 findings, 4 categories
    └── cross-analysis.md        ← persistence invariants and cross-category analysis
```

---

## The Production Case

`examples/production-case/` contains operational scars and hooks from a civil engineering firm in Paraguay running nine business areas through Claude Code. The underlying dataset: 163 findings extracted from 17 source files (15 Claude Code session logs, 2 ChatGPT memory exports), spanning August 2025 to April 2026.

This is not a cleaned-up demo. These are the real files — including the failures, the reincidences, and the evolution of each rule as the system learned what it took to make a correction stick. The production case includes 11 scars and 9 hooks across four hook event types: `SessionStart`, `PreToolUse`, `UserPromptSubmit`.

### A note on what is NOT in this repository

A 12th scar (`scar_012`, canal_compartido_sin_briefing — critical severity, blocking) has been operational locally since 2026-04-30. It is **withheld from this repository** because it contains specific commercial-negotiation context that cannot be sanitized without losing the testimonial value of the production case. The underlying pattern — that briefings must not travel through shared channels with external recipients — is generic; the implementation reflecting it may appear in a sibling project as a sanitized cookbook entry.

### Key findings from the production dataset

- **163 findings** across 4 categories: 37 repeated errors (A), 55 successful corrections (B), 29 false confidences (C), 42 metacognitive frictions (D)
- **Ratio B/A = 1.49** — for every repeated error, approximately 1.5 successful corrections. RIALTO, the project with the densest scar-like system (67+ numbered rules), had the highest correction density in the dataset
- **Rule shape predicts persistence**: binary rules leak at 17%, proportional/conditional rules leak at 75–100%
- **Verbal corrections with no physical support** have a measured escape rate of 100%

### Reincidences after publication (2026-04-15 and 2026-04-22)

Two reincidences were documented after the public release of the framework:

- **A3.1 (2026-04-15) — "expansion vs reading."** The operator complied formally with `scar_004` (read the memory index) but did not expand the pointer files referenced by the task. The scar fired in form, failed in function. Filed at `02_ANALISIS/incidente_2026-04-15_expansion_vs_lectura.md` (in the lab notes, not in this repository).
- **A3.2 (2026-04-22) — "pull-gravitational at session close."** While documenting the canonical AASHTO/Peltier case, the agent committed a functionally equivalent error at close: a stale relative-time reference to an entity that had been mutated 35 minutes / 33 turns earlier within the same session. Stronger evidence than A3.1: the framework was active, the canonical case was open in context, and the recurrence happened anyway.

Both reincidences confirm a thesis the paper makes explicitly: without enforcement outside the model, even full awareness of the framework does not prevent recurrence. Memory systems, even when complete, are Layer 3 — not Layer 4.

---

## Research

The companion paper is available in three places:

- **Full text**: [`research/paper.md`](research/paper.md) in this repository
- **Zenodo** (citable preprint with DOI): [doi:10.5281/zenodo.19555971](https://doi.org/10.5281/zenodo.19555971)
- **Web** (annotated, with commentary): [victordelpuerto.com/posts/lucy-syndrome/](https://victordelpuerto.com/posts/lucy-syndrome/)

### Derivative essays

- **#1 — From Memory to Scar** (May 2026): [victordelpuerto.com/posts/from-memory-to-scar/](https://victordelpuerto.com/posts/from-memory-to-scar/). Extends the four-layer progression with Anthropic's Managed Agents Memory beta (2026-04-24) as a working example of Layer 3 industrialized.

---

## Citation

```bibtex
@misc{delpuerto2026lucy,
  author    = {Del Puerto, Victor Daniel},
  title     = {Lucy Syndrome in LLM Agents: A Practitioner Framework
               for Cross-Session Correction Persistence},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19555971},
  url       = {https://doi.org/10.5281/zenodo.19555971}
}
```

See [CITATION.cff](CITATION.cff) for CFF format.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

The research paper (`research/paper.md`) is © Victor Daniel Del Puerto Gauto, all rights reserved; included here to accompany the code. See [NOTICE.md](NOTICE.md) for full attribution.

---

## Author

Victor Daniel Del Puerto Gauto
[victordelpuerto.com](https://victordelpuerto.com) · [info@dgingenieriasrl.com](mailto:info@dgingenieriasrl.com)
