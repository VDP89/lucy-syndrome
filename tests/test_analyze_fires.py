"""Tests for logging/analyze_fires.py -- metrics computation."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from conftest import load_module

@pytest.fixture()
def analyze_mod():
    return load_module("logging/analyze_fires.py", "_analyze_fires")


def make_fire(scar_id="scar_001", outcome="unknown", criticidad="media",
              latency_ms=10.0, tokens_added=100, timestamp=None):
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    return {"timestamp": ts, "scar_id": scar_id, "outcome": outcome,
            "criticidad": criticidad, "latency_ms": latency_ms,
            "tokens_added": tokens_added}


def make_opp(scar_id="scar_001", validated=None, fired=False, timestamp=None):
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    return {"timestamp": ts, "scar_id": scar_id, "validated": validated, "fired": fired}


class TestEmptyInputs:
    def test_empty_returns_dict(self, analyze_mod):
        results = analyze_mod.compute_metrics([], [], None)
        assert isinstance(results, dict)

    def test_empty_metrics_are_none(self, analyze_mod):
        results = analyze_mod.compute_metrics([], [], None)
        for m in results.values():
            assert m["activation_rate"] is None

    def test_returns_all_scars_by_default(self, analyze_mod):
        results = analyze_mod.compute_metrics([], [], None)
        for scar in analyze_mod.ALL_SCARS:
            assert scar in results


class TestActivationRate:
    def test_zero_fires_one_opp_is_zero(self, analyze_mod):
        results = analyze_mod.compute_metrics([], [make_opp("scar_001")], "scar_001")
        assert results["scar_001"]["activation_rate"] == 0.0

    def test_one_fire_one_opp_is_one(self, analyze_mod):
        results = analyze_mod.compute_metrics(
            [make_fire("scar_001")], [make_opp("scar_001")], "scar_001")
        assert results["scar_001"]["activation_rate"] == 1.0

    def test_one_fire_two_opps_is_half(self, analyze_mod):
        results = analyze_mod.compute_metrics(
            [make_fire("scar_001")],
            [make_opp("scar_001"), make_opp("scar_001")],
            "scar_001")
        assert results["scar_001"]["activation_rate"] == 0.5

    def test_no_opps_returns_none(self, analyze_mod):
        results = analyze_mod.compute_metrics([make_fire("scar_001")], [], "scar_001")
        assert results["scar_001"]["activation_rate"] is None


class TestPreventionRate:
    def test_one_prevented_of_one_fire(self, analyze_mod):
        fires = [make_fire("scar_001", outcome="prevented")]
        results = analyze_mod.compute_metrics(fires, [], "scar_001")
        assert results["scar_001"]["prevention_rate"] == 1.0

    def test_zero_fires_returns_none(self, analyze_mod):
        results = analyze_mod.compute_metrics([], [], "scar_001")
        assert results["scar_001"]["prevention_rate"] is None

    def test_error_prevented_counts(self, analyze_mod):
        fires = [make_fire("scar_001", outcome="error_prevented")]
        results = analyze_mod.compute_metrics(fires, [], "scar_001")
        assert results["scar_001"]["prevention_rate"] == 1.0


class TestFalsePositiveRate:
    def test_half_false_positive(self, analyze_mod):
        fires = [make_fire("scar_001", outcome="false_positive"),
                 make_fire("scar_001", outcome="unknown")]
        results = analyze_mod.compute_metrics(fires, [], "scar_001")
        assert results["scar_001"]["false_positive_rate"] == 0.5

    def test_no_false_positives(self, analyze_mod):
        fires = [make_fire("scar_001", outcome="prevented")]
        results = analyze_mod.compute_metrics(fires, [], "scar_001")
        assert results["scar_001"]["false_positive_rate"] == 0.0


class TestLeakRate:
    def test_leaked_outcome(self, analyze_mod):
        fires = [make_fire("scar_001", outcome="leaked")]
        results = analyze_mod.compute_metrics(fires, [], "scar_001")
        assert results["scar_001"]["leak_after_fire_rate"] == 1.0

    def test_error_despite_fire_counts(self, analyze_mod):
        fires = [make_fire("scar_001", outcome="error_despite_fire")]
        results = analyze_mod.compute_metrics(fires, [], "scar_001")
        assert results["scar_001"]["leak_after_fire_rate"] == 1.0


class TestCoverage:
    def test_fires_with_no_missed_is_one(self, analyze_mod):
        results = analyze_mod.compute_metrics([make_fire("scar_001")], [], "scar_001")
        assert results["scar_001"]["coverage"] == 1.0

    def test_fires_with_one_missed_is_half(self, analyze_mod):
        fires = [make_fire("scar_001")]
        opps = [make_opp("scar_001", validated=True, fired=False)]
        results = analyze_mod.compute_metrics(fires, opps, "scar_001")
        assert results["scar_001"]["coverage"] == 0.5

    def test_unvalidated_opps_not_missed(self, analyze_mod):
        fires = [make_fire("scar_001")]
        opps = [make_opp("scar_001", validated=None, fired=False)]
        results = analyze_mod.compute_metrics(fires, opps, "scar_001")
        assert results["scar_001"]["coverage"] == 1.0


class TestLatencyAndTokens:
    def test_mean_latency(self, analyze_mod):
        fires = [make_fire("scar_001", latency_ms=10),
                 make_fire("scar_001", latency_ms=20)]
        results = analyze_mod.compute_metrics(fires, [], "scar_001")
        assert results["scar_001"]["latency_overhead_ms"] == 15.0

    def test_mean_tokens(self, analyze_mod):
        fires = [make_fire("scar_001", tokens_added=100),
                 make_fire("scar_001", tokens_added=200)]
        results = analyze_mod.compute_metrics(fires, [], "scar_001")
        assert results["scar_001"]["token_overhead"] == 150.0

    def test_no_fires_latency_none(self, analyze_mod):
        results = analyze_mod.compute_metrics([], [], "scar_001")
        assert results["scar_001"]["latency_overhead_ms"] is None


class TestScarFilter:
    def test_filter_single_scar(self, analyze_mod):
        fires = [make_fire("scar_001"), make_fire("scar_002")]
        results = analyze_mod.compute_metrics(fires, [], "scar_001")
        assert list(results.keys()) == ["scar_001"]

    def test_no_filter_returns_all(self, analyze_mod):
        results = analyze_mod.compute_metrics([], [], None)
        assert set(results.keys()) == set(analyze_mod.ALL_SCARS)


class TestJsonlLoading:
    def test_malformed_lines_skipped(self, analyze_mod, tmp_path):
        f = tmp_path / "fires.jsonl"
        ts = datetime.now(timezone.utc).isoformat()
        good = json.dumps({"timestamp": ts, "scar_id": "scar_001",
                           "latency_ms": 5, "tokens_added": 10,
                           "outcome": "unknown", "criticidad": "media"})
        f.write_text("not json\n" + good + "\n{broken\n", encoding="utf-8")
        cutoff = analyze_mod._period_cutoff("all")
        rows = analyze_mod._load_jsonl(f, cutoff)
        assert len(rows) == 1

    def test_missing_file_returns_empty(self, analyze_mod, tmp_path):
        cutoff = analyze_mod._period_cutoff("all")
        rows = analyze_mod._load_jsonl(tmp_path / "nonexistent.jsonl", cutoff)
        assert rows == []


class TestPeriodCutoff:
    def test_all_is_far_past(self, analyze_mod):
        cutoff = analyze_mod._period_cutoff("all")
        assert cutoff.year < 2000

    def test_7d_is_approx_7_days_ago(self, analyze_mod):
        cutoff = analyze_mod._period_cutoff("7d")
        now = datetime.now(timezone.utc)
        assert 6 <= (now - cutoff).days <= 8

    def test_30d_is_approx_30_days_ago(self, analyze_mod):
        cutoff = analyze_mod._period_cutoff("30d")
        now = datetime.now(timezone.utc)
        assert 29 <= (now - cutoff).days <= 31


class TestParseTs:
    def test_valid_iso_with_tz(self, analyze_mod):
        dt = analyze_mod._parse_ts("2026-01-15T10:30:00+00:00")
        assert dt.year == 2026

    def test_invalid_returns_min(self, analyze_mod):
        dt = analyze_mod._parse_ts("not a timestamp")
        assert dt.year == datetime.min.year

    def test_naive_ts_gets_utc(self, analyze_mod):
        dt = analyze_mod._parse_ts("2026-01-15T10:30:00")
        assert dt.tzinfo is not None
