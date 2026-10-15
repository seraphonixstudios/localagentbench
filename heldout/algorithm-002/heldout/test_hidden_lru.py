"""HELD-OUT oracle for algorithm-002: seeded model cross-check + hammer."""
import random
import threading

from lru import LRUCache


def _model_run(ops, capacity):
    """Simple reference LRU: most-recent-first order list."""
    order = []
    store = {}
    for op, key, value in ops:
        if op == "put":
            if key in store:
                order.remove(key)
            order.append(key)
            store[key] = value
            while len(order) > capacity:
                store.pop(order.pop(0))
        else:
            if key in store:
                order.remove(key)
                order.append(key)
    return store


def test_seeded_cross_check():
    rng = random.Random(20261015)
    ops = [(rng.choice(["get", "put"]), f"k{rng.randint(0, 9)}",
            rng.randint(0, 99)) for _ in range(300)]
    expected = _model_run(ops, 5)
    c = LRUCache(5)
    for op, key, value in ops:
        if op == "put":
            c.put(key, value)
        else:
            c.get(key)
    for key, value in expected.items():
        assert c.get(key) == value
    assert len(c) == len(expected)


def test_heavy_hammer_invariant():
    c = LRUCache(30)
    def worker(i):
        for j in range(300):
            c.put(f"w{i}-{j}", (i, j))
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(c) <= 30
    assert c.get("missing") is None
