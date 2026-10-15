# Changelog

## [Unreleased]

- Aider: declare local context windows via litellm metadata (kills the
  unknown-model warning, bounds history to the real 4k window) and default
  `OLLAMA_API_BASE`. Verified warnings gone; did not flip the refactor-002
  600s dithering failure (model-side reasoning loop, zero edits).
- Aider × 22-task eval: 13/22 (59.1%) vs OpenCode 5/22 on the same model;
  9 tasks flip to Aider, 1 to OpenCode, refactors fail for both.
- Full 22-task `qwen3:8b` eval: 5/22; 3 passes hidden-test-confirmed, 2
  partial solutions caught by visible/hidden split; 2 held-out oracles
  strengthened (data-002 type-key row, feature-001 CLI test); public
  leaderboard refreshed.
- Aider adapter (`--agent aider`, incl. uv-bin resolution and transcript
  parsing); adapter registry + CLI choices extended.
- 8 new tasks (22 total): bugfix-003 (thread race), refactor-003 (validators),
  data-002 (dirty JSONL), cli-001 (retry + exit codes), scientific-003
  (stable softmax), algorithm-002 (thread-safe LRU), feature-003 (config
  loader), test-003 (retry tests). Held-out oracles for 7 of the 8.

## [0.1.0] - 2026-10-15

Initial public release.

- Harness: YAML task schema, isolated runner, OpenCode + mock adapters, Ollama helpers + tool-call canary, metrics (pass@1/pass@k, latency, tokens, tool calls, held-out rates), Markdown/HTML reports, run comparison, CLI.
- 14 tasks across bugfix/feature/refactor/test/scientific/algorithm/data, all reference-solvable; held-out oracles for 4 tasks.
- Baselines: `qwen3:8b` 20/42 pass@1 (47.6%, 8/14 pass@3=100%); `qwen2.5-coder:7b` 0/12 (no native tool calls — documented, gated by canary).
- CI on Ubuntu + Windows; GitHub Pages publishing.
