# Contributing to LocalAgentBench

## Ways to contribute

- **New tasks** (highest value): bugfix/feature/refactor/test/scientific tasks with deterministic oracles.
- **Held-out tests** for tasks that only have visible oracles.
- **Agent adapters** (Aider, Claude Code, ...): implement the `AgentAdapter` protocol.
- **Docs, bug reports, benchmark results** on your own hardware.

## Adding a task

1. Copy an existing pair: `tasks/<id>.yaml` + `fixtures/<id>/`.
2. Rules for the fixture:
   - Self-contained, **stdlib-only** where possible (no network, no downloads).
   - Oracle must be **deterministic**: same repo state → same verdict, every run.
   - Keep prompts precise: file names, function signatures, exact expected behavior.
3. Add a reference solution to `scripts/verify_reference_solutions.py` proving the task is solvable.
4. Optionally add hidden tests under `heldout/<id>/heldout/` + a `heldout:` block in the YAML (must live **outside** `fixtures/`).
5. Run the gate before opening a PR:
   ```bash
   python -m localagentbench check
   python -m pytest tests/ -q
   python scripts/verify_reference_solutions.py
   ```

## Adding an adapter

1. Implement `run(prompt, workdir, model, timeout_s, max_turns, **kwargs) -> AgentResult` (see `localagentbench/adapters/__init__.py`).
2. Register it in `runner.get_adapter()`.
3. Add `--agent <name>` to the CLI choices and a test that runs it (a mock or a 30s canary — no heavyweight downloads in tests).

## Pull requests

- One logical change per PR, with a clear description and test evidence.
- CI must pass on Ubuntu + Windows (`check`, `pytest`, solvability, mock smoke).
- Be kind and precise in review; see `CODE_OF_CONDUCT.md`.
