---
type: procedural
title: Run Python data analysis with uv ephemeral dependencies
project: global
created: 2026-10-02
updated: 2026-10-02
status: active
tags: [python, data, uv]
---

## When to use
Any Python data analysis in the cloud container (pandas/numpy/duckdb/openpyxl are not installed).

## Steps
1. Write the analysis as a script file (reproducible), e.g. `projects/<slug>/analysis/x.py`.
2. Run: `uv run --with pandas --with numpy --with openpyxl --with duckdb python <script>`
   (add `--with matplotlib`, `scipy`, `statsmodels` as needed). Cold start ≈4 s, cached after.
3. Do not `pip install` globally — the container is ephemeral and global installs hide dependencies.
