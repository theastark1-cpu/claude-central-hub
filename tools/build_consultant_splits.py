#!/usr/bin/env python3
"""Build consultant-splits dynamic Excel + dashboard JSON from a TPA Reporting Package.

Reads:
  1. The TPA reporting package xlsx (per-investor performance fees = the GP pool).
  2. The internal Monthly Return xlsx (IDS sheet → investor → consultant mapping).

Writes:
  1. <output_xlsx>: a self-contained workbook with live formulas (named cells for split %,
     xlookups for consultant attribution, sumifs for consultant aggregation).
  2. <repo>/data/consultant_splits.json: month-keyed snapshot for the dashboard.

Reconciliation insight (March 2026):
  - TPA "Gross Income" $404,850.79  = the Fund's 82% cut (post-TruQuant).
  - TPA "Performance Fees Crystallized" $121,404.24 = GP Cut (30% of Fund cut).
  - TPA "Net to Investors" $283,276.56 = Investor Cut (70% of Fund cut).
  TruQuant's 18% is taken upstream and never enters Armada Prime's books.

Each TPA investor's perf_fee column is therefore the per-investor GP pool. We attribute
that pool to the consultant who raised the investor (per IDS), then split it:
  Fund Mgmt:  59.5%
  Consultant: 39.0%
  Raj:         0.5%
  Nairne:      0.5%
  Phil:        0.5%

Usage:
  python tools/build_consultant_splits.py <tpa_xlsx> [--internal <internal_xlsx>]
                                                     [--output-xlsx <path>]
                                                     [--label "Mar 2026"]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_tpa_report import parse_workbook  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "data" / "consultant_splits.json"
DEFAULT_INTERNAL = Path("/Users/nairne/Downloads/March 2026 Monthly Return (1).xlsx")
DEFAULT_TPA = Path(
    "/Users/nairne/Downloads/Reporting Package - March 2026_v2_final/"
    "Armada_Prime_LLP_Reporting Package_2026-03-31_1777286642911.xlsx"
)
DEFAULT_OUTPUT_XLSX = REPO_ROOT / "Armada_Consultant_Splits.xlsx"

SPLIT_PCTS = {
    "fund_mgmt": 0.595,
    "consultant": 0.39,
    "raj": 0.005,
    "nairne": 0.005,
    "alec": 0.005,  # Alec is the new GP (was Phil before 2026-04-27)
}

# Confirmed by user 2026-04-27. Augments / overrides the internal IDS sheet.
# Fund Hub SPV = sub-LP container with mixed AJ/Alec investors; will be split out
# in a separate buildout. For now its 39% portion is held in "Fund Hub SPV
# (Pending Split)" so it stays visible.
CONSULTANT_OVERRIDES = {
    "14-Class B-1027-1": "Fund Hub SPV (Pending Split)",  # Fund Hub Investments LLC
    "14-Class B-1076-1": "Alec Atkinson",                  # Philippe Henriques
    "14-Class B-1073-1": "Alec Atkinson",                  # PGJCHoldings LLC
    "14-Class B-1072-1": "Alec Atkinson",                  # Mashirito LLC
    "14-Class B-1068-1": "Alec Atkinson",                  # Weston Shea Christensen
}


# ---------------------------------------------------------------------------
# IDS loader
# ---------------------------------------------------------------------------

def load_ids(internal_xlsx: Path) -> dict[str, dict]:
    """Return {tpa_id: {name, consultant, position_id}} from the internal IDS sheet,
    with overrides applied. Skips rows missing TPA ID or consultant.
    """
    wb = openpyxl.load_workbook(internal_xlsx, data_only=True)
    ws = wb["IDS"]
    out: dict[str, dict] = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        name, tpa_id, pos_id, consultant = row[0], row[1], row[2], row[3]
        if not tpa_id:
            continue
        out[str(tpa_id).strip()] = {
            "name": name.strip() if isinstance(name, str) else name,
            "consultant": consultant.strip() if isinstance(consultant, str) else consultant,
            "position_id": pos_id,
        }
    for tpa_id, cons in CONSULTANT_OVERRIDES.items():
        if tpa_id in out:
            out[tpa_id]["consultant"] = cons
        else:
            out[tpa_id] = {"name": None, "consultant": cons, "position_id": None}
    return out


# ---------------------------------------------------------------------------
# Costs loader
# ---------------------------------------------------------------------------

def load_costs(internal_xlsx: Path) -> list[dict]:
    """Read the Costs sheet from the internal Monthly Return file.

    Returns a list of {name, amount} dicts (excludes the TOTAL row).
    """
    wb = openpyxl.load_workbook(internal_xlsx, data_only=True)
    ws = wb["Costs"]
    out = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        name = row[0]
        amount = row[1] if len(row) > 1 else None
        if not isinstance(name, str):
            continue
        name = name.strip()
        if not name or name.lower() == "total":
            break
        if not isinstance(amount, (int, float)):
            continue
        out.append({"name": name, "amount": float(amount)})
    return out


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------

def reconcile(tpa_investors: list[dict], ids_map: dict[str, dict]) -> list[dict]:
    """Return per-investor rows with consultant attribution and reconciliation flag."""
    out = []
    for inv in tpa_investors:
        tpa_id = str(inv["investor_no"]).strip()
        ids_row = ids_map.get(tpa_id, {})
        consultant = ids_row.get("consultant") or "Unmapped"
        out.append({
            "tpa_id": tpa_id,
            "name": inv["name"],
            "consultant": consultant,
            "position_id": ids_row.get("position_id"),
            "begin_balance": inv.get("begin_balance", 0) or 0,
            "ending_balance": inv.get("ending_balance", 0) or 0,
            "gross_profit": inv.get("gross_profit", 0) or 0,
            "perf_fee": inv.get("perf_fee", 0) or 0,
            "additions": inv.get("additions", 0) or 0,
            "withdrawals": inv.get("withdrawals", 0) or 0,
        })
    return out


# ---------------------------------------------------------------------------
# Excel builder (formulas, not values)
# ---------------------------------------------------------------------------

ACCENT = "1f6feb"
HEADER_FILL = PatternFill("solid", fgColor="1a2236")
HEADER_FONT = Font(bold=True, color="e2e8f0", size=10)
TITLE_FONT = Font(bold=True, color="ffffff", size=12)
INPUT_FILL = PatternFill("solid", fgColor="2a3550")
TOTAL_FILL = PatternFill("solid", fgColor="334155")
OK_FILL = PatternFill("solid", fgColor="14532d")
WARN_FILL = PatternFill("solid", fgColor="7f1d1d")
BORDER = Border(*(Side(style="thin", color="2a3550"),) * 4)


def _style_header(cell):
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.border = BORDER
    cell.alignment = Alignment(horizontal="left", vertical="center")


def _autosize(ws, min_w: int = 10, max_w: int = 48):
    for col_cells in ws.columns:
        col = col_cells[0].column_letter
        widest = max((len(str(c.value)) if c.value is not None else 0 for c in col_cells), default=0)
        ws.column_dimensions[col].width = max(min_w, min(max_w, widest + 2))


def build_workbook(records: list[dict], period_label: str, output_path: Path,
                   costs: list[dict]) -> dict:
    """Write the dynamic Excel. Returns summary dict."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # --------- 1. Inputs ---------
    ws_in = wb.create_sheet("Inputs")
    ws_in["A1"] = "Armada Prime LLP — Consultant Splits"
    ws_in["A1"].font = TITLE_FONT
    ws_in.merge_cells("A1:F1")
    ws_in["A2"] = f"Period: {period_label}"
    ws_in["A2"].font = Font(italic=True, color="94a3b8")

    # Named cells for split percentages
    ws_in["A4"] = "GP Pool Split %"
    ws_in["A4"].font = Font(bold=True, color="e2e8f0")
    pct_rows = [
        ("Fund Mgmt", "GP_FundMgmt_Pct", SPLIT_PCTS["fund_mgmt"]),
        ("Consultant", "GP_Consultant_Pct", SPLIT_PCTS["consultant"]),
        ("Raj", "GP_Raj_Pct", SPLIT_PCTS["raj"]),
        ("Nairne", "GP_Nairne_Pct", SPLIT_PCTS["nairne"]),
        ("Alec (GP)", "GP_Alec_Pct", SPLIT_PCTS["alec"]),
    ]
    for i, (label, name, val) in enumerate(pct_rows, start=5):
        ws_in.cell(row=i, column=1, value=label)
        c = ws_in.cell(row=i, column=2, value=val)
        c.fill = INPUT_FILL
        c.number_format = "0.00%"
        wb.defined_names[name] = DefinedName(name=name, attr_text=f"Inputs!$B${i}")

    ws_in["A11"] = "Total split (sanity)"
    ws_in["B11"] = "=SUM(B5:B9)"
    ws_in["B11"].number_format = "0.00%"
    ws_in["B11"].font = Font(bold=True, color="10b981")

    ws_in["A13"] = "Expense Pool"
    ws_in["A13"].font = Font(bold=True, color="e2e8f0")
    ws_in["A14"] = "Operating expenses (live-linked to Costs sheet)"
    ws_in["B14"] = "=Costs_Total"  # named range defined when Costs sheet is built
    ws_in["B14"].number_format = '"$"#,##0.00'
    ws_in["B14"].font = Font(bold=True, color="10b981")
    wb.defined_names["Expense_Pool"] = DefinedName(name="Expense_Pool", attr_text="Inputs!$B$14")

    ws_in["A16"] = "Notes"
    ws_in["A16"].font = Font(bold=True, color="e2e8f0")
    ws_in["A17"] = (
        "TPA per-investor performance-fee crystallized = each investor's GP pool. "
        "Consultant attribution flows from IDS → Per-Investor Allocation → Consultant Summary. "
        "Edit the Per-Investor sheet to override perf_fee for what-if scenarios."
    )
    ws_in["A17"].alignment = Alignment(wrap_text=True, vertical="top")
    ws_in.merge_cells("A17:F19")

    ws_in.column_dimensions["A"].width = 38
    ws_in.column_dimensions["B"].width = 18

    # --------- 2. IDS Mapping ---------
    ws_ids = wb.create_sheet("IDS Mapping")
    ids_headers = ["TPA ID", "Investor Name", "Position ID", "Consultant", "Source"]
    for i, h in enumerate(ids_headers, start=1):
        c = ws_ids.cell(row=1, column=i, value=h)
        _style_header(c)

    seen_ids: set[str] = set()
    for r in records:
        seen_ids.add(r["tpa_id"])
    # All IDS rows (mapped + unmapped + overrides) — so we can xlookup safely
    for i, rec in enumerate(records, start=2):
        ws_ids.cell(row=i, column=1, value=rec["tpa_id"])
        ws_ids.cell(row=i, column=2, value=rec["name"])
        ws_ids.cell(row=i, column=3, value=rec["position_id"])
        ws_ids.cell(row=i, column=4, value=rec["consultant"])
        src = "TPA + IDS"
        if rec["tpa_id"] in CONSULTANT_OVERRIDES:
            src = "Override (confirmed 2026-04-27)"
        if rec["consultant"] == "Unmapped":
            src = "UNMAPPED"
        ws_ids.cell(row=i, column=5, value=src)

    last_id_row = len(records) + 1
    wb.defined_names["IDS_TPA"] = DefinedName(
        name="IDS_TPA",
        attr_text=f"'IDS Mapping'!$A$2:$A${last_id_row}",
    )
    wb.defined_names["IDS_Consultant"] = DefinedName(
        name="IDS_Consultant",
        attr_text=f"'IDS Mapping'!$D$2:$D${last_id_row}",
    )
    _autosize(ws_ids)

    # --------- 3. Per-Investor Allocation ---------
    ws_p = wb.create_sheet("Per-Investor Allocation")
    p_headers = [
        "TPA ID", "Investor", "Consultant",
        "Begin Balance", "Ending Balance", "Gross P&L", "Perf Fee (GP Pool)",
        "Fund Mgmt", "Consultant Cut", "Raj", "Nairne", "Alec (GP)",
        "Sum Check",
    ]
    for i, h in enumerate(p_headers, start=1):
        c = ws_p.cell(row=1, column=i, value=h)
        _style_header(c)

    for i, rec in enumerate(records, start=2):
        ws_p.cell(row=i, column=1, value=rec["tpa_id"])
        ws_p.cell(row=i, column=2, value=rec["name"])
        # Live xlookup so consultant changes in IDS Mapping flow through
        ws_p.cell(row=i, column=3,
                  value=f'=IFERROR(XLOOKUP(A{i}, IDS_TPA, IDS_Consultant), "Unmapped")')
        ws_p.cell(row=i, column=4, value=rec["begin_balance"]).number_format = '"$"#,##0.00'
        ws_p.cell(row=i, column=5, value=rec["ending_balance"]).number_format = '"$"#,##0.00'
        ws_p.cell(row=i, column=6, value=rec["gross_profit"]).number_format = '"$"#,##0.00'
        c_pf = ws_p.cell(row=i, column=7, value=rec["perf_fee"])
        c_pf.number_format = '"$"#,##0.00'
        c_pf.fill = INPUT_FILL
        # Split formulas reference the named cells
        ws_p.cell(row=i, column=8, value=f"=G{i}*GP_FundMgmt_Pct").number_format = '"$"#,##0.00'
        ws_p.cell(row=i, column=9, value=f"=G{i}*GP_Consultant_Pct").number_format = '"$"#,##0.00'
        ws_p.cell(row=i, column=10, value=f"=G{i}*GP_Raj_Pct").number_format = '"$"#,##0.00'
        ws_p.cell(row=i, column=11, value=f"=G{i}*GP_Nairne_Pct").number_format = '"$"#,##0.00'
        ws_p.cell(row=i, column=12, value=f"=G{i}*GP_Alec_Pct").number_format = '"$"#,##0.00'
        ws_p.cell(row=i, column=13,
                  value=f"=ROUND(SUM(H{i}:L{i})-G{i}, 2)").number_format = '"$"#,##0.00'

    last_inv_row = len(records) + 1
    total_row = last_inv_row + 1
    ws_p.cell(row=total_row, column=2, value="TOTAL").font = Font(bold=True)
    for col in range(4, 13):
        cl = get_column_letter(col)
        cell = ws_p.cell(row=total_row, column=col,
                         value=f"=SUM({cl}2:{cl}{last_inv_row})")
        cell.number_format = '"$"#,##0.00'
        cell.font = Font(bold=True)
        cell.fill = TOTAL_FILL
    ws_p.cell(row=total_row, column=13,
              value=f"=ROUND(SUM(H{total_row}:L{total_row})-G{total_row}, 2)").number_format = '"$"#,##0.00'

    wb.defined_names["PI_Consultant"] = DefinedName(
        name="PI_Consultant",
        attr_text=f"'Per-Investor Allocation'!$C$2:$C${last_inv_row}",
    )
    wb.defined_names["PI_PerfFee"] = DefinedName(
        name="PI_PerfFee",
        attr_text=f"'Per-Investor Allocation'!$G$2:$G${last_inv_row}",
    )
    wb.defined_names["PI_ConsultantCut"] = DefinedName(
        name="PI_ConsultantCut",
        attr_text=f"'Per-Investor Allocation'!$I$2:$I${last_inv_row}",
    )
    wb.defined_names["PI_FundMgmt"] = DefinedName(
        name="PI_FundMgmt",
        attr_text=f"'Per-Investor Allocation'!$H$2:$H${last_inv_row}",
    )
    wb.defined_names["PI_Capital"] = DefinedName(
        name="PI_Capital",
        attr_text=f"'Per-Investor Allocation'!$E$2:$E${last_inv_row}",
    )
    _autosize(ws_p)

    # --------- 4. Consultant Summary ---------
    consultant_names = sorted({r["consultant"] for r in records if r["consultant"] != "Unmapped"})
    if any(r["consultant"] == "Unmapped" for r in records):
        consultant_names.append("Unmapped")

    ws_c = wb.create_sheet("Consultant Summary")
    c_headers = [
        "Consultant", "# Investors", "Capital Raised", "GP Earned",
        "% of GP Pool", "Allocated Expenses", "Net Payout",
    ]
    for i, h in enumerate(c_headers, start=1):
        c = ws_c.cell(row=1, column=i, value=h)
        _style_header(c)

    for i, name in enumerate(consultant_names, start=2):
        ws_c.cell(row=i, column=1, value=name)
        ws_c.cell(row=i, column=2,
                  value=f'=COUNTIF(PI_Consultant, A{i})')
        ws_c.cell(row=i, column=3,
                  value=f'=SUMIF(PI_Consultant, A{i}, PI_Capital)').number_format = '"$"#,##0.00'
        # GP Earned = sum of consultant cut for this consultant's investors
        ws_c.cell(row=i, column=4,
                  value=f'=SUMIF(PI_Consultant, A{i}, PI_ConsultantCut)').number_format = '"$"#,##0.00'

    # Row for Fund Mgmt aggregate (every investor contributes regardless of consultant)
    fm_row = len(consultant_names) + 2
    ws_c.cell(row=fm_row, column=1, value="Fund Mgmt").font = Font(italic=True, color="93c5fd")
    ws_c.cell(row=fm_row, column=2, value=f'=COUNTA(PI_Consultant)')
    ws_c.cell(row=fm_row, column=3, value=f'=SUM(PI_Capital)').number_format = '"$"#,##0.00'
    ws_c.cell(row=fm_row, column=4, value=f'=SUM(PI_FundMgmt)').number_format = '"$"#,##0.00'

    # Fixed partners (Raj/Nairne/Alec — Alec replaced Phil 2026-04-27 as new GP)
    fixed_specs = [
        ("Raj (fixed 0.5%)", "GP_Raj_Pct"),
        ("Nairne (fixed 0.5%)", "GP_Nairne_Pct"),
        ("Alec (GP fixed 0.5%)", "GP_Alec_Pct"),
    ]
    for j, (label, pct_name) in enumerate(fixed_specs, start=1):
        r = fm_row + j
        ws_c.cell(row=r, column=1, value=label).font = Font(italic=True, color="d8b4fe")
        ws_c.cell(row=r, column=2, value="—")
        ws_c.cell(row=r, column=3, value="—")
        ws_c.cell(row=r, column=4,
                  value=f'=SUM(PI_PerfFee)*{pct_name}').number_format = '"$"#,##0.00'

    last_summary_row = fm_row + len(fixed_specs)

    # GP Pool total used for % calc
    pool_cell = f"$D${last_summary_row + 1}"

    for r in range(2, last_summary_row + 1):
        ws_c.cell(row=r, column=5, value=f"=IFERROR(D{r}/{pool_cell},0)").number_format = "0.00%"
        ws_c.cell(row=r, column=6,
                  value=f"=IFERROR(D{r}/{pool_cell},0)*Expense_Pool").number_format = '"$"#,##0.00'
        ws_c.cell(row=r, column=7, value=f"=D{r}-F{r}").number_format = '"$"#,##0.00'

    # Total row
    total_r = last_summary_row + 1
    ws_c.cell(row=total_r, column=1, value="GP POOL TOTAL").font = Font(bold=True)
    for col_letter in ("D", "F", "G"):
        cell = ws_c[f"{col_letter}{total_r}"]
        # Need a sum that doesn't double-count: GP Earned column already includes
        # consultants + Fund Mgmt + fixed; total is the sum of column D for rows 2..last_summary_row
        cell.value = f"=SUM({col_letter}2:{col_letter}{last_summary_row})"
        cell.number_format = '"$"#,##0.00'
        cell.font = Font(bold=True)
        cell.fill = TOTAL_FILL

    _autosize(ws_c)

    # --------- 5. Costs ---------
    # The Costs sheet feeds Expense_Pool (named cell) and is then allocated
    # pro-rata by GP % via the existing Allocated Expenses formula in
    # Consultant Summary. Edit a cost line item and everything downstream
    # recalculates.
    ws_costs = wb.create_sheet("Costs")
    ws_costs["A1"] = "Operating Costs"
    ws_costs["A1"].font = TITLE_FONT
    ws_costs.merge_cells("A1:D1")
    ws_costs["A2"] = f"Period: {period_label}"
    ws_costs["A2"].font = Font(italic=True, color="94a3b8")

    cost_headers = ["Category", "Amount", "Notes", "% of Pool"]
    for i, h in enumerate(cost_headers, start=1):
        c = ws_costs.cell(row=4, column=i, value=h)
        _style_header(c)

    cost_data_start = 5
    for i, item in enumerate(costs, start=cost_data_start):
        ws_costs.cell(row=i, column=1, value=item["name"])
        cell = ws_costs.cell(row=i, column=2, value=item["amount"])
        cell.number_format = '"$"#,##0.00'
        cell.fill = INPUT_FILL
        ws_costs.cell(row=i, column=4,
                      value=f"=B{i}/Costs_Total").number_format = "0.00%"

    last_cost_row = cost_data_start + len(costs) - 1
    total_row_costs = last_cost_row + 1
    ws_costs.cell(row=total_row_costs, column=1, value="TOTAL").font = Font(bold=True)
    total_cell = ws_costs.cell(row=total_row_costs, column=2,
                               value=f"=SUM(B{cost_data_start}:B{last_cost_row})")
    total_cell.number_format = '"$"#,##0.00'
    total_cell.font = Font(bold=True)
    total_cell.fill = TOTAL_FILL
    ws_costs.cell(row=total_row_costs, column=4, value="=SUM(D5:D" + str(last_cost_row) + ")").number_format = "0.00%"

    wb.defined_names["Costs_Total"] = DefinedName(
        name="Costs_Total",
        attr_text=f"Costs!$B${total_row_costs}",
    )

    # Allocation by party section (mirrors Consultant Summary's Allocated Expenses)
    ws_costs.cell(row=total_row_costs + 2, column=1, value="Allocation by GP %").font = Font(bold=True, color="e2e8f0")
    alloc_hdr_row = total_row_costs + 3
    for i, h in enumerate(["Party", "% of GP Pool", "Allocated Expense"], start=1):
        c = ws_costs.cell(row=alloc_hdr_row, column=i, value=h)
        _style_header(c)
    # Reference Consultant Summary directly so it always agrees
    parties = consultant_names + ["Fund Mgmt"] + [s[0] for s in fixed_specs]
    for i, party in enumerate(parties, start=alloc_hdr_row + 1):
        ws_costs.cell(row=i, column=1, value=party)
        ws_costs.cell(row=i, column=2,
                      value=f'=IFERROR(VLOOKUP(A{i},\'Consultant Summary\'!$A$2:$E${last_summary_row},5,FALSE),0)').number_format = "0.00%"
        ws_costs.cell(row=i, column=3, value=f"=B{i}*Costs_Total").number_format = '"$"#,##0.00'
    alloc_total_row = alloc_hdr_row + 1 + len(parties)
    ws_costs.cell(row=alloc_total_row, column=1, value="TOTAL").font = Font(bold=True)
    for col_letter, formula in [("B", f"=SUM(B{alloc_hdr_row+1}:B{alloc_total_row-1})"),
                                  ("C", f"=SUM(C{alloc_hdr_row+1}:C{alloc_total_row-1})")]:
        cell = ws_costs[f"{col_letter}{alloc_total_row}"]
        cell.value = formula
        cell.font = Font(bold=True)
        cell.fill = TOTAL_FILL
    ws_costs[f"B{alloc_total_row}"].number_format = "0.00%"
    ws_costs[f"C{alloc_total_row}"].number_format = '"$"#,##0.00'

    ws_costs.column_dimensions["A"].width = 32
    ws_costs.column_dimensions["B"].width = 16
    ws_costs.column_dimensions["C"].width = 36
    ws_costs.column_dimensions["D"].width = 12

    # --------- 6. Reconciliation ---------
    ws_r = wb.create_sheet("Reconciliation")
    ws_r["A1"] = "Reconciliation Checks"
    ws_r["A1"].font = TITLE_FONT
    ws_r.merge_cells("A1:D1")

    checks = [
        ("Sum of per-investor Perf Fee (GP pool from TPA)",
         f"=SUM(PI_PerfFee)",
         "TPA crystallized total — should match the package's reported number"),
        ("Sum of all per-investor split columns (H–L)",
         f"='Per-Investor Allocation'!H{total_row}+'Per-Investor Allocation'!I{total_row}+'Per-Investor Allocation'!J{total_row}+'Per-Investor Allocation'!K{total_row}+'Per-Investor Allocation'!L{total_row}",
         "Should equal sum of perf fees (no leakage)"),
        ("Difference (H+I+J+K+L − Perf Fee total)",
         f"=ROUND(B4-B3,2)",
         "Should be 0.00"),
        ("# investors with consultant = Unmapped",
         f'=COUNTIF(PI_Consultant, "Unmapped")',
         "Should be 0; if not, fix the IDS Mapping sheet"),
        ("Split % sanity (must equal 100%)",
         f"=Inputs!$B$11",
         "Sum of all five split percentages"),
    ]
    ws_r.cell(row=2, column=1, value="Check").font = Font(bold=True)
    ws_r.cell(row=2, column=2, value="Result").font = Font(bold=True)
    ws_r.cell(row=2, column=3, value="Notes").font = Font(bold=True)
    for i, (label, formula, note) in enumerate(checks, start=3):
        ws_r.cell(row=i, column=1, value=label)
        c = ws_r.cell(row=i, column=2, value=formula)
        if "$" in note or "TPA" in label or "Sum" in label:
            c.number_format = '"$"#,##0.00'
        ws_r.cell(row=i, column=3, value=note)

    ws_r.column_dimensions["A"].width = 50
    ws_r.column_dimensions["B"].width = 18
    ws_r.column_dimensions["C"].width = 60

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return {
        "investor_count": len(records),
        "unmapped": [r for r in records if r["consultant"] == "Unmapped"],
    }


# ---------------------------------------------------------------------------
# JSON builder (snapshot for the dashboard)
# ---------------------------------------------------------------------------

def build_json_snapshot(
    records: list[dict],
    tpa_record: dict,
    period_label: str,
    costs: list[dict],
) -> dict:
    """Compute static snapshot used by the dashboard."""
    total_perf = sum(r["perf_fee"] for r in records)
    total_costs = sum(c["amount"] for c in costs)

    # Per-consultant aggregation (computed values, not formulas)
    by_cons: dict[str, dict] = {}
    for r in records:
        bucket = by_cons.setdefault(r["consultant"], {
            "consultant": r["consultant"],
            "investor_count": 0,
            "capital_raised": 0.0,
            "gp_earned_consultant_cut": 0.0,
            "investors": [],
        })
        bucket["investor_count"] += 1
        bucket["capital_raised"] += r["ending_balance"]
        bucket["gp_earned_consultant_cut"] += r["perf_fee"] * SPLIT_PCTS["consultant"]
        bucket["investors"].append({
            "tpa_id": r["tpa_id"],
            "name": r["name"],
            "ending_balance": round(r["ending_balance"], 2),
            "gross_profit": round(r["gross_profit"], 2),
            "perf_fee": round(r["perf_fee"], 2),
            "consultant_cut": round(r["perf_fee"] * SPLIT_PCTS["consultant"], 2),
        })

    consultants = []
    for k, v in sorted(by_cons.items(), key=lambda kv: -kv[1]["gp_earned_consultant_cut"]):
        consultants.append({
            **v,
            "capital_raised": round(v["capital_raised"], 2),
            "gp_earned_consultant_cut": round(v["gp_earned_consultant_cut"], 2),
            "pct_of_gp_pool": round(v["gp_earned_consultant_cut"] / total_perf, 6) if total_perf else 0,
        })

    fund_mgmt_total = total_perf * SPLIT_PCTS["fund_mgmt"]
    fixed = {
        "raj": total_perf * SPLIT_PCTS["raj"],
        "nairne": total_perf * SPLIT_PCTS["nairne"],
        "alec_gp": total_perf * SPLIT_PCTS["alec"],
    }

    # Compute each party's % of GP pool, used to weight expense allocation.
    # Each consultant: their consultant_cut / total_perf
    # Fund Mgmt: 59.5%; Raj/Nairne fixed: 0.5% each; Alec (GP) fixed: 0.5%
    # NB: Alec Atkinson the consultant gets BOTH his consultant 39% and the
    # new GP-fixed 0.5% — these are separate buckets.
    pool_share = {}
    for c in consultants:
        pool_share[c["consultant"]] = c["pct_of_gp_pool"]
    pool_share["Fund Mgmt"] = SPLIT_PCTS["fund_mgmt"]
    pool_share["Raj (GP fixed)"] = SPLIT_PCTS["raj"]
    pool_share["Nairne (GP fixed)"] = SPLIT_PCTS["nairne"]
    pool_share["Alec (GP fixed)"] = SPLIT_PCTS["alec"]

    cost_allocation = [
        {"party": party, "pct_of_gp_pool": share, "allocated_expense": round(share * total_costs, 2)}
        for party, share in pool_share.items()
    ]

    bs = tpa_record.get("balance_sheet", {})
    inc = tpa_record.get("income_statement", {})
    fl = tpa_record.get("fund_level", {})

    return {
        "period": tpa_record["period"],
        "period_label": period_label,
        "as_of": tpa_record["as_of"],
        "split_pcts": SPLIT_PCTS,
        "fund_totals": {
            "tpa_gross_income": round(inc.get("total_income", 0), 2),
            "tpa_net_income": round(inc.get("net_income", 0), 2),
            "tpa_perf_fees_crystallized": round(total_perf, 2),
            "fund_mgmt_pool": round(fund_mgmt_total, 2),
            "consultants_pool": round(total_perf * SPLIT_PCTS["consultant"], 2),
            "raj_pool": round(fixed["raj"], 2),
            "nairne_pool": round(fixed["nairne"], 2),
            "alec_gp_pool": round(fixed["alec_gp"], 2),
            "investor_count": len(records),
            "unmapped_count": sum(1 for r in records if r["consultant"] == "Unmapped"),
            "ending_aum": round(bs.get("total_capital", 0), 2),
            "gross_mtd_ror": fl.get("gross_mtd_ror", 0),
            "net_mtd_ror": fl.get("net_mtd_ror", 0),
            "total_costs": round(total_costs, 2),
        },
        "consultants": consultants,
        "investors": [
            {
                "tpa_id": r["tpa_id"],
                "name": r["name"],
                "consultant": r["consultant"],
                "ending_balance": round(r["ending_balance"], 2),
                "gross_profit": round(r["gross_profit"], 2),
                "perf_fee": round(r["perf_fee"], 2),
                "fund_mgmt_cut": round(r["perf_fee"] * SPLIT_PCTS["fund_mgmt"], 2),
                "consultant_cut": round(r["perf_fee"] * SPLIT_PCTS["consultant"], 2),
                "raj_cut": round(r["perf_fee"] * SPLIT_PCTS["raj"], 2),
                "nairne_cut": round(r["perf_fee"] * SPLIT_PCTS["nairne"], 2),
                "alec_gp_cut": round(r["perf_fee"] * SPLIT_PCTS["alec"], 2),
            }
            for r in sorted(records, key=lambda x: -x["perf_fee"])
        ],
        "costs": {
            "total": round(total_costs, 2),
            "line_items": [
                {"name": c["name"], "amount": round(c["amount"], 2)}
                for c in costs
            ],
            "allocation_by_party": cost_allocation,
        },
    }


def upsert_json(snapshot: dict, json_path: Path = JSON_PATH) -> None:
    if json_path.exists():
        history = json.loads(json_path.read_text())
    else:
        history = {"fund": "Armada Prime LLP", "months": []}
    history["fund"] = "Armada Prime LLP"
    months = [m for m in history.get("months", []) if m.get("period") != snapshot["period"]]
    months.append(snapshot)
    months.sort(key=lambda m: m["period"])
    history["months"] = months
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(history, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tpa_xlsx", type=Path, nargs="?", default=DEFAULT_TPA,
                    help="Path to TPA Reporting Package xlsx")
    ap.add_argument("--internal", type=Path, default=DEFAULT_INTERNAL,
                    help="Path to internal Monthly Return xlsx (for IDS sheet)")
    ap.add_argument("--output-xlsx", type=Path, default=DEFAULT_OUTPUT_XLSX,
                    help="Where to write the dynamic Excel")
    ap.add_argument("--label", type=str, default=None, help="Override period_label")
    args = ap.parse_args()

    if not args.tpa_xlsx.exists():
        print(f"error: TPA file not found: {args.tpa_xlsx}", file=sys.stderr)
        return 1
    if not args.internal.exists():
        print(f"error: internal file not found: {args.internal}", file=sys.stderr)
        return 1

    print(f"Loading TPA package:  {args.tpa_xlsx.name}")
    tpa = parse_workbook(args.tpa_xlsx)
    print(f"  period={tpa['period']}  investors={len(tpa['investors'])}  perf_fees=${sum(i.get('perf_fee',0) for i in tpa['investors']):,.2f}")

    print(f"Loading internal IDS: {args.internal.name}")
    ids_map = load_ids(args.internal)
    print(f"  IDS rows: {len(ids_map)}  (incl. {len(CONSULTANT_OVERRIDES)} confirmed overrides)")

    records = reconcile(tpa["investors"], ids_map)
    unmapped = [r for r in records if r["consultant"] == "Unmapped"]
    print(f"Reconciled: {len(records)} investors, {len(unmapped)} unmapped")
    for u in unmapped:
        print(f"  UNMAPPED: {u['tpa_id']:22}  {u['name']}")

    costs = load_costs(args.internal)
    print(f"Costs: {len(costs)} line items, total ${sum(c['amount'] for c in costs):,.2f}")

    label = args.label or tpa["period_label"]
    summary = build_workbook(records, label, args.output_xlsx, costs)
    print(f"Wrote Excel: {args.output_xlsx}")

    snapshot = build_json_snapshot(records, tpa, label, costs)
    upsert_json(snapshot)
    print(f"Wrote JSON: {JSON_PATH}")

    print(f"\nGP pool ${snapshot['fund_totals']['tpa_perf_fees_crystallized']:,.2f}  →  "
          f"Fund Mgmt ${snapshot['fund_totals']['fund_mgmt_pool']:,.2f}  +  "
          f"Consultants ${snapshot['fund_totals']['consultants_pool']:,.2f}  +  "
          f"Raj/Nairne/Alec(GP) ${snapshot['fund_totals']['raj_pool']*3:,.2f}")
    print(f"Total costs: ${snapshot['fund_totals']['total_costs']:,.2f} (allocated pro-rata by GP %)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
