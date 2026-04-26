"""Shared fixtures and helpers for lucy-syndrome tests."""
import importlib.util
import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent


def load_module(rel_path: str, unique_name: str = None):
    """Import a module by file path, bypassing sys.modules and naming conflicts."""
    path = REPO_ROOT / rel_path
    name = unique_name or f"_lucy_{rel_path.replace('/', '_').replace('.', '_')}"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_hook(hook_rel_path: str, input_data: dict) -> tuple:
    """
    Execute a hook script (module-level) with mocked stdin/stdout/sys.exit.

    Returns (output_dict | None, exit_code | None).
    """
    input_json = json.dumps(input_data)
    stdout_buf = io.StringIO()
    hook_path = REPO_ROOT / hook_rel_path

    def fake_exit(code=0):
        raise SystemExit(code)

    with (
        patch("sys.stdin", io.StringIO(input_json)),
        patch("sys.stdout", stdout_buf),
        patch("sys.exit", side_effect=fake_exit),
    ):
        try:
            spec = importlib.util.spec_from_file_location(
                f"_hook_{hook_path.stem}_{id(input_data)}", hook_path
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            # For hooks that wrap logic in main() (e.g. hook_scar_004_expand)
            if hasattr(mod, "main") and callable(mod.main):
                mod.main()
            out = stdout_buf.getvalue()
            return (json.loads(out) if out.strip() else None), None
        except SystemExit as e:
            return None, (int(e.code) if e.code is not None else 0)


def run_hook_raw(hook_rel_path: str, raw_input: str) -> tuple:
    """Same as run_hook but with raw stdin string (for hooks using sys.stdin.read())."""
    stdout_buf = io.StringIO()
    hook_path = REPO_ROOT / hook_rel_path

    def fake_exit(code=0):
        raise SystemExit(code)

    with (
        patch("sys.stdin", io.StringIO(raw_input)),
        patch("sys.stdout", stdout_buf),
        patch("sys.exit", side_effect=fake_exit),
    ):
        try:
            spec = importlib.util.spec_from_file_location(
                f"_hook_{hook_path.stem}_{id(raw_input)}", hook_path
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "main") and callable(mod.main):
                mod.main()
            out = stdout_buf.getvalue()
            return (json.loads(out) if out.strip() else None), None
        except SystemExit as e:
            return None, (int(e.code) if e.code is not None else 0)


def make_pretool(tool_name: str, file_path: str, content: str) -> dict:
    """Build a standard PreToolUse hook payload."""
    return {
        "tool_name": tool_name,
        "event": "PreToolUse",
        "tool_input": {"file_path": file_path, "content": content},
    }
