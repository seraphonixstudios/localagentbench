"""Oracle: correctness plus no-overflow on large logits."""
import pytest

from softmax import softmax


def test_uniform():
    assert softmax([1, 1, 1]) == pytest.approx([1 / 3, 1 / 3, 1 / 3])


def test_known_values():
    assert softmax([1, 2, 3]) == pytest.approx(
        [0.09003057, 0.24472847, 0.66524096])


def test_large_logits_no_overflow():
    assert softmax([1000, 1001, 1002]) == pytest.approx(
        [0.09003057, 0.24472847, 0.66524096])


def test_single():
    assert softmax([5]) == pytest.approx([1.0])


def test_empty_raises():
    with pytest.raises(ValueError):
        softmax([])
