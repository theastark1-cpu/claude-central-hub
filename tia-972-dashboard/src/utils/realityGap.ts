import type { Candle, Pair, YearMarketStats } from "@/types";
import { clamp, mean, stdev } from "./stats";

const inYear = (date: string, year: number) => date.startsWith(String(year));

export const yearlyMarketStats = (
  pair: Pair,
  candles: Candle[],
): YearMarketStats[] => {
  return pair.years
    .slice()
    .sort((a, b) => a.year - b.year)
    .map((ys) => {
      const yearCandles = candles.filter(
        (c) => inYear(c.date, ys.year) && c.close != null,
      );
      if (yearCandles.length < 5) {
        return {
          year: ys.year,
          market_drift_pct: 0,
          market_vol_pct: 0,
          flag: "inline" as const,
          gap_score: 0,
        };
      }
      const start = yearCandles[0].close as number;
      const end = yearCandles[yearCandles.length - 1].close as number;
      const drift = ((end - start) / start) * 100;
      const logRets: number[] = [];
      for (let i = 1; i < yearCandles.length; i++) {
        const a = yearCandles[i - 1].close as number;
        const b = yearCandles[i].close as number;
        if (a > 0 && b > 0) logRets.push(Math.log(b / a));
      }
      const dailyStd = stdev(logRets);
      const vol = dailyStd * Math.sqrt(252) * 100;
      const ret = ys.net_profit_pct;
      let flag: YearMarketStats["flag"] = "inline";
      if (Math.abs(drift) < 3 && ret > 5) flag = "alpha";
      else if (Math.abs(drift) > 5 && ret < 2) flag = "mismatch";
      const gap = clamp(ret - 0.5 * vol, -10, 10);
      return {
        year: ys.year,
        market_drift_pct: drift,
        market_vol_pct: vol,
        flag,
        gap_score: gap,
      };
    });
};

export const meanMarketDrift = (s: YearMarketStats[]) =>
  mean(s.map((x) => Math.abs(x.market_drift_pct)));
export const meanMarketVol = (s: YearMarketStats[]) =>
  mean(s.map((x) => x.market_vol_pct));
