"""
Coverage for the logging side-effect path in logging/opportunity_observer.py.

The observer module-level code does:
    sys.path.insert(0, ".../logs")
    from log_opportunity import log_opportunity as _log_opp

In the standard test runs `_log_opp` is None (import fails), so the for-loop
that actually writes to opportunities.jsonl never executes. To cover lines
156-170 we inject a fake `log_opportunity` module into sys.modules BEFORE
loading the observer, then assert it was called per detected opportunity.
"""
import importlib.util
import io
import json
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent
HOOK_PATH = REPO_ROOT / "logging" / "opportunity_observer.py"


def _run_observer_with_fake_logger(payload: dict) -> tuple[list[dict], str, int | None]:
    """
    Execute opportunity_observer.py with a fake `log_opportunity` module.

    Returns: (calls, stdout_text, exit_code)
        calls: list of kwargs each `_log_opp` invocation received
        stdout_text: raw stdout content
        exit_code: SystemExit code if the script exited, else None
    """
    calls: list[dict] = []

    def fake_log_opportunity(**kwargs):
        calls.append(kwargs)

    fake_mod = types.ModuleType("log_opportunity")
    fake_mod.log_opportunity = fake_log_opportunity

    stdout_buf = io.StringIO()
    raw = json.dumps(payload)

    def fake_exit(code=0):
        raise SystemExit(code)

    # save & restore sys.modules state
    original = sys.modules.get("log_opportunity")
    sys.modules["log_opportunity"] = fake_mod
    try:
        with (
            patch("sys.stdin", io.StringIO(raw)),
            patch("sys.stdout", stdout_buf),
            patch("sys.exit", side_effect=fake_exit),
        ):
            try:
                spec = importlib.util.spec_from_file_location(
                    f"_obs_{id(payload)}", HOOK_PATH
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return calls, stdout_buf.getvalue(), None
            except SystemExit as e:
                return calls, stdout_buf.getvalue(), int(e.code) if e.code is not None else 0
    finally:
        if original is not None:
            sys.modules["log_opportunity"] = original
        else:
            sys.modules.pop("log_opportunity", None)


def _payload(tool="Write", file_path="app.py", content="x = 1", event="PreToolUse"):
    return {
        "tool_name": tool,
        "event": event,
        "tool_input": {"file_path": file_path, "content": content},
    }


# ---------------------------------------------------------------- #
# Logging side-effect — single opportunity
# ---------------------------------------------------------------- #
class TestSingleOpportunityLogged:
    def test_code_write_invokes_logger_once(self):
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="src/app.py", content="x = 1\n" * 5)
        )
        assert len(calls) == 1
        assert calls[0]["scar_id"] == "scar_002"

    def test_logger_receives_required_fields(self):
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="src/app.py", content="x = 1")
        )
        assert calls
        kw = calls[0]
        for field in ("scar_id", "session_id", "event_type", "tool_name",
                      "context_hash", "project_context", "notes", "fired"):
            assert field in kw, f"Missing kwarg: {field}"

    def test_fired_kwarg_is_false(self):
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="src/app.py", content="x = 1")
        )
        assert calls[0]["fired"] is False

    def test_session_id_is_8_hex_chars(self):
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="src/app.py", content="x = 1")
        )
        sid = calls[0]["session_id"]
        assert len(sid) == 8
        int(sid, 16)  # must be valid hex

    def test_context_hash_starts_with_sha256(self):
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="src/app.py", content="x = 1")
        )
        assert calls[0]["context_hash"].startswith("sha256:")

    def test_event_type_propagated(self):
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(event="PostToolUse", file_path="src/app.py", content="x = 1")
        )
        assert calls[0]["event_type"] == "PostToolUse"


# ---------------------------------------------------------------- #
# Multiple opportunities — both scar_010 and scar_011 fire
# ---------------------------------------------------------------- #
class TestMultipleOpportunitiesLogged:
    def test_deliverable_md_logs_two(self):
        # path matches "landing" -> scar_010 + .md ext -> scar_011
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="output/landing.md", content="# title")
        )
        scar_ids = [c["scar_id"] for c in calls]
        assert "scar_010" in scar_ids
        assert "scar_011" in scar_ids

    def test_deliverable_non_text_only_logs_scar_010(self):
        # path matches "landing" but extension .pdf is not in TEXT set -> only scar_010
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="output/landing.pdf", content="binary")
        )
        scar_ids = [c["scar_id"] for c in calls]
        assert scar_ids == ["scar_010"]


# ---------------------------------------------------------------- #
# project_context detection
# ---------------------------------------------------------------- #
class TestProjectContextDetection:
    def test_project_a_detected_in_path(self):
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="project_a/src/app.py", content="x = 1")
        )
        assert calls[0]["project_context"] == "project_a"

    def test_project_b_detected_in_content(self):
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="src/app.py", content="// ref: proj-b deployment")
        )
        assert calls[0]["project_context"] == "project_b"

    def test_unknown_falls_back_to_other(self):
        calls, _, _ = _run_observer_with_fake_logger(
            _payload(file_path="src/app.py", content="totally unrelated content")
        )
        assert calls[0]["project_context"] == "other"


# ---------------------------------------------------------------- #
# Output contract
# ---------------------------------------------------------------- #
class TestOutputContract:
    def test_emits_empty_dict_on_match(self):
        _, stdout, _ = _run_observer_with_fake_logger(
            _payload(file_path="src/app.py", content="x = 1")
        )
        assert json.loads(stdout) == {}

    def test_no_match_no_logger_call(self):
        calls, _, code = _run_observer_with_fake_logger(
            _payload(file_path="/tmp/notes.txt", content="hello")
        )
        assert calls == []
        assert code == 0
