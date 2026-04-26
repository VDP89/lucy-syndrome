# Contributing to Lucy Syndrome

Thanks for your interest. This project is small and opinionated, so contributions are welcome but should fit the framework's grain. Read this once before opening a PR and you'll save us both time.

---

## What this repo is — and isn't

**It is** a framework for making LLM corrections persist via functional scars and Claude Code hooks, plus the reference implementation, plus a real production case study.

**It isn't** a general LLM agent toolkit, a memory system, a RAG framework, or a prompt-management library. PRs that pull the project in those directions will be politely declined.

---

## Setting up

```bash
git clone https://github.com/VDP89/lucy-syndrome.git
cd lucy-syndrome
pip install -e ".[test]"   # installs pytest + pytest-cov
pytest                      # 290 tests, ~1 second
```

CI runs the same suite on Python 3.10, 3.11, and 3.12 with a 70% coverage gate. The current floor is 98%.

---

## What kinds of changes are welcome

### Yes, please

- **Bug fixes** in installer, hooks, or logging
- **New generic hooks** in `hooks/` — must be domain-independent, stdlib-only, under ~100 lines, with tests
- **New generic scars** in `scars/` — must be domain-independent, follow the six-section template, reference an existing or new generic hook
- **Test coverage improvements** — especially for the bare-`except` branches in `logging/log_*.py`
- **Documentation fixes** — typos, broken links, clarification of confusing passages
- **Cross-platform fixes** — the installer is bash; pure-Python equivalent welcomed

### Maybe — open an issue first

- Restructuring the repo for PyPI/pipx distribution (architectural decision)
- Hooks for events beyond `SessionStart` / `PreToolUse` / `UserPromptSubmit` / `PostToolUse`
- A `lucy-syndrome` CLI that wraps `install.sh` in pure Python
- New top-level directories
- Changes to the JSON schema in `docs/logging-schema.json`

### No

- Domain-specific scars or hooks (those go in your own `examples/<your-case>/`, not the generic dirs)
- Python dependencies beyond stdlib for hooks (the installer must work on a fresh Python install with no pip availability)
- Removing or rewriting the production case in `examples/production-case/` — it's a snapshot of real usage and is preserved for fidelity
- Reformatting the research paper (`research/paper.md`) — it's an immutable companion document

---

## Adding a generic scar

1. Copy `framework/scar_template.md` to `scars/scar_NNN_descriptive_name.md` (use the next free number).
2. Fill in all six sections. The "What happened" section should describe a real incident — invented scars are weaker than scars rooted in actual failures, even if you anonymize.
3. Set `status: example` in the frontmatter so users know it's a reference, not their own scar.
4. If the scar needs an enforcement hook, add it in step 5 below.
5. Add at least one paragraph to `scars/README.md` explaining when this scar applies.

**A scar is too domain-specific if** any of these are true:
- It references a particular industry, company, or product
- The trigger uses paths or filenames that aren't broadly recognizable (e.g., `07_marca/`)
- The fix references tools or rituals that aren't widely available

When unsure, ask in an issue.

---

## Adding a generic hook

1. Copy `framework/hook_template.py` to `hooks/hook_descriptive_name.py`.
2. The hook must:
   - Read JSON from stdin via `json.load`, exit 0 silently on parse failure
   - Use only the Python standard library
   - Stay under ~100 lines
   - Exit 0 silently for non-matching invocations (the vast majority)
   - Emit JSON to stdout only when the trigger fires
   - Be wrapped in a `main()` function with `if __name__ == "__main__": main()` at the bottom (so tests can call it)
3. Add tests in `tests/test_hooks_generic.py` covering: trigger fires, trigger doesn't fire, malformed JSON, missing fields. Aim for 100% coverage of the new file.
4. If the hook calls `log_scar_fire()`, follow the pattern in `examples/production-case/hooks/hook_scar_001_docx.py`: import inside a `try/except`, guard the call with `if _log:`.

---

## Tests are required

Every PR that changes behavior must update or add tests. CI will reject anything that drops coverage below the gate. The fastest way to write a hook test is to copy a class from `tests/test_hooks_generic.py` and adapt the trigger payload.

Run before pushing:

```bash
pytest --cov=./logging --cov=./hooks --cov=examples/production-case/hooks \
       --cov-config=pyproject.toml --cov-report=term-missing
```

---

## Commit and PR conventions

**Commit messages**: short imperative subject, blank line, body explaining *why* not *what*. Prefixes used: `feat:`, `fix:`, `test:`, `chore:`, `docs:`.

```
fix: hook_session_start now reads scar dir dynamically

The hardcoded SCARS list drifted from the placeholder install.sh creates,
so SessionStart announced 3 scars that did not exist.
```

**PR title**: same shape as the commit subject. Keep under 70 characters.

**PR body**: use the template — summary, test plan, anything reviewer should know. If the PR fixes an issue, add `Closes #N`.

---

## Append-only policy on scars

Scars in this repo, the production case, and your own fork should never be deleted. If a scar becomes obsolete:

1. Mark it `status: archived` in the frontmatter
2. Add a dated note in the scar file explaining why
3. Keep the file in place

The dynamic `hook_session_start.py` skips archived scars automatically. The historical record stays, which is the point — Lucy Syndrome is partly about not forgetting why a rule existed.

---

## Reporting bugs / requesting features

Open an issue using the templates in `.github/ISSUE_TEMPLATE/`. For bugs, include the install path, Python version, and the exact stdin payload that reproduces it. For features, describe the failure mode in your own work that the feature would address.

---

## Code of conduct

Be respectful. Disagree by being more specific, not louder. The project is research-adjacent; thoughtful skepticism is welcome.

---

## License

By contributing, you agree your contributions are licensed under Apache 2.0, the same as the rest of the codebase. The research paper (`research/paper.md`) remains under its own copyright as documented in `NOTICE.md`.
