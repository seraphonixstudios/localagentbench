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


FIXES = {
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
