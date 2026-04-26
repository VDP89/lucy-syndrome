<!-- Thanks for contributing. Please skim CONTRIBUTING.md before opening
the PR, and fill in the sections below. PRs missing a test plan or
violating the scope rules in CONTRIBUTING.md may be asked for changes. -->

## Summary

<!-- What does this PR do, and why? Two or three sentences. -->

## Changes

<!-- Bullet list of the concrete changes. Mention which files. -->

-
-
-

## Test plan

<!-- How was this verified? Check the boxes that apply. -->

- [ ] `pytest --cov` passes locally
- [ ] Coverage did not drop below 70% (or, ideally, the previous floor)
- [ ] New code has tests in `tests/`
- [ ] If installer changed: ran `./install.sh /tmp/some-fresh-dir` and the smoke test reported OK
- [ ] If a hook changed: piped a representative JSON payload via `echo '...' | python <hook>` and inspected the output
- [ ] If docs changed: skimmed the rendered Markdown on GitHub

## Scope check (CONTRIBUTING.md)

- [ ] Change is domain-independent (or, if domain-specific, lives under `examples/<case>/`)
- [ ] No new runtime dependencies for hooks (stdlib only)
- [ ] If a scar was added, it follows the six-section template and `status: example`
- [ ] If a scar became obsolete, it was archived (`status: archived`) rather than deleted

## Related issues

<!-- "Closes #N" or "Refs #N" if applicable. -->

---

<!-- Reviewer note: leave the production case (`examples/production-case/`)
and the research paper (`research/paper.md`) untouched unless the PR is
explicitly about updating them. -->
