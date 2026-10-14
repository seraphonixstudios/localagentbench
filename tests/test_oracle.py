from localagentbench.oracle import run_oracle


def test_oracle_pass_fail(tmp_path):
    ok = run_oracle(["python -c \"raise SystemExit(0)\""], str(tmp_path))
    assert ok.passed
    bad = run_oracle(["python -c \"raise SystemExit(1)\""], str(tmp_path))
    assert not bad.passed
    assert bad.commands[0]["exit_code"] == 1


def test_oracle_captures_utf8(tmp_path):
    # Model output routinely contains bytes cp1252 can't decode (e.g. CJK).
    # Capture must not die on Windows locale encodings (regression: reader
    # thread UnicodeDecodeError dropped a whole trajectory). The child
    # writes raw UTF-8 bytes to dodge its own console encoding.
    res = run_oracle(
        ["python -c \"import sys; sys.stdout.buffer.write("
         "'a\\u2014b\\u4e2d'.encode('utf-8'))\""],
        str(tmp_path))
    assert res.passed
    assert "a\u2014b\u4e2d" in res.commands[0]["stdout"]
