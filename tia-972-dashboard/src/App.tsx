import { useStrategyData } from "@/hooks/useStrategyData";
import { useKeyboardNav } from "@/hooks/useKeyboardNav";
import { Gate } from "@/components/Gate";
import { Header } from "@/components/Header";
import { MacroGrid } from "@/components/ZoneA/MacroGrid";
import { TemporalArena } from "@/components/ZoneB/TemporalArena";
import { Comparator } from "@/components/ZoneC/Comparator";

export default function App() {
  return (
    <Gate>
      <Dashboard />
    </Gate>
  );
}

function Dashboard() {
  const { data, error } = useStrategyData();
  useKeyboardNav(data);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-loss mono">Error: {error}</div>
      </div>
    );
  }
  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="mono text-muted text-sm tracking-widest ticker-pulse">LOADING…</div>
      </div>
    );
  }

  return (
    <main className="min-h-screen pb-16">
      <Header data={data} />
      <MacroGrid data={data} />
      <TemporalArena data={data} />
      <Comparator data={data} />
      <footer className="px-6 lg:px-10 py-6 mt-8 border-t border-border text-[11px] mono text-muted flex flex-wrap items-center justify-between gap-3">
        <span>↑↓←→ cycle pairs · Space toggles view · click DD% to replay</span>
        <span>Strategy: TIA-9.72 walk-forward · Market data: Yahoo Finance daily OHLC</span>
      </footer>
    </main>
  );
}
