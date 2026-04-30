# Decision Log

Record decisions here so both agents stay aligned.

## 2026-04-30 — Armada Prime Tech LLC 2025 year-end reconciliation built (1099/K-1 prep)

Per Nairne, year-end accounting for the GP entity Armada Prime Tech LLC for tax year 2025. Scope decisions:

- **Period**: Aug 1, 2025 – Dec 31, 2025 only. Armada Prime Tech LLC didn't exist before Aug 2025; the Jan–Jul 2025 fund was Arcane Capital Partners with a separate (different) GP entity, separate tax filing.
- **K-1 members (per Nairne)**: Raj Duggal (50%) and Nairne (50%) of GP net income. Everyone else who got GP-pool payouts is a 1099 contractor — including Phil (0.5% slice in 2025), Fund Mgmt entity (59.5%), all consultants in the 39% pool, and TruQuant for the August-only "Trader & Developer" line.
- **Source of truth**: TPA Reporting Packages (Performance Fees Crystallized) for what GP earned. Distributions Armada Tech 2025 (INTERNAL ONLY) ledger for what GP actually paid out (cash basis). Both views included in deliverable.
- **August 2025 anomaly recognized**: Aug used a different waterfall (9.5% Consultant + 13.5% Trader & Developer + 5.5% Mgmt + 1.5% to Raj/Nairne/Phil = 30% of true gross). TruQuant's 18% moved upstream of the GP entity from September onwards.
- **TruQuant excluded from GP expenses entirely (per Nairne 2026-04-30)**: even the August "Trader & Developer" $6,909.93 and Spydr $170.86 (Aug+Sep) are NOT 1099 expenses of Armada Prime Tech LLC. TQ's relationship is upstream of the GP entity.
- **Fund Mgmt 59.5% slice IS Nairne's K-1 income, NOT a separate entity 1099 (per Nairne 2026-04-30)**: Nairne owns 60% of Armada Prime Tech LLC (= 59.5% Fund Mgmt + 0.5% direct). Raj owns 0.5%. This is partnership-correct accounting: partner allocations don't reduce partnership net income; only contractor 1099 expenses + op expenses do.

Headline numbers (corrected partnership accounting):
- 2025 GP gross income (TPA-authoritative): **$153,023.03**
- 2025 1099 contractor expenses: **$54,491.59** (Alec $38,076.87; Jake $10,388.66; AJ $4,152.70; Phil $946.97; Issac $761.49; Luke $164.90)
- 2025 GP-paid op expenses (preliminary, subject to reclass): **$91,225** (includes $25k Oct 506c SPV Loan and $18k Dec Insurance which the accountant likely needs to reclass — adjusted ~$51K)
- 2025 Partnership net income (allocated to K-1 partners): **+$7,306.44** (positive! was previously shown as a loss because Fund Mgmt was mistakenly counted as expense)
- 2025 K-1 cash distributions: Nairne $85,996.83 (Fund Mgmt $85,049.86 + direct $946.97); Raj $946.97
- 2025 K-1 allocated net income (per derived ownership 99.17/0.83): Nairne $7,246.06; Raj $60.38

Deliverable files:
- `tools/build_2025_year_end.py` — aggregator (re-runnable)
- `2025-armada-prime-tech-1099-k1.xlsx` — 8-tab workbook for the accountant (Summary, 1099 Summary, K-1 Summary, Monthly Detail, Per-Consultant Monthly, GP Expenses, Distributions Ledger, Reconciliation)
- `2025-armada-prime-tech-summary.md` — narrative summary

Open items before sending to accountant: Fund Mgmt entity name+EIN, Phil's last name+SSN, TruQuant 1099 treatment, op expense reclassification (esp. SPV Loans + Insurance), per-recipient SSN/address.

## 2026-04-30 — Accelerated Consulting Capital Relations OS scaffolded in `accelerated-os/`

The Alec Playbook (April 2026, v1.0) was implemented as `accelerated-os/`: a Capital Relations Operating System for converting Alec's ~5K-name UHNW network into systematic relationships across Armada Prime LLP and adjacent products. Brand was renamed mid-build from "Cipher Strategies" to "Accelerated Consulting" (per Nairne 2026-04-30).

Architecture decisions (frozen):
- **CRM source-of-truth**: GoHighLevel (already provisioned with 5K contacts loaded). Custom fields, pipelines, sequences spec'd in `accelerated-os/GHL_CONFIG_SPEC.md`. Wiring is manual GHL UI work.
- **Intelligence layer**: this repo, in `accelerated-os/`. Voice memo intake (Telegram → Whisper → Claude structuring → GHL writeback), draft engine (Claude in Alec's voice → mobile approval inbox → GHL send), daily brief, weekly audit, monthly LP notes, quarterly newsletter.
- **Scheduling**: GitHub Actions cron (reuses pattern from `yt-automation/.github/workflows/daily-ideas.yml`).
- **Voice memo capture**: Telegram bot (default; reconsider WhatsApp Business API in Phase 2 if friction).
- **Approval inbox UI**: dedicated mobile-first HTML (gh-pages) with swipe approve/edit/reject. SMS-based reply approval was rejected — edit-in-place can't work over SMS.
- **Newsletter**: Substack for T3/T4 quarterly. GHL native and Beehiiv rejected — Substack has the strongest UHNW-curated-reading brand association.
- **Voice cloning** (ElevenLabs etc.): deferred to Phase 6 and scoped to T3/T4 voicemails only — voice-cloning T1/T2 fails the "Alec's actual voice" trust contract.

Roles:
- Alec is the principal (sender, voice memo source, decision-maker).
- Nairne is the operator (Amber-equivalent: tiers DB, drafts follow-ups, runs dinners, owns the system).
- Sends always under Alec's name and number/email; Amber's email is exposed only as the logistics contact in dinner invites.

Key files:
- Plan: `~/.claude/plans/users-nairne-downloads-alecplaybook-doc-joyful-gizmo.md`
- Repo: `accelerated-os/README.md` (entry point), `accelerated-os/GHL_CONFIG_SPEC.md`, `accelerated-os/tiering_worksheet.md`
- Templates: `accelerated-os/draft_engine/prompts/` (14 files, one per Layer 5 template)
- Playbooks: `accelerated-os/playbooks/` (Milken, LA dinner, NYC dinner, operating cadence)
- Code: `accelerated-os/voice_memo/`, `accelerated-os/draft_engine/`, `accelerated-os/orchestrator/`, `accelerated-os/approval_inbox/`, `accelerated-os/daily_brief/`

Status: Phase 1 build is on the Claude side complete (this commit). Phase 1 finishes when (1) GHL is wired per spec, (2) the 5K is tiered, (3) GitHub Secrets are set, (4) Telegram bot is created. Real first stress test is the LA dinner late June, not Milken.

Recurring monthly cost target: ~$1,000–1,200/mo (GHL Agency Pro $497, Claude API $300–500, Whisper $20–30, LinkedIn Sales Nav $99, Notion $16, R2 $5, misc $50).

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
