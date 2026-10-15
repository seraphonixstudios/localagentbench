# LocalAgentBench report

Model: `ollama/qwen3:8b-gpu` · Agent: `aider` · Runs: 22 · Success rate: 59.1%
Avg wall: 61.5s · Tokens in/out: 9477/9352 · Tool calls: 22 (failed: 0)

## Per-task

| task | n | pass@1 | pass@k | heldout | avg wall |
|---|---|---|---|---|---|
| algorithm-001-binary-search | 1 | 100% | 100% | 100% | 31.3s |
| algorithm-002-lru-cache | 1 | 100% | 100% | 100% | 47.0s |
| bugfix-001-off-by-one | 1 | 100% | 100% | 100% | 27.1s |
| bugfix-002-mutable-default | 1 | 100% | 100% | 100% | 24.0s |
| bugfix-003-race-condition | 1 | 100% | 100% | 100% | 30.5s |
| calib-001-wrong-operator | 1 | 100% | 100% | 100% | 17.7s |
| calib-002-greet | 1 | 100% | 100% | 100% | 15.5s |
| cli-001-argparse-retry | 1 | 0% | 0% | 0% | 47.1s |
| data-001-csv-summary | 1 | 0% | 0% | 100% | 30.3s |
| data-002-jsonl-aggregate | 1 | 100% | 100% | 100% | 31.7s |
| feature-001-wordcount-cli | 1 | 100% | 100% | 100% | 28.8s |
| feature-002-json-log-filter | 1 | 100% | 100% | 100% | 31.2s |
| feature-003-config-loader | 1 | 0% | 0% | 0% | 42.0s |
| refactor-001-extract-discount | 1 | 0% | 0% | 0% | 28.6s |
| refactor-002-retry-helper | 1 | 0% | 0% | 0% | 600.0s |
| refactor-003-extract-validator | 1 | 0% | 0% | 0% | 27.5s |
| scientific-001-robust-stats | 1 | 0% | 0% | 100% | 81.0s |
| scientific-002-trapezoid | 1 | 100% | 100% | 100% | 33.5s |
| scientific-003-stable-softmax | 1 | 100% | 100% | 100% | 35.2s |
| test-001-bank-tests | 1 | 100% | 100% | — | 73.4s |
| test-002-lru-tests | 1 | 0% | 0% | — | 39.1s |
| test-003-retry-behavior | 1 | 0% | 0% | — | 31.5s |

## Runs

| run | task | success | heldout | wall | tokens | tools |
|---|---|---|---|---|---|---|
| algorithm-001-binary-search-ced86a4d | algorithm-001-binary-search | PASS | PASS | 31.263s | 703/950 | 1 |
| algorithm-002-lru-cache-303e4bd0 | algorithm-002-lru-cache | PASS | PASS | 47.038s | -/- | 1 |
| bugfix-001-off-by-one-4abfd193 | bugfix-001-off-by-one | PASS | PASS | 27.056s | 694/688 | 1 |
| bugfix-002-mutable-default-d8ec4cf7 | bugfix-002-mutable-default | PASS | PASS | 24.017s | 710/549 | 1 |
| bugfix-003-race-condition-5ed71d9f | bugfix-003-race-condition | PASS | PASS | 30.507s | 718/866 | 1 |
| calib-001-wrong-operator-676c0832 | calib-001-wrong-operator | PASS | PASS | 17.658s | 684/299 | 1 |
| calib-002-greet-eccc1f19 | calib-002-greet | PASS | PASS | 15.48s | 688/183 | 1 |
| cli-001-argparse-retry-e199fa07 | cli-001-argparse-retry | FAIL | FAIL | 47.125s | -/- | 1 |
| data-001-csv-summary-0891bc50 | data-001-csv-summary | FAIL | PASS | 30.346s | 729/857 | 2 |
| data-002-jsonl-aggregate-1cbf3dea | data-002-jsonl-aggregate | PASS | PASS | 31.73s | 797/929 | 1 |
| feature-001-wordcount-cli-dfe3c087 | feature-001-wordcount-cli | PASS | PASS | 28.843s | 735/785 | 1 |
| feature-002-json-log-filter-dcaaec61 | feature-002-json-log-filter | PASS | PASS | 31.241s | 715/901 | 1 |
| feature-003-config-loader-28123737 | feature-003-config-loader | FAIL | FAIL | 42.02s | -/- | 1 |
| refactor-001-extract-discount-36681ca7 | refactor-001-extract-discount | FAIL | FAIL | 28.631s | 719/751 | 1 |
| refactor-002-retry-helper-c1d6cfe0 | refactor-002-retry-helper | FAIL | FAIL | 600.024s | -/- | 0 |
| refactor-003-extract-validator-ece233bc | refactor-003-extract-validator | FAIL | FAIL | 27.503s | 742/719 | 1 |
| scientific-001-robust-stats-00c39a5e | scientific-001-robust-stats | FAIL | PASS | 80.993s | -/- | 1 |
| scientific-002-trapezoid-d3e81624 | scientific-002-trapezoid | PASS | PASS | 33.454s | -/- | 1 |
| scientific-003-stable-softmax-00a70fb0 | scientific-003-stable-softmax | PASS | PASS | 35.184s | -/- | 1 |
| test-001-bank-tests-24240d4c | test-001-bank-tests | PASS | — | 73.359s | -/- | 1 |
| test-002-lru-tests-1bbe6acd | test-002-lru-tests | FAIL | — | 39.091s | -/- | 1 |
| test-003-retry-behavior-95d0eb3a | test-003-retry-behavior | FAIL | — | 31.517s | 843/875 | 1 |

## Human preference (placeholder)
Export run pairs for later pairwise ranking; see `preference-template.csv`.
