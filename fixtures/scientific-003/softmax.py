"""Naive softmax. Task: make it numerically stable (stdlib only)."""
import math


def softmax(xs):
    """Return softmax probabilities. Must not overflow on large logits;
    raise ValueError on empty input."""
    exps = [math.exp(x) for x in xs]
    total = sum(exps)
    return [e / total for e in exps]
