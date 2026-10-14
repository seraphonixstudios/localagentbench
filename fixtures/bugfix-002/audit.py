"""Audit log helper with the classic mutable-default-arg bug."""


def append_log(entry, log=[]):
    log.append(entry)
    return log
