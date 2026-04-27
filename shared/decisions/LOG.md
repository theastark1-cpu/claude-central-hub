# Decision Log

Record decisions here so both agents stay aligned.

## 2026-04-27 — Consultant compensation calculated off TPA, not internal model

The internal Monthly Return file recalculates each investor's P&L from a flat fund-level return %; the TPA package uses actual per-investor accruals. Consultant compensation now flows from TPA's per-investor performance-fee column (the GP pool), not the internal makeshift sheet.

Reconciliation insight (frozen here so future agents don't relitigate):
- TPA "Gross Income" = the Fund's 82% cut. TruQuant's 18% is taken upstream and never enters Armada Prime's books.
- TPA "Performance Fees Crystallized" = the GP Cut (30% of Fund cut). Splits 59.5/39/0.5/0.5/0.5 (Mgmt/Consultant/Raj/Nairne/Phil).
- TPA "Net to Investors" = Investor Cut (70% of Fund cut), matches internal 2.41% net return.

Investor → consultant mapping is sourced from the internal IDS sheet, with confirmed overrides hardcoded in `tools/build_consultant_splits.py` (`CONSULTANT_OVERRIDES`). For March 2026: Philippe Henriques + PGJCHoldings + Mashirito + Weston Shea Christensen → Alec Atkinson; Fund Hub Investments LLC → "Fund Hub SPV (Pending Split)" since it's a sub-LP container with mixed AJ/Alec investors that needs a separate buildout.

Monthly workflow:
1. Save TPA package xlsx anywhere.
2. Run `python tools/build_consultant_splits.py <path>` (regenerates both Excel + JSON).
3. Commit + push; GitHub Pages refreshes within ~60s.

Password for Consultant Splits dashboard: `armada2026` (same SHA256 hash as `index.html`, separate sessionStorage key `ap_splits_auth`).

## 2026-04-16 — Two separate dashboards for Armada Prime

Keep `index.html` (Q1 2026 monthly-return / GP / consultant analytics) and new `tpa-dashboard.html` (TPA Reporting Package: Balance Sheet, Income Statement, Capital Schedule, Investor Capital Summary, Fees, Reconciliation) as **separate pages** with cross-links.

Rationale: the two data models are fundamentally different — the return dashboard is gross-return-driven with waterfall splits, while the TPA package is audit-grade accounting. Merging them into one file would have bloated the HTML and mixed business-operations reporting with external-admin bookkeeping.

Monthly workflow for TPA:
1. Save new month's xlsx anywhere.
2. Run `python tools/parse_tpa_report.py <path>` — `data/tpa_history.json` is upserted.
3. Commit + push; GitHub Pages refreshes within ~60s.

Password for TPA dashboard: `armada-tpa-2026` (SHA256 gate, same pattern as index.html).
