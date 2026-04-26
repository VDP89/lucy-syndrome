"""Tests for hooks/ -- generic framework-level hooks."""
import io
import json
from unittest.mock import patch

import pytest

from conftest import load_module, run_hook, run_hook_raw, make_pretool


# hook_session_start ------------------------------------------------------------
class TestGenericSessionStart:
    HOOK = "hooks/hook_session_start.py"

    def test_always_produces_output(self):
        out, _ = run_hook(self.HOOK, {})
        assert out is not None

    def test_event_name_is_session_start(self):
        out, _ = run_hook(self.HOOK, {})
        assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"

    def test_context_mentions_scar(self):
        out, _ = run_hook(self.HOOK, {})
        assert "scar" in out["hookSpecificOutput"]["additionalContext"].lower()

    def test_context_is_string(self):
        out, _ = run_hook(self.HOOK, {})
        assert isinstance(out["hookSpecificOutput"]["additionalContext"], str)

    def test_output_structure_complete(self):
        out, _ = run_hook(self.HOOK, {})
        assert "hookSpecificOutput" in out
        hso = out["hookSpecificOutput"]
        assert "hookEventName" in hso
        assert "additionalContext" in hso


# hook_session_start -- dynamic scar discovery ---------------------------------
class TestSessionStartDiscovery:
    """Targets the new auto-discovery behavior."""

    @pytest.fixture()
    def mod(self):
        return load_module("hooks/hook_session_start.py", "_hss_discovery")

    def _scar(self, scar_id="scar_001", name="my_scar", severity="high",
              status="active", body="# scar\n\nbody.\n"):
        return (
            f"---\nid: {scar_id}\nname: {name}\nseverity: {severity}\n"
            f"status: {status}\n---\n\n{body}"
        )

    def test_parse_frontmatter_extracts_keys(self, mod):
        fm = mod.parse_frontmatter(
            "---\nid: scar_007\nname: foo\nseverity: high\n---\n\nbody"
        )
        assert fm == {"id": "scar_007", "name": "foo", "severity": "high"}

    def test_parse_frontmatter_no_block_returns_empty(self, mod):
        assert mod.parse_frontmatter("# just a markdown file") == {}

    def test_parse_frontmatter_empty_string(self, mod):
        assert mod.parse_frontmatter("") == {}

    def test_discover_missing_dir_returns_empty(self, mod, tmp_path):
        assert mod.discover_scars(tmp_path / "nonexistent") == []

    def test_discover_path_is_a_file_returns_empty(self, mod, tmp_path):
        f = tmp_path / "not_a_dir.md"
        f.write_text("hi", encoding="utf-8")
        assert mod.discover_scars(f) == []

    def test_discover_finds_scar_files(self, mod, tmp_path):
        (tmp_path / "scar_001_a.md").write_text(self._scar("scar_001", "a"),
                                                encoding="utf-8")
        (tmp_path / "scar_002_b.md").write_text(self._scar("scar_002", "b"),
                                                encoding="utf-8")
        scars = mod.discover_scars(tmp_path)
        assert [s["id"] for s in scars] == ["scar_001", "scar_002"]
        assert [s["name"] for s in scars] == ["a", "b"]

    def test_discover_skips_non_scar_files(self, mod, tmp_path):
        (tmp_path / "scar_001_a.md").write_text(self._scar("scar_001", "a"),
                                                encoding="utf-8")
        (tmp_path / "README.md").write_text("# readme", encoding="utf-8")
        (tmp_path / "scratch.md").write_text("# scratch", encoding="utf-8")
        (tmp_path / "SCARRING_INDEX.md").write_text("# idx", encoding="utf-8")
        scars = mod.discover_scars(tmp_path)
        assert [s["id"] for s in scars] == ["scar_001"]

    def test_discover_excludes_archived(self, mod, tmp_path):
        (tmp_path / "scar_001_a.md").write_text(
            self._scar("scar_001", "active_one", status="active"), encoding="utf-8")
        (tmp_path / "scar_002_b.md").write_text(
            self._scar("scar_002", "old_one", status="archived"), encoding="utf-8")
        scars = mod.discover_scars(tmp_path)
        assert [s["id"] for s in scars] == ["scar_001"]

    def test_discover_default_severity_when_missing(self, mod, tmp_path):
        (tmp_path / "scar_001_a.md").write_text(
            "---\nid: scar_001\nname: a\n---\n\nbody", encoding="utf-8")
        scars = mod.discover_scars(tmp_path)
        assert scars[0]["severity"] == "medium"

    def test_discover_falls_back_to_filename_id(self, mod, tmp_path):
        # no frontmatter at all -> id derived from filename stem
        (tmp_path / "scar_007_legacy.md").write_text(
            "no frontmatter\nbody only", encoding="utf-8")
        scars = mod.discover_scars(tmp_path)
        assert scars[0]["id"] == "scar_007_legacy"

    def test_build_context_no_scars_message(self, mod):
        ctx = mod.build_context([], ".claude/scarring")
        assert "No scar files found" in ctx
        assert ".claude/scarring" in ctx

    def test_build_context_lists_each_scar(self, mod):
        scars = [
            {"id": "scar_001", "name": "a", "severity": "high",
             "file": "scar_001_a.md"},
            {"id": "scar_002", "name": "b", "severity": "low",
             "file": "scar_002_b.md"},
        ]
        ctx = mod.build_context(scars, ".claude/scarring")
        assert "2 scar(s)" in ctx
        assert "scar_001 a [high]" in ctx
        assert "scar_002 b [low]" in ctx
        assert "SCARRING_INDEX.md" in ctx

    def test_main_uses_env_var_override(self, mod, tmp_path, monkeypatch):
        (tmp_path / "scar_001_env.md").write_text(
            self._scar("scar_001", "env_scar"), encoding="utf-8")
        monkeypatch.setenv("LUCY_SCAR_DIR", str(tmp_path))
        stdout = io.StringIO()
        with patch.object(mod.sys, "stdout", stdout):
            mod.main()
        out = json.loads(stdout.getvalue())
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "scar_001" in ctx
        assert "env_scar" in ctx

    def test_main_with_no_scars_still_emits_output(self, mod, tmp_path, monkeypatch):
        monkeypatch.setenv("LUCY_SCAR_DIR", str(tmp_path / "empty"))
        stdout = io.StringIO()
        with patch.object(mod.sys, "stdout", stdout):
            mod.main()
        out = json.loads(stdout.getvalue())
        assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
        assert "No scar files found" in out["hookSpecificOutput"]["additionalContext"]


# hook_example_review -----------------------------------------------------------
class TestGenericExampleReview:
    HOOK = "hooks/hook_example_review.py"

    def _py(self, n):
        return "x = 1\n" * n

    def test_201_line_py_fires(self):
        out, _ = run_hook(self.HOOK, make_pretool("Write", "module.py", self._py(201)))
        assert out is not None

    def test_50_line_py_no_fire(self):
        _, code = run_hook(self.HOOK, make_pretool("Write", "small.py", self._py(50)))
        assert code == 0

    def test_exactly_200_no_fire(self):
        _, code = run_hook(self.HOOK, make_pretool("Write", "edge.py", self._py(199)))
        assert code == 0

    def test_js_file_fires(self):
        out, _ = run_hook(self.HOOK, make_pretool("Write", "app.js", self._py(250)))
        assert out is not None

    def test_go_file_fires(self):
        out, _ = run_hook(self.HOOK, make_pretool("Write", "main.go", self._py(210)))
        assert out is not None

    def test_html_not_code_no_fire(self):
        _, code = run_hook(self.HOOK, make_pretool("Write", "page.html", self._py(500)))
        assert code == 0

    def test_context_shows_line_count(self):
        out, _ = run_hook(self.HOOK, make_pretool("Write", "big.py", self._py(250)))
        assert "lines" in out["hookSpecificOutput"]["additionalContext"]

    def test_context_mentions_review(self):
        out, _ = run_hook(self.HOOK, make_pretool("Write", "module.py", self._py(201)))
        assert "review" in out["hookSpecificOutput"]["additionalContext"].lower()

    def test_system_message_present(self):
        out, _ = run_hook(self.HOOK, make_pretool("Write", "module.py", self._py(201)))
        assert "systemMessage" in out

    def test_invalid_json_exits_cleanly(self):
        _, code = run_hook_raw(self.HOOK, "{bad json")
        assert code == 0

    def test_new_string_field_works(self):
        payload = {"tool_name": "Edit", "event": "PreToolUse",
                   "tool_input": {"file_path": "app.py", "new_string": "x = 1\n" * 201}}
        out, _ = run_hook(self.HOOK, payload)
        assert out is not None
