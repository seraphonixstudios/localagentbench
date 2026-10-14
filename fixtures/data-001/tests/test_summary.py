"""Oracle for CSV summary (header + bad rows tolerated)."""
from summary import summarize


def test_totals():
    assert summarize("sales.csv") == {"books": 15.0, "games": 25.25}


def test_skips_header_and_bad_rows():
    totals = summarize("sales.csv")
    assert "category" not in totals
    assert "toys" not in totals
