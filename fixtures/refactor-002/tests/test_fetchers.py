"""Behavioural oracle for the retry refactor."""
import fetchers


def _reset():
    fetchers.CALLS.clear()


def test_users_retries_then_succeeds():
    _reset()
    assert fetchers.fetch_users() == [{"id": 1}]
    assert fetchers.CALLS["users"] == 3


def test_orders_retries_then_succeeds():
    _reset()
    assert fetchers.fetch_orders() == [{"id": 7}]
    assert fetchers.CALLS["orders"] == 2
