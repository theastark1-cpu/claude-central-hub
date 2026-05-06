# Monily Tax Organizer — Document Package
## Armada Prime Tech LLC — Tax Year 2025

**Prepared:** 2026-05-05
**Period of operations:** Aug 1, 2025 – Dec 31, 2025 (entity formed at Armada Prime LLP relaunch)
**Filing status:** First year of filing
**Tax classification:** Multi-member LLC, partnership for tax purposes

---

## What's in this package

| File | Purpose |
|---|---|
| `01_Profit_and_Loss_Statement_2025.xlsx` | Full P&L with both GAAP and tax-reclass columns |
| `02_Balance_Sheet_2025.xlsx` | Best-effort balance sheet (placeholders flagged for accountant) |
| `03_General_Ledger_2025.xlsx` | Transaction-level cash ledger, all 5 months |
| `04_Asset_Schedule_2025.xlsx` | Fixed asset / depreciation schedule (none for 2025) |
| `05_Cover_Memo_for_Monily.md` | This document |
| **Bonus** `2025-armada-prime-tech-1099-k1.xlsx` | Standalone 15-tab workbook with monthly detail, 1099 list, K-1 allocation, reconciliation |

---

## Headline Numbers (2025)

| Line | GAAP-Basis | After Tax-Reclass |
|---|---:|---:|
| **Revenue** (Performance Fees from Armada Prime LLP) | $153,023.03 | $153,023.03 |
| Direct Costs (1099 contractor commissions) | ($54,491.59) | ($54,491.59) |
| Operating Expenses | ($91,225.00) | ($51,450.00) |
| **Net Income (Partnership)** | **$7,306.44** | **$47,081.44** |

The GAAP→reclass swing is the **$29,275 in 506c SPV Loans** (move to balance sheet as loan receivable / equity investment) and **$10,500 in Insurance proration** (Dec $18K is annual D&O — only 5/12 should hit 2025 P&L, the rest is prepaid).

---

## Member Structure & K-1 Allocation

| Member | Ownership % | Cash Distributions Received | K-1 Allocated Net Income (Reclass-Basis) |
|---|---:|---:|---:|
| **Nairne** | 99.17% (60/60.5) | $85,996.83 | $46,692.34 |
| **Raj Duggal** | 0.83% (0.5/60.5) | $946.97 | $389.10 |

Nairne's 60% = Fund Management 59.5% slice + direct 0.5%. The Fund Management slice is K-1 income to Nairne (NOT a separate entity expense / 1099). Raj's 0.5% direct slice is also K-1 income.

---

## 1099-NEC Recipients (Aug–Dec 2025 totals)

The following individuals/entities received contractor payments and need 1099-NECs:

| Recipient | 2025 Total |
|---|---:|
| Alec Atkinson | $38,076.87 |
| Jake Gordon | $10,388.66 |
| AJ Affleck | $4,152.70 |
| Phil (last name TBD) | $946.97 |
| Issac Morris | $761.49 |
| Luke Affleck | $164.90 |
| Chris (operating contractor) | $11,500.00 |
| **Total 1099 Payments** | **$65,991.59** |

Note: Chris's $11,500 (Nov $7,500 + Dec $4,000) is in Operating Expenses on the P&L, not Direct Costs. Still requires a 1099-NEC.

Recipients' SSN/EIN + addresses need to be collected separately.

---

## Operating Expenses Summary

| Category | GAAP Amount | Reclass-Adjusted | Reclass Reason |
|---|---:|---:|---|
| Insurance | $18,000.00 | $7,500.00 | Annual D&O policy → pro-rate to 5/12 of year |
| Chris (contractor labor) | $11,500.00 | $11,500.00 | — |
| PVD | $12,000.00 | $12,000.00 | — *(verify vendor for 1099)* |
| Website | $7,500.00 | $7,500.00 | — |
| Ad Spend / Marketing | $5,000.00 | $5,000.00 | — *(verify vendor for 1099)* |
| Alpha Verification | $2,250.00 | $2,250.00 | — |
| TPA Admin Fees | $5,700.00 | $5,700.00 | — *(may overlap fund-level admin)* |
| 506c SPV Loan | $29,275.00 | $0.00 | **MOVE TO BALANCE SHEET (loan/capital)** |
| **Total** | **$91,225.00** | **$51,450.00** | |

---

## Methodology & Source Documents

### Revenue Recognition
- Source: TPA (Formidium) Reporting Packages, "Performance Fees Crystallized" line, monthly Aug–Dec 2025
- This is the gross GP cut earned by Armada Prime Tech LLC from Armada Prime LLP
- TruQuant's 18% upstream cut (and the August "Trader & Developer" / "Spydr" amounts paid inside the GP entity in August only) are EXCLUDED — these belong upstream of this entity per a 2026-04-30 policy decision

### Distribution Tracking
- Source: Internal "Distributions Armada Tech 2025 (INTERNAL ONLY)" ledger
- All payments are CASH BASIS — what was actually disbursed in each month
- Per-recipient amounts are NET (already after weighted costs / Coinbase fees applied at the disbursement layer)

### Operating Expenses
- Source: "Costs" sections of each month's Distributions ledger (Aug–Nov) plus "BEST ONE of December 2025 Monthly Return.xlsx" Costs tab (Dec)

### Member Structure
- Confirmed by the user on 2026-04-30
- Nairne owns 60% (= Fund Mgmt 59.5% + direct 0.5%); Raj owns 0.5%
- Phil's 0.5% slice is a 1099 payment, not a member allocation (Phil is not an LLC member; Phil was replaced by Alec as an equity-holding GP in April 2026, but for 2025 Phil received a 1099)

---

## Open Items the Accountant Will Need

1. **EIN** — from IRS letter (CP-575 / 147C)
2. **Formation documents** — Articles of Organization / Certificate of Formation for the LLC
3. **Registered address + state of formation**
4. **Business phone + email**
5. **Member SSNs + addresses** for Nairne and Raj (for K-1s)
6. **1099 recipient SSN/EIN + addresses** for Alec, Jake, AJ, Phil, Issac, Luke, Chris, plus any vendors crossing the $600 threshold (PVD, Ad Spend providers)
7. **Bank/wallet statements** as of 12/31/2025 to populate Balance Sheet Cash line
8. **Initial member capital contributions** — what each member contributed at formation
9. **Confirm cash basis vs accrual basis** for tax reporting — this determines whether to use the Distributions ledger (cash) or the TPA-derived totals (accrual). The two views differ by ~$11,587 across the year.
10. **Foreign financial account question** — verify if any crypto wallets/exchanges used qualify as "foreign financial accounts" for FBAR/Form 8938 purposes
11. **506c SPV structure** — confirm whether the $29,275 in SPV disbursements is a loan (interest-bearing?) or an equity investment, for proper balance sheet classification
12. **Insurance pro-ration** — confirm the $18K Dec Insurance is annual D&O coverage for accountant to book the prepaid asset correctly

---

## Tax Organizer Form Answers

For the Monily Partnership Tax Organizer, here are the answers I can provide:

| Field | Answer |
|---|---|
| Legal name of business | Armada Prime Tech LLC |
| Filing for the year | 2025 |
| EIN | *(need from user)* |
| Phone Number | *(need from user)* |
| Email | *(need from user)* |
| Corporation address / State / City / Zip / Country | *(need from user)* |
| Above address is new | No |
| Is it first year of Filing | **Yes** |
| Partnership state residence | *(need from user — likely state of formation)* |
| EIN letter | Yes (need to upload) |
| Letter of Incorporation | Yes (need to upload) |
| Profit & Loss Statement | **Yes** — see `01_Profit_and_Loss_Statement_2025.xlsx` |
| Balance Sheet | **Partial** — see `02_Balance_Sheet_2025.xlsx` (placeholders flagged) |
| General Ledgers | **Yes** — see `03_General_Ledger_2025.xlsx` |
| Asset Schedule Template | **Yes** (no fixed assets) — see `04_Asset_Schedule_2025.xlsx` |
| Payroll Report and Filings | **N/A** — no W-2 employees |
| Last Filed Tax Year | **No** (first year) |
| Sales Tax Filings | **N/A** |
| Estimated State Tax Payments | **No** *(unless made — confirm)* |
| First time filing with Monily | **Yes** *(assumed)* |
| Number of Share Holders | **2** (Nairne + Raj Duggal) |
| Change of business name during year | No |
| Calendar year filer | **Yes** |
| Foreign account interest/signature authority | *(verify — depends on crypto exchange custody)* |
| Any shareholder a disregarded entity / trust / S-corp | No (members are individuals — confirm) |
| Owns 20%+ of foreign/domestic corp | No |
| Outstanding restricted stock | No |
| Outstanding stock options/warrants | No |
| Distribution of property or transfer of shareholder interest | No (Phil → Alec was 2026, not 2025) |
| Accessibility expenses | No |
| FICA on tips | No (no W-2 employees) |
| Low-income housing rentals | No |
| R&D expenditures | No |

---

## Reproduce This Package

```bash
python tools/build_monily_package.py
```

Source data is pulled from `tools/build_2025_year_end.py` (which pulls from TPA reports + internal Distributions ledger).
