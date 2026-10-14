# Changelog

## [0.1.0] - 2026-10-15

Initial public release.

- Harness: YAML task schema, isolated runner, OpenCode + mock adapters, Ollama helpers + tool-call canary, metrics (pass@1/pass@k, latency, tokens, tool calls, held-out rates), Markdown/HTML reports, run comparison, CLI.
- 14 tasks across bugfix/feature/refactor/test/scientific/algorithm/data, all reference-solvable; held-out oracles for 4 tasks.
- Baselines: `qwen3:8b` 20/42 pass@1 (47.6%, 8/14 pass@3=100%); `qwen2.5-coder:7b` 0/12 (no native tool calls — documented, gated by canary).
- CI on Ubuntu + Windows; GitHub Pages publishing.
