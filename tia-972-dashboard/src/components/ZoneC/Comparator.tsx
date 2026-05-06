import { useMemo } from "react";
import {
  ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";
import type { StrategyData } from "@/types";
import { Section } from "@/components/shared/Section";
import { useDashboard } from "@/store/dashboard";
import { useMarketData } from "@/hooks/useMarketData";
import { yearlyMarketStats } from "@/utils/realityGap";
import { validationScore, scoreColor, scoreLabel } from "@/utils/validationScore";
import { avgAnnualReturn, peakMaxDD, totalTrades, mean, clamp } from "@/utils/stats";
import { fmtPct, fmtPctNoSign, prettySymbol } from "@/utils/format";

export const Comparator = ({ data }: { data: StrategyData }) => {
  const selectedPair = useDashboard((s) => s.selectedPair);
  const pair = data.pairs.find((p) => p.symbol === selectedPair) ?? data.pairs[0];
  const { data: market } = useMarketData(pair.symbol);

  const marketStats = useMemo(
    () => (market ? yearlyMarketStats(pair, market.candles) : []),
    [pair, market],
  );

  const score = validationScore(pair);
  const scoreC = scoreColor(score);

  const avgRet = avgAnnualReturn(pair.years);
  const peak = peakMaxDD(pair.years);
  const trades = totalTrades(pair.years);
  const avgTradesYr = trades / pair.years.length;
  const gridResilience = mean(
    pair.years.map((y) => (y.biggest_grid_pips ? Math.min(y.biggest_grid_pips / 1000, 1) * 100 : 30)),
  );

  const realizedDrift = mean(marketStats.map((m) => Math.abs(m.market_drift_pct)));
  const realizedVol = mean(marketStats.map((m) => m.market_vol_pct));

  const strategyRow = {
    "Avg Return": clamp(avgRet * 8, 0, 100),
    "DD Discipline": clamp(100 - peak * 6, 0, 100),
    "Trade Frequency": clamp(avgTradesYr * 3, 0, 100),
    "Grid Resilience": clamp(gridResilience, 0, 100),
    "Vol Capture": clamp(avgRet / Math.max(realizedVol, 0.1) * 80, 0, 100),
  };
  const marketRow = {
    "Avg Return": clamp(realizedDrift * 6, 0, 100),
    "DD Discipline": clamp(100 - realizedVol * 4, 0, 100),
    "Trade Frequency": 50,
    "Grid Resilience": 50,
    "Vol Capture": clamp(realizedVol * 6, 0, 100),
  };

  const radarData = Object.keys(strategyRow).map((axis) => ({
    axis,
    Strategy: (strategyRow as Record<string, number>)[axis],
    Market: (marketRow as Record<string, number>)[axis],
  }));

  const flagCounts = marketStats.reduce(
    (acc, s) => ({ ...acc, [s.flag]: (acc[s.flag] ?? 0) + 1 }),
    { alpha: 0, mismatch: 0, inline: 0 } as Record<string, number>,
  );

  return (
    <Section
      eyebrow="Zone C · Comparator"
      title={`Reality gap · ${prettySymbol(pair.symbol)}`}
      subtitle="Strategy radar vs. market radar. The Reality Gap badge classifies each year as Alpha Generated, In-Line, or Regime Mismatch using realized drift and volatility from the live tape."
    >
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-4 rounded-xl border border-border bg-panel p-5">
          <div className="text-[10px] uppercase tracking-[0.18em] text-muted mb-3">Strategy</div>
          <ResponsiveContainer width="100%" height={260}>
            <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="axis" tick={{ fontSize: 10, fill: "#576574", fontFamily: "JetBrains Mono" }} />
              <PolarRadiusAxis stroke="rgba(255,255,255,0.05)" tick={false} axisLine={false} />
              <Radar
                name="Strategy"
                dataKey="Strategy"
                stroke="#00d084"
                fill="#00d084"
                fillOpacity={0.2}
                strokeWidth={1.5}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="col-span-12 lg:col-span-4 rounded-xl border border-border bg-panel p-5 flex flex-col items-center justify-center text-center">
          <div className="text-[10px] uppercase tracking-[0.18em] text-muted">Validation Score</div>
          <div
            className="mono text-7xl font-semibold mt-2"
            style={{ color: scoreC, textShadow: `0 0 30px ${scoreC}40` }}
          >
            {score}
          </div>
          <div className="text-sm mono mt-1" style={{ color: scoreC }}>{scoreLabel(score)}</div>
          <div className="grid grid-cols-3 gap-3 mt-6 w-full">
            <FlagCount label="Alpha" v={flagCounts.alpha} c="#00d084" />
            <FlagCount label="In-line" v={flagCounts.inline} c="#576574" />
            <FlagCount label="Mismatch" v={flagCounts.mismatch} c="#ff4757" />
          </div>
          <div className="mt-6 grid grid-cols-2 gap-3 w-full text-[11px] mono">
            <div className="rounded-md border border-border p-3">
              <div className="text-muted text-[10px] uppercase tracking-wider">Strat avg/yr</div>
              <div className="text-profit text-base mt-1">{fmtPct(avgRet, 2)}</div>
            </div>
            <div className="rounded-md border border-border p-3">
              <div className="text-muted text-[10px] uppercase tracking-wider">Realized vol</div>
              <div className="text-fg text-base mt-1">{fmtPctNoSign(realizedVol, 2)}</div>
            </div>
          </div>
        </div>

        <div className="col-span-12 lg:col-span-4 rounded-xl border border-border bg-panel p-5">
          <div className="text-[10px] uppercase tracking-[0.18em] text-muted mb-3">Market</div>
          <ResponsiveContainer width="100%" height={260}>
            <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="axis" tick={{ fontSize: 10, fill: "#576574", fontFamily: "JetBrains Mono" }} />
              <PolarRadiusAxis stroke="rgba(255,255,255,0.05)" tick={false} axisLine={false} />
              <Radar
                name="Market"
                dataKey="Market"
                stroke="#feca57"
                fill="#feca57"
                fillOpacity={0.18}
                strokeWidth={1.5}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="col-span-12 rounded-xl border border-border bg-panel p-5">
          <div className="text-[10px] uppercase tracking-[0.18em] text-muted mb-3">
            Per-year reality gap
          </div>
          <table className="w-full mono text-xs">
            <thead className="text-muted text-[10px]">
              <tr>
                <th className="text-left font-normal py-1">YEAR</th>
                <th className="text-right font-normal">STRAT RET</th>
                <th className="text-right font-normal">MKT DRIFT</th>
                <th className="text-right font-normal">MKT VOL</th>
                <th className="text-right font-normal">GAP</th>
                <th className="text-right font-normal">FLAG</th>
              </tr>
            </thead>
            <tbody>
              {marketStats.map((m) => {
                const ys = pair.years.find((y) => y.year === m.year)!;
                const flagColor =
                  m.flag === "alpha" ? "#00d084" : m.flag === "mismatch" ? "#ff4757" : "#576574";
                const flagText =
                  m.flag === "alpha" ? "ALPHA" : m.flag === "mismatch" ? "MISMATCH" : "IN-LINE";
                return (
                  <tr key={m.year} className="border-t border-border/60">
                    <td className="py-2">{m.year}</td>
                    <td className="text-right text-profit">{fmtPctNoSign(ys.net_profit_pct)}</td>
                    <td className="text-right" style={{ color: m.market_drift_pct >= 0 ? "#00d084" : "#ff4757" }}>
                      {fmtPct(m.market_drift_pct, 2)}
                    </td>
                    <td className="text-right text-fg">{fmtPctNoSign(m.market_vol_pct, 2)}</td>
                    <td className="text-right" style={{ color: m.gap_score >= 0 ? "#00d084" : "#ff4757" }}>
                      {fmtPct(m.gap_score, 2)}
                    </td>
                    <td className="text-right">
                      <span
                        className="px-2 py-0.5 rounded-full text-[10px]"
                        style={{ backgroundColor: `${flagColor}1f`, color: flagColor }}
                      >
                        {flagText}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </Section>
  );
};

const FlagCount = ({ label, v, c }: { label: string; v: number; c: string }) => (
  <div className="rounded-md border border-border p-2 text-center">
    <div className="mono text-2xl" style={{ color: c }}>{v}</div>
    <div className="text-[10px] uppercase tracking-wider text-muted mt-1">{label}</div>
  </div>
);
