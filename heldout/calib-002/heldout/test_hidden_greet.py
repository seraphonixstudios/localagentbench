"""HELD-OUT oracle for calib-002: more names."""
from greet import greet


def test_zoe():
    assert greet("Zoe") == "Hello, Zoe!"


def test_empty():
    assert greet("") == "Hello, !"


def test_space():
    assert greet("A B") == "Hello, A B!"
