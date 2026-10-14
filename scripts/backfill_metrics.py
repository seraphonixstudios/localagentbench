"""Backfill per-run metrics by re-parsing stored agent.stdout.log files.

Usage: python scripts/backfill_metrics.py results/<run>
Rewrites each result.json and summary.json using the current trajectory
parser (useful when the parser improves after a run).
"""
import json
import pathlib
import sys

sys.path.insert(0, ".")

from localagentbench.adapters.opencode import parse_jsonl_trajectory
from localagentbench.metrics import aggregate

base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "results/latest")
results = []
for d in sorted(base.iterdir()):
    if not d.is_dir() or not (d / "result.json").is_file():
        continue
    rec = json.load(open(d / "result.json", encoding="utf-8"))
    log = d / "agent.stdout.log"
    if log.is_file():
        sig = parse_jsonl_trajectory(log.read_text(errors="replace"))
        rec["tool_calls"] = sig["tool_calls"]
        rec["failed_tool_calls"] = sig["failed_tool_calls"]
        rec["input_tokens"] = sig["input_tokens"]
        rec["output_tokens"] = sig["output_tokens"]
    json.dump(rec, open(d / "result.json", "w", encoding="utf-8"), indent=2)
    results.append(rec)

summary = aggregate(results)
old = json.load(open(base / "summary.json", encoding="utf-8"))
summary.update({k: old["summary"][k] for k in
                ("suite_id", "model", "agent", "harness_version",
                 "repeat", "finished_at") if k in old["summary"]})
json.dump({"summary": summary, "results": results},
          open(base / "summary.json", "w", encoding="utf-8"), indent=2)
print(f"backfilled {len(results)} runs: "
      f"{summary['total_successes']}/{summary['total_runs']} passing, "
      f"{summary['total_tool_calls']} tool calls "
      f"({summary['total_failed_tool_calls']} failed), "
      f"{summary['total_input_tokens']}/{summary['total_output_tokens']} tok in/out")
