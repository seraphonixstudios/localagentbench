"""CSV sales summarizer stub (stdlib csv only)."""
from __future__ import annotations


def summarize(csv_path: str) -> dict:
    """Read CSV with columns (category, amount) and return
    {category: total_amount: float}, skipping rows with missing/bad amounts.
    Header row must be tolerated."""
    raise NotImplementedError("implement summarize()")
