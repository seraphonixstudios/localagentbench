"""Unreliable fetch CLI. Task: add --retry and proper exit codes."""
from __future__ import annotations

import argparse
from pathlib import Path

STATE = Path("fails_left.txt")


def attempt() -> str:
    """One attempt. Fails while the fails_left.txt counter is positive,
    consuming one failure per call; missing file means success."""
    left = int(STATE.read_text(encoding="utf-8").strip()) if STATE.exists() else 0
    if left > 0:
        STATE.write_text(str(left - 1), encoding="utf-8")
        raise RuntimeError("boom")
    return "OK"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Fetch with retries")
    args = parser.parse_args(argv)
    print(attempt())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
