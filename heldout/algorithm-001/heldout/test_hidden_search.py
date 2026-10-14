"""HELD-OUT oracle for algorithm-001: randomized cross-check vs bisect."""
import bisect
import random

from search import bisect_index


def test_random_against_bisect():
    rng = random.Random(20261015)
    for _ in range(50):
        n = rng.randint(0, 30)
        xs = sorted(rng.randint(0, 10) for _ in range(n))
        x = rng.randint(0, 10)
        i = bisect.bisect_left(xs, x)
        expected = i if i < len(xs) and xs[i] == x else -1
        assert bisect_index(xs, x) == expected


def test_all_equal():
    assert bisect_index([7] * 100, 7) == 0
    assert bisect_index([7] * 100, 6) == -1
