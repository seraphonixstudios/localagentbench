"""Aider adapter — invokes `aider` headless in the task workdir.

Command shape (verified against aider 0.86):
    aider --model <model> --no-git --no-auto-commits --yes-always \
        --message "<prompt>"
with cwd=workdir. Aider exits 0 even when the task is incomplete, so
success always comes from the oracle, never the exit code.

Model ids: harness ids like `ollama/qwen3:8b` map directly to aider's
`--model ollama/<ollama-tag>` naming.

Install: pip's aider-chat is ancient on new Pythons; use
    uv tool install aider-chat --python 3.12
The adapter resolves the binary via PATH plus uv's fallback bin dirs.

Output parsing (heuristic, documented): `Applied edit to ...` lines count
as tool calls; aider's `Tokens: N sent, M received.` line gives token
usage; failures match `failed to apply`-style lines.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import time

from . import AgentResult

TOKENS_RE = re.compile(r"Tokens:\s*([\d,]+)\s*sent,\s*([\d,]+)\s*received")
EDIT_RE = re.compile(r"Applied edit to ")
FAILED_RE = re.compile(r"(?i)failed to apply|error applying|malformed.*?edit")


def metadata_file() -> str:
    """Absolute path of the shipped litellm model-metadata file."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "aider-models.json")


def aider_binary() -> str | None:
    found = shutil.which("aider")
    if found:
        return found
    # uv tool fallback bins (uv's dir is often not on PATH)
    home = os.path.expanduser("~")
    for cand in (os.path.join(home, ".local", "bin", "aider"),
                 os.path.join(home, ".local", "bin", "aider.exe")):
        if os.path.isfile(cand):
            return cand
    return None


def aider_model_id(model: str) -> str:
    """Harness `ollama/qwen3:8b` -> aider `ollama/qwen3:8b` (passthrough)."""
    return model if "/" in model else f"ollama/{model}"


def build_command(prompt: str, model: str, binary: str = "aider",
                  extra_args: list[str] | None = None) -> list[str]:
    cmd = [binary, "--model", aider_model_id(model),
           "--no-git", "--no-auto-commits", "--yes-always",
           "--model-metadata-file", metadata_file(),
           "--message", prompt]
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def parse_aider_output(stdout: str) -> dict:
    """Parse aider's human-readable transcript (never raises)."""
    edits = len(EDIT_RE.findall(stdout or ""))
    failed = len(FAILED_RE.findall(stdout or ""))
    in_tok = out_tok = None
    m = TOKENS_RE.search(stdout or "")
    if m:
        in_tok = int(m.group(1).replace(",", ""))
        out_tok = int(m.group(2).replace(",", ""))
    return {"tool_calls": edits, "failed_tool_calls": failed,
            "input_tokens": in_tok, "output_tokens": out_tok}


class AiderAdapter:
    name = "aider"

    def __init__(self, extra_args: list[str] | None = None):
        self.extra_args = extra_args or []

    def run(self, prompt: str, workdir: str, model: str,
            timeout_s: int, max_turns: int, **kwargs) -> AgentResult:
        binary = aider_binary()
        t0 = time.time()
        if binary is None:
            return AgentResult(
                adapter=self.name, model=model, workdir=workdir,
                exit_code=127, stderr="aider binary not found. Install: "
                "uv tool install aider-chat --python 3.12 "
                "(pip's aider-chat is too old on new Pythons). "
                "Or run with --agent mock for a dry-run.",
                wall_s=time.time() - t0,
                extra={"hint": "missing_binary"})
        # No --max-turns flag; bound via prompt suffix (same as opencode).
        bounded = (f"{prompt}\n\n[bench: complete the task in at most "
                   f"{max_turns} tool steps. Do not ask follow-up questions.]")
        cmd = build_command(bounded, model, binary, self.extra_args)
        env = dict(os.environ)
        # Aider warns when this is unset; default to local Ollama but
        # respect an explicit remote/proxied endpoint.
        env.setdefault("OLLAMA_API_BASE", "http://127.0.0.1:11434")
        try:
            proc = subprocess.run(
                cmd, cwd=workdir, capture_output=True, text=True,
                encoding="utf-8", errors="replace", env=env,
                timeout=timeout_s)
            wall = time.time() - t0
            sig = parse_aider_output(proc.stdout or "")
            return AgentResult(
                adapter=self.name, model=model, workdir=workdir,
                exit_code=proc.returncode, stdout=proc.stdout or "",
                stderr=proc.stderr or "", wall_s=wall,
                tool_calls=sig["tool_calls"],
                failed_tool_calls=sig["failed_tool_calls"],
                input_tokens=sig["input_tokens"],
                output_tokens=sig["output_tokens"],
                extra={"cmd": cmd})
        except subprocess.TimeoutExpired as e:
            wall = time.time() - t0
            out = e.stdout
            stdout = out.decode(errors="replace") if isinstance(out, bytes) \
                else str(out or "")
            return AgentResult(
                adapter=self.name, model=model, workdir=workdir,
                exit_code=124, stdout=stdout,
                stderr=f"agent timed out after {timeout_s}s",
                wall_s=wall, extra={"timeout": True})
        except OSError as e:
            return AgentResult(adapter=self.name, model=model,
                               workdir=workdir, exit_code=127,
                               stderr=str(e), wall_s=time.time() - t0)
