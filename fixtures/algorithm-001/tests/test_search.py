"""Oracle for leftmost binary search."""
from search import bisect_index


def test_found_middle():
    assert bisect_index([1, 2, 3, 4, 5], 3) == 2


def test_leftmost_duplicate():
    assert bisect_index([1, 2, 2, 2, 3], 2) == 1


def test_not_found():
    assert bisect_index([1, 3, 5], 4) == -1
    assert bisect_index([], 1) == -1


def test_first_last():
    assert bisect_index([1, 2, 3], 1) == 0
    assert bisect_index([1, 2, 3], 3) == 2


def test_large():
    xs = list(range(0, 10000, 2))
    assert bisect_index(xs, 0) == 0
    assert bisect_index(xs, 9998) == 4999
    assert bisect_index(xs, 9999) == -1
