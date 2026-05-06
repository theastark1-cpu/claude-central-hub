# TIA-9.72 Walk-Forward Analytics Dashboard

Immersive single-page dashboard for the **TIA-9.72** systematic forex grid-trading
framework's 6-year walk-forward validation (2020–2025), overlaid against actual
historical price action for the same 10 pairs.

Bloomberg-Terminal-meets-pitch-deck: dark mode, monospace numerics, three-zone
layout, 3D-tilt cards, regime-detection overlays, drawdown replay, keyboard nav.

## Run it

```bash
cd tia-972-dashboard

# Phase 1 — data layer (already cached in data/)
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
python scripts/parse_pdf.py        # → data/strategy.json
python scripts/fetch_market.py     # → data/market/*.json

# Phase 2 — frontend
npm install
npm run dev    # → http://localhost:5173
```

The data is also mirrored into `public/data/` so the Vite dev server serves it
directly.

## Architecture

```
tia-972-dashboard/
├── data/                       # canonical data store
│   ├── source/                 # the original PDF
│   ├── strategy.json           # parsed walk-forward stats
│   └── market/<SYMBOL>.json    # daily OHLC per pair
├── public/data/                # mirror served by Vite dev/build
├── scripts/
│   ├── parse_pdf.py            # pdfplumber → strategy.json
│   ├── fetch_market.py         # yfinance → market/*.json
│   └── requirements.txt
├── src/
│   ├── App.tsx, main.tsx, types.ts
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── ZoneA/MacroGrid.tsx, PairCard.tsx
│   │   ├── ZoneB/TemporalArena.tsx, StackedReturnsChart.tsx,
│   │   │       PriceTimeline.tsx, YearScrubber.tsx
│   │   ├── ZoneC/Comparator.tsx
│   │   └── shared/{KPI,Section}.tsx
│   ├── hooks/{useStrategyData,useMarketData,useTilt,useKeyboardNav}.ts
│   ├── store/dashboard.ts      # Zustand: selected pair / year / view / replay
│   └── utils/
│       ├── stats.ts            # mean, stdev, sparkline, risk tier
│       ├── format.ts           # pct/pips formatting
│       ├── realityGap.ts       # strategy-vs-market per-year score
│       ├── validationScore.ts  # 0–100 robustness blend
│       └── regimeDetection.ts  # ATR + Bollinger → trending/ranging/vol bands
├── index.html, vite.config.ts, tsconfig.json
└── tailwind.config.js, postcss.config.js
```

## Three zones

- **Zone A · Macro Grid** — 10 pair cards. Each shows 6-year cumulative,
  average annual, peak DD, validation score, equity sparkline. Tier colour
  (green / yellow / red) = avg max DD bucket. Mouse-tilt 3D effect; hover
  expands to a year-by-year DD/return table. Click a DD% to replay that year.
- **Zone B · Temporal Arena** — left panel: stacked AreaChart of all 10 pairs'
  annual net profit, with a year scrubber. Right panel: real daily close for
  the selected pair, with regime bands (trending / ranging / high-vol /
  low-vol) and DD-intensity shading.
- **Zone C · Comparator** — Strategy radar vs. Market radar side-by-side, the
  validation score in the middle, and a per-year reality-gap table flagging
  every fold as **Alpha Generated**, **In-Line**, or **Regime Mismatch**.

## Interactions

- `← →` or `↑ ↓` — cycle pairs
- `Space` — toggle Strategy ↔ Market view
- Click a DD% inside any pair-card year row — animated drawdown replay
- Click the year-scrubber or any year tick — set selected year
- Hover any pair card — 3D tilt + expanded year breakdown

## Data sources

- **Strategy data**: parsed from `data/source/TIA-9.72_6yr_walkforward.pdf`
  with `pdfplumber`. 10 pairs × 6 years (2020–2025) = 60 rows. Columns: net
  profit, max drawdown, biggest grid (pips), avg DD per first trade, avg DD
  per sequence, max levels, total trades.
- **Market data**: daily OHLC from Yahoo Finance via `yfinance`,
  2020-01-01 → 2025-12-31. Tickers map symbol `XXXYYYX` → `XXXYYY=X`.

## Methodology

See [methodology.md](methodology.md) for the math behind risk tiers, regime
detection, the Reality Gap score, and the 0–100 Validation Score.

## Pairs covered

EURUSDX, NZDUSDX, EURCADX, USDCADX, AUDUSDX, AUDCADX, GBPCADX, NZDCADX,
GBPUSDX, AUDNZDX.

## Notes / out of scope

- Sound design (Web Audio drone) — deliberately not built.
- Three.js — not needed; CSS `transform3d` covers the tilt cleanly.
- No paid charting libraries (Recharts only).
- The drawdown replay distributes trade-count dots evenly across the 12-month
  window because the source PDF only carries yearly aggregates, not per-trade
  timestamps. Documented honestly in `methodology.md`.
