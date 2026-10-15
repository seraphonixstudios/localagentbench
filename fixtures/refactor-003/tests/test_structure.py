"""Structural oracle: helpers must exist and both call sites must use them."""
import inspect

import auth


def test_helpers_exist_and_agree():
    assert callable(getattr(auth, "is_valid_email", None))
    assert callable(getattr(auth, "is_valid_password", None))
    assert auth.is_valid_email("a@b.co") is True
    assert auth.is_valid_email("nope") is False
    assert auth.is_valid_email("a@b") is False
    assert auth.is_valid_password("secret99") is True
    assert auth.is_valid_password("short") is False
    assert auth.is_valid_password("nodigits!") is False


def test_call_sites_use_helpers():
    src = inspect.getsource(auth.register) + inspect.getsource(auth.change_password)
    assert src.count("is_valid_email") >= 2
    assert src.count("is_valid_password") >= 2
