"""Oracle: run task success commands, capture pass/fail."""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field


@dataclass
class OracleResult:
    passed: bool
    commands: list[dict] = field(default_factory=list)
    wall_s: float = 0.0


def run_oracle(commands: list[str], workdir: str,
               timeout_s: int = 120) -> OracleResult:
    results: list[dict] = []
    t0 = time.time()
    ok = True
    for cmd in commands:
        c0 = time.time()
        try:
            proc = subprocess.run(cmd, shell=True, cwd=workdir,
                                  capture_output=True, text=True,
                                  encoding="utf-8", errors="replace",
                                  timeout=timeout_s)
            passed = proc.returncode == 0
            results.append({"command": cmd, "exit_code": proc.returncode,
                            "passed": passed, "stdout": proc.stdout[-4000:],
                            "stderr": proc.stderr[-4000:],
                            "wall_s": round(time.time() - c0, 3)})
            if not passed:
                ok = False
        except subprocess.TimeoutExpired:
            results.append({"command": cmd, "exit_code": 124, "passed": False,
                            "stdout": "", "stderr": f"timeout after {timeout_s}s",
                            "wall_s": timeout_s})
            ok = False
            break
    return OracleResult(passed=ok, commands=results,
                        wall_s=round(time.time() - t0, 3))
