# Logging — Lucy Syndrome Phase 2

`log_scar_fire.py` is the append-only JSONL logger that closes **I5** (the fifth persistence invariant): *a scar must have a refinable activation metric*.

Without this module, hook fires leave no trace. With it, every fire writes one line to `fires.jsonl`, enabling the nine Phase 2 metrics defined in [`../docs/metrics.md`](../docs/metrics.md).

---

## How it works

Each hook calls `log_scar_fire()` right before emitting its output. The function:

1. Measures hook execution time (`latency_ms`) from the `start_time` the hook recorded at entry
2. Estimates tokens injected (`tokens_added`) from the context string lengths
3. Hashes the trigger content (`payload_hash`) for reproducibility without logging raw data
4. Derives `session_id` and `project_id` from cwd + date hashes — no sensitive paths stored
5. Writes one JSON object to `fires.jsonl` (append-only, one object per line)

All errors are caught silently. The logger **never** breaks the hook.

---

## Installation

`install.sh` copies this file to `.claude/scarring/logs/log_scar_fire.py` in your project.

Fires are written to `.claude/scarring/logs/fires.jsonl`, which is in `.gitignore`.

---

## Hook integration pattern

```python
import sys
import time
from pathlib import Path

_START = time.time()

# Import logger — fails silently if not yet installed
try:
    sys.path.insert(0, str(Path(__file__).parent.parent / "logs"))
    from log_scar_fire import log_scar_fire as _log
except Exception:
    _log = None

# ... hook logic ...

# Right before json.dump(output, sys.stdout):
if _log:
    _log(
        scar_id="scar_001",
        hook_id="hook_scar_001_your_name",
        event_type="PreToolUse",          # or SessionStart / UserPromptSubmit
        trigger_match="file.py — keyword", # what matched (<200 chars)
        severity="warn",
        tool_name=data.get("tool_name"),   # None for SessionStart/UserPromptSubmit
        context_injected=_CONTEXT,         # the additionalContext string
        system_message=_SYSMSG,            # the systemMessage string
        payload_raw=content[:500],         # raw trigger content for hashing
        start_time=_START,
    )
```

---

## Schema

All 18 required fields follow [`../docs/logging-schema.json`](../docs/logging-schema.json).

| Field | Source | Notes |
|---|---|---|
| `timestamp` | auto | ISO 8601 with local timezone |
| `session_id` | auto | sha256(cwd + date)[:8] |
| `event_id` | auto | UUID v4 |
| `scar_id` | caller | `scar_NNN` pattern (schema). Use `infra_NNN` for non-scar hooks |
| `hook_id` | caller | filename without `.py` |
| `hook_version` | caller | default `"1.0.0"` |
| `model` | auto | env var `CLAUDE_MODEL` or `"unknown"` |
| `project_id` | auto | sha256(cwd)[:8] |
| `event_type` | caller | SessionStart / PreToolUse / UserPromptSubmit |
| `tool_name` | caller | tool that fired the hook; `None` for session events |
| `trigger_match` | caller | matched fragment, truncated to 200 chars |
| `latency_ms` | auto | measured from `start_time` |
| `tokens_added` | auto | estimated as `(len(context) + len(sysmsg)) // 4` |
| `severity` | caller | default `"warn"` |
| `outcome` | default `"unknown"` | operator sets after review |
| `criticidad` | auto | from `_CRITICIDAD_MAP` or caller override |
| `payload_hash` | auto | sha256 of `payload_raw` or `trigger_match` |
| `reviewed_by_human` | default `false` | operator sets to `true` after review |
| `notes` | optional | operator annotation |

---

## Reviewing fires

`fires.jsonl` is append-only. To review and annotate:

1. Open the file (one JSON object per line)
2. For each entry, set `reviewed_by_human: true` and update `outcome`:
   - `"prevented"` — the hook fired and the error did not occur
   - `"leaked"` — the hook fired but the error occurred anyway
   - `"false_positive"` — the hook fired but the error was not imminent
3. Add `notes` as needed

The `analyze_fires.py` script (in development) will compute the nine metrics from this data.

---

## Non-conformant scar IDs

The schema pattern for `scar_id` is `^scar_[0-9]{3}$`. Two hook types deviate:

- **Session-start hooks** (`event_type: SessionStart`) may use `scar_id: "session_start"` — useful for session counting via unique `session_id` values
- **Infrastructure hooks** (Dropbox mirror warnings, etc.) use `scar_id: "infra_NNN"` — these are not scars but produce operationally useful fire records

`analyze_fires.py` will filter these by prefix when computing per-scar metrics.
