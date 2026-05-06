import type { StrategyData } from "@/types";
import { Section } from "@/components/shared/Section";
import { useDashboard } from "@/store/dashboard";
import { useMarketData } from "@/hooks/useMarketData";
import { StackedReturnsChart } from "./StackedReturnsChart";
import { PriceTimeline } from "./PriceTimeline";
import { YearScrubber } from "./YearScrubber";
import { fmtPctNoSign, prettySymbol } from "@/utils/format";

export const TemporalArena = ({ data }: { data: StrategyData }) => {
  const selectedPair = useDashboard((s) => s.selectedPair);
  const selectedYear = useDashboard((s) => s.selectedYear);
  const viewMode = useDashboard((s) => s.viewMode);
  const replay = useDashboard((s) => s.replay);
  const clearReplay = useDashboard((s) => s.clearReplay);

  const pair = data.pairs.find((p) => p.symbol === selectedPair) ?? data.pairs[0];
  const yearStat = pair.years.find((y) => y.year === selectedYear);
  const { data: market, loading } = useMarketData(pair.symbol);

  return (
    <Section
      eyebrow="Zone B · Temporal Arena"
      title="Strategy claim vs. live tape"
      subtitle="Top: stacked annual net profit across all 10 pairs. Bottom: actual price for the selected pair, shaded by detected regime + drawdown intensity. Drag the scrubber or use ← → to cycle pairs. Spacebar toggles Strategy ↔ Market view."
      right={
        <div className="flex items-center gap-3">
          <span className="mono text-[11px] text-muted">VIEW</span>
          <span
            className="mono text-[11px] px-2 py-1 rounded-md border border-border"
            style={{ color: viewMode === "strategy" ? "#feca57" : "#e8e9ee" }}
          >
            {viewMode.toUpperCase()}
          </span>
          {replay && (
            <button
              onClick={clearReplay}
              className="mono text-[11px] px-2 py-1 rounded-md border border-loss/40 text-loss hover:bg-loss/10"
            >
              EXIT REPLAY · {replay.year}
            </button>
          )}
        </div>
      }
    >
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-7 rounded-xl border border-border bg-panel p-5">
          <Header label="Annual net profit · all pairs (stacked)" />
          <StackedReturnsChart data={data} />
          <div className="mt-3">
            <YearScrubber />
          </div>
        </div>
        <div className="col-span-12 xl:col-span-5 rounded-xl border border-border bg-panel p-5">
          <Header
            label={`${prettySymbol(pair.symbol)} · daily close (real)`}
            right={
              yearStat ? (
                <span className="mono text-[11px]">
                  <span className="text-muted">{selectedYear} · </span>
                  <span className="text-profit">{fmtPctNoSign(yearStat.net_profit_pct)}</span>
                  <span className="text-muted"> / </span>
                  <span className="text-loss">DD {fmtPctNoSign(yearStat.max_drawdown_pct)}</span>
                </span>
              ) : null
            }
          />
          {loading ? (
            <div className="h-[300px] flex items-center justify-center text-muted text-sm">Loading market data…</div>
          ) : market ? (
            <PriceTimeline pair={pair} market={market} />
          ) : (
            <div className="h-[300px] flex items-center justify-center text-loss text-sm">No market data</div>
          )}
          <RegimeLegend />
        </div>
      </div>
    </Section>
  );
};

const Header = ({ label, right }: { label: string; right?: React.ReactNode }) => (
  <div className="flex items-center justify-between mb-3">
    <span className="text-[10px] uppercase tracking-[0.18em] text-muted">{label}</span>
    {right}
  </div>
);

const RegimeLegend = () => (
  <div className="mt-3 flex flex-wrap items-center gap-3 text-[10px] mono text-muted">
    <Swatch color="rgba(0, 208, 132, 0.35)" label="trending" />
    <Swatch color="rgba(255, 71, 87, 0.35)" label="high-vol" />
    <Swatch color="rgba(254, 202, 87, 0.25)" label="low-vol" />
    <Swatch color="rgba(87, 101, 116, 0.25)" label="ranging" />
    <Swatch color="rgba(255, 71, 87, 0.5)" label="strategy DD shading" />
  </div>
);

const Swatch = ({ color, label }: { color: string; label: string }) => (
  <span className="inline-flex items-center gap-1.5">
    <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
    {label}
  </span>
);
