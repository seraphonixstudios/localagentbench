"""HELD-OUT oracle for cli-001: different fail counts and edge retries."""
import subprocess
import sys
from pathlib import Path

STATE = Path("fails_left.txt")


def _run(*args):
    return subprocess.run([sys.executable, "fetch.py", *args],
                          capture_output=True, text=True)


def test_exact_retry_budget():
    STATE.write_text("3", encoding="utf-8")
    r = _run("--retry", "3")
    assert r.returncode == 0
    assert r.stdout.strip() == "OK"


def test_zero_retry_with_failure():
    STATE.write_text("1", encoding="utf-8")
    r = _run("--retry", "0")
    assert r.returncode != 0
    assert "Traceback" not in r.stderr


def test_generous_retry_immediate_success():
    STATE.write_text("0", encoding="utf-8")
    r = _run("--retry", "5")
    assert r.returncode == 0
    assert r.stdout.strip() == "OK"
