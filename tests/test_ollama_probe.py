"""Unit tests for the Ollama tool-call probe (network stubbed)."""
import io
import json

from localagentbench.ollama import probe_tool_calls


class _Resp:
    def __init__(self, payload):
        self._buf = io.BytesIO(json.dumps(payload).encode())

    def __enter__(self):
        return self._buf

    def __exit__(self, *a):
        return False


def _patch(monkeypatch, message):
    import urllib.request
    monkeypatch.setattr(
        urllib.request, "urlopen",
        lambda *a, **k: _Resp({"choices": [{"message": message}]}))


def test_probe_detects_native_tools(monkeypatch):
    _patch(monkeypatch, {"content": "",
                         "tool_calls": [{"function": {"name": "add"}}]})
    res = probe_tool_calls("ollama/m:1b")
    assert res["supported"] is True


def test_probe_rejects_text_json(monkeypatch):
    _patch(monkeypatch, {"content": '{"name": "add", "arguments": {}}',
                         "tool_calls": None})
    res = probe_tool_calls("ollama/m:1b")
    assert res["supported"] is False
    assert "text instead of tool_calls" in res["detail"]


def test_probe_handles_request_failure(monkeypatch):
    import urllib.request
    def boom(*a, **k):
        raise ConnectionError("down")
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    res = probe_tool_calls("ollama/m:1b")
    assert res["supported"] is False
