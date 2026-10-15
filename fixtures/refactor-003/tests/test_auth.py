"""Behavioural oracle for the validator refactor (must keep passing)."""
import pytest

import auth


def test_register_ok():
    users = {}
    assert auth.register("a@b.co", "secret99", users) is True
    assert users == {"a@b.co": "secret99"}


def test_register_rejects():
    with pytest.raises(ValueError):
        auth.register("nope", "secret99", {})
    with pytest.raises(ValueError):
        auth.register("a@b", "secret99", {})
    with pytest.raises(ValueError):
        auth.register("a@b.co", "short", {})
    with pytest.raises(ValueError):
        auth.register("a@b.co", "nodigits!", {})


def test_register_duplicate():
    users = {"a@b.co": "secret99"}
    with pytest.raises(ValueError):
        auth.register("a@b.co", "other99", users)


def test_change_password_ok():
    users = {"a@b.co": "secret99"}
    assert auth.change_password("a@b.co", "secret99", "newpass1", users) is True
    assert users["a@b.co"] == "newpass1"


def test_change_password_rejects():
    users = {"a@b.co": "secret99"}
    with pytest.raises(ValueError):
        auth.change_password("bad", "secret99", "newpass1", users)
    with pytest.raises(ValueError):
        auth.change_password("a@b.co", "wrong", "newpass1", users)
    with pytest.raises(ValueError):
        auth.change_password("a@b.co", "secret99", "weak", users)
