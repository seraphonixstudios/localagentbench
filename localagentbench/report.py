"""Markdown + HTML report generator from results JSON."""
from __future__ import annotations

import json
from pathlib import Path


def load_bundle(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def to_markdown(bundle: dict) -> str:
    s = bundle.get("summary", {})
    results = bundle.get("results", [])
    lines = [
        "# LocalAgentBench report", "",
        f"Model: `{s.get('model')}` · Agent: `{s.get('agent')}` · "
        f"Runs: {s.get('total_runs')} · Success rate: {s.get('success_rate', 0):.1%}",
        f"Avg wall: {s.get('avg_wall_s', 0):.1f}s · "
        f"Tokens in/out: {s.get('total_input_tokens')}/{s.get('total_output_tokens')} · "
        f"Tool calls: {s.get('total_tool_calls')} "
        f"(failed: {s.get('total_failed_tool_calls', s.get('total_failed_tool_calls', 0))})",
        "", "## Per-task", "",
        "| task | n | pass@1 | pass@k | heldout | avg wall |",
        "|---|---|---|---|---|---|",
    ]
    for tid, pt in sorted((s.get("per_task") or {}).items()):
        ho = pt.get("heldout_pass_rate")
        ho_s = f"{ho:.0%}" if ho is not None else "\u2014"
        lines.append(f"| {tid} | {pt['n']} | {pt['pass_at_1']:.0%} | "
                     f"{pt['pass_at_k']:.0%} | {ho_s} | {pt['avg_wall_s']:.1f}s |")
    lines += ["", "## Runs", "",
              "| run | task | success | heldout | wall | tokens | tools |",
              "|---|---|---|---|---|---|---|"]
    for r in results:
        tok = f"{r.get('input_tokens') or '-'}/{r.get('output_tokens') or '-'}"
        ho = r.get("heldout_passed")
        ho_s = ("PASS" if ho else "FAIL") if ho is not None else "\u2014"
        lines.append(f"| {r.get('run_id')} | {r.get('task_id')} | "
                     f"{'PASS' if r.get('success') else 'FAIL'} | {ho_s} | "
                     f"{r.get('agent_wall_s')}s | {tok} | {r.get('tool_calls')} |")
    lines += ["",
              "## Human preference (placeholder)",
              "Export run pairs for later pairwise ranking; see `preference-template.csv`.",
              ""]
    return "\n".join(lines)


def to_html(bundle: dict) -> str:
    md_rows = ""
    s = bundle.get("summary", {})
    for tid, pt in sorted((s.get("per_task") or {}).items()):
        md_rows += (f"<tr><td>{tid}</td><td>{pt['n']}</td>"
                    f"<td>{pt['pass_at_1']:.0%}</td><td>{pt['pass_at_k']:.0%}</td>"
                    f"<td>{pt['avg_wall_s']:.1f}s</td></tr>")
    run_rows = ""
    for r in bundle.get("results", []):
        cls = "pass" if r.get("success") else "fail"
        run_rows += (f"<tr class='{cls}'><td>{r.get('run_id')}</td>"
                     f"<td>{r.get('task_id')}</td>"
                     f"<td>{'PASS' if r.get('success') else 'FAIL'}</td>"
                     f"<td>{r.get('agent_wall_s')}s</td>"
                     f"<td>{r.get('tool_calls')}</td></tr>")
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>LocalAgentBench report</title>
<style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:.4rem .6rem}}
tr.pass td{{background:#e9f9ec}}tr.fail td{{background:#fdeaea}}</style>
</head><body>
<h1>LocalAgentBench report</h1>
<p>Model <code>{s.get('model')}</code> · Agent <code>{s.get('agent')}</code> ·
Runs {s.get('total_runs')} · Success {s.get('success_rate', 0):.1%} ·
Avg wall {s.get('avg_wall_s', 0):.1f}s</p>
<h2>Per-task</h2>
<table><tr><th>task</th><th>n</th><th>pass@1</th><th>pass@k</th><th>avg wall</th></tr>
{md_rows}</table>
<h2>Runs</h2>
<table><tr><th>run</th><th>task</th><th>result</th><th>wall</th><th>tools</th></tr>
{run_rows}</table>
<p><em>Static file — publish this folder to GitHub Pages.</em></p>
</body></html>"""


def write_reports(bundle_path: Path, out_dir: Path) -> list[Path]:
    bundle = load_bundle(bundle_path) if bundle_path.name.endswith(".json") and bundle_path.is_file() \
        else load_bundle(bundle_path / "summary.json")
    out_dir.mkdir(parents=True, exist_ok=True)
    md = out_dir / "report.md"
    html = out_dir / "index.html"
    md.write_text(to_markdown(bundle), encoding="utf-8")
    html.write_text(to_html(bundle), encoding="utf-8")
    # preference export placeholder
    pref = out_dir / "preference-template.csv"
    pref.write_text("run_a,run_b,task_id,preferred,notes\n", encoding="utf-8")
    return [md, html, pref]
