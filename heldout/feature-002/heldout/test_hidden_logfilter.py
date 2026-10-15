"""HELD-OUT oracle for feature-002: case-sensitivity + INFO path."""
import json
import subprocess
import sys

from logfilter import filter_events


def test_case_sensitive():
    evs = [{"level": "error"}, {"level": "ERROR"}]
    assert filter_events(evs, "ERROR") == [{"level": "ERROR"}]
    assert filter_events(evs, "error") == [{"level": "error"}]


def test_cli_info():
    r = subprocess.run([sys.executable, "logfilter.py", "app.log", "INFO"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert [json.loads(l)["msg"] for l in r.stdout.splitlines()] == [
        "boot", "retry"]
