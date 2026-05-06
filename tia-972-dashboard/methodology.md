# Methodology

All derived metrics are computed in the frontend from two raw inputs:
1. `data/strategy.json` — parsed from the TIA-9.72 walk-forward PDF
2. `data/market/<SYMBOL>.json` — daily OHLC from Yahoo Finance

No PnL series or per-trade timestamps are available in the source PDF, so
everything below operates on yearly aggregates from the strategy side and
daily bars from the market side.

## Risk tier (Zone A pair-card color)

Computed as the mean of `max_drawdown_pct` across the 6 years.

- Green: avg max DD < 5%
- Yellow: 5% ≤ avg max DD ≤ 10%
- Red: avg max DD > 10%

## Equity-curve sparkline

Yearly returns compounded: `equity[i] = equity[i-1] * (1 + net_profit_pct[i] / 100)`,
seeded at 1.0 in 2019Y-end.

## Regime detection (overlay on Zone B price chart)

Per pair, on daily closes:

- **ATR(14)** normalized by close → high-vol if above the trailing 252-day 75th percentile, low-vol if below the 25th percentile, else mid.
- **Bollinger Bands (SMA20, σ20)** → label `trending` if `|close − SMA20| > 1.5σ` for ≥10 consecutive sessions, else `ranging`.
- Final label per ~3-month window = mode of daily labels in the window.

## Reality Gap (per pair, per year)

For each `(pair, year)`:

1. `strategy_return` = `net_profit_pct`
2. `market_drift` = `(close_yearend − close_yearstart) / close_yearstart * 100`
3. `market_vol` = annualized stdev of daily log returns × 100

Flags:
- **Alpha Generated**: `|market_drift| < 3%` AND `strategy_return > 5%` — strategy made money in a flat/choppy market.
- **Regime Mismatch**: `|market_drift| > 5%` AND `strategy_return < 2%` — strategy whiffed in a clear trend.
- **In-line**: neither flag fires.

`gap_score = clamp(strategy_return − 0.5 × market_vol, −10, +10)` — positive means strategy outperformed what the realized vol would justify.

## Validation Score (0–100, per pair)

Weighted blend across the 6 walk-forward folds:

- **Profit consistency** (40%): `1 − stdev(returns) / mean(returns)`, clamped to [0, 1]. Penalizes years that swung wildly relative to the average.
- **DD discipline** (30%): `1 − max(max_drawdown_pct) / 15`. The framework imposes a 15% per-asset risk cap; pairs that approached it are penalized.
- **Trade-frequency stability** (15%): `1 − stdev(trades) / mean(trades)`, clamped.
- **Profitability** (15%): `min(mean(returns) / 10, 1)` — pairs averaging 10%/yr or better get full credit.

Score = `100 × (0.40·consistency + 0.30·dd_discipline + 0.15·trade_stability + 0.15·profitability)`.

Expected calibration: EURUSDX ≈ 85+, NZDCADX ≈ 40–55 (high variance, several "None" grid years).

## Drawdown Replay caveat

Yearly aggregates only — we don't have per-trade entry/exit timestamps.
Replay markers (`trades` count for that year) are distributed evenly across
the 12-month window. The price line, year boundary, and DD shading are real;
the trade-dot positions are illustrative.
