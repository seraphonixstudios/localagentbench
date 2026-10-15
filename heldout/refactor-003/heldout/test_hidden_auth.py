"""HELD-OUT oracle for refactor-003: rule-consistent edge inputs."""
import auth


def test_email_edges():
    assert auth.is_valid_email("user@mail.example.org") is True
    assert auth.is_valid_email("x@y.z") is True
    assert auth.is_valid_email("@") is False
    assert auth.is_valid_email("") is False
    assert auth.is_valid_email("a@b@c") is False  # rule: no dot in last segment


def test_password_edges():
    assert auth.is_valid_password("12345678") is True
    assert auth.is_valid_password("abcd1234") is True
    assert auth.is_valid_password("abc123") is False
    assert auth.is_valid_password("") is False


def test_behavior_preserved_on_edges():
    users = {}
    assert auth.register("x@y.z", "12345678", users) is True
    import pytest
    with pytest.raises(ValueError):
        auth.register("@", "12345678", {})
