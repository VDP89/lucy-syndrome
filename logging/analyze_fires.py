#!/usr/bin/env python3
"""
analyze_fires.py — Lucy Syndrome Phase 3: Metrics analyzer.

Reads fires.jsonl and opportunities.jsonl and computes 9 metrics per scar.

Usage:
    python analyze_fires.py
    python analyze_fires.py --period 7d
    python analyze_fires.py --period 30d
    python analyze_fires.py --period all
    python analyze_fires.py --scar scar_002

Prerequisites:
    fires.jsonl       — populated by log_scar_fire.py in each hook
    opportunities.jsonl — populated by log_opportunity.py in opportunity_observer

Both files live in .claude/scarring/logs/ (not committed to git).

Metrics:
    1. activation_rate      = fires / opportunities
    2. recurrence_rate      = outcome==error_repeated / opportunities
    3. prevention_rate      = outcome==prevented / fires
    4. false_positive_rate  = outcome==false_positive / fires
    5. leak_after_fire_rate = outcome==leaked / fires
    6. coverage             = fires / (fires + confirmed_missed_opportunities)
    7. latency_overhead_ms  = mean(latency_ms) across fires
    8. token_overhead       = mean(tokens_added) across fires
    9. severity_adjusted_harm = sum(criticidad_weight * harm_events) / fires
"""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

_LOGS_DIR = Path(__file__).parent.parent / "logs"
_FIRES_FILE = _LOGS_DIR / "fires.jsonl"
_OPPORTUNITIES_FILE = _LOGS_DIR / "opportunities.jsonl"

CRITICIDAD_WEIGHT = {"baja": 1, "media": 2, "alta": 3, "critica": 5}

ALL_SCARS = [
    "scar_001", "scar_002", "scar_003", "scar_004", "scar_005",
    "scar_006", "scar_007", "scar_008", "scar_009", "scar_010", "scar_011",
]


def _parse_ts(ts: str) -> datetime:
    try:
        dt = datetime.fromisoformat(ts)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def _period_cutoff(period: str) -> datetime:
    now = datetime.now(timezone.utc)
    if period == "7d":
        return now - timedelta(days=7)
    if period == "30d":
        return now - timedelta(days=30)
    return datetime.min.replace(tzinfo=timezone.utc)


def _load_jsonl(path: Path, cutoff: datetime) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                if _parse_ts(row.get("timestamp", "")) >= cutoff:
                    rows.append(row)
            except Exception:
                pass
    return rows


def compute_metrics(fires: list[dict], opportunities: list[dict], scar_filter: str | None) -> dict:
    scars = [scar_filter] if scar_filter else ALL_SCARS

    fires_by_scar: dict[str, list[dict]] = defaultdict(list)
    opps_by_scar: dict[str, list[dict]] = defaultdict(list)

    for f in fires:
        fires_by_scar[f.get("scar_id", "")].append(f)
    for o in opportunities:
        opps_by_scar[o.get("scar_id", "")].append(o)

    results = {}
    for scar_id in scars:
        f_list = fires_by_scar.get(scar_id, [])
        o_list = opps_by_scar.get(scar_id, [])
        n_fires = len(f_list)
        n_opps = len(o_list)

        recurrences = sum(1 for f in f_list if f.get("outcome") == "error_repeated")
        prevented = sum(1 for f in f_list if f.get("outcome") in ("prevented", "error_prevented"))
        false_pos = sum(1 for f in f_list if f.get("outcome") == "false_positive")
        leaks = sum(1 for f in f_list if f.get("outcome") in ("leaked", "error_despite_fire"))
        # Missed = validated=True opportunities that did NOT fire
        missed = sum(1 for o in o_list if o.get("validated") is True and not o.get("fired"))

        latencies = [f["latency_ms"] for f in f_list if f.get("latency_ms") is not None]
        tokens = [f["tokens_added"] for f in f_list if f.get("tokens_added") is not None]
        weight = CRITICIDAD_WEIGHT.get(
            f_list[0].get("criticidad", "media") if f_list else "media", 2
        )

        results[scar_id] = {
            "n_fires": n_fires,
            "n_opportunities": n_opps,
            "n_missed": missed,
            "activation_rate": n_fires / n_opps if n_opps > 0 else None,
            "recurrence_rate": recurrences / n_opps if n_opps > 0 else None,
            "prevention_rate": prevented / n_fires if n_fires > 0 else None,
            "false_positive_rate": false_pos / n_fires if n_fires > 0 else None,
            "leak_after_fire_rate": leaks / n_fires if n_fires > 0 else None,
            "coverage": n_fires / (n_fires + missed) if (n_fires + missed) > 0 else None,
            "latency_overhead_ms": sum(latencies) / len(latencies) if latencies else None,
            "token_overhead": sum(tokens) / len(tokens) if tokens else None,
            "severity_adjusted_harm": weight * (recurrences + leaks) / n_fires if n_fires > 0 else None,
        }
    return results


def _pct(v: float | None) -> str:
    return f"{v * 100:5.1f}%" if v is not None else "  n/a "


def _num(v: float | None, d: int = 1) -> str:
    return f"{v:.{d}f}" if v is not None else "n/a"


def print_table(metrics: dict, period: str) -> None:
    print(f"\n{'='*80}")
    print(f"  Lucy Syndrome — Scar Metrics  |  period: {period}")
    print(f"{'='*80}")
    print(f"{'Scar':<12} {'Fires':>6} {'Opps':>6} {'Missed':>7} "
          f"{'Activ%':>7} {'Cover%':>7} {'FP%':>6} {'Prev%':>6} "
          f"{'Lat(ms)':>8} {'Tok':>5}")
    print("-" * 80)

    totals: dict[str, float] = defaultdict(float)
    for scar_id in sorted(metrics):
        m = metrics[scar_id]
        if m["n_fires"] == 0 and m["n_opportunities"] == 0:
            continue
        print(f"{scar_id:<12} {m['n_fires']:>6} {m['n_opportunities']:>6} {m['n_missed']:>7} "
              f"{_pct(m['activation_rate']):>7} {_pct(m['coverage']):>7} "
              f"{_pct(m['false_positive_rate']):>6} {_pct(m['prevention_rate']):>6} "
              f"{_num(m['latency_overhead_ms']):>8} {_num(m['token_overhead'], 0):>5}")
        totals["fires"] += m["n_fires"]
        totals["opps"] += m["n_opportunities"]
        totals["missed"] += m["n_missed"]

    print("-" * 80)
    g_act = totals["fires"] / totals["opps"] if totals["opps"] > 0 else None
    g_cov = totals["fires"] / (totals["fires"] + totals["missed"]) if (totals["fires"] + totals["missed"]) > 0 else None
    print(f"{'GLOBAL':<12} {int(totals['fires']):>6} {int(totals['opps']):>6} "
          f"{int(totals['missed']):>7} {_pct(g_act):>7} {_pct(g_cov):>7}")
    print(f"{'='*80}\n")
    if totals["opps"] == 0:
        print("  NOTE: No opportunities recorded yet. See logging/opportunity_observer.py.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Lucy Syndrome scar metrics.")
    parser.add_argument("--period", default="all", choices=["7d", "30d", "all"])
    parser.add_argument("--scar", default=None)
    args = parser.parse_args()

    cutoff = _period_cutoff(args.period)
    fires = _load_jsonl(_FIRES_FILE, cutoff)
    opportunities = _load_jsonl(_OPPORTUNITIES_FILE, cutoff)
    print(f"  Loaded {len(fires)} fires, {len(opportunities)} opportunities")
    print_table(compute_metrics(fires, opportunities, args.scar), args.period)


if __name__ == "__main__":
    main()
