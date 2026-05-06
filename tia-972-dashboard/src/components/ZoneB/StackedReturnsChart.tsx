import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
} from "recharts";
import type { StrategyData } from "@/types";
import { useDashboard } from "@/store/dashboard";
import { tierColor, riskTier } from "@/utils/stats";

export const StackedReturnsChart = ({ data }: { data: StrategyData }) => {
  const selectedYear = useDashboard((s) => s.selectedYear);
  const selectedPair = useDashboard((s) => s.selectedPair);

  const years = [2020, 2021, 2022, 2023, 2024, 2025];
  const rows = years.map((yr) => {
    const row: Record<string, number | string> = { year: yr };
    for (const p of data.pairs) {
      const y = p.years.find((x) => x.year === yr);
      row[p.symbol] = y ? y.net_profit_pct : 0;
    }
    return row;
  });

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={rows} margin={{ top: 16, right: 16, left: 0, bottom: 0 }}>
        <defs>
          {data.pairs.map((p) => {
            const c = tierColor(riskTier(p.years));
            const isSel = p.symbol === selectedPair;
            return (
              <linearGradient key={p.symbol} id={`fill-${p.symbol}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={c} stopOpacity={isSel ? 0.55 : 0.18} />
                <stop offset="100%" stopColor={c} stopOpacity={0} />
              </linearGradient>
            );
          })}
        </defs>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" />
        <XAxis
          dataKey="year"
          stroke="#576574"
          tick={{ fontSize: 11, fontFamily: "JetBrains Mono" }}
          axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
        />
        <YAxis
          stroke="#576574"
          tick={{ fontSize: 11, fontFamily: "JetBrains Mono" }}
          axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
          tickFormatter={(v) => `${v}%`}
        />
        <ReferenceLine x={selectedYear} stroke="#feca57" strokeDasharray="3 3" />
        <Tooltip
          contentStyle={{
            background: "#16161f",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 8,
            fontSize: 11,
            fontFamily: "JetBrains Mono",
          }}
          labelStyle={{ color: "#feca57" }}
          formatter={(v: number, name: string) => [`${v.toFixed(2)}%`, name]}
        />
        {data.pairs.map((p) => {
          const c = tierColor(riskTier(p.years));
          const isSel = p.symbol === selectedPair;
          return (
            <Area
              key={p.symbol}
              type="monotone"
              dataKey={p.symbol}
              stackId="1"
              stroke={c}
              strokeOpacity={isSel ? 1 : 0.45}
              strokeWidth={isSel ? 2 : 1}
              fill={`url(#fill-${p.symbol})`}
            />
          );
        })}
      </AreaChart>
    </ResponsiveContainer>
  );
};
