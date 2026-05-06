import type { StrategyData } from "@/types";
import { Section } from "@/components/shared/Section";
import { PairCard } from "./PairCard";
import { cumulativeReturnPct } from "@/utils/stats";

export const MacroGrid = ({ data }: { data: StrategyData }) => {
  const sorted = [...data.pairs].sort(
    (a, b) => cumulativeReturnPct(b.years) - cumulativeReturnPct(a.years),
  );
  return (
    <Section
      eyebrow="Zone A · Macro Grid"
      title="Ten pairs, six folds, one risk envelope"
      subtitle="Sorted by 6-year cumulative return. Each card: cumulative, average annual, peak drawdown, total trades, equity sparkline. Tier color = avg max drawdown bucket. Hover for year-by-year. Click a DD% to replay that year."
      right={
        <div className="flex items-center gap-3 text-[11px] text-muted">
          <Legend swatch="#00d084" label="<5% avg DD" />
          <Legend swatch="#feca57" label="5–10%" />
          <Legend swatch="#ff4757" label=">10%" />
        </div>
      }
    >
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
        {sorted.map((p) => (
          <PairCard key={p.symbol} pair={p} />
        ))}
      </div>
    </Section>
  );
};

const Legend = ({ swatch, label }: { swatch: string; label: string }) => (
  <div className="flex items-center gap-1.5">
    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: swatch }} />
    <span className="mono">{label}</span>
  </div>
);
