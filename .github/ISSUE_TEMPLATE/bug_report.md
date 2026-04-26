---
name: Bug report
about: Something in the framework, installer, or hooks is misbehaving
title: "bug: <short description>"
labels: bug
---

## What happened

<!-- Describe the actual behavior. Quote any error message verbatim. -->

## What you expected

<!-- One or two sentences. -->

## How to reproduce

<!-- Minimal command or stdin payload that triggers the bug.

For hook bugs:
    echo '{...}' | python .claude/scarring/hooks/hook_xxx.py

For installer bugs:
    bash install.sh /tmp/some-test-dir
-->

```bash
<paste here>
```

## Environment

- **Lucy Syndrome version / commit**: <e.g. v1.2.0 or commit sha>
- **Python**: <output of `python --version`>
- **OS**: <Linux / macOS / Windows + version>
- **Claude Code version** (if relevant): <output of `claude --version`>

## Additional context

<!-- Logs from fires.jsonl, stack traces, anything else that helps. -->
