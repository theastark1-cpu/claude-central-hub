#!/usr/bin/env python3
"""
Parse the TIA-9.72 walk-forward PDF into a structured JSON file.

Input:  data/source/TIA-9.72_6yr_walkforward.pdf
Output: data/strategy.json

The PDF contains 10 per-pair tables, each with 6 yearly rows (2020-2025) and
columns: Year, Net Profit, Max Drawdown, Biggest Grid, Avg DD / First Trade,
Avg DD / Sequence, Max Levels, Trades.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / "data" / "source" / "TIA-9.72_6yr_walkforward.pdf"
OUT_PATH = ROOT / "data" / "strategy.json"

EXPECTED_PAIRS = [
    "EURUSDX", "NZDUSDX", "EURCADX", "USDCADX", "AUDUSDX",
    "AUDCADX", "GBPCADX", "NZDCADX", "GBPUSDX", "AUDNZDX",
]

# Map our symbol (with trailing X like Yahoo's =X tickers) to the actual yfinance ticker.
YAHOO_TICKER = {sym: f"{sym[:-1]}=X" for sym in EXPECTED_PAIRS}

PAIR_HEADER_RE = re.compile(r"^([A-Z]{6}X)$")


def _to_float_pct(s: str) -> float | None:
    s = s.strip()
    if s in ("", "None", "-", "—"):
        return None
    return float(s.rstrip("%"))


def _to_float(s: str) -> float | None:
    s = s.strip()
    if s in ("", "None", "-", "—"):
        return None
    return float(s)


def _to_int(s: str) -> int | None:
    s = s.strip()
    if s in ("", "None", "-", "—"):
        return None
    return int(s)


def parse_pdf(pdf_path: Path) -> dict:
    """Walk every page, find pair-name headings, and parse the table that follows.

    pdfplumber's `extract_tables` already returns the tables on each page in
    reading order, paired with their bounding boxes. We map them back to the
    nearest pair-name heading by looking for the symbol in the page text.
    """
    pairs: list[dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            # Pair headings appear on their own line.
            page_pairs = [
                line.strip()
                for line in text.splitlines()
                if PAIR_HEADER_RE.match(line.strip())
            ]
            tables = page.extract_tables()

            if len(page_pairs) != len(tables):
                # Some pages may have a Conclusion text block w/o a table.
                # Trim from the right (tables come in reading order).
                tables = tables[: len(page_pairs)]

            for symbol, table in zip(page_pairs, tables):
                rows = _parse_table(table)
                pairs.append({
                    "symbol": symbol,
                    "yahoo_ticker": YAHOO_TICKER.get(symbol, f"{symbol[:-1]}=X"),
                    "years": rows,
                })

    # Validate
    found_symbols = [p["symbol"] for p in pairs]
    missing = [s for s in EXPECTED_PAIRS if s not in found_symbols]
    if missing:
        raise RuntimeError(f"Missing pairs in parsed output: {missing}")
    for p in pairs:
        if len(p["years"]) != 6:
            raise RuntimeError(f"{p['symbol']} has {len(p['years'])} year-rows, expected 6")

    # Re-order to match EXPECTED_PAIRS
    by_sym = {p["symbol"]: p for p in pairs}
    pairs_ordered = [by_sym[s] for s in EXPECTED_PAIRS]

    return {
        "framework": "TIA-9.72",
        "title": "6-Year Walk Forward Validation",
        "period": {"start": "2020-01-01", "end": "2025-01-01"},
        "pairs": pairs_ordered,
    }


def _parse_table(table: list[list[str | None]]) -> list[dict]:
    """Convert a raw pdfplumber table into a list of typed year-row dicts.

    Expected header order:
      Year, Net Profit, Max Drawdown, Biggest Grid,
      Avg DD / First Trade, Avg DD / Sequence, Max Levels, Trades
    """
    rows: list[dict] = []
    for raw_row in table:
        if not raw_row or not raw_row[0]:
            continue
        cells = [(c or "").strip() for c in raw_row]
        year_str = cells[0]
        if not year_str.isdigit() or len(year_str) != 4:
            continue  # skip header / blank rows
        rows.append({
            "year": int(year_str),
            "net_profit_pct": _to_float_pct(cells[1]),
            "max_drawdown_pct": _to_float_pct(cells[2]),
            "biggest_grid_pips": _to_float(cells[3]),
            "avg_dd_first_trade_pct": _to_float_pct(cells[4]),
            "avg_dd_sequence_pct": _to_float_pct(cells[5]),
            "max_levels": _to_int(cells[6]),
            "trades": _to_int(cells[7]),
        })
    # Years descending in the PDF; sort ascending for downstream convenience.
    rows.sort(key=lambda r: r["year"])
    return rows


def main() -> int:
    if not PDF_PATH.exists():
        print(f"PDF not found at {PDF_PATH}", file=sys.stderr)
        return 1
    data = parse_pdf(PDF_PATH)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, indent=2))
    n_rows = sum(len(p["years"]) for p in data["pairs"])
    print(f"Wrote {OUT_PATH} | {len(data['pairs'])} pairs | {n_rows} year-rows")
    # Spot-check
    eur = next(p for p in data["pairs"] if p["symbol"] == "EURUSDX")
    y2020 = next(y for y in eur["years"] if y["year"] == 2020)
    print(f"Spot check EURUSDX 2020: net_profit={y2020['net_profit_pct']}% "
          f"max_dd={y2020['max_drawdown_pct']}% trades={y2020['trades']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
