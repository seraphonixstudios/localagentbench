"""Ollama helpers: detect models, recommend coding models, check context."""
from __future__ import annotations

import json
import shutil
import subprocess

# Preferred coding models for local eval (ordered). First available wins.
RECOMMENDED_CODING_MODELS = [
    "qwen3-coder:30b",
    "qwen2.5-coder:32b",
    "qwen2.5-coder:14b",
    "deepseek-coder-v2:16b",
    "qwen2.5-coder:7b",
    "starcoder2:15b",
    "codellama:13b",
    "qwen3:8b",
]

# Models known to have weak tool-calling; harness warns and suggests settings.
WEAK_TOOLCALL_MODELS = ("llama3", "dolphin", "llava", "whisper", "embed")


def ollama_available() -> bool:
    return shutil.which("ollama") is not None


def list_models() -> list[dict]:
    """Return [{'name': ..., 'size_gb': float, 'modified': str}] or []."""
    if not ollama_available():
        return []
    try:
        out = subprocess.run(["ollama", "list"], capture_output=True,
                             text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    lines = out.stdout.strip().splitlines()
    models: list[dict] = []
    for line in lines[1:]:  # skip header
        parts = line.split()
        if not parts:
            continue
        models.append({"name": parts[0], "raw": line.strip()})
    return models


def available_model_names() -> list[str]:
    return [m["name"] for m in list_models()]


def recommend_model(available: list[str] | None = None) -> str | None:
    avail = available if available is not None else available_model_names()
    for rec in RECOMMENDED_CODING_MODELS:
        base = rec.split(":")[0]
        for a in avail:
            if a == rec or a.startswith(base + ":") or a.startswith(base):
                return a
    return avail[0] if avail else None


def normalize_model(model: str) -> str:
    """'qwen3-coder:30b' -> 'ollama/qwen3-coder:30b' style used by OpenCode."""
    if "/" in model:
        return model
    return f"ollama/{model}"


def strip_provider(model: str) -> str:
    return model.split("/", 1)[1] if "/" in model else model


def toolcall_warning(model: str) -> str | None:
    low = model.lower()
    for w in WEAK_TOOLCALL_MODELS:
        if w in low:
            return (f"Model '{model}' (matched '{w}') may have weak tool-calling. "
                    "Prefer a coder model (qwen2.5-coder, qwen3-coder, deepseek-coder-v2). "
                    "If you must use it, lower max_turns and use simple fixture tasks.")
    return None


def ollama_show(model: str) -> dict:
    name = strip_provider(model)
    try:
        out = subprocess.run(["ollama", "show", name], capture_output=True,
                             text=True, timeout=15)
    except (OSError, subprocess.SubprocessError) as e:
        return {"ok": False, "error": str(e)}
    return {"ok": out.returncode == 0, "output": out.stdout + out.stderr}


def probe_tool_calls(model: str, timeout: int = 120) -> dict:
    """Ask the model to call a dummy `add` tool via the OpenAI-compatible
    endpoint. Returns {supported: bool, detail: str}.

    A model that only emits tool-call-shaped *text* (content set,
    tool_calls null) cannot drive an agentic loop — fail fast instead of
    burning a full eval. Stdlib only (urllib).
    """
    import json as _json
    import urllib.request as _req
    name = strip_provider(model)
    body = {
        "model": name,
        "messages": [{"role": "user", "content":
                      "What is 2+2? You must call the add tool."}],
        "tools": [{"type": "function", "function": {
            "name": "add", "description": "Add two numbers",
            "parameters": {"type": "object",
                           "properties": {"a": {"type": "number"},
                                          "b": {"type": "number"}},
                           "required": ["a", "b"]}}}],
        "tool_choice": "auto",
    }
    try:
        req = _req.Request(
            "http://127.0.0.1:11434/v1/chat/completions",
            data=_json.dumps(body).encode(),
            headers={"Content-Type": "application/json"})
        with _req.urlopen(req, timeout=timeout) as r:
            resp = _json.load(r)
    except Exception as e:
        return {"supported": False,
                "detail": f"probe request failed: {type(e).__name__}: {e}"}
    try:
        msg = resp["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return {"supported": False, "detail": f"unexpected response: {resp!r}"[:200]}
    calls = msg.get("tool_calls")
    if calls:
        return {"supported": True,
                "detail": f"native tool_calls: {calls[0].get('function', {}).get('name')}"}
    return {"supported": False,
            "detail": "model emitted text instead of tool_calls: "
                      f"{(msg.get('content') or '')[:120]!r}"}
