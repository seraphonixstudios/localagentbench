"""Behavioural oracle for the refactor (must keep passing)."""
from orders import total_member, total_standard


def test_standard_no_discount():
    assert total_standard([(10, 2)]) == 20


def test_standard_discount():
    assert total_standard([(60, 2)]) == 108.0


def test_member_no_threshold():
    assert total_member([(10, 2)]) == 19.0


def test_member_threshold():
    assert total_member([(60, 2)]) == 102.6
