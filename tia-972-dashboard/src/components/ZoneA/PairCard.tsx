import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import type { Pair } from "@/types";
import { useTilt } from "@/hooks/useTilt";
import { useDashboard } from "@/store/dashboard";
import {
  avgAnnualReturn,
  avgMaxDD,
  cumulativeReturnPct,
  peakMaxDD,
  riskTier,
  sparklinePath,
  tierColor,
  totalTrades,
  orderedYears,
} from "@/utils/stats";
import { validationScore, scoreColor, scoreLabel } from "@/utils/validationScore";
import { fmtPctNoSign, fmtPct, prettySymbol } from "@/utils/format";

interface Props { pair: Pair }

export const PairCard = ({ pair }: Props) => {
  const { ref, style, onMove, onLeave } = useTilt(6);
  const [expanded, setExpanded] = useState(false);
  const setSelectedPair = useDashboard((s) => s.setSelectedPair);
  const triggerReplay = useDashboard((s) => s.triggerReplay);
  const selectedPair = useDashboard((s) => s.selectedPair);

  const tier = riskTier(pair.years);
  const c = tierColor(tier);
  const cumRet = cumulativeReturnPct(pair.years);
  const avgRet = avgAnnualReturn(pair.years);
  const peak = peakMaxDD(pair.years);
  const avgDD = avgMaxDD(pair.years);
  const trades = totalTrades(pair.years);
  const score = validationScore(pair);
  const scoreC = scoreColor(score);

  const sw = 220, sh = 56;
  const sp = sparklinePath(pair.years, sw, sh);

  const isActive = selectedPair === pair.symbol;

  return (
    <motion.div
      ref={ref}
      onMouseMove={onMove}
      onMouseLeave={() => { onLeave(); setExpanded(false); }}
      onMouseEnter={() => setExpanded(true)}
      onClick={() => setSelectedPair(pair.symbol)}
      style={style}
      className={`card-shine card-tilt relative cursor-pointer rounded-xl border p-5 tier-${tier} ${isActive ? "ring-1 ring-accent/60" : ""}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="mono text-xs text-muted tracking-widest">{prettySymbol(pair.symbol)}</div>
          <div className="text-lg font-semibold mt-1">{pair.symbol.replace(/X$/, "")}</div>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="inline-flex items-center mono text-[10px] px-2 py-0.5 rounded-full"
            style={{ backgroundColor: `${scoreC}1f`, color: scoreC }}
            title={`Validation Score: ${scoreLabel(score)}`}
          >
            {score}
          </span>
          <span
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: c, boxShadow: `0 0 10px ${c}` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <Stat label="6Y CUM" value={fmtPct(cumRet, 1)} tone={cumRet >= 0 ? "profit" : "loss"} />
        <Stat label="AVG/YR" value={fmtPct(avgRet, 2)} tone="profit" />
        <Stat label="PEAK DD" value={fmtPctNoSign(peak)} tone="loss" />
      </div>

      <svg width={sw} height={sh} viewBox={`0 0 ${sw} ${sh}`} className="w-full block">
        <defs>
          <linearGradient id={`g-${pair.symbol}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={c} stopOpacity="0.35" />
            <stop offset="100%" stopColor={c} stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          d={`${sp.path} L ${sw - 2},${sh - 2} L 2,${sh - 2} Z`}
          fill={`url(#g-${pair.symbol})`}
        />
        <path d={sp.path} stroke={c} strokeWidth="1.5" fill="none" />
        <circle cx={sp.lastX} cy={sp.lastY} r="2.5" fill={c} />
      </svg>

      <div className="grid grid-cols-2 gap-3 mt-4 text-xs text-muted">
        <div className="flex justify-between"><span>AVG DD</span><span className="mono text-fg">{fmtPctNoSign(avgDD)}</span></div>
        <div className="flex justify-between"><span>TRADES</span><span className="mono text-fg">{trades}</span></div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 6 }}
            transition={{ duration: 0.18 }}
            className="absolute left-0 right-0 top-full z-30 mt-2 rounded-xl border border-border bg-panel2 shadow-card p-4 text-xs"
          >
            <div className="text-[10px] uppercase tracking-[0.18em] text-muted mb-2">Year-by-year</div>
            <table className="w-full mono">
              <thead className="text-muted text-[10px]">
                <tr>
                  <th className="text-left font-normal py-1">YR</th>
                  <th className="text-right font-normal">RET</th>
                  <th className="text-right font-normal">DD</th>
                  <th className="text-right font-normal">GRID</th>
                  <th className="text-right font-normal">TRD</th>
                </tr>
              </thead>
              <tbody>
                {orderedYears(pair).map((y) => (
                  <tr key={y.year} className="border-t border-border/60">
                    <td className="py-1.5">{y.year}</td>
                    <td className="text-right text-profit">{fmtPctNoSign(y.net_profit_pct)}</td>
                    <td
                      className="text-right text-loss cursor-pointer hover:underline"
                      onClick={(e) => {
                        e.stopPropagation();
                        triggerReplay(pair.symbol, y.year);
                      }}
                      title="Click to replay"
                    >
                      {fmtPctNoSign(y.max_drawdown_pct)}
                    </td>
                    <td className="text-right text-fg">{y.biggest_grid_pips ?? "—"}</td>
                    <td className="text-right text-fg">{y.trades}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const Stat = ({ label, value, tone }: { label: string; value: string; tone: "profit" | "loss" | "neutral" }) => (
  <div>
    <div className="text-[9px] uppercase tracking-[0.18em] text-muted">{label}</div>
    <div className={`mono text-sm mt-1 ${tone === "profit" ? "text-profit" : tone === "loss" ? "text-loss" : "text-fg"}`}>
      {value}
    </div>
  </div>
);
