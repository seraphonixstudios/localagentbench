# LocalAgentBench

[![CI](https://github.com/seraphonixstudios/localagentbench/actions/workflows/ci.yml/badge.svg)](https://github.com/seraphonixstudios/localagentbench/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)

Open-source, **reproducible evaluation harness for coding agents**, local-first with **Ollama + OpenCode**.

- Tasks are versioned **YAML files** (`tasks/`) with a fixture repo (or git URL) + a **deterministic oracle** (commands that must exit 0).
- The runner isolates every run in a temp dir, invokes the agent **headless** (`opencode run`), captures trajectory/token/time signals, runs the oracle **plus hidden held-out tests**, and writes **structured JSON + raw logs**.
- Reports render to **Markdown + static HTML** (publish `results/<run>/site/` to GitHub Pages).
- Agent adapters are **pluggable** (`localagentbench/adapters/`) — OpenCode first, Claude Code / Aider later.

## Latest results

`qwen3:8b` (local, RTX 5060 Ti 8GB), 14 tasks × 3 reps = 42 runs:

| task | pass@1 | pass@3 |
|---|---|---|
| algorithm-001, calib-002, feature-001, feature-002, scientific-002 | 100% | 100% |
| bugfix-001, data-001 | 67% | 100% |
| test-001 | 33% | 100% |
| bugfix-002, calib-001, refactor-001/002, scientific-001, test-002 | 0% | 0% |

**20/42 (47.6%) pass@1; 8/14 tasks pass@3 = 100%.** `qwen2.5-coder:7b` scores 0/12 — it emits tool-call-shaped *text* instead of native `tool_calls` and cannot drive the loop (see canary below). Full reports: [`results/`](results/).

## Quickstart

```bash
# 1. Prereqs: Python 3.10+, Ollama, OpenCode
pip install -r requirements.txt
ollama serve
npm install --global @opencode/cli            # provides `opencode run`

# 2. Pick a model AND gate it with the tool-call canary (30s).
#    A model that fails this cannot score above 0 — don't burn an eval on it.
ollama pull qwen3:8b
python -m localagentbench doctor --probe qwen3:8b

# 3. Sanity check
python -m localagentbench doctor
python -m localagentbench check               # validate tasks/ + held-out separation
python -m localagentbench list-tasks

# 4. Dry run (no model needed — verifies harness plumbing)
python -m localagentbench run --agent mock --model ollama/ci-mock:0b --tasks ./tasks --out ./results/smoke --report

# 5. Real run (fully offline with Ollama)
python -m localagentbench run --model ollama/qwen3:8b --tasks ./tasks --agent opencode --out ./results/r1 --report
# repeat 3x per task for pass@k:
python -m localagentbench run --model ollama/qwen3:8b --repeat 3 --out ./results/r3 --report
```

CLI reference:

```
localagentbench run --model ollama/qwen3:8b --tasks ./tasks --agent opencode
localagentbench run --task bugfix-001-off-by-one --keep-workdir   # debug one task
localagentbench report --results ./results/r1/summary.json --out ./results/r1/site
localagentbench compare --base ./results/r1 --other ./results/r2  # model A vs B
localagentbench doctor --probe <model>                            # tool-call canary
```

## Task format

```yaml
id: bugfix-001-off-by-one        # ^[a-z0-9]+(-[a-z0-9]+)*$
title: Fix off-by-one in median()
difficulty: easy                  # easy | medium | hard
category: bugfix                  # bugfix feature refactor test scientific algorithm cli data docs
language: python
prompt: |                         # instruction given to the agent
  Fix median() so ...
repo:
  type: fixture                   # fixture | git
  path: fixtures/bugfix-001       # or url/ref for git
oracle:
  command:                        # ALL must exit 0, run with cwd=workdir
    - python -m pytest -q
  timeout_s: 60
heldout:                          # optional hidden tests (never shown to agent)
  path: heldout/bugfix-001        # lives OUTSIDE fixtures/, injected post-run
  command:
    - python -m pytest -q heldout
  timeout_s: 60
timeout_s: 300                    # agent timeout
max_turns: 15
```

Validate: `python -m localagentbench check`.

## How it works

1. **Isolation** (`isolation.py`): per-run temp dir; fixture copied or `git clone --depth 1` + checkout. No cross-run contamination.
2. **Agent** (`adapters/opencode.py`): runs the resolved `opencode` binary headless with `cwd=workdir`. Captures stdout/stderr, wall time; parses the NDJSON event stream for token/tool signals. Missing binary → clear error (use `--agent mock` for plumbing tests).
3. **Oracle** (`oracle.py`): runs each command with timeout, records exit/stdout/stderr. UTF-8 capture with replacement (Windows-safe).
4. **Held-out oracle** (`isolation.inject_heldout`): after the agent phase, hidden tests from `heldout/<id>/` (never copied to the workdir up front) are injected and run. `success` requires both visible and held-out passes; visible-pass + held-out-fail is reported as an overfit/cheat signal. `check` rejects held-out dirs living inside the fixture tree.
5. **Metrics** (`metrics.py`): per-run latency, tokens (in/out when the trajectory exposes them), tool calls + failed calls (hallucination proxy); aggregate success rate, unbiased `pass@k` (Chen et al.), avg latency/tokens, held-out rates. `human_preference` field + `preference-template.csv` placeholder for later pairwise ranking.
6. **Reports** (`report.py`): `report.md` + static `index.html` from `summary.json`.

## Ollama notes (local-first)

- **Gate every model with the canary first**: `doctor --probe <model>`. Verified 2026-10: `qwen2.5-coder:7b` FAILS (text-shaped pseudo-calls), `qwen3:8b` PASSES.
- `doctor` lists local models and recommends coding ones (`qwen3-coder`, `qwen2.5-coder`, `deepseek-coder-v2`, ...). 30B models need ~20GB VRAM; on 8GB cards, probe small models and trust the canary over the name.
- Non-coding models (dolphin, llava, whisper, embed) trigger a tool-calling warning; keep `max_turns` small for them.
- Cloud providers later: pass any OpenCode model id (`anthropic/...`, `openai/...`) — the harness is provider-agnostic. See `opencode.json.example` for Ollama wiring.

## Project structure

```
tasks/            task YAML (22; see CHANGELOG for batches)
fixtures/         agent-visible repos
heldout/          hidden tests for 11 tasks (injected post-run)
localagentbench/  harness (schema, runner, adapters, metrics, report, cli)
tests/            unit + end-to-end tests
scripts/          solvability proofs, metric backfill, model probes
results/          run bundles (git-ignored) -> site/ for Pages
.github/          CI (Ubuntu+Windows) + Pages + issue/PR templates
```

## Methodology

- One task = one isolated repo snapshot + deterministic oracle. Agent sees only the repo + prompt.
- Primary metric: **pass@1** (single attempt); with `--repeat k`, **pass@k** (unbiased estimator).
- Secondary: wall latency (total + per-turn), tokens in/out, tool-call counts + failures, held-out pass rate.
- Cost control: fixture tasks run offline in seconds; no network needed except `git` tasks.
- Known gap: `test`-category tasks (agent writes the tests) use structural checks rather than hidden behavior tests.

See [`METHODOLOGY.md`](METHODOLOGY.md) for metric definitions.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). TL;DR: deterministic oracles, stdlib-only fixtures, reference solution in `scripts/verify_reference_solutions.py`, green CI. Task proposals welcome via the [new-task issue form](.github/ISSUE_TEMPLATE/new_task.md); results via the [results form](.github/ISSUE_TEMPLATE/results.md).

## License

MIT — see [LICENSE](LICENSE). Security notes: [SECURITY.md](SECURITY.md). Changelog: [CHANGELOG.md](CHANGELOG.md).
