"""HELD-OUT oracle for feature-001. Never shown to the agent."""
import subprocess
import sys

from wordcount import count_stats


def test_tabs_and_spaces():
    assert count_stats("a\tb  c\n") == {"lines": 1, "words": 3, "chars": 7}


def test_no_trailing_newline():
    assert count_stats("one two") == {"lines": 1, "words": 2, "chars": 7}


def test_multiline_counts():
    text = "x\n\ny\n"
    assert count_stats(text) == {"lines": 3, "words": 2, "chars": 5}


def test_cli_prints_counts(tmp_path):
    p = tmp_path / "tiny.txt"
    p.write_text("ab cd\n", encoding="utf-8")
    r = subprocess.run([sys.executable, "wordcount.py", str(p)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip().startswith("1 2 6")
