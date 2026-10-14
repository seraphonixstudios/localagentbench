"""Compare two result bundles (e.g. model A vs model B)."""
from __future__ import annotations

import json
from pathlib import Path


def _load(p: Path) -> dict:
    p = p / "summary.json" if p.is_dir() else p
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def compare(base: Path, other: Path) -> str:
    a = _load(base)
    b = _load(other)
    sa, sb = a.get("summary", {}), b.get("summary", {})
    lines = [
        "# LocalAgentBench comparison", "",
        f"base: `{sa.get('model')}` ({sa.get('agent')}, "
        f"{sa.get('total_successes')}/{sa.get('total_runs')} = "
        f"{sa.get('success_rate', 0):.1%})",
        f"other: `{sb.get('model')}` ({sb.get('agent')}, "
        f"{sb.get('total_successes')}/{sb.get('total_runs')} = "
        f"{sb.get('success_rate', 0):.1%})",
        "",
        "| task | base pass@1 | other pass@1 | delta |",
        "|---|---|---|---|",
    ]
    tasks = sorted(set(sa.get("per_task", {})) | set(sb.get("per_task", {})))
    for t in tasks:
        pa = sa.get("per_task", {}).get(t, {}).get("pass_at_1")
        pb = sb.get("per_task", {}).get(t, {}).get("pass_at_1")
        fa = f"{pa:.0%}" if pa is not None else "n/a"
        fb = f"{pb:.0%}" if pb is not None else "n/a"
        d = f"{(pb - pa):+.0%}" if pa is not None and pb is not None else "n/a"
        lines.append(f"| {t} | {fa} | {fb} | {d} |")
    return "\n".join(lines) + "\n"
