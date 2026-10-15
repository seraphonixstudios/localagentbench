"""Incomplete LRU cache. Task: implement get/put + thread safety."""
from collections import OrderedDict


class LRUCache:
    """Fixed-capacity LRU cache. get() returns None on miss."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self.capacity = capacity
        self._d: OrderedDict = OrderedDict()

    def get(self, key):
        raise NotImplementedError("implement get()")

    def put(self, key, value) -> None:
        raise NotImplementedError("implement put()")

    def __len__(self):
        return len(self._d)
