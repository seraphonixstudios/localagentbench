"""Metrics: per-run records + aggregation (pass@1, pass@k, latency, tokens)."""
from __future__ import annotations

import math
from collections import defaultdict


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator (Chen et al. 2021). n=tries, c=correct."""
    if n <= 0 or c <= 0:
        return 0.0
    if k > n:
        k = n
    if c >= n:
        return 1.0
    # 1 - C(n-c, k) / C(n, k)
    def comb(a: int, b: int) -> float:
        if b < 0 or b > a:
            return 0.0
        return math.comb(a, b)
    denom = comb(n, k)
    if denom == 0:
        return 0.0
    return 1.0 - comb(n - c, k) / denom


def aggregate(results: list[dict]) -> dict:
    by_task: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_task[r["task_id"]].append(r)
    per_task = {}
    for tid, rs in by_task.items():
        n = len(rs)
        c = sum(1 for r in rs if r.get("oracle_passed"))
        lat = [r.get("agent_wall_s", 0) for r in rs]
        inp = [r.get("input_tokens") or 0 for r in rs]
        out = [r.get("output_tokens") or 0 for r in rs]
        ho_rs = [r for r in rs if r.get("heldout_passed") is not None]
        ho_c = sum(1 for r in ho_rs if r.get("heldout_passed"))
        per_task[tid] = {
            "n": n, "successes": c,
            "pass_at_1": (c / n) if n else 0.0,
            "pass_at_k": pass_at_k(n, c, min(k_n(n), n)),
            "avg_wall_s": sum(lat) / len(lat) if lat else 0.0,
            "avg_input_tokens": sum(inp) / len(inp) if inp else 0.0,
            "avg_output_tokens": sum(out) / len(out) if out else 0.0,
            "heldout_n": len(ho_rs),
            "heldout_passes": ho_c,
            "heldout_pass_rate": (ho_c / len(ho_rs)) if ho_rs else None,
        }
    total = len(results)
    succ = sum(1 for r in results if r.get("oracle_passed"))
    walls = [r.get("agent_wall_s", 0) for r in results]
    ho_all = [r for r in results if r.get("heldout_passed") is not None]
    ho_ok = sum(1 for r in ho_all if r.get("heldout_passed"))
    return {
        "total_runs": total,
        "total_successes": succ,
        "success_rate": (succ / total) if total else 0.0,
        "heldout_runs": len(ho_all),
        "heldout_passes": ho_ok,
        "heldout_pass_rate": (ho_ok / len(ho_all)) if ho_all else None,
        "per_task": per_task,
        "avg_wall_s": (sum(walls) / len(walls)) if walls else 0.0,
        "total_input_tokens": sum(r.get("input_tokens") or 0 for r in results),
        "total_output_tokens": sum(r.get("output_tokens") or 0 for r in results),
        "total_tool_calls": sum(r.get("tool_calls") or 0 for r in results),
        "total_failed_tool_calls": sum(r.get("failed_tool_calls") or 0 for r in results),
    }


def k_n(n: int) -> int:
    return n  # pass@k with k=n by default; report also shows pass@1
