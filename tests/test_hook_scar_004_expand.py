"""
Deep coverage for examples/production-case/hooks/hook_scar_004_expand.py.

The existing TestHookScar004Expand in test_hooks_production.py only exercises
the trigger-phrase / empty-prompt branches via run_hook (which reads the real
MEMORY.md from $HOME and almost always finds nothing). These tests cover:

  - extract_keywords  (pure)
  - parse_memory_index (with synthetic MEMORY.md in tmp_path)
  - score_entries (pure)
  - build_context_message (pure, all three branches)
  - main()         (integration: stdin -> stdout, MEMORY_PATH monkeypatched)
"""
import io
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from conftest import load_module

HOOK_REL = "examples/production-case/hooks/hook_scar_004_expand.py"


@pytest.fixture()
def expand_mod(tmp_path, monkeypatch):
    """Load the hook module fresh and point MEMORY_PATH at tmp_path."""
    mod = load_module(HOOK_REL, f"_h004_{id(tmp_path)}")
    fake_memory = tmp_path / "MEMORY.md"
    monkeypatch.setattr(mod, "MEMORY_PATH", fake_memory)
    return mod, fake_memory


def _run_main(mod, prompt: str) -> tuple[dict | None, int | None]:
    """Drive mod.main() with a synthesized stdin payload."""
    payload = json.dumps({"prompt": prompt})
    stdout_buf = io.StringIO()

    def fake_exit(code=0):
        raise SystemExit(code)

    with (
        patch.object(mod.sys, "stdin", io.StringIO(payload)),
        patch.object(mod.sys, "stdout", stdout_buf),
        patch.object(mod.sys, "exit", side_effect=fake_exit),
    ):
        try:
            mod.main()
            text = stdout_buf.getvalue()
            return (json.loads(text) if text.strip() else None), None
        except SystemExit as e:
            return None, (int(e.code) if e.code is not None else 0)


# ---------------------------------------------------------------- #
# extract_keywords
# ---------------------------------------------------------------- #
class TestExtractKeywords:
    def test_empty_returns_empty_set(self, expand_mod):
        mod, _ = expand_mod
        assert mod.extract_keywords("") == set()

    def test_none_returns_empty_set(self, expand_mod):
        mod, _ = expand_mod
        assert mod.extract_keywords(None) == set()

    def test_lowercases(self, expand_mod):
        mod, _ = expand_mod
        kws = mod.extract_keywords("AUTHENTICATION strategy")
        assert "authentication" in kws
        assert "strategy" in kws

    def test_filters_short_tokens(self, expand_mod):
        mod, _ = expand_mod
        # MIN_KEYWORD_LEN = 4, so "abc" (3 chars) is dropped
        kws = mod.extract_keywords("abc database engineering")
        assert "abc" not in kws
        assert "database" in kws
        assert "engineering" in kws

    def test_filters_stopwords(self, expand_mod):
        mod, _ = expand_mod
        # "para", "como" are in STOPWORDS
        kws = mod.extract_keywords("para como database")
        assert "para" not in kws
        assert "como" not in kws
        assert "database" in kws

    def test_filters_admin_stopwords(self, expand_mod):
        mod, _ = expand_mod
        kws = mod.extract_keywords("cerramos sesion listo proyecto")
        # all three admin words are stopwords
        for w in ("cerramos", "sesion", "listo"):
            assert w not in kws

    def test_punctuation_split(self, expand_mod):
        mod, _ = expand_mod
        kws = mod.extract_keywords("authentication, database. tokens!")
        assert {"authentication", "database", "tokens"} <= kws

    def test_underscore_token_kept(self, expand_mod):
        mod, _ = expand_mod
        # regex r"[a-zA-Z_][a-zA-Z0-9_]*" allows underscore tokens
        kws = mod.extract_keywords("project_auth deployment")
        assert "project_auth" in kws


# ---------------------------------------------------------------- #
# parse_memory_index
# ---------------------------------------------------------------- #
class TestParseMemoryIndex:
    def test_missing_file_returns_empty(self, expand_mod):
        mod, fake = expand_mod
        # fake doesn't exist
        assert mod.parse_memory_index(fake) == []

    def test_parses_link_entry(self, expand_mod):
        mod, fake = expand_mod
        fake.write_text(
            "# Index\n"
            "- [Authentication Flow](project_auth.md) - login and session tokens\n",
            encoding="utf-8",
        )
        entries = mod.parse_memory_index(fake)
        assert len(entries) == 1
        assert entries[0]["file"] == "project_auth.md"
        assert "Authentication" in entries[0]["title"]
        assert "login" in entries[0]["hook"]

    def test_parses_bare_name_entry(self, expand_mod):
        mod, fake = expand_mod
        fake.write_text(
            "- project_database → schema migrations and backups\n",
            encoding="utf-8",
        )
        entries = mod.parse_memory_index(fake)
        assert len(entries) == 1
        assert entries[0]["file"] == "project_database.md"

    def test_skips_headers_and_blank_lines(self, expand_mod):
        mod, fake = expand_mod
        fake.write_text(
            "# Top header\n"
            "## Section\n"
            "\n"
            "- [Real](project_real.md) - hook\n"
            "\n",
            encoding="utf-8",
        )
        entries = mod.parse_memory_index(fake)
        assert len(entries) == 1
        assert entries[0]["file"] == "project_real.md"

    def test_skips_unparseable_lines(self, expand_mod):
        mod, fake = expand_mod
        fake.write_text(
            "random prose without a list marker\n"
            "- [Valid](project_valid.md) - real hook\n"
            "- not a valid entry line at all just text\n",
            encoding="utf-8",
        )
        entries = mod.parse_memory_index(fake)
        # only the well-formed entry should survive
        files = [e["file"] for e in entries]
        assert "project_valid.md" in files

    def test_keywords_combine_basename_title_hook(self, expand_mod):
        mod, fake = expand_mod
        fake.write_text(
            "- [Authentication](project_auth_strategy.md) - "
            "tokens and session refresh\n",
            encoding="utf-8",
        )
        entries = mod.parse_memory_index(fake)
        assert len(entries) == 1
        kw = entries[0]["keywords"]
        # basename "project_auth_strategy" -> "auth strategy" after prefix strip
        assert "auth" in kw
        assert "strategy" in kw
        # from title
        assert "authentication" in kw
        # from hook
        assert "tokens" in kw

    def test_unreadable_file_returns_empty(self, expand_mod, tmp_path):
        mod, _ = expand_mod
        # path that points to a directory (can't be read as text)
        directory = tmp_path / "subdir"
        directory.mkdir()
        assert mod.parse_memory_index(directory) == []

    def test_multiple_entries_preserved_in_order(self, expand_mod):
        mod, fake = expand_mod
        fake.write_text(
            "- [A](project_a.md) - first\n"
            "- [B](project_b.md) - second\n"
            "- [C](project_c.md) - third\n",
            encoding="utf-8",
        )
        entries = mod.parse_memory_index(fake)
        assert [e["file"] for e in entries] == [
            "project_a.md", "project_b.md", "project_c.md"
        ]


# ---------------------------------------------------------------- #
# score_entries
# ---------------------------------------------------------------- #
class TestScoreEntries:
    def test_no_overlap_returns_empty(self, expand_mod):
        mod, _ = expand_mod
        entries = [{"file": "a.md", "title": "A", "hook": "",
                    "keywords": {"alpha", "beta"}}]
        assert mod.score_entries(entries, {"gamma"}) == []

    def test_below_min_match_count_filtered(self, expand_mod):
        mod, _ = expand_mod
        # MIN_MATCH_COUNT = 2, so a single match is filtered out
        entries = [{"file": "a.md", "title": "A", "hook": "",
                    "keywords": {"alpha", "beta"}}]
        assert mod.score_entries(entries, {"alpha"}) == []

    def test_meets_min_match_count(self, expand_mod):
        mod, _ = expand_mod
        entries = [{"file": "a.md", "title": "A", "hook": "",
                    "keywords": {"alpha", "beta", "gamma"}}]
        result = mod.score_entries(entries, {"alpha", "beta"})
        assert len(result) == 1
        assert result[0]["score"] == 2
        assert result[0]["matched"] == ["alpha", "beta"]

    def test_sorted_by_score_descending(self, expand_mod):
        mod, _ = expand_mod
        entries = [
            {"file": "weak.md", "title": "W", "hook": "",
             "keywords": {"alpha", "beta"}},
            {"file": "strong.md", "title": "S", "hook": "",
             "keywords": {"alpha", "beta", "gamma", "delta"}},
        ]
        result = mod.score_entries(entries, {"alpha", "beta", "gamma", "delta"})
        assert [r["file"] for r in result] == ["strong.md", "weak.md"]

    def test_tie_broken_by_filename(self, expand_mod):
        mod, _ = expand_mod
        entries = [
            {"file": "zeta.md", "title": "Z", "hook": "",
             "keywords": {"alpha", "beta"}},
            {"file": "alpha.md", "title": "A", "hook": "",
             "keywords": {"alpha", "beta"}},
        ]
        result = mod.score_entries(entries, {"alpha", "beta"})
        # equal score -> alphabetical asc by file
        assert [r["file"] for r in result] == ["alpha.md", "zeta.md"]

    def test_matched_keywords_sorted(self, expand_mod):
        mod, _ = expand_mod
        entries = [{"file": "a.md", "title": "A", "hook": "",
                    "keywords": {"zeta", "alpha", "mu"}}]
        result = mod.score_entries(entries, {"zeta", "alpha", "mu"})
        assert result[0]["matched"] == ["alpha", "mu", "zeta"]


# ---------------------------------------------------------------- #
# build_context_message
# ---------------------------------------------------------------- #
class TestBuildContextMessage:
    def test_trigger_only_no_matches(self, expand_mod):
        mod, _ = expand_mod
        msg = mod.build_context_message("nuestro plan", [], trigger_hit=True)
        assert "scar_004 Etapa 0" in msg
        assert "frase-trigger" in msg
        # the indice-no-satisface tail line is always appended
        assert "indice MEMORY.md NO satisface" in msg

    def test_with_matches(self, expand_mod):
        mod, _ = expand_mod
        matches = [
            {"file": "project_auth.md", "title": "Auth",
             "hook": "tokens and session refresh", "keywords": set(),
             "matched": ["auth", "tokens"], "score": 2},
        ]
        msg = mod.build_context_message("auth tokens", matches, trigger_hit=True)
        assert "memoria persistida" in msg
        assert "project_auth.md" in msg
        assert "tokens and session refresh" in msg

    def test_caps_matches_at_max_results(self, expand_mod):
        mod, _ = expand_mod
        # MAX_RESULTS = 5; pass 7, only 5 should appear
        matches = [
            {"file": f"file_{i}.md", "title": f"T{i}",
             "hook": f"hook {i}", "keywords": set(),
             "matched": ["x", "y"], "score": 2}
            for i in range(7)
        ]
        msg = mod.build_context_message("anything", matches, trigger_hit=False)
        assert "file_0.md" in msg
        assert "file_4.md" in msg
        assert "file_5.md" not in msg
        assert "file_6.md" not in msg

    def test_truncates_long_hook_text(self, expand_mod):
        mod, _ = expand_mod
        long_hook = "A" * 200
        matches = [{"file": "f.md", "title": "T", "hook": long_hook,
                    "keywords": set(), "matched": ["x", "y"], "score": 2}]
        msg = mod.build_context_message("x y", matches, trigger_hit=False)
        # truncation kicks in past 90 chars and adds ellipsis
        assert "..." in msg

    def test_no_trigger_no_matches_still_has_tail(self, expand_mod):
        mod, _ = expand_mod
        # this combination is normally short-circuited in main(), but the
        # function itself should still produce the tail-only message.
        msg = mod.build_context_message("anything", [], trigger_hit=False)
        assert "indice MEMORY.md NO satisface" in msg


# ---------------------------------------------------------------- #
# main() integration
# ---------------------------------------------------------------- #
class TestMainIntegration:
    def test_invalid_json_exits_zero(self, expand_mod):
        mod, _ = expand_mod
        stdout_buf = io.StringIO()

        def fake_exit(code=0):
            raise SystemExit(code)

        with (
            patch.object(mod.sys, "stdin", io.StringIO("not json{{{")),
            patch.object(mod.sys, "stdout", stdout_buf),
            patch.object(mod.sys, "exit", side_effect=fake_exit),
        ):
            with pytest.raises(SystemExit) as exc:
                mod.main()
            assert exc.value.code == 0

    def test_empty_prompt_exits_silently(self, expand_mod):
        mod, _ = expand_mod
        out, code = _run_main(mod, "")
        assert out is None
        assert code == 0

    def test_no_trigger_no_matches_exits_silently(self, expand_mod):
        mod, fake = expand_mod
        # Empty MEMORY.md + benign prompt -> no trigger, no matches -> exit 0
        fake.write_text("# header only\n", encoding="utf-8")
        out, code = _run_main(mod, "ayudame con algo trivial sin contexto")
        assert out is None
        assert code == 0

    def test_trigger_phrase_emits_output(self, expand_mod):
        mod, fake = expand_mod
        fake.write_text("# empty\n", encoding="utf-8")
        out, _ = _run_main(mod, "como quedamos con el plan de la semana")
        assert out is not None
        assert "hookSpecificOutput" in out
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "frase-trigger" in ctx
        assert out["systemMessage"].startswith("scar_004 Etapa 0")

    def test_keyword_match_emits_output_and_lists_files(self, expand_mod):
        mod, fake = expand_mod
        fake.write_text(
            "- [Authentication](project_auth.md) - tokens and session refresh\n"
            "- [Database](project_database.md) - schema migrations\n",
            encoding="utf-8",
        )
        # two overlapping keywords with the auth entry: "authentication" + "tokens"
        out, _ = _run_main(mod, "explain authentication tokens please")
        assert out is not None
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "memoria persistida" in ctx
        assert "project_auth.md" in ctx
        # scar_004 system message reflects file count
        assert "expandir 1 archivo" in out["systemMessage"]

    def test_event_name_is_user_prompt_submit(self, expand_mod):
        mod, fake = expand_mod
        fake.write_text("# empty\n", encoding="utf-8")
        out, _ = _run_main(mod, "nuestra estrategia comercial")
        assert out["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
