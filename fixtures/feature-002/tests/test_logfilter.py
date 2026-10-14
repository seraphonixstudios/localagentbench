"""Oracle for the JSON log filter feature."""
import json
import subprocess
import sys

from logfilter import filter_events


def test_filter():
    evs = [{"level": "INFO"}, {"level": "ERROR"}, {"level": "ERROR"}]
    assert filter_events(evs, "ERROR") == [{"level": "ERROR"}, {"level": "ERROR"}]
    assert filter_events(evs, "DEBUG") == []


def test_cli():
    r = subprocess.run([sys.executable, "logfilter.py", "app.log", "ERROR"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    lines = [json.loads(l) for l in r.stdout.splitlines()]
    assert [e["msg"] for e in lines] == ["disk full", "timeout"]
