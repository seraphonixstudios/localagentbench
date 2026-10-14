"""CLI: `localagentbench run ...`, `report`, `list-tasks`, `check`, `doctor`."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .ollama import (RECOMMENDED_CODING_MODELS, available_model_names,
                     normalize_model, ollama_available, recommend_model,
                     toolcall_warning)
from .report import write_reports
from .runner import run_suite
from .schema import load_tasks


def _repo_root() -> Path:
    return Path.cwd()


def cmd_run(args) -> int:
    tasks_dir = Path(args.tasks)
    out_dir = Path(args.out)
    tasks = load_tasks(tasks_dir, task_ids=args.task, categories=args.category)
    if not tasks:
        print("no tasks matched", file=sys.stderr)
        return 2
    model = normalize_model(args.model) if args.model else None
    if model is None:
        rec = recommend_model()
        if rec is None:
            print("No Ollama models found. Start Ollama (`ollama serve`) and "
                  "`ollama pull qwen2.5-coder:7b`, or pass --model explicitly.",
                  file=sys.stderr)
            return 2
        model = normalize_model(rec)
        print(f"no --model given; using detected model {model}")
    warn = toolcall_warning(model)
    if warn:
        print(f"warning: {warn}", file=sys.stderr)
    print(f"LocalAgentBench v{__version__}: {len(tasks)} task(s), "
          f"model={model}, agent={args.agent}, repeat={args.repeat}")
    bundle = run_suite(tasks, model, args.agent, _repo_root(), out_dir,
                       repeat=args.repeat, keep_workdir=args.keep_workdir,
                       task_timeout_override=args.timeout)
    s = bundle["summary"]
    print(f"done: {s['total_successes']}/{s['total_runs']} "
          f"({s['success_rate']:.1%}) -> {out_dir / 'summary.json'}")
    if args.report:
        outs = write_reports(out_dir / "summary.json", out_dir / "site")
        print("reports: " + ", ".join(str(p) for p in outs))
    return 0


def cmd_list_tasks(args) -> int:
    tasks = load_tasks(Path(args.tasks))
    for t in tasks:
        print(f"{t.id:28s} {t.difficulty:6s} {t.category:10s} {t.title}")
    return 0


def cmd_check(args) -> int:
    from .schema import check_task_repo, load_task_file
    tasks_dir = Path(args.tasks)
    repo_root = _repo_root()
    files = sorted([*tasks_dir.glob("*.yaml"), *tasks_dir.glob("*.yml")])
    bad = 0
    for f in files:
        try:
            t = load_task_file(f)
            repo_errors = check_task_repo(t, repo_root)
            if repo_errors:
                raise ValueError("; ".join(repo_errors))
            ho = " +heldout" if t.heldout else ""
            print(f"OK   {f.name}{ho}")
        except Exception as e:
            bad += 1
            print(f"FAIL {f.name}: {e}")
    return 1 if bad else 0


def cmd_doctor(_args) -> int:
    print(f"localagentbench {__version__}")
    print(f"ollama binary: {'found' if ollama_available() else 'MISSING'}")
    models = available_model_names()
    print(f"ollama models ({len(models)}): {', '.join(models) if models else '(none)'}")
    rec = recommend_model(models)
    print(f"recommended: {rec or '(none available)'}")
    print(f"good coding choices: {', '.join(RECOMMENDED_CODING_MODELS)}")
    try:
        import yaml  # noqa
        print("pyyaml: ok")
    except ImportError:
        print("pyyaml: MISSING (pip install pyyaml)")
    from .adapters.opencode import opencode_binary
    print(f"opencode: {opencode_binary() or 'MISSING — npm i -g @opencode/cli'}")
    if _args.probe:
        from .ollama import probe_tool_calls
        print(f"probing tool calls for {_args.probe} ...")
        res = probe_tool_calls(_args.probe)
        print(f"native tool calls: {'SUPPORTED' if res['supported'] else 'NOT SUPPORTED'}")
        print(f"detail: {res['detail']}")
        if not res["supported"]:
            print("This model cannot drive the agentic loop; pick another "
                  "model before running a full eval.")
    return 0


def cmd_report(args) -> int:
    outs = write_reports(Path(args.results), Path(args.out))
    print("wrote: " + ", ".join(str(p) for p in outs))
    return 0


def cmd_compare(args) -> int:
    from .compare import compare
    print(compare(Path(args.base), Path(args.other)), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="localagentbench",
                                description="Reproducible eval harness for coding agents (local-first)")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run tasks")
    r.add_argument("--model", default=None,
                   help="e.g. ollama/qwen3-coder:30b (default: auto-detect)")
    r.add_argument("--tasks", default="./tasks")
    r.add_argument("--agent", default="opencode",
                   choices=["opencode", "mock"])
    r.add_argument("--out", default="./results/latest")
    r.add_argument("--task", action="append", default=None,
                   help="run only this task id (repeatable)")
    r.add_argument("--category", action="append", default=None)
    r.add_argument("--repeat", type=int, default=1,
                   help="repetitions per task (for pass@k)")
    r.add_argument("--timeout", type=int, default=None,
                   help="override agent timeout seconds per task")
    r.add_argument("--keep-workdir", action="store_true")
    r.add_argument("--report", action="store_true",
                   help="also write markdown+HTML reports")
    r.set_defaults(func=cmd_run)

    l = sub.add_parser("list-tasks", help="list tasks")
    l.add_argument("--tasks", default="./tasks")
    l.set_defaults(func=cmd_list_tasks)

    c = sub.add_parser("check", help="validate task YAML")
    c.add_argument("--tasks", default="./tasks")
    c.set_defaults(func=cmd_check)

    d = sub.add_parser("doctor", help="check ollama/opencode setup")
    d.add_argument("--probe", default=None, metavar="MODEL",
                   help="probe whether MODEL supports native tool calls "
                        "(30s canary before a full eval)")
    d.set_defaults(func=cmd_doctor)

    rp = sub.add_parser("report", help="render reports from results")
    rp.add_argument("--results", default="./results/latest/summary.json")
    rp.add_argument("--out", default="./results/latest/site")
    rp.set_defaults(func=cmd_report)

    cmp = sub.add_parser("compare", help="compare two result bundles")
    cmp.add_argument("--base", required=True)
    cmp.add_argument("--other", required=True)
    cmp.set_defaults(func=cmd_compare)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
