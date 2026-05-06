import { useMemo } from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceArea,
} from "recharts";
import type { Pair, MarketData } from "@/types";
import { detectRegimes, regimeColor } from "@/utils/regimeDetection";
import { useDashboard } from "@/store/dashboard";

interface Props {
  pair: Pair;
  market: MarketData;
}

export const PriceTimeline = ({ pair, market }: Props) => {
  const replay = useDashboard((s) => s.replay);

  const data = useMemo(
    () =>
      market.candles
        .filter((c) => c.close != null)
        .map((c) => ({ date: c.date, close: c.close as number, t: new Date(c.date).getTime() })),
    [market],
  );

  const regimes = useMemo(() => detectRegimes(market.candles), [market]);

  const ddBands = useMemo(() => {
    return pair.years.map((y) => {
      const intensity = Math.min(y.max_drawdown_pct / 14, 1);
      return {
        x1: `${y.year}-01-01`,
        x2: `${y.year}-12-31`,
        opacity: 0.06 + 0.18 * intensity,
        dd: y.max_drawdown_pct,
      };
    });
  }, [pair]);

  const isReplaying = replay && replay.pair === pair.symbol;
  const displayed = useMemo(() => {
    if (!isReplaying) return data;
    return data.filter((d) => d.date.startsWith(String(replay!.year)));
  }, [data, isReplaying, replay]);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={displayed} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" />
        <XAxis
          dataKey="date"
          type="category"
          stroke="#576574"
          tick={{ fontSize: 11, fontFamily: "JetBrains Mono" }}
          axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
          interval="preserveStartEnd"
          minTickGap={60}
          tickFormatter={(d: string) => (typeof d === "string" ? d.slice(0, 7) : "")}
        />
        <YAxis
          stroke="#576574"
          tick={{ fontSize: 11, fontFamily: "JetBrains Mono" }}
          axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
          domain={["auto", "auto"]}
          tickFormatter={(v: number) => v.toFixed(4)}
          width={70}
        />
        {regimes.map((r, i) => (
          <ReferenceArea
            key={`reg-${i}`}
            x1={r.startDate}
            x2={r.endDate}
            fill={regimeColor(r.label)}
            fillOpacity={1}
            ifOverflow="extendDomain"
          />
        ))}
        {ddBands.map((b, i) => (
          <ReferenceArea
            key={`dd-${i}`}
            x1={b.x1}
            x2={b.x2}
            fill="#ff4757"
            fillOpacity={b.opacity}
            ifOverflow="extendDomain"
          />
        ))}
        <Tooltip
          contentStyle={{
            background: "#16161f",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 8,
            fontSize: 11,
            fontFamily: "JetBrains Mono",
          }}
          labelStyle={{ color: "#feca57" }}
          formatter={(v: number) => [v.toFixed(5), "close"]}
        />
        <Line
          type="monotone"
          dataKey="close"
          stroke="#e8e9ee"
          strokeWidth={1.4}
          dot={false}
          isAnimationActive={Boolean(isReplaying)}
          animationDuration={isReplaying ? 2500 : 600}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
