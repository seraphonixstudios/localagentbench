"""Pluggable agent adapters."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class AgentResult:
    adapter: str
    model: str
    workdir: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    wall_s: float = 0.0
    # Best-effort structured signals parsed from trajectory
    tool_calls: int = 0
    failed_tool_calls: int = 0
    input_tokens: int | None = None
    output_tokens: int | None = None
    raw_log_path: str | None = None
    extra: dict = field(default_factory=dict)


class AgentAdapter(Protocol):
    name: str

    def run(self, prompt: str, workdir: str, model: str,
            timeout_s: int, max_turns: int, **kwargs) -> AgentResult:
        ...
