"""HELD-OUT oracle for bugfix-001. Never shown to the agent."""
from median import median


def test_negatives_even():
    assert median([-5, -1, -3, -2]) == -2.5


def test_floats():
    assert median([1.5, 0.5, 2.5, 1.0]) == 1.25


def test_single():
    assert median([42]) == 42


def test_larger_even():
    assert median([9, 1, 8, 2, 7, 3]) == 5.0
