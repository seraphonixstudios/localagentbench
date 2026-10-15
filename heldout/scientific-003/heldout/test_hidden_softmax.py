"""HELD-OUT oracle for scientific-003: extreme logits."""
import math

import pytest

from softmax import softmax


def test_huge_equal():
    assert softmax([1e6, 1e6, 1e6]) == pytest.approx([1 / 3, 1 / 3, 1 / 3])


def test_huge_spread():
    assert softmax([1e6 - 1, 1e6, 1e6 + 1]) == pytest.approx(
        [0.09003057, 0.24472847, 0.66524096])


def test_large_negative():
    assert softmax([-1000, -1000]) == pytest.approx([0.5, 0.5])


def test_sums_to_one():
    out = softmax([1234.5, -987.1, 0.3, 55])
    assert sum(out) == pytest.approx(1.0)
    assert all(v >= 0 for v in out)
