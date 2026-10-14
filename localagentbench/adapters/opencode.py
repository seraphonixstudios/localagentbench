"""OpenCode adapter — invokes `opencode run` headless in the task workdir.

Uses the documented headless mode:
    opencode run --format json --model <model> --agent <agent> "<prompt>"
with cwd=workdir. Captures stdout/stderr, wall time, and parses
newline-delimited JSON for token/tool signals on a best-effort basis.
Falls back gracefully when OpenCode is not installed (clear error).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from . import AgentResult


def opencode_binary() -> str | None:
    found = shutil.which("opencode")
    if found is None:
        return None
    # Prefer a sibling .exe over npm .cmd/.bat shims. cmd.exe re-parses the
    # command line and mangles embedded double quotes (a prompt containing
    # `"` + a shell metachar like `>` breaks with "directory name invalid").
    # A real .exe receives argv verbatim via CommandLineToArgvW.
    root, ext = os.path.splitext(found)
    if ext.lower() in (".cmd", ".bat", ".ps1"):
        cands = [
            root + ".exe",  # sibling exe
            # npm global layout: <root>/node_modules/@opencode/cli/bin/*.exe
            os.path.join(os.path.dirname(found), "node_modules",
                         "@opencode", "cli", "bin", "opencode.exe"),
        ]
        for cand in cands:
            if os.path.isfile(cand):
                return cand
    return found


def build_command(prompt: str, model: str, agent: str,
                  extra_args: list[str] | None = None,
                  binary: str = "opencode") -> list[str]:
    # NOTE: argv[0] must be the *resolved* binary path. A bare "opencode"
    # fails on Windows: CreateProcess (no shell) only appends .exe and
    # ignores PATHEXT, so the npm `opencode.cmd` shim is never found
    # (WinError 2). shutil.which() resolves it correctly.
    # --auto: approve non-denied permissions so headless runs never hang
    # waiting for an interactive permission prompt.
    cmd = [binary, "run", "--auto", "--format", "json",
           "--model", model, "--agent", agent, prompt]
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def parse_jsonl_trajectory(stdout: str) -> dict:
    """Parse `opencode run --format json` NDJSON event stream.

    Real event shapes (OpenCode v2):
      {"type":"tool_use","part":{"type":"tool","tool":<name>,
        "state":{"status":"completed"|"error",...}}}
      {"type":"step_finish","part":{"type":"step-finish",
        "tokens":{"input":n,"output":n,"reasoning":n,...}}}
      {"type":"text","part":{"type":"text","text":...}}
    Unknown shapes are ignored — never raises.
    """
    tool_calls = 0
    failed = 0
    in_tok = 0
    out_tok = 0
    texts: list[str] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = obj.get("type")
        part = obj.get("part") or {}
        if etype == "tool_use":
            tool_calls += 1
            state = part.get("state") or {}
            if state.get("status") == "error":
                failed += 1
        elif etype == "step_finish":
            toks = part.get("tokens") or {}
            if isinstance(toks.get("input"), int):
                in_tok += toks["input"]
            if isinstance(toks.get("output"), int):
                out_tok += toks["output"]
        elif etype == "text":
            t = part.get("text")
            if isinstance(t, str) and t.strip():
                texts.append(t)
    return {"tool_calls": tool_calls, "failed_tool_calls": failed,
            "input_tokens": in_tok or None, "output_tokens": out_tok or None,
            "text": "\n".join(texts)}


class OpenCodeAdapter:
    name = "opencode"

    def __init__(self, agent: str = "build",
                 extra_args: list[str] | None = None):
        self.agent = agent
        self.extra_args = extra_args or []

    def run(self, prompt: str, workdir: str, model: str,
            timeout_s: int, max_turns: int, **kwargs) -> AgentResult:
        binary = opencode_binary()
        t0 = time.time()
        if binary is None:
            return AgentResult(
                adapter=self.name, model=model, workdir=workdir,
                exit_code=127, stderr="opencode binary not found on PATH. "
                "Install: npm i -g @opencode/cli (https://opencode.ai). "
                "Or run with --agent mock for a dry-run.",
                wall_s=time.time() - t0,
                extra={"hint": "missing_binary"})
        # Constrain turns via prompt suffix; OpenCode has no --max-turns for run.
        bounded = (f"{prompt}\n\n[bench: complete the task in at most "
                   f"{max_turns} tool steps. Do not ask follow-up questions.]")
        cmd = build_command(bounded, model, self.agent, self.extra_args,
                            binary=binary)
        try:
            proc = subprocess.run(
                cmd, cwd=workdir, capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                timeout=timeout_s)
            wall = time.time() - t0
            signals = parse_jsonl_trajectory(proc.stdout or "")
            return AgentResult(
                adapter=self.name, model=model, workdir=workdir,
                exit_code=proc.returncode, stdout=proc.stdout or "",
                stderr=proc.stderr or "", wall_s=wall,
                tool_calls=signals["tool_calls"],
                failed_tool_calls=signals["failed_tool_calls"],
                input_tokens=signals["input_tokens"],
                output_tokens=signals["output_tokens"],
                extra={"cmd": cmd})
        except subprocess.TimeoutExpired as e:
            wall = time.time() - t0
            return AgentResult(
                adapter=self.name, model=model, workdir=workdir,
                exit_code=124, stdout=(e.stdout or b"").decode(errors="replace")
                if isinstance(e.stdout, bytes) else str(e.stdout or ""),
                stderr=f"agent timed out after {timeout_s}s",
                wall_s=wall, extra={"timeout": True})
        except OSError as e:
            return AgentResult(adapter=self.name, model=model,
                               workdir=workdir, exit_code=127,
                               stderr=str(e), wall_s=time.time() - t0)
