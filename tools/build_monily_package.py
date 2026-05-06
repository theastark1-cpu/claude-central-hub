#!/usr/bin/env python3
"""Build the full Monily Partnership Tax Organizer document package for
Armada Prime Tech LLC, tax year 2025.

Generates the following files in /Users/nairne/claude-central-hub/monily-package/:
  01_Profit_and_Loss_Statement_2025.xlsx
  02_Balance_Sheet_2025.xlsx           (best-effort, flagged for accountant)
  03_General_Ledger_2025.xlsx           (transaction-level cash distributions + expenses)
  04_Asset_Schedule_2025.xlsx           (template — no fixed assets to depreciate)
  05_Cover_Memo_for_Monily.md           (narrative summary + open items)

Pulls source data from build_2025_year_end.py constants (ACTUAL_PAID,
ACTUAL_GROSS, GP_OP_EXPENSES, NAIRNE_ALIASES, K1_RECIPIENTS, etc.).

Usage:
    python tools/build_monily_package.py
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_2025_year_end import (
    ACTUAL_PAID,
    GP_OP_EXPENSES,
    K1_RECIPIENTS,
    NAIRNE_ALIASES,
    PERIOD_LABELS,
    SPLIT_PCTS_2025,
    TPA_FILES,
    INTERNAL_IDS,
    EXTRA_2025_OVERRIDES,
)
from build_consultant_splits import load_ids
from parse_tpa_report import parse_workbook

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "monily-package"
OUT_DIR.mkdir(exist_ok=True)

# Styling
HDR_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
HDR_FONT = Font(bold=True, color="FFFFFF", size=11)
SECTION_FILL = PatternFill(start_color="305496", end_color="305496", fill_type="solid")
SECTION_FONT = Font(bold=True, color="FFFFFF", size=12)
SUBTOTAL_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
TOTAL_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
WARN_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
THIN = Side(border_style="thin", color="999999")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
MONEY = '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'
DATE_FMT = "yyyy-mm-dd"

ENTITY_NAME = "Armada Prime Tech LLC"
TAX_YEAR = "2025"
PERIOD_DESC = "Aug 1, 2025 – Dec 31, 2025"


def set_header(ws, row: int, ncols: int) -> None:
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HDR_FILL
        cell.font = HDR_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BOX


def title_block(ws, doc_title: str, ncols: int = 5) -> int:
    ws.cell(row=1, column=1, value=ENTITY_NAME).font = Font(bold=True, size=16)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    ws.cell(row=2, column=1, value=doc_title).font = Font(bold=True, size=13, color="1F4E79")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    ws.cell(row=3, column=1, value=f"Tax Year {TAX_YEAR}  |  Period: {PERIOD_DESC}  |  Generated {date.today().isoformat()}").font = Font(italic=True, color="666666")
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=ncols)
    return 5


# ---------------------------------------------------------------------------
# 01 — Profit & Loss Statement
# ---------------------------------------------------------------------------

def build_pnl():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "P&L Statement"

    # Aggregate per-recipient totals
    year_totals = {}
    for period, recipients in ACTUAL_PAID.items():
        for k, v in recipients.items():
            year_totals[k] = year_totals.get(k, 0) + v
    op_total = sum(a for items in GP_OP_EXPENSES.values() for _, a in items)

    # Compute revenue = TPA Performance Fees Crystallized for Aug-Dec 2025
    revenue = compute_tpa_perf_fees_total()

    nairne_total = sum(year_totals.get(a, 0) for a in NAIRNE_ALIASES)
    raj_total = year_totals.get("Raj", 0)
    contractor_total = sum(v for k, v in year_totals.items() if k not in K1_RECIPIENTS)

    # Reclass-adjusted op expenses (move SPV loans to balance sheet, prorate insurance)
    spv_reclass = 4275 + 25000  # Aug + Oct
    insurance_prorate = 18000 - 7500  # reduce $18k Dec to $7.5k for 5-month period

    r = title_block(ws, "Profit & Loss Statement", ncols=4)
    headers = ["Line Item", "GAAP-Style ($)", "Tax-Reclass ($)", "Notes"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header(ws, r, len(headers))
    r += 1

    def section(title):
        nonlocal r
        ws.cell(row=r, column=1, value=title)
        for c in range(1, len(headers) + 1):
            ws.cell(row=r, column=c).fill = SECTION_FILL
            ws.cell(row=r, column=c).font = SECTION_FONT
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(headers))
        r += 1

    def line(label, gaap, reclass=None, note="", bold=False, fill=None):
        nonlocal r
        ws.cell(row=r, column=1, value=label)
        if gaap is not None:
            ws.cell(row=r, column=2, value=gaap).number_format = MONEY
        if reclass is not None:
            ws.cell(row=r, column=3, value=reclass).number_format = MONEY
        ws.cell(row=r, column=4, value=note).alignment = Alignment(wrap_text=True)
        if bold:
            for c in range(1, len(headers) + 1):
                ws.cell(row=r, column=c).font = Font(bold=True)
        if fill:
            for c in range(1, len(headers) + 1):
                ws.cell(row=r, column=c).fill = fill
        r += 1

    section("REVENUE")
    line("Performance Fees Income (from Armada Prime LLP)", revenue, revenue,
         "Per TPA Reporting Packages, Performance Fees Crystallized line, Aug-Dec 2025.")
    line("Total Revenue", revenue, revenue, bold=True, fill=SUBTOTAL_FILL)
    r += 1

    section("DIRECT COSTS — Capital Raiser Commissions (1099 contractors)")
    contractors_list = [
        ("Alec Atkinson", year_totals.get("Alec Atkinson", 0)),
        ("Jake Gordon", year_totals.get("Jake Gordon", 0)),
        ("AJ Affleck", year_totals.get("AJ Affleck", 0)),
        ("Issac Morris", year_totals.get("Issac", 0)),
        ("Luke Affleck", year_totals.get("Luke", 0)),
        ("Phil — fixed 0.5% slice", year_totals.get("Phil", 0)),
    ]
    for name, amt in contractors_list:
        line(f"  {name}", amt, amt, "1099-NEC issued separately")
    line("Total Direct Costs", contractor_total, contractor_total, bold=True, fill=SUBTOTAL_FILL)
    r += 1

    # Operating expenses (broken out into line items)
    section("OPERATING EXPENSES")
    op_breakdown = aggregate_op_expenses()
    op_breakdown_total = sum(op_breakdown.values())
    op_reclass_total = op_breakdown_total - spv_reclass - insurance_prorate

    op_lines = [
        ("Chris (Contractor labor — 1099)", op_breakdown.get("Chris", 0), op_breakdown.get("Chris", 0), "Issue 1099-NEC; verify SSN/address"),
        ("Insurance (D&O)", op_breakdown.get("Insurance", 0), 7500, "Reclass: $18k Dec is annual D&O. Pro-rate to ~$7,500 for Aug-Dec period."),
        ("PVD", op_breakdown.get("PVD", 0), op_breakdown.get("PVD", 0), "Vendor identification needed for 1099 obligation"),
        ("Website", op_breakdown.get("Website", 0), op_breakdown.get("Website", 0), "Marketing/web build"),
        ("Ad Spend / Marketing", op_breakdown.get("Ad Spend", 0), op_breakdown.get("Ad Spend", 0), "Marketing"),
        ("Alpha Verification", op_breakdown.get("Alpha Verification", 0), op_breakdown.get("Alpha Verification", 0), "Compliance/verification service"),
        ("TPA Admin Fees (Formidium)", op_breakdown.get("TPA", 0), op_breakdown.get("TPA", 0), "Verify GP-paid vs fund-paid (fund books also have $600/mo)"),
        ("506c SPV Loan", op_breakdown.get("506c SPV Loan", 0), 0, "RECLASS to Balance Sheet: $29,275 is a loan/capital item, not P&L expense."),
    ]
    for label, gaap, reclass, note in op_lines:
        line(f"  {label}", gaap, reclass, note)
    line("Total Operating Expenses", op_breakdown_total, op_reclass_total, bold=True, fill=SUBTOTAL_FILL)
    r += 1

    # Net income
    section("NET INCOME (Partnership)")
    gaap_net = revenue - contractor_total - op_breakdown_total
    reclass_net = revenue - contractor_total - op_reclass_total
    line("Total Revenue", revenue, revenue)
    line("Less: Direct Costs (1099 contractors)", -contractor_total, -contractor_total)
    line("Less: Operating Expenses", -op_breakdown_total, -op_reclass_total)
    line("= NET INCOME", gaap_net, reclass_net, bold=True, fill=TOTAL_FILL,
         note="Tax-reclass column reflects accountant-preferred adjustments (SPV loans → balance sheet, insurance pro-rated).")
    r += 1

    # K-1 allocation
    section("K-1 PARTNER ALLOCATION (per derived ownership: Nairne 99.17% / Raj 0.83%)")
    nairne_pct = 60.0 / 60.5
    raj_pct = 0.5 / 60.5
    line("Nairne — Cash distributions received", nairne_total, nairne_total,
         "Includes Fund Mgmt 59.5% slice + direct 0.5%. Reported on K-1 capital account.")
    line("Nairne — Allocated share of Net Income (99.17%)",
         gaap_net * nairne_pct, reclass_net * nairne_pct,
         "Reported on K-1 Schedule K-1, Box 1 (Ordinary Income).")
    line("Raj Duggal — Cash distributions received", raj_total, raj_total,
         "Reported on K-1 capital account.")
    line("Raj Duggal — Allocated share of Net Income (0.83%)",
         gaap_net * raj_pct, reclass_net * raj_pct,
         "Reported on K-1 Schedule K-1, Box 1.")
    r += 1

    # Notes
    section("PREPARER NOTES")
    notes = [
        "1. Entity formed at the Armada Prime relaunch in August 2025; first year of operations and first year filing.",
        "2. Revenue source: Performance Fees Crystallized line of TPA (Formidium) reporting packages, per the 2026-04-27 internal decision making TPA the authoritative source for GP/consultant compensation.",
        "3. Member structure: Nairne 60% (= Fund Mgmt 59.5% + direct 0.5%) and Raj Duggal 0.5%. The Fund Mgmt 59.5% slice is Nairne's K-1 income, NOT a separate entity 1099 expense.",
        "4. Phil's 0.5% slice is a 1099-NEC contractor payment (Phil is not a member of the LLC).",
        "5. TruQuant payments are NOT included in this entity's books. TruQuant's 18% is taken upstream of Armada Prime LLP from September onwards. The August 'Trader & Developer' $6,909.93 + 'Spydr' $88.78 paid to TruQuant inside the GP entity's operational ledger is excluded per a policy decision (TQ is upstream of GP).",
        "6. Contractor amounts shown above are CASH BASIS (per the internal Distributions Armada Tech 2025 ledger). Difference vs accrual basis (TPA Performance Fees Crystallized) = ~$11,587 across the year, comprising the $6,999 TQ exclusion and cash-vs-accrual timing.",
        "7. RECOMMEND: $29,275 of '506c SPV Loan' line items should be reclassified to the Balance Sheet (loan/capital items, not P&L expenses).",
        "8. RECOMMEND: $18,000 Insurance line in December likely represents an annual D&O policy and should be pro-rated to ~$7,500 for the 5-month period of operations.",
    ]
    for note in notes:
        line(note, None, None)
        ws.row_dimensions[r-1].height = 30

    # Column widths
    ws.column_dimensions["A"].width = 50
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 60

    out = OUT_DIR / "01_Profit_and_Loss_Statement_2025.xlsx"
    wb.save(out)
    print(f"Wrote {out}")
    return revenue, contractor_total, op_breakdown_total, op_reclass_total, nairne_total, raj_total


def aggregate_op_expenses() -> dict:
    """Aggregate op expenses by vendor type across all months."""
    out = {}
    mapping = {
        "506c SPV Loan": "506c SPV Loan",
        "PVD": "PVD",
        "Website": "Website",
        "Ad Spend": "Ad Spend",
        "Chris": "Chris",
        "Alpha Verification": "Alpha Verification",
        "Formidium (TPA)": "TPA",
        "TPA (Formidium)": "TPA",
        "TPA (second line)": "TPA",
        "Insurance": "Insurance",
    }
    for period, items in GP_OP_EXPENSES.items():
        for vendor, amount in items:
            key = mapping.get(vendor, vendor)
            out[key] = out.get(key, 0) + amount
    return out


def compute_tpa_perf_fees_total() -> float:
    # Hard-coded from prior verified output: $153,023.03
    # (Aug $15,355.51 + Sep $12,474.75 + Oct $51,906.99 + Nov $57,074.09 + Dec $16,211.69)
    return 15355.51 + 12474.75 + 51906.99 + 57074.09 + 16211.69


# ---------------------------------------------------------------------------
# 02 — Balance Sheet (best-effort)
# ---------------------------------------------------------------------------

def build_balance_sheet(revenue, contractor_total, op_total_gaap, op_total_reclass, nairne_cash, raj_cash):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Balance Sheet"

    r = title_block(ws, "Balance Sheet (as of Dec 31, 2025)", ncols=4)
    headers = ["Account", "Amount ($)", "Source / Method", "Notes"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header(ws, r, len(headers))
    r += 1

    def section(title):
        nonlocal r
        ws.cell(row=r, column=1, value=title)
        for c in range(1, len(headers) + 1):
            ws.cell(row=r, column=c).fill = SECTION_FILL
            ws.cell(row=r, column=c).font = SECTION_FONT
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(headers))
        r += 1

    def line(label, amount, source="", note="", bold=False, fill=None, warn=False):
        nonlocal r
        ws.cell(row=r, column=1, value=label)
        if amount is not None:
            ws.cell(row=r, column=2, value=amount).number_format = MONEY
        ws.cell(row=r, column=3, value=source)
        ws.cell(row=r, column=4, value=note).alignment = Alignment(wrap_text=True)
        if bold:
            for c in range(1, len(headers) + 1):
                ws.cell(row=r, column=c).font = Font(bold=True)
        if fill:
            for c in range(1, len(headers) + 1):
                ws.cell(row=r, column=c).fill = fill
        if warn:
            for c in range(1, len(headers) + 1):
                ws.cell(row=r, column=c).fill = WARN_FILL
        r += 1

    # Calculate net income (used for retained earnings)
    net_income = revenue - contractor_total - op_total_gaap

    # 506c SPV Loan reclass amount
    spv_loans = 4275 + 25000  # Aug + Oct disbursements

    section("ASSETS")
    line("Cash & Cash Equivalents (Bank + Crypto Wallets)", None,
         "PLACEHOLDER", "⚠️ Need bank statements / wallet balances as of 12/31/2025 to populate", warn=True)
    line("506c SPV Loan Receivable / SPV Investment", spv_loans,
         "Reclassified from P&L", "Aug $4,275 + Oct $25,000 disbursements; classify per accountant (loan receivable vs equity investment)")
    line("Prepaid Insurance", 10500,
         "Reclassified from P&L",
         "$18,000 Dec Insurance less $7,500 pro-rated to 2025 = $10,500 prepaid for 2026")
    line("Other Receivables / Accruals", None,
         "PLACEHOLDER", "⚠️ Any TPA accruals (e.g., Dec perf fees not yet received in cash)?", warn=True)
    line("Total Assets", spv_loans + 10500, bold=True, fill=SUBTOTAL_FILL,
         note="Excludes cash and other unspecified assets — placeholders flagged above")
    r += 1

    section("LIABILITIES")
    line("Accounts Payable", None, "PLACEHOLDER",
         "⚠️ Any unpaid contractor amounts as of 12/31? Distributions Ledger shows ~$11,588 cumulative cash-vs-accrual delta", warn=True)
    line("Accrued Expenses", None, "PLACEHOLDER", "⚠️ Any Q4 op expenses incurred but not yet paid?", warn=True)
    line("Total Liabilities", 0, bold=True, fill=SUBTOTAL_FILL,
         note="Excludes placeholders flagged above")
    r += 1

    section("MEMBERS' EQUITY")
    line("Member Capital — Nairne (60% ownership)", None,
         "PLACEHOLDER", "⚠️ Initial capital contributions in 2025? Asked separately by Monily", warn=True)
    line("Member Capital — Raj Duggal (0.5% ownership)", None,
         "PLACEHOLDER", "⚠️ Initial capital contributions in 2025?", warn=True)
    line("Cumulative Distributions — Nairne", -nairne_cash,
         "Cash distributions made in 2025", f"Includes Fund Mgmt 59.5% (${nairne_cash - 946.97:,.2f}) + direct 0.5% ($946.97)")
    line("Cumulative Distributions — Raj Duggal", -raj_cash,
         "Cash distributions made in 2025", "")
    line("Retained Earnings (Net Income for the year)", net_income,
         "From P&L Statement", f"GAAP-basis: ${net_income:,.2f}. Reclass-adjusted: ${revenue - contractor_total - op_total_reclass:,.2f}")
    line("Total Members' Equity", net_income - nairne_cash - raj_cash, bold=True, fill=SUBTOTAL_FILL,
         note="Excludes member capital contributions (placeholders)")
    r += 1

    # Reconciliation
    section("BALANCING NOTE")
    line("Total Assets", spv_loans + 10500)
    line("= Total Liabilities + Members' Equity", 0 + (net_income - nairne_cash - raj_cash),
         note="When member capital + cash + payables are filled in, this should balance to total assets.")
    line("Imbalance (placeholder gap)", (spv_loans + 10500) - (net_income - nairne_cash - raj_cash),
         note="Reflects the missing cash and member capital contribution data — accountant will fill in.", fill=WARN_FILL)
    r += 1

    section("METHODOLOGY")
    method_notes = [
        "1. This is a BEST-EFFORT balance sheet built from available transactional data (Distributions ledger + TPA reporting). Several lines marked PLACEHOLDER need to be populated by the accountant from bank statements, wallet balances, and member capital records.",
        "2. The 506c SPV Loan items ($4,275 Aug + $25,000 Oct = $29,275 total) were originally tracked as P&L 'Costs' but are reclassified here to the asset side per standard practice for loan disbursements / SPV setup costs.",
        "3. The $18,000 December Insurance line is split: $7,500 pro-rated to 2025 P&L (5-month period of operations) and $10,500 booked as Prepaid Insurance asset (2026 coverage).",
        "4. Cumulative Distributions are shown as negative equity (reduce capital accounts). Member capital contributions need to be added to balance the sheet.",
        "5. The $11,588 cash-vs-accrual delta on the Distributions ledger may need to flow through Accounts Payable (if cash basis) or be irrelevant (if accrual basis). Confirm with accountant.",
    ]
    for note in method_notes:
        ws.cell(row=r, column=1, value=note).alignment = Alignment(wrap_text=True)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(headers))
        ws.row_dimensions[r].height = 35
        r += 1

    ws.column_dimensions["A"].width = 50
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 28
    ws.column_dimensions["D"].width = 60

    out = OUT_DIR / "02_Balance_Sheet_2025.xlsx"
    wb.save(out)
    print(f"Wrote {out}")


# ---------------------------------------------------------------------------
# 03 — General Ledger (transaction-level)
# ---------------------------------------------------------------------------

def build_general_ledger():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "General Ledger 2025"

    r = title_block(ws, "General Ledger — Cash Transactions", ncols=7)
    headers = ["Date", "Type", "Account", "Counterparty", "Description", "Debit ($)", "Credit ($)"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header(ws, r, len(headers))
    r += 1

    # Build transactions: each month, revenue receipt + per-recipient distributions + op expense payments
    perf_fees = {
        "2025-08": 15355.51,
        "2025-09": 12474.75,
        "2025-10": 51906.99,
        "2025-11": 57074.09,
        "2025-12": 16211.69,
    }

    end_of_month = {
        "2025-08": "2025-08-31",
        "2025-09": "2025-09-30",
        "2025-10": "2025-10-31",
        "2025-11": "2025-11-30",
        "2025-12": "2025-12-31",
    }

    txn_count = 0
    total_debit = 0.0
    total_credit = 0.0

    for period in ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12"]:
        eom = end_of_month[period]
        # Revenue receipt
        amt = perf_fees[period]
        write_txn(ws, r, eom, "Revenue", "Performance Fees Income", "Armada Prime LLP (TPA)",
                  f"{PERIOD_LABELS[period]} GP cut received from fund", debit=amt, credit=None)
        r += 1
        txn_count += 1
        total_debit += amt

        # Distributions to people (each as a debit to expense or equity-distribution, credit to cash)
        for recipient, payout in ACTUAL_PAID.get(period, {}).items():
            if payout == 0:
                continue
            if recipient == "Fund Mgmt":
                acct = "K-1 Distribution to Member"
                desc = f"Distribution to Nairne (Fund Mgmt 59.5% slice, K-1 partner)"
                cp = "Nairne"
            elif recipient == "Nairne":
                acct = "K-1 Distribution to Member"
                desc = f"Distribution to Nairne (direct 0.5% slice, K-1 partner)"
                cp = "Nairne"
            elif recipient == "Raj":
                acct = "K-1 Distribution to Member"
                desc = f"Distribution to Raj Duggal (direct 0.5% slice, K-1 partner)"
                cp = "Raj Duggal"
            elif recipient == "Phil":
                acct = "Capital Raiser Commission Expense (1099)"
                desc = f"1099-NEC payment to Phil (0.5% direct slice)"
                cp = "Phil"
            else:
                acct = "Capital Raiser Commission Expense (1099)"
                desc = f"1099-NEC payment to {recipient}"
                cp = recipient
            # For expense/distribution: credit cash (money out). Negative payouts
            # (clawbacks) are debits to cash (money returned to GP).
            if payout >= 0:
                debit_val = None
                credit_val = payout
                total_credit += payout
            else:
                debit_val = -payout
                credit_val = None
                total_debit += -payout
            write_txn(ws, r, eom, "Distribution" if recipient in K1_RECIPIENTS else "Expense",
                      acct, cp, desc, debit=debit_val, credit=credit_val)
            r += 1
            txn_count += 1

        # Op expenses
        for vendor, amount in GP_OP_EXPENSES.get(period, []):
            acct = categorize_account(vendor)
            write_txn(ws, r, eom, "Expense", acct, vendor,
                      f"GP-paid expense: {vendor}", debit=None, credit=amount)
            r += 1
            txn_count += 1
            total_credit += amount

    # Summary
    r += 1
    ws.cell(row=r, column=1, value=f"TOTAL TRANSACTIONS: {txn_count}").font = Font(bold=True)
    r += 1
    ws.cell(row=r, column=1, value="TOTAL DEBITS").font = Font(bold=True)
    ws.cell(row=r, column=6, value=total_debit).number_format = MONEY
    ws.cell(row=r, column=6).font = Font(bold=True)
    r += 1
    ws.cell(row=r, column=1, value="TOTAL CREDITS").font = Font(bold=True)
    ws.cell(row=r, column=7, value=total_credit).number_format = MONEY
    ws.cell(row=r, column=7).font = Font(bold=True)
    r += 1
    ws.cell(row=r, column=1, value=f"NET (Debit − Credit) = Net Income proxy: ${total_debit - total_credit:,.2f}").font = Font(italic=True, bold=True)

    # Notes
    r += 2
    ws.cell(row=r, column=1, value="NOTES").font = Font(bold=True, color="C00000")
    r += 1
    notes = [
        "Each row represents a single cash transaction. Revenue receipts are debits to Cash; distributions and expense payments are credits to Cash.",
        "Account classification: K-1 Distribution to Member (Nairne, Raj — partners) vs Capital Raiser Commission Expense (Alec, Jake, AJ, Phil, Issac, Luke — 1099 contractors) vs operating expense buckets (Insurance, Marketing, etc.).",
        "Dates are end-of-month (month of accrual). Actual cash settlement dates may have been a few days/weeks later — adjust if cash basis with strict timing.",
        "Source: Distributions Armada Tech 2025 (INTERNAL ONLY) ledger + BEST ONE December 2025 Monthly Return Costs sheet.",
        "TruQuant payments excluded entirely (per Nairne 2026-04-30 — TQ is upstream of GP entity).",
        "Issac's December −$278.48 entry is a clawback against prior month overpayment.",
    ]
    for note in notes:
        ws.cell(row=r, column=1, value=note).alignment = Alignment(wrap_text=True)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(headers))
        ws.row_dimensions[r].height = 30
        r += 1

    # Column widths
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 13
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 22
    ws.column_dimensions["E"].width = 50
    ws.column_dimensions["F"].width = 14
    ws.column_dimensions["G"].width = 14

    out = OUT_DIR / "03_General_Ledger_2025.xlsx"
    wb.save(out)
    print(f"Wrote {out}")


def write_txn(ws, row, dt, ttype, account, counterparty, desc, debit=None, credit=None):
    ws.cell(row=row, column=1, value=dt).number_format = DATE_FMT
    ws.cell(row=row, column=2, value=ttype)
    ws.cell(row=row, column=3, value=account)
    ws.cell(row=row, column=4, value=counterparty)
    ws.cell(row=row, column=5, value=desc)
    if debit is not None:
        ws.cell(row=row, column=6, value=debit).number_format = MONEY
    if credit is not None:
        ws.cell(row=row, column=7, value=credit).number_format = MONEY


def categorize_account(vendor: str) -> str:
    v = vendor.lower()
    if "insurance" in v: return "Insurance Expense"
    if "spv" in v or "loan" in v: return "506c SPV Loan (RECLASS to Asset)"
    if "tpa" in v or "formidium" in v: return "Professional Fees — TPA Admin"
    if "chris" in v: return "Contractor Labor — Chris"
    if "pvd" in v: return "Professional Fees — PVD"
    if "website" in v: return "Marketing — Website"
    if "ad spend" in v or "ads" in v or "badtwin" in v: return "Marketing — Advertising"
    if "alpha" in v: return "Compliance — Verification"
    return "Other Operating Expense"


# ---------------------------------------------------------------------------
# 04 — Asset Schedule (template / minimal)
# ---------------------------------------------------------------------------

def build_asset_schedule():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Asset Schedule"

    r = title_block(ws, "Asset Schedule (Fixed Assets / Depreciation)", ncols=8)
    headers = ["Asset Description", "Acquisition Date", "Cost", "Useful Life", "Depreciation Method", "Prior Accum Depr", "2025 Depr Expense", "Net Book Value"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header(ws, r, len(headers))
    r += 1

    # No fixed assets known for this entity — first year, services-only LLC
    ws.cell(row=r, column=1, value="(No fixed assets recorded for 2025)").font = Font(italic=True, color="999999")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(headers))
    r += 2

    # Other tracked items
    ws.cell(row=r, column=1, value="OTHER ITEMS THAT MAY BELONG ON SCHEDULE").font = Font(bold=True, color="C00000")
    r += 1
    other_items = [
        ("506c SPV Loan disbursement (Aug)", "2025-08-31", 4275.00, "—", "Loan/Investment (NOT depreciable)", 0, 0, 4275.00),
        ("506c SPV Loan disbursement (Oct)", "2025-10-31", 25000.00, "—", "Loan/Investment (NOT depreciable)", 0, 0, 25000.00),
    ]
    for desc, dt, cost, life, method, prior_dep, this_dep, nbv in other_items:
        ws.cell(row=r, column=1, value=desc)
        ws.cell(row=r, column=2, value=dt)
        ws.cell(row=r, column=3, value=cost).number_format = MONEY
        ws.cell(row=r, column=4, value=life)
        ws.cell(row=r, column=5, value=method)
        ws.cell(row=r, column=6, value=prior_dep).number_format = MONEY
        ws.cell(row=r, column=7, value=this_dep).number_format = MONEY
        ws.cell(row=r, column=8, value=nbv).number_format = MONEY
        r += 1

    r += 2
    ws.cell(row=r, column=1, value="NOTES").font = Font(bold=True)
    r += 1
    notes = [
        "Armada Prime Tech LLC has no fixed assets / depreciable property recorded for 2025. The entity is a services-only LLC (capital management) that uses no PP&E.",
        "The 506c SPV Loan disbursements ($4,275 Aug + $25,000 Oct = $29,275) shown above are NOT depreciable. They are loan receivables or equity investments (depending on the SPV structure) and belong on the Balance Sheet as assets, not on this depreciation schedule.",
        "If equipment, software, or other capital assets were purchased in 2025 that aren't reflected here, please add them and re-classify accordingly.",
    ]
    for note in notes:
        ws.cell(row=r, column=1, value=note).alignment = Alignment(wrap_text=True)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(headers))
        ws.row_dimensions[r].height = 30
        r += 1

    for i, w in enumerate([35, 14, 14, 14, 28, 16, 16, 16], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    out = OUT_DIR / "04_Asset_Schedule_2025.xlsx"
    wb.save(out)
    print(f"Wrote {out}")


# ---------------------------------------------------------------------------
# 05 — Cover Memo
# ---------------------------------------------------------------------------

def build_cover_memo(revenue, contractor_total, op_gaap, op_reclass, nairne_cash, raj_cash):
    net_gaap = revenue - contractor_total - op_gaap
    net_reclass = revenue - contractor_total - op_reclass

    md = f"""# Monily Tax Organizer — Document Package
## Armada Prime Tech LLC — Tax Year 2025

**Prepared:** {date.today().isoformat()}
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
| **Revenue** (Performance Fees from Armada Prime LLP) | ${revenue:,.2f} | ${revenue:,.2f} |
| Direct Costs (1099 contractor commissions) | (${contractor_total:,.2f}) | (${contractor_total:,.2f}) |
| Operating Expenses | (${op_gaap:,.2f}) | (${op_reclass:,.2f}) |
| **Net Income (Partnership)** | **${net_gaap:,.2f}** | **${net_reclass:,.2f}** |

The GAAP→reclass swing is the **$29,275 in 506c SPV Loans** (move to balance sheet as loan receivable / equity investment) and **$10,500 in Insurance proration** (Dec $18K is annual D&O — only 5/12 should hit 2025 P&L, the rest is prepaid).

---

## Member Structure & K-1 Allocation

| Member | Ownership % | Cash Distributions Received | K-1 Allocated Net Income (Reclass-Basis) |
|---|---:|---:|---:|
| **Nairne** | 99.17% (60/60.5) | ${nairne_cash:,.2f} | ${net_reclass * 60.0/60.5:,.2f} |
| **Raj Duggal** | 0.83% (0.5/60.5) | ${raj_cash:,.2f} | ${net_reclass * 0.5/60.5:,.2f} |

Nairne's 60% = Fund Management 59.5% slice + direct 0.5%. The Fund Management slice is K-1 income to Nairne (NOT a separate entity expense / 1099). Raj's 0.5% direct slice is also K-1 income.

---

## 1099-NEC Recipients (Aug–Dec 2025 totals)

The following individuals/entities received contractor payments and need 1099-NECs:

| Recipient | 2025 Total |
|---|---:|
| Alec Atkinson | ${sum(ACTUAL_PAID[p].get('Alec Atkinson', 0) for p in ACTUAL_PAID):,.2f} |
| Jake Gordon | ${sum(ACTUAL_PAID[p].get('Jake Gordon', 0) for p in ACTUAL_PAID):,.2f} |
| AJ Affleck | ${sum(ACTUAL_PAID[p].get('AJ Affleck', 0) for p in ACTUAL_PAID):,.2f} |
| Phil (last name TBD) | ${sum(ACTUAL_PAID[p].get('Phil', 0) for p in ACTUAL_PAID):,.2f} |
| Issac Morris | ${sum(ACTUAL_PAID[p].get('Issac', 0) for p in ACTUAL_PAID):,.2f} |
| Luke Affleck | ${sum(ACTUAL_PAID[p].get('Luke', 0) for p in ACTUAL_PAID):,.2f} |
| Chris (operating contractor) | $11,500.00 |
| **Total 1099 Payments** | **${contractor_total + 11500:,.2f}** |

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
"""
    out = OUT_DIR / "05_Cover_Memo_for_Monily.md"
    out.write_text(md)
    print(f"Wrote {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    revenue, contractor_total, op_gaap, op_reclass, nairne_cash, raj_cash = build_pnl()
    build_balance_sheet(revenue, contractor_total, op_gaap, op_reclass, nairne_cash, raj_cash)
    build_general_ledger()
    build_asset_schedule()
    build_cover_memo(revenue, contractor_total, op_gaap, op_reclass, nairne_cash, raj_cash)
    print(f"\nDone. Package files in {OUT_DIR}/")
