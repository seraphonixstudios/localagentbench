from localagentbench.metrics import aggregate, pass_at_k


def test_pass_at_k_edges():
    assert pass_at_k(1, 1, 1) == 1.0
    assert pass_at_k(3, 0, 1) == 0.0
    assert pass_at_k(3, 3, 2) == 1.0
    v = pass_at_k(3, 1, 1)
    assert abs(v - 1 / 3) < 1e-9


def test_aggregate():
    rs = [
        {"task_id": "a", "oracle_passed": True, "agent_wall_s": 2.0,
         "input_tokens": 10, "output_tokens": 5, "tool_calls": 3,
         "failed_tool_calls": 0},
        {"task_id": "a", "oracle_passed": False, "agent_wall_s": 4.0,
         "input_tokens": 10, "output_tokens": 5, "tool_calls": 3,
         "failed_tool_calls": 1},
    ]
    agg = aggregate(rs)
    assert agg["total_runs"] == 2 and agg["total_successes"] == 1
    assert agg["per_task"]["a"]["pass_at_1"] == 0.5
    assert agg["total_failed_tool_calls"] == 1
