# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The Zenodo DOI [`10.5281/zenodo.19555971`](https://doi.org/10.5281/zenodo.19555971) cites the initial 1.0 release; subsequent releases below are additive improvements over that snapshot.

---

## [1.2.0] -- 2026-04-26

### Added

- `CONTRIBUTING.md` describing how to add scars, hooks, and tests, plus the project's scope rules.
- `.github/ISSUE_TEMPLATE/{bug_report,feature_request}.md` and `.github/PULL_REQUEST_TEMPLATE.md`.
- CI / coverage / Python-version badges in the README.
- 135 new tests across `tests/test_hook_scar_004_expand.py`, `tests/test_validate_opportunities.py`, `tests/test_opportunity_observer_logging.py`, `tests/test_hooks_edge_cases.py`, and expansions of `tests/test_analyze_fires.py` and `tests/test_hooks_generic.py`.
- Smoke test in `install.sh` that pipes minimal payloads through the freshly-installed hooks and reports OK / FAIL.

### Changed

- `hooks/hook_session_start.py` now discovers scars dynamically by scanning the scar directory and parsing each `scar_*.md` frontmatter. The previous hardcoded `SCARS = [...]` list is gone. `LUCY_SCAR_DIR` env var overrides the default `.claude/scarring/`.
- `install.sh` auto-creates `.claude/settings.json` from the example when none exists; if a settings file is already present it is preserved untouched and a `.example` reference is copied alongside.
- `framework/settings.json.example` no longer references hooks that don't ship in this repo.
- `pyproject.toml` removed `validate_opportunities.py` from the coverage `omit` list (now fully tested).

### Fixed

- `Vdp89` -> `VDP89` capitalization in the GitHub URLs in `README.md` and `CITATION.cff`.
- Duplicate "step 4." in the installer's Next Steps output.
- `framework/settings.json.example` referenced `hook_batch_coverage.py` and `hook_expand_memory.py`, which don't exist; with the `2>/dev/null || true` guard around each command, copying the example into a real `settings.json` produced silent failures.
- `hooks/hook_session_start.py` advertised three example scar IDs that the installer never created.

### Coverage

- Total: 83% -> **98%** (line + branch)
- Tests: 155 -> **290**
- All production hooks: 98-100%
- `validate_opportunities.py`: 0% (omitted) -> **99%**

---

## [1.1.0] -- 2026-04-25

### Added

- Initial test suite (`tests/`) with 155 tests and CI workflow on Python 3.10 / 3.11 / 3.12 (`b1550d8`, `923f17f`).
- `pyproject.toml` declaring the package metadata and pytest configuration.

---

## [1.0.0] -- 2026-04-25

Initial release accompanying the Zenodo deposit.

### Added

- Functional scars framework (`framework/`, `scars/`, `hooks/`).
- Production case study (`examples/production-case/`) with 11 scars and 8 hooks from a civil engineering operation.
- Phase 2 logging (`logging/log_scar_fire.py`) and Phase 3 hybrid fires+opportunities model (`logging/log_opportunity.py`, `logging/opportunity_observer.py`, `logging/analyze_fires.py`, `logging/validate_opportunities.py`).
- `install.sh` bootstrap script.
- Companion research paper (`research/paper.md`), documentation under `docs/` (logging schema, metrics, escalation policy, experimental design), and `framework/ARCHITECTURE.md` with Mermaid diagrams.

---

[1.2.0]: https://github.com/VDP89/lucy-syndrome/releases/tag/v1.2.0
[1.1.0]: https://github.com/VDP89/lucy-syndrome/compare/da76901...923f17f
[1.0.0]: https://github.com/VDP89/lucy-syndrome/tree/da76901
