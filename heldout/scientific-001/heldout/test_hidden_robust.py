"""HELD-OUT oracle for scientific-001: more trimmed/winsorized cases."""
import statistics

import pytest

from robust import trimmed_mean, winsorized_std


def test_trimmed_mean_half():
    assert trimmed_mean([10, 20, 30, 40, 50, 60], 0.5) == pytest.approx(35.0)


def test_trimmed_mean_negatives():
    assert trimmed_mean([-5, -1, 0, 1, 5], 0.0) == pytest.approx(0.0)


def test_winsorized_flat():
    assert winsorized_std([1, 1, 1, 1, 100], 0.4) == pytest.approx(0.0)


def test_winsorized_single():
    assert winsorized_std([5], 0.0) == pytest.approx(statistics.pstdev([5]))


def test_winsorized_empty_raises():
    with pytest.raises(ValueError):
        winsorized_std([], 0.1)
