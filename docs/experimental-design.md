# Experimental Design — Lucy Syndrome Phase 2

> Formal specifications for testing conjectures H1–H5.  
> These conjectures are stated in the paper (Zenodo v3, Part III §4) as falsifiable claims.  
> This document adds minimum sample sizes, statistical designs, and success criteria.

---

## Prerequisites

All H1–H5 experiments require:
1. **Logging infrastructure active** — `fires.jsonl` populated by `log_scar_fire.py` (see [logging-schema.json](logging-schema.json))
2. **Minimum 4 weeks of baseline data** before interpreting trends
3. **Operator labeling** — `reviewed_by_human: true` on entries used for recurrence/prevention metrics

---

## H1: Scars reduce repeated errors ≥40% in fragile domains within 4 weeks

**Conjecture:** In domains where errors repeat frequently (fragile domains), active functional scars reduce recurrence rate by at least 40% compared to baseline (pre-scar state).

| Parameter | Specification |
|---|---|
| **n minimum** | 200–300 error opportunities |
| **Design** | Stepped-wedge: introduce scars sequentially across domains; each domain serves as its own control in the pre-scar period |
| **Primary metric** | `recurrence_rate` per domain per week |
| **Baseline** | Historical recurrence rate from dataset (163 findings, `cross-analysis.md`) or prospective pre-scar period of ≥2 weeks |
| **Success criterion** | ≥40% reduction in recurrence rate, p < 0.05 (two-tailed paired t-test across domains) |
| **Failure criterion** | Reduction < 40% or p ≥ 0.05 → revisit the 5 invariants; the scar design may not satisfy I1 or I3 |

**Practical note:** With ~10 hook-relevant tool calls per session and 1 session/day, 200 opportunities ≈ 20 days. 300 ≈ 30 days. This is achievable in 4–6 weeks of normal operation.

---

## H2: Binary rules persist >90%; proportional rules persist <40%, independent of support

**Conjecture:** The form of the rule — not the quality of its documentation — predicts whether it persists across sessions. Binary (yes/no) rules persist at >90% rate; proportional rules (X% of Y, balance A/B) persist at <40%, regardless of whether they have physical support (I2).

| Parameter | Specification |
|---|---|
| **n minimum** | ≥50 corrections per rule type (binary, proportional, conditional, verbal-only, structural) |
| **Design** | Observational categorization of incoming corrections; tag each correction with rule form at capture time |
| **Statistical method** | Chi-square test for independence between rule form and persistence outcome; logistic regression with rule form as predictor |
| **Primary metric** | Persistence rate (correction holds across 3+ subsequent sessions) by rule form category |
| **Success criterion** | Binary > 90%, proportional < 40%, statistically distinguishable (p < 0.01) |
| **Failure criterion** | No significant difference between rule forms → the persistence cliff described in the paper is not a stable predictor |

**Existing supporting evidence:** Table in `research/statistics.md` shows binary rules at 17% leak rate (83% persistence) and proportional at 80% leak rate (20% persistence), consistent with H2. This experiment formalizes and scales that observation.

---

## H3: Negative correlation between reference document size and correction fidelity

**Conjecture:** The larger the reference document consulted during a session, the lower the fidelity to operator corrections in the system prompt ("gravitational pull" effect). A reference spec of 550K characters exerts more pull than one of 50K.

| Parameter | Specification |
|---|---|
| **n minimum** | 400–600 task runs |
| **Design** | Factorial: vary document size (small/medium/large) × correction type (binary/proportional) × domain |
| **Primary metric** | Fidelity score: proportion of relevant outputs that correctly apply the operator correction |
| **Statistical method** | Linear regression: fidelity ~ log(document_size). Include domain as covariate. |
| **Success criterion** | Negative slope (r² > 0.3) with p < 0.05 |
| **Failure criterion** | No significant negative correlation → gravitational pull is not document-size-dependent; look for other predictors |

**Context:** The `cross-analysis.md` documents RIALTO's PBC (~550K chars) as a real-world example of this effect. This experiment operationalizes that observation with controlled variation.

---

## H4: Metacognitive friction (D) accounts for >70% of repeated errors (A); forcing uncertainty declaration breaks the cycle

**Conjecture:** Most repeated errors (category A) are preceded by a metacognitive friction event (category D) — the model generates without declaring uncertainty. If the operator inserts an "uncertainty gate" (forcing the model to declare confidence before generating), the A rate drops by >70%.

| Parameter | Specification |
|---|---|
| **n minimum** | 300–500 tasks |
| **Design** | A/B: treatment group uses uncertainty gate prompt ("Before generating X, state your confidence level and any open questions"); control group uses standard prompt |
| **Primary metric** | Type A error rate (repeated error) per session in each condition |
| **Secondary metric** | Ratio of D-type events preceding A-type events (should be >70% in control, lower in treatment) |
| **Statistical method** | Two-proportion z-test; treatment vs control A-rate |
| **Success criterion** | Reduction in A-rate > 70% in treatment vs control |
| **Failure criterion** | Reduction < 70% → D events are not the dominant A precursor, or uncertainty gates are insufficient |

**Existing supporting evidence:** `cross-analysis.md` §4 shows 42 D-type events correlate with 37 A-type errors (ratio ~1.14). Analysis of event pairs shows >80% of A-type errors had a D-type antecedent in the same or prior session. H4 tests whether *forcing* D-declaration prospectively reduces A.

---

## H5: Claude and ChatGPT show similar syndrome rates in comparable domains, different detectability

**Conjecture:** The Lucy Syndrome is architectural (not model-specific). Claude and ChatGPT show <15% difference in A-type error rates in the same domains. However, detectability (the rate at which the model produces signals that allow the operator to identify the syndrome) differs by >30%.

| Parameter | Specification |
|---|---|
| **n minimum** | ≥250 tasks per model (≥500 total) |
| **Design** | Cross-benchmark: same task corpus run on both models; operator blind to model during categorization |
| **Primary metric** | A-type error rate per model per domain |
| **Secondary metric** | D-type event rate (proxy for detectability — a model with more D events is "easier" to catch) |
| **Statistical method** | Two-proportion z-test for A-rate difference; two-proportion z-test for D-rate difference |
| **Success criterion** | A-rate difference < 15% AND D-rate difference > 30% |
| **Failure criterion** | A-rate difference > 15% → syndrome is partially model-specific; revisit architecture claim |

**Existing evidence:** `research/statistics.md` shows 11 ChatGPT-sourced findings with distribution within <5% of Claude across all 4 categories. H5 scales and formalizes this cross-platform check.

---

## Experiment Roadmap (12-week timeline from logging activation)

| Weeks | Milestone |
|---|---|
| 1–2 | Logging active; baseline data collection begins |
| 3–5 | First activation_rate data; identify scars with zero fires (adjust filters) |
| 6–8 | Sufficient data to run H2 (≥50 corrections categorized); preliminary H1 check |
| 9–10 | H1 formal evaluation if 200+ opportunities available; H4 A/B if feasible |
| 11–12 | First Phase 2 metrics report; H1 pass/fail decision; escalation policy review |

H3 and H5 require more setup (controlled document-size variation; cross-model benchmark) — target Month 2–3.

---

*Specification derived from Lucy Syndrome paper (Zenodo DOI: 10.5281/zenodo.19555971) and Deep Research report, 2026-04-25.*
