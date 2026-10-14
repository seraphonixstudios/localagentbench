"""Robust statistics stubs. Task: implement trimmed mean + winsorized std (stdlib only)."""
from __future__ import annotations


def trimmed_mean(values, proportion: float) -> float:
    """Mean after cutting proportion/2 from each end (sorted).

    proportion in [0, 0.5). proportion=0 == plain mean.
    Raises ValueError on empty input or if trimming removes all data.
    """
    raise NotImplementedError("implement trimmed_mean()")


def winsorized_std(values, proportion: float) -> float:
    """Population std after winsorizing proportion/2 of each tail to the
    nearest kept value. proportion in [0, 0.5). Raises ValueError on empty
    input or if trimming removes all data."""
    raise NotImplementedError("implement winsorized_std()")
