"""Oracle: drive the CLI against mocked failures (fails_left.txt)."""
import subprocess
import sys
from pathlib import Path

STATE = Path("fails_left.txt")


def _run(*args):
    return subprocess.run([sys.executable, "fetch.py", *args],
                          capture_output=True, text=True)


def test_success_no_retry_needed():
    STATE.write_text("0", encoding="utf-8")
    r = _run()
    assert r.returncode == 0
    assert r.stdout.strip() == "OK"


def test_retry_eventually_succeeds():
    STATE.write_text("2", encoding="utf-8")
    r = _run("--retry", "3")
    assert r.returncode == 0
    assert r.stdout.strip() == "OK"


def test_exhausted_fails_cleanly():
    STATE.write_text("5", encoding="utf-8")
    r = _run("--retry", "2")
    assert r.returncode != 0
    assert "Traceback" not in r.stderr


def test_no_retry_flag_fails():
    STATE.write_text("1", encoding="utf-8")
    r = _run()
    assert r.returncode != 0


def test_help():
    r = _run("--help")
    assert r.returncode == 0
    assert "--retry" in r.stdout
