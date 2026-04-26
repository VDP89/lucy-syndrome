# Lucy Syndrome

**A practitioner framework for making LLM corrections persist across sessions.**

[![CI](https://github.com/VDP89/lucy-syndrome/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/VDP89/lucy-syndrome/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)](https://github.com/VDP89/lucy-syndrome/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://github.com/VDP89/lucy-syndrome/blob/main/pyproject.toml)
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
- **A production case study** — the actual 11 scars and 8 hooks from a civil engineering firm running 9 business areas through Claude Code, grounded in 163 findings extracted from 17 operational session logs

The companion research paper (DOI: [10.5281/zenodo.19555971](https://doi.org/10.5281/zenodo.19555971)) describes the underlying dataset, the five persistence invariants, and the three-layer implementation model.

---

## Why It Matters

The standard industry solutions — system prompts, knowledge bases, memory systems, RAG — share a fundamental limitation: they present information, but do not create the weight of experience. A correction documented after a costly mistake gets read with the same attention as a style preference. There is no mechanism for "this one matters more because it hurt last time."

Functional scars are an attempt to build that mechanism. The research identifies five invariants that distinguish corrections that persist from those that decay:

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
git clone https://github.com/VDP89/lucy-syndrome.git
cd lucy-syndrome
./install.sh /path/to/your/project
```

The installer creates `.claude/scarring/{hooks,logs}/` in your project, drops a blank scar template, copies the SessionStart and example review hooks, and runs a smoke test. If your project has no `.claude/settings.json` yet it writes one with the hooks wired; if you already have one it leaves it untouched and prints the merge instructions.

After the install reports `Installation complete and smoke test passed`, restart Claude Code (or open it from the project) and the SessionStart hook will announce the scarring system on the first prompt.

### Your first scar

1. Edit `.claude/scarring/scar_001_your_first_scar.md` (the placeholder created by `install.sh`) using the six sections in `framework/scar_template.md`: what happened, where it applies, why it is forgotten, the fix, how to verify, metrics.
2. The SessionStart hook auto-discovers any `scar_*.md` file in `.claude/scarring/` -- no edit to the hook is needed.
3. If the new scar needs an enforcement hook (PreToolUse / UserPromptSubmit / etc.), copy `framework/hook_template.py` into `.claude/scarring/hooks/` and add a matching entry under `"hooks"` in `.claude/settings.json`.

The first time the trigger fires and the reminder injects automatically, the value of the system becomes concrete.

### Verify the install

```bash
echo '{}' | python3 .claude/scarring/hooks/hook_session_start.py
```

Should print a one-line JSON object whose `additionalContext` lists every `scar_*.md` file you have. If it lists `scar_001_your_first_scar.md`, you are wired.

---

## Observability: closing I5

The fifth persistence invariant requires that every scar have a *refinable activation metric* — a way to know whether it is firing, whether it is preventing errors, and whether its trigger is too broad or too narrow.

`logging/log_scar_fire.py` closes this gap. Every hook that calls it writes one JSON line to `fires.jsonl` on each fire, capturing: timestamp, session ID, scar ID, hook version, tokens injected, hook latency, trigger fragment, and payload hash.

From this data, the nine Phase 2 metrics in [`docs/metrics.md`](docs/metrics.md) become computable — including `activation_rate`, `false_positive_rate`, `latency_overhead`, and `severity_adjusted_harm`.

`install.sh` copies the logger to `.claude/scarring/logs/` automatically. `fires.jsonl` is gitignored by default. See [`logging/README.md`](logging/README.md) for the integration pattern.

---

## Repository Structure

```
lucy-syndrome/
├── README.md                    ← you are here
├── LICENSE                      ← Apache 2.0
├── NOTICE.md                    ← attribution and what is not here
├── CITATION.cff                 ← academic citation file
├── install.sh                   ← bootstrap script
│
├── framework/                   ← templates and guides
│   ├── README.md               ← how the framework works end to end
│   ├── scar_template.md        ← blank scar to fill in
│   ├── hook_template.py        ← blank hook to customize
│   └── settings.json.example   ← Claude Code hook configuration
│
├── logging/                     ← Phase 2 observability
│   ├── log_scar_fire.py        ← append-only JSONL logger (closes I5)
│   ├── README.md               ← integration pattern + schema reference
│   └── .gitignore              ← excludes fires.jsonl from git
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
│   └── hook_example_review.py  ← fires on large code writes (for scar_example_001)
│
├── docs/
│   ├── logging-schema.json     ← JSON Schema for fires.jsonl entries (18 fields)
│   ├── metrics.md              ← 9 Phase 2 metrics derived from fires.jsonl
│   └── escalation-policy.md   ← thresholds for warn→deny escalation
│
├── examples/
│   └── production-case/         ← real 11 scars + 8 hooks from production
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

`examples/production-case/` contains the actual operational scars and hooks from a civil engineering firm in Paraguay running nine business areas through Claude Code. The underlying dataset: 163 findings extracted from 17 source files (15 Claude Code session logs, 2 ChatGPT memory exports), spanning August 2025 to April 2026.

This is not a cleaned-up demo. These are the real files — including the failures, the reincidences, and the evolution of each rule as the system learned what it took to make a correction stick. The production case includes 11 scars and 8 hooks across four hook event types: `SessionStart`, `PreToolUse`, and `UserPromptSubmit`.

Key findings from the production dataset:

- **163 findings** across 4 categories: 37 repeated errors (A), 55 successful corrections (B), 29 false confidences (C), 42 metacognitive frictions (D)
- **Ratio B/A = 1.49** — for every repeated error, approximately 1.5 successful corrections. RIALTO, the project with the densest scar-like system (67+ numbered rules), had the highest correction density in the dataset
- **Rule shape predicts persistence**: binary rules leak at 17%, proportional/conditional rules leak at 75–100%
- **Verbal corrections with no physical support** have a measured escape rate of 100%

---

## Research

The companion paper is available in three places:

- **Full text**: [`research/paper.md`](research/paper.md) in this repository
- **Zenodo** (citable preprint with DOI): [doi:10.5281/zenodo.19555971](https://doi.org/10.5281/zenodo.19555971)
- **Web** (annotated, with commentary): [victordelpuerto.com/posts/lucy-syndrome/](https://victordelpuerto.com/posts/lucy-syndrome/)

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, scope rules, the scar/hook authoring process, and PR expectations. Bug reports and feature requests are welcome via the templates in [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/).

Release history lives in [CHANGELOG.md](CHANGELOG.md).

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

The research paper (`research/paper.md`) is © Victor Daniel Del Puerto Gauto, all rights reserved; included here to accompany the code. See [NOTICE.md](NOTICE.md) for full attribution.

---

## Author

Victor Daniel Del Puerto Gauto
[victordelpuerto.com](https://victordelpuerto.com) · [info@dgingenieriasrl.com](mailto:info@dgingenieriasrl.com)
