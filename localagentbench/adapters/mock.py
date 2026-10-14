"""Mock adapter for dry-runs and CI without a model.

--agent mock: optionally applies a canned patch (env MOCK_PATCH=apply) else
does nothing. Used to verify harness plumbing end-to-end.
"""
from __future__ import annotations

import os
import time

from . import AgentResult


class MockAdapter:
    name = "mock"

    def run(self, prompt: str, workdir: str, model: str,
            timeout_s: int, max_turns: int, **kwargs) -> AgentResult:
        t0 = time.time()
        mode = os.environ.get("LAB_MOCK", "noop")
        note = f"mock adapter ({mode}): no changes made"
        if mode == "noop":
            pass
        time.sleep(0.05)
        return AgentResult(adapter=self.name, model=model, workdir=workdir,
                           exit_code=0, stdout=note, stderr="",
                           wall_s=time.time() - t0,
                           tool_calls=0, failed_tool_calls=0,
                           extra={"mode": mode})
