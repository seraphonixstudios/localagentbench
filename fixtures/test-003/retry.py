"""Retry helper. Task for the agent: WRITE the tests (see task YAML)."""
from __future__ import annotations


def with_retry(fn, attempts=3, exceptions=(Exception,)):
    """Call fn(); retry on `exceptions` up to `attempts` total tries.

    Returns fn()'s value on success, re-raises the last error when attempts
    run out. attempts < 1 raises ValueError.
    """
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    last = None
    for _ in range(attempts):
        try:
            return fn()
        except exceptions as e:
            last = e
    raise last
