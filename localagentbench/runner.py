"""Core runner: task loop with isolation, agent invoke, oracle, JSON output."""
from __future__ import annotations

import json
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .adapters.mock import MockAdapter
from .adapters.opencode import OpenCodeAdapter
from .isolation import inject_heldout, prepare_workdir
from .metrics import aggregate
from .ollama import normalize_model, strip_provider, toolcall_warning
from .oracle import run_oracle
from .schema import Task


def get_adapter(name: str, agent: str = "build"):
    if name == "opencode":
        return OpenCodeAdapter(agent=agent)
    if name == "mock":
        return MockAdapter()
    raise ValueError(f"unknown agent adapter '{name}' (choose: opencode, mock)")


def run_single_task(task: Task, model: str, adapter, repo_root: Path,
                    out_dir: Path, keep_workdir: bool = False,
                    oracle_timeout_s: int | None = None) -> dict:
    run_id = f"{task.id}-{uuid.uuid4().hex[:8]}"
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix=f"lab-{task.id}-"))

    record: dict = {
        "run_id": run_id, "task_id": task.id, "task_title": task.title,
        "difficulty": task.difficulty, "category": task.category,
        "model": model, "adapter": getattr(adapter, "name", "?"),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "workdir": str(workdir),
        # human-preference placeholder: fill in later via pairwise UI
        "human_preference": None,
    }
    warn = toolcall_warning(model)
    if warn:
        record["model_warning"] = warn
    try:
        prepare_workdir(task, repo_root, dest=workdir)
        # --- agent phase ---
        t0 = time.time()
        agent_res = adapter.run(task.prompt, str(workdir), model,
                                task.timeout_s, task.max_turns)
        agent_wall = time.time() - t0
        record.update({
            "agent_exit_code": agent_res.exit_code,
            "agent_wall_s": round(agent_wall, 3),
            "agent_wall_per_turn": round(agent_wall / max(task.max_turns, 1), 3),
            "tool_calls": agent_res.tool_calls,
            "failed_tool_calls": agent_res.failed_tool_calls,
            "input_tokens": agent_res.input_tokens,
            "output_tokens": agent_res.output_tokens,
            "agent_stderr_tail": (agent_res.stderr or "")[-2000:],
        })
        (run_dir / "agent.stdout.log").write_text(agent_res.stdout or "", encoding="utf-8")
        (run_dir / "agent.stderr.log").write_text(agent_res.stderr or "", encoding="utf-8")
        # --- oracle phase (visible tests) ---
        oc = run_oracle(task.oracle.command, str(workdir),
                        oracle_timeout_s or task.oracle.timeout_s)
        record.update({
            "oracle_passed": oc.passed,
            "oracle_wall_s": oc.wall_s,
            "oracle_commands": oc.commands,
            "success": bool(oc.passed),
        })
        (run_dir / "oracle.json").write_text(
            json.dumps({"passed": oc.passed, "commands": oc.commands}, indent=2),
            encoding="utf-8")
        # --- held-out phase: inject hidden tests post-run, then run them ---
        record["heldout_passed"] = None
        if task.heldout:
            injected = inject_heldout(task, repo_root, workdir)
            hoc = run_oracle(task.heldout.command, str(workdir),
                             task.heldout.timeout_s)
            record.update({
                "heldout_injected": injected,
                "heldout_passed": hoc.passed,
                "heldout_wall_s": hoc.wall_s,
                "heldout_commands": hoc.commands,
                # visible-pass + heldout-fail == overfit/cheat signal
                "success": bool(oc.passed and hoc.passed),
            })
            (run_dir / "heldout.json").write_text(
                json.dumps({"passed": hoc.passed,
                            "commands": hoc.commands}, indent=2),
                encoding="utf-8")
    except Exception as e:  # harness-level failure (bad fixture, git error…)
        record.update({"success": False, "oracle_passed": False,
                       "harness_error": f"{type(e).__name__}: {e}"})
    finally:
        record["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_dir / "result.json").write_text(json.dumps(record, indent=2),
                                             encoding="utf-8")
        if not keep_workdir:
            import shutil
            shutil.rmtree(workdir, ignore_errors=True)
        else:
            record["kept_workdir"] = str(workdir)
            (run_dir / "result.json").write_text(json.dumps(record, indent=2),
                                                 encoding="utf-8")
    return record


def run_suite(tasks: list[Task], model: str, agent_name: str, repo_root: Path,
              out_dir: Path, repeat: int = 1, keep_workdir: bool = False,
              task_timeout_override: int | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    adapter = get_adapter(agent_name)
    if task_timeout_override:
        for t in tasks:
            t.timeout_s = task_timeout_override
    results: list[dict] = []
    suite_id = uuid.uuid4().hex[:8]
    for i in range(repeat):
        for task in tasks:
            rec = run_single_task(task, model, adapter, repo_root, out_dir,
                                  keep_workdir=keep_workdir)
            rec["repetition"] = i + 1
            (out_dir / rec["run_id"] / "result.json").write_text(
                json.dumps(rec, indent=2), encoding="utf-8")
            results.append(rec)
            status = "PASS" if rec.get("success") else "FAIL"
            print(f"[{status}] {task.id} run={rec['run_id']} "
                  f"agent={rec.get('agent_wall_s')}s "
                  f"oracle={rec.get('oracle_wall_s')}s", flush=True)
    summary = aggregate(results)
    summary.update({
        "suite_id": suite_id, "model": model, "agent": agent_name,
        "harness_version": __version__, "repeat": repeat,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    })
    (out_dir / "summary.json").write_text(json.dumps(
        {"summary": summary, "results": results}, indent=2), encoding="utf-8")
    return {"summary": summary, "results": results}
