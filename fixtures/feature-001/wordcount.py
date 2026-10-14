"""Word-count CLI. Task: implement count_stats() + argparse wiring."""
from __future__ import annotations

import argparse
from pathlib import Path


def count_stats(text: str) -> dict:
    """Return {'lines': int, 'words': int, 'chars': int} for text.

    lines = number of lines (splitlines), words = whitespace-separated tokens,
    chars = len(text).
    """
    raise NotImplementedError("implement count_stats()")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print line/word/char counts")
    parser.add_argument("file", help="text file to analyze")
    args = parser.parse_args(argv)
    text = Path(args.file).read_text(encoding="utf-8")
    stats = count_stats(text)
    print(f"{stats['lines']} {stats['words']} {stats['chars']} {args.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
