"""HELD-OUT oracle for refactor-001: discount boundaries + behavior."""
import pytest

from orders import discounted, total_member, total_standard


def test_boundaries():
    assert discounted(100) == 100
    assert discounted(100.01) == pytest.approx(90.009)
    assert discounted(0) == 0


def test_totals_agree():
    assert total_standard([(60, 2)]) == 108.0
    assert total_member([(10, 2)]) == 19.0
