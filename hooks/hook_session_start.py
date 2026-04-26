#!/usr/bin/env python3
"""
Hook SessionStart — Lucy Syndrome scarring system.

Scans the scar directory at session start and injects a summary of all
active scars (those whose frontmatter declares status != archived) as
additionalContext, so the model knows which corrections to apply.

Customization:
  - LUCY_SCAR_DIR env var overrides the default scar directory.
  - Default is `.claude/scarring/` relative to the current working dir.

Adding a new scar requires no edit to this hook — drop a `scar_*.md` file
with frontmatter (id, name, severity, status) into the scar dir.
"""
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_SCAR_DIR = ".claude/scarring"
SCAR_FILE_PATTERN = re.compile(r"^scar_[A-Za-z0-9_]+\.md$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """Extract YAML-ish key:value pairs from the leading frontmatter block."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm


def discover_scars(directory: Path) -> list[dict]:
    """Return active scars sorted by id, parsed from frontmatter."""
    if not directory.exists() or not directory.is_dir():
        return []
    scars: list[dict] = []
    for path in sorted(directory.iterdir()):
        if not path.is_file() or not SCAR_FILE_PATTERN.match(path.name):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        fm = parse_frontmatter(text)
        if fm.get("status", "active").lower() == "archived":
            continue
        scars.append({
            "id": fm.get("id") or path.stem,
            "name": fm.get("name", ""),
            "severity": fm.get("severity", "medium"),
            "file": path.name,
        })
    return scars


def build_context(scars: list[dict], scar_dir: str) -> str:
    if not scars:
        return (
            f"Scarring system active. No scar files found in {scar_dir}/. "
            "Drop a scar_*.md file there (see framework/scar_template.md) "
            "to make corrections persist across sessions."
        )
    lines = [f"Scarring system active. {len(scars)} scar(s) in {scar_dir}/:\n"]
    for s in scars:
        name = s["name"] or "(unnamed)"
        lines.append(f"- {s['id']} {name} [{s['severity']}] -- {s['file']}")
    lines.append(
        "\nBefore starting technical work, read the scar file relevant to the "
        "task. See SCARRING_INDEX.md for the full inventory and management policy."
    )
    return "\n".join(lines)


def main() -> None:
    scar_dir = os.environ.get("LUCY_SCAR_DIR") or DEFAULT_SCAR_DIR
    scars = discover_scars(Path(scar_dir))
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(scars, scar_dir),
        }
    }
    json.dump(output, sys.stdout)


if __name__ == "__main__":
    main()
