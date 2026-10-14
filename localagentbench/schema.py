"""Task schema: load + validate YAML task files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_CATEGORIES = {
    "bugfix", "feature", "refactor", "test", "scientific",
    "algorithm", "cli", "data", "docs",
}
VALID_REPO_TYPES = {"fixture", "git"}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@dataclass
class RepoSpec:
    type: str  # fixture | git
    path: str | None = None   # fixture dir, relative to repo root
    url: str | None = None    # git URL
    ref: str | None = None    # commit/branch/tag


@dataclass
class OracleSpec:
    # Ordered shell commands run with cwd=workdir. All must exit 0.
    command: list[str] = field(default_factory=list)
    timeout_s: int = 120


@dataclass
class HeldoutSpec:
    # Extra tests injected AFTER the agent phase. The agent never sees them:
    # heldout/<id>/ is never copied to the workdir up front.
    path: str = ""
    command: list[str] = field(default_factory=list)
    timeout_s: int = 120


@dataclass
class Task:
    id: str
    title: str
    difficulty: str
    category: str
    prompt: str
    repo: RepoSpec
    oracle: OracleSpec
    heldout: HeldoutSpec | None = None
    timeout_s: int = 600
    max_turns: int = 25
    language: str = "python"
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "difficulty": self.difficulty,
            "category": self.category,
            "prompt": self.prompt,
            "repo": {"type": self.repo.type, "path": self.repo.path,
                     "url": self.repo.url, "ref": self.repo.ref},
            "oracle": {"command": self.oracle.command,
                       "timeout_s": self.oracle.timeout_s},
            "heldout": ({"path": self.heldout.path,
                         "command": self.heldout.command,
                         "timeout_s": self.heldout.timeout_s}
                        if self.heldout else None),
            "timeout_s": self.timeout_s,
            "max_turns": self.max_turns,
            "language": self.language,
            "tags": self.tags,
        }


def validate_task_dict(d: dict, source: str = "<dict>") -> list[str]:
    errors: list[str] = []
    for f in ("id", "title", "difficulty", "category", "prompt", "repo", "oracle"):
        if f not in d:
            errors.append(f"{source}: missing required field '{f}'")
    if errors:
        return errors
    if not isinstance(d["id"], str) or not ID_RE.match(d["id"]):
        errors.append(f"{source}: id must match {ID_RE.pattern}")
    if d.get("difficulty") not in VALID_DIFFICULTIES:
        errors.append(f"{source}: difficulty must be one of {sorted(VALID_DIFFICULTIES)}")
    if d.get("category") not in VALID_CATEGORIES:
        errors.append(f"{source}: category must be one of {sorted(VALID_CATEGORIES)}")
    if not isinstance(d.get("prompt"), str) or len(d["prompt"].strip()) < 10:
        errors.append(f"{source}: prompt must be a non-trivial string")
    repo = d.get("repo")
    if not isinstance(repo, dict) or repo.get("type") not in VALID_REPO_TYPES:
        errors.append(f"{source}: repo.type must be one of {sorted(VALID_REPO_TYPES)}")
    else:
        if repo["type"] == "fixture" and not repo.get("path"):
            errors.append(f"{source}: repo.path required for fixture tasks")
        if repo["type"] == "git" and not repo.get("url"):
            errors.append(f"{source}: repo.url required for git tasks")
    oracle = d.get("oracle")
    if not isinstance(oracle, dict) or not oracle.get("command"):
        errors.append(f"{source}: oracle.command must be a non-empty list of shell commands")
    elif not isinstance(oracle["command"], list) or not all(isinstance(c, str) for c in oracle["command"]):
        errors.append(f"{source}: oracle.command must be list[str]")
    ho = d.get("heldout")
    if ho is not None:
        if not isinstance(ho, dict) or not ho.get("path"):
            errors.append(f"{source}: heldout.path required when heldout is present")
        if not isinstance(ho.get("command"), list) or not ho.get("command") \
                or not all(isinstance(c, str) for c in ho["command"]):
            errors.append(f"{source}: heldout.command must be a non-empty list[str]")
    for f in ("timeout_s", "max_turns"):
        if f in d and (not isinstance(d[f], int) or d[f] <= 0):
            errors.append(f"{source}: {f} must be a positive int")
    return errors


def task_from_dict(d: dict) -> Task:
    repo = d["repo"]
    oc = d["oracle"]
    ho = d.get("heldout")
    return Task(
        id=d["id"], title=d["title"], difficulty=d["difficulty"],
        category=d["category"], prompt=d["prompt"],
        repo=RepoSpec(type=repo["type"], path=repo.get("path"),
                      url=repo.get("url"), ref=repo.get("ref")),
        oracle=OracleSpec(command=list(oc["command"]),
                          timeout_s=int(oc.get("timeout_s", 120))),
        heldout=(HeldoutSpec(path=ho["path"], command=list(ho["command"]),
                             timeout_s=int(ho.get("timeout_s", 120)))
                 if ho else None),
        timeout_s=int(d.get("timeout_s", 600)),
        max_turns=int(d.get("max_turns", 25)),
        language=str(d.get("language", "python")),
        tags=list(d.get("tags", [])),
    )


def check_task_repo(task: Task, repo_root: Path) -> list[str]:
    """Verify fixture/heldout dirs exist and heldout can't leak to the agent.

    Returns error strings (empty = ok). Held-out tests must live outside the
    fixture tree, otherwise they'd be copied into the workdir up front.
    """
    errors: list[str] = []
    if task.repo.type == "fixture":
        fx = (repo_root / (task.repo.path or "")).resolve()
        if not fx.is_dir():
            errors.append(f"{task.id}: fixture not found: {fx}")
    if task.heldout:
        ho = (repo_root / task.heldout.path).resolve()
        if not ho.is_dir():
            errors.append(f"{task.id}: heldout dir not found: {ho}")
        elif task.repo.type == "fixture":
            fx = (repo_root / (task.repo.path or "")).resolve()
            try:
                ho.relative_to(fx)
                errors.append(f"{task.id}: heldout dir must not live "
                              f"inside the fixture tree ({ho})")
            except ValueError:
                pass
    return errors


def load_task_file(path: Path) -> Task:
    with open(path, encoding="utf-8") as fh:
        d = yaml.safe_load(fh)
    if not isinstance(d, dict):
        raise ValueError(f"{path}: task YAML must be a mapping")
    errors = validate_task_dict(d, source=str(path))
    if errors:
        raise Valueeror("; ".join(errors)) if False else ValueError("; ".join(errors))
    return task_from_dict(d)


def load_tasks(tasks_dir: Path, task_ids: list[str] | None = None,
               categories: list[str] | None = None) -> list[Task]:
    files = sorted([*tasks_dir.glob("*.yaml"), *tasks_dir.glob("*.yml")])
    tasks = []
    for f in files:
        t = load_task_file(f)
        if task_ids and t.id not in task_ids:
            continue
        if categories and t.category not in categories:
            continue
        tasks.append(t)
    # deterministic order
    tasks.sort(key=lambda t: t.id)
    if task_ids:
        missing = set(task_ids) - {t.id for t in tasks}
        if missing:
            raise ValueError(f"unknown task ids: {sorted(missing)}")
    return tasks
