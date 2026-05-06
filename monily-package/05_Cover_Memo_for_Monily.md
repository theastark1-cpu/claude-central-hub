# Monily Tax Organizer — Cover Memo
## Armada Prime Tech LLC — Tax Year 2025

**Prepared:** 2026-05-05
**Period of operations:** Aug 1, 2025 – Dec 31, 2025 (entity formed at Armada Prime LLP relaunch)
**Filing status:** First year of filing
**Tax classification:** Multi-member LLC, partnership for tax purposes

---

## What's in this package

| File | Purpose |
|---|---|
| `Monily_Tax_Package_2025.xlsx` | **Single combined workbook** with 8 tabs (Cover & Summary, P&L, Balance Sheet, GL, Asset Schedule, K-1 Partners, 1099 Recipients, Tax Organizer Answers) |
| `05_Cover_Memo_for_Monily.md` / `.docx` | This narrative cover memo |
| `06_Bonus_Detailed_Workbook.xlsx` | Standalone 15-tab reconciliation backup |

---

## Headline Numbers (2025)

| Line | GAAP-Basis | After Tax-Reclass |
|---|---:|---:|
| **Revenue** (Performance Fees from Armada Prime LLP) | $153,023.03 | $153,023.03 |
| Direct Costs (1099 contractor commissions) | ($86,754.81) | ($86,754.81) |
| Operating Expenses | ($91,225.00) | ($51,450.00) |
| **Net Income (Partnership)** | **$-24,956.78** | **$14,818.22** |

The GAAP→reclass swing is **$29,275 in 506c SPV Loans** (move to balance sheet) and **$10,500 in Insurance proration** (Dec $18K is annual D&O — only 5/12 hits 2025).

---

## Member Structure & K-1 Allocation (3 Partners)

Per Nairne 2026-05-05 — **Phil corrected to K-1 partner** (was previously thought to be a 1099 contractor).

| Member | Ownership % | Cash Distributions Received | K-1 Allocated Net Income (Reclass-Basis) |
|---|---:|---:|---:|
| **Nairne** | 98.36% (60/61) | $34,188.88 | $14,575.30 |
| **Raj Duggal** | 0.82% (0.5/61) | $946.97 | $121.46 |
| **Phil** | 0.82% (0.5/61) | $946.97 | $121.46 |

Nairne's 60% = Fund Management 59.5% slice + direct 0.5%. The Fund Management slice is K-1 income to Nairne (NOT a separate entity expense / 1099).

---

## 1099-NEC Recipients (Aug–Dec 2025 totals)

| Recipient | 2025 Total |
|---|---:|
| Alec Atkinson | $38,076.87 |
| Jake Gordon | $10,388.66 |
| AJ Affleck | $37,139.89 |
| Issac Morris | $761.49 |
| Luke Affleck | $164.90 |
| Nikki | $223.00 |
| Chris (operating contractor) | $11,500.00 |
| **Total 1099 Payments** | **$98,254.81** |

**Phil is NOT on the 1099 list** — Phil is a K-1 partner. See K-1 Partners tab.

---

## Operating Expenses Summary

| Category | GAAP Amount | Reclass-Adjusted | Reclass Reason |
|---|---:|---:|---|
| Insurance | $18,000.00 | $7,500.00 | Annual D&O policy → pro-rate to 5/12 of year |
| Chris (contractor labor) | $11,500.00 | $11,500.00 | — |
| PVD | $12,000.00 | $12,000.00 | — *(verify vendor for 1099)* |
| Website | $7,500.00 | $7,500.00 | — |
| Ad Spend / Marketing | $5,000.00 | $5,000.00 | — |
| Alpha Verification | $2,250.00 | $2,250.00 | — |
| TPA Admin Fees | $5,700.00 | $5,700.00 | — *(may overlap fund-level admin)* |
| 506c SPV Loan | $29,275.00 | $0.00 | **MOVE TO BALANCE SHEET (loan/capital)** |
| **Total** | **$91,225.00** | **$51,450.00** | |

---

## Methodology

### Revenue Recognition
- Source: TPA (Formidium) Reporting Packages, "Performance Fees Crystallized" line, monthly Aug–Dec 2025
- TruQuant's 18% upstream cut and the August "Trader & Developer" / "Spydr" amounts are EXCLUDED — they belong upstream of this entity per a 2026-04-30 policy decision

### Distribution Tracking
- Source: Internal "Distributions Armada Tech 2025 (INTERNAL ONLY)" ledger
- All payments are CASH BASIS — what was actually disbursed each month
- Per-recipient amounts are NET (already after weighted costs / Coinbase fees)

### Member Structure (Updated 2026-05-05)
- **Nairne**: 60% ownership (= Fund Mgmt 59.5% + direct 0.5%) — K-1 partner
- **Raj Duggal**: 0.5% ownership — K-1 partner
- **Phil**: 0.5% ownership — K-1 partner *(corrected from prior 1099 status)*
- Phil held the 0.5% slice all of 2025; Alec replaced him in April 2026

---

## Open Items the Accountant Will Need

1. **EIN** — from IRS letter (CP-575 / 147C)
2. **Formation documents** — Articles of Organization for the LLC
3. **Registered address + state of formation**
4. **Business phone + email**
5. **Member SSNs + addresses** for Nairne, Raj, AND Phil (3 K-1s)
6. **1099 recipient SSN/EIN + addresses** for Alec, Jake, AJ, Issac, Luke, Chris, plus PVD/Ad Spend/Website vendors crossing $600
7. **Bank/wallet statements** as of 12/31/2025 to populate Balance Sheet Cash line
8. **Initial member capital contributions** for all 3 members at formation
9. **Confirm cash basis vs accrual basis** for tax reporting
10. **Foreign financial account question** — verify crypto wallets/exchanges
11. **506c SPV structure** — confirm whether the $29,275 is loan or equity investment
12. **Insurance pro-ration** — confirm $18K Dec is annual D&O

---

## Reproduce This Package

```bash
python tools/build_monily_package.py
python tools/md_to_docx.py     # to regenerate the .docx
```
