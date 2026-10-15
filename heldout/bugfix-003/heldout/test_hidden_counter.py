"""HELD-OUT oracle for bugfix-003: heavier hammer + mixed increments."""
import threading

from counter import Counter


def test_heavy_hammer():
    c = Counter()
    threads = [threading.Thread(target=c.increment, args=(10_000,))
               for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.value() == 80_000


def test_mixed_increments():
    c = Counter()
    threads = ([threading.Thread(target=c.increment, args=(1,))
                for _ in range(200)]
               + [threading.Thread(target=c.increment, args=(500,))
                  for _ in range(4)])
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.value() == 200 + 2000
