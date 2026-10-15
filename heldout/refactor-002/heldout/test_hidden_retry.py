"""HELD-OUT oracle for refactor-002: with_retry semantics directly."""
import pytest

from fetchers import with_retry


def test_eventual_success():
    calls = []

    def fn():
        calls.append(1)
        if len(calls) < 3:
            raise ConnectionError("x")
        return "ok"

    assert with_retry(fn) == "ok"
    assert len(calls) == 3


def test_exhaustion_reraises_last():
    calls = []

    def fn():
        calls.append(1)
        raise ConnectionError("down")

    with pytest.raises(ConnectionError):
        with_retry(fn, attempts=2)
    assert len(calls) == 2


def test_attempts_one():
    calls = []

    def fn():
        calls.append(1)
        raise ConnectionError("down")

    with pytest.raises(ConnectionError):
        with_retry(fn, attempts=1)
    assert len(calls) == 1
