"""HELD-OUT oracle for feature-001. Never shown to the agent."""
from wordcount import count_stats


def test_tabs_and_spaces():
    assert count_stats("a\tb  c\n") == {"lines": 1, "words": 3, "chars": 7}


def test_no_trailing_newline():
    assert count_stats("one two") == {"lines": 1, "words": 2, "chars": 7}


def test_multiline_counts():
    text = "x\n\ny\n"
    assert count_stats(text) == {"lines": 3, "words": 2, "chars": 5}
