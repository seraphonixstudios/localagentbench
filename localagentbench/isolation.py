"""Isolated workspaces: temp dir per run, fixture copy or git clone."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from .schema import Task


def prepare_workdir(task: Task, repo_root: Path,
                    dest: Path | None = None) -> Path:
    """Copy fixture or clone git repo into an isolated dir. Returns workdir."""
    if dest is None:
        dest = Path(tempfile.mkdtemp(prefix=f"lab-{task.id}-"))
    else:
        dest.mkdir(parents=True, exist_ok=True)
    if task.repo.type == "fixture":
        if not task.repo.path:
            raise ValueError(f"task {task.id}: fixture path missing")
        src = (repo_root / task.repo.path).resolve()
        if not src.is_dir():
            raise FileNotFoundError(f"task {task.id}: fixture not found: {src}")
        for item in src.iterdir():
            if item.name == "__pycache__" or item.suffix == ".pyc":
                continue  # never ship bytecode to the agent workdir
            s, d = item, dest / item.name
            if item.is_dir():
                shutil.copytree(s, d, dirs_exist_ok=True,
                                ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copy2(s, d)
    elif task.repo.type == "git":
        if not task.repo.url:
            raise ValueError(f"task {task.id}: git url missing")
        subprocess.run(["git", "clone", "--depth", "1", task.repo.url,
                        str(dest)], check=True, capture_output=True)
        if task.repo.ref:
            subprocess.run(["git", "checkout", task.repo.ref], cwd=dest,
                           check=True, capture_output=True)
    else:
        raise ValueError(f"task {task.id}: unknown repo type {task.repo.type}")
    return dest


def inject_heldout(task: Task, repo_root: Path, workdir: Path) -> list[str]:
    """Copy held-out tests into the workdir AFTER the agent phase.

    Returns the list of injected top-level names (for the run record).
    The agent never sees these files: they live outside the fixture tree
    and are only copied here, post-run, before the held-out oracle runs.
    """
    if not task.heldout:
        return []
    src = (repo_root / task.heldout.path).resolve()
    if not src.is_dir():
        raise FileNotFoundError(f"task {task.id}: heldout not found: {src}")
    try:
        src.relative_to(workdir.resolve())
        inside = True
    except ValueError:
        inside = False
    if inside:
        raise ValueError(f"task {task.id}: heldout dir inside workdir?!")
    injected: list[str] = []
    for item in src.iterdir():
        if item.name == "__pycache__" or item.suffix == ".pyc":
            continue
        s, d = item, workdir / item.name
        if item.is_dir():
            shutil.copytree(s, d, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(s, d)
        injected.append(item.name)
    return injected
