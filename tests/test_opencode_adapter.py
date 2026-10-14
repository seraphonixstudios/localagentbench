"""Regression tests for the OpenCode adapter's binary resolution.

On Windows, invoking bare `opencode` via CreateProcess (no shell) fails with
WinError 2 because only `.exe` is appended (PATHEXT ignored) and the npm
shim is `opencode.cmd`. The adapter must exec the shutil.which()-resolved
path instead.
"""
import json

import shutil

from localagentbench.adapters.opencode import (OpenCodeAdapter, build_command,
                                               opencode_binary,
                                               parse_jsonl_trajectory)


def test_build_command_uses_resolved_binary():
    resolved = shutil.which("opencode") or "opencode"
    cmd = build_command("do it", "ollama/m:1b", "build", binary=resolved)
    assert cmd[0] == resolved
    assert "--auto" in cmd and "--format" in cmd and "json" in cmd


def test_missing_binary_gives_clear_error(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    res = OpenCodeAdapter().run("do it", str(tmp_path), "ollama/m:1b",
                                timeout_s=10, max_turns=5)
    assert res.exit_code == 127
    assert "opencode binary not found" in res.stderr


def test_binary_prefers_sibling_exe(tmp_path, monkeypatch):
    shim = tmp_path / "opencode.cmd"
    shim.write_text("stub")
    (tmp_path / "opencode.exe").write_text("stub")
    monkeypatch.setattr(shutil, "which", lambda *a, **k: str(shim))
    assert opencode_binary() == str(tmp_path / "opencode.exe")


def test_binary_prefers_npm_layout_exe(tmp_path, monkeypatch):
    shim = tmp_path / "opencode.cmd"
    shim.write_text("stub")
    exe = tmp_path / "node_modules" / "@opencode" / "cli" / "bin" / "opencode.exe"
    exe.parent.mkdir(parents=True)
    exe.write_text("stub")
    monkeypatch.setattr(shutil, "which", lambda *a, **k: str(shim))
    assert opencode_binary() == str(exe)


def test_binary_falls_back_without_sibling_exe(tmp_path, monkeypatch):
    shim = tmp_path / "opencode.cmd"
    shim.write_text("stub")
    monkeypatch.setattr(shutil, "which", lambda *a, **k: str(shim))
    assert opencode_binary() == str(shim)


def test_parse_real_event_schema():
    stream = "\n".join([
        json.dumps({"type": "step_start", "part": {"type": "step-start"}}),
        json.dumps({"type": "tool_use", "part": {
            "type": "tool", "tool": "read",
            "state": {"status": "completed"}}}),
        json.dumps({"type": "step_finish", "part": {
            "type": "step-finish",
            "tokens": {"input": 10, "output": 581, "reasoning": 0}}}),
        json.dumps({"type": "tool_use", "part": {
            "type": "tool", "tool": "subagent",
            "state": {"status": "error"}}}),
        json.dumps({"type": "step_finish", "part": {
            "type": "step-finish",
            "tokens": {"input": 1, "output": 676, "reasoning": 5}}}),
        json.dumps({"type": "text", "part": {"type": "text", "text": "hi"}}),
        "not json {{{",
    ])
    sig = parse_jsonl_trajectory(stream)
    assert sig["tool_calls"] == 2
    assert sig["failed_tool_calls"] == 1
    assert sig["input_tokens"] == 11
    assert sig["output_tokens"] == 1257
    assert sig["text"] == "hi"
