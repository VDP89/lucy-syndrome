"""
Edge-case coverage for production hooks (P3 gaps from coverage report).

Covers:
  - the `_log()` call sites in every hook (which are skipped when the
    optional `log_scar_fire` import fails — i.e., always, in standard tests)
  - hook_scar_011 branches: bak/preview skip, wrong-ext exit, empty content,
    8-unique-word break in the dedup loop
  - hook_scar_010 branches: /.claude/ skip path
  - hook_scar_005: stdin.read() raising
  - hook_dropbox_mirror_warn: empty stdin -> env/cwd fallback
"""
import importlib.util
import io
import json
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent


def _run_with_fake_log(hook_rel: str, raw_input: str | dict) -> tuple[list[dict], str, int | None]:
    """
    Run a hook with a fake `log_scar_fire` module so the `_log()` branches
    actually execute.

    Returns (log_calls, stdout, exit_code).
    """
    log_calls: list[dict] = []

    def fake_log_scar_fire(**kwargs):
        log_calls.append(kwargs)

    fake_mod = types.ModuleType("log_scar_fire")
    fake_mod.log_scar_fire = fake_log_scar_fire

    raw = raw_input if isinstance(raw_input, str) else json.dumps(raw_input)
    stdout_buf = io.StringIO()

    def fake_exit(code=0):
        raise SystemExit(code)

    saved = sys.modules.get("log_scar_fire")
    sys.modules["log_scar_fire"] = fake_mod
    try:
        with (
            patch("sys.stdin", io.StringIO(raw)),
            patch("sys.stdout", stdout_buf),
            patch("sys.exit", side_effect=fake_exit),
        ):
            try:
                hook_path = REPO_ROOT / hook_rel
                spec = importlib.util.spec_from_file_location(
                    f"_p3_{hook_path.stem}_{id(raw_input)}", hook_path
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                # hook_scar_004_expand wraps logic in main()
                if hasattr(mod, "main") and callable(mod.main):
                    mod.main()
                return log_calls, stdout_buf.getvalue(), None
            except SystemExit as e:
                return log_calls, stdout_buf.getvalue(), int(e.code) if e.code is not None else 0
    finally:
        if saved is not None:
            sys.modules["log_scar_fire"] = saved
        else:
            sys.modules.pop("log_scar_fire", None)


def _pretool(tool="Write", file_path="x.py", content="", **extra):
    body = {
        "tool_name": tool,
        "event": "PreToolUse",
        "tool_input": {"file_path": file_path, "content": content},
    }
    body.update(extra)
    return body


# ---------------------------------------------------------------- #
# scar_001 — _log call site
# ---------------------------------------------------------------- #
class TestScar001LogCallSite:
    HOOK = "examples/production-case/hooks/hook_scar_001_docx.py"

    def test_log_called_when_docx_in_py(self):
        calls, _, _ = _run_with_fake_log(
            self.HOOK, _pretool(file_path="gen.py", content="from docx import Document"),
        )
        assert len(calls) == 1
        assert calls[0]["scar_id"] == "scar_001"
        assert "gen.py" in calls[0]["trigger_match"]


# ---------------------------------------------------------------- #
# scar_002 — _log call site
# ---------------------------------------------------------------- #
class TestScar002LogCallSite:
    HOOK = "examples/production-case/hooks/hook_scar_002_size.py"

    def test_log_called_for_long_py(self):
        calls, _, _ = _run_with_fake_log(
            self.HOOK, _pretool(file_path="big.py", content="x = 1\n" * 250),
        )
        assert len(calls) == 1
        assert calls[0]["scar_id"] == "scar_002"
        assert "lines" in calls[0]["trigger_match"]


# ---------------------------------------------------------------- #
# scar_004 — _log call site
# ---------------------------------------------------------------- #
class TestScar004LogCallSite:
    HOOK = "examples/production-case/hooks/hook_scar_004_expand.py"

    def test_log_called_on_trigger_phrase(self):
        # trigger phrase fires; the real MEMORY.md may or may not exist on disk,
        # but the hook still calls _log with the trigger summary.
        calls, _, _ = _run_with_fake_log(
            self.HOOK, {"prompt": "como quedamos con la base que construimos"},
        )
        assert len(calls) == 1
        assert calls[0]["scar_id"] == "scar_004"


# ---------------------------------------------------------------- #
# scar_005 — stdin.read failure + _log call site
# ---------------------------------------------------------------- #
class TestScar005:
    HOOK = "examples/production-case/hooks/hook_scar_005_subagent.py"

    def test_log_called_unconditionally(self):
        calls, _, _ = _run_with_fake_log(self.HOOK, "{}")
        assert len(calls) == 1
        assert calls[0]["scar_id"] == "scar_005"
        assert calls[0]["tool_name"] == "Task"

    def test_stdin_read_failure_swallowed(self):
        """The bare except around sys.stdin.read() (lines 26-27) must not crash."""
        log_calls: list[dict] = []
        fake_mod = types.ModuleType("log_scar_fire")
        fake_mod.log_scar_fire = lambda **kw: log_calls.append(kw)

        class ExplodingStdin:
            def read(self):
                raise OSError("simulated pipe error")

        stdout_buf = io.StringIO()
        saved = sys.modules.get("log_scar_fire")
        sys.modules["log_scar_fire"] = fake_mod
        try:
            with (
                patch("sys.stdin", ExplodingStdin()),
                patch("sys.stdout", stdout_buf),
            ):
                hook_path = REPO_ROOT / self.HOOK
                spec = importlib.util.spec_from_file_location(
                    f"_p3_s005_explode", hook_path
                )
                mod = importlib.util.module_from_spec(spec)
                # must not raise
                spec.loader.exec_module(mod)
            # the hook still emits its output despite stdin error
            assert json.loads(stdout_buf.getvalue())["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
            assert len(log_calls) == 1
        finally:
            if saved is not None:
                sys.modules["log_scar_fire"] = saved
            else:
                sys.modules.pop("log_scar_fire", None)


# ---------------------------------------------------------------- #
# scar_010 — extra exit branches + _log call site
# ---------------------------------------------------------------- #
class TestScar010:
    HOOK = "examples/production-case/hooks/hook_scar_010_no_cerrar_puertas.py"

    def test_log_called_on_match(self):
        calls, _, _ = _run_with_fake_log(self.HOOK,
            _pretool(file_path="07_marca/brand.md", content="DG no es una empresa cualquiera."))
        assert len(calls) == 1
        assert calls[0]["scar_id"] == "scar_010"

    def test_claude_internal_path_skipped(self):
        # `/.claude/` short-circuit (line 75)
        _, stdout, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="/.claude/scratch/brand_notes.md",
                     content="DG no es."))
        assert code == 0
        assert stdout == ""

    def test_memory_path_skipped(self):
        _, stdout, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="/memory/notes.md", content="DG no es nada."))
        assert code == 0

    def test_node_modules_skipped(self):
        _, stdout, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="project/node_modules/brand/index.md",
                     content="no es."))
        assert code == 0

    def test_bak_file_skipped(self):
        # `.bak` short-circuit (line 87 region)
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="07_marca/brand.md.bak", content="no es nada."))
        assert code == 0

    def test_js_file_skipped(self):
        # `.js` short-circuit
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="07_marca/build.js", content="no es algo."))
        assert code == 0

    def test_deliverable_wrong_extension_skipped(self):
        # path matches but extension is not in TEXT_EXTENSIONS (line 87 actually)
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="07_marca/brand.json", content="no es nada."))
        assert code == 0

    def test_empty_content_skipped(self):
        # path + extension match but content is empty (line 90)
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="07_marca/brand.md", content=""))
        assert code == 0


# ---------------------------------------------------------------- #
# scar_011 — extra exit branches + _log call site
# ---------------------------------------------------------------- #
class TestScar011:
    HOOK = "examples/production-case/hooks/hook_scar_011_tildes_entregables.py"

    def test_log_called_on_match(self):
        calls, _, _ = _run_with_fake_log(self.HOOK,
            _pretool(file_path="05_imagen_comunicacion/manual.md",
                     content="La funcion del sistema."))
        assert len(calls) == 1
        assert calls[0]["scar_id"] == "scar_011"

    def test_bak_file_skipped(self):
        # `.bak` short-circuit (line 87)
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="05_imagen_comunicacion/brochure.md.bak",
                     content="La funcion principal."))
        assert code == 0

    def test_previews_path_skipped(self):
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="05_imagen_comunicacion/_previews/draft.md",
                     content="La funcion sin tilde."))
        assert code == 0

    def test_capture_path_skipped(self):
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="05_imagen_comunicacion/_capture_2026/draft.md",
                     content="La funcion sin tilde."))
        assert code == 0

    def test_fix_tildes_path_skipped(self):
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="05_imagen_comunicacion/_fix_tildes_log.md",
                     content="La funcion sin tilde."))
        assert code == 0

    def test_deliverable_wrong_extension_skipped(self):
        # deliverable path matches, but extension not in TEXT_EXTENSIONS (line 99)
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="05_imagen_comunicacion/manual.svg",
                     content="La funcion principal."))
        assert code == 0

    def test_empty_content_skipped(self):
        # path + ext match but empty content (line 101)
        _, _, code = _run_with_fake_log(self.HOOK,
            _pretool(file_path="05_imagen_comunicacion/manual.md", content=""))
        assert code == 0

    def test_dedup_breaks_at_8_unique_words(self):
        """Force the `if len(seen) >= 8: break` branch (line 117)."""
        # 9 distinct unaccented trigger words -> dedup loop should stop at 8
        words = "funcion gestion seccion revision decision direccion "\
                "ingenieria tecnologia tipografia"
        calls, _, _ = _run_with_fake_log(self.HOOK,
            _pretool(file_path="05_imagen_comunicacion/manual.md",
                     content=f"Texto con {words} acumuladas."))
        assert len(calls) == 1
        # `seen` is rendered into trigger_match (top 5); ensure logging happened
        # and that the hook didn't crash on the >8 unique-words case.
        assert calls[0]["scar_id"] == "scar_011"


# ---------------------------------------------------------------- #
# session_start (production) — _log call site
# ---------------------------------------------------------------- #
class TestProductionSessionStartLog:
    HOOK = "examples/production-case/hooks/hook_session_start.py"

    def test_log_called_on_session_start(self):
        calls, _, _ = _run_with_fake_log(self.HOOK, {})
        assert len(calls) == 1


# ---------------------------------------------------------------- #
# dropbox — empty stdin -> env/cwd fallback + _log call site
# ---------------------------------------------------------------- #
class TestDropboxMirror:
    HOOK = "examples/production-case/hooks/hook_dropbox_mirror_warn.py"

    def test_log_called_when_mirror_detected(self):
        calls, _, _ = _run_with_fake_log(self.HOOK,
            {"cwd": "C:/Users/me/Dropbox/Contabilidad/DG-2026"})
        assert len(calls) == 1
        assert calls[0]["scar_id"] == "infra_001"

    def test_empty_raw_falls_back_to_env(self, monkeypatch):
        """raw="" -> falls through to os.environ['CLAUDE_PROJECT_DIR'] (lines 39, 46)."""
        monkeypatch.setenv("CLAUDE_PROJECT_DIR",
                           "C:/Users/me/Dropbox/Contabilidad/whatever")
        calls, _, _ = _run_with_fake_log(self.HOOK, "")
        # mirror detected via env var fallback
        assert len(calls) == 1

    def test_invalid_json_in_raw_falls_back(self, monkeypatch):
        """Garbage JSON in stdin (line 42-43 except branch) falls back to env/cwd."""
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", "D:/DG-2026_OFFICE")  # canonical
        # invalid json -> except: pass ; then env fallback (canonical) -> no fire
        calls, stdout, _ = _run_with_fake_log(self.HOOK, "{not valid json")
        assert calls == []
        assert stdout == ""
