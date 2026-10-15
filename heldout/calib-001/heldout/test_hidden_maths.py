"""HELD-OUT oracle for calib-001: more numbers."""
from maths import add


def test_negatives():
    assert add(-2, -3) == -5


def test_floats():
    assert add(1.5, 2.5) == 4.0


def test_large():
    assert add(10 ** 12, 1) == 1000000000001
