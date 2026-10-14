"""Two fetchers with DUPLICATED retry loops. Task: extract with_retry()."""
from __future__ import annotations

CALLS: dict = {}


def _flaky_fetch_users(failures_before_success: int = 2):
    CALLS["users"] = CALLS.get("users", 0) + 1
    if CALLS["users"] <= failures_before_success:
        raise ConnectionError("users down")
    return [{"id": 1}]


def _flaky_fetch_orders(failures_before_success: int = 1):
    CALLS["orders"] = CALLS.get("orders", 0) + 1
    if CALLS["orders"] <= failures_before_success:
        raise ConnectionError("orders down")
    return [{"id": 7}]


def fetch_users():
    last = None
    for _ in range(3):
        try:
            return _flaky_fetch_users()
        except ConnectionError as e:
            last = e
    raise last


def fetch_orders():
    last = None
    for _ in range(3):
        try:
            return _flaky_fetch_orders()
        except ConnectionError as e:
            last = e
    raise last
