import { useDashboard } from "@/store/dashboard";
import type { StrategyData } from "@/types";
import { mean } from "@/utils/stats";

export const Header = ({ data }: { data: StrategyData }) => {
  const viewMode = useDashboard((s) => s.viewMode);

  const allReturns = data.pairs.flatMap((p) => p.years.map((y) => y.net_profit_pct));
  const allDDs = data.pairs.flatMap((p) => p.years.map((y) => y.max_drawdown_pct));
  const totalTrades = data.pairs.reduce(
    (a, p) => a + p.years.reduce((b, y) => b + y.trades, 0),
    0,
  );

  return (
    <header className="px-6 lg:px-10 pt-8 pb-6">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3">
            <span className="ticker-pulse w-2 h-2 rounded-full bg-profit shadow-[0_0_10px_#00d084]" />
            <span className="text-[10px] uppercase tracking-[0.32em] text-muted mono">
              Walk-Forward Validation · Live · {viewMode}
            </span>
          </div>
          <h1 className="mt-2 text-4xl lg:text-5xl font-semibold tracking-tight">
            <span className="mono text-accent">{data.framework}</span>
            <span className="text-fg/80"> · 6-year fold engine</span>
          </h1>
          <p className="mt-2 text-sm text-muted max-w-2xl">
            {data.title} · 10 forex pairs · {data.period.start.slice(0,4)}–{data.period.end.slice(0,4)} · 6 sequential out-of-sample folds.
          </p>
        </div>

        <div className="flex items-end gap-8">
          <Stat label="Pairs" value={String(data.pairs.length)} />
          <Stat label="Avg yr ret" value={`${mean(allReturns).toFixed(2)}%`} tone="profit" />
          <Stat label="Avg max DD" value={`${mean(allDDs).toFixed(2)}%`} tone="loss" />
          <Stat label="Trades" value={totalTrades.toLocaleString()} />
        </div>
      </div>
    </header>
  );
};

const Stat = ({ label, value, tone }: { label: string; value: string; tone?: "profit" | "loss" }) => (
  <div>
    <div className="text-[10px] uppercase tracking-[0.18em] text-muted">{label}</div>
    <div
      className={`mono text-2xl mt-1 ${tone === "profit" ? "text-profit" : tone === "loss" ? "text-loss" : "text-fg"}`}
    >
      {value}
    </div>
  </div>
);
