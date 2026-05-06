import type { Pair } from "@/types";
import { clamp, mean, stdev } from "./stats";

export const validationScore = (pair: Pair): number => {
  const rets = pair.years.map((y) => y.net_profit_pct);
  const dds = pair.years.map((y) => y.max_drawdown_pct);
  const trs = pair.years.map((y) => y.trades);

  const mRet = mean(rets);
  const consistency = clamp(1 - stdev(rets) / Math.max(mRet, 0.01), 0, 1);
  const ddDiscipline = clamp(1 - Math.max(...dds) / 15, 0, 1);
  const tradeStability = clamp(1 - stdev(trs) / Math.max(mean(trs), 1), 0, 1);
  const profitability = clamp(mRet / 10, 0, 1);

  return Math.round(
    100 * (0.4 * consistency + 0.3 * ddDiscipline + 0.15 * tradeStability + 0.15 * profitability),
  );
};

export const scoreLabel = (s: number) =>
  s >= 80 ? "Robust" : s >= 65 ? "Solid" : s >= 50 ? "Mixed" : "Fragile";

export const scoreColor = (s: number) =>
  s >= 80 ? "#00d084" : s >= 65 ? "#7ec9a3" : s >= 50 ? "#feca57" : "#ff4757";
