from localagentbench.compare import compare


def test_compare_marks_deltas(tmp_path):
    (tmp_path / "a.json").write_text(
        '{"summary": {"model": "m1", "agent": "mock", "total_runs": 1, '
        '"total_successes": 0, "success_rate": 0.0, '
        '"per_task": {"t": {"pass_at_1": 0.0}}}, "results": []}')
    (tmp_path / "b.json").write_text(
        '{"summary": {"model": "m2", "agent": "mock", "total_runs": 1, '
        '"total_successes": 1, "success_rate": 1.0, '
        '"per_task": {"t": {"pass_at_1": 1.0}}}, "results": []}')
    out = compare(tmp_path / "a.json", tmp_path / "b.json")
    assert "+100%" in out and "| t |" in out
