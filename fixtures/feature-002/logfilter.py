"""JSON-lines log filter stub. Task: implement filter_events() + CLI."""
from __future__ import annotations

import argparse
import json


def filter_events(events: list[dict], level: str) -> list[dict]:
    """Return events whose 'level' equals `level` (case-sensitive)."""
    raise NotImplementedError("implement filter_events()")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Filter JSON-lines log by level")
    parser.add_argument("file", help="JSON-lines log file")
    parser.add_argument("level", help="level to keep, e.g. ERROR")
    args = parser.parse_args(argv)
    with open(args.file, encoding="utf-8") as fh:
        events = [json.loads(line) for line in fh if line.strip()]
    for ev in filter_events(events, args.level):
        print(json.dumps(ev))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
