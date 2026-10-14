"""Oracle: independent calls must not share state."""
from audit import append_log


def test_independent_calls():
    assert append_log("a") == ["a"]
    assert append_log("b") == ["b"]


def test_explicit_log_still_works():
    mine = []
    assert append_log("x", mine) == ["x"]
    assert mine == ["x"]
    assert append_log("y") == ["y"]
