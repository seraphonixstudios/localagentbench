"""Oracle: the final count must be exact under threads."""
import threading

from counter import Counter


def _hammer(counter, per_thread, n_threads):
    threads = [threading.Thread(target=counter.increment, args=(per_thread,))
               for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def test_single_thread():
    c = Counter()
    c.increment(1000)
    assert c.value() == 1000


def test_concurrent_exact():
    # 4 x 25k contested increments; an unlocked counter loses thousands.
    for _ in range(3):
        c = Counter()
        _hammer(c, 25_000, 4)
        assert c.value() == 100_000
