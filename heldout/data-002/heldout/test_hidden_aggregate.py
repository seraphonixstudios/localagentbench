"""HELD-OUT oracle for data-002: fresh JSONL with more edge rows."""
from aggregate import summarize


def test_second_file(tmp_path):
    p = tmp_path / "more.jsonl"
    p.write_text(
        '{"type": "a", "value": -4}\n'
        '{"type": "a", "value": 2.5, "extra": "ignored"}\n'
        '{"type": "b", "value": [1]}\n'
        '{"type": "b", "value": {"x": 1}}\n'
        '{"type": "a", "value": false}\n'
        '\n'
        '[]\n',
        encoding="utf-8")
    assert summarize(str(p)) == {
        "count": 2, "avg_value": -0.75, "by_type": {"a": 2}}


def test_empty_file(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("\n", encoding="utf-8")
    assert summarize(str(p)) == {"count": 0, "avg_value": 0.0, "by_type": {}}
