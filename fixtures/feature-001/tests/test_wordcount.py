"""Oracle tests for the wordcount feature (FAIL until implemented)."""
import subprocess
import sys

from wordcount import count_stats


def test_counts():
    assert count_stats("Hello world\nsecond line here\n") == {
        "lines": 2, "words": 5, "chars": 29}


def test_empty():
    assert count_stats("") == {"lines": 0, "words": 0, "chars": 0}


def test_cli_runs():
    r = subprocess.run([sys.executable, "wordcount.py", "sample.txt"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip().startswith("2 5 29")
