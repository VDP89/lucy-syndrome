"""
Tests for logging/opportunity_observer.py.

Observer outputs {} to stdout on match, calls sys.exit(0) on no-match.
"""
import pytest
from conftest import run_hook, run_hook_raw, make_pretool

HOOK = "logging/opportunity_observer.py"


def fired(payload: dict) -> bool:
    output, exit_code = run_hook(HOOK, payload)
    return output is not None


class TestDocxOpportunity:
    def test_write_docx_triggers(self):
        assert fired(make_pretool("Write", "output/report.docx", "content"))

    def test_edit_docx_triggers(self):
        assert fired(make_pretool("Edit", "path/to/doc.docx", "new content"))

    def test_read_docx_does_not_trigger(self):
        assert not fired(make_pretool("Read", "output/report.docx", "content"))


class TestCodeOpportunity:
    def test_write_py_triggers(self):
        assert fired(make_pretool("Write", "app.py", "x = 1\n" * 10))

    def test_write_ts_triggers(self):
        assert fired(make_pretool("Write", "src/index.ts", "const x = 1;"))

    def test_write_js_triggers(self):
        assert fired(make_pretool("Write", "main.js", "console.log(1)"))

    def test_write_plain_txt_does_not_trigger(self):
        assert not fired(make_pretool("Write", "/tmp/notes.txt", "hello"))


class TestTaskOpportunity:
    def test_task_dispatch_triggers(self):
        payload = {"tool_name": "Task", "event": "PreToolUse",
                   "tool_input": {"prompt": "do something"}}
        assert fired(payload)

    def test_bash_does_not_trigger_task_rule(self):
        payload = {"tool_name": "Bash", "event": "PreToolUse",
                   "tool_input": {"command": "ls"}}
        assert not fired(payload)


class TestDeliverableOpportunity:
    def test_landing_html_triggers(self):
        assert fired(make_pretool("Write",
                                  "05_imagen_comunicacion/landing/index.html",
                                  "<!DOCTYPE html><html></html>"))

    def test_informe_md_triggers(self):
        assert fired(make_pretool("Write", "output/informe_mensual.md", "# Report"))

    def test_brand_md_triggers(self):
        assert fired(make_pretool("Write", "07_marca/brand_guidelines.md", "# Brand"))


class TestNoOpportunity:
    def test_plain_scratch_file_no_match(self):
        assert not fired(make_pretool("Write", "/tmp/scratch.txt", "hello"))

    def test_invalid_json_exits_cleanly(self):
        output, exit_code = run_hook_raw(HOOK, "not valid json {{{")
        assert output is None
        assert exit_code == 0

    def test_read_tool_no_code_opportunity(self):
        assert not fired({"tool_name": "Read", "event": "PreToolUse",
                          "tool_input": {"file_path": "app.py"}})


class TestOutputFormat:
    def test_output_is_empty_dict_on_match(self):
        output, _ = run_hook(HOOK, make_pretool("Write", "app.py", "x = 1"))
        assert output == {}
