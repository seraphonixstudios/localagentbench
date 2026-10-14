"""Buggy median implementation — task: fix it."""
from __future__ import annotations


def median(values):
    """Return the median of a non-empty sequence of numbers."""
    if not values:
        raise ValueError("median of empty sequence")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    # BUG: off-by-one — averages the wrong pair for even-length input
    return (s[mid] + s[mid + 1]) / 2
