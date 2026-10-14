"""Oracle tests for median (currently FAIL on buggy implementation)."""
from median import median


def test_odd():
    assert median([3, 1, 2]) == 2


def test_even():
    assert median([4, 1, 3, 2]) == 2.5


def test_even_two_elements():
    assert median([10, 0]) == 5.0


def test_sorted_and_unsorted_same():
    assert median([5, 5, 5, 5]) == 5


def test_empty_raises():
    import pytest
    with pytest.raises(ValueError):
        median([])
