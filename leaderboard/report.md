# LocalAgentBench report

Model: `ollama/qwen3:8b-gpu` · Agent: `opencode` · Runs: 42 · Success rate: 47.6%
Avg wall: 101.4s · Tokens in/out: 82294/108498 · Tool calls: 167 (failed: 4)

## Per-task

| task | n | pass@1 | pass@k | heldout | avg wall |
|---|---|---|---|---|---|
| algorithm-001-binary-search | 3 | 100% | 100% | — | 54.1s |
| bugfix-001-off-by-one | 3 | 67% | 100% | — | 128.1s |
| bugfix-002-mutable-default | 3 | 0% | 0% | — | 57.8s |
| calib-001-wrong-operator | 3 | 0% | 0% | — | 188.0s |
| calib-002-greet | 3 | 100% | 100% | — | 49.1s |
| data-001-csv-summary | 3 | 67% | 100% | — | 68.8s |
| feature-001-wordcount-cli | 3 | 100% | 100% | — | 47.8s |
| feature-002-json-log-filter | 3 | 100% | 100% | — | 46.9s |
| refactor-001-extract-discount | 3 | 0% | 0% | — | 133.0s |
| refactor-002-retry-helper | 3 | 0% | 0% | — | 128.4s |
| scientific-001-robust-stats | 3 | 0% | 0% | — | 145.2s |
| scientific-002-trapezoid | 3 | 100% | 100% | — | 122.9s |
| test-001-bank-tests | 3 | 33% | 100% | — | 116.8s |
| test-002-lru-tests | 3 | 0% | 0% | — | 132.0s |

## Runs

| run | task | success | heldout | wall | tokens | tools |
|---|---|---|---|---|---|---|
| algorithm-001-binary-search-30746249 | algorithm-001-binary-search | PASS | — | 46.936s | 2046/1726 | 1 |
| algorithm-001-binary-search-3814d023 | algorithm-001-binary-search | PASS | — | 83.123s | 2046/1294 | 1 |
| algorithm-001-binary-search-ffeeffc8 | algorithm-001-binary-search | PASS | — | 32.281s | 116/1264 | 1 |
| bugfix-001-off-by-one-04a5669f | bugfix-001-off-by-one | PASS | — | 154.326s | 4093/2474 | 3 |
| bugfix-001-off-by-one-793a09d2 | bugfix-001-off-by-one | FAIL | — | 195.659s | 4134/10029 | 44 |
| bugfix-001-off-by-one-9965f4e9 | bugfix-001-off-by-one | PASS | — | 34.26s | 2047/1343 | 2 |
| bugfix-002-mutable-default-748fb5de | bugfix-002-mutable-default | FAIL | — | 94.108s | 2046/544 | 1 |
| bugfix-002-mutable-default-ba566b78 | bugfix-002-mutable-default | FAIL | — | 25.02s | 2046/743 | 1 |
| bugfix-002-mutable-default-bcf8f154 | bugfix-002-mutable-default | FAIL | — | 54.364s | -/- | 0 |
| calib-001-wrong-operator-74563295 | calib-001-wrong-operator | FAIL | — | 28.771s | 2047/930 | 2 |
| calib-001-wrong-operator-afc8a9ec | calib-001-wrong-operator | FAIL | — | 235.224s | 4096/4205 | 6 |
| calib-001-wrong-operator-c06d6712 | calib-001-wrong-operator | FAIL | — | 300.028s | 4162/16139 | 53 |
| calib-002-greet-ac00ca00 | calib-002-greet | PASS | — | 17.506s | 1/260 | 2 |
| calib-002-greet-b17047a8 | calib-002-greet | PASS | — | 31.867s | 2046/451 | 2 |
| calib-002-greet-e2294133 | calib-002-greet | PASS | — | 97.957s | 4092/657 | 3 |
| data-001-csv-summary-0f4d63b6 | data-001-csv-summary | PASS | — | 16.603s | 1/567 | 1 |
| data-001-csv-summary-2c42bb09 | data-001-csv-summary | PASS | — | 17.875s | 2046/596 | 1 |
| data-001-csv-summary-3d69c671 | data-001-csv-summary | FAIL | — | 171.833s | -/- | 0 |
| feature-001-wordcount-cli-03b713f9 | feature-001-wordcount-cli | PASS | — | 19.582s | 1/785 | 1 |
| feature-001-wordcount-cli-5a619e22 | feature-001-wordcount-cli | PASS | — | 26.064s | 2046/925 | 1 |
| feature-001-wordcount-cli-bfc1aa79 | feature-001-wordcount-cli | PASS | — | 97.758s | 2046/1214 | 1 |
| feature-002-json-log-filter-ab2c5a60 | feature-002-json-log-filter | PASS | — | 28.563s | 2046/1015 | 1 |
| feature-002-json-log-filter-f42513bd | feature-002-json-log-filter | PASS | — | 77.804s | 2046/1052 | 1 |
| feature-002-json-log-filter-f4f8a61e | feature-002-json-log-filter | PASS | — | 34.453s | 1/1248 | 1 |
| refactor-001-extract-discount-112a6181 | refactor-001-extract-discount | FAIL | — | 300.034s | 4099/6302 | 9 |
| refactor-001-extract-discount-98c9874d | refactor-001-extract-discount | FAIL | — | 30.172s | 1/1104 | 1 |
| refactor-001-extract-discount-bee2185a | refactor-001-extract-discount | FAIL | — | 68.805s | 4097/3430 | 7 |
| refactor-002-retry-helper-53dd5d84 | refactor-002-retry-helper | FAIL | — | 261.943s | 2046/5464 | 0 |
| refactor-002-retry-helper-afac5a25 | refactor-002-retry-helper | FAIL | — | 49.475s | -/- | 0 |
| refactor-002-retry-helper-e65ce678 | refactor-002-retry-helper | FAIL | — | 73.847s | 4092/1152 | 2 |
| scientific-001-robust-stats-235bb960 | scientific-001-robust-stats | FAIL | — | 75.329s | -/- | 0 |
| scientific-001-robust-stats-943b1045 | scientific-001-robust-stats | FAIL | — | 112.677s | 2046/6566 | 0 |
| scientific-001-robust-stats-f2e7c036 | scientific-001-robust-stats | FAIL | — | 247.504s | 2046/5342 | 0 |
| scientific-002-trapezoid-33f4c05a | scientific-002-trapezoid | PASS | — | 300.028s | 4111/6637 | 13 |
| scientific-002-trapezoid-885e48e4 | scientific-002-trapezoid | PASS | — | 29.176s | 2046/1381 | 1 |
| scientific-002-trapezoid-965342a4 | scientific-002-trapezoid | PASS | — | 39.414s | 2046/1505 | 1 |
| test-001-bank-tests-77c4c55f | test-001-bank-tests | PASS | — | 190.321s | 2061/2377 | 2 |
| test-001-bank-tests-d06469f4 | test-001-bank-tests | FAIL | — | 101.922s | 168/3688 | 0 |
| test-001-bank-tests-f33f3c12 | test-001-bank-tests | FAIL | — | 58.306s | 2046/3252 | 0 |
| test-002-lru-tests-11cbcbee | test-002-lru-tests | FAIL | — | 242.851s | 2046/4382 | 0 |
| test-002-lru-tests-ed115d07 | test-002-lru-tests | FAIL | — | 73.677s | 2046/1720 | 1 |
| test-002-lru-tests-faa3b033 | test-002-lru-tests | FAIL | — | 79.444s | 2046/4735 | 0 |

## Human preference (placeholder)
Export run pairs for later pairwise ranking; see `preference-template.csv`.
