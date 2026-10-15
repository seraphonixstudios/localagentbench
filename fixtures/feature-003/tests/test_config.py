"""Oracle for the config loader feature."""
import pytest

from config import DEFAULTS, load_config


def test_missing_file_gives_defaults():
    assert load_config("does-not-exist.json") == DEFAULTS
    assert load_config("does-not-exist.json") is not DEFAULTS


def test_file_merge():
    assert load_config("example.json") == {
        "host": "localhost", "port": 9000, "debug": False,
        "limits": {"cpu": 2, "mem": 1024}}


def test_overrides_dotted():
    out = load_config("example.json", {"port": 1, "limits.cpu": 8})
    assert out["port"] == 1
    assert out["limits"] == {"cpu": 8, "mem": 1024}


def test_overrides_nested_dict_merges():
    out = load_config("example.json", {"limits": {"cpu": 1}})
    assert out["limits"] == {"cpu": 1, "mem": 1024}


def test_bad_types():
    with pytest.raises(TypeError):
        load_config("example.json", {"port": "x"})
    with pytest.raises(TypeError):
        load_config("example.json", {"port": True})
    with pytest.raises(TypeError):
        load_config("example.json", {"debug": 1})
    with pytest.raises(TypeError):
        load_config("example.json", {"limits": 5})


def test_unknown_keys():
    with pytest.raises(KeyError):
        load_config("example.json", {"nope": 1})
    with pytest.raises(KeyError):
        load_config("example.json", {"limits.gpu": 1})


def test_defaults_not_mutated():
    out = load_config("example.json", {"port": 1})
    out["limits"]["cpu"] = 999
    assert DEFAULTS == {"host": "localhost", "port": 8080, "debug": False,
                        "limits": {"cpu": 2, "mem": 512}}
    assert load_config("example.json")["limits"]["cpu"] == 2
