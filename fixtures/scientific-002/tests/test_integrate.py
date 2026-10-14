"""Oracle: trapezoidal rule vs analytic integrals."""
import math

import pytest

from integrate import trapezoid


def test_linear_exact():
    assert trapezoid(lambda x: 2 * x + 1, 0, 3, 4) == pytest.approx(12.0)


def test_quadratic_converges():
    assert trapezoid(lambda x: x * x, 0, 2, 1000) == pytest.approx(8 / 3, rel=1e-3)


def test_sine():
    assert trapezoid(math.sin, 0, math.pi, 2000) == pytest.approx(2.0, rel=1e-3)


def test_single_trapezoid():
    assert trapezoid(lambda x: x, 0, 1, 1) == pytest.approx(0.5)
