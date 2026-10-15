"""Tests for the Aider adapter (no model/binary needed — all stubbed)."""
import shutil
import subprocess

import localagentbench.adapters.aider as aider_mod
from localagentbench.adapters.aider import (AiderAdapter, build_command,
                                            parse_aider_output)

SAMPLE = """greet.py
Applied edit to greet.py
Tokens: 667 sent, 685 received.
"""


def test_build_command_shape():
    cmd = build_command("do it", "ollama/qwen3:8b", binary="aider")
    assert cmd[:2] == ["aider", "--model"]
    assert "ollama/qwen3:8b" in cmd
    for flag in ("--no-git", "--no-auto-commits", "--yes-always",
                 "--model-metadata-file", "--message", "do it"):
        assert flag in cmd
    assert cmd[cmd.index("--model-metadata-file") + 1].endswith(
        "aider-models.json")


def test_model_id_passthrough():
    assert aider_mod.aider_model_id("ollama/qwen3:8b") == "ollama/qwen3:8b"
    assert aider_mod.aider_model_id("qwen3:8b") == "ollama/qwen3:8b"


def test_parse_output():
    sig = parse_aider_output(SAMPLE)
    assert sig["tool_calls"] == 1
    assert sig["failed_tool_calls"] == 0
    assert sig["input_tokens"] == 667
    assert sig["output_tokens"] == 685


def test_parse_failures():
    sig = parse_aider_output("Failed to apply edit\nTokens: 1 sent, 2 received.")
    assert sig["tool_calls"] == 0
    assert sig["failed_tool_calls"] == 1


def test_missing_binary(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda *a, **k: None)
    monkeypatch.setattr(aider_mod.os.path, "isfile", lambda *a, **k: False)
    res = AiderAdapter().run("do it", str(tmp_path), "ollama/m:1b",
                             timeout_s=10, max_turns=5)
    assert res.exit_code == 127
    assert "aider binary not found" in res.stderr


def test_metadata_file_valid():
    import json
    from localagentbench.adapters.aider import metadata_file
    data = json.load(open(metadata_file(), encoding="utf-8"))
    entries = {k: v for k, v in data.items() if not k.startswith("_")}
    assert entries, "no model entries"
    for name, info in entries.items():
        assert info["max_input_tokens"] > 0, name
        assert info["litellm_provider"] == "ollama", name


def test_run_parses_transcript(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda *a, **k: "aider")

    class Proc:
        returncode = 0
        stdout = SAMPLE
        stderr = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Proc())
    res = AiderAdapter().run("do it", str(tmp_path), "ollama/m:1b",
                             timeout_s=10, max_turns=5)
    assert res.exit_code == 0
    assert res.tool_calls == 1
    assert res.input_tokens == 667 and res.output_tokens == 685
