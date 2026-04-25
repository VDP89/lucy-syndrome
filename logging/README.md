# Logging — Lucy Syndrome Phase 3 (Hybrid Model)

This directory contains the logging infrastructure for the Lucy Syndrome framework.

## Architecture: Hybrid Fires + Opportunities

Phase 2 introduced `fires.jsonl` — a log of every hook activation. Phase 3 adds
`opportunities.jsonl` — a log of every context where a scar *should have had a chance to fire*.

```
fires.jsonl        → "the hook actually fired"          (precision signal)
opportunities.jsonl → "the hook should have fired here"  (recall denominator)
```

Without opportunities, coverage = fires / fires = 1.0 — trivially true and useless.
With opportunities, you can compute actual recall and identify missed catches.

---

## Files

| File | Purpose |
|---|---|
| `log_scar_fire.py` | Appends one entry to `fires.jsonl` per hook activation |
| `log_opportunity.py` | Appends one entry to `opportunities.jsonl` per detected opportunity |
| `opportunity_observer.py` | Hook that detects opportunities (register as PostToolUse notification) |
| `analyze_fires.py` | Reads both JSONL files and computes 9 metrics per scar |
| `validate_opportunities.py` | CLI to review and validate opportunity candidates |

Data files (`fires.jsonl`, `opportunities.jsonl`) are in `.gitignore` and never committed.

---

## Key Distinction: Opportunities vs Hook Triggers

Opportunity rules are intentionally **broader** than hook trigger thresholds:

| Scar | Hook fires when | Opportunity exists when |
|---|---|---|
| scar_002 | Code file > 200 lines | Any code file Write/Edit |
| scar_001 | Python script touches "docx" | Any `.docx` file written |
| scar_005 | Any Task dispatch | Any Task dispatch (same) |
| scar_010/011 | Write to deliverable path with bad patterns | Write to deliverable path |

This gap — hook threshold vs opportunity breadth — is where recall is lost.

---

## Data Flow

```
Claude Code session
  ↓ Write/Edit/Task tool call
  ├── hook fires (PreToolUse) → log_scar_fire.py → fires.jsonl
  └── observer fires (PostToolUse/notification) → log_opportunity.py → opportunities.jsonl

Weekly:
  analyze_fires.py → metrics table (stdout)
  validate_opportunities.py --report → review candidates
  validate_opportunities.py --validate <id> --result true|false → update records
```

---

## Hook integration — fires

```python
import sys, time
from pathlib import Path

_START = time.time()

try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "logs"))
    from log_scar_fire import log_scar_fire as _log
except Exception:
    _log = None

# ... hook logic ...

if _log:
    _log(
        scar_id="scar_001",
        hook_id="hook_scar_001_your_name",
        event_type="PreToolUse",
        trigger_match="file.py — keyword",
        severity="warn",
        tool_name=data.get("tool_name"),
        context_injected=_CONTEXT,
        system_message=_SYSMSG,
        payload_raw=content[:500],
        start_time=_START,
        project_context="project_a",  # optional Phase 3 field
    )
```

---

## Hook integration — opportunities

Register `opportunity_observer.py` as a PostToolUse hook (notification type) for
`Write|Edit|Task` events. It runs after the tool completes so it never blocks execution.

Settings.json entry (adapt path):
```json
{
  "hookEventName": "PostToolUse",
  "hooks": [{
    "type": "command",
    "command": "python .claude/scarring/hooks/hook_opportunity_observer.py"
  }]
}
```

---

## Metrics quick reference

Run `python analyze_fires.py --period 30d` for a full table. Key metrics:

| # | Metric | Formula | Auto? |
|---|---|---|---|
| 1 | activation_rate | fires / opportunities | ✓ |
| 2 | recurrence_rate | error_repeated / opportunities | manual |
| 3 | prevention_rate | prevented / fires | manual |
| 4 | false_positive_rate | false_positive / fires | manual |
| 5 | leak_after_fire_rate | leaked / fires | manual |
| 6 | **coverage** | fires / (fires + missed_opportunities) | semi (needs validation) |
| 7 | latency_overhead_ms | mean(latency_ms) | ✓ |
| 8 | token_overhead | mean(tokens_added) | ✓ |
| 9 | severity_adjusted_harm | Σ(weight × harm) / fires | manual |

Full spec: [`../docs/metrics.md`](../docs/metrics.md).

---

## Schema

`fires.jsonl` entries follow [`../docs/logging-schema.json`](../docs/logging-schema.json) (ScarFireEvent).  
`opportunities.jsonl` entries follow the OpportunityEvent schema in the same file.

---

*Phase 3 specification — 2026-04-25. Compatible with Lucy Syndrome Zenodo v3 (DOI: 10.5281/zenodo.19555971).*
