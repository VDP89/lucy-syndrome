"""
Tests for logging/validate_opportunities.py.

This CLI mutates opportunities.jsonl in-place — happy path, idempotency,
corrupt-input handling and stats output all need coverage.
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from conftest import load_module


@pytest.fixture()
def vmod(tmp_path, monkeypatch):
    """Load validate_opportunities with _OPPORTUNITIES_FILE pointing at tmp_path."""
    mod = load_module("logging/validate_opportunities.py", f"_vop_{id(tmp_path)}")
    opp_path = tmp_path / "opportunities.jsonl"
    monkeypatch.setattr(mod, "_OPPORTUNITIES_FILE", opp_path)
    monkeypatch.setattr(mod, "_LOGS_DIR", tmp_path)
    return mod, opp_path


def _row(event_id="evt-1", scar_id="scar_002", validated=None, fired=False, **extra):
    base = {
        "timestamp": "2026-04-25T10:00:00+00:00",
        "session_id": "abcd1234",
        "event_id": event_id,
        "scar_id": scar_id,
        "candidate": True,
        "source": "observer",
        "validated": validated,
        "fired": fired,
        "tool_name": "Write",
        "project_context": "project_a",
        "notes": "test note",
    }
    base.update(extra)
    return base


def _write_rows(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------- #
# _load / _save
# ---------------------------------------------------------------- #
class TestLoad:
    def test_missing_file_returns_empty(self, vmod):
        mod, _ = vmod
        assert mod._load() == []

    def test_loads_existing_rows(self, vmod):
        mod, path = vmod
        _write_rows(path, [_row("a"), _row("b")])
        rows = mod._load()
        assert len(rows) == 2
        assert {r["event_id"] for r in rows} == {"a", "b"}

    def test_skips_blank_lines(self, vmod):
        mod, path = vmod
        path.write_text(
            json.dumps(_row("a")) + "\n\n  \n" + json.dumps(_row("b")) + "\n",
            encoding="utf-8",
        )
        rows = mod._load()
        assert len(rows) == 2

    def test_corrupt_lines_silently_skipped(self, vmod):
        mod, path = vmod
        path.write_text(
            "not json\n"
            + json.dumps(_row("a")) + "\n"
            + "{broken json\n"
            + json.dumps(_row("b")) + "\n",
            encoding="utf-8",
        )
        rows = mod._load()
        assert [r["event_id"] for r in rows] == ["a", "b"]


class TestSave:
    def test_round_trip(self, vmod):
        mod, path = vmod
        rows = [_row("a"), _row("b", validated=True)]
        mod._save(rows)
        loaded = mod._load()
        assert len(loaded) == 2
        assert loaded[1]["validated"] is True

    def test_preserves_unicode(self, vmod):
        mod, path = vmod
        rows = [_row("a", notes="acción está documentada")]
        mod._save(rows)
        text = path.read_text(encoding="utf-8")
        assert "acción" in text


# ---------------------------------------------------------------- #
# _parse_bool / _validate_bool_arg
# ---------------------------------------------------------------- #
class TestParseBool:
    @pytest.mark.parametrize("s,expected", [
        ("true", True), ("TRUE", True), ("1", True), ("yes", True),
        ("false", False), ("0", False), ("no", False), ("", False),
    ])
    def test_parse(self, vmod, s, expected):
        mod, _ = vmod
        assert mod._parse_bool(s) is expected


class TestValidateBoolArg:
    def test_accepts_true(self, vmod):
        mod, _ = vmod
        assert mod._validate_bool_arg("true", "--result") is True

    def test_accepts_false(self, vmod):
        mod, _ = vmod
        assert mod._validate_bool_arg("false", "--result") is False

    def test_rejects_garbage(self, vmod, capsys):
        mod, _ = vmod
        with pytest.raises(SystemExit) as exc:
            mod._validate_bool_arg("maybe", "--result")
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "--result" in captured.out
        assert "must be true or false" in captured.out


# ---------------------------------------------------------------- #
# cmd_validate (single event)
# ---------------------------------------------------------------- #
class _Args:
    """Minimal stand-in for argparse Namespace."""
    def __init__(self, **kw):
        self.__dict__.update(kw)


class TestCmdValidate:
    def test_happy_path_marks_validated_true(self, vmod):
        mod, path = vmod
        _write_rows(path, [_row("a"), _row("b")])
        mod.cmd_validate(_Args(validate="a", result="true"))
        rows = mod._load()
        target = next(r for r in rows if r["event_id"] == "a")
        assert target["validated"] is True
        assert "validated_at" in target
        # untouched row stays None
        other = next(r for r in rows if r["event_id"] == "b")
        assert other["validated"] is None

    def test_marks_validated_false(self, vmod):
        mod, path = vmod
        _write_rows(path, [_row("a")])
        mod.cmd_validate(_Args(validate="a", result="false"))
        assert mod._load()[0]["validated"] is False

    def test_idempotent_revalidation(self, vmod):
        mod, path = vmod
        _write_rows(path, [_row("a")])
        mod.cmd_validate(_Args(validate="a", result="true"))
        mod.cmd_validate(_Args(validate="a", result="true"))
        rows = mod._load()
        assert len(rows) == 1
        assert rows[0]["validated"] is True

    def test_event_id_not_found_exits_1(self, vmod, capsys):
        mod, path = vmod
        _write_rows(path, [_row("a")])
        with pytest.raises(SystemExit) as exc:
            mod.cmd_validate(_Args(validate="ghost", result="true"))
        assert exc.value.code == 1
        out = capsys.readouterr().out
        assert "ghost" in out

    def test_invalid_result_exits_1(self, vmod):
        mod, path = vmod
        _write_rows(path, [_row("a")])
        with pytest.raises(SystemExit) as exc:
            mod.cmd_validate(_Args(validate="a", result="banana"))
        assert exc.value.code == 1


# ---------------------------------------------------------------- #
# cmd_validate_all
# ---------------------------------------------------------------- #
class TestCmdValidateAll:
    def test_validates_all_pending(self, vmod):
        mod, path = vmod
        _write_rows(path, [_row("a"), _row("b"), _row("c", validated=True)])
        mod.cmd_validate_all(_Args(validate_all="true"))
        rows = mod._load()
        # all three end up True (already-True one is left alone, but two get set)
        assert sum(1 for r in rows if r["validated"] is True) == 3

    def test_does_not_overwrite_already_validated(self, vmod):
        mod, path = vmod
        _write_rows(path, [_row("a", validated=False), _row("b")])  # one rejected, one pending
        mod.cmd_validate_all(_Args(validate_all="true"))
        rows = mod._load()
        rejected = next(r for r in rows if r["event_id"] == "a")
        pending_now = next(r for r in rows if r["event_id"] == "b")
        assert rejected["validated"] is False  # untouched
        assert pending_now["validated"] is True

    def test_invalid_arg_exits_1(self, vmod):
        mod, _ = vmod
        with pytest.raises(SystemExit) as exc:
            mod.cmd_validate_all(_Args(validate_all="banana"))
        assert exc.value.code == 1


# ---------------------------------------------------------------- #
# cmd_stats
# ---------------------------------------------------------------- #
class TestCmdStats:
    def test_empty_file(self, vmod, capsys):
        mod, _ = vmod
        mod.cmd_stats(_Args())
        out = capsys.readouterr().out
        assert "Total candidates:" in out
        assert "0" in out

    def test_counts_by_validation_state(self, vmod, capsys):
        mod, path = vmod
        _write_rows(path, [
            _row("a", validated=None),
            _row("b", validated=True, fired=True),
            _row("c", validated=True, fired=False),
            _row("d", validated=False),
        ])
        mod.cmd_stats(_Args())
        out = capsys.readouterr().out
        assert "Pending:" in out
        assert "Confirmed (real): 2" in out
        assert "Rejected (FP):    1" in out
        assert "Fired:            1" in out

    def test_coverage_percent_when_confirmed_present(self, vmod, capsys):
        mod, path = vmod
        # 1 fired + 1 confirmed-but-not-fired -> coverage = 50%
        _write_rows(path, [
            _row("a", validated=True, fired=True),
            _row("b", validated=True, fired=False),
        ])
        mod.cmd_stats(_Args())
        out = capsys.readouterr().out
        assert "Coverage:" in out
        assert "50.0%" in out


# ---------------------------------------------------------------- #
# cmd_report
# ---------------------------------------------------------------- #
class TestCmdReport:
    def test_no_pending_short_circuits(self, vmod, capsys):
        mod, path = vmod
        _write_rows(path, [_row("a", validated=True)])
        mod.cmd_report(_Args())
        out = capsys.readouterr().out
        assert "All opportunities are validated" in out
        # no report file written
        assert not list(Path(mod._LOGS_DIR).glob("OPPORTUNITIES_PENDING_REVIEW_*.md"))

    def test_writes_markdown_report(self, vmod, capsys):
        mod, path = vmod
        _write_rows(path, [
            _row("evt-aaa", scar_id="scar_002"),
            _row("evt-bbb", scar_id="scar_004"),
        ])
        mod.cmd_report(_Args())
        out = capsys.readouterr().out
        assert "Report:" in out
        # one report markdown file created in _LOGS_DIR
        reports = list(Path(mod._LOGS_DIR).glob("OPPORTUNITIES_PENDING_REVIEW_*.md"))
        assert len(reports) == 1
        body = reports[0].read_text(encoding="utf-8")
        assert "evt-aaa" in body
        assert "evt-bbb" in body
        assert "scar_002" in body
        assert "scar_004" in body

    def test_groups_by_scar(self, vmod):
        mod, path = vmod
        _write_rows(path, [
            _row("a", scar_id="scar_002"),
            _row("b", scar_id="scar_002"),
            _row("c", scar_id="scar_004"),
        ])
        mod.cmd_report(_Args())
        body = next(Path(mod._LOGS_DIR).glob("OPPORTUNITIES_PENDING_REVIEW_*.md")).read_text()
        # scar_002 group should announce 2 pending
        assert "scar_002 (2 pending)" in body
        assert "scar_004 (1 pending)" in body


# ---------------------------------------------------------------- #
# main() argparse routing
# ---------------------------------------------------------------- #
class TestMain:
    def _run_main(self, mod, argv):
        with patch.object(sys, "argv", ["validate_opportunities.py"] + argv):
            mod.main()

    def test_main_dispatches_stats(self, vmod, capsys):
        mod, _ = vmod
        self._run_main(mod, ["--stats"])
        assert "Total candidates:" in capsys.readouterr().out

    def test_main_dispatches_report(self, vmod, capsys):
        mod, path = vmod
        _write_rows(path, [_row("a")])
        self._run_main(mod, ["--report"])
        assert "Report:" in capsys.readouterr().out

    def test_main_dispatches_validate(self, vmod, capsys):
        mod, path = vmod
        _write_rows(path, [_row("a")])
        self._run_main(mod, ["--validate", "a", "--result", "true"])
        out = capsys.readouterr().out
        assert "Updated a" in out
        assert mod._load()[0]["validated"] is True

    def test_main_validate_without_result_errors(self, vmod, capsys):
        mod, path = vmod
        _write_rows(path, [_row("a")])
        with pytest.raises(SystemExit):
            self._run_main(mod, ["--validate", "a"])

    def test_main_dispatches_validate_all(self, vmod, capsys):
        mod, path = vmod
        _write_rows(path, [_row("a")])
        self._run_main(mod, ["--validate-all", "true"])
        assert mod._load()[0]["validated"] is True
