export interface YearStat {
  year: number;
  net_profit_pct: number;
  max_drawdown_pct: number;
  biggest_grid_pips: number | null;
  avg_dd_first_trade_pct: number;
  avg_dd_sequence_pct: number | null;
  max_levels: number;
  trades: number;
}

export interface Pair {
  symbol: string;
  yahoo_ticker: string;
  years: YearStat[];
}

export interface StrategyData {
  framework: string;
  title: string;
  period: { start: string; end: string };
  pairs: Pair[];
}

export interface Candle {
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
}

export interface MarketData {
  symbol: string;
  ticker: string;
  start: string;
  end: string;
  candles: Candle[];
}

export type RiskTier = "green" | "yellow" | "red";
export type ViewMode = "strategy" | "market";
export type RegimeLabel = "trending" | "ranging" | "high-vol" | "low-vol";

export interface YearMarketStats {
  year: number;
  market_drift_pct: number;
  market_vol_pct: number;
  flag: "alpha" | "mismatch" | "inline";
  gap_score: number;
}
