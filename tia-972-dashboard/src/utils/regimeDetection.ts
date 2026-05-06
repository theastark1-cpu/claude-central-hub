import type { Candle, RegimeLabel } from "@/types";

const sma = (xs: number[], i: number, n: number): number | null => {
  if (i < n - 1) return null;
  let s = 0;
  for (let k = i - n + 1; k <= i; k++) s += xs[k];
  return s / n;
};

const stdev = (xs: number[], i: number, n: number, mean: number): number | null => {
  if (i < n - 1) return null;
  let s = 0;
  for (let k = i - n + 1; k <= i; k++) s += (xs[k] - mean) ** 2;
  return Math.sqrt(s / n);
};

export interface RegimeBand {
  startDate: string;
  endDate: string;
  label: RegimeLabel;
}

export const detectRegimes = (candles: Candle[]): RegimeBand[] => {
  const valid = candles.filter((c) => c.close != null) as Required<Candle>[];
  if (valid.length < 30) return [];
  const closes = valid.map((c) => c.close as number);
  const highs = valid.map((c) => c.high as number);
  const lows = valid.map((c) => c.low as number);

  // True Range
  const tr: number[] = [0];
  for (let i = 1; i < valid.length; i++) {
    const prevClose = closes[i - 1];
    tr.push(
      Math.max(
        highs[i] - lows[i],
        Math.abs(highs[i] - prevClose),
        Math.abs(lows[i] - prevClose),
      ),
    );
  }
  const atr14: (number | null)[] = tr.map((_, i) => sma(tr, i, 14));

  const labels: RegimeLabel[] = valid.map((_, i) => {
    const m = sma(closes, i, 20);
    const sd = m == null ? null : stdev(closes, i, 20, m);
    const atr = atr14[i];
    if (m == null || sd == null || atr == null) return "ranging";
    const dev = Math.abs(closes[i] - m);
    const trending = dev > 1.5 * sd;
    const atrPct = atr / closes[i];
    // crude vol bands
    if (atrPct > 0.0085) return trending ? "trending" : "high-vol";
    if (atrPct < 0.004) return "low-vol";
    return trending ? "trending" : "ranging";
  });

  // Compress to bands of ~3 month windows by mode
  const bands: RegimeBand[] = [];
  const winSize = 63; // ~3 months trading days
  for (let i = 0; i < labels.length; i += winSize) {
    const slice = labels.slice(i, i + winSize);
    if (slice.length < 5) continue;
    const counts: Record<string, number> = {};
    slice.forEach((l) => (counts[l] = (counts[l] ?? 0) + 1));
    const dominant = Object.entries(counts).sort(
      (a, b) => b[1] - a[1],
    )[0][0] as RegimeLabel;
    bands.push({
      startDate: valid[i].date,
      endDate: valid[Math.min(i + winSize - 1, valid.length - 1)].date,
      label: dominant,
    });
  }
  return bands;
};

export const regimeColor = (l: RegimeLabel) =>
  l === "trending"
    ? "rgba(0, 208, 132, 0.10)"
    : l === "high-vol"
    ? "rgba(255, 71, 87, 0.10)"
    : l === "low-vol"
    ? "rgba(254, 202, 87, 0.06)"
    : "rgba(87, 101, 116, 0.06)";
