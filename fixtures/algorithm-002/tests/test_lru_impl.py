"""Oracle: eviction order, recency, update, edges — plus lock presence."""
import threading

import pytest

from lru import LRUCache


def _lock_attrs(cache):
    lock_types = (type(threading.Lock()), type(threading.RLock()))
    return [v for v in vars(cache).values() if isinstance(v, lock_types)]


def test_miss_and_len():
    c = LRUCache(2)
    assert c.get("x") is None
    assert len(c) == 0


def test_evicts_lru_not_mru():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert c.get("a") is None
    assert (c.get("b"), c.get("c")) == (2, 3)


def test_get_refreshes_recency():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None


def test_update_value_and_recency():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 9)
    assert c.get("a") == 9 and len(c) == 2
    c.put("c", 3)
    assert c.get("b") is None


def test_bad_capacity():
    with pytest.raises(ValueError):
        LRUCache(0)


def test_thread_safety_lock_present():
    assert _lock_attrs(LRUCache(4)), "guard methods with a threading.Lock"


def test_concurrent_no_corruption():
    c = LRUCache(50)
    def worker(i):
        for j in range(200):
            c.put(f"t{i}-{j}", j)
            c.get(f"t{i}-{j}")
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(c) <= 50
