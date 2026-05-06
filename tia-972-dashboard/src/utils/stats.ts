import type { Pair, YearStat, RiskTier } from "@/types";

export const mean = (xs: number[]): number =>
  xs.length === 0 ? 0 : xs.reduce((a, b) => a + b, 0) / xs.length;

export const stdev = (xs: number[]): number => {
  if (xs.length < 2) return 0;
  const m = mean(xs);
  const v = xs.reduce((acc, x) => acc + (x - m) ** 2, 0) / (xs.length - 1);
  return Math.sqrt(v);
};

export const clamp = (v: number, lo: number, hi: number) =>
  Math.max(lo, Math.min(hi, v));

export const cumulativeReturnPct = (years: YearStat[]): number => {
  let eq = 1;
  for (const y of [...years].sort((a, b) => a.year - b.year)) {
    eq *= 1 + y.net_profit_pct / 100;
  }
  return (eq - 1) * 100;
};

export const equityCurve = (years: YearStat[]): { year: number; equity: number }[] => {
  let eq = 1;
  const sorted = [...years].sort((a, b) => a.year - b.year);
  const out: { year: number; equity: number }[] = [
    { year: sorted[0].year - 1, equity: 1 },
  ];
  for (const y of sorted) {
    eq *= 1 + y.net_profit_pct / 100;
    out.push({ year: y.year, equity: eq });
  }
  return out;
};

export const avgMaxDD = (years: YearStat[]): number =>
  mean(years.map((y) => y.max_drawdown_pct));

export const peakMaxDD = (years: YearStat[]): number =>
  Math.max(...years.map((y) => y.max_drawdown_pct));

export const avgAnnualReturn = (years: YearStat[]): number =>
  mean(years.map((y) => y.net_profit_pct));

export const totalTrades = (years: YearStat[]): number =>
  years.reduce((a, y) => a + y.trades, 0);

export const riskTier = (years: YearStat[]): RiskTier => {
  const avg = avgMaxDD(years);
  if (avg < 5) return "green";
  if (avg <= 10) return "yellow";
  return "red";
};

export const tierColor = (tier: RiskTier) =>
  tier === "green" ? "#00d084" : tier === "yellow" ? "#feca57" : "#ff4757";

export const sparklinePath = (
  years: YearStat[],
  width: number,
  height: number,
  pad = 2,
): { path: string; lastX: number; lastY: number } => {
  const eq = equityCurve(years);
  const xs = eq.map((p) => p.year);
  const ys = eq.map((p) => p.equity);
  const xMin = Math.min(...xs);
  const xMax = Math.max(...xs);
  const yMin = Math.min(...ys);
  const yMax = Math.max(...ys);
  const xR = xMax - xMin || 1;
  const yR = yMax - yMin || 1;
  const px = (x: number) => pad + ((x - xMin) / xR) * (width - 2 * pad);
  const py = (y: number) => height - pad - ((y - yMin) / yR) * (height - 2 * pad);
  const path = eq
    .map((p, i) => `${i === 0 ? "M" : "L"}${px(p.year).toFixed(2)},${py(p.equity).toFixed(2)}`)
    .join(" ");
  const last = eq[eq.length - 1];
  return { path, lastX: px(last.year), lastY: py(last.equity) };
};

export const orderedYears = (p: Pair): YearStat[] =>
  [...p.years].sort((a, b) => a.year - b.year);
