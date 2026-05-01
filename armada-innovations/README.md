# Armada Innovations LLC — GP Accounting

Tracks the GP economics of **Armada Capital Group LLP** (the new RE/PE-style fund — separate from Armada Prime LLP). The GP entity is **Armada Innovations LLC**, owned by:

| Member  | Share  | Role               |
| ------- | ------ | ------------------ |
| Nairne  | 60%    | Managing Member    |
| Alec    | 39.5%  | Capital Relations  |
| Chris   | 0.5%   | Member             |

## Files

- **index.html** — GP-focused dashboard. Member splits, monthly distribution waterfall, ITD totals.
- **acg-tpa.html** — Armada Capital Group LLP fund-level TPA dashboard (parallels `../tpa-dashboard.html` for Armada Prime LLP). Balance sheet, income statement, capital activity, PCAP, SOI, reconciliation.
- **data/acg_history.json** — single source of truth for both pages. Top-level keys: `fund`, `gp_entity`, `members`, `months[]`, `last_updated`.
- **data/armada-innovations-2026.xlsx** — manual workbook with High Level / Member Distribution / Capital Roll (PCAS template) / Fund Source / Source Trail tabs.

## Access

Both HTML pages share password **`innovations-2026`** and the same `ai_auth` session key — log in once on either page and the other unlocks for the rest of the browser session.

## Current data

Seeded with March 2026 only — first month with a GP distribution.

- ACG LLP total assets: $528,499.10
- LP commitments: Bliss $500K (funded), JJNA $8M (April 2026 close)
- GP distribution to Innovations: **$3,720**
  - Nairne 60% → $2,232.00
  - Alec 39.5% → $1,469.40
  - Chris 0.5% → $18.60

## Adding a new month

When the next TPA package arrives:

1. Open the TPA TB workbook. Read the `Trial Balance` sheet for balance-sheet / income-statement totals, the `PCAP - MTD` sheet for partner activity, and the `SOI` sheet for positions.
2. Append a new month object to `data/acg_history.json` (copy the March 2026 block as a template). Keep sign conventions: revenue Cr (negative), expense Dr (positive). Update `last_updated`.
3. Append a row to `data/armada-innovations-2026.xlsx` `High Level` tab (formula columns auto-fill the 60/39.5/0.5 split) and add a corresponding `Source Trail` row.
4. Reload either HTML page — month chip selector picks up new entries automatically.

## Cross-references

- Sister project: `../tpa-dashboard.html` (Armada Prime LLP TPA — same architecture)
- Returns dashboard: `../index.html` (Armada Prime LLP fund dashboard)
- See root `CLAUDE.md` for entity structure across both funds.
