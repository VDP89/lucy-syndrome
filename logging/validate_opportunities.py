#!/usr/bin/env python3
"""
validate_opportunities.py — Lucy Syndrome Phase 3: Opportunity validation.

Generates Markdown review reports and allows updating the validated field
in opportunities.jsonl via CLI.

Usage:
    python validate_opportunities.py --report
    python validate_opportunities.py --validate <event_id> --result true|false
    python validate_opportunities.py --validate-all true|false
    python validate_opportunities.py --stats
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_LOGS_DIR = Path(__file__).parent.parent / "logs"
_OPPORTUNITIES_FILE = _LOGS_DIR / "opportunities.jsonl"


def _load() -> list[dict]:
    if not _OPPORTUNITIES_FILE.exists():
        return []
    rows = []
    with _OPPORTUNITIES_FILE.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows


def _save(rows: list[dict]) -> None:
    with _OPPORTUNITIES_FILE.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _parse_bool(s: str) -> bool:
    return s.strip().lower() in ("true", "1", "yes")


def _validate_bool_arg(s: str, flag: str) -> bool:
    if s.strip().lower() not in ("true", "false", "1", "0", "yes", "no"):
        print(f"Error: {flag} must be true or false. Got: {s!r}")
        sys.exit(1)
    return _parse_bool(s)


def cmd_report(_args) -> None:
    rows = _load()
    pending = [r for r in rows if r.get("validated") is None]
    if not pending:
        print("No pending candidates. All opportunities are validated.")
        return

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = _LOGS_DIR / f"OPPORTUNITIES_PENDING_REVIEW_{date_str}.md"

    by_scar: dict[str, list[dict]] = {}
    for r in pending:
        by_scar.setdefault(r.get("scar_id", "unknown"), []).append(r)

    lines = [
        f"# Opportunities Pending Review — {date_str}",
        f"\n{len(pending)} of {len(rows)} candidates await validation.\n",
        "Validate each with:",
        "```",
        "python validate_opportunities.py --validate <event_id> --result true|false",
        "```\n---\n",
    ]
    for scar_id in sorted(by_scar):
        lines.append(f"## {scar_id} ({len(by_scar[scar_id])} pending)\n")
        for r in by_scar[scar_id]:
            eid = r.get("event_id", "?")
            lines += [
                f"### {eid}",
                f"- **Timestamp:** {r.get('timestamp', '?')}",
                f"- **Tool:** {r.get('tool_name', '?')}",
                f"- **Project:** {r.get('project_context', '?')}",
                f"- **Fired:** {r.get('fired', False)}",
                f"- **Notes:** {r.get('notes', '')}",
                f"\n  `python validate_opportunities.py --validate {eid} --result true`\n",
            ]
    lines.append(f"---\n*Generated {datetime.now(timezone.utc).isoformat()}*")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report: {out}\nPending: {len(pending)}/{len(rows)}")


def cmd_validate(args) -> None:
    result = _validate_bool_arg(args.result, "--result")
    rows = _load()
    now = datetime.now(timezone.utc).isoformat()
    matched = False
    for row in rows:
        if row.get("event_id") == args.validate:
            row["validated"] = result
            row["validated_at"] = now
            matched = True
            break
    if not matched:
        print(f"Error: event_id not found: {args.validate}")
        sys.exit(1)
    _save(rows)
    print(f"Updated {args.validate} -> validated={result}")


def cmd_validate_all(args) -> None:
    result = _validate_bool_arg(args.validate_all, "--validate-all")
    rows = _load()
    now = datetime.now(timezone.utc).isoformat()
    count = sum(
        (row.update({"validated": result, "validated_at": now}) or 1)
        for row in rows if row.get("validated") is None
    )
    _save(rows)
    print(f"Updated {count} candidates -> validated={result}")


def cmd_stats(_args) -> None:
    rows = _load()
    pending = sum(1 for r in rows if r.get("validated") is None)
    confirmed = sum(1 for r in rows if r.get("validated") is True)
    rejected = sum(1 for r in rows if r.get("validated") is False)
    fired = sum(1 for r in rows if r.get("fired") is True)
    print(f"\nTotal candidates:   {len(rows)}")
    print(f"  Pending:          {pending}")
    print(f"  Confirmed (real): {confirmed}")
    print(f"  Rejected (FP):    {rejected}")
    print(f"  Fired:            {fired}")
    if confirmed > 0:
        missed = sum(1 for r in rows if r.get("validated") is True and not r.get("fired"))
        cov = fired / (fired + missed) * 100 if (fired + missed) > 0 else 0
        print(f"  Confirmed missed: {missed}")
        print(f"  Coverage:         {cov:.1f}%")
    print()


def main() -> None:
    p = argparse.ArgumentParser(description="Validate Lucy Syndrome opportunity candidates.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--report", action="store_true")
    g.add_argument("--validate", metavar="EVENT_ID")
    g.add_argument("--validate-all", metavar="true|false")
    g.add_argument("--stats", action="store_true")
    p.add_argument("--result", metavar="true|false")
    args = p.parse_args()

    if args.report:
        cmd_report(args)
    elif args.validate:
        if not args.result:
            p.error("--validate requires --result true|false")
        cmd_validate(args)
    elif args.validate_all:
        cmd_validate_all(args)
    elif args.stats:
        cmd_stats(args)


if __name__ == "__main__":
    main()
