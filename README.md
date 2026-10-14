# LocalAgentBench

Open-source, **reproducible evaluation harness for coding agents**, local-first with **Ollama + OpenCode**.

- Tasks are versioned **YAML files** (`tasks/`) with a fixture repo (or git URL) + an **oracle** (commands that must exit 0).
- The runner isolates every run in a temp dir, invokes the agent **headless** (`opencode run`), captures trajectory/token/time signals, runs the oracle, and writes **structured JSON + raw logs**.
- Reports render to **Markdown + static HTML** (publish `results/<run>/site/` to GitHub Pages).
- Agent adapters are **pluggable** (`localagentbench/adapters/`) — OpenCode first, Claude Code / Aider later.

## Quickstart

```bash
# 1. Prereqs: Python 3.10+, Ollama, OpenCode
pip install -r requirements.txt
ollama serve                                  # in one terminal
ollama pull qwen2.5-coder:7b                  # small; or qwen3-coder:30b if you have VRAM
npm install --global @opencode/cli            # provides `opencode run`
# Optional: point OpenCode at local Ollama (see opencode.json.example)
cp opencode.json.example opencode.json

# 2. Sanity check
python -m localagentbench doctor
python -m localagentbench check               # validate tasks/
python -m localagentbench list-tasks

# 3. Dry run (no model needed — verifies harness plumbing)
python -m localagentbench run --agent mock --tasks ./tasks --out ./results/smoke --report

# 4. Real run (fully offline with Ollama)
python -m localagentbench run --model ollama/qwen2.5-coder:7b --tasks ./tasks --agent opencode --out ./results/r1 --report
# repeat 3x per task for pass@k:
python -m localagentbench run --model ollama/qwen2.5-coder:7b --repeat 3 --out ./results/r3 --report
```

CLI reference:

```
localagentbench run --model ollama/qwen3-coder:30b --tasks ./tasks --agent opencode
localagentbench run --task bugfix-001-off-by-one --keep-workdir   # debug one task
localagentbench report --results ./results/r1/summary.json --out ./results/r1/site
localagentbench compare --base ./results/r1 --other ./results/r2  # model A vs B
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
2. **Agent** (`adapters/opencode.py`): runs `opencode run --format json --model <m> --agent <a> "<prompt>"` with `cwd=workdir`. Captures stdout/stderr, wall time; best-effort parses NDJSON for token/tool signals. Missing binary → clear error (use `--agent mock` for plumbing tests).
3. **Oracle** (`oracle.py`): runs each command with timeout, records exit/stdout/stderr. `success = all(exit 0)`.
4. **Held-out oracle** (`isolation.inject_heldout`): after the agent phase, hidden tests from `heldout/<id>/` (never copied to the workdir up front) are injected and run. `success` requires both visible and held-out passes; visible-pass + held-out-fail is reported as an overfit/cheat signal. `check` rejects held-out dirs living inside the fixture tree.
4. **Metrics** (`metrics.py`): per-run latency, tokens (in/out when the trajectory exposes them), tool calls + failed calls (hallucination proxy); aggregate success rate, unbiased `pass@k` (Chen et al.), avg latency/tokens. `human_preference` field + `preference-template.csv` placeholder for later pairwise ranking.
5. **Reports** (`report.py`): `report.md` + static `index.html` from `summary.json`.

## Ollama notes (local-first)

- **Gate every model with the tool-call canary first**: `python -m localagentbench doctor --probe <model>`. A model that emits tool-call-shaped *text* instead of native `tool_calls` cannot drive the agentic loop — a full eval on it scores 0/12 by construction. Verified 2026-10: `qwen2.5-coder:7b` FAILS the canary (emits `{"name": ...}` as text), `qwen3:8b` PASSES.
- `doctor` lists local models and recommends coding ones: `qwen3-coder`, `qwen2.5-coder`, `deepseek-coder-v2`, `starcoder2`, `codellama`. Your box currently has `qwen3:8b` (general) — pull a coder model for real evals.
- Non-coding models (llama, dolphin, llava, whisper, embed) trigger a tool-calling warning; keep `max_turns` small for them.
- Quantization/context: check with `ollama show <model>`; 30b models need ~20GB+ VRAM/RAM — the harness never forces a pull, it uses what `ollama list` reports.
- Cloud providers later: pass any OpenCode model id (`anthropic/...`, `openai/...`) — the harness is provider-agnostic.

## Methodology

- One task = one isolated repo snapshot + deterministic oracle. Agent sees only the repo + prompt.
- Primary metric: **pass@1** (single attempt); with `--repeat k`, **pass@k** (unbiased estimator).
- Secondary: wall latency (total + per-turn), tokens in/out, tool-call counts + failures.
- Cost control: fixture tasks run offline in seconds; no network needed except `git` tasks.
- Known limitation (v0.1): visible oracle tests ship in-fixture (agent-visible). Mitigation: `heldout/` tests are injected post-run and never visible to the agent; `success` requires both. Remaining gap: `test`-category tasks (agent writes the tests) use structural checks rather than hidden behavior tests.

## Contributing

- Add a task: copy an existing `tasks/*.yaml` + `fixtures/<id>/`, keep oracle **deterministic and stdlib-only** where possible, add a reference fix to `scripts/verify_reference_solutions.py`, run `check` + a `--agent mock` smoke run, open a PR.
- Add an adapter: subclass the `AgentAdapter` protocol in `localagentbench/adapters/`, register in `runner.get_adapter()`.
- Publish results: PR the `results/<run>/summary.json` + site bundle; Pages workflow serves `site/`.

See `METHODOLOGY.md` for metric definitions.
