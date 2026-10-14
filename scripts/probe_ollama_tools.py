"""Probe whether an Ollama model honors native tool calls.

POSTs to /v1/chat/completions with one dummy function tool and asks the
model to use it. Native support -> response contains tool_calls.
Text-JSON instead -> the model can't drive an agentic loop on this path.
"""
import json
import sys
import urllib.request

model = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5-coder:7b"
body = {
    "model": model,
    "messages": [
        {"role": "user",
         "content": "What is 2+2? You must call the add tool with a=2, b=2."},
    ],
    "tools": [{
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        },
    }],
    "tool_choice": "auto",
}
req = urllib.request.Request(
    "http://127.0.0.1:11434/v1/chat/completions",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=180) as r:
    resp = json.load(r)
msg = resp["choices"][0]["message"]
print("content:", (msg.get("content") or "")[:300])
print("tool_calls:", json.dumps(msg.get("tool_calls"))[:500])
