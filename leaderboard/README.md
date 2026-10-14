# Leaderboard (published to GitHub Pages)

This folder holds the **curated, published** benchmark site. It is a snapshot —
refresh it deliberately when new headline results land:

```bash
# after a notable run, e.g. results/qwen3-k3:
Copy-Item ./results/<run>/site/* ./leaderboard/ -Force
git add leaderboard && git commit -m "Leaderboard: <model> <score>" && git push
```

Raw per-run bundles live under `results/` (git-ignored); only promoted
snapshots belong here. Deployed by `.github/workflows/pages.yml`.
