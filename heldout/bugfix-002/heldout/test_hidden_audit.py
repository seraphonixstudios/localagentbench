"""HELD-OUT oracle for bugfix-002: repeated independence + explicit list."""
from audit import append_log


def test_many_independent():
    for ch in "abcde":
        assert append_log(ch) == [ch]


def test_explicit_accumulates():
    mine = ["x"]
    assert append_log("y", mine) == ["x", "y"]
    assert mine == ["x", "y"]
    assert append_log("z") == ["z"]
