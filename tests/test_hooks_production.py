"""Tests for examples/production-case/hooks/ -- all 8 production hooks."""
import pytest
from conftest import run_hook, run_hook_raw, make_pretool

DIR = "examples/production-case/hooks"


def hook(name):
    return f"{DIR}/{name}"


# scar_001_docx -----------------------------------------------------------------
class TestHookScar001Docx:
    def test_py_with_docx_fires(self):
        out, _ = run_hook(hook("hook_scar_001_docx.py"),
                          make_pretool("Write", "gen.py", "from docx import Document"))
        assert out is not None
        assert "additionalContext" in out["hookSpecificOutput"]

    def test_py_without_docx_no_fire(self):
        _, code = run_hook(hook("hook_scar_001_docx.py"),
                           make_pretool("Write", "main.py", "print(42)"))
        assert code == 0

    def test_html_with_docx_no_fire(self):
        _, code = run_hook(hook("hook_scar_001_docx.py"),
                           make_pretool("Write", "page.html", "docx reference"))
        assert code == 0

    def test_invalid_json_exits_cleanly(self):
        _, code = run_hook_raw(hook("hook_scar_001_docx.py"), "{{invalid")
        assert code == 0

    def test_context_mentions_scar_001(self):
        out, _ = run_hook(hook("hook_scar_001_docx.py"),
                          make_pretool("Write", "gen.py", "import docx"))
        assert "scar_001" in out["hookSpecificOutput"]["additionalContext"]

    def test_system_message_present(self):
        out, _ = run_hook(hook("hook_scar_001_docx.py"),
                          make_pretool("Write", "gen.py", "docx.Document()"))
        assert "systemMessage" in out


# scar_002_size -----------------------------------------------------------------
class TestHookScar002Size:
    def _py(self, n):
        return "x = 1\n" * n

    def test_201_line_py_fires(self):
        out, _ = run_hook(hook("hook_scar_002_size.py"),
                          make_pretool("Write", "big.py", self._py(201)))
        assert out is not None

    def test_50_line_py_no_fire(self):
        _, code = run_hook(hook("hook_scar_002_size.py"),
                           make_pretool("Write", "small.py", self._py(50)))
        assert code == 0

    def test_exactly_200_no_fire(self):
        _, code = run_hook(hook("hook_scar_002_size.py"),
                           make_pretool("Write", "edge.py", self._py(199)))
        assert code == 0

    def test_html_not_code_no_fire(self):
        _, code = run_hook(hook("hook_scar_002_size.py"),
                           make_pretool("Write", "page.html", self._py(300)))
        assert code == 0

    def test_ts_file_fires(self):
        out, _ = run_hook(hook("hook_scar_002_size.py"),
                          make_pretool("Write", "component.ts", self._py(210)))
        assert out is not None

    def test_context_shows_line_count(self):
        out, _ = run_hook(hook("hook_scar_002_size.py"),
                          make_pretool("Write", "app.py", self._py(250)))
        assert "lineas" in out["hookSpecificOutput"]["additionalContext"]

    def test_invalid_json_exits_cleanly(self):
        _, code = run_hook_raw(hook("hook_scar_002_size.py"), "bad")
        assert code == 0


# scar_005_subagent -------------------------------------------------------------
class TestHookScar005Subagent:
    def test_always_fires(self):
        out, _ = run_hook(hook("hook_scar_005_subagent.py"), {})
        assert out is not None

    def test_context_mentions_cobertura(self):
        out, _ = run_hook(hook("hook_scar_005_subagent.py"), {})
        assert "COBERTURA" in out["hookSpecificOutput"]["additionalContext"]

    def test_system_message_present(self):
        out, _ = run_hook(hook("hook_scar_005_subagent.py"), {})
        assert "systemMessage" in out

    def test_fires_with_task_payload(self):
        out, _ = run_hook(hook("hook_scar_005_subagent.py"),
                          {"tool_name": "Task", "tool_input": {"prompt": "work"}})
        assert out is not None


# scar_010_no_cerrar_puertas ----------------------------------------------------
class TestHookScar010NoCerrarPuertas:
    def _brand(self, content):
        return make_pretool("Write", "07_marca/brand_guidelines.md", content)

    def test_no_es_fires(self):
        out, _ = run_hook(hook("hook_scar_010_no_cerrar_puertas.py"),
                          self._brand("DG no es una consultora tradicional."))
        assert out is not None

    def test_no_somos_fires(self):
        out, _ = run_hook(hook("hook_scar_010_no_cerrar_puertas.py"),
                          self._brand("DG no somos una empresa convencional."))
        assert out is not None

    def test_clean_content_no_fire(self):
        _, code = run_hook(hook("hook_scar_010_no_cerrar_puertas.py"),
                           self._brand("DG es una empresa de ingenieria."))
        assert code == 0

    def test_non_deliverable_path_no_fire(self):
        _, code = run_hook(hook("hook_scar_010_no_cerrar_puertas.py"),
                           make_pretool("Write", "src/readme.md", "no es un error"))
        assert code == 0

    def test_py_file_skipped(self):
        _, code = run_hook(hook("hook_scar_010_no_cerrar_puertas.py"),
                           make_pretool("Write", "07_marca/script.py", "# no es"))
        assert code == 0

    def test_context_mentions_scar_010(self):
        out, _ = run_hook(hook("hook_scar_010_no_cerrar_puertas.py"),
                          self._brand("DG no es lo que buscamos en el mercado."))
        assert "scar_010" in out["hookSpecificOutput"]["additionalContext"]

    def test_invalid_json_exits_cleanly(self):
        _, code = run_hook_raw(hook("hook_scar_010_no_cerrar_puertas.py"), "bad")
        assert code == 0


# scar_011_tildes_entregables ---------------------------------------------------
class TestHookScar011TildesEntregables:
    def _doc(self, content, path="05_imagen_comunicacion/brochure/manual.md"):
        return make_pretool("Write", path, content)

    def test_funcion_without_accent_fires(self):
        out, _ = run_hook(hook("hook_scar_011_tildes_entregables.py"),
                          self._doc("La funcion principal del sistema."))
        assert out is not None

    def test_gestion_fires(self):
        out, _ = run_hook(hook("hook_scar_011_tildes_entregables.py"),
                          self._doc("La gestion de proyectos es clave."))
        assert out is not None

    def test_ingenieria_fires(self):
        out, _ = run_hook(hook("hook_scar_011_tildes_entregables.py"),
                          self._doc("Empresa de ingenieria."))
        assert out is not None

    def test_accented_content_no_fire(self):
        _, code = run_hook(hook("hook_scar_011_tildes_entregables.py"),
                           self._doc("La funci\u00f3n principal del sistema."))
        assert code == 0

    def test_non_deliverable_path_no_fire(self):
        _, code = run_hook(hook("hook_scar_011_tildes_entregables.py"),
                           make_pretool("Write", "src/notes.md", "La funcion principal."))
        assert code == 0

    def test_py_file_in_deliverable_path_skipped(self):
        _, code = run_hook(hook("hook_scar_011_tildes_entregables.py"),
                           make_pretool("Write", "05_imagen_comunicacion/script.py",
                                        "# funcion"))
        assert code == 0

    def test_claude_internal_path_skipped(self):
        _, code = run_hook(hook("hook_scar_011_tildes_entregables.py"),
                           make_pretool("Write", "/.claude/memory/notes.md",
                                        "funcion principal"))
        assert code == 0

    def test_context_mentions_scar_011(self):
        out, _ = run_hook(hook("hook_scar_011_tildes_entregables.py"),
                          self._doc("La funcion y la gestion son claves."))
        assert "scar_011" in out["hookSpecificOutput"]["additionalContext"]

    def test_invalid_json_exits_cleanly(self):
        _, code = run_hook_raw(hook("hook_scar_011_tildes_entregables.py"), "bad")
        assert code == 0


# scar_004_expand ---------------------------------------------------------------
class TestHookScar004Expand:
    def test_trigger_phrase_fires(self):
        out, _ = run_hook(hook("hook_scar_004_expand.py"),
                          {"prompt": "nuestro plan de trabajo para esta semana"})
        assert out is not None

    def test_nuestra_estrategia_fires(self):
        out, _ = run_hook(hook("hook_scar_004_expand.py"),
                          {"prompt": "basado en nuestra estrategia de contenido"})
        assert out is not None

    def test_empty_prompt_no_fire(self):
        _, code = run_hook(hook("hook_scar_004_expand.py"), {"prompt": ""})
        assert code == 0

    def test_output_has_additional_context_when_fires(self):
        out, _ = run_hook(hook("hook_scar_004_expand.py"),
                          {"prompt": "como quedamos con el plan"})
        if out is not None:
            assert "additionalContext" in out["hookSpecificOutput"]

    def test_invalid_json_exits_cleanly(self):
        _, code = run_hook_raw(hook("hook_scar_004_expand.py"), "badinput")
        assert code == 0


# hook_session_start (production) -----------------------------------------------
class TestProductionSessionStart:
    def test_always_produces_output(self):
        out, _ = run_hook(hook("hook_session_start.py"), {})
        assert out is not None

    def test_event_name_is_session_start(self):
        out, _ = run_hook(hook("hook_session_start.py"), {})
        assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"

    def test_context_mentions_scars(self):
        out, _ = run_hook(hook("hook_session_start.py"), {})
        assert "scar_" in out["hookSpecificOutput"]["additionalContext"]

    def test_context_is_nonempty(self):
        out, _ = run_hook(hook("hook_session_start.py"), {})
        assert len(out["hookSpecificOutput"]["additionalContext"]) > 50


# hook_dropbox_mirror_warn -------------------------------------------------------
class TestHookDropboxMirrorWarn:
    def test_dropbox_cwd_fires(self):
        out, _ = run_hook(hook("hook_dropbox_mirror_warn.py"),
                          {"cwd": "C:/Users/Me/Dropbox/Contabilidad/DG-2026"})
        assert out is not None

    def test_canonical_cwd_no_fire(self):
        out, _ = run_hook(hook("hook_dropbox_mirror_warn.py"),
                          {"cwd": "D:/DG-2026_OFFICE"})
        assert out is None

    def test_dropbox_warning_message(self):
        out, _ = run_hook(hook("hook_dropbox_mirror_warn.py"),
                          {"cwd": "C:/Users/Me/Dropbox/Contabilidad/DG"})
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "dropbox" in ctx.lower() or "Dropbox" in ctx

    def test_workspace_key_also_works(self):
        out, _ = run_hook(hook("hook_dropbox_mirror_warn.py"),
                          {"workspace": "C:/dropbox/contabilidad/project"})
        assert out is not None
