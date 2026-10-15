# LocalAgentBench report

Model: `ollama/qwen3:8b-gpu` · Agent: `opencode` · Runs: 22 · Success rate: 22.7%
Avg wall: 56.4s · Tokens in/out: 34782/31872 · Tool calls: 14 (failed: 2)

## Per-task

| task | n | pass@1 | pass@k | heldout | avg wall |
|---|---|---|---|---|---|
| algorithm-001-binary-search | 1 | 0% | 0% | 0% | 52.8s |
| algorithm-002-lru-cache | 1 | 0% | 0% | 0% | 48.3s |
| bugfix-001-off-by-one | 1 | 0% | 0% | 0% | 65.1s |
| bugfix-002-mutable-default | 1 | 0% | 0% | — | 26.5s |
| bugfix-003-race-condition | 1 | 100% | 100% | 100% | 39.1s |
| calib-001-wrong-operator | 1 | 0% | 0% | — | 18.6s |
| calib-002-greet | 1 | 0% | 0% | — | 300.0s |
| cli-001-argparse-retry | 1 | 0% | 0% | 0% | 29.2s |
| data-001-csv-summary | 1 | 100% | 100% | 100% | 24.3s |
| data-002-jsonl-aggregate | 1 | 0% | 0% | 100% | 41.3s |
| feature-001-wordcount-cli | 1 | 0% | 0% | 100% | 23.9s |
| feature-002-json-log-filter | 1 | 100% | 100% | — | 19.2s |
| feature-003-config-loader | 1 | 0% | 0% | 0% | 93.9s |
| refactor-001-extract-discount | 1 | 0% | 0% | — | 25.7s |
| refactor-002-retry-helper | 1 | 0% | 0% | — | 56.4s |
| refactor-003-extract-validator | 1 | 0% | 0% | 0% | 58.8s |
| scientific-001-robust-stats | 1 | 0% | 0% | — | 86.6s |
| scientific-002-trapezoid | 1 | 100% | 100% | — | 28.3s |
| scientific-003-stable-softmax | 1 | 100% | 100% | 100% | 31.0s |
| test-001-bank-tests | 1 | 0% | 0% | — | 66.0s |
| test-002-lru-tests | 1 | 0% | 0% | — | 59.5s |
| test-003-retry-behavior | 1 | 0% | 0% | — | 45.3s |

## Runs

| run | task | success | heldout | wall | tokens | tools |
|---|---|---|---|---|---|---|
| algorithm-001-binary-search-8a86d7ce | algorithm-001-binary-search | FAIL | FAIL | 52.779s | -/- | 0 |
| algorithm-002-lru-cache-53385342 | algorithm-002-lru-cache | FAIL | FAIL | 48.324s | -/- | 0 |
| bugfix-001-off-by-one-95b7eb8d | bugfix-001-off-by-one | FAIL | FAIL | 65.097s | -/- | 0 |
| bugfix-002-mutable-default-a7634cab | bugfix-002-mutable-default | FAIL | — | 26.542s | 2046/757 | 1 |
| bugfix-003-race-condition-dd945436 | bugfix-003-race-condition | PASS | PASS | 39.1s | 4092/1354 | 2 |
| calib-001-wrong-operator-8b8a8acd | calib-001-wrong-operator | FAIL | — | 18.589s | 2046/438 | 1 |
| calib-002-greet-709bd17f | calib-002-greet | FAIL | — | 300.023s | -/- | 0 |
| cli-001-argparse-retry-2c1d9196 | cli-001-argparse-retry | FAIL | FAIL | 29.155s | 2046/1436 | 1 |
| data-001-csv-summary-e67034a6 | data-001-csv-summary | PASS | PASS | 24.307s | 2046/1232 | 1 |
| data-002-jsonl-aggregate-5b45da86 | data-002-jsonl-aggregate | FAIL | PASS | 41.332s | 2046/2280 | 2 |
| feature-001-wordcount-cli-7a6496b1 | feature-001-wordcount-cli | FAIL | PASS | 23.866s | 2046/963 | 1 |
| feature-002-json-log-filter-233060fc | feature-002-json-log-filter | PASS | — | 19.23s | 2046/745 | 1 |
| feature-003-config-loader-3217b2d3 | feature-003-config-loader | FAIL | FAIL | 93.879s | 2046/5907 | 0 |
| refactor-001-extract-discount-bdf69e85 | refactor-001-extract-discount | FAIL | — | 25.678s | 2046/1187 | 1 |
| refactor-002-retry-helper-b7b11e71 | refactor-002-retry-helper | FAIL | — | 56.364s | 2046/3489 | 0 |
| refactor-003-extract-validator-a8602011 | refactor-003-extract-validator | FAIL | FAIL | 58.795s | 2046/516 | 1 |
| scientific-001-robust-stats-61eb6ec7 | scientific-001-robust-stats | FAIL | — | 86.615s | 2046/5408 | 0 |
| scientific-002-trapezoid-e0c45efd | scientific-002-trapezoid | PASS | — | 28.286s | 2046/977 | 1 |
| scientific-003-stable-softmax-9ae39f32 | scientific-003-stable-softmax | PASS | PASS | 31.027s | 2046/973 | 1 |
| test-001-bank-tests-1dc32c58 | test-001-bank-tests | FAIL | — | 66.007s | 2046/4210 | 0 |
| test-002-lru-tests-115455d6 | test-002-lru-tests | FAIL | — | 59.516s | -/- | 0 |
| test-003-retry-behavior-627b3a38 | test-003-retry-behavior | FAIL | — | 45.323s | -/- | 0 |

## Human preference (placeholder)
Export run pairs for later pairwise ranking; see `preference-template.csv`.
