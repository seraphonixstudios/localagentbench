"""HELD-OUT oracle for feature-003: more type edges and merges."""
import pytest

from config import load_config


def test_more_bad_types():
    with pytest.raises(TypeError):
        load_config("example.json", {"port": 1.5})
    with pytest.raises(TypeError):
        load_config("example.json", {"debug": None})
    with pytest.raises(TypeError):
        load_config("example.json", {"host": 7})
    with pytest.raises(TypeError):
        load_config("example.json", {"limits.mem": "lots"})


def test_empty_overrides_is_file_merge():
    assert load_config("example.json", {}) == load_config("example.json")


def test_nested_override_on_defaults():
    out = load_config("missing.json", {"limits.mem": 256})
    assert out["limits"] == {"cpu": 2, "mem": 256}
    assert out["host"] == "localhost"


def test_file_with_unknown_key(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('{"host": "x", "zzz": 1}', encoding="utf-8")
    with pytest.raises(KeyError):
        load_config(str(p))
