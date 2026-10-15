"""Verify each task is solvable: apply reference solution in temp copy, run oracle."""
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

R = Path('.')


def fix_bugfix_001(tmp: Path):
    p = tmp / 'median.py'
    p.write_text(p.read_text().replace(
        'return (s[mid] + s[mid + 1]) / 2',
        'return (s[mid - 1] + s[mid]) / 2'))


def fix_bugfix_002(tmp: Path):
    (tmp / 'audit.py').write_text(
        'def append_log(entry, log=None):\n'
        '    if log is None:\n'
        '        log = []\n'
        '    log.append(entry)\n'
        '    return log\n')


def fix_feature_001(tmp: Path):
    p = tmp / 'wordcount.py'
    p.write_text(p.read_text().replace(
        'raise NotImplementedError("implement count_stats()")',
        "return {'lines': len(text.splitlines()), "
        "'words': len(text.split()), 'chars': len(text)}"))


def fix_feature_002(tmp: Path):
    p = tmp / 'logfilter.py'
    p.write_text(p.read_text().replace(
        'raise NotImplementedError("implement filter_events()")',
        'return [e for e in events if e.get("level") == level]'))


def fix_refactor_001(tmp: Path):
    (tmp / 'orders.py').write_text(
        'def discounted(subtotal):\n'
        '    return subtotal - subtotal * 0.10 if subtotal > 100 else subtotal\n'
        '\n'
        'def total_standard(items):\n'
        '    return discounted(sum(p * q for p, q in items))\n'
        '\n'
        'def total_member(items):\n'
        '    return discounted(sum(p * q for p, q in items)) * 0.95\n')


def fix_refactor_002(tmp: Path):
    p = tmp / 'fetchers.py'
    src = p.read_text()
    helper = ('def with_retry(fn, attempts=3):\n'
              '    last = None\n'
              '    for _ in range(attempts):\n'
              '        try:\n'
              '            return fn()\n'
              '        except ConnectionError as e:\n'
              '            last = e\n'
              '    raise last\n'
              '\n\n')
    src = src.replace('def fetch_users():\n'
                      '    last = None\n'
                      '    for _ in range(3):\n'
                      '        try:\n'
                      '            return _flaky_fetch_users()\n'
                      '        except ConnectionError as e:\n'
                      '            last = e\n'
                      '    raise last\n',
                      'def fetch_users():\n'
                      '    return with_retry(_flaky_fetch_users)\n')
    src = src.replace('def fetch_orders():\n'
                      '    last = None\n'
                      '    for _ in range(3):\n'
                      '        try:\n'
                      '            return _flaky_fetch_orders()\n'
                      '        except ConnectionError as e:\n'
                      '            last = e\n'
                      '    raise last\n',
                      'def fetch_orders():\n'
                      '    return with_retry(_flaky_fetch_orders)\n')
    marker = 'def _flaky_fetch_users'
    src = src.replace(marker, helper + marker)
    p.write_text(src)


def fix_test_001(tmp: Path):
    (tmp / 'tests' / 'test_bank.py').write_text(
        'import pytest\nfrom bank import BankAccount\n'
        'def test_deposit_ok(): assert BankAccount(10).deposit(5) == 15\n'
        'def test_deposit_bad():\n'
        '    with pytest.raises(ValueError): BankAccount().deposit(0)\n'
        '    with pytest.raises(ValueError): BankAccount().deposit(-1)\n'
        'def test_withdraw_ok(): assert BankAccount(10).withdraw(4) == 6\n'
        'def test_withdraw_bad():\n'
        '    with pytest.raises(ValueError): BankAccount(10).withdraw(0)\n'
        'def test_overdraft_allowed():\n'
        '    assert BankAccount(10, overdraft_limit=5).withdraw(14) == -4\n'
        'def test_overdraft_exceeded():\n'
        '    with pytest.raises(ValueError):\n'
        '        BankAccount(10, overdraft_limit=5).withdraw(16)\n'
        'def test_negative_initial():\n'
        '    with pytest.raises(ValueError): BankAccount(-1)\n')


def fix_test_002(tmp: Path):
    (tmp / 'tests' / 'test_lru.py').write_text(
        'from lru import LRUCache\n'
        'import pytest\n'
        'def test_put_get():\n'
        '    c = LRUCache(2); c.put("a", 1); assert c.get("a") == 1\n'
        'def test_miss_none(): assert LRUCache(2).get("zzz") is None\n'
        'def test_eviction_lru():\n'
        '    c = LRUCache(2); c.put("a", 1); c.put("b", 2); c.put("c", 3)\n'
        '    assert c.get("a") is None and c.get("b") == 2 and c.get("c") == 3\n'
        'def test_recency_refresh():\n'
        '    c = LRUCache(2); c.put("a", 1); c.put("b", 2); c.get("a")\n'
        '    c.put("c", 3)\n'
        '    assert c.get("a") == 1 and c.get("b") is None\n'
        'def test_update_value():\n'
        '    c = LRUCache(2); c.put("a", 1); c.put("a", 9)\n'
        '    assert c.get("a") == 9 and len(c) == 1\n'
        'def test_update_refreshes_recency():\n'
        '    c = LRUCache(2); c.put("a", 1); c.put("b", 2); c.put("a", 5)\n'
        '    c.put("c", 3); assert c.get("b") is None and c.get("a") == 5\n'
        'def test_bad_capacity():\n'
        '    with pytest.raises(ValueError): LRUCache(0)\n'
        '    with pytest.raises(ValueError): LRUCache(-2)\n'
        'def test_len():\n'
        '    c = LRUCache(3); assert len(c) == 0\n'
        '    c.put("a", 1); c.put("b", 2); assert len(c) == 2\n')


def fix_scientific_001(tmp: Path):
    (tmp / 'robust.py').write_text(
        'import statistics\n'
        'def trimmed_mean(values, proportion):\n'
        '    s = sorted(values); n = len(s)\n'
        '    if n == 0: raise ValueError("empty")\n'
        '    k = int(proportion / 2 * n)\n'
        '    kept = s[k:n - k] if k else s[:]\n'
        '    if not kept: raise ValueError("all trimmed")\n'
        '    return sum(kept) / len(kept)\n'
        'def winsorized_std(values, proportion):\n'
        '    s = sorted(values); n = len(s)\n'
        '    if n == 0: raise ValueError("empty")\n'
        '    k = int(proportion / 2 * n)\n'
        '    if k and n - 2 * k <= 0: raise ValueError("all trimmed")\n'
        '    if k:\n'
        '        lo, hi = s[k], s[n - k - 1]\n'
        '        w = [lo] * k + s[k:n - k] + [hi] * k\n'
        '    else: w = s[:]\n'
        '    if not w: raise ValueError("all trimmed")\n'
        '    return statistics.pstdev(w)\n')


def fix_scientific_002(tmp: Path):
    (tmp / 'integrate.py').write_text(
        'def trapezoid(f, a, b, n):\n'
        '    h = (b - a) / n\n'
        '    s = 0.5 * f(a) + 0.5 * f(b)\n'
        '    for i in range(1, n):\n'
        '        s += f(a + i * h)\n'
        '    return s * h\n')


def fix_algorithm_001(tmp: Path):
    (tmp / 'search.py').write_text(
        'def bisect_index(xs, x):\n'
        '    lo, hi, ans = 0, len(xs) - 1, -1\n'
        '    while lo <= hi:\n'
        '        mid = (lo + hi) // 2\n'
        '        if xs[mid] == x:\n'
        '            ans = mid; hi = mid - 1\n'
        '        elif xs[mid] < x:\n'
        '            lo = mid + 1\n'
        '        else:\n'
        '            hi = mid - 1\n'
        '    return ans\n')


def fix_data_001(tmp: Path):    (tmp / 'summary.py').write_text(
        'import csv\n'
        'def summarize(csv_path):\n'
        '    totals = {}\n'
        '    with open(csv_path, newline="", encoding="utf-8") as fh:\n'
        '        for row in csv.reader(fh):\n'
        '            if len(row) < 2:\n'
        '                continue\n'
        '            try:\n'
        '                amt = float(row[1])\n'
        '            except ValueError:\n'
        '                continue\n'
        '            totals[row[0]] = totals.get(row[0], 0.0) + amt\n'
        '    return totals\n')


def fix_calib_001(tmp: Path):
    p = tmp / 'maths.py'
    p.write_text(p.read_text().replace('return a - b', 'return a + b'))


def fix_calib_002(tmp: Path):
    p = tmp / 'greet.py'
    p.write_text(p.read_text().replace(
        'raise NotImplementedError("implement greet()")',
        'return f"Hello, {name}!"'))


def fix_bugfix_003(tmp: Path):
    (tmp / 'counter.py').write_text(
        'import threading\n'
        '\n\n'
        'class Counter:\n'
        '    def __init__(self):\n'
        '        self.count = 0\n'
        '        self._lock = threading.Lock()\n'
        '\n'
        '    def increment(self, n=1):\n'
        '        with self._lock:\n'
        '            for _ in range(n):\n'
        '                self.count += 1\n'
        '\n'
        '    def value(self):\n'
        '        with self._lock:\n'
        '            return self.count\n')


def fix_refactor_003(tmp: Path):
    (tmp / 'auth.py').write_text(
        'def is_valid_email(email):\n'
        '    return "@" in email and "." in email.split("@")[-1]\n'
        '\n\n'
        'def is_valid_password(password):\n'
        '    return len(password) >= 8 and any(c.isdigit() for c in password)\n'
        '\n\n'
        'def register(email, password, users):\n'
        '    if not is_valid_email(email):\n'
        '        raise ValueError("invalid email")\n'
        '    if not is_valid_password(password):\n'
        '        raise ValueError("weak password")\n'
        '    if email in users:\n'
        '        raise ValueError("already registered")\n'
        '    users[email] = password\n'
        '    return True\n'
        '\n\n'
        'def change_password(email, old_password, new_password, users):\n'
        '    if not is_valid_email(email):\n'
        '        raise ValueError("invalid email")\n'
        '    if users.get(email) != old_password:\n'
        '        raise ValueError("wrong password")\n'
        '    if not is_valid_password(new_password):\n'
        '        raise ValueError("weak password")\n'
        '    users[email] = new_password\n'
        '    return True\n')


def fix_data_002(tmp: Path):
    (tmp / 'aggregate.py').write_text(
        'import json\n'
        'def summarize(path):\n'
        '    values = []\n'
        '    by_type = {}\n'
        '    with open(path, encoding="utf-8") as fh:\n'
        '        for line in fh:\n'
        '            if not line.strip():\n'
        '                continue\n'
        '            try:\n'
        '                rec = json.loads(line)\n'
        '            except ValueError:\n'
        '                continue\n'
        '            if not isinstance(rec, dict):\n'
        '                continue\n'
        '            t, v = rec.get("type"), rec.get("value")\n'
        '            if not isinstance(t, str):\n'
        '                continue\n'
        '            if not isinstance(v, (int, float)) or isinstance(v, bool):\n'
        '                continue\n'
        '            values.append(v)\n'
        '            by_type[t] = by_type.get(t, 0) + 1\n'
        '    return {"count": len(values),\n'
        '            "avg_value": sum(values) / len(values) if values else 0.0,\n'
        '            "by_type": by_type}\n')


def fix_cli_001(tmp: Path):
    p = tmp / 'fetch.py'
    src = p.read_text()
    old_main = src[src.index('def main('):]
    new_main = ('def main(argv=None):\n'
                '    import argparse\n'
                '    import sys\n'
                '    parser = argparse.ArgumentParser(description="Fetch with retries")\n'
                '    parser.add_argument("--retry", type=int, default=0)\n'
                '    args = parser.parse_args(argv)\n'
                '    last = None\n'
                '    for _ in range(args.retry + 1):\n'
                '        try:\n'
                '            print(attempt())\n'
                '            return 0\n'
                '        except RuntimeError as e:\n'
                '            last = e\n'
                '    print(f"failed after {args.retry + 1} attempts: {last}", file=sys.stderr)\n'
                '    return 2\n'
                '\n\n'
                'if __name__ == "__main__":\n'
                '    raise SystemExit(main())\n')
    p.write_text(src[:src.index('def main(')] + new_main)


def fix_scientific_003(tmp: Path):
    (tmp / 'softmax.py').write_text(
        'import math\n'
        'def softmax(xs):\n'
        '    xs = list(xs)\n'
        '    if not xs:\n'
        '        raise ValueError("empty")\n'
        '    m = max(xs)\n'
        '    exps = [math.exp(x - m) for x in xs]\n'
        '    total = sum(exps)\n'
        '    return [e / total for e in exps]\n')


def fix_algorithm_002(tmp: Path):
    (tmp / 'lru.py').write_text(
        'import threading\n'
        'from collections import OrderedDict\n'
        '\n\n'
        'class LRUCache:\n'
        '    def __init__(self, capacity):\n'
        '        if capacity <= 0:\n'
        '            raise ValueError("capacity must be > 0")\n'
        '        self.capacity = capacity\n'
        '        self._d = OrderedDict()\n'
        '        self._lock = threading.Lock()\n'
        '\n'
        '    def get(self, key):\n'
        '        with self._lock:\n'
        '            if key not in self._d:\n'
        '                return None\n'
        '            self._d.move_to_end(key)\n'
        '            return self._d[key]\n'
        '\n'
        '    def put(self, key, value):\n'
        '        with self._lock:\n'
        '            if key in self._d:\n'
        '                self._d.move_to_end(key)\n'
        '            self._d[key] = value\n'
        '            while len(self._d) > self.capacity:\n'
        '                self._d.popitem(last=False)\n'
        '\n'
        '    def __len__(self):\n'
        '        with self._lock:\n'
        '            return len(self._d)\n')


def fix_feature_003(tmp: Path):
    (tmp / 'config.py').write_text(
        'import copy\n'
        'import json\n'
        'from pathlib import Path\n'
        '\n'
        'DEFAULTS = {\n'
        '    "host": "localhost",\n'
        '    "port": 8080,\n'
        '    "debug": False,\n'
        '    "limits": {"cpu": 2, "mem": 512},\n'
        '}\n'
        '\n\n'
        'def _check(value, default, key):\n'
        '    if isinstance(default, bool):\n'
        '        if not isinstance(value, bool):\n'
        '            raise TypeError(key)\n'
        '    elif isinstance(default, int):\n'
        '        if not isinstance(value, int) or isinstance(value, bool):\n'
        '            raise TypeError(key)\n'
        '    elif isinstance(default, str):\n'
        '        if not isinstance(value, str):\n'
        '            raise TypeError(key)\n'
        '    elif isinstance(default, dict):\n'
        '        if not isinstance(value, dict):\n'
        '            raise TypeError(key)\n'
        '\n\n'
        'def _merge(base, upd):\n'
        '    out = copy.deepcopy(base)\n'
        '    for key, value in upd.items():\n'
        '        if key not in out:\n'
        '            raise KeyError(key)\n'
        '        if isinstance(out[key], dict):\n'
        '            if not isinstance(value, dict):\n'
        '                raise TypeError(key)\n'
        '            out[key] = _merge(out[key], value)\n'
        '        else:\n'
        '            _check(value, out[key], key)\n'
        '            out[key] = value\n'
        '    return out\n'
        '\n\n'
        'def load_config(path, overrides=None):\n'
        '    cfg = copy.deepcopy(DEFAULTS)\n'
        '    p = Path(path)\n'
        '    if p.exists():\n'
        '        data = json.loads(p.read_text(encoding="utf-8"))\n'
        '        if not isinstance(data, dict):\n'
        '            raise TypeError("top-level must be object")\n'
        '        cfg = _merge(cfg, data)\n'
        '    if overrides:\n'
        '        nested = {}\n'
        '        for key, value in overrides.items():\n'
        '            node = nested\n'
        '            parts = key.split(".")\n'
        '            for part in parts[:-1]:\n'
        '                node = node.setdefault(part, {})\n'
        '            node[parts[-1]] = value\n'
        '        cfg = _merge(cfg, nested)\n'
        '    return cfg\n')


def fix_test_003(tmp: Path):
    (tmp / 'tests' / 'test_retry.py').write_text(
        'import pytest\nfrom retry import with_retry\n'
        'def test_success_first_try():\n'
        '    calls = []\n'
        '    def fn():\n'
        '        calls.append(1)\n'
        '        return "ok"\n'
        '    assert with_retry(fn) == "ok"\n'
        '    assert len(calls) == 1\n'
        'def test_transient_then_success():\n'
        '    calls = []\n'
        '    def fn():\n'
        '        calls.append(1)\n'
        '        if len(calls) < 3:\n'
        '            raise ValueError("flaky")\n'
        '        return "recovered"\n'
        '    assert with_retry(fn, attempts=3) == "recovered"\n'
        '    assert len(calls) == 3\n'
        'def test_permanent_failure():\n'
        '    calls = []\n'
        '    def fn():\n'
        '        calls.append(1)\n'
        '        raise ValueError("always fails")\n'
        '    with pytest.raises(ValueError, match="always fails"):\n'
        '        with_retry(fn, attempts=4)\n'
        '    assert len(calls) == 4\n'
        'def test_unlisted_exception_no_retry():\n'
        '    calls = []\n'
        '    def fn():\n'
        '        calls.append(1)\n'
        '        raise TypeError("fatal")\n'
        '    with pytest.raises(TypeError):\n'
        '        with_retry(fn, attempts=5, exceptions=(ValueError,))\n'
        '    assert len(calls) == 1\n'
        'def test_attempts_one():\n'
        '    calls = []\n'
        '    def fn():\n'
        '        calls.append(1)\n'
        '        return 7\n'
        '    assert with_retry(fn, attempts=1) == 7\n'
        '    assert len(calls) == 1\n'
        'def test_bad_attempts():\n'
        '    with pytest.raises(ValueError):\n'
        '        with_retry(lambda: 1, attempts=0)\n'
        'def test_transient_custom_exception():\n'
        '    calls = []\n'
        '    def fn():\n'
        '        calls.append(1)\n'
        '        if len(calls) == 1:\n'
        '            raise KeyError("transient")\n'
        '        return "k"\n'
        '    assert with_retry(fn, attempts=2, exceptions=(KeyError,)) == "k"\n'
        '    assert len(calls) == 2\n')


FIXES = {
    'bugfix-003-race-condition': fix_bugfix_003,
    'refactor-003-extract-validator': fix_refactor_003,
    'data-002-jsonl-aggregate': fix_data_002,
    'cli-001-argparse-retry': fix_cli_001,
    'scientific-003-stable-softmax': fix_scientific_003,
    'algorithm-002-lru-cache': fix_algorithm_002,
    'feature-003-config-loader': fix_feature_003,
    'test-003-retry-behavior': fix_test_003,
    'calib-001-wrong-operator': fix_calib_001,
    'calib-002-greet': fix_calib_002,
    'bugfix-001-off-by-one': fix_bugfix_001,
    'bugfix-002-mutable-default': fix_bugfix_002,
    'feature-001-wordcount-cli': fix_feature_001,
    'feature-002-json-log-filter': fix_feature_002,
    'refactor-001-extract-discount': fix_refactor_001,
    'refactor-002-retry-helper': fix_refactor_002,
    'test-001-bank-tests': fix_test_001,
    'test-002-lru-tests': fix_test_002,
    'scientific-001-robust-stats': fix_scientific_001,
    'scientific-002-trapezoid': fix_scientific_002,
    'algorithm-001-binary-search': fix_algorithm_001,
    'data-001-csv-summary': fix_data_001,
}

failed = 0
for tf in sorted(Path('tasks').glob('*.yaml')):
    d = yaml.safe_load(open(tf, encoding='utf-8'))
    tid = d['id']
    tmp = Path(tempfile.mkdtemp())
    shutil.copytree(R / d['repo']['path'], tmp, dirs_exist_ok=True)
    if tid not in FIXES:
        print(f'NO-REFERENCE  {tid}')
        failed += 1
        continue
    FIXES[tid](tmp)
    ok = True
    for cmd in d['oracle']['command']:
        r = subprocess.run(cmd, shell=True, cwd=tmp,
                           capture_output=True, text=True)
        if r.returncode != 0:
            ok = False
            print(f'{tid}: ORACLE FAIL: {cmd}')
            print(r.stdout[-800:])
            print(r.stderr[-800:])
    ho = d.get('heldout')
    if ho:
        import shutil as _sh
        src = R / ho['path']
        for item in src.iterdir():
            s, dst = item, tmp / item.name
            if item.is_dir():
                _sh.copytree(s, dst, dirs_exist_ok=True)
            else:
                _sh.copy2(s, dst)
        for cmd in ho['command']:
            r = subprocess.run(cmd, shell=True, cwd=tmp,
                               capture_output=True, text=True)
            if r.returncode != 0:
                ok = False
                print(f'{tid}: HELDOUT FAIL: {cmd}')
                print(r.stdout[-800:])
                print(r.stderr[-800:])
    print(('SOLVABLE     ' if ok else 'NOT-SOLVABLE ') + tid)
    if not ok:
        failed += 1
    shutil.rmtree(tmp, ignore_errors=True)
raise SystemExit(1 if failed else 0)
