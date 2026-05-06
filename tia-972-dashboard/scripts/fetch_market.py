#!/usr/bin/env python3
"""
Fetch daily OHLC for all 10 forex pairs from Yahoo Finance via yfinance.

Output: data/market/<SYMBOL>.json (one file per pair).

Re-runs are no-op when the file exists, unless --force is passed.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
STRATEGY_PATH = ROOT / "data" / "strategy.json"
MARKET_DIR = ROOT / "data" / "market"

START = "2020-01-01"
END = "2025-12-31"


def fetch_one(symbol: str, ticker: str, force: bool) -> dict:
    out_path = MARKET_DIR / f"{symbol}.json"
    if out_path.exists() and not force:
        existing = json.loads(out_path.read_text())
        return {"symbol": symbol, "candles": len(existing.get("candles", [])), "cached": True}

    df = yf.download(
        ticker, start=START, end=END, interval="1d",
        progress=False, auto_adjust=False,
    )
    if df.empty:
        raise RuntimeError(f"No data returned for {ticker}")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index().rename(columns=str.lower)

    candles = []
    for _, row in df.iterrows():
        date = row["date"]
        if hasattr(date, "strftime"):
            date_str = date.strftime("%Y-%m-%d")
        else:
            date_str = str(date)[:10]
        candles.append({
            "date": date_str,
            "open": _safe(row.get("open")),
            "high": _safe(row.get("high")),
            "low": _safe(row.get("low")),
            "close": _safe(row.get("close")),
            "volume": _safe(row.get("volume"), is_int=True),
        })

    payload = {"symbol": symbol, "ticker": ticker, "start": START, "end": END,
               "candles": candles}
    out_path.write_text(json.dumps(payload))
    return {"symbol": symbol, "candles": len(candles), "cached": False}


def _safe(v, is_int: bool = False):
    if v is None or pd.isna(v):
        return None
    return int(v) if is_int else float(v)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Refetch even if cached")
    args = parser.parse_args()

    if not STRATEGY_PATH.exists():
        print(f"strategy.json missing — run parse_pdf.py first", file=sys.stderr)
        return 1
    strategy = json.loads(STRATEGY_PATH.read_text())
    pairs = strategy["pairs"]

    MARKET_DIR.mkdir(parents=True, exist_ok=True)

    for p in pairs:
        try:
            res = fetch_one(p["symbol"], p["yahoo_ticker"], args.force)
            tag = "cached" if res["cached"] else "fetched"
            print(f"  {p['symbol']:<10} {p['yahoo_ticker']:<10} {res['candles']:>5} candles ({tag})")
        except Exception as e:
            print(f"  {p['symbol']:<10} FAILED: {e}", file=sys.stderr)
            return 2
        if not res["cached"]:
            time.sleep(0.3)  # be polite

    print(f"Market data in {MARKET_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
