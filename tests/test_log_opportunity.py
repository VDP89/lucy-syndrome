"""Tests for logging/log_opportunity.py."""
import json
import stat
import uuid
from datetime import datetime

import pytest

from conftest import load_module


@pytest.fixture()
def opp_mod(tmp_path, monkeypatch):
    mod = load_module("logging/log_opportunity.py", f"_lo_{id(tmp_path)}")
    opp_path = tmp_path / "opportunities.jsonl"
    monkeypatch.setattr(mod, "_OPPORTUNITIES_FILE", opp_path)
    return mod, opp_path


def _log(mod, **overrides):
    defaults = dict(scar_id="scar_002", session_id="abcd1234", event_type="PreToolUse")
    defaults.update(overrides)
    mod.log_opportunity(**defaults)


class TestHappyPath:
    def test_writes_one_line(self, opp_mod):
        mod, path = opp_mod
        _log(mod)
        assert path.exists()
        assert len([l for l in path.read_text().splitlines() if l.strip()]) == 1

    def test_line_is_valid_json(self, opp_mod):
        mod, path = opp_mod
        _log(mod)
        assert isinstance(json.loads(path.read_text().strip()), dict)

    def test_required_fields(self, opp_mod):
        mod, path = opp_mod
        _log(mod)
        entry = json.loads(path.read_text().strip())
        for field in ("timestamp", "session_id", "event_id", "scar_id",
                      "candidate", "fired", "source"):
            assert field in entry, f"Missing field: {field}"

    def test_candidate_is_true(self, opp_mod):
        mod, path = opp_mod
        _log(mod)
        assert json.loads(path.read_text().strip())["candidate"] is True

    def test_source_is_observer(self, opp_mod):
        mod, path = opp_mod
        _log(mod)
        assert json.loads(path.read_text().strip())["source"] == "observer"

    def test_fired_defaults_false(self, opp_mod):
        mod, path = opp_mod
        _log(mod)
        assert json.loads(path.read_text().strip())["fired"] is False

    def test_validated_defaults_none(self, opp_mod):
        mod, path = opp_mod
        _log(mod)
        assert json.loads(path.read_text().strip())["validated"] is None

    def test_scar_id_preserved(self, opp_mod):
        mod, path = opp_mod
        _log(mod, scar_id="scar_005")
        assert json.loads(path.read_text().strip())["scar_id"] == "scar_005"


class TestTimestamp:
    def test_parseable_iso8601(self, opp_mod):
        mod, path = opp_mod
        _log(mod)
        ts = json.loads(path.read_text().strip())["timestamp"]
        dt = datetime.fromisoformat(ts)
        assert dt.tzinfo is not None


class TestOptionalFields:
    def test_tool_name_preserved(self, opp_mod):
        mod, path = opp_mod
        _log(mod, tool_name="Write")
        assert json.loads(path.read_text().strip())["tool_name"] == "Write"

    def test_project_context_preserved(self, opp_mod):
        mod, path = opp_mod
        _log(mod, project_context="project_a")
        assert json.loads(path.read_text().strip())["project_context"] == "project_a"

    def test_notes_preserved(self, opp_mod):
        mod, path = opp_mod
        _log(mod, notes="code write 150L: app.py")
        assert "code write" in json.loads(path.read_text().strip())["notes"]

    def test_fired_true(self, opp_mod):
        mod, path = opp_mod
        _log(mod, fired=True)
        assert json.loads(path.read_text().strip())["fired"] is True

    def test_validated_true(self, opp_mod):
        mod, path = opp_mod
        _log(mod, validated=True)
        assert json.loads(path.read_text().strip())["validated"] is True


class TestFileCreation:
    def test_creates_file_if_not_exists(self, opp_mod):
        mod, path = opp_mod
        assert not path.exists()
        _log(mod)
        assert path.exists()

    def test_appends_multiple(self, opp_mod):
        mod, path = opp_mod
        _log(mod, scar_id="scar_001")
        _log(mod, scar_id="scar_002")
        assert len(path.read_text().strip().splitlines()) == 2

    def test_event_id_is_uuid(self, opp_mod):
        mod, path = opp_mod
        _log(mod)
        eid = json.loads(path.read_text().strip())["event_id"]
        uuid.UUID(eid)


class TestSilentFailure:
    def test_permission_denied_does_not_raise(self, tmp_path, monkeypatch):
        mod = load_module("logging/log_opportunity.py", f"_lo_perm_{id(tmp_path)}")
        opp_path = tmp_path / "opportunities.jsonl"
        monkeypatch.setattr(mod, "_OPPORTUNITIES_FILE", opp_path)
        tmp_path.chmod(stat.S_IRUSR | stat.S_IXUSR)
        try:
            _log(mod)
        finally:
            tmp_path.chmod(0o755)
