"""Oracle for the calibration feature."""
from greet import greet


def test_greet_ada():
    assert greet("Ada") == "Hello, Ada!"


def test_greet_bob():
    assert greet("Bob") == "Hello, Bob!"
