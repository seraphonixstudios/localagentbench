"""Config loader stub. Task: defaults, validation, nested keys."""
from __future__ import annotations

DEFAULTS = {
    "host": "localhost",
    "port": 8080,
    "debug": False,
    "limits": {"cpu": 2, "mem": 512},
}


def load_config(path, overrides=None):
    """Load JSON config from path, deep-merged over DEFAULTS.

    - Missing file -> DEFAULTS.
    - overrides: {"dotted.key": value} applied last.
    - Types must match DEFAULTS (int rejects bool, bool/dict strict).
    - Unknown keys -> KeyError, wrong types -> TypeError.
    Never mutates DEFAULTS.
    """
    raise NotImplementedError("implement load_config()")
