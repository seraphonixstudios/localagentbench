"""End-to-end: full run_suite() pipeline with the mock adapter.

Covers isolation + agent invoke + oracle + summary.json + reports without
needing Ollama or OpenCode installed.
"""
import json
from pathlib import Path

from localagentbench.compare import compare
from localagentbench.report import write_reports
from localagentbench.runner import run_suite
from localagentbench.schema import OracleSpec, RepoSpec, Task, load_tasks

REPO_ROOT = Path(__file__).resolve().parent.parent
TWO_TASKS = ["bugfix-001-off-by-one", "feature-001-wordcount-cli"]


def _load_result(run_dir: Path) -> dict:
    with open(run_dir / "result.json", encoding="utf-8") as fh:
        return json.load(fh)


def test_e2e_mock_runs_record_failures(tmp_path):
    """Mock agent changes nothing, so oracles fail — but the harness must
    record complete, well-formed results."""
    tasks = load_tasks(REPO_ROOT / "tasks", task_ids=TWO_TASKS)
    assert [t.id for t in tasks] == sorted(TWO_TASKS)
    out = tmp_path / "results"
    bundle = run_suite(tasks, "ollama/mock-model:8b", "mock",
                       REPO_ROOT, out, repeat=1)

    summary = bundle["summary"]
    assert summary["total_runs"] == 2
    assert summary["total_successes"] == 0
    assert summary["success_rate"] == 0.0
    for tid in TWO_TASKS:
        assert summary["per_task"][tid]["pass_at_1"] == 0.0

    run_dirs = [d for d in out.iterdir() if d.is_dir()]
    assert len(run_dirs) == 2
    for run_dir in run_dirs:
        for f in ("result.json", "agent.stdout.log",
                  "agent.stderr.log", "oracle.json"):
            assert (run_dir / f).is_file(), f"missing {f} in {run_dir}"
        rec = _load_result(run_dir)
        for key in ("run_id", "task_id", "model", "adapter",
                    "agent_wall_s", "tool_calls", "failed_tool_calls",
                    "oracle_passed", "success", "human_preference",
                    "oracle_commands"):
            assert key in rec, f"missing key {key}"
        assert rec["success"] is False
        assert rec["adapter"] == "mock"

    # summary.json round-trips the bundle
    with open(out / "summary.json", encoding="utf-8") as fh:
        assert json.load(fh)["summary"]["total_runs"] == 2


def _make_trivial_repo(repo: Path) -> None:
    fx = repo / "fixtures" / "trivial"
    (fx / "tests").mkdir(parents=True)
    (fx / "trivial.py").write_text(
        "def add(a, b):\n    return a + b\n", encoding="utf-8")
    (fx / "tests" / "test_trivial.py").write_text(
        "from trivial import add\n"
        "def test_add():\n    assert add(1, 2) == 3\n",
        encoding="utf-8")


def test_e2e_pass_path_report_and_compare(tmp_path):
    """A task whose oracle already passes exercises the success path,
    report rendering, and bundle comparison (repeat=2 -> pass@k)."""
    repo = tmp_path / "repo"
    _make_trivial_repo(repo)
    task = Task(
        id="trivial-001-pass", title="Trivially passing task",
        difficulty="easy", category="test", prompt="Nothing to do.",
        repo=RepoSpec(type="fixture", path="fixtures/trivial"),
        oracle=OracleSpec(command=["python -m pytest -q"]),
        timeout_s=120, max_turns=5)
    out = tmp_path / "out"
    bundle = run_suite([task], "ollama/mock-model:8b", "mock",
                       repo, out, repeat=2)

    summary = bundle["summary"]
    assert summary["success_rate"] == 1.0
    pt = summary["per_task"]["trivial-001-pass"]
    assert pt["n"] == 2 and pt["pass_at_1"] == 1.0 and pt["pass_at_k"] == 1.0

    outs = write_reports(out / "summary.json", out / "site")
    assert len(outs) == 3
    md = (out / "site" / "report.md").read_text(encoding="utf-8")
    html = (out / "site" / "index.html").read_text(encoding="utf-8")
    assert "trivial-001-pass" in md and "trivial-001-pass" in html

    cmp = compare(out / "summary.json", out / "summary.json")
    assert "+0%" in cmp


def _make_heldout_repo(repo: Path, heldout_body: str) -> Task:
    from localagentbench.schema import HeldoutSpec, OracleSpec, RepoSpec, Task
    fx = repo / "fixtures" / "ho"
    (fx / "tests").mkdir(parents=True)
    (fx / "mod.py").write_text("VALUE = 41\n", encoding="utf-8")
    (fx / "tests" / "test_vis.py").write_text(
        "from mod import VALUE\n"
        "def test_visible():\n    assert VALUE == 41\n", encoding="utf-8")
    ho = repo / "heldout" / "ho" / "heldout"
    ho.mkdir(parents=True)
    (ho / "test_hidden.py").write_text(heldout_body, encoding="utf-8")
    return Task(
        id="ho-001-task", title="heldout demo", difficulty="easy",
        category="bugfix", prompt="Nothing to do.",
        repo=RepoSpec(type="fixture", path="fixtures/ho"),
        oracle=OracleSpec(command=["python -m pytest -q tests"]),
        heldout=HeldoutSpec(path="heldout/ho",
                            command=["python -m pytest -q heldout"]),
        timeout_s=120, max_turns=5)


def test_e2e_heldout_pass(tmp_path):
    repo = tmp_path / "repo"
    task = _make_heldout_repo(
        repo, "from mod import VALUE\n"
              "def test_hidden():\n    assert VALUE == 41\n")
    out = tmp_path / "out"
    bundle = run_suite([task], "ollama/mock-model:8b", "mock",
                       repo, out, repeat=1)
    rec = bundle["results"][0]
    assert rec["oracle_passed"] is True
    assert rec["heldout_passed"] is True
    assert rec["success"] is True
    assert (out / rec["run_id"] / "heldout.json").is_file()
    assert bundle["summary"]["heldout_pass_rate"] == 1.0


def test_e2e_heldout_catches_cheat(tmp_path):
    """Visible tests pass but hidden tests fail -> success must be False."""
    repo = tmp_path / "repo"
    task = _make_heldout_repo(
        repo, "from mod import VALUE\n"
              "def test_hidden():\n    assert VALUE == 42\n")
    out = tmp_path / "out"
    bundle = run_suite([task], "ollama/mock-model:8b", "mock",
                       repo, out, repeat=1)
    rec = bundle["results"][0]
    assert rec["oracle_passed"] is True
    assert rec["heldout_passed"] is False
    assert rec["success"] is False
