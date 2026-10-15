"""HELD-OUT oracle for scientific-002: cosine, quadratic, reversed."""
import math

import pytest

from integrate import trapezoid


def test_cosine():
    assert trapezoid(math.sin, 0, math.pi / 2, 2000) == pytest.approx(1.0, rel=1e-3)


def test_quadratic_unit():
    assert trapezoid(lambda x: x * x, 0, 1, 2000) == pytest.approx(1 / 3, rel=1e-3)


def test_reversed_limits():
    assert trapezoid(lambda x: x, 1, 0, 4) == pytest.approx(-0.5)
