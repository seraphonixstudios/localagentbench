"""Oracle: trimmed mean / winsorized std vs reference values (stdlib only)."""
import statistics

import pytest

from robust import trimmed_mean, winsorized_std


def test_trimmed_mean_zero_is_mean():
    assert trimmed_mean([1, 2, 3, 4], 0.0) == pytest.approx(2.5)


def test_trimmed_mean_cuts_tails():
    # sorted: [1,2,3,4,100]; proportion 0.4 -> cut 1 from each end -> mean(2,3,4)
    assert trimmed_mean([100, 1, 2, 3, 4], 0.4) == pytest.approx(3.0)


def test_trimmed_mean_errors():
    with pytest.raises(ValueError):
        trimmed_mean([], 0.1)


def test_winsorized_std_zero_is_pstdev():
    assert winsorized_std([1, 2, 3, 4, 5], 0.0) == pytest.approx(
        statistics.pstdev([1, 2, 3, 4, 5]))


def test_winsorized_std_robust_to_outlier():
    plain = statistics.pstdev([1, 2, 3, 4, 100])
    robust = winsorized_std([1, 2, 3, 4, 100], 0.4)
    assert robust < plain
    # winsorized to [2,2,3,4,4]
    assert robust == pytest.approx(statistics.pstdev([2, 2, 3, 4, 4]))
