"""Tests for logging/log_scar_fire.py -- silent-failure JSONL logger."""
import json
import stat
import uuid
from datetime import datetime

import pytest

from conftest import load_module


@pytest.fixture()
def log_mod(tmp_path, monkeypatch):
    mod = load_module("logging/log_scar_fire.py", f"_lsf_{id(tmp_path)}")
    fires_path = tmp_path / "fires.jsonl"
    monkeypatch.setattr(mod, "_FIRES_FILE", fires_path)
    monkeypatch.setattr(mod, "_LOGS_DIR", tmp_path)
    return mod, fires_path


def _fire(mod, **overrides):
    defaults = dict(scar_id="scar_001", hook_id="hook_test",
                    event_type="PreToolUse", trigger_match="test match")
    defaults.update(overrides)
    mod.log_scar_fire(**defaults)


class TestHappyPath:
    def test_writes_one_line(self, log_mod):
        mod, path = log_mod
        _fire(mod)
        assert path.exists()
        assert len([l for l in path.read_text().splitlines() if l.strip()]) == 1

    def test_line_is_valid_json(self, log_mod):
        mod, path = log_mod
        _fire(mod)
        assert isinstance(json.loads(path.read_text().strip()), dict)

    def test_required_fields_present(self, log_mod):
        mod, path = log_mod
        _fire(mod)
        entry = json.loads(path.read_text().strip())
        for field in ("timestamp", "session_id", "event_id", "scar_id",
                      "hook_id", "event_type", "trigger_match", "payload_hash"):
            assert field in entry, f"Missing field: {field}"

    def test_scar_id_preserved(self, log_mod):
        mod, path = log_mod
        _fire(mod, scar_id="scar_007")
        assert json.loads(path.read_text().strip())["scar_id"] == "scar_007"

    def test_event_type_preserved(self, log_mod):
        mod, path = log_mod
        _fire(mod, event_type="SessionStart")
        assert json.loads(path.read_text().strip())["event_type"] == "SessionStart"

    def test_tool_name_preserved(self, log_mod):
        mod, path = log_mod
        _fire(mod, tool_name="Write")
        assert json.loads(path.read_text().strip())["tool_name"] == "Write"

    def test_reviewed_by_human_is_false(self, log_mod):
        mod, path = log_mod
        _fire(mod)
        assert json.loads(path.read_text().strip())["reviewed_by_human"] is False

    def test_severity_preserved(self, log_mod):
        mod, path = log_mod
        _fire(mod, severity="deny")
        assert json.loads(path.read_text().strip())["severity"] == "deny"


class TestTimestamp:
    def test_parseable_iso8601_with_tz(self, log_mod):
        mod, path = log_mod
        _fire(mod)
        ts = json.loads(path.read_text().strip())["timestamp"]
        dt = datetime.fromisoformat(ts)
        assert dt.tzinfo is not None

    def test_trigger_match_truncated_at_200(self, log_mod):
        mod, path = log_mod
        _fire(mod, trigger_match="x" * 300)
        stored = json.loads(path.read_text().strip())["trigger_match"]
        assert len(stored) <= 200


class TestPayloadHash:
    def test_starts_with_sha256(self, log_mod):
        mod, path = log_mod
        _fire(mod, payload_raw="hello world")
        assert json.loads(path.read_text().strip())["payload_hash"].startswith("sha256:")

    def test_deterministic_for_same_input(self, log_mod):
        mod, path = log_mod
        _fire(mod, payload_raw="same content")
        _fire(mod, payload_raw="same content")
        lines = path.read_text().strip().splitlines()
        h1 = json.loads(lines[0])["payload_hash"]
        h2 = json.loads(lines[1])["payload_hash"]
        assert h1 == h2

    def test_differs_for_different_inputs(self, log_mod):
        mod, path = log_mod
        _fire(mod, payload_raw="content A")
        _fire(mod, payload_raw="content B")
        lines = path.read_text().strip().splitlines()
        h1 = json.loads(lines[0])["payload_hash"]
        h2 = json.loads(lines[1])["payload_hash"]
        assert h1 != h2


class TestTokenEstimation:
    def test_nonnegative(self, log_mod):
        mod, path = log_mod
        _fire(mod, context_injected="a" * 400, system_message="b" * 200)
        assert json.loads(path.read_text().strip())["tokens_added"] >= 0

    def test_zero_when_empty(self, log_mod):
        mod, path = log_mod
        _fire(mod, context_injected="", system_message="")
        assert json.loads(path.read_text().strip())["tokens_added"] == 0

    def test_estimate_formula(self, log_mod):
        mod, path = log_mod
        _fire(mod, context_injected="a" * 400, system_message="b" * 400)
        tokens = json.loads(path.read_text().strip())["tokens_added"]
        assert tokens == max(0, (400 + 400) // 4)


class TestCriticidad:
    def test_default_is_media_for_unknown_scar(self, log_mod):
        mod, path = log_mod
        _fire(mod, scar_id="scar_unknown_xyz")
        assert json.loads(path.read_text().strip())["criticidad"] == "media"

    def test_override_critica(self, log_mod):
        mod, path = log_mod
        _fire(mod, criticidad="critica")
        assert json.loads(path.read_text().strip())["criticidad"] == "critica"

    def test_override_baja(self, log_mod):
        mod, path = log_mod
        _fire(mod, criticidad="baja")
        assert json.loads(path.read_text().strip())["criticidad"] == "baja"


class TestFileCreation:
    def test_creates_file_if_not_exists(self, log_mod):
        mod, path = log_mod
        assert not path.exists()
        _fire(mod)
        assert path.exists()

    def test_appends_multiple_calls(self, log_mod):
        mod, path = log_mod
        for i in range(3):
            _fire(mod, scar_id=f"scar_{i:03d}")
        assert len(path.read_text().strip().splitlines()) == 3

    def test_each_appended_line_valid_json(self, log_mod):
        mod, path = log_mod
        for i in range(5):
            _fire(mod, scar_id=f"scar_{i:03d}")
        for line in path.read_text().strip().splitlines():
            json.loads(line)


class TestSilentFailure:
    def test_permission_denied_does_not_raise(self, tmp_path, monkeypatch):
        mod = load_module("logging/log_scar_fire.py", f"_lsf_perm_{id(tmp_path)}")
        fires_path = tmp_path / "fires.jsonl"
        monkeypatch.setattr(mod, "_FIRES_FILE", fires_path)
        monkeypatch.setattr(mod, "_LOGS_DIR", tmp_path)
        tmp_path.chmod(stat.S_IRUSR | stat.S_IXUSR)
        try:
            _fire(mod)
        finally:
            tmp_path.chmod(0o755)

    def test_none_scar_id_does_not_raise(self, log_mod):
        mod, _ = log_mod
        mod.log_scar_fire(scar_id=None, hook_id="", event_type="", trigger_match="")


class TestLatency:
    def test_is_numeric_nonnegative(self, log_mod):
        import time
        mod, path = log_mod
        _fire(mod, start_time=time.time())
        entry = json.loads(path.read_text().strip())
        assert isinstance(entry["latency_ms"], (int, float))
        assert entry["latency_ms"] >= 0

    def test_none_start_does_not_raise(self, log_mod):
        mod, path = log_mod
        _fire(mod, start_time=None)
        assert json.loads(path.read_text().strip())["latency_ms"] >= 0


class TestIdentifiers:
    def test_session_id_is_8_hex_chars(self, log_mod):
        mod, path = log_mod
        _fire(mod)
        sid = json.loads(path.read_text().strip())["session_id"]
        assert len(sid) == 8
        int(sid, 16)

    def test_event_id_is_uuid(self, log_mod):
        mod, path = log_mod
        _fire(mod)
        eid = json.loads(path.read_text().strip())["event_id"]
        uuid.UUID(eid)

    def test_event_ids_are_unique(self, log_mod):
        mod, path = log_mod
        _fire(mod)
        _fire(mod)
        lines = path.read_text().strip().splitlines()
        ids = [json.loads(l)["event_id"] for l in lines]
        assert ids[0] != ids[1]
