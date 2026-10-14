"""HELD-OUT oracle for data-001: fresh CSV with edge rows."""
from summary import summarize


def test_second_csv(tmp_path):
    p = tmp_path / "more.csv"
    p.write_text("category,amount\n"
                 "a,1\n"
                 "b,2.5\n"
                 "a,not-a-number\n"
                 "c,\n"
                 "b,0.5\n"
                 ",3\n", encoding="utf-8")
    totals = summarize(str(p))
    assert totals.get("a") == 1.0
    assert totals.get("b") == 3.0
    assert "c" not in totals
