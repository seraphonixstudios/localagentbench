"""Oracle: golden aggregation of events.jsonl (bad rows skipped)."""
from aggregate import summarize


def test_golden():
    assert summarize("events.jsonl") == {
        "count": 4, "avg_value": 16.375, "by_type": {"click": 3, "view": 1}}


def test_keys_present():
    out = summarize("events.jsonl")
    assert set(out) == {"count", "avg_value", "by_type"}
