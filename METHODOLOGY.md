# Methodology notes

## Metrics

- **success (per run)**: all oracle commands exit 0 in the isolated workdir.
- **pass@1**: fraction of runs passing (equals mean success when repeat=1).
- **pass@k** (repeat>1): unbiased estimator from Chen et al. (2021),
  `1 - C(n-c, k)/C(n, k)`, computed per task with k=n by default.
- **latency**: `agent_wall_s` (subprocess wall time) + `agent_wall_per_turn`
  (wall / max_turns, a comparable proxy); `oracle_wall_s` separately.
- **tokens**: best-effort parse of `opencode run --format json` NDJSON
  (`usage` / input/output keys). Often `null` for local models — the harness
  records nulls honestly instead of estimating. For exact Ollama counts, run
  with `OLLAMA_DEBUG` or scrape `ollama ps` (roadmap).
- **tool calls**: parsed from trajectory when exposed; `failed_tool_calls`
  (error-status events) is a cheap hallucination proxy.
- **human_preference**: always present, default null. `report` writes
  `preference-template.csv` (`run_a,run_b,task_id,preferred,notes`) for later
  pairwise ranking; a ranking UI is roadmap.

## Threats / limits

1. Visible oracle tests ship in-fixture (agent-visible, could be hardcoded
   against). Mitigation: `heldout/` tests are injected post-run and never
   visible; `success` requires both, and visible-pass + heldout-fail is
   surfaced as an overfit signal. `check` enforces the separation.
2. Token counts depend on provider surfacing; local models often omit them.
3. Single-machine wall times are noisy — report relative deltas, not absolutes.
4. `max_turns` is enforced via prompt suffix (OpenCode `run` has no flag);
   adapter-level enforcement is roadmap.
