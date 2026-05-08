# Changelog

All notable changes to this project are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] — 2026-05-08

### Added

- **Phase 3 — Opportunity observer.** New hook `hook_opportunity_observer.py` (in `examples/production-case/hooks/`) that logs candidate opportunities to `opportunities.jsonl`, separate from the fires log. Provides the recall denominator that was missing in Phase 2: without observed opportunities, recall = fires / fires = 1.0 (trivially useless). With opportunities, recall becomes a real metric: e.g. `scar_010` shows 4 fires against 152 observations = 2.6% recall, which is actionable feedback for tuning the trigger threshold.
- **First derivative essay published.** *From Memory to Scar — Why More Context Did Not Solve LLM Correction Persistence* (May 2026). Available at [victordelpuerto.com/posts/from-memory-to-scar/](https://victordelpuerto.com/posts/from-memory-to-scar/). The essay extends the four-layer progression argument from the paper with a concrete example: Anthropic's Managed Agents Memory beta (released 2026-04-24) as Layer 3 industrialized — a packaged version of what the paper argues does not close the persistence gap on its own.
- **Production telemetry from 13 days of Phase E.** Cumulative numbers from 2026-04-25 (Phase E deployment) through 2026-05-08:
  - 359 fires logged across 7 active scars
  - 910 opportunities observed across 4 instrumented scars
  - Latency p50 = 29.2 ms, p99 = 390 ms, max = 506.9 ms
  - One scar (scar_004) has fired 197 times — the highest-frequency scar in the dataset, and the one that exposed the latency outlier (regex parse of memory index on every prompt).

### Changed

- **README updated** to reflect Phase E observed data instead of Phase 2 readiness claims. The previous text said "the nine Phase 2 metrics become computable" — they are now computed continuously and the numbers are real.
- **scar_004 calibration** documented in `examples/production-case/hooks/hook_scar_004_expand.py`. `MIN_MATCH_COUNT` raised from 1 to 2; stopwords list extended with administrative terms (`sesion`, `session`, `cerramos`, `abrir`, `guardar`, `despedir`, `terminar`, `finalizar`, `listo`, `hecho`). Reduces false positives in session-closing prompts that happened to share tokens with memory index entries.

### Documented (not new code, new findings)

- **Reincidence A3.1 (2026-04-15).** First post-publication reincidence of `scar_004` documented in operational use. The operator read the memory index (formal compliance with the scar) but did not expand the pointer files (functional non-compliance). The scar fired in form, failed in function. Filed at `02_ANALISIS/incidente_2026-04-15_expansion_vs_lectura.md` (referenced in the paper as a candidate for invariant I4.b).
- **Reincidence A3.2 (2026-04-22).** Second post-publication reincidence: while documenting the canonical AASHTO/Peltier pull-gravitational case, the agent committed a functionally equivalent error at session close (a stale relative-time reference to an entity that had been mutated within the same session). Distance from mutation to error: ~35 minutes / 33 turns. Filed at `02_ANALISIS/incidente_2026-04-22_pull_gravitacional_en_cierre.md`. Stronger evidence than A3.1: the framework was active, the canonical case was open in context, and the recurrence happened anyway. Confirms that without enforcement outside the model, even full awareness of the framework does not prevent recurrence.
- **AASHTO/Peltier canonical case.** Civil engineering example of pull-gravitational error (the AI applied AASHTO 93 to articulated pavement, where the correct method is Peltier — and invented a structural coefficient `a1 ≈ 0.25` for a method that has no experimental basis for that pavement type). Documented in detail at `02_ANALISIS/RELATORIO_CASO_AASHTO93_EMPEDRADO_FLUODER_2026-04-22.md` and shipped as the central case in the LinkedIn post of 2026-04-22.

### Notes

- **Phase E observability is the closing of invariant I5** ("refinable activation metric") in operational form. The metrics document (`docs/metrics.md`) defines the nine metrics; this release ships the data they are computed from.
- **Schema evolution caveat.** The first ~30 fires (April) lack the `opportunity` and `project_context` fields. Consumers of `fires.jsonl` should tolerate both formats. Field versioning will be addressed in a future release.
- **Hook deuda tecnica.** Internal audit identified ~20-25% boilerplate repetition across hooks, schema evolution without migration, and hardcoded paths in injected messages. These are not blockers for operation but justify a clean reimplementation in a sibling project (work in progress, separate from this repository to keep the academic citation surface stable).

### Not included in this release

- `scar_012` (canal_compartido_sin_briefing) — a critical-severity blocking hook that has been operational locally since 2026-04-30 but is withheld from public release because it contains specific commercial-negotiation context that cannot be sanitized without losing the testimonial value of the production case. The pattern (briefings must not travel through shared channels with external recipients) is generic and may appear as a sanitized cookbook entry in the sibling project.

---

## [1.2.0] — 2026-04-25

### Added
- Phase 2 logging via `log_scar_fire.py` — closes invariant I5.
- `framework/ARCHITECTURE.md` with Mermaid diagrams.
- Phase 2 implementation docs: `docs/metrics.md`, `docs/logging-schema.json`, `docs/escalation-policy.md`, `docs/experimental-design.md`.
- `install.sh` for bootstrap into external projects.

## [1.1.0] — 2026-04-13

### Added
- Zenodo DOI citation in README ([10.5281/zenodo.19555971](https://doi.org/10.5281/zenodo.19555971)).
- `CITATION.cff` for academic citation in CFF format.

## [1.0.0] — 2026-04-09

### Added
- Initial commit: 5 functional scars + 4 Claude Code hooks.
- Apache 2.0 license.
- Companion paper text in `research/paper.md`.
- `framework/scar_template.md` and `framework/hook_template.py`.

---

[1.3.0]: https://github.com/Vdp89/lucy-syndrome/releases/tag/v1.3.0
[1.2.0]: https://github.com/Vdp89/lucy-syndrome/releases/tag/v1.2.0
[1.1.0]: https://github.com/Vdp89/lucy-syndrome/releases/tag/v1.1.0
[1.0.0]: https://github.com/Vdp89/lucy-syndrome/releases/tag/v1.0.0
