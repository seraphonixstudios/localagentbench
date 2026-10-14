"""One-off failure-mode analysis for the qwen3 baseline."""
import json
import pathlib

base = pathlib.Path('results/baseline-qwen3-8b')
for d in sorted(base.iterdir()):
    if not d.is_dir():
        continue
    r = json.load(open(d / 'result.json', encoding='utf-8'))
    so = (d / 'agent.stdout.log').read_text(errors='replace')
    print(f"{r['task_id'][:32]:32s} exit={r['agent_exit_code']} "
          f"wall={r['agent_wall_s']:7.1f}s tools={r['tool_calls']} "
          f"tok={r['input_tokens']}/{r['output_tokens']} "
          f"outlen={len(so)} err={r['agent_stderr_tail'][:90]!r}")
