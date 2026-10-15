"""JSONL event summarizer stub. Task: implement summarize()."""
from __future__ import annotations


def summarize(path: str) -> dict:
    """Read a JSON-lines file of {"type": str, "value": number} records.

    Skip blank lines, malformed JSON, and records with missing keys or wrong
    types (type must be str, value must be int/float but not bool).
    Return {"count": <valid records>, "avg_value": <mean or 0.0>,
    "by_type": {<type>: <count>}}.
    """
    raise NotImplementedError("implement summarize()")
