"""Tests for hooks/ -- generic framework-level hooks."""
import pytest
from conftest import run_hook, run_hook_raw, make_pretool


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
