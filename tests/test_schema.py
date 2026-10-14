import pytest
import yaml

from localagentbench.schema import (load_task_file, load_tasks,
                                    validate_task_dict)
from pathlib import Path

TASKS = Path(__file__).resolve().parent.parent / "tasks"


def test_all_tasks_validate():
    files = sorted([*TASKS.glob("*.yaml"), *TASKS.glob("*.yml")])
    assert len(files) >= 5, "expected at least 5 starter tasks"
    for f in files:
        d = yaml.safe_load(open(f, encoding="utf-8"))
        assert validate_task_dict(d, str(f)) == [], f"{f} invalid"


def test_task_ids_unique_and_sorted():
    tasks = load_tasks(TASKS)
    ids = [t.id for t in tasks]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids)


def test_invalid_rejected():
    errs = validate_task_dict({"id": "x"}, source="t")
    assert any("missing" in e for e in errs)


def test_heldout_validates(tmp_path):
    base = {"id": "h-001", "title": "t", "difficulty": "easy",
            "category": "bugfix", "prompt": "do the thing now please",
            "repo": {"type": "fixture", "path": "fixtures/h"},
            "oracle": {"command": ["python -m pytest -q"]}}
    assert validate_task_dict(base, "t") == []
    bad = dict(base, heldout={"command": ["x"]})
    assert any("heldout.path" in e for e in validate_task_dict(bad, "t"))
    bad2 = dict(base, heldout={"path": "heldout/h"})
    assert any("heldout.command" in e for e in validate_task_dict(bad2, "t"))


def test_heldout_leak_check(tmp_path):
    from localagentbench.schema import check_task_repo, task_from_dict
    fx = tmp_path / "fixtures" / "h"
    (fx / "tests").mkdir(parents=True)
    ho = tmp_path / "heldout" / "h"
    ho.mkdir(parents=True)
    base = {"id": "h-001", "title": "t", "difficulty": "easy",
            "category": "bugfix", "prompt": "do the thing now please",
            "repo": {"type": "fixture", "path": "fixtures/h"},
            "oracle": {"command": ["python -m pytest -q"]},
            "heldout": {"path": "heldout/h",
                        "command": ["python -m pytest -q heldout"]}}
    t = task_from_dict(base)
    assert check_task_repo(t, tmp_path) == []
    # heldout inside the fixture tree must be rejected
    bad = task_from_dict(dict(base, heldout={"path": "fixtures/h/heldout",
                                             "command": ["x"]}))
    (fx / "heldout").mkdir(exist_ok=True)
    assert any("must not live" in e for e in check_task_repo(bad, tmp_path))
