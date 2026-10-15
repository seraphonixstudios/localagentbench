"""Shared counter. Task: fix the race so the final count is always exact."""


class Counter:
    """Counter incremented from multiple threads."""

    def __init__(self) -> None:
        self.count = 0

    def increment(self, n: int = 1) -> None:
        # BUG: read-modify-write without synchronization; concurrent
        # increments lose updates.
        for _ in range(n):
            self.count += 1

    def value(self) -> int:
        return self.count
