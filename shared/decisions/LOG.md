# Decision Log

Record decisions here so both agents stay aligned.

## 2026-04-16 — Two separate dashboards for Armada Prime

Keep `index.html` (Q1 2026 monthly-return / GP / consultant analytics) and new `tpa-dashboard.html` (TPA Reporting Package: Balance Sheet, Income Statement, Capital Schedule, Investor Capital Summary, Fees, Reconciliation) as **separate pages** with cross-links.

Rationale: the two data models are fundamentally different — the return dashboard is gross-return-driven with waterfall splits, while the TPA package is audit-grade accounting. Merging them into one file would have bloated the HTML and mixed business-operations reporting with external-admin bookkeeping.

Monthly workflow for TPA:
1. Save new month's xlsx anywhere.
2. Run `python tools/parse_tpa_report.py <path>` — `data/tpa_history.json` is upserted.
3. Commit + push; GitHub Pages refreshes within ~60s.

Password for TPA dashboard: `armada-tpa-2026` (SHA256 gate, same pattern as index.html).
