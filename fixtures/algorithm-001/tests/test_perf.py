"""Deterministic complexity oracle: counts element accesses.

A linear scan over 2M elements needs ~2M accesses; binary search needs ~21.
No timing involved, so this is stable across machines.
"""
from search import bisect_index


class CountingList:
    def __init__(self, n):
        self.n = n
        self.accesses = 0

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        self.accesses += 1
        if not 0 <= i < self.n:
            raise IndexError(i)
        return i * 2


def test_logarithmic_accesses():
    xs = CountingList(2_000_000)
    assert bisect_index(xs, 2 * (2_000_000 - 1)) == 2_000_000 - 1
    assert xs.accesses <= 100, f"{xs.accesses} accesses: not O(log n)"


def test_absent_logarithmic():
    xs = CountingList(2_000_000)
    assert bisect_index(xs, 1) == -1
    assert xs.accesses <= 100, f"{xs.accesses} accesses: not O(log n)"
