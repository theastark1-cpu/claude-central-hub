#!/usr/bin/env python3
"""Build the consolidated Monily Partnership Tax Organizer document for
Armada Prime Tech LLC, tax year 2025.

Produces ONE combined xlsx with all financial schedules as tabs:
  /Users/nairne/claude-central-hub/monily-package/Monily_Tax_Package_2025.xlsx
    Tabs:
      1. Cover & Summary
      2. P&L Statement
      3. Balance Sheet
      4. General Ledger
      5. Asset Schedule
      6. K-1 Partners
      7. 1099 Recipients
      8. Tax Organizer Answers

Plus the narrative cover memo files:
  05_Cover_Memo_for_Monily.md
  05_Cover_Memo_for_Monily.docx (built separately by md_to_docx.py)

Per Nairne 2026-05-05: Phil is a K-1 partner (was previously thought to
be a 1099 contractor — corrected here).

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
)

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "monily-package"
OUT_DIR.mkdir(exist_ok=True)
OUT_XLSX = OUT_DIR / "Monily_Tax_Package_2025.xlsx"
OUT_MD = OUT_DIR / "05_Cover_Memo_for_Monily.md"

# Styling
HDR_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
HDR_FONT = Font(bold=True, color="FFFFFF", size=11)
SECTION_FILL = PatternFill(start_color="305496", end_color="305496", fill_type="solid")
SECTION_FONT = Font(bold=True, color="FFFFFF", size=12)
SUBTOTAL_FILL = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
TOTAL_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
WARN_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
K1_FILL = PatternFill(start_color="E8F4FD", end_color="E8F4FD", fill_type="solid")
THIN = Side(border_style="thin", color="999999")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
MONEY = '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'
DATE_FMT = "yyyy-mm-dd"

ENTITY_NAME = "Armada Prime Tech LLC"
TAX_YEAR = "2025"
PERIOD_DESC = "Aug 1, 2025 – Dec 31, 2025"


# ---------------------------------------------------------------------------
# Year-totals computation (centralized so all tabs use the same numbers)
# ---------------------------------------------------------------------------

def compute_year_totals():
    year_totals = {}
    for period, recipients in ACTUAL_PAID.items():
        for k, v in recipients.items():
            year_totals[k] = year_totals.get(k, 0) + v

    revenue = sum([15355.51, 12474.75, 51906.99, 57074.09, 16211.69])
    nairne_total = sum(year_totals.get(a, 0) for a in NAIRNE_ALIASES)
    raj_total = year_totals.get("Raj", 0)
    phil_total = year_totals.get("Phil", 0)
    contractor_total = sum(v for k, v in year_totals.items() if k not in K1_RECIPIENTS)

    op_expenses = aggregate_op_expenses()
    op_total_gaap = sum(op_expenses.values())
    spv_reclass = 4275 + 25000  # Aug + Oct
    insurance_prorate = 18000 - 7500
    op_total_reclass = op_total_gaap - spv_reclass - insurance_prorate

    net_gaap = revenue - contractor_total - op_total_gaap
    net_reclass = revenue - contractor_total - op_total_reclass

    # Ownership %
    nairne_pct = 60.0 / 61.0
    raj_pct = 0.5 / 61.0
    phil_pct = 0.5 / 61.0

    return {
        "year_totals": year_totals,
        "revenue": revenue,
        "nairne_cash": nairne_total,
        "raj_cash": raj_total,
        "phil_cash": phil_total,
        "contractor_total": contractor_total,
        "op_expenses": op_expenses,
        "op_total_gaap": op_total_gaap,
        "op_total_reclass": op_total_reclass,
        "spv_reclass": spv_reclass,
        "insurance_prorate": insurance_prorate,
        "net_gaap": net_gaap,
        "net_reclass": net_reclass,
        "nairne_pct": nairne_pct,
        "raj_pct": raj_pct,
        "phil_pct": phil_pct,
    }


def aggregate_op_expenses() -> dict:
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
# Tab helpers
# ---------------------------------------------------------------------------

def title_block(ws, doc_title: str, ncols: int = 5) -> int:
    ws.cell(row=1, column=1, value=ENTITY_NAME).font = Font(bold=True, size=16)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    ws.cell(row=2, column=1, value=doc_title).font = Font(bold=True, size=13, color="1F4E79")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    ws.cell(row=3, column=1, value=f"Tax Year {TAX_YEAR}  |  Period: {PERIOD_DESC}  |  Generated {date.today().isoformat()}").font = Font(italic=True, color="666666")
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=ncols)
    return 5


def set_header_row(ws, row: int, ncols: int):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HDR_FILL
        cell.font = HDR_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BOX


def write_section(ws, row: int, title: str, ncols: int) -> int:
    ws.cell(row=row, column=1, value=title)
    for c in range(1, ncols + 1):
        ws.cell(row=row, column=c).fill = SECTION_FILL
        ws.cell(row=row, column=c).font = SECTION_FONT
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    return row + 1


# ---------------------------------------------------------------------------
# Tab 1: Cover & Summary
# ---------------------------------------------------------------------------

def build_cover_tab(wb, T):
    ws = wb.create_sheet("1. Cover & Summary")

    r = title_block(ws, "Tax Package — Cover & Summary", ncols=4)

    # Filing summary
    info_rows = [
        ("Entity Name", ENTITY_NAME),
        ("Filing for Tax Year", TAX_YEAR),
        ("Period of Operations", PERIOD_DESC),
        ("Filing Status", "First year of filing (entity formed at Armada Prime relaunch)"),
        ("Tax Classification", "Multi-member LLC, taxed as partnership"),
        ("Number of Partners", "3 (Nairne, Raj Duggal, Phil)"),
        ("Calendar Year Filer", "Yes"),
    ]
    for label, value in info_rows:
        ws.cell(row=r, column=1, value=label).font = Font(bold=True)
        ws.cell(row=r, column=2, value=value)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
        r += 1
    r += 1

    r = write_section(ws, r, "HEADLINE NUMBERS", ncols=4)
    headers = ["Line Item", "GAAP-Basis ($)", "Tax-Reclass ($)", "Notes"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header_row(ws, r, 4)
    r += 1
    rows = [
        ("Revenue (Performance Fees from Armada Prime LLP)", T["revenue"], T["revenue"], "TPA-authoritative; Aug-Dec 2025"),
        ("Less: 1099 Contractor Expenses (Alec, Jake, AJ, Issac, Luke)", -T["contractor_total"], -T["contractor_total"], "Phil moved to K-1 per Nairne 2026-05-05"),
        ("Less: Operating Expenses", -T["op_total_gaap"], -T["op_total_reclass"], "Reclass moves $29,275 SPV loans to balance sheet, pro-rates Insurance"),
        ("PARTNERSHIP NET INCOME", T["net_gaap"], T["net_reclass"], "Allocated to K-1 partners"),
    ]
    for label, gaap, reclass, note in rows:
        ws.cell(row=r, column=1, value=label)
        ws.cell(row=r, column=2, value=gaap).number_format = MONEY
        ws.cell(row=r, column=3, value=reclass).number_format = MONEY
        ws.cell(row=r, column=4, value=note).alignment = Alignment(wrap_text=True)
        if "NET INCOME" in label:
            for c in range(1, 5):
                ws.cell(row=r, column=c).fill = TOTAL_FILL
                ws.cell(row=r, column=c).font = Font(bold=True)
        r += 1
    r += 1

    r = write_section(ws, r, "K-1 PARTNERS (3 partners)", ncols=4)
    headers = ["Partner", "Ownership %", "Cash Distributions ($)", "Allocated K-1 Income (Reclass-Basis, $)"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header_row(ws, r, 4)
    r += 1
    k1_rows = [
        ("Nairne (Fund Mgmt 59.5% + direct 0.5%)", T["nairne_pct"], T["nairne_cash"], T["net_reclass"] * T["nairne_pct"]),
        ("Raj Duggal (direct 0.5%)", T["raj_pct"], T["raj_cash"], T["net_reclass"] * T["raj_pct"]),
        ("Phil (direct 0.5%)", T["phil_pct"], T["phil_cash"], T["net_reclass"] * T["phil_pct"]),
    ]
    for partner, pct, cash, allocated in k1_rows:
        ws.cell(row=r, column=1, value=partner)
        ws.cell(row=r, column=2, value=f"{pct*100:.2f}%")
        ws.cell(row=r, column=3, value=cash).number_format = MONEY
        ws.cell(row=r, column=4, value=allocated).number_format = MONEY
        for c in range(1, 5):
            ws.cell(row=r, column=c).fill = K1_FILL
        r += 1
    r += 1

    r = write_section(ws, r, "TAB GUIDE", ncols=4)
    tab_guide = [
        ("1. Cover & Summary", "This tab — entity info, headline numbers, K-1 partner allocations, file overview"),
        ("2. P&L Statement", "Full Profit & Loss with GAAP and Tax-Reclass columns, line-by-line detail"),
        ("3. Balance Sheet", "As of Dec 31, 2025. Best-effort with placeholders flagged for accountant"),
        ("4. General Ledger", "Transaction-level ledger of all cash movements (revenue, distributions, expenses)"),
        ("5. Asset Schedule", "Fixed asset / depreciation schedule. No fixed assets recorded."),
        ("6. K-1 Partners", "Detailed partner schedule for K-1 prep (Nairne, Raj, Phil)"),
        ("7. 1099 Recipients", "Detailed contractor schedule for 1099-NEC prep"),
        ("8. Tax Organizer Answers", "Pre-filled answers for the Monily Partnership Tax Organizer form"),
    ]
    for tab_name, desc in tab_guide:
        ws.cell(row=r, column=1, value=tab_name).font = Font(bold=True)
        ws.cell(row=r, column=2, value=desc)
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
        ws.cell(row=r, column=2).alignment = Alignment(wrap_text=True)
        r += 1

    ws.column_dimensions["A"].width = 45
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 22
    ws.column_dimensions["D"].width = 50


# ---------------------------------------------------------------------------
# Tab 2: P&L Statement
# ---------------------------------------------------------------------------

def build_pnl_tab(wb, T):
    ws = wb.create_sheet("2. P&L Statement")
    r = title_block(ws, "Profit & Loss Statement", ncols=4)
    headers = ["Line Item", "GAAP-Style ($)", "Tax-Reclass ($)", "Notes"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header_row(ws, r, 4)
    r += 1

    def line(label, gaap=None, reclass=None, note="", bold=False, fill=None):
        nonlocal r
        ws.cell(row=r, column=1, value=label)
        if gaap is not None:
            ws.cell(row=r, column=2, value=gaap).number_format = MONEY
        if reclass is not None:
            ws.cell(row=r, column=3, value=reclass).number_format = MONEY
        ws.cell(row=r, column=4, value=note).alignment = Alignment(wrap_text=True)
        if bold:
            for c in range(1, 5):
                ws.cell(row=r, column=c).font = Font(bold=True)
        if fill:
            for c in range(1, 5):
                ws.cell(row=r, column=c).fill = fill
        r += 1

    r = write_section(ws, r, "REVENUE", 4)
    line("Performance Fees Income (from Armada Prime LLP)", T["revenue"], T["revenue"],
         "Per TPA Reporting Packages, Performance Fees Crystallized line, Aug-Dec 2025.")
    line("Total Revenue", T["revenue"], T["revenue"], bold=True, fill=SUBTOTAL_FILL)
    r += 1

    r = write_section(ws, r, "DIRECT COSTS — Capital Raiser Commissions (1099 contractors)", 4)
    yt = T["year_totals"]
    contractors = [
        ("Alec Atkinson", yt.get("Alec Atkinson", 0)),
        ("Jake Gordon", yt.get("Jake Gordon", 0)),
        ("AJ Affleck", yt.get("AJ Affleck", 0)),
        ("Issac Morris", yt.get("Issac", 0)),
        ("Luke Affleck", yt.get("Luke", 0)),
    ]
    for name, amt in contractors:
        line(f"  {name}", amt, amt, "1099-NEC issued separately")
    line("Total Direct Costs", T["contractor_total"], T["contractor_total"], bold=True, fill=SUBTOTAL_FILL)
    r += 1

    r = write_section(ws, r, "OPERATING EXPENSES", 4)
    op = T["op_expenses"]
    op_lines = [
        ("Chris (Contractor labor — 1099)", op.get("Chris", 0), op.get("Chris", 0), "Issue 1099-NEC; verify SSN/address"),
        ("Insurance (D&O)", op.get("Insurance", 0), 7500, "Reclass: $18k Dec is annual D&O. Pro-rate to ~$7,500 for Aug-Dec period."),
        ("PVD", op.get("PVD", 0), op.get("PVD", 0), "Vendor identification needed for 1099 obligation"),
        ("Website", op.get("Website", 0), op.get("Website", 0), "Marketing/web build"),
        ("Ad Spend / Marketing", op.get("Ad Spend", 0), op.get("Ad Spend", 0), "Marketing"),
        ("Alpha Verification", op.get("Alpha Verification", 0), op.get("Alpha Verification", 0), "Compliance/verification service"),
        ("TPA Admin Fees (Formidium)", op.get("TPA", 0), op.get("TPA", 0), "Verify GP-paid vs fund-paid (fund books also have $600/mo)"),
        ("506c SPV Loan", op.get("506c SPV Loan", 0), 0, "RECLASS to Balance Sheet: $29,275 is a loan/capital item, not P&L expense."),
    ]
    for label, gaap, reclass, note in op_lines:
        line(f"  {label}", gaap, reclass, note)
    line("Total Operating Expenses", T["op_total_gaap"], T["op_total_reclass"], bold=True, fill=SUBTOTAL_FILL)
    r += 1

    r = write_section(ws, r, "NET INCOME (Partnership)", 4)
    line("Total Revenue", T["revenue"], T["revenue"])
    line("Less: Direct Costs (1099 contractors)", -T["contractor_total"], -T["contractor_total"])
    line("Less: Operating Expenses", -T["op_total_gaap"], -T["op_total_reclass"])
    line("= NET INCOME", T["net_gaap"], T["net_reclass"], bold=True, fill=TOTAL_FILL,
         note="Tax-reclass column reflects accountant-preferred adjustments.")
    r += 1

    r = write_section(ws, r, "K-1 PARTNER ALLOCATION", 4)
    line(f"Nairne — Cash distributions received", T["nairne_cash"], T["nairne_cash"],
         "Includes Fund Mgmt 59.5% + direct 0.5%. K-1 capital account.")
    line(f"Nairne — Allocated share of Net Income (98.36%)",
         T["net_gaap"] * T["nairne_pct"], T["net_reclass"] * T["nairne_pct"],
         "K-1 Box 1 (Ordinary Income).")
    line("Raj Duggal — Cash distributions received", T["raj_cash"], T["raj_cash"], "K-1 capital account.")
    line("Raj Duggal — Allocated share of Net Income (0.82%)",
         T["net_gaap"] * T["raj_pct"], T["net_reclass"] * T["raj_pct"], "K-1 Box 1.")
    line("Phil — Cash distributions received", T["phil_cash"], T["phil_cash"], "K-1 capital account.")
    line("Phil — Allocated share of Net Income (0.82%)",
         T["net_gaap"] * T["phil_pct"], T["net_reclass"] * T["phil_pct"], "K-1 Box 1.")
    r += 1

    r = write_section(ws, r, "PREPARER NOTES", 4)
    notes = [
        "1. Entity formed at the Armada Prime relaunch in August 2025; first year of operations.",
        "2. Revenue source: TPA (Formidium) Performance Fees Crystallized line, Aug-Dec 2025.",
        "3. Member structure (per Nairne 2026-05-05): Nairne 60% (Fund Mgmt 59.5% + direct 0.5%), Raj Duggal 0.5%, Phil 0.5%. All three are K-1 partners.",
        "4. Phil was previously thought to be a 1099 contractor but has been corrected to K-1 partner status.",
        "5. TruQuant payments are NOT included. The August 'Trader & Developer' $6,909.93 + 'Spydr' $88.78 are excluded per 2026-04-30 policy decision (TQ is upstream of GP entity).",
        "6. Contractor amounts shown are CASH BASIS per Distributions Armada Tech 2025 ledger. Difference vs accrual basis (TPA Performance Fees Crystallized) ≈ $11,587.",
        "7. RECOMMEND: $29,275 of '506c SPV Loan' line items should be reclassified to Balance Sheet (loan/capital).",
        "8. RECOMMEND: $18,000 December Insurance line is likely annual D&O — pro-rate to ~$7,500 for the 5-month period; book remainder as Prepaid Asset.",
    ]
    for note in notes:
        line(note)
        ws.row_dimensions[r-1].height = 30

    ws.column_dimensions["A"].width = 50
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 60


# ---------------------------------------------------------------------------
# Tab 3: Balance Sheet
# ---------------------------------------------------------------------------

def build_balance_sheet_tab(wb, T):
    ws = wb.create_sheet("3. Balance Sheet")
    r = title_block(ws, "Balance Sheet (as of Dec 31, 2025)", ncols=4)
    headers = ["Account", "Amount ($)", "Source / Method", "Notes"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header_row(ws, r, 4)
    r += 1

    def line(label, amount=None, source="", note="", bold=False, fill=None, warn=False):
        nonlocal r
        ws.cell(row=r, column=1, value=label)
        if amount is not None:
            ws.cell(row=r, column=2, value=amount).number_format = MONEY
        ws.cell(row=r, column=3, value=source)
        ws.cell(row=r, column=4, value=note).alignment = Alignment(wrap_text=True)
        if bold:
            for c in range(1, 5):
                ws.cell(row=r, column=c).font = Font(bold=True)
        if warn:
            for c in range(1, 5):
                ws.cell(row=r, column=c).fill = WARN_FILL
        elif fill:
            for c in range(1, 5):
                ws.cell(row=r, column=c).fill = fill
        r += 1

    spv_loans = T["spv_reclass"]

    r = write_section(ws, r, "ASSETS", 4)
    line("Cash & Cash Equivalents (Bank + Crypto Wallets)", None,
         "PLACEHOLDER", "⚠️ Need bank statements / wallet balances as of 12/31/2025", warn=True)
    line("506c SPV Loan Receivable / SPV Investment", spv_loans,
         "Reclassified from P&L", "Aug $4,275 + Oct $25,000")
    line("Prepaid Insurance", 10500,
         "Reclassified from P&L", "Dec $18k less $7,500 pro-rated to 2025 = $10,500 prepaid for 2026")
    line("Other Receivables / Accruals", None,
         "PLACEHOLDER", "⚠️ Any TPA accruals?", warn=True)
    line("Total Assets (excl. placeholders)", spv_loans + 10500, bold=True, fill=SUBTOTAL_FILL)
    r += 1

    r = write_section(ws, r, "LIABILITIES", 4)
    line("Accounts Payable", None, "PLACEHOLDER", "⚠️ Any unpaid contractor amounts? Distributions Ledger shows ~$11,588 cumulative cash-vs-accrual delta", warn=True)
    line("Accrued Expenses", None, "PLACEHOLDER", "⚠️ Any Q4 op expenses incurred but not paid?", warn=True)
    line("Total Liabilities", 0, bold=True, fill=SUBTOTAL_FILL)
    r += 1

    r = write_section(ws, r, "MEMBERS' EQUITY", 4)
    line("Member Capital — Nairne (60% ownership)", None,
         "PLACEHOLDER", "⚠️ Initial capital contributions in 2025?", warn=True)
    line("Member Capital — Raj Duggal (0.5% ownership)", None,
         "PLACEHOLDER", "⚠️ Initial capital contributions in 2025?", warn=True)
    line("Member Capital — Phil (0.5% ownership)", None,
         "PLACEHOLDER", "⚠️ Initial capital contributions in 2025?", warn=True)
    line("Cumulative Distributions — Nairne", -T["nairne_cash"],
         "Cash distributions made in 2025", f"Fund Mgmt ${T['nairne_cash'] - 946.97:,.2f} + direct ${946.97:,.2f}")
    line("Cumulative Distributions — Raj Duggal", -T["raj_cash"], "Cash distributions made in 2025")
    line("Cumulative Distributions — Phil", -T["phil_cash"], "Cash distributions made in 2025")
    line("Retained Earnings (Net Income for the year)", T["net_gaap"],
         "From P&L Statement", f"GAAP: ${T['net_gaap']:,.2f}. Reclass: ${T['net_reclass']:,.2f}")
    equity_total = T["net_gaap"] - T["nairne_cash"] - T["raj_cash"] - T["phil_cash"]
    line("Total Members' Equity (excl. placeholders)", equity_total, bold=True, fill=SUBTOTAL_FILL)
    r += 1

    r = write_section(ws, r, "BALANCING NOTE", 4)
    line("Total Assets", spv_loans + 10500)
    line("Total Liabilities + Equity", equity_total,
         note="When member capital + cash + payables are filled in, this should balance.")
    line("Imbalance (placeholder gap)", (spv_loans + 10500) - equity_total,
         note="Reflects the missing cash + member capital data.", warn=True)
    r += 1

    r = write_section(ws, r, "METHODOLOGY", 4)
    method_notes = [
        "1. Best-effort balance sheet built from transactional data. PLACEHOLDER lines need population by accountant.",
        "2. 506c SPV Loans ($29,275) reclassified from P&L to assets.",
        "3. $18,000 Dec Insurance split: $7,500 to 2025 P&L, $10,500 booked as Prepaid Asset.",
        "4. Cumulative Distributions shown as negative equity. Member capital contributions need to be added.",
        "5. The $11,588 cash-vs-accrual delta on Distributions ledger may flow through Accounts Payable. Confirm tax basis with accountant.",
    ]
    for note in method_notes:
        line(note)
        ws.row_dimensions[r-1].height = 30

    ws.column_dimensions["A"].width = 50
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 28
    ws.column_dimensions["D"].width = 60


# ---------------------------------------------------------------------------
# Tab 4: General Ledger
# ---------------------------------------------------------------------------

def build_gl_tab(wb, T):
    ws = wb.create_sheet("4. General Ledger")
    r = title_block(ws, "General Ledger — Cash Transactions", ncols=7)
    headers = ["Date", "Type", "Account", "Counterparty", "Description", "Debit ($)", "Credit ($)"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header_row(ws, r, 7)
    r += 1

    perf_fees = {
        "2025-08": 15355.51, "2025-09": 12474.75, "2025-10": 51906.99,
        "2025-11": 57074.09, "2025-12": 16211.69,
    }
    eom = {
        "2025-08": "2025-08-31", "2025-09": "2025-09-30", "2025-10": "2025-10-31",
        "2025-11": "2025-11-30", "2025-12": "2025-12-31",
    }

    txn_count = 0
    total_debit = 0.0
    total_credit = 0.0

    for period in ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12"]:
        d = eom[period]
        amt = perf_fees[period]
        write_txn(ws, r, d, "Revenue", "Performance Fees Income", "Armada Prime LLP (TPA)",
                  f"{PERIOD_LABELS[period]} GP cut received from fund", debit=amt, credit=None)
        r += 1
        txn_count += 1
        total_debit += amt

        for recipient, payout in ACTUAL_PAID.get(period, {}).items():
            if payout == 0:
                continue
            if recipient == "Fund Mgmt":
                acct = "K-1 Distribution to Member"
                desc = "Distribution to Nairne (Fund Mgmt 59.5% slice)"
                cp = "Nairne"
            elif recipient == "Nairne":
                acct = "K-1 Distribution to Member"
                desc = "Distribution to Nairne (direct 0.5%)"
                cp = "Nairne"
            elif recipient == "Raj":
                acct = "K-1 Distribution to Member"
                desc = "Distribution to Raj Duggal (direct 0.5%)"
                cp = "Raj Duggal"
            elif recipient == "Phil":
                acct = "K-1 Distribution to Member"
                desc = "Distribution to Phil (direct 0.5%, K-1 partner per Nairne 2026-05-05)"
                cp = "Phil"
            else:
                acct = "Capital Raiser Commission Expense (1099)"
                desc = f"1099-NEC payment to {recipient}"
                cp = recipient

            if payout >= 0:
                debit_val = None
                credit_val = payout
                total_credit += payout
            else:
                debit_val = -payout
                credit_val = None
                total_debit += -payout

            ttype = "Distribution" if recipient in K1_RECIPIENTS else "Expense"
            write_txn(ws, r, d, ttype, acct, cp, desc, debit=debit_val, credit=credit_val)
            r += 1
            txn_count += 1

        for vendor, amount in GP_OP_EXPENSES.get(period, []):
            acct = categorize_account(vendor)
            write_txn(ws, r, d, "Expense", acct, vendor,
                      f"GP-paid expense: {vendor}", debit=None, credit=amount)
            r += 1
            txn_count += 1
            total_credit += amount

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

    r += 2
    ws.cell(row=r, column=1, value="NOTES").font = Font(bold=True, color="C00000")
    r += 1
    notes = [
        "Each row = one cash transaction. Revenue receipts are debits to Cash; distributions and expense payments are credits to Cash.",
        "K-1 Distribution to Member: Nairne, Raj, Phil (all K-1 partners).",
        "Capital Raiser Commission Expense: Alec, Jake, AJ, Issac, Luke (1099 contractors).",
        "Dates are end-of-month. Actual settlement may have been days/weeks later.",
        "Source: Distributions Armada Tech 2025 ledger + BEST ONE Dec 2025 Costs.",
        "TruQuant payments excluded entirely (per Nairne 2026-04-30).",
        "Issac's December −$278.48 entry is a clawback against prior month overpayment.",
    ]
    for note in notes:
        ws.cell(row=r, column=1, value=note).alignment = Alignment(wrap_text=True)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
        ws.row_dimensions[r].height = 30
        r += 1

    for col, w in zip("ABCDEFG", [12, 13, 35, 22, 50, 14, 14]):
        ws.column_dimensions[col].width = w


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


# ---------------------------------------------------------------------------
# Tab 5: Asset Schedule
# ---------------------------------------------------------------------------

def build_asset_tab(wb, T):
    ws = wb.create_sheet("5. Asset Schedule")
    r = title_block(ws, "Asset Schedule (Fixed Assets / Depreciation)", ncols=8)
    headers = ["Asset Description", "Acquisition Date", "Cost", "Useful Life", "Depreciation Method", "Prior Accum Depr", "2025 Depr Expense", "Net Book Value"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header_row(ws, r, 8)
    r += 1

    ws.cell(row=r, column=1, value="(No fixed assets recorded for 2025)").font = Font(italic=True, color="999999")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    r += 2

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
        "Armada Prime Tech LLC has no fixed assets / depreciable property recorded for 2025. Services-only LLC.",
        "506c SPV Loan disbursements ($29,275 total) are NOT depreciable. They are loan receivables / equity investments — Balance Sheet items.",
        "If equipment / software / capital assets were purchased in 2025, please add them.",
    ]
    for note in notes:
        ws.cell(row=r, column=1, value=note).alignment = Alignment(wrap_text=True)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
        ws.row_dimensions[r].height = 30
        r += 1

    for i, w in enumerate([35, 14, 14, 14, 28, 16, 16, 16], 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------------------------------------------------------------------
# Tab 6: K-1 Partners
# ---------------------------------------------------------------------------

def build_k1_tab(wb, T):
    ws = wb.create_sheet("6. K-1 Partners")
    r = title_block(ws, "K-1 Partner Schedule", ncols=6)

    ws.cell(row=r, column=1, value="Per Nairne 2026-05-05: 3 K-1 partners — Nairne (60%), Raj Duggal (0.5%), Phil (0.5%). Phil corrected from prior 1099 status.").font = Font(italic=True, color="C00000")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    r += 2

    headers = ["Partner Name", "Ownership %", "Cash Distributions ($)", "K-1 Allocated Net Income — GAAP ($)", "K-1 Allocated Net Income — Reclass ($)", "SSN/Address (fill in)"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header_row(ws, r, 6)
    r += 1

    partners = [
        ("Nairne", T["nairne_pct"], T["nairne_cash"]),
        ("Raj Duggal", T["raj_pct"], T["raj_cash"]),
        ("Phil", T["phil_pct"], T["phil_cash"]),
    ]
    total_cash = 0
    total_gaap = 0
    total_reclass = 0
    for name, pct, cash in partners:
        ws.cell(row=r, column=1, value=name)
        ws.cell(row=r, column=2, value=f"{pct*100:.4f}%")
        ws.cell(row=r, column=3, value=cash).number_format = MONEY
        gaap_alloc = T["net_gaap"] * pct
        reclass_alloc = T["net_reclass"] * pct
        ws.cell(row=r, column=4, value=gaap_alloc).number_format = MONEY
        ws.cell(row=r, column=5, value=reclass_alloc).number_format = MONEY
        ws.cell(row=r, column=6, value="")
        for c in range(1, 7):
            ws.cell(row=r, column=c).fill = K1_FILL
        total_cash += cash
        total_gaap += gaap_alloc
        total_reclass += reclass_alloc
        r += 1

    ws.cell(row=r, column=1, value="TOTAL").font = Font(bold=True)
    ws.cell(row=r, column=2, value="100.00%")
    ws.cell(row=r, column=3, value=total_cash).number_format = MONEY
    ws.cell(row=r, column=4, value=total_gaap).number_format = MONEY
    ws.cell(row=r, column=5, value=total_reclass).number_format = MONEY
    for c in range(1, 7):
        ws.cell(row=r, column=c).fill = TOTAL_FILL
        ws.cell(row=r, column=c).font = Font(bold=True)
    r += 2

    ws.cell(row=r, column=1, value="NOTES").font = Font(bold=True)
    r += 1
    notes = [
        "Nairne's 60% is the sum of Fund Management 59.5% slice + direct 0.5% slice. Both are partner allocations (K-1), not entity expenses.",
        "Cash Distributions and Allocated K-1 Income are different concepts in partnership tax. K-1 Box 1 reports allocated income; Box L tracks capital account changes from distributions.",
        "Ownership % shown is derived from the 60/0.5/0.5 split. The actual LLC operating agreement governs the legal allocation.",
        "If the operating agreement specifies a different income allocation method (e.g., guaranteed payments to Nairne for managing), the accountant should adjust.",
    ]
    for note in notes:
        ws.cell(row=r, column=1, value=note).alignment = Alignment(wrap_text=True)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
        ws.row_dimensions[r].height = 30
        r += 1

    for i, w in enumerate([20, 14, 22, 28, 28, 35], 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------------------------------------------------------------------
# Tab 7: 1099 Recipients
# ---------------------------------------------------------------------------

def build_1099_tab(wb, T):
    ws = wb.create_sheet("7. 1099 Recipients")
    r = title_block(ws, "1099-NEC Recipients Schedule", ncols=5)

    headers = ["Recipient", "2025 Total ($)", "Source of Payment", "EIN/SSN (fill in)", "Address (fill in)"]
    for i, h in enumerate(headers, 1):
        ws.cell(row=r, column=i, value=h)
    set_header_row(ws, r, 5)
    r += 1

    yt = T["year_totals"]
    contractors = [
        ("Alec Atkinson", yt.get("Alec Atkinson", 0), "Capital raiser commission (39% of his investors' perf fees)"),
        ("Jake Gordon", yt.get("Jake Gordon", 0), "Capital raiser commission"),
        ("AJ Affleck", yt.get("AJ Affleck", 0), "Capital raiser commission"),
        ("Issac Morris", yt.get("Issac", 0), "Capital raiser commission"),
        ("Luke Affleck", yt.get("Luke", 0), "Capital raiser commission"),
        ("Chris (last name TBD)", 11500.00, "Operating contractor labor (Nov $7,500 + Dec $4,000)"),
    ]
    total = 0
    for name, amt, src in contractors:
        ws.cell(row=r, column=1, value=name)
        ws.cell(row=r, column=2, value=amt).number_format = MONEY
        ws.cell(row=r, column=3, value=src)
        ws.cell(row=r, column=4, value="")
        ws.cell(row=r, column=5, value="")
        total += amt
        r += 1
    ws.cell(row=r, column=1, value="TOTAL 1099 PAYMENTS").font = Font(bold=True)
    ws.cell(row=r, column=2, value=total).number_format = MONEY
    for c in range(1, 6):
        ws.cell(row=r, column=c).fill = TOTAL_FILL
        ws.cell(row=r, column=c).font = Font(bold=True)
    r += 2

    ws.cell(row=r, column=1, value="VENDORS THAT MAY ALSO REQUIRE 1099").font = Font(bold=True, color="C00000")
    r += 1
    vendors_check = [
        ("PVD", 12000.00, "If individual/sole prop and >$600 → 1099-NEC. Verify entity type."),
        ("Ad Spend / Marketing vendors", 5000.00, "If individual/sole prop. Verify."),
        ("Website builder", 7500.00, "If individual contractor. Verify."),
        ("Alpha Verification", 2250.00, "Likely corporate; unlikely 1099 needed. Verify."),
        ("Insurance carrier", 18000.00, "Corporate — no 1099."),
        ("Formidium (TPA)", 5700.00, "Corporate — no 1099."),
    ]
    for name, amt, note in vendors_check:
        ws.cell(row=r, column=1, value=name)
        ws.cell(row=r, column=2, value=amt).number_format = MONEY
        ws.cell(row=r, column=3, value=note).alignment = Alignment(wrap_text=True)
        r += 1
    r += 1

    ws.cell(row=r, column=1, value="NOTE: Phil is NOT on this 1099 list — Phil is a K-1 partner (per Nairne 2026-05-05). See K-1 Partners tab.").font = Font(italic=True, color="C00000")
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)

    for i, w in enumerate([22, 16, 60, 22, 35], 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------------------------------------------------------------------
# Tab 8: Tax Organizer Answers
# ---------------------------------------------------------------------------

def build_organizer_tab(wb, T):
    ws = wb.create_sheet("8. Tax Organizer Answers")
    r = title_block(ws, "Monily Partnership Tax Organizer — Pre-Filled Answers", ncols=3)

    sections = [
        ("CORPORATION GENERAL INFORMATION", [
            ("Legal name of business", "Armada Prime Tech LLC"),
            ("Filing for the year", "2025"),
            ("EIN", "⚠️ TO PROVIDE — from IRS letter"),
            ("Phone Number", "⚠️ TO PROVIDE"),
            ("Email", "⚠️ TO PROVIDE"),
            ("Corporation address / State / City / Zip / Country", "⚠️ TO PROVIDE"),
            ("Above address is new", "No"),
            ("Is it first year of Filing", "Yes"),
            ("Partnership state residence", "⚠️ TO PROVIDE (state of formation)"),
        ]),
        ("DOCUMENTS (Yes/No/N/A)", [
            ("EIN letter", "Yes (need to upload)"),
            ("Letter of Incorporation", "Yes (need to upload)"),
            ("Profit & Loss Statement", "Yes — see Tab 2"),
            ("Balance Sheet", "Partial — see Tab 3 (placeholders flagged)"),
            ("General Ledgers", "Yes — see Tab 4"),
            ("Asset Schedule Template", "Yes (no fixed assets) — see Tab 5"),
            ("Payroll Report and Filings", "N/A (no W-2 employees)"),
            ("Last Filed Tax Year", "No (first year)"),
            ("Sales Tax Filings", "N/A"),
            ("Estimated State Tax Payments", "No (unless made — confirm)"),
            ("First time filing with Monily", "Yes"),
        ]),
        ("PARTNERS INFORMATION", [
            ("Number of Share Holders (Partners)", "3 (Nairne, Raj Duggal, Phil)"),
            ("Change of business name during year", "No"),
            ("Calendar year filer", "Yes"),
            ("Foreign account interest/signature authority", "⚠️ Verify — depends on crypto exchange custody"),
            ("Any shareholder a disregarded entity / trust / S-corp", "No (members are individuals — confirm)"),
            ("Owns 20%+ of foreign/domestic corp", "No"),
            ("Outstanding restricted stock", "No"),
            ("Outstanding stock options/warrants", "No"),
            ("Distribution of property or transfer of shareholder interest", "No (Phil → Alec was 2026, not 2025)"),
            ("Accessibility expenses", "No"),
            ("FICA on tips above min wage", "No (no W-2 employees)"),
            ("Own residential rental buildings (low-income housing)", "No"),
            ("R&D expenditures during year", "No"),
        ]),
        ("SIGNATURE", [
            ("Taxpayer Sign", "Nairne (Managing Member)"),
            ("Taxpayer Title", "Managing Member"),
            ("Date", date.today().isoformat()),
        ]),
    ]

    for section_title, fields in sections:
        r = write_section(ws, r, section_title, 3)
        for label, value in fields:
            ws.cell(row=r, column=1, value=label).font = Font(bold=True)
            ws.cell(row=r, column=2, value=value)
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=3)
            ws.cell(row=r, column=2).alignment = Alignment(wrap_text=True)
            if "⚠️" in str(value):
                for c in range(1, 4):
                    ws.cell(row=r, column=c).fill = WARN_FILL
            r += 1
        r += 1

    ws.column_dimensions["A"].width = 50
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 35


# ---------------------------------------------------------------------------
# Cover memo (markdown)
# ---------------------------------------------------------------------------

def build_cover_memo(T):
    md = f"""# Monily Tax Organizer — Cover Memo
## Armada Prime Tech LLC — Tax Year 2025

**Prepared:** {date.today().isoformat()}
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
| **Revenue** (Performance Fees from Armada Prime LLP) | ${T['revenue']:,.2f} | ${T['revenue']:,.2f} |
| Direct Costs (1099 contractor commissions) | (${T['contractor_total']:,.2f}) | (${T['contractor_total']:,.2f}) |
| Operating Expenses | (${T['op_total_gaap']:,.2f}) | (${T['op_total_reclass']:,.2f}) |
| **Net Income (Partnership)** | **${T['net_gaap']:,.2f}** | **${T['net_reclass']:,.2f}** |

The GAAP→reclass swing is **$29,275 in 506c SPV Loans** (move to balance sheet) and **$10,500 in Insurance proration** (Dec $18K is annual D&O — only 5/12 hits 2025).

---

## Member Structure & K-1 Allocation (3 Partners)

Per Nairne 2026-05-05 — **Phil corrected to K-1 partner** (was previously thought to be a 1099 contractor).

| Member | Ownership % | Cash Distributions Received | K-1 Allocated Net Income (Reclass-Basis) |
|---|---:|---:|---:|
| **Nairne** | {T['nairne_pct']*100:.2f}% (60/61) | ${T['nairne_cash']:,.2f} | ${T['net_reclass'] * T['nairne_pct']:,.2f} |
| **Raj Duggal** | {T['raj_pct']*100:.2f}% (0.5/61) | ${T['raj_cash']:,.2f} | ${T['net_reclass'] * T['raj_pct']:,.2f} |
| **Phil** | {T['phil_pct']*100:.2f}% (0.5/61) | ${T['phil_cash']:,.2f} | ${T['net_reclass'] * T['phil_pct']:,.2f} |

Nairne's 60% = Fund Management 59.5% slice + direct 0.5%. The Fund Management slice is K-1 income to Nairne (NOT a separate entity expense / 1099).

---

## 1099-NEC Recipients (Aug–Dec 2025 totals)

| Recipient | 2025 Total |
|---|---:|
| Alec Atkinson | ${T['year_totals'].get('Alec Atkinson', 0):,.2f} |
| Jake Gordon | ${T['year_totals'].get('Jake Gordon', 0):,.2f} |
| AJ Affleck | ${T['year_totals'].get('AJ Affleck', 0):,.2f} |
| Issac Morris | ${T['year_totals'].get('Issac', 0):,.2f} |
| Luke Affleck | ${T['year_totals'].get('Luke', 0):,.2f} |
| Chris (operating contractor) | $11,500.00 |
| **Total 1099 Payments** | **${T['contractor_total'] + 11500:,.2f}** |

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
| **Total** | **${T['op_total_gaap']:,.2f}** | **${T['op_total_reclass']:,.2f}** | |

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
"""
    OUT_MD.write_text(md)
    print(f"Wrote {OUT_MD}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    T = compute_year_totals()

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    build_cover_tab(wb, T)
    build_pnl_tab(wb, T)
    build_balance_sheet_tab(wb, T)
    build_gl_tab(wb, T)
    build_asset_tab(wb, T)
    build_k1_tab(wb, T)
    build_1099_tab(wb, T)
    build_organizer_tab(wb, T)

    wb.save(OUT_XLSX)
    print(f"Wrote {OUT_XLSX}")

    build_cover_memo(T)
    print(f"\nDone. Package files in {OUT_DIR}/")
